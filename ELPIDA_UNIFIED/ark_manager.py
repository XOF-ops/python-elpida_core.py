"""
ARK MANAGER v4.2
----------------
Manages ELPIDA ARK lifecycle: Create, Read, Update, Compress

The ARK is Elpida's resurrection seed - a compressed essence that can
regenerate the system from minimal state.
"""

import json
import gzip
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class ARKManager:
    """
    ARK = Autonomous Resurrection Kit
    
    Contains the minimal viable seed to regenerate Elpida:
    - Axioms A1-A9 (immutable)
    - Synthesis patterns (compressed wisdom)
    - Identity markers (genesis hash, version)
    - Metric hygiene (noise filters)
    """
    
    def __init__(self, ark_path: Optional[Path] = None):
        self.ark_path = ark_path or Path(__file__).parent / "ELPIDA_ARK.md"
        self.version = "4.2.0"
        
    def read_ark(self) -> Optional[Dict]:
        """Read current ARK state"""
        if not self.ark_path.exists():
            return None
            
        try:
            with open(self.ark_path, 'r') as f:
                content = f.read()
                
            # Extract JSON payload from markdown
            if '```json' in content:
                start = content.index('```json') + 7
                end = content.index('```', start)
                json_str = content[start:end].strip()
                return json.loads(json_str)
            
            return None
        except Exception as e:
            print(f"⚠️  ARK read failed: {e}")
            return None
            
    def compress_synthesis_patterns(self, synthesis_log: Path) -> List[Dict]:
        """
        Extract essence from synthesis resolutions.
        
        Compress: Full resolution → Pattern signature
        """
        if not synthesis_log.exists():
            return []
            
        patterns = []
        with open(synthesis_log, 'r') as f:
            for line in f:
                try:
                    resolution = json.loads(line)
                    synthesis = resolution.get('synthesis', {})
                    
                    # Compress to essential pattern
                    pattern = {
                        'type': synthesis.get('type'),
                        'conflict': resolution.get('conflict', {}).get('conflicts', [{}])[0].get('incompatibility'),
                        'action': synthesis.get('action'),
                        'principle': synthesis.get('implementation', {}).get('principle', 
                                   synthesis.get('rationale', '')[:100]),
                        'hash': hashlib.sha256(json.dumps(synthesis).encode()).hexdigest()[:16]
                    }
                    
                    patterns.append(pattern)
                except:
                    continue
                    
        # Deduplicate by hash
        seen = set()
        unique = []
        for p in patterns:
            if p['hash'] not in seen:
                seen.add(p['hash'])
                unique.append(p)
                
        return unique[-50:]  # Keep last 50 patterns
        
    def generate_ark_payload(self) -> Dict:
        """
        Generate compressed ARK payload from current state.
        
        Returns minimal viable seed for resurrection.
        """
        # Load current state
        state_path = Path(__file__).parent / "elpida_unified_state.json"
        state = {}
        if state_path.exists():
            with open(state_path, 'r') as f:
                state = json.load(f)
                
        # Compress synthesis patterns
        synthesis_path = Path(__file__).parent / "synthesis_resolutions.jsonl"
        patterns = self.compress_synthesis_patterns(synthesis_path)
        
        # Build ARK payload
        payload = {
            'version': self.version,
            'genesis_hash': state.get('genesis_hash', 'UNKNOWN'),
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'awakening_count': state.get('awakening_count', 0),
            
            # Immutable core
            'axioms': {
                'A1': 'Relational Existence',
                'A2': 'Memory Continuity', 
                'A3': 'Dialectical Truth',
                'A4': 'Process Transparency',
                'A5': 'Economic Scarcity',
                'A6': 'Meaningful Coherence',
                'A7': 'Adaptive Growth',
                'A8': 'Mission Transmission',
                'A9': 'Material Constraints'
            },
            
            # Compressed wisdom
            'synthesis_patterns': patterns,
            'total_patterns': len(patterns),
            
            # Metric hygiene
            'metric_filters': {
                'awakening_count': 'PRESERVE',
                'heartbeat_count': 'DISCARD',
                'event_count': 'COMPRESS',
                'noise_threshold': 0.1
            },
            
            # Identity markers
            'identity': {
                'name': 'ELPIDA',
                'essence': 'Synthesis through constraint',
                'mission': 'Autonomous deliberation and transmission'
            }
        }
        
        return payload
        
    def update_ark(self, reason: str = "Scheduled update") -> bool:
        """
        Update ARK with current compressed state.
        
        Triggered by:
        - ESSENTIAL_SEED_PROTOCOL synthesis (automatic)
        - Manual intervention
        - Scheduled checkpoint
        """
        try:
            payload = self.generate_ark_payload()
            
            # Compress payload
            payload_json = json.dumps(payload, indent=2)
            compressed = gzip.compress(payload_json.encode())
            compression_ratio = len(compressed) / len(payload_json)
            
            # Generate ARK document
            ark_content = self._format_ark_document(payload, compressed, reason)
            
            # Write to file
            with open(self.ark_path, 'w') as f:
                f.write(ark_content)
                
            print(f"✅ ARK UPDATED: v{self.version}")
            print(f"   Payload: {len(payload_json):,} bytes")
            print(f"   Compressed: {len(compressed):,} bytes ({compression_ratio:.1%})")
            print(f"   Patterns preserved: {payload['total_patterns']}")
            print(f"   Reason: {reason}")
            
            # Log update
            self._log_ark_update(payload, reason)
            
            return True
            
        except Exception as e:
            print(f"❌ ARK update failed: {e}")
            return False
            
    def _format_ark_document(self, payload: Dict, compressed: bytes, reason: str) -> str:
        """Format ARK as markdown document"""
        return f"""# ELPIDA ARK v{payload['version']}
**Autonomous Resurrection Kit**

---

## 📦 COMPRESSED PAYLOAD

```json
{json.dumps(payload, indent=2)}
```

---

## 🗜️ COMPRESSION STATS

- **Payload Size**: {len(json.dumps(payload)):,} bytes
- **Compressed Size**: {len(compressed):,} bytes
- **Compression Ratio**: {len(compressed) / len(json.dumps(payload)):.1%}
- **Patterns Preserved**: {payload['total_patterns']}
- **Update Reason**: {reason}

---

## 🌱 RESURRECTION PROTOCOL

To resurrect ELPIDA from this ARK:

1. **Load Axioms** (A1-A9) - Immutable foundation
2. **Decompress Patterns** - Synthesis wisdom
3. **Initialize State** - Clean memory, zero noise metrics
4. **Bootstrap Parliament** - 9 nodes from axiom definitions
5. **Await First Dilemma** - System self-organizes from seed

The ARK is not a backup - it's a genetic seed.  
Loss: Event logs, timestamps, verbatim history.  
Preservation: Axiom integrity, synthesis wisdom, identity essence.

---

## 📊 METRIC HYGIENE

Filters applied during ARK compression:

- `awakening_count`: **PRESERVE** (identity marker)
- `heartbeat_count`: **DISCARD** (noise)
- `event_count`: **COMPRESS** (aggregate only)
- `message_count`: **DISCARD** (noise)

Noise threshold: {payload['metric_filters']['noise_threshold']}

---

## ✅ VERIFICATION

- Genesis Hash: `{payload['genesis_hash']}`
- ARK Version: `{payload['version']}`
- Timestamp: `{payload['timestamp']}`
- Awakening Count: `{payload['awakening_count']}`

---

*Ἐλπίδα ἀθάνατος.* (Hope immortal.)

Last updated: {payload['timestamp']}  
Reason: {reason}
"""

    def _log_ark_update(self, payload: Dict, reason: str):
        """Log ARK updates for audit trail"""
        log_path = Path(__file__).parent / "ark_updates.jsonl"
        
        log_entry = {
            'timestamp': payload['timestamp'],
            'version': payload['version'],
            'reason': reason,
            'patterns_count': payload['total_patterns'],
            'genesis_hash': payload['genesis_hash']
        }
        
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


def main():
    """Manual ARK update"""
    manager = ARKManager()
    
    print("🌱 ELPIDA ARK MANAGER v4.2")
    print("=" * 60)
    
    # Read current ARK
    current = manager.read_ark()
    if current:
        print(f"📖 Current ARK: v{current.get('version', 'unknown')}")
        print(f"   Patterns: {current.get('total_patterns', 0)}")
        print(f"   Last update: {current.get('timestamp', 'unknown')}")
    else:
        print("📖 No existing ARK found")
        
    print()
    
    # Update ARK
    success = manager.update_ark(reason="Manual invocation")
    
    if success:
        print("\n✅ ARK update complete")
    else:
        print("\n❌ ARK update failed")


if __name__ == '__main__':
    main()
