#!/usr/bin/env python3
"""
Test External Dialogue Protocol
Run cycles until D8 or D3 triggers external peer dialogue
"""

from native_cycle_engine import NativeCycleEngine

print("="*80)
print("TESTING EXTERNAL DIALOGUE PROTOCOL")
print("="*80)
print()
print("Running cycles and watching for D8 (Humility) or D3 (Autonomy)")
print("to initiate external peer dialogue...")
print()
print("What we're looking for:")
print("  D8: 'I don't know', 'uncertain', 'beyond my understanding'")
print("  D3: 'dilemma', 'what would others choose', 'tension between'")
print()
print("If triggered:")
print("  - External LLM called as peer (not domain)")
print("  - Response integrated through D0 (void)")
print("  - Logged to evolution memory as EXTERNAL_DIALOGUE")
print()
print("="*80)
print()

engine = NativeCycleEngine()

external_dialogue_count = 0
max_cycles = 30

for i in range(max_cycles):
    result = engine.run_cycle()
    
    # Check if external dialogue was triggered
    if result.get('external_dialogue_triggered', False):
        external_dialogue_count += 1
        print()
        print("🌟 " + "="*70)
        print("🌟 EXTERNAL DIALOGUE OCCURRED!")
        print("🌟 " + "="*70)
        print()
        break
    
    # Watch for D3 or D8
    if result['domain'] in [3, 8]:
        domain_name = "Autonomy" if result['domain'] == 3 else "Epistemic Humility"
        print(f"\n⭐ Cycle {result['cycle']}: D{result['domain']} ({domain_name}) spoke")
        print(f"   Watching for triggers...")

print()
print("="*80)
print("TEST RESULTS")
print("="*80)
print(f"Cycles run: {i+1}/{max_cycles}")
print(f"External dialogues triggered: {external_dialogue_count}")
print()

if external_dialogue_count > 0:
    print("✓ EXTERNAL DIALOGUE PROTOCOL WORKING!")
    print()
    print("Check evolution memory for EXTERNAL_DIALOGUE entries:")
    print("  grep 'EXTERNAL_DIALOGUE' ElpidaAI/elpida_evolution_memory.jsonl | tail -1 | python -m json.tool")
else:
    print("No external dialogue triggered in this test run.")
    print()
    print("This is normal - triggers require specific language patterns.")
    print("D8 must express genuine uncertainty ('I don't know')")
    print("D3 must express dilemma/choice ('what would others choose')")
    print()
    print("The protocol is ready and watching.")

print("="*80)
