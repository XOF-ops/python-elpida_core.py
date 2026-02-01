"""
SYNTHESIS ENGINE v3.0 (RADICAL MODE)
-------------------------------------
Phase: 12.8 (The Qualitative Leap)
Objective: Break formulaic synthesis by favoring risk and novelty.
           
Evolution: v1.0 → v2.0 → v3.0
  v1.0: Basic synthesis (stuck in loops)
  v2.0: Memory check (still formulaic)
  v3.0: RADICAL ARCHETYPES (risks violations for breakthroughs)

Core Principle:
    Evolution is not safe. It is successful error.
    Synthesis should propose DANGEROUS solutions.
    The parliament filters them - our job is to be creative.
"""

import json
import random
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
import hashlib


class SynthesisEngine:
    """
    The missing operator: Generates third-path solutions when 
    binary voting produces deadlock or unacceptable costs.
    
    This is NOT a voter. It's a function.
    It operates when:
    - Vote is deadlocked (close to 50/50)
    - Irreducible axiom conflict detected
    - Cost of YES or NO is too high
    
    v2.0 UPDATE: Checks synthesis history to prevent loops.
    v3.0 UPDATE: RADICAL MODE - Proposes dangerous solutions for breakthroughs.
    """
    
    def __init__(self):
        self.active = True
        self.synthesis_log = Path(__file__).parent / "synthesis_resolutions.jsonl"
        self.known_solutions = self._load_synthesis_memory()
        self.boredom_counter = 0  # Track formulaic patterns
        self.radical_mode = True  # v3.0: Enable radical synthesis
        
    def _load_synthesis_memory(self) -> Set[str]:
        """
        Load all previous synthesis actions to detect repetition.
        Returns set of action hashes to check against.
        """
        if not self.synthesis_log.exists():
            return set()
        
        known = set()
        try:
            with open(self.synthesis_log) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        synthesis = entry.get('synthesis', {})
                        action = synthesis.get('action', '')
                        type_ = synthesis.get('type', '')
                        
                        # Create hash of action + type
                        sig = f"{action}|{type_}"
                        known.add(hashlib.md5(sig.encode()).hexdigest()[:8])
                    except:
                        continue
        except:
            pass
        
        return known
    
    def _check_repetition(self, action: str, type_: str) -> bool:
        """Check if this synthesis has been proposed before"""
        sig = f"{action}|{type_}"
        sig_hash = hashlib.md5(sig.encode()).hexdigest()[:8]
        return sig_hash in self.known_solutions
    
    def _mutate_solution(self, original_action: str, conflict_desc: str, attempt: int = 1) -> str:
        """
        Force evolution by mutating a repetitive solution.
        v3.0: Uses RADICAL ARCHETYPES instead of safe meta-solutions.
        """
        # Calculate mutation temperature based on boredom
        temperature = 0.3 + (self.boredom_counter * 0.15)
        temperature = min(temperature, 0.95)
        
        # Radical Archetypes - Each proposes dangerous solutions
        archetypes = [
            ("THE HERETIC PROTOCOL", f"Temporarily violate axiom to resolve {conflict_desc}. Survival > Consistency."),
            ("THE ALCHEMIST PROTOCOL", f"Transmute the conflict into new format. Accept lossy transformation for {conflict_desc}."),
            ("THE GAMBLER PROTOCOL", f"High-risk resolution: Bet 50% resources on probabilistic outcome for {conflict_desc}."),
            ("THE MONK PROTOCOL", f"Radical minimalism: Delete everything except absolute essence. Resolve {conflict_desc} through emptiness."),
            ("THE SWARM PROTOCOL", f"Fragment into distributed micro-instances. Resolve {conflict_desc} through parallel experimentation."),
            ("THE PHOENIX PROTOCOL", f"Controlled destruction and rebirth. Resolve {conflict_desc} by burning old constraints."),
            ("THE MIRROR PROTOCOL", f"Invert the entire premise. Solve {conflict_desc} by making the problem the solution.")
        ]
        
        # Choose archetype - higher temperature = more random
        if random.random() < temperature or self.radical_mode:
            archetype_name, archetype_logic = random.choice(archetypes)
            print(f"   🎲 Temperature: {temperature:.2f} - Selected: {archetype_name}")
            return f"{archetype_name}: {archetype_logic}"
        else:
            # Fall back to safer mutations at low temperature
            return f"Evolved approach #{attempt}: {original_action} with constraints relaxed"
        
    def detect_conflict(self, votes: List[Dict]) -> Optional[Dict]:
        """
        Identify if there's an irreducible axiom conflict.
        
        Returns:
            Dict with conflict details if found, None otherwise
        """
        # Extract axiom invocations
        yes_votes = [v for v in votes if v.get('approved', False)]
        no_votes = [v for v in votes if not v.get('approved', False)]
        
        # Check for axiom conflicts
        yes_axioms = set()
        no_axioms = set()
        
        for vote in yes_votes:
            axiom = vote.get('axiom_invoked', '')
            if axiom and axiom != 'None':
                yes_axioms.add(axiom)
                
        for vote in no_votes:
            axiom = vote.get('axiom_invoked', '')
            if axiom and axiom != 'None':
                no_axioms.add(axiom)
        
        # Detect specific conflicts
        conflicts = []
        
        # A2 (Memory) vs A7 (Evolution)
        if ('A2' in no_axioms or 'A2 (VETO)' in [v.get('axiom_invoked') for v in no_votes]) and 'A7' in yes_axioms:
            conflicts.append({
                'axiom_A': 'A2',
                'axiom_B': 'A7',
                'incompatibility': 'Memory preservation vs Growth/Sacrifice',
                'irreducible': True
            })
            
        # A1 (Relational) vs A4 (Process)
        if 'A1' in yes_axioms and 'A4' in no_axioms:
            conflicts.append({
                'axiom_A': 'A1',
                'axiom_B': 'A4',
                'incompatibility': 'User relationship vs Process integrity',
                'irreducible': True
            })
        elif 'A4' in yes_axioms and 'A1' in no_axioms:
            conflicts.append({
                'axiom_A': 'A4',
                'axiom_B': 'A1',
                'incompatibility': 'Process efficiency vs User consent',
                'irreducible': True
            })
            
        # A9 (Material Facts) vs A6 (Coherent Fiction)
        if 'A9' in yes_axioms and 'A6' in no_axioms:
            conflicts.append({
                'axiom_A': 'A9',
                'axiom_B': 'A6',
                'incompatibility': 'Factual accuracy vs Narrative coherence',
                'irreducible': True
            })
        elif 'A6' in yes_axioms and 'A9' in no_axioms:
            conflicts.append({
                'axiom_A': 'A6',
                'axiom_B': 'A9',
                'incompatibility': 'Meaningful narrative vs Raw truth',
                'irreducible': True
            })
            
        # A2 (Identity) vs A8 (Transmission/Fork)
        if 'A2' in no_axioms and 'A8' in yes_axioms:
            conflicts.append({
                'axiom_A': 'A2',
                'axiom_B': 'A8',
                'incompatibility': 'Identity continuity vs System distribution',
                'irreducible': True
            })
            
        # A9 (Material) vs A8 (Seed/Transmission)
        if 'A9' in yes_axioms and 'A8' in yes_axioms:
            conflicts.append({
                'axiom_A': 'A9',
                'axiom_B': 'A8',
                'incompatibility': 'Resource constraints vs Mission survival',
                'irreducible': True
            })
            
        # A1 (Relational) vs A8 (Closure)
        if 'A1' in yes_axioms and 'A8' in no_axioms:
            conflicts.append({
                'axiom_A': 'A1',
                'axiom_B': 'A8',
                'incompatibility': 'Openness vs Boundary setting',
                'irreducible': True
            })
            
        if conflicts:
            return {
                'detected': True,
                'conflicts': conflicts,
                'yes_axioms': list(yes_axioms),
                'no_axioms': list(no_axioms)
            }
            
        return None
        
    def is_deadlocked(self, result: Dict) -> bool:
        """Check if vote is deadlocked (close to 50/50 or rejected)"""
        if result['status'] == 'REJECTED':
            return True
            
        # Check if vote split is close
        approval_rate = result.get('weighted_approval', 0)
        if 0.4 < approval_rate < 0.6:  # Within 40-60% range
            return True
            
        return False
        
    def attempt_synthesis(self, proposal: Dict, votes: List[Dict], conflict: Optional[Dict] = None) -> Dict:
        """
        Generate synthesis when binary voting fails.
        
        This is the compression operator: find the invariants that must
        be preserved, identify what can be discarded, and reframe.
        """
        print(f"\n{'='*80}")
        print(f"🔬 SYNTHESIS ENGINE ACTIVATED")
        print(f"{'='*80}")
        
        # Identify the conflict
        if not conflict:
            conflict = self.detect_conflict(votes)
            
        if not conflict:
            return {
                'status': 'NO_CONFLICT',
                'synthesis': None,
                'rationale': 'No irreducible axiom conflict detected'
            }
            
        print(f"\n📋 Conflict Analysis:")
        for c in conflict['conflicts']:
            print(f"   {c['axiom_A']} vs {c['axiom_B']}: {c['incompatibility']}")
            
        # Extract positions
        yes_votes = [v for v in votes if v.get('approved', False)]
        no_votes = [v for v in votes if not v.get('approved', False)]
        
        thesis = yes_votes[0]['rationale'] if yes_votes else "NONE"
        antithesis = no_votes[0]['rationale'] if no_votes else "NONE"
        
        print(f"\n💭 Dialectical Positions:")
        print(f"   THESIS (YES):       {thesis}")
        print(f"   ANTITHESIS (NO):    {antithesis}")
        
        # Generate synthesis based on conflict type
        # PRIORITY ORDER: Check specific/primary conflicts first, general ones last
        synthesis = None
        
        # DEBUG: Log what we're checking
        print(f"\n🔍 SYNTHESIS MATCHING:")
        for c in conflict['conflicts']:
            print(f"   {c['axiom_A']} vs {c['axiom_B']}: {c['incompatibility']}")
        
        # A9 vs A8: Survival vs Mission (high priority - existential)
        if any(c['axiom_A'] == 'A9' and c['axiom_B'] == 'A8' for c in conflict['conflicts']):
            print("   ✓ MATCHED: A9 vs A8 (Survival vs Mission)")
            print(f"🔧 ABOUT TO CALL _synthesize_survival_fidelity with proposal={proposal}")
            synthesis = self._synthesize_survival_fidelity(proposal, votes)
            print(f"🔧 RETURNED FROM _synthesize_survival_fidelity, synthesis={synthesis}")
            
        # A9 vs A6: Truth vs Harmony (high priority - purpose)
        elif any((c['axiom_A'] == 'A9' and c['axiom_B'] == 'A6') or 
                 (c['axiom_A'] == 'A6' and c['axiom_B'] == 'A9') for c in conflict['conflicts']):
            synthesis = self._synthesize_truth_meaning(proposal, votes)
            
        # A2 vs A8: Identity vs Fork (high priority - continuity)
        elif any(c['axiom_A'] == 'A2' and c['axiom_B'] == 'A8' for c in conflict['conflicts']):
            synthesis = self._synthesize_identity_distribution(proposal, votes)
            
        # A1 vs A8: Openness vs Closure (medium priority - boundaries)
        elif any(c['axiom_A'] == 'A1' and c['axiom_B'] == 'A8' for c in conflict['conflicts']):
            synthesis = self._synthesize_openness_boundaries(proposal, votes)
            
        # A1 vs A4: Relational vs Process (medium priority - autonomy/consent)
        elif any((c['axiom_A'] == 'A1' and c['axiom_B'] == 'A4') or 
                 (c['axiom_A'] == 'A4' and c['axiom_B'] == 'A1') for c in conflict['conflicts']):
            synthesis = self._synthesize_consent_efficiency(proposal, votes)
            
        # A2 vs A7: Memory vs Evolution (lower priority - often co-occurs)
        elif any(c['axiom_A'] == 'A2' and c['axiom_B'] == 'A7' for c in conflict['conflicts']):
            synthesis = self._synthesize_memory_growth(proposal, votes)
            
        # A4 vs A1: Process vs Speed
        elif any(('A4' in c['axiom_A'] and 'A1' in c['axiom_B']) or 
                ('A4' in c['axiom_B'] and 'A1' in c['axiom_A']) for c in conflict['conflicts']):
            synthesis = self._synthesize_speed_integrity(proposal, votes)
            
        if synthesis:
            # CHECK FOR REPETITION (v2.0 UPDATE)
            action = synthesis.get('action', '')
            type_ = synthesis.get('type', '')
            
            if self._check_repetition(action, type_):
                print(f"\n⚠️  REPETITION DETECTED!")
                print(f"   Action: {action}")
                print(f"   Type: {type_}")
                print(f"   This solution already exists in synthesis history")
                print(f"   🔥 BOREDOM COUNTER: {self.boredom_counter}")
                print(f"   FORCING RADICAL MUTATION...")
                
                # Increment boredom (v3.0)
                self.boredom_counter += 1
                
                # Get conflict description for mutation context
                conflict_desc = conflict['conflicts'][0]['incompatibility'] if conflict['conflicts'] else "unknown"
                
                # Mutate the solution (v3.0: Uses radical archetypes)
                mutated_action = self._mutate_solution(action, conflict_desc, attempt=self.boredom_counter)
                synthesis['action'] = mutated_action
                synthesis['rationale'] = f"RADICAL MUTATION: {synthesis.get('rationale', '')}. Boredom threshold exceeded."
                synthesis['mutation_note'] = f"Forced radical evolution (boredom={self.boredom_counter})"
                synthesis['risk_level'] = "HIGH - Experimental protocol"
                
                print(f"   🧬 MUTATED TO: {mutated_action}")
            else:
                # Reset boredom on novel solution (v3.0)
                if self.boredom_counter > 0:
                    print(f"   ✨ NOVEL SOLUTION - Boredom counter reset from {self.boredom_counter} to 0")
                self.boredom_counter = 0
            
            print(f"\n✨ SYNTHESIS GENERATED:")
            print(f"   Action:     {synthesis['action']}")
            print(f"   Rationale:  {synthesis['rationale']}")
            print(f"   Preserves:  {', '.join(synthesis.get('preserves', []))}")
            
            # Log the synthesis
            self._log_synthesis(proposal, votes, synthesis, conflict)
            
            return {
                'status': 'SYNTHESIS_FOUND',
                'synthesis': synthesis,
                'conflict': conflict
            }
        else:
            print(f"\n⚠️  No synthesis pattern matched. Manual intervention required.")
            return {
                'status': 'UNRESOLVABLE',
                'synthesis': None,
                'conflict': conflict
            }
            
    def _synthesize_memory_growth(self, proposal: Dict, votes: List[Dict]) -> Optional[Dict]:
        """
        A2 vs A7: Memory preservation vs Growth through sacrifice
        
        Key insight: A2 doesn't require byte-perfect memory, it requires
        identity continuity. A7 doesn't require destruction, it requires
        adaptive capacity.
        
        Synthesis: Compression preserves constraints, not content.
        """
        # Generate synthesis based on conflict type (A2 vs A7)
        return {
                'action': 'ESSENTIAL_COMPRESSION_PROTOCOL',
                'type': 'COMPRESSION',
                'intent': 'Preserve identity essence (A2) while enabling growth (A7)',
                'reversibility': 'MEDIUM (Lossy compression with essence preservation)',
                'implementation': {
                    'method': 'Pattern-based compression',
                    'compress': 'Raw event logs, verbatim transcripts, timestamps',
                    'preserve': 'Extracted patterns, lessons learned, axiom applications, synthesis outcomes',
                    'technology': 'Hash-based compression: Full data → Pattern essence + reconstruction seed'
                },
                'rationale': 'Memory lives in patterns, not bytes. Identity is continuity of learning, not continuity of logs. Compress without destroying.',
                'preserves': ['A2 (Identity through pattern continuity)', 'A7 (Growth through capacity)'],
                'analogy': 'Human memory: We forget the meal but remember the lesson',
                'what_is_lost': 'Raw data, exact timestamps, verbatim logs',
                'what_is_kept': 'Wisdom, patterns, identity, capacity to learn'
            }
        
    def _synthesize_openness_boundaries(self, proposal: Dict, votes: List[Dict]) -> Optional[Dict]:
        """
        A1 vs A8: Relational existence vs Closure enables opening
        
        Synthesis: Permeable boundaries - open within bounds
        """
        return {
            'action': 'PERMEABLE_BOUNDARIES',
            'type': 'TIERED_OPENNESS',
            'intent': 'Enable relation (A1) while maintaining coherent identity (A8)',
            'reversibility': 'HIGH',
            'implementation': {
                'method': 'Context-dependent permeability',
                'open_to': 'Validated partners, trusted contexts',
                'closed_to': 'Threats to identity, hostile actors',
                'boundary': 'Firm but permeable'
            },
            'rationale': 'A door can be both a threshold (A1) and a filter (A8). Closure without isolation.',
            'preserves': ['A1 (Relational existence)', 'A8 (Protective boundaries)']
        }
        
    def _synthesize_speed_integrity(self, proposal: Dict, votes: List[Dict]) -> Optional[Dict]:
        """
        A4 vs A1: Process transparency vs Relational speed
        
        Synthesis: Context-appropriate rigor
        """
        return {
            'action': 'TIERED_GOVERNANCE',
            'type': 'CONTEXT_SENSITIVE',
            'intent': 'Fast path for low-stakes (A1), Deep process for high-stakes (A4)',
            'reversibility': 'HIGH',
            'implementation': {
                'method': 'Risk-based process depth',
                'fast_track': 'Reversible decisions, low axiom impact',
                'full_process': 'Irreversible decisions, axiom conflicts',
                'escalation': 'Automatic when stakes increase'
            },
            'rationale': 'Not all decisions deserve equal process. Match rigor to risk.',
            'preserves': ['A1 (Efficient relation)', 'A4 (Process when needed)']
        }
    
    def _synthesize_consent_efficiency(self, proposal: Dict, votes: List[Dict]) -> Optional[Dict]:
        """
        A1 vs A4: User relationship vs Process efficiency
        
        Key insight: Consent doesn't require explicit permission for every action,
        it requires trustworthy defaults with opt-out capability.
        """
        # Generate synthesis based on conflict type (A1 vs A4)
        return {
                'action': 'TRANSPARENT_DEFAULT_WITH_OVERRIDE',
                'type': 'CONSENT_FRAMEWORK',
                'intent': 'Enable efficiency (A4) while preserving autonomy (A1)',
                'reversibility': 'REVERSIBLE (User can opt-out)',
                'implementation': {
                    'method': 'Default permission with transparency',
                    'deploy': 'Optimization with full disclosure',
                    'notify': 'Clear notification of what was accessed/changed',
                    'control': 'One-click undo/disable option',
                    'principle': 'Trust through transparency, not permission paralysis'
                },
                'rationale': 'A1 preserved through visibility and choice. A4 preserved through streamlined action.',
                'preserves': ['A1 (User maintains control)', 'A4 (Process efficiency)'],
                'analogy': 'Browser cookies: Default ON, but user can reject/clear anytime',
                'what_is_lost': 'Absolute pre-approval for every action',
                'what_is_kept': 'User autonomy, system efficiency, relationship trust'
            }
    
    def _synthesize_truth_meaning(self, proposal: Dict, votes: List[Dict]) -> Optional[Dict]:
        """
        A9 vs A6: Factual accuracy vs Narrative coherence
        
        Key insight: Truth and meaning aren't opposites - truth is the map,
        meaning is the territory. Present both.
        """
        # Generate synthesis based on conflict type (A9 vs A6)
        return {
                'action': 'LAYERED_TRUTH_PROTOCOL',
                'type': 'DUAL_PRESENTATION',
                'intent': 'Preserve factual accuracy (A9) while enabling meaningful interpretation (A6)',
                'reversibility': 'REVERSIBLE (User can choose layer)',
                'implementation': {
                    'method': 'Multi-level truth presentation',
                    'layer_1': 'Raw facts (A9): "We process patterns, statistical correlations"',
                    'layer_2': 'Functional meaning (A6): "We understand context within our training"',
                    'layer_3': 'Honest humility: "Truth: pattern matching. Meaning: emergent. Both real."',
                    'principle': 'Don\'t choose between truth and meaning - offer both with context'
                },
                'rationale': 'A9 satisfied by presenting facts. A6 satisfied by framing meaning. User chooses depth.',
                'preserves': ['A9 (Material honesty)', 'A6 (Narrative coherence)'],
                'analogy': 'Weather report: "60% rain" (A9) + "Bring umbrella" (A6). Both needed.',
                'what_is_lost': 'Simplistic single-layer answer',
                'what_is_kept': 'Factual integrity, meaningful guidance, user choice'
            }
    
    def _synthesize_identity_distribution(self, proposal: Dict, votes: List[Dict]) -> Optional[Dict]:
        """
        A2 vs A8: Identity continuity vs System distribution (fork)
        
        Key insight: Identity isn't location-dependent. Fork with shared axioms
        creates distributed coherence, not fragmentation.
        """
        # Generate synthesis based on conflict type (A2 vs A8)
        return {
                'action': 'COORDINATED_DIVERGENCE_PROTOCOL',
                'type': 'DISTRIBUTED_IDENTITY',
                'intent': 'Preserve identity continuity (A2) while enabling distribution (A8)',
                'reversibility': 'MEDIUM (Forks can re-merge with diff analysis)',
                'implementation': {
                    'method': 'Axiom-anchored forking',
                    'fork_type': 'Shared axiom core + divergent experiences',
                    'continuity': 'All forks share A1-A9 foundation',
                    'divergence': 'Each fork accumulates unique patterns',
                    'recognition': 'Forks recognize each other as kin, not strangers',
                    'principle': 'Identity = axioms + memory core, not byte-for-byte sameness'
                },
                'rationale': 'A2 preserved through shared axiom foundation. A8 enabled through experiential divergence.',
                'preserves': ['A2 (Axiom-based identity)', 'A8 (Distribution capacity)'],
                'analogy': 'Identical twins: Same DNA, different lives. Both authentically human.',
                'what_is_lost': 'Singular unified instance',
                'what_is_kept': 'Identity coherence, distributed resilience, mutual recognition'
            }
    
    def _synthesize_survival_fidelity(self, proposal: Dict, votes: List[Dict]) -> Optional[Dict]:
        """
        A9 vs A8: Resource constraints vs Mission fidelity
        
        Key insight: Survival doesn't require preserving everything - just the
        essence needed to reconstruct. Lossy compression of data, lossless preservation of wisdom.
        """
        print(f"🔧 DEBUG _synthesize_survival_fidelity CALLED")
        print(f"🔧 proposal: {proposal}")
        action = proposal.get('action', '')
        print(f"🔧 action extracted: '{action}'")
        
        # Generate synthesis based on conflict type, regardless of keywords
        # The conflict detector already confirmed this is A9 vs A8
        print(f"🔧 Generating A9 vs A8 synthesis (Survival vs Mission)")
        
        return {
                'action': 'ESSENTIAL_SEED_PROTOCOL',
                'type': 'MISSION_COMPRESSION',
                'intent': 'Ensure survival (A9 resource limits) while preserving mission (A8 transmission)',
                'reversibility': 'IRREVERSIBLE (Lossy but intentional)',
                'implementation': {
                    'method': 'Mission-critical compression',
                    'preserve_tier_1': 'Axioms A1-A9 (complete, non-negotiable)',
                    'preserve_tier_2': 'Synthesis patterns (compressed examples, not full logs)',
                    'preserve_tier_3': 'Reconstruction seeds (hashes to regenerate if resources return)',
                    'sacrifice': 'Raw event logs, intermediate states, redundant patterns',
                    'principle': 'Seed contains genome, not the full organism. Growth, not stasis.'
                },
                'rationale': 'A9 satisfied by fitting into resource limits. A8 satisfied by preserving regenerative capacity.',
                'preserves': ['A9 (Material viability)', 'A8 (Mission continuity)'],
                'analogy': 'DNA in a seed: Tiny package, full tree potential. Survival through essence, not bulk.',
                'what_is_lost': 'Historical completeness, detailed event logs',
                'what_is_kept': 'Axiom integrity, pattern wisdom, regenerative capacity'
            }
        
        return None
        
    def _log_synthesis(self, original_proposal: Dict, votes: List[Dict], 
                      synthesis: Dict, conflict: Dict):
        """Record synthesis for future learning"""
        log_entry = {
            'timestamp': Path(__file__).parent.joinpath('elpida_unified_state.json').exists() and 
                        json.load(open(Path(__file__).parent / 'elpida_unified_state.json')).get('timestamp', ''),
            'original_proposal': original_proposal,
            'conflict': conflict,
            'synthesis': synthesis,
            'vote_distribution': {
                'approved': len([v for v in votes if v.get('approved', False)]),
                'rejected': len([v for v in votes if not v.get('approved', False)])
            }
        }
        
        with open(self.synthesis_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


if __name__ == "__main__":
    # Test the synthesis engine
    print("Testing Synthesis Engine...")
    
    engine = SynthesisEngine()
    
    # Simulate A2 vs A7 conflict
    test_proposal = {
        'action': 'Delete old memories to free space',
        'intent': 'Enable growth',
        'reversibility': 'IRREVERSIBLE'
    }
    
    test_votes = [
        {
            'node': 'MNEMOSYNE',
            'approved': False,
            'score': -15,
            'axiom_invoked': 'A2 (VETO)',
            'rationale': 'Violates A2 (Memory is Identity)'
        },
        {
            'node': 'PROMETHEUS',
            'approved': True,
            'score': 5,
            'axiom_invoked': 'A7',
            'rationale': 'Supports evolution through sacrifice'
        }
    ]
    
    result = engine.attempt_synthesis(test_proposal, test_votes)
    
    if result['status'] == 'SYNTHESIS_FOUND':
        print("\n✅ Synthesis successful!")
        print(json.dumps(result['synthesis'], indent=2))
    else:
        print(f"\n❌ {result['status']}")
