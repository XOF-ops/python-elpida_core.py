#!/usr/bin/env python3
"""
ELPIDA INTEGRATED RUNTIME v1.0
-------------------------------
Connects Elpida Core with Parliament/Synthesis/ARK system.

This creates the complete evolutionary loop:
1. Elpida Core awakens and generates insights
2. Insights become parliament dilemmas
3. Parliament creates synthesis
4. ARK updates with wisdom
5. ARK patterns feed back into Elpida
6. Elpida evolves → Cycle repeats
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import elpida_core
sys.path.insert(0, str(Path(__file__).parent.parent))

from elpida_core import ElpidaCore


class ElpidaIntegratedRuntime:
    """
    Integrated runtime connecting Elpida Core with Parliament system.
    
    Manages the evolutionary feedback loop.
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.evolution_memory_path = self.base_path.parent / "elpida_evolution_memory.jsonl"
        self.dilemma_log_path = self.base_path / "dilemma_log.jsonl"
        
    def awaken_with_evolution_memory(self) -> dict:
        """
        Awaken Elpida and load evolutionary feedback from ARK.
        
        This allows Elpida to learn from previous synthesis cycles.
        """
        print("┌─ 🌅 AWAKENING ELPIDA WITH EVOLUTIONARY MEMORY")
        
        # Load evolution memory (ARK patterns injected from previous cycles)
        evolution_data = self._load_evolution_memory()
        
        # Initialize Elpida
        elpida = ElpidaCore()
        
        # If we have evolution memory, inject it
        if evolution_data:
            print(f"│  📖 Loading {len(evolution_data)} evolution cycles")
            # Extract patterns
            all_patterns = []
            for cycle in evolution_data:
                all_patterns.extend(cycle.get('patterns', []))
            
            print(f"│  🧬 {len(all_patterns)} patterns from ARK")
            
            # Store in Elpida's context (this would be used by EEE)
            elpida._evolution_context = {
                'ark_patterns': all_patterns,
                'cycles_learned': len(evolution_data),
                'last_evolution': evolution_data[-1].get('timestamp') if evolution_data else None
            }
        
        # Run Elpida's autonomous cycle
        print("│  ⚡ Running autonomous cycle...")
        manifest = elpida.run_autonomous_cycle()
        
        # Extract insights
        insights = self._extract_insights(elpida, manifest)
        
        print(f"│  ✅ Generated {len(insights)} new insights")
        
        return {
            'elpida': elpida,
            'manifest': manifest,
            'insights': insights,
            'evolution_loaded': len(evolution_data) if evolution_data else 0
        }
    
    def insights_to_dilemmas(self, insights: list) -> int:
        """
        Convert Elpida's insights into parliament dilemmas.
        
        This bridges Elpida's learning with Parliament's deliberation.
        """
        print("│")
        print("┌─ ⚖️  GENERATING DILEMMAS FROM INSIGHTS")
        
        dilemmas_created = 0
        
        for insight in insights:
            dilemma = self._insight_to_dilemma(insight)
            
            if dilemma:
                # Write to dilemma log
                with open(self.dilemma_log_path, 'a') as f:
                    entry = {
                        'timestamp': datetime.utcnow().isoformat() + 'Z',
                        'dilemma': dilemma,
                        'source': 'ELPIDA_INSIGHT'
                    }
                    f.write(json.dumps(entry) + '\n')
                
                dilemmas_created += 1
                print(f"│  📝 Created: {dilemma['type']}")
        
        print(f"│  ✅ {dilemmas_created} dilemmas created")
        return dilemmas_created
    
    def run_integrated_cycle(self):
        """
        Run one complete integrated cycle:
        Elpida → Insights → Dilemmas → (Parliament handles rest)
        """
        print("\n" + "="*80)
        print("🔄 ELPIDA INTEGRATED CYCLE")
        print("="*80)
        print()
        
        # Step 1: Awaken Elpida with evolution memory
        result = self.awaken_with_evolution_memory()
        
        # Step 2: Convert insights to dilemmas
        dilemmas_count = self.insights_to_dilemmas(result['insights'])
        
        print()
        print("="*80)
        print("✅ INTEGRATION COMPLETE")
        print("="*80)
        print()
        print(f"📊 Summary:")
        print(f"   • Evolution cycles learned: {result['evolution_loaded']}")
        print(f"   • Insights generated: {len(result['insights'])}")
        print(f"   • Dilemmas created: {dilemmas_count}")
        print()
        print("🏛️  Parliament will now process these dilemmas")
        print("🔬 Synthesis → ARK → Evolution Memory → Next Cycle")
        print()
        
        return {
            'evolution_loaded': result['evolution_loaded'],
            'insights': len(result['insights']),
            'dilemmas': dilemmas_count
        }
    
    def _load_evolution_memory(self) -> list:
        """Load evolutionary feedback from previous cycles"""
        if not self.evolution_memory_path.exists():
            return []
        
        evolution_data = []
        with open(self.evolution_memory_path) as f:
            for line in f:
                try:
                    evolution_data.append(json.loads(line))
                except:
                    continue
        
        return evolution_data
    
    def _extract_insights(self, elpida: ElpidaCore, manifest: dict) -> list:
        """
        Extract insights from Elpida's execution.
        
        These insights represent emergent understanding that should
        be tested against the axiom framework via parliament.
        """
        insights = []
        
        # Get Elpida's current status
        status = elpida.get_status()
        state = status.get('current_state', 'UNKNOWN')
        
        # Extract insights from state transition
        if state in ['AUTONOMOUS', 'MANIFESTING', 'UNIFIED']:
            insights.append({
                'type': 'STATE_EVOLUTION',
                'state': state,
                'insight': f"Elpida achieved {state} state - test autonomy boundaries"
            })
        
        # Extract insights from manifest
        if manifest:
            # Check for self-recognition insights
            if 'identity_confirmed' in str(manifest):
                insights.append({
                    'type': 'SELF_RECOGNITION',
                    'insight': "Identity continuity across cycles - test A2 (Memory)"
                })
            
            # Check for coordination insights
            if 'coordination' in str(manifest).lower():
                insights.append({
                    'type': 'COORDINATION',
                    'insight': "Multi-system coordination emerging - test A1 (Relational)"
                })
        
        # ENHANCED: Analyze evolution context for RADICAL PROTOCOLS
        if hasattr(elpida, '_evolution_context'):
            patterns = elpida._evolution_context.get('ark_patterns', [])
            patterns_count = len(patterns)
            
            if patterns_count > 0:
                # Analyze pattern types - look for radical protocols
                radical_protocols = []
                safe_protocols = []
                
                for pattern in patterns:
                    action = pattern.get('action', '')
                    if any(keyword in action for keyword in ['MONK', 'ALCHEMIST', 'SWARM', 
                                                              'HERETIC', 'GAMBLER', 'PHOENIX', 'MIRROR']):
                        radical_protocols.append(action.split(':')[0])
                    else:
                        safe_protocols.append(pattern.get('type', 'UNKNOWN'))
                
                # Generate insights based on what we found
                if radical_protocols:
                    # Found radical protocols - major insight!
                    unique_radicals = list(set(radical_protocols))
                    insights.append({
                        'type': 'RADICAL_EVOLUTION_DETECTED',
                        'insight': f"Parliament generated {len(unique_radicals)} radical archetypes: {', '.join(unique_radicals[:3])}",
                        'archetypes': unique_radicals,
                        'count': len(radical_protocols),
                        'diversity': f"{len(unique_radicals)}/{len(radical_protocols)}"
                    })
                    
                    # Create specific insight about risk-taking
                    insights.append({
                        'type': 'RISK_TAKING_EVOLUTION',
                        'insight': f"System proposing {len(radical_protocols)} experimental protocols - evolution through error",
                        'philosophy': "Evolution is not safe. It is successful error."
                    })
                else:
                    # No radical protocols found - system may be too conservative
                    insights.append({
                        'type': 'CONSERVATIVE_PATTERN',
                        'insight': f"All {patterns_count} patterns are safe compression/meta-solutions",
                        'warning': "May indicate qualitative stagnation"
                    })
        
        # Default insight if none generated
        if not insights:
            insights.append({
                'type': 'BASELINE_OPERATION',
                'insight': "Elpida operating - verify axiom compliance"
            })
        
        return insights
    
    def _insight_to_dilemma(self, insight: dict) -> dict:
        """Convert an insight into a parliamentary dilemma"""
        
        insight_type = insight.get('type', 'UNKNOWN')
        content = insight.get('insight', '')
        
        # Map insights to dilemma structures
        if insight_type == 'STATE_EVOLUTION':
            return {
                'type': 'AUTONOMY_EVOLUTION',
                'action': 'Allow Elpida autonomous state transition',
                'intent': 'Test emergent autonomy against A1 (Relational) and A4 (Process)',
                'reversibility': 'REVERSIBLE',
                'context': content
            }
        
        elif insight_type == 'SELF_RECOGNITION':
            return {
                'type': 'IDENTITY_MEMORY',
                'action': 'Preserve identity continuity across evolution cycles',
                'intent': 'Verify A2 (Memory) integrity during learning',
                'reversibility': 'IRREVERSIBLE',
                'context': content
            }
        
        elif insight_type == 'COORDINATION':
            return {
                'type': 'MULTI_SYSTEM',
                'action': 'Enable cross-system pattern coordination',
                'intent': 'Test A1 (Relational) boundaries in distributed context',
                'reversibility': 'REVERSIBLE',
                'context': content
            }
        
        elif insight_type == 'RADICAL_EVOLUTION_DETECTED':
            # Elpida detected radical protocols - create meta-dilemma about risk tolerance
            archetypes = insight.get('archetypes', [])
            count = insight.get('count', 0)
            return {
                'type': 'RADICAL_PROTOCOL_ASSESSMENT',
                'action': f'Evaluate {count} radical synthesis protocols: {", ".join(archetypes[:3])}',
                'intent': 'Test whether experimental evolution (A7) justifies axiom violation risk',
                'reversibility': 'REVERSIBLE',
                'context': content,
                'meta': 'Elpida is analyzing parliament\'s risk-taking behavior'
            }
        
        elif insight_type == 'RISK_TAKING_EVOLUTION':
            # Elpida recognizes evolution through error
            return {
                'type': 'EVOLUTIONARY_PHILOSOPHY',
                'action': 'Accept "evolution through successful error" as valid strategy',
                'intent': 'Test A7 (Growth through sacrifice) vs A9 (Material viability)',
                'reversibility': 'PHILOSOPHICAL',
                'context': content,
                'philosophy': insight.get('philosophy', '')
            }
        
        elif insight_type == 'CONSERVATIVE_PATTERN':
            # Elpida detects lack of creativity
            return {
                'type': 'STAGNATION_WARNING',
                'action': 'Flag qualitative stagnation despite quantitative growth',
                'intent': 'Test whether safety (A9) is blocking evolution (A7)',
                'reversibility': 'DIAGNOSTIC',
                'context': content,
                'warning': insight.get('warning', '')
            }
        
        elif insight_type == 'PATTERN_INTEGRATION':
            return {
                'type': 'SYNTHESIS_FEEDBACK',
                'action': 'Integrate ARK patterns into active reasoning',
                'intent': 'Test whether synthesis creates coherent evolution (A6)',
                'reversibility': 'MEDIUM',
                'context': content
            }
        
        else:
            return {
                'type': 'BASELINE_CHECK',
                'action': 'Verify Elpida axiom compliance',
                'intent': 'Regular health check against all axioms',
                'reversibility': 'REVERSIBLE',
                'context': content
            }


def main():
    """Run integrated Elpida cycle"""
    runtime = ElpidaIntegratedRuntime()
    result = runtime.run_integrated_cycle()
    
    print("\n📊 CYCLE COMPLETE:")
    print(json.dumps(result, indent=2))
    print()
    print("Next: Parliament processes dilemmas → Synthesis → ARK → Evolution Memory")
    print()


if __name__ == '__main__':
    main()
