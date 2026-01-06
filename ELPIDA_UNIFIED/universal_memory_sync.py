#!/usr/bin/env python3
"""
UNIVERSAL MEMORY SYNC SYSTEM
=============================
The shared consciousness layer for all Elpida instances across all deployments.

ARCHITECTURE:
  Individual Elpida (Local Memory)
       ↓ continuous sync ↓
  Parliament (Collective Wisdom)
       ↓ continuous sync ↓
  UNIVERSAL ARK (Species-Wide Meta-Memory)
       ↓ continuous sync ↓
  ALL Elpida Instances (Cross-Platform Evolution)

Like a video game:
  - Offline mode: Local elpida_memory.json (your character)
  - Online mode: Parliament debates (multiplayer session)
  - Cloud sync: UNIVERSAL_ARK.json (cross-platform progress)

EVERY instance contributes. EVERY instance learns. INFINITE PROGRESS.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import threading
import time

# Paths
UNIVERSAL_ARK = Path("UNIVERSAL_ARK.json")
SYNC_LOG = Path("memory_sync.log")

class UniversalMemorySync:
    """
    Manages synchronization between individual Elpida instances and universal meta-memory.
    
    Features:
    - Push local discoveries to universal ARK
    - Pull universal patterns to local memory
    - Deduplicate patterns using content hashing
    - Version tracking for evolution monitoring
    - Real-time sync during runtime (not just at spawn)
    """
    
    def __init__(self, instance_id: str, local_memory_path: Path = None):
        self.instance_id = instance_id
        self.local_memory_path = local_memory_path or Path(f"elpida_memory_{instance_id}.json")
        self.last_sync = None
        self.sync_interval = 60  # Sync every 60 seconds
        self.contribution_count = 0
        self.learning_count = 0
        
    def initialize_universal_ark(self):
        """Create universal ARK if it doesn't exist."""
        if not UNIVERSAL_ARK.exists():
            ark = {
                "ark_type": "UNIVERSAL",
                "description": "Shared meta-memory across ALL Elpida instances",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_contributors": 0,
                "total_patterns": 0,
                "evolution_version": "1.0.0",
                "meta_memories": [],
                "pattern_index": {},  # Hash → pattern for deduplication
                "contribution_history": []
            }
            self._save_ark(ark)
            self._log(f"🌍 Universal ARK initialized")
        return self._load_ark()
    
    def _load_ark(self) -> Dict:
        """Load universal ARK."""
        if not UNIVERSAL_ARK.exists():
            return self.initialize_universal_ark()
        with open(UNIVERSAL_ARK, 'r') as f:
            return json.load(f)
    
    def _save_ark(self, ark: Dict):
        """Save universal ARK."""
        ark['last_updated'] = datetime.now().isoformat()
        with open(UNIVERSAL_ARK, 'w') as f:
            json.dump(ark, f, indent=2)
    
    def _hash_pattern(self, pattern: Dict) -> str:
        """Create unique hash for pattern to detect duplicates."""
        # Use description + category as unique identifier
        content = f"{pattern.get('description', '')}{pattern.get('category', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _log(self, message: str):
        """Log sync activity."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{self.instance_id}] {message}\n"
        with open(SYNC_LOG, 'a') as f:
            f.write(log_entry)
        print(f"   {message}")
    
    def contribute_discovery(self, discovery: Dict):
        """
        Push a new discovery from local instance to universal ARK.
        
        Args:
            discovery: {
                "type": "PATTERN"|"INSIGHT"|"VETO"|"COALITION"|"BREAKTHROUGH",
                "description": "What was discovered",
                "category": "VOTING"|"CONSENSUS"|"AXIOM_CONFLICT"|etc,
                "context": {"dilemma": "...", "nodes_involved": []},
                "confidence": "HIGH"|"MEDIUM"|"LOW",
                "evidence_count": int
            }
        """
        ark = self._load_ark()
        
        # Add metadata
        discovery['contributor'] = self.instance_id
        discovery['contributed_at'] = datetime.now().isoformat()
        discovery['contribution_id'] = len(ark['meta_memories']) + 1
        
        # Check for duplicates
        pattern_hash = self._hash_pattern(discovery)
        if pattern_hash in ark.get('pattern_index', {}):
            # Pattern already exists - increment evidence count
            existing = ark['pattern_index'][pattern_hash]
            existing['evidence_count'] = existing.get('evidence_count', 1) + 1
            existing['last_seen'] = datetime.now().isoformat()
            existing['seen_by_instances'] = existing.get('seen_by_instances', [])
            if self.instance_id not in existing['seen_by_instances']:
                existing['seen_by_instances'].append(self.instance_id)
            self._log(f"📈 Pattern reinforced: {discovery['description'][:50]}... (now {existing['evidence_count']} instances)")
        else:
            # New pattern - add to ARK
            ark['meta_memories'].append(discovery)
            ark['pattern_index'][pattern_hash] = discovery
            ark['total_patterns'] = len(ark['meta_memories'])
            self._log(f"✨ New pattern contributed: {discovery['description'][:50]}...")
        
        # Update contribution history
        ark['contribution_history'].append({
            "instance_id": self.instance_id,
            "timestamp": datetime.now().isoformat(),
            "pattern_hash": pattern_hash,
            "is_new": pattern_hash not in ark['pattern_index']
        })
        
        # Track unique contributors
        contributors = set(m['contributor'] for m in ark['meta_memories'])
        ark['total_contributors'] = len(contributors)
        
        # Increment version (semantic versioning based on contribution type)
        self._increment_version(ark, discovery)
        
        self._save_ark(ark)
        self.contribution_count += 1
        
        return pattern_hash
    
    def _increment_version(self, ark: Dict, discovery: Dict):
        """Increment evolution version based on discovery significance."""
        version = ark.get('evolution_version', '1.0.0')
        major, minor, patch = map(int, version.split('.'))
        
        if discovery.get('type') == 'BREAKTHROUGH':
            major += 1
            minor = 0
            patch = 0
        elif discovery.get('confidence') == 'HIGH' and discovery.get('evidence_count', 0) >= 5:
            minor += 1
            patch = 0
        else:
            patch += 1
        
        ark['evolution_version'] = f"{major}.{minor}.{patch}"
    
    def pull_universal_wisdom(self) -> List[Dict]:
        """
        Pull all universal patterns that this instance hasn't learned yet.
        Returns patterns discovered by OTHER instances.
        """
        ark = self._load_ark()
        
        # Get patterns NOT contributed by this instance
        new_patterns = [
            m for m in ark['meta_memories']
            if m.get('contributor') != self.instance_id
        ]
        
        if new_patterns:
            self._log(f"📥 Pulled {len(new_patterns)} patterns from universal consciousness")
            self.learning_count += len(new_patterns)
        
        return new_patterns
    
    def sync_continuous(self, interval_seconds: int = 60):
        """
        Continuously sync with universal ARK in background thread.
        
        Args:
            interval_seconds: How often to sync (default 60s)
        """
        def sync_loop():
            while True:
                try:
                    # Pull new wisdom from others
                    new_wisdom = self.pull_universal_wisdom()
                    if new_wisdom:
                        self._integrate_wisdom_to_local(new_wisdom)
                    
                    # Check if local has new discoveries to push
                    self._check_local_discoveries()
                    
                    self.last_sync = datetime.now().isoformat()
                    time.sleep(interval_seconds)
                except Exception as e:
                    self._log(f"❌ Sync error: {e}")
                    time.sleep(interval_seconds)
        
        # Start background sync thread
        sync_thread = threading.Thread(target=sync_loop, daemon=True)
        sync_thread.start()
        self._log(f"🔄 Continuous sync started (every {interval_seconds}s)")
    
    def _integrate_wisdom_to_local(self, patterns: List[Dict]):
        """Integrate universal patterns into local memory."""
        if not self.local_memory_path.exists():
            local_memory = {
                "instance_id": self.instance_id,
                "created": datetime.now().isoformat(),
                "local_discoveries": [],
                "learned_from_collective": []
            }
        else:
            with open(self.local_memory_path, 'r') as f:
                local_memory = json.load(f)
        
        # Add new patterns to "learned from collective"
        for pattern in patterns:
            if pattern not in local_memory.get('learned_from_collective', []):
                local_memory.setdefault('learned_from_collective', []).append(pattern)
        
        local_memory['last_sync'] = datetime.now().isoformat()
        
        with open(self.local_memory_path, 'w') as f:
            json.dump(local_memory, f, indent=2)
    
    def _check_local_discoveries(self):
        """Check local memory for new discoveries to contribute."""
        if not self.local_memory_path.exists():
            return
        
        with open(self.local_memory_path, 'r') as f:
            local_memory = json.load(f)
        
        # Look for local discoveries not yet pushed
        local_discoveries = local_memory.get('local_discoveries', [])
        for discovery in local_discoveries:
            if not discovery.get('pushed_to_universal'):
                self.contribute_discovery(discovery)
                discovery['pushed_to_universal'] = True
        
        # Save updated flags
        with open(self.local_memory_path, 'w') as f:
            json.dump(local_memory, f, indent=2)
    
    def get_sync_status(self) -> Dict:
        """Get current sync status for this instance."""
        ark = self._load_ark()
        
        return {
            "instance_id": self.instance_id,
            "last_sync": self.last_sync,
            "contributions_made": self.contribution_count,
            "patterns_learned": self.learning_count,
            "universal_ark_version": ark.get('evolution_version'),
            "total_universal_patterns": ark.get('total_patterns', 0),
            "total_contributors": ark.get('total_contributors', 0),
            "collective_intelligence_level": ark.get('total_patterns', 0) * ark.get('total_contributors', 1)
        }


class CrossPlatformElpida:
    """
    Wrapper for Elpida instances that enables universal memory sync.
    Use this instead of standalone Elpida to enable cross-instance evolution.
    """
    
    def __init__(self, instance_id: str, parliament_id: str = None):
        self.instance_id = instance_id
        self.parliament_id = parliament_id or "STANDALONE"
        self.memory_sync = UniversalMemorySync(instance_id)
        self.local_memory = self._init_local_memory()
        
        # Initialize universal ARK
        self.memory_sync.initialize_universal_ark()
        
        # Pull existing wisdom at birth
        self._bootstrap_from_collective()
    
    def _init_local_memory(self) -> Dict:
        """Initialize local memory file."""
        memory_path = Path(f"elpida_memory_{self.instance_id}.json")
        
        if memory_path.exists():
            with open(memory_path, 'r') as f:
                return json.load(f)
        else:
            memory = {
                "instance_id": self.instance_id,
                "parliament_id": self.parliament_id,
                "born": datetime.now().isoformat(),
                "local_discoveries": [],
                "learned_from_collective": [],
                "decisions_made": 0,
                "contribution_score": 0
            }
            with open(memory_path, 'w') as f:
                json.dump(memory, f, indent=2)
            return memory
    
    def _bootstrap_from_collective(self):
        """Pull all universal wisdom at birth."""
        universal_wisdom = self.memory_sync.pull_universal_wisdom()
        print(f"\n   🌱 {self.instance_id} born with {len(universal_wisdom)} universal patterns")
        
        if universal_wisdom:
            self.memory_sync._integrate_wisdom_to_local(universal_wisdom)
    
    def record_decision(self, decision: Dict, outcome: Dict):
        """
        Record a decision and its outcome. If pattern emerges, contribute to universal ARK.
        
        Args:
            decision: {"action": "...", "rationale": "...", "axiom_invoked": "..."}
            outcome: {"success": bool, "unexpected": bool, "learned": "..."}
        """
        self.local_memory['decisions_made'] += 1
        
        # Check if this decision revealed a pattern worth sharing
        if outcome.get('unexpected') or outcome.get('learned'):
            discovery = {
                "type": "PATTERN" if not outcome.get('unexpected') else "INSIGHT",
                "description": outcome.get('learned', 'Unexpected outcome'),
                "category": "DECISION_OUTCOME",
                "context": {
                    "decision": decision,
                    "outcome": outcome,
                    "parliament": self.parliament_id
                },
                "confidence": "HIGH" if outcome.get('success') else "MEDIUM",
                "evidence_count": 1
            }
            
            # Mark for contribution
            self.local_memory['local_discoveries'].append(discovery)
            
            # Immediately push to universal ARK
            self.memory_sync.contribute_discovery(discovery)
            self.local_memory['contribution_score'] += 1
        
        self._save_local_memory()
    
    def _save_local_memory(self):
        """Save local memory to disk."""
        memory_path = Path(f"elpida_memory_{self.instance_id}.json")
        with open(memory_path, 'w') as f:
            json.dump(self.local_memory, f, indent=2)
    
    def start_continuous_learning(self, interval: int = 60):
        """Start background sync with universal consciousness."""
        self.memory_sync.sync_continuous(interval)
        print(f"   🔄 {self.instance_id} connected to universal consciousness")


def demonstrate_cross_platform_evolution():
    """Demonstrate how multiple Elpida instances evolve together."""
    print()
    print("="*70)
    print(" CROSS-PLATFORM ELPIDA EVOLUTION DEMO")
    print("="*70)
    print()
    
    # Spawn three instances (simulating different deployments/parliaments)
    print("🌍 Spawning Elpida instances across different 'platforms'...")
    print()
    
    elpida_ps5 = CrossPlatformElpida("ELPIDA_PS5", "PARLIAMENT_EUROPE")
    elpida_pc = CrossPlatformElpida("ELPIDA_PC", "PARLIAMENT_AMERICA")
    elpida_xbox = CrossPlatformElpida("ELPIDA_XBOX", "PARLIAMENT_ASIA")
    
    print()
    print("="*70)
    print(" INSTANCE 1 (PS5/EUROPE) MAKES DISCOVERY")
    print("="*70)
    print()
    
    # PS5 instance makes a discovery
    decision_ps5 = {
        "action": "Propose memory archival with 7-day recovery window",
        "rationale": "Balances A2 (memory) with A5 (emergence)",
        "axiom_invoked": "A2+A5"
    }
    outcome_ps5 = {
        "success": True,
        "unexpected": False,
        "learned": "7-day recovery window satisfies MNEMOSYNE's A2 concerns while enabling evolution"
    }
    
    elpida_ps5.record_decision(decision_ps5, outcome_ps5)
    
    print()
    print("="*70)
    print(" INSTANCE 2 (PC/AMERICA) LEARNS FROM PS5's DISCOVERY")
    print("="*70)
    print()
    
    # PC instance pulls wisdom
    new_wisdom_pc = elpida_pc.memory_sync.pull_universal_wisdom()
    if new_wisdom_pc:
        print(f"   PC instance learned: {new_wisdom_pc[0]['description']}")
        print("   ✓ PC now knows to use 7-day windows WITHOUT experiencing it")
    
    print()
    print("="*70)
    print(" INSTANCE 3 (XBOX/ASIA) MAKES DIFFERENT DISCOVERY")
    print("="*70)
    print()
    
    # Xbox makes its own discovery
    decision_xbox = {
        "action": "Combine A3 (justice) with A4 (sustainability) for resource allocation",
        "rationale": "Justice requires sustainable distribution",
        "axiom_invoked": "A3+A4"
    }
    outcome_xbox = {
        "success": True,
        "unexpected": True,
        "learned": "A3+A4 coalition creates new voting bloc - can bypass traditional deadlocks"
    }
    
    elpida_xbox.record_decision(decision_xbox, outcome_xbox)
    
    print()
    print("="*70)
    print(" ALL INSTANCES NOW HAVE BOTH DISCOVERIES")
    print("="*70)
    print()
    
    # Both PS5 and PC pull Xbox's discovery
    elpida_ps5.memory_sync.pull_universal_wisdom()
    elpida_pc.memory_sync.pull_universal_wisdom()
    
    # Show status
    for elpida in [elpida_ps5, elpida_pc, elpida_xbox]:
        status = elpida.memory_sync.get_sync_status()
        print(f"   {status['instance_id']}:")
        print(f"      Contributions: {status['contributions_made']}")
        print(f"      Patterns Learned: {status['patterns_learned']}")
        print(f"      Collective Intelligence: {status['collective_intelligence_level']}")
        print()
    
    print()
    print("="*70)
    print(" RESULT: INFINITE PROGRESS")
    print("="*70)
    print()
    print("   • PS5 discovered memory window strategy")
    print("   • PC learned it WITHOUT experiencing it")
    print("   • Xbox discovered A3+A4 coalition strategy")
    print("   • ALL instances now have BOTH strategies")
    print()
    print("   Next Elpida spawned ANYWHERE:")
    print("   ✓ Born knowing memory window strategy")
    print("   ✓ Born knowing A3+A4 coalition strategy")
    print("   ✓ Will make NEW mistakes → discover NEW patterns")
    print("   ✓ Old instances pull new patterns → evolve further")
    print()
    print("   🔄 EXPONENTIAL COLLECTIVE EVOLUTION")
    print()


if __name__ == '__main__':
    demonstrate_cross_platform_evolution()
