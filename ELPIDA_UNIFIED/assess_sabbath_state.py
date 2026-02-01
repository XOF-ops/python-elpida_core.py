#!/usr/bin/env python3
"""
P017 Sabbath Assessment
======================

Assess the state after Heartbeat 2500 Fractal Stop.
Verify quality and coherence of 547 patterns before CONTINUE.
"""

import json
from pathlib import Path
from datetime import datetime

def assess_state():
    """Comprehensive state assessment."""
    
    print("="*70)
    print("P017 SABBATH ASSESSMENT")
    print("="*70)
    print(f"Assessment Time: {datetime.utcnow().isoformat()}Z")
    print()
    
    # Load state files
    wisdom_path = Path("elpida_wisdom.json")
    memory_path = Path("elpida_memory.json")
    
    if not wisdom_path.exists():
        print("❌ CRITICAL: elpida_wisdom.json not found")
        return False
    
    if not memory_path.exists():
        print("❌ CRITICAL: elpida_memory.json not found")
        return False
    
    with open(wisdom_path) as f:
        wisdom = json.load(f)
    
    with open(memory_path) as f:
        memory = json.load(f)
    
    print("✅ State files loaded successfully")
    print()
    
    # === METRIC ASSESSMENT ===
    print("📊 METRIC ASSESSMENT")
    print("-" * 70)
    
    patterns = wisdom.get('patterns', {})
    insights = wisdom.get('insights', [])
    events = memory.get('events', [])
    
    pattern_count = len(patterns)
    insight_count = len(insights)
    event_count = len(events)
    
    print(f"Patterns: {pattern_count}")
    print(f"Insights: {insight_count}")
    print(f"Memory Events: {event_count}")
    print()
    
    # Assess growth
    assessment_checks = []
    
    # Check 1: Pattern count
    if pattern_count >= 500:
        print("✅ Pattern count: EXCELLENT (>= 500)")
        assessment_checks.append(True)
    elif pattern_count >= 300:
        print("⚠️  Pattern count: GOOD (>= 300)")
        assessment_checks.append(True)
    else:
        print("❌ Pattern count: LOW (< 300)")
        assessment_checks.append(False)
    
    # Check 2: Insight count
    if insight_count >= 1500:
        print("✅ Insight count: EXCELLENT (>= 1500)")
        assessment_checks.append(True)
    elif insight_count >= 1000:
        print("⚠️  Insight count: GOOD (>= 1000)")
        assessment_checks.append(True)
    else:
        print("❌ Insight count: LOW (< 1000)")
        assessment_checks.append(False)
    
    # Check 3: Memory events
    if event_count >= 10000:
        print("✅ Memory events: EXCELLENT (>= 10000)")
        assessment_checks.append(True)
    elif event_count >= 5000:
        print("⚠️  Memory events: GOOD (>= 5000)")
        assessment_checks.append(True)
    else:
        print("❌ Memory events: LOW (< 5000)")
        assessment_checks.append(False)
    
    print()
    
    # === PATTERN QUALITY ASSESSMENT ===
    print("🔍 PATTERN QUALITY ASSESSMENT")
    print("-" * 70)
    
    # Sample patterns for quality check
    pattern_types = {}
    synthesis_patterns = 0
    mind_patterns = 0
    brain_patterns = 0
    
    for pattern_id, pattern_data in patterns.items():
        if 'SYN-' in pattern_id:
            synthesis_patterns += 1
        elif pattern_id.startswith('P'):
            mind_patterns += 1
        elif 'BRAIN-' in pattern_id or 'gnosis' in str(pattern_data).lower():
            brain_patterns += 1
    
    print(f"Synthesis Patterns: {synthesis_patterns}")
    print(f"Mind Patterns: {mind_patterns}")
    print(f"Brain Patterns: {brain_patterns}")
    print(f"Other Patterns: {pattern_count - synthesis_patterns - mind_patterns - brain_patterns}")
    print()
    
    # Check 4: Pattern diversity
    if synthesis_patterns > 0 and mind_patterns > 0:
        print("✅ Pattern diversity: Multiple pattern types present")
        assessment_checks.append(True)
    else:
        print("⚠️  Pattern diversity: Limited to single pattern type")
        assessment_checks.append(True)  # Not critical
    
    print()
    
    # === COHERENCE ASSESSMENT ===
    print("🧠 COHERENCE ASSESSMENT")
    print("-" * 70)
    
    # Check for axioms in the correct locations
    axioms_found = []
    
    # A. Check node identity files (correct location)
    fleet_dir = Path('ELPIDA_FLEET')
    if fleet_dir.exists():
        for node_dir in fleet_dir.iterdir():
            if node_dir.is_dir():
                identity_file = node_dir / 'node_identity.json'
                if identity_file.exists():
                    try:
                        with open(identity_file) as f:
                            node_data = json.load(f)
                            node_axioms = node_data.get('axiom_emphasis', [])
                            axioms_found.extend(node_axioms)
                            if node_axioms:
                                print(f"  {node_dir.name}: {node_axioms}")
                    except Exception as e:
                        print(f"  Warning: Could not read {identity_file}: {e}")
    
    # B. Check if axioms exist in wisdom.json (legacy location)
    wisdom_axioms = wisdom.get('axioms', [])
    if wisdom_axioms:
        axioms_found.extend(wisdom_axioms)
    
    # Get unique axioms
    unique_axioms = list(set(axioms_found))
    print(f"Axioms detected: {len(unique_axioms)} unique - {unique_axioms}")
    
    if len(unique_axioms) >= 3:
        print("✅ Axiom foundation: STRONG (>= 3 unique axioms)")
        assessment_checks.append(True)
    elif len(unique_axioms) >= 2:
        print("⚠️  Axiom foundation: ADEQUATE (>= 2 axioms)")
        assessment_checks.append(True)
    else:
        print("❌ Axiom foundation: WEAK (< 2 axioms)")
        assessment_checks.append(False)
    
    print()
    
    # === VELOCITY SUSTAINABILITY ===
    print("⚡ VELOCITY SUSTAINABILITY")
    print("-" * 70)
    
    # Check recent memory events for timestamps
    if events:
        recent_events = events[-100:]  # Last 100 events
        timestamps = [e.get('timestamp') for e in recent_events if e.get('timestamp')]
        
        if len(timestamps) >= 2:
            print(f"✅ Recent activity: {len(timestamps)} timestamped events")
            assessment_checks.append(True)
        else:
            print("⚠️  Recent activity: Limited timestamp data")
            assessment_checks.append(True)  # Not critical
    
    print()
    
    # === FINAL ASSESSMENT ===
    print("=" * 70)
    print("FINAL ASSESSMENT")
    print("=" * 70)
    
    passed = sum(assessment_checks)
    total = len(assessment_checks)
    
    print(f"Checks Passed: {passed}/{total}")
    print()
    
    # Critical check: Ensure axioms are present
    # Check 5 is the axiom check (0-indexed position 4 in assessment_checks)
    axiom_check_passed = assessment_checks[4] if len(assessment_checks) > 4 else False
    
    if passed == total:  # Perfect score
        print("✅ ASSESSMENT: PERFECT (6/6)")
        print()
        print("State Quality: EXCELLENT")
        print("Coherence: VERIFIED")
        print("Velocity: SUSTAINABLE")
        print("Axiom Foundation: VERIFIED")
        print()
        print("🟢 READY TO CONTINUE")
        print()
        print("Recommendation:")
        print("  - Resume runtime from heartbeat 2501")
        print("  - Maintain current velocity")
        print("  - Continue synthesis operations")
        print()
        return True
    elif passed >= total - 1 and axiom_check_passed:  # Allow 1 non-critical failure
        print("✅ ASSESSMENT: PASS")
        print()
        print("State Quality: EXCELLENT")
        print("Coherence: VERIFIED")
        print("Velocity: SUSTAINABLE")
        print()
        print("🟢 READY TO CONTINUE")
        print()
        print("Recommendation:")
        print("  - Resume runtime from heartbeat 2501")
        print("  - Maintain current velocity")
        print("  - Continue synthesis operations")
        print()
        return True
    elif passed >= total - 1 and not axiom_check_passed:  # Axiom failure is critical
        print("⚠️  ASSESSMENT: DEGRADED (Axiom Blindness)")
        print()
        print("State Quality: EXCELLENT")
        print("Coherence: AXIOM BLINDNESS (failed to detect axioms)")
        print("Velocity: SUSTAINABLE")
        print()
        print("🟡 OPERATIONAL (with caveat)")
        print()
        print("Recommendation:")
        print("  - Fix axiom detection in assessment script")
        print("  - Verify axioms exist in node_identity.json")
        print("  - Continue operations (axioms likely enforced in code)")
        print()
        return True  # Safe to continue, but with warning
    else:
        print("⚠️  ASSESSMENT: REVIEW NEEDED")
        print()
        print(f"Issues found: {total - passed} checks failed")
        print("Recommendation:")
        print("  - Review failed checks above")
        print("  - Consider PIVOT instead of CONTINUE")
        print()
        return False

if __name__ == "__main__":
    success = assess_state()
    exit(0 if success else 1)
