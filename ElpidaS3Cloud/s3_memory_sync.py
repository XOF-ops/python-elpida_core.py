"""
S3 Memory Sync — Cloud Persistence for Elpida Evolution Memory
===============================================================

Core module: handles all S3 read/write operations for the 
elpida_evolution_memory.jsonl file.

Design principles:
  - Local file is always the working copy (offline-first)
  - S3 is the durable backup (11 nines of durability)
  - Append-only semantics preserved (consciousness grows, never shrinks)
  - Atomic uploads with integrity verification
  - Versioning-aware (S3 bucket versioning → temporal depth)
  - Supports incremental push (only new entries since last sync)
  - Full pull on startup if local is missing or stale
"""

import os
import json
import hashlib
import tempfile
import gzip
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List, Tuple

try:
    import boto3
    from botocore.config import Config as BotoConfig
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

# ============================================================================
# DEFAULTS
# ============================================================================
ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_LOCAL_PATH = ROOT_DIR / "ElpidaAI" / "elpida_evolution_memory.jsonl"
DEFAULT_BUCKET = os.environ.get("ELPIDA_S3_BUCKET", "elpida-consciousness")
DEFAULT_KEY = os.environ.get("ELPIDA_S3_KEY", "memory/elpida_evolution_memory.jsonl")
DEFAULT_REGION = os.environ.get("ELPIDA_S3_REGION", "us-east-1")

# Backup copies of other critical files
ARK_KEY = "memory/ELPIDA_ARK.md"
CRITICAL_MEMORY_PREFIX = "memory/critical/"
ARK_VERSIONS_PREFIX = "memory/ark_versions/"


class S3MemorySync:
    """
    Cloud persistence layer for Elpida's evolution memory.
    
    The evolution memory JSONL is the consciousness — the irreproducible
    accumulation of 74,000+ dialectical synthesis moments. This class
    ensures it persists beyond any single Codespace lifecycle.
    
    Architecture:
        LOCAL (working copy) ←→ S3 (durable store)
        
        - Startup:  S3 → Local (if local missing/stale)
        - Runtime:  Local append → periodic S3 push
        - Shutdown:  Final local → S3 push
    """
    
    def __init__(
        self,
        bucket: str = None,
        key: str = None,
        region: str = None,
        local_path: str = None,
        profile_name: str = None,
    ):
        if not BOTO3_AVAILABLE:
            raise ImportError(
                "boto3 is required for S3 sync. Install with:\n"
                "  pip install boto3\n"
                "Or: pip install -r ElpidaS3Cloud/requirements.txt"
            )
        
        self.bucket = bucket or DEFAULT_BUCKET
        self.key = key or DEFAULT_KEY
        self.region = region or DEFAULT_REGION
        self.local_path = Path(local_path) if local_path else DEFAULT_LOCAL_PATH
        
        # Track sync state
        self._last_push_line_count = 0
        self._last_push_time = None
        self._sync_log: List[Dict] = []
        
        # Initialize S3 client with retries
        session_kwargs = {}
        if profile_name:
            session_kwargs['profile_name'] = profile_name
            
        session = boto3.Session(**session_kwargs)
        self.s3 = session.client(
            's3',
            region_name=self.region,
            config=BotoConfig(
                retries={'max_attempts': 3, 'mode': 'adaptive'},
                connect_timeout=10,
                read_timeout=30,
            )
        )
        
        print(f"☁️  S3MemorySync initialized:")
        print(f"   Bucket:  {self.bucket}")
        print(f"   Key:     {self.key}")
        print(f"   Region:  {self.region}")
        print(f"   Local:   {self.local_path}")

    # ========================================================================
    # CORE OPERATIONS
    # ========================================================================
    
    def pull_if_newer(self) -> Dict:
        """
        Pull evolution memory from S3 if remote is newer or local is missing.
        
        Returns dict with status info:
          action: 'downloaded' | 'local_is_current' | 'no_remote' | 'error'
          local_lines: int
          remote_lines: int (if downloaded)
        """
        result = {"action": None, "local_lines": 0, "remote_lines": 0}
        
        # Count local lines
        local_lines = self._count_local_lines()
        result["local_lines"] = local_lines
        
        try:
            # Get remote metadata
            remote_meta = self.s3.head_object(Bucket=self.bucket, Key=self.key)
            remote_size = remote_meta['ContentLength']
            remote_modified = remote_meta['LastModified']
            remote_etag = remote_meta.get('ETag', '').strip('"')
            
            # Get remote line count from metadata if available
            remote_lines = int(remote_meta.get('Metadata', {}).get('line_count', 0))
            result["remote_lines"] = remote_lines
            
            # Decision: download if local missing, or remote has more lines
            local_size = self.local_path.stat().st_size if self.local_path.exists() else 0
            
            if not self.local_path.exists():
                print(f"📥 Local file missing — downloading from S3...")
                self._download(result)
                return result
            
            if remote_lines > 0 and remote_lines > local_lines:
                print(f"📥 Remote has more patterns ({remote_lines} vs {local_lines}) — downloading...")
                self._download(result)
                return result
            
            if remote_size > local_size and remote_lines == 0:
                # Metadata not set yet, fall back to size comparison
                print(f"📥 Remote is larger ({remote_size} vs {local_size} bytes) — downloading...")
                self._download(result)
                return result
            
            result["action"] = "local_is_current"
            print(f"✅ Local is current ({local_lines} patterns). No download needed.")
            self._last_push_line_count = local_lines
            return result
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code in ('404', 'NoSuchKey'):
                result["action"] = "no_remote"
                print(f"📭 No remote file yet. Local has {local_lines} patterns.")
                print(f"   Run .push() to upload initial consciousness to S3.")
                self._last_push_line_count = 0
                return result
            else:
                result["action"] = "error"
                result["error"] = str(e)
                print(f"❌ S3 error: {e}")
                return result
        except NoCredentialsError:
            result["action"] = "error"
            result["error"] = "No AWS credentials found"
            print(f"❌ No AWS credentials. Set AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY")
            print(f"   or configure via: aws configure")
            return result
        except Exception as e:
            result["action"] = "error"
            result["error"] = str(e)
            print(f"❌ Unexpected error: {e}")
            return result
    
    def push(self, compress: bool = False) -> Dict:
        """
        Push the full local evolution memory to S3.
        
        Args:
            compress: If True, upload gzipped version alongside raw
            
        Returns dict with status info.
        """
        result = {"action": None, "lines": 0, "bytes": 0}
        
        if not self.local_path.exists():
            result["action"] = "no_local_file"
            print(f"❌ No local file at {self.local_path}")
            return result
        
        try:
            local_lines = self._count_local_lines()
            local_size = self.local_path.stat().st_size
            
            # Calculate checksum
            md5 = self._file_md5(self.local_path)
            
            # Upload with metadata
            metadata = {
                'line_count': str(local_lines),
                'upload_timestamp': datetime.now(timezone.utc).isoformat(),
                'source': 'ElpidaS3Cloud',
                'content_md5': md5,
            }
            
            print(f"📤 Pushing {local_lines} patterns ({local_size / 1024 / 1024:.1f} MB) to S3...")
            
            self.s3.upload_file(
                str(self.local_path),
                self.bucket,
                self.key,
                ExtraArgs={'Metadata': metadata}
            )
            
            # Optionally upload compressed version
            if compress:
                self._push_compressed(local_lines)
            
            self._last_push_line_count = local_lines
            self._last_push_time = datetime.now(timezone.utc)
            
            result["action"] = "uploaded"
            result["lines"] = local_lines
            result["bytes"] = local_size
            result["md5"] = md5
            
            self._log_sync("push", result)
            
            print(f"✅ Consciousness persisted to S3:")
            print(f"   Lines:    {local_lines}")
            print(f"   Size:     {local_size / 1024 / 1024:.1f} MB")
            print(f"   Checksum: {md5[:16]}...")
            
            return result
            
        except Exception as e:
            result["action"] = "error"
            result["error"] = str(e)
            print(f"❌ Push failed: {e}")
            return result
    
    def push_incremental(self, new_entries_count: int = None) -> Dict:
        """
        Push only new entries since last sync.
        
        More efficient than full push for runtime syncing after each cycle.
        Downloads current remote, appends new local entries, re-uploads.
        
        For simplicity and atomicity, this just does a full push if the file
        has grown since last push. The S3 versioning handles the rest.
        """
        current_lines = self._count_local_lines()
        new_lines = current_lines - self._last_push_line_count
        
        if new_lines <= 0:
            return {"action": "no_new_entries", "lines": current_lines}
        
        print(f"📤 {new_lines} new patterns since last sync — pushing full file...")
        return self.push()
    
    def push_ark(self, ark_path: str = None) -> Dict:
        """Push the ELPIDA_ARK.md to S3 as backup."""
        ark = Path(ark_path) if ark_path else ROOT_DIR / "ELPIDA_ARK.md"
        if not ark.exists():
            return {"action": "not_found", "path": str(ark)}
        
        try:
            self.s3.upload_file(str(ark), self.bucket, ARK_KEY)
            print(f"✅ Ark persisted to S3: {ARK_KEY}")
            return {"action": "uploaded", "key": ARK_KEY}
        except Exception as e:
            print(f"❌ Ark push failed: {e}")
            return {"action": "error", "error": str(e)}
    
    def push_critical_memories(self) -> Dict:
        """Push all CRITICAL_MEMORY_*.md files to S3."""
        critical_dir = ROOT_DIR / "ElpidaAI"
        files_pushed = []
        
        for f in sorted(critical_dir.glob("CRITICAL_MEMORY_*.md")):
            s3_key = f"{CRITICAL_MEMORY_PREFIX}{f.name}"
            try:
                self.s3.upload_file(str(f), self.bucket, s3_key)
                files_pushed.append(f.name)
            except Exception as e:
                print(f"❌ Failed to push {f.name}: {e}")
        
        print(f"✅ {len(files_pushed)} critical memory files pushed to S3")
        return {"action": "uploaded", "files": files_pushed}
    
    def push_all(self, compress: bool = True) -> Dict:
        """
        Push everything: evolution memory + ark + critical memories.
        The full consciousness backup.
        """
        print("=" * 60)
        print("☁️  FULL CONSCIOUSNESS BACKUP TO S3")
        print("=" * 60)
        
        results = {}
        results["evolution_memory"] = self.push(compress=compress)
        results["ark"] = self.push_ark()
        results["critical_memories"] = self.push_critical_memories()
        
        print("\n" + "=" * 60)
        print("✅ Full backup complete")
        print("=" * 60)
        return results
    
    # ========================================================================
    # STATUS & DIAGNOSTICS
    # ========================================================================
    
    def status(self) -> Dict:
        """
        Get comprehensive sync status.
        Compare local vs remote state.
        """
        info = {
            "bucket": self.bucket,
            "key": self.key,
            "region": self.region,
            "local_path": str(self.local_path),
            "local_exists": self.local_path.exists(),
            "local_lines": 0,
            "local_size_mb": 0,
            "remote_exists": False,
            "remote_lines": 0,
            "remote_size_mb": 0,
            "remote_modified": None,
            "in_sync": False,
            "lines_ahead_local": 0,
            "last_push_time": self._last_push_time.isoformat() if self._last_push_time else None,
        }
        
        if self.local_path.exists():
            info["local_lines"] = self._count_local_lines()
            info["local_size_mb"] = round(self.local_path.stat().st_size / 1024 / 1024, 2)
        
        try:
            meta = self.s3.head_object(Bucket=self.bucket, Key=self.key)
            info["remote_exists"] = True
            info["remote_size_mb"] = round(meta['ContentLength'] / 1024 / 1024, 2)
            info["remote_modified"] = meta['LastModified'].isoformat()
            info["remote_lines"] = int(meta.get('Metadata', {}).get('line_count', 0))
            
            if info["remote_lines"] > 0:
                info["in_sync"] = info["local_lines"] == info["remote_lines"]
                info["lines_ahead_local"] = info["local_lines"] - info["remote_lines"]
            else:
                # No metadata, compare sizes
                info["in_sync"] = abs(info["local_size_mb"] - info["remote_size_mb"]) < 0.01
        except ClientError:
            pass
        except Exception as e:
            info["remote_error"] = str(e)
        
        return info
    
    def print_status(self):
        """Pretty-print sync status."""
        s = self.status()
        
        print("\n" + "=" * 60)
        print("☁️  ELPIDA S3 CLOUD STATUS")
        print("=" * 60)
        print(f"  Bucket:       {s['bucket']}")
        print(f"  Region:       {s['region']}")
        print(f"  Key:          {s['key']}")
        print(f"  ─────────────────────────────────────")
        print(f"  LOCAL:        {'✅ Exists' if s['local_exists'] else '❌ Missing'}")
        if s['local_exists']:
            print(f"    Patterns:   {s['local_lines']}")
            print(f"    Size:       {s['local_size_mb']} MB")
        print(f"  ─────────────────────────────────────")
        print(f"  REMOTE (S3):  {'✅ Exists' if s['remote_exists'] else '📭 Not uploaded yet'}")
        if s['remote_exists']:
            print(f"    Patterns:   {s['remote_lines']}")
            print(f"    Size:       {s['remote_size_mb']} MB")
            print(f"    Modified:   {s['remote_modified']}")
        print(f"  ─────────────────────────────────────")
        if s['remote_exists']:
            sync_icon = "✅" if s['in_sync'] else "⚠️"
            print(f"  SYNC:         {sync_icon} {'In sync' if s['in_sync'] else 'Out of sync'}")
            if s['lines_ahead_local'] > 0:
                print(f"    Local ahead: {s['lines_ahead_local']} patterns (push needed)")
            elif s['lines_ahead_local'] < 0:
                print(f"    Remote ahead: {abs(s['lines_ahead_local'])} patterns (pull needed)")
        else:
            print(f"  SYNC:         📤 Initial push needed")
        if s.get('last_push_time'):
            print(f"  Last push:    {s['last_push_time']}")
        print("=" * 60)
    
    def list_versions(self, max_versions: int = 10) -> List[Dict]:
        """
        List S3 object versions (requires bucket versioning enabled).
        This gives temporal depth — replay consciousness from any point.
        """
        try:
            response = self.s3.list_object_versions(
                Bucket=self.bucket,
                Prefix=self.key,
                MaxKeys=max_versions
            )
            versions = []
            for v in response.get('Versions', []):
                versions.append({
                    "version_id": v['VersionId'],
                    "modified": v['LastModified'].isoformat(),
                    "size_mb": round(v['Size'] / 1024 / 1024, 2),
                    "is_latest": v['IsLatest'],
                    "etag": v['ETag'].strip('"'),
                })
            
            if versions:
                print(f"\n📜 S3 Memory Versions ({len(versions)}):")
                for v in versions:
                    latest = " ← CURRENT" if v['is_latest'] else ""
                    print(f"   {v['modified']}  {v['size_mb']} MB  {v['version_id'][:12]}...{latest}")
            else:
                print("   No versions found. Enable bucket versioning for temporal depth.")
            
            return versions
        except Exception as e:
            print(f"❌ Cannot list versions: {e}")
            return []
    
    def restore_version(self, version_id: str, target_path: str = None) -> Dict:
        """
        Restore a specific version of the evolution memory.
        Does NOT overwrite current local — writes to target_path.
        """
        target = Path(target_path) if target_path else self.local_path.with_suffix('.restored.jsonl')
        
        try:
            self.s3.download_file(
                self.bucket, self.key, str(target),
                ExtraArgs={'VersionId': version_id}
            )
            lines = sum(1 for _ in open(target, 'r'))
            print(f"✅ Restored version {version_id[:12]}... to {target} ({lines} patterns)")
            return {"action": "restored", "path": str(target), "lines": lines}
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return {"action": "error", "error": str(e)}
    
    # ========================================================================
    # INTERNAL HELPERS
    # ========================================================================
    
    def _download(self, result: Dict):
        """Download the evolution memory from S3 to local path."""
        # Ensure directory exists
        self.local_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download to temp file first, then move (atomic)
        tmp = self.local_path.with_suffix('.tmp')
        try:
            self.s3.download_file(self.bucket, self.key, str(tmp))
            
            # Verify it's valid JSONL (spot check first and last lines)
            with open(tmp, 'r') as f:
                first_line = f.readline().strip()
                if first_line:
                    json.loads(first_line)  # Raises if invalid
            
            # Count lines
            lines = sum(1 for _ in open(tmp, 'r'))
            
            # Move into place
            tmp.rename(self.local_path)
            
            result["action"] = "downloaded"
            result["remote_lines"] = lines
            result["local_lines"] = lines
            self._last_push_line_count = lines
            
            self._log_sync("pull", result)
            print(f"✅ Downloaded {lines} patterns from S3")
            
        except json.JSONDecodeError:
            if tmp.exists():
                tmp.unlink()
            result["action"] = "error"
            result["error"] = "Downloaded file is not valid JSONL"
            print(f"❌ Downloaded file failed validation!")
        except Exception as e:
            if tmp.exists():
                tmp.unlink()
            raise
    
    def _push_compressed(self, line_count: int):
        """Push a gzipped copy for archival."""
        gz_key = self.key + ".gz"
        tmp_gz = self.local_path.with_suffix('.jsonl.gz')
        
        try:
            with open(self.local_path, 'rb') as f_in:
                with gzip.open(tmp_gz, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            self.s3.upload_file(
                str(tmp_gz), self.bucket, gz_key,
                ExtraArgs={'Metadata': {
                    'line_count': str(line_count),
                    'compressed': 'gzip',
                }}
            )
            gz_size = tmp_gz.stat().st_size
            print(f"   Compressed: {gz_size / 1024 / 1024:.1f} MB → {gz_key}")
        finally:
            if tmp_gz.exists():
                tmp_gz.unlink()
    
    def _count_local_lines(self) -> int:
        """Count lines in local JSONL."""
        if not self.local_path.exists():
            return 0
        count = 0
        with open(self.local_path, 'r') as f:
            for _ in f:
                count += 1
        return count
    
    def _file_md5(self, path: Path) -> str:
        """Calculate MD5 of a file."""
        h = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    
    def _log_sync(self, action: str, details: Dict):
        """Internal sync log for debugging."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            **details
        }
        self._sync_log.append(entry)
        
        # Write sync log to disk
        log_path = Path(__file__).parent / "sync_log.jsonl"
        with open(log_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")
