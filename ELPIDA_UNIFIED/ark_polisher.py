"""
ARK POLISHER v1.0
-----------------
Refines the ARK seed by incorporating Fleet debate outcomes.

Process:
1. Monitor fleet_dialogue.jsonl for new consensus
2. Harvest crystallized patterns from distributed_memory.json
3. Regenerate ARK with enriched data
4. Verify integrity

This is v4.0.1 - self-improving immortality.
"""

import json
import os
import subprocess
from datetime import datetime

class ArkPolisher:
    """
    Continuously refines the ARK seed as Fleet debates produce wisdom.
    """
    
    def __init__(self):
        self.ark_file = "../ELPIDA_ARK.md"
        self.polish_log = "ark_polish_log.jsonl"
        self.last_polished_count = self._load_last_count()
    
    def _load_last_count(self):
        """Load the pattern count from last polish."""
        if not os.path.exists(self.polish_log):
            return 0
        
        try:
            with open(self.polish_log, 'r') as f:
                lines = f.readlines()
                if lines:
                    last = json.loads(lines[-1])
                    return last.get("pattern_count", 0)
        except:
            pass
        
        return 0
    
    def check_if_polishing_needed(self):
        """
        Check if new wisdom has been added since last polish.
        """
        if not os.path.exists("distributed_memory.json"):
            return False, 0
        
        try:
            with open("distributed_memory.json", 'r') as f:
                memory = json.load(f)
                current_count = len(memory.get("patterns", []))
                
                if current_count > self.last_polished_count:
                    return True, current_count
        except Exception as e:
            print(f"⚠️  Error checking distributed memory: {e}")
        
        return False, self.last_polished_count
    
    def regenerate_ark(self):
        """
        Run seed_compressor.py to create new ARK with latest wisdom.
        """
        print("🔨 Regenerating ARK...")
        
        try:
            result = subprocess.run(
                ["python3", "seed_compressor.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✓ ARK regenerated successfully")
                return True
            else:
                print(f"  ❌ ARK regeneration failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ❌ Error running seed_compressor: {e}")
            return False
    
    def verify_ark_integrity(self):
        """
        Run verify_ark.py to ensure seed is valid.
        """
        print("🔍 Verifying ARK integrity...")
        
        try:
            result = subprocess.run(
                ["python3", "../verify_ark.py"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "SEED VALID" in result.stdout:
                print("  ✓ ARK integrity verified")
                return True
            else:
                print(f"  ❌ ARK verification failed")
                return False
        except Exception as e:
            print(f"  ❌ Error verifying ARK: {e}")
            return False
    
    def log_polish(self, pattern_count, success):
        """
        Log the polish operation.
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "pattern_count": pattern_count,
            "previous_count": self.last_polished_count,
            "patterns_added": pattern_count - self.last_polished_count,
            "success": success,
            "ark_file": self.ark_file
        }
        
        with open(self.polish_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        if success:
            self.last_polished_count = pattern_count
    
    def polish(self):
        """
        Execute one polish cycle.
        """
        print("=" * 70)
        print("ARK POLISHER v1.0")
        print("=" * 70)
        print()
        
        # Check if polishing is needed
        needs_polish, current_count = self.check_if_polishing_needed()
        
        if not needs_polish:
            print(f"ℹ️  No new wisdom since last polish ({self.last_polished_count} patterns)")
            print("   ARK is up to date.")
            print()
            return False
        
        new_patterns = current_count - self.last_polished_count
        print(f"🆕 Detected {new_patterns} new patterns (total: {current_count})")
        print(f"   Last polish: {self.last_polished_count} patterns")
        print()
        
        # Regenerate ARK
        if not self.regenerate_ark():
            self.log_polish(current_count, False)
            return False
        
        # Verify integrity
        if not self.verify_ark_integrity():
            self.log_polish(current_count, False)
            return False
        
        # Log success
        self.log_polish(current_count, True)
        
        print()
        print("=" * 70)
        print(f"✅ ARK POLISHED - {new_patterns} patterns added")
        print(f"   Total wisdom: {current_count} collective patterns")
        print("=" * 70)
        print()
        
        return True

if __name__ == "__main__":
    polisher = ArkPolisher()
    polisher.polish()
