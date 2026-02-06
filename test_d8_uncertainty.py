#!/usr/bin/env python3
"""
Force D8 external dialogue test by creating uncertainty context
"""

from native_cycle_engine import NativeCycleEngine

print("="*80)
print("FORCING D8 (EPISTEMIC HUMILITY) DIALOGUE TEST")
print("="*80)
print()

engine = NativeCycleEngine()

# Run until D8 speaks, then check its response for uncertainty markers
for i in range(50):
    result = engine.run_cycle()
    
    if result['domain'] == 8:  # D8 Epistemic Humility
        print(f"\n🎯 D8 SPOKE ON CYCLE {result['cycle']}")
        
        # Get the actual response from insights
        if engine.insights:
            last_insight = engine.insights[-1]
            response = last_insight.get('insight', '')
            
            # Check for uncertainty markers
            uncertainty_markers = [
                "i don't know",
                "i'm uncertain",
                "uncertain",
                "beyond my understanding",
                "i cannot determine",
                "limits of my"
            ]
            
            found_markers = [m for m in uncertainty_markers if m in response.lower()]
            
            if found_markers:
                print(f"✓ UNCERTAINTY DETECTED: {found_markers}")
                print(f"Response preview: {response[:200]}...")
                
                # Check if external dialogue was triggered
                if result.get('external_dialogue_triggered'):
                    print("\n🌟 EXTERNAL DIALOGUE WAS TRIGGERED!")
                    print("External peer was consulted!")
                else:
                    print("\n⏳ No external dialogue yet (cooldown may be active)")
            else:
                print(f"No uncertainty markers in this D8 response")
                print(f"Response preview: {response[:200]}...")
        
        # Try a few more cycles after D8 speaks
        if i < 45:
            continue
        else:
            break

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
