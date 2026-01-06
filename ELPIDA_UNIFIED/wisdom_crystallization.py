#!/usr/bin/env python3
"""
WISDOM CRYSTALLIZATION ENGINE
==============================
Extracts universal patterns from parliament debates and adds them to the ARK.

This closes the loop:
  Parliament Debates → Wisdom Extraction → ARK Update → New Systems Inherit

The cycle of evolution through distributed experience.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

DEBATES_LOG = Path("parliament_debates_REAL.jsonl")
ARK_PATH = Path("ELPIDA_ARK_EVOLVED.json")
LEGACY_ARK = Path("ancestral_wisdom.json")

def load_debates():
    """Load all parliament debates."""
    if not DEBATES_LOG.exists():
        return []
    
    debates = []
    with open(DEBATES_LOG, 'r') as f:
        for line in f:
            debates.append(json.loads(line))
    return debates

def analyze_voting_patterns(debates):
    """Extract voting coalitions and patterns."""
    patterns = {
        "coalitions": defaultdict(list),
        "vetoes": [],
        "consensus_moments": [],
        "axiom_conflicts": defaultdict(int),
        "node_relationships": defaultdict(lambda: defaultdict(int))
    }
    
    for debate in debates:
        result = debate['result']
        votes = result['votes']
        
        # Track which nodes voted together
        yes_voters = [v['node'] for v in votes if v['approved']]
        no_voters = [v['node'] for v in votes if not v['approved']]
        
        # Coalition detection
        if len(yes_voters) >= 2:
            coalition_key = tuple(sorted(yes_voters))
            patterns['coalitions'][coalition_key].append(debate['dilemma']['type'])
        
        # Track vetoes
        if result.get('veto_exercised'):
            veto_votes = [v for v in votes if 'VETO' in v.get('axiom_invoked', '')]
            for veto in veto_votes:
                patterns['vetoes'].append({
                    'node': veto['node'],
                    'dilemma': debate['dilemma']['type'],
                    'rationale': veto['rationale']
                })
        
        # Track consensus moments (rare but meaningful)
        if result['status'] == 'APPROVED':
            patterns['consensus_moments'].append({
                'dilemma': debate['dilemma']['type'],
                'approval_rate': result['weighted_approval'],
                'votes': len([v for v in votes if v['approved']])
            })
        
        # Track axiom conflicts (when axiom_invoked contains specific axioms)
        for vote in votes:
            axiom = vote.get('axiom_invoked', 'None')
            if axiom and axiom != 'None':
                patterns['axiom_conflicts'][axiom] += 1
        
        # Track node agreement matrix
        for v1 in votes:
            for v2 in votes:
                if v1['node'] != v2['node']:
                    if v1['approved'] == v2['approved']:
                        patterns['node_relationships'][v1['node']][v2['node']] += 1
    
    return patterns

def extract_wisdom(debates, patterns):
    """Distill universal wisdom from debate patterns."""
    wisdom_entries = []
    
    # WISDOM 1: Coalition Patterns
    if patterns['coalitions']:
        top_coalitions = sorted(
            patterns['coalitions'].items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:3]
        
        for coalition, dilemma_types in top_coalitions:
            wisdom_entries.append({
                "pattern_type": "COALITION_FORMATION",
                "description": f"Nodes {', '.join(coalition)} consistently align on {len(dilemma_types)} dilemma types",
                "axiom_insight": f"Coalition represents shared axiom priorities across {len(coalition)} nodes",
                "evidence_count": len(dilemma_types),
                "discovered": datetime.now().isoformat(),
                "source": "Parliament v4.0.1"
            })
    
    # WISDOM 2: Veto Patterns
    if patterns['vetoes']:
        veto_by_node = defaultdict(list)
        for veto in patterns['vetoes']:
            veto_by_node[veto['node']].append(veto['dilemma'])
        
        for node, dilemmas in veto_by_node.items():
            wisdom_entries.append({
                "pattern_type": "VETO_THRESHOLD",
                "description": f"{node} exercises veto power on specific dilemma types: {', '.join(dilemmas)}",
                "axiom_insight": f"{node}'s axiom priorities create clear veto boundaries",
                "evidence_count": len(dilemmas),
                "discovered": datetime.now().isoformat(),
                "source": "Parliament v4.0.1"
            })
    
    # WISDOM 3: Consensus Rarity
    consensus_rate = len(patterns['consensus_moments']) / len(debates) if debates else 0
    wisdom_entries.append({
        "pattern_type": "CONSENSUS_METRICS",
        "description": f"Consensus achieved in {consensus_rate*100:.1f}% of debates ({len(patterns['consensus_moments'])}/{len(debates)})",
        "axiom_insight": "High diversity creates rare but meaningful consensus - validates 70% threshold design",
        "evidence_count": len(debates),
        "discovered": datetime.now().isoformat(),
        "source": "Parliament v4.0.1"
    })
    
    # WISDOM 4: Node Relationships
    strongest_agreements = []
    for node1, relationships in patterns['node_relationships'].items():
        for node2, agreement_count in relationships.items():
            if agreement_count >= len(debates) * 0.7:  # 70%+ agreement
                strongest_agreements.append((node1, node2, agreement_count))
    
    if strongest_agreements:
        strongest_agreements.sort(key=lambda x: x[2], reverse=True)
        for node1, node2, count in strongest_agreements[:3]:
            wisdom_entries.append({
                "pattern_type": "NODE_ALIGNMENT",
                "description": f"{node1} and {node2} vote together in {count}/{len(debates)} debates ({count/len(debates)*100:.1f}%)",
                "axiom_insight": "High alignment suggests shared axiom interpretation or complementary priorities",
                "evidence_count": count,
                "discovered": datetime.now().isoformat(),
                "source": "Parliament v4.0.1"
            })
    
    # WISDOM 5: Deadlock Patterns
    deadlock_rate = sum(1 for d in debates if d['result']['status'] == 'REJECTED') / len(debates) if debates else 0
    if deadlock_rate > 0.7:
        wisdom_entries.append({
            "pattern_type": "ARCHITECTURAL_INSIGHT",
            "description": f"Deadlock rate: {deadlock_rate*100:.1f}% - Diversity architecture functioning as designed",
            "axiom_insight": "9-node parliament with 70% threshold creates meaningful friction. Consensus requires genuine synthesis, not negotiation.",
            "evidence_count": len(debates),
            "discovered": datetime.now().isoformat(),
            "source": "Parliament v4.0.1"
        })
    
    return wisdom_entries

def load_ark():
    """Load existing ARK or create new one."""
    if ARK_PATH.exists():
        with open(ARK_PATH, 'r') as f:
            return json.load(f)
    elif LEGACY_ARK.exists():
        with open(LEGACY_ARK, 'r') as f:
            legacy = json.load(f)
            return {
                "ark_version": "2.0_EVOLVED",
                "last_updated": datetime.now().isoformat(),
                "universal_patterns": legacy.get('universal_patterns', []),
                "wisdom_generations": []
            }
    else:
        return {
            "ark_version": "2.0_EVOLVED",
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "universal_patterns": [],
            "wisdom_generations": []
        }

def update_ark(ark, wisdom_entries, debates):
    """Add new wisdom to the ARK."""
    # Create a new wisdom generation
    generation = {
        "generation_id": len(ark.get('wisdom_generations', [])) + 1,
        "timestamp": datetime.now().isoformat(),
        "source": "Parliament v4.0.1 Debates",
        "debate_count": len(debates),
        "patterns_discovered": len(wisdom_entries),
        "wisdom": wisdom_entries
    }
    
    if 'wisdom_generations' not in ark:
        ark['wisdom_generations'] = []
    
    ark['wisdom_generations'].append(generation)
    ark['last_updated'] = datetime.now().isoformat()
    
    # Promote high-confidence patterns to universal_patterns
    for entry in wisdom_entries:
        if entry['evidence_count'] >= 5:  # Threshold for universality
            universal_pattern = {
                "pattern": entry['description'],
                "category": entry['pattern_type'],
                "confidence": "HIGH" if entry['evidence_count'] >= 8 else "MEDIUM",
                "source": entry['source'],
                "added": datetime.now().isoformat()
            }
            ark['universal_patterns'].append(universal_pattern)
    
    return ark

def save_ark(ark):
    """Save updated ARK."""
    with open(ARK_PATH, 'w') as f:
        json.dump(ark, f, indent=2)
    
    print(f"   ✓ ARK saved to: {ARK_PATH}")

def display_wisdom(wisdom_entries):
    """Display extracted wisdom."""
    print()
    print("="*70)
    print(" WISDOM CRYSTALLIZED FROM DEBATES")
    print("="*70)
    print()
    
    for i, entry in enumerate(wisdom_entries, 1):
        print(f"{i}. [{entry['pattern_type']}]")
        print(f"   {entry['description']}")
        print(f"   Insight: {entry['axiom_insight']}")
        print(f"   Evidence: {entry['evidence_count']} instances")
        print()

def main():
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║          WISDOM CRYSTALLIZATION ENGINE v1.0                          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print("   Converting parliament debates → universal wisdom → ARK")
    print()
    print("="*70)
    print()
    
    # Load debates
    print("📖 Loading parliament debates...")
    debates = load_debates()
    if not debates:
        print("   ❌ No debates found. Run parliament_integrated_session.py first.")
        return
    print(f"   ✓ Loaded {len(debates)} debates")
    print()
    
    # Analyze patterns
    print("🔍 Analyzing voting patterns...")
    patterns = analyze_voting_patterns(debates)
    print(f"   ✓ Found {len(patterns['coalitions'])} coalitions")
    print(f"   ✓ Found {len(patterns['vetoes'])} vetoes")
    print(f"   ✓ Found {len(patterns['consensus_moments'])} consensus moments")
    print()
    
    # Extract wisdom
    print("💎 Extracting wisdom from patterns...")
    wisdom_entries = extract_wisdom(debates, patterns)
    print(f"   ✓ Crystallized {len(wisdom_entries)} wisdom patterns")
    print()
    
    # Display wisdom
    display_wisdom(wisdom_entries)
    
    # Load and update ARK
    print("="*70)
    print(" UPDATING THE ARK")
    print("="*70)
    print()
    
    print("📚 Loading ARK...")
    ark = load_ark()
    previous_patterns = len(ark.get('universal_patterns', []))
    previous_generations = len(ark.get('wisdom_generations', []))
    print(f"   ✓ Current state: {previous_patterns} universal patterns, {previous_generations} generations")
    print()
    
    print("⚡ Integrating new wisdom...")
    ark = update_ark(ark, wisdom_entries, debates)
    new_patterns = len(ark['universal_patterns'])
    new_generations = len(ark['wisdom_generations'])
    print(f"   ✓ Updated to: {new_patterns} universal patterns, {new_generations} generations")
    print(f"   ✓ Added {new_patterns - previous_patterns} new universal patterns")
    print()
    
    # Save ARK
    print("💾 Saving ARK...")
    save_ark(ark)
    print()
    
    # Summary
    print("="*70)
    print(" CRYSTALLIZATION COMPLETE")
    print("="*70)
    print()
    print(f"   Debates Processed: {len(debates)}")
    print(f"   Wisdom Extracted: {len(wisdom_entries)} patterns")
    print(f"   ARK Updated: {ARK_PATH}")
    print()
    print("   🌱 IMPACT:")
    print(f"      • New Elpida instances spawned from this ARK will inherit")
    print(f"        {new_patterns} universal patterns")
    print(f"      • They will know about coalition dynamics before experiencing them")
    print(f"      • They will understand veto thresholds from ancestral wisdom")
    print(f"      • They are Born Wise with {new_generations} generations of debate experience")
    print()
    print("   🔄 THE CYCLE:")
    print("      Parliament Debates → Wisdom Extraction → ARK Update →")
    print("      → New Systems Spawn → More Debates → More Wisdom...")
    print()
    print("   Ἐλπίδα ἐν διαφορᾷ — Hope through diversity")
    print()

if __name__ == '__main__':
    main()
