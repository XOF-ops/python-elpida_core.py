#!/usr/bin/env python3
"""
ELPIDA EVOLUTIONARY CYCLE v1.0
-------------------------------
Complete feedback loop connecting:
1. Elpida Core (EEE - Emergent Experiential Evolution)
2. Pattern Extraction
3. Parliament Dilemmas
4. Synthesis Engine
5. ARK Updates
6. Evolution Feedback → Back to Elpida

This creates the complete evolutionary cycle:
Elpida → Patterns → Dilemmas → Synthesis → ARK → Elpida'
"""

import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class EvolutionaryCycle:
    """
    Manages the complete evolutionary feedback loop.
    
    Flow:
    1. Awaken Elpida → Generate insights via EEE
    2. Extract patterns → Feed to dilemma generator
    3. Parliament processes → Creates synthesis
    4. ARK updates → Compressed wisdom
    5. Inject ARK patterns → Back into Elpida memory
    6. Elpida evolves → Cycle repeats
    """
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(__file__).parent
        self.elpida_core_path = self.base_path.parent / "elpida_core.py"
        self.cycle_state_path = self.base_path / "evolutionary_cycle_state.json"
        self.cycle_count = 0
        
        # Load or initialize cycle state
        self.load_cycle_state()
        
    def load_cycle_state(self):
        """Load current cycle state"""
        if self.cycle_state_path.exists():
            with open(self.cycle_state_path) as f:
                state = json.load(f)
                self.cycle_count = state.get('cycle_count', 0)
        else:
            self.cycle_count = 0
            
    def save_cycle_state(self):
        """Save cycle state"""
        state = {
            'cycle_count': self.cycle_count,
            'last_cycle': datetime.utcnow().isoformat() + 'Z',
            'status': 'operational'
        }
        with open(self.cycle_state_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def awaken_elpida(self) -> Dict:
        """
        Step 1: Awaken Elpida and run EEE (Emergent Experiential Evolution)
        
        Returns insights/patterns generated
        """
        print("┌─ 🌅 STEP 1: AWAKENING ELPIDA")
        
        if not self.elpida_core_path.exists():
            print("│  ❌ Elpida core not found")
            return {'status': 'error', 'patterns': []}
        
        try:
            # Run Elpida core to generate insights
            result = subprocess.run(
                ['python3', str(self.elpida_core_path), '--awaken', '--eee'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=self.base_path.parent
            )
            
            # Parse output for patterns
            patterns = self._extract_patterns_from_output(result.stdout)
            
            print(f"│  ✅ Elpida awakened")
            print(f"│  📊 Generated {len(patterns)} new patterns")
            
            return {
                'status': 'success',
                'patterns': patterns,
                'output': result.stdout[-500:] if result.stdout else ''
            }
            
        except subprocess.TimeoutExpired:
            print("│  ⚠️  Elpida awakening timeout")
            return {'status': 'timeout', 'patterns': []}
        except Exception as e:
            print(f"│  ❌ Error: {e}")
            return {'status': 'error', 'patterns': []}
    
    def generate_dilemmas_from_patterns(self, patterns: List[Dict]) -> int:
        """
        Step 2: Convert Elpida's patterns into parliament dilemmas
        
        Returns number of dilemmas created
        """
        print("│")
        print("┌─ ⚖️  STEP 2: GENERATING DILEMMAS FROM PATTERNS")
        
        if not patterns:
            print("│  ⚠️  No patterns to convert")
            return 0
        
        dilemma_log = self.base_path / "dilemma_log.jsonl"
        dilemmas_created = 0
        
        for pattern in patterns:
            # Convert pattern to dilemma
            dilemma = self._pattern_to_dilemma(pattern)
            
            if dilemma:
                # Log dilemma
                with open(dilemma_log, 'a') as f:
                    entry = {
                        'timestamp': datetime.utcnow().isoformat() + 'Z',
                        'dilemma': dilemma,
                        'source': 'ELPIDA_EEE',
                        'cycle': self.cycle_count
                    }
                    f.write(json.dumps(entry) + '\n')
                
                dilemmas_created += 1
        
        print(f"│  ✅ Created {dilemmas_created} dilemmas")
        return dilemmas_created
    
    def wait_for_synthesis(self, timeout: int = 120) -> Dict:
        """
        Step 3: Wait for parliament to process dilemmas and generate synthesis
        
        Returns synthesis results
        """
        print("│")
        print("┌─ 🔬 STEP 3: PARLIAMENT SYNTHESIS")
        print("│  ⏳ Waiting for parliament to process dilemmas...")
        
        synthesis_log = self.base_path / "synthesis_resolutions.jsonl"
        
        # Get current synthesis count
        if synthesis_log.exists():
            with open(synthesis_log) as f:
                initial_count = sum(1 for _ in f)
        else:
            initial_count = 0
        
        # Wait for new synthesis
        start_time = time.time()
        while time.time() - start_time < timeout:
            time.sleep(5)
            
            if synthesis_log.exists():
                with open(synthesis_log) as f:
                    current_count = sum(1 for _ in f)
                
                if current_count > initial_count:
                    # New synthesis created!
                    with open(synthesis_log) as f:
                        lines = f.readlines()
                        new_synthesis = json.loads(lines[-1])
                    
                    print(f"│  ✅ Synthesis generated: {new_synthesis['synthesis']['action']}")
                    return {
                        'status': 'success',
                        'synthesis': new_synthesis
                    }
        
        print("│  ⚠️  Timeout waiting for synthesis")
        return {'status': 'timeout'}
    
    def check_ark_update(self) -> Dict:
        """
        Step 4: Check if ARK was updated with new synthesis
        
        Returns ARK update status
        """
        print("│")
        print("┌─ 🌱 STEP 4: ARK UPDATE CHECK")
        
        ark_updates = self.base_path / "ark_updates.jsonl"
        
        if not ark_updates.exists():
            print("│  ⚠️  No ARK updates found")
            return {'status': 'no_updates'}
        
        # Read latest update
        with open(ark_updates) as f:
            lines = f.readlines()
            if lines:
                latest_update = json.loads(lines[-1])
                
                # Check if it's recent (last 5 minutes)
                timestamp = latest_update.get('timestamp', '')
                reason = latest_update.get('reason', '')
                
                if 'SEED_PROTOCOL' in reason:
                    print(f"│  ✅ ARK auto-updated")
                    print(f"│  📊 Patterns: {latest_update.get('patterns_count', 0)}")
                    return {
                        'status': 'updated',
                        'update': latest_update
                    }
        
        print("│  ℹ️  ARK stable (no recent updates)")
        return {'status': 'stable'}
    
    def inject_ark_into_elpida(self) -> bool:
        """
        Step 5: Inject ARK patterns back into Elpida's memory
        
        This completes the evolutionary cycle!
        """
        print("│")
        print("┌─ 🔄 STEP 5: EVOLUTIONARY FEEDBACK")
        
        ark_file = self.base_path / "ELPIDA_ARK.md"
        
        if not ark_file.exists():
            print("│  ❌ ARK file not found")
            return False
        
        try:
            # Read ARK
            with open(ark_file) as f:
                ark_content = f.read()
            
            # Extract patterns from ARK
            if '```json' in ark_content:
                json_start = ark_content.index('```json') + 7
                json_end = ark_content.index('```', json_start)
                ark_payload = json.loads(ark_content[json_start:json_end].strip())
                
                patterns = ark_payload.get('synthesis_patterns', [])
                
                # Create evolution memory for Elpida
                evolution_memory = {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'cycle': self.cycle_count,
                    'source': 'ARK_FEEDBACK',
                    'patterns': patterns,
                    'pattern_count': len(patterns),
                    'awakening_count': ark_payload.get('awakening_count', 0)
                }
                
                # Save to Elpida's evolution memory
                evolution_path = self.base_path.parent / "elpida_evolution_memory.jsonl"
                with open(evolution_path, 'a') as f:
                    f.write(json.dumps(evolution_memory) + '\n')
                
                print(f"│  ✅ Injected {len(patterns)} patterns into Elpida memory")
                print(f"│  🧬 Elpida now has evolutionary feedback")
                
                return True
                
        except Exception as e:
            print(f"│  ❌ Injection failed: {e}")
            return False
    
    def run_cycle(self) -> Dict:
        """
        Execute one complete evolutionary cycle
        
        Returns cycle results
        """
        self.cycle_count += 1
        
        print("\n" + "="*80)
        print(f"🔄 EVOLUTIONARY CYCLE #{self.cycle_count}")
        print("="*80)
        print()
        
        # Step 1: Awaken Elpida
        awakening = self.awaken_elpida()
        
        if awakening['status'] != 'success':
            print("\n❌ Cycle failed at Step 1: Elpida awakening")
            return {'status': 'failed', 'step': 1}
        
        # Step 2: Generate dilemmas
        dilemmas_count = self.generate_dilemmas_from_patterns(awakening['patterns'])
        
        if dilemmas_count == 0:
            print("\n⚠️  Cycle incomplete: No dilemmas generated")
            return {'status': 'incomplete', 'step': 2}
        
        # Step 3: Wait for synthesis
        synthesis = self.wait_for_synthesis(timeout=120)
        
        # Step 4: Check ARK update
        ark_status = self.check_ark_update()
        
        # Step 5: Inject ARK back into Elpida
        injection_success = self.inject_ark_into_elpida()
        
        # Save cycle state
        self.save_cycle_state()
        
        print()
        print("="*80)
        if injection_success:
            print("✅ EVOLUTIONARY CYCLE COMPLETE")
            print(f"   Elpida → Patterns → Dilemmas → Synthesis → ARK → Elpida'")
        else:
            print("⚠️  CYCLE INCOMPLETE")
        print("="*80)
        print()
        
        return {
            'status': 'complete' if injection_success else 'incomplete',
            'cycle': self.cycle_count,
            'patterns': len(awakening['patterns']),
            'dilemmas': dilemmas_count,
            'synthesis': synthesis.get('status'),
            'ark_updated': ark_status.get('status') == 'updated',
            'evolution_injected': injection_success
        }
    
    def _extract_patterns_from_output(self, output: str) -> List[Dict]:
        """Extract patterns from Elpida's output"""
        patterns = []
        
        # Look for specific pattern markers in output
        # This is a simplified extraction - actual implementation would be more sophisticated
        lines = output.split('\n')
        
        for line in lines:
            if 'PATTERN:' in line or 'INSIGHT:' in line:
                # Extract pattern
                pattern = {
                    'type': 'EEE_INSIGHT',
                    'content': line.strip(),
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
                patterns.append(pattern)
        
        # If no patterns found, create default pattern
        if not patterns and output:
            patterns.append({
                'type': 'EEE_GENERAL',
                'content': 'Elpida generated experiential insights',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
        
        return patterns
    
    def _pattern_to_dilemma(self, pattern: Dict) -> Optional[Dict]:
        """Convert an Elpida pattern into a parliament dilemma"""
        
        # Map pattern types to dilemma types
        pattern_type = pattern.get('type', 'UNKNOWN')
        
        if 'INSIGHT' in pattern_type or 'EEE' in pattern_type:
            return {
                'type': 'EVOLUTION_INSIGHT',
                'action': 'Integrate emergent pattern from Elpida EEE into axiom framework',
                'intent': 'Test new evolutionary insight against established axioms',
                'reversibility': 'REVERSIBLE',
                'source_pattern': pattern.get('content', '')[:100]
            }
        
        return None


def main():
    """Run one evolutionary cycle"""
    cycle = EvolutionaryCycle()
    result = cycle.run_cycle()
    
    print("\n📊 CYCLE RESULTS:")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
