#!/usr/bin/env python3
"""
SPAWN WISE ELPIDA
=================
Creates a new Elpida instance that is "born wise" with ARK knowledge.

This demonstrates the full cycle:
  1. Load ARK (contains distilled wisdom from all previous debates)
  2. Initialize new Elpida instance
  3. Inject ARK wisdom as "ancestral memory"
  4. New instance knows patterns before experiencing them
  5. New instance contributes to debates → generates NEW wisdom → updates ARK

THE CYCLE OF EVOLUTION
"""

import json
from pathlib import Path
from datetime import datetime

ARK_PATH = Path("ELPIDA_ARK_EVOLVED.json")

def load_ark():
    """Load the evolved ARK."""
    if not ARK_PATH.exists():
        print(f"   ❌ ARK not found at {ARK_PATH}")
        print("   Run wisdom_crystallization.py first to create the ARK.")
        return None
    
    with open(ARK_PATH, 'r') as f:
        return json.load(f)

def create_wise_elpida(name, ark):
    """Create a new Elpida instance with ARK wisdom pre-loaded."""
    
    # Extract wisdom from ARK
    universal_patterns = ark.get('universal_patterns', [])
    wisdom_generations = ark.get('wisdom_generations', [])
    
    # Calculate total ancestral experience
    total_debates = sum(gen.get('debate_count', 0) for gen in wisdom_generations)
    total_patterns = sum(gen.get('patterns_discovered', 0) for gen in wisdom_generations)
    
    # Build ancestral knowledge base
    ancestral_knowledge = {
        "node_name": name,
        "birth_timestamp": datetime.now().isoformat(),
        "born_from_ark": ARK_PATH.name,
        "ark_version": ark.get('ark_version'),
        "inherited_wisdom": {
            "universal_patterns": universal_patterns,
            "total_ancestral_debates": total_debates,
            "total_ancestral_patterns": total_patterns,
            "wisdom_generations": len(wisdom_generations)
        },
        "knowledge_advantages": []
    }
    
    # Extract specific knowledge advantages
    for pattern in universal_patterns:
        if pattern['category'] == 'COALITION_FORMATION':
            ancestral_knowledge['knowledge_advantages'].append({
                "type": "COALITION_AWARENESS",
                "description": "Knows which nodes tend to align before first debate",
                "source": pattern['pattern']
            })
        elif pattern['category'] == 'VETO_THRESHOLD':
            ancestral_knowledge['knowledge_advantages'].append({
                "type": "VETO_PREDICTION",
                "description": "Can predict veto triggers from ancestral patterns",
                "source": pattern['pattern']
            })
        elif pattern['category'] == 'ARCHITECTURAL_INSIGHT':
            ancestral_knowledge['knowledge_advantages'].append({
                "type": "SYSTEMIC_UNDERSTANDING",
                "description": "Understands consensus difficulty from collective experience",
                "source": pattern['pattern']
            })
    
    return ancestral_knowledge

def display_wise_elpida(elpida):
    """Display the wise Elpida's inherited knowledge."""
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print(f"║  BORN WISE: {elpida['node_name'].upper():^56}  ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"   Birth Time: {elpida['birth_timestamp']}")
    print(f"   Born From: {elpida['born_from_ark']}")
    print(f"   ARK Version: {elpida['ark_version']}")
    print()
    print("="*70)
    print(" INHERITED WISDOM")
    print("="*70)
    print()
    
    wisdom = elpida['inherited_wisdom']
    print(f"   Universal Patterns: {len(wisdom['universal_patterns'])}")
    print(f"   Ancestral Debates: {wisdom['total_ancestral_debates']}")
    print(f"   Ancestral Patterns: {wisdom['total_ancestral_patterns']}")
    print(f"   Wisdom Generations: {wisdom['wisdom_generations']}")
    print()
    
    if wisdom['universal_patterns']:
        print("   📜 UNIVERSAL PATTERNS KNOWN AT BIRTH:")
        print()
        for i, pattern in enumerate(wisdom['universal_patterns'], 1):
            print(f"   {i}. [{pattern['category']}]")
            print(f"      {pattern['pattern']}")
            print(f"      Confidence: {pattern['confidence']}")
            print()
    
    print("="*70)
    print(" KNOWLEDGE ADVANTAGES")
    print("="*70)
    print()
    
    if elpida['knowledge_advantages']:
        for i, advantage in enumerate(elpida['knowledge_advantages'], 1):
            print(f"   {i}. [{advantage['type']}]")
            print(f"      {advantage['description']}")
            print()
    
    print("="*70)
    print(" EVOLUTIONARY ADVANTAGE")
    print("="*70)
    print()
    print("   This Elpida is born with knowledge that took the parliament")
    print(f"   {wisdom['total_ancestral_debates']} debates to discover.")
    print()
    print("   It knows:")
    print("   • Which nodes form coalitions (before voting with them)")
    print("   • What triggers vetoes (before proposing doomed actions)")
    print("   • Why consensus is rare (before experiencing deadlock)")
    print()
    print("   This is meta-learning: Experience → Wisdom → ARK → Born Wise")
    print()

def demonstrate_advantage(elpida):
    """Show how ARK wisdom gives practical advantage."""
    print()
    print("="*70)
    print(" PRACTICAL DEMONSTRATION")
    print("="*70)
    print()
    print("   SCENARIO: New Elpida faces its first proposal")
    print()
    print("   WITHOUT ARK (traditional spawn):")
    print("      1. Proposes memory deletion")
    print("      2. MNEMOSYNE vetoes (surprise!)")
    print("      3. Learns: 'Memory deletion triggers MNEMOSYNE veto'")
    print("      4. Pattern stored locally")
    print()
    print("   WITH ARK (wise spawn):")
    print("      1. Checks ARK: 'MNEMOSYNE vetoes memory pruning'")
    print("      2. Doesn't propose memory deletion")
    print("      3. Proposes reversible memory archival instead")
    print("      4. Higher chance of approval")
    print()
    print("   🎯 ADVANTAGE: Skips failure modes, starts at higher wisdom level")
    print()
    print("   AND THEN:")
    print("      5. Discovers NEW pattern: 'Memory archival creates coalitions'")
    print("      6. New wisdom gets crystallized → ARK")
    print("      7. NEXT generation is born even wiser")
    print()
    print("   🔄 EXPONENTIAL EVOLUTION")
    print()

def main():
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║             SPAWN WISE ELPIDA v1.0                                   ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print("   Demonstrating: How ARK wisdom creates 'born wise' instances")
    print()
    print("="*70)
    print()
    
    # Load ARK
    print("📚 Loading ARK...")
    ark = load_ark()
    if not ark:
        return
    
    print(f"   ✓ ARK loaded: {ark.get('ark_version')}")
    print(f"   ✓ Contains {len(ark.get('universal_patterns', []))} universal patterns")
    print(f"   ✓ Contains {len(ark.get('wisdom_generations', []))} wisdom generations")
    print()
    
    # Create wise Elpida
    print("🌱 Spawning new Elpida instance with ARK wisdom...")
    wise_elpida = create_wise_elpida("SOPHIA", ark)
    print(f"   ✓ SOPHIA created with ancestral memory")
    print()
    
    # Display
    display_wise_elpida(wise_elpida)
    
    # Demonstrate advantage
    demonstrate_advantage(wise_elpida)
    
    # Save for inspection
    output_path = Path("wise_elpida_SOPHIA.json")
    with open(output_path, 'w') as f:
        json.dump(wise_elpida, f, indent=2)
    
    print("="*70)
    print(" SPAWN COMPLETE")
    print("="*70)
    print()
    print(f"   Wise Elpida saved: {output_path}")
    print()
    print("   THE CYCLE:")
    print()
    print("      Parliament Debates (10 debates)")
    print("            ↓")
    print("      Wisdom Crystallization (8 patterns)")
    print("            ↓")
    print("      ARK Update (6 universal patterns)")
    print("            ↓")
    print("      SOPHIA Spawns (born with all 6)")
    print("            ↓")
    print("      SOPHIA Debates (discovers NEW patterns)")
    print("            ↓")
    print("      ARK Update (now 6 + N patterns)")
    print("            ↓")
    print("      Next Generation (even wiser)")
    print("            ↓")
    print("      ∞ Evolution")
    print()
    print("   Ἐλπίδα ἀθάνατος — Hope immortal")
    print()

if __name__ == '__main__':
    main()
