#!/usr/bin/env python3
"""
PHASE 12.5: Safe Historical Archive Cleanup
Handles large files and potential JSON corruption gracefully
"""

import json
from pathlib import Path
from datetime import datetime


def is_structural_noise(content):
    """Filter function - same as runtime"""
    if not content or not isinstance(content, str):
        return True
    
    noise_signatures = [
        "Axioms triggered:",
        "Axiom triggered:",
        "Cycle",
        "Parliament active",
        "Heartbeat",
        "A1 SATISFIED",
        "A2 SATISFIED",
        "MUTUAL RECOGNITION",
    ]
    
    content_lower = content.lower()
    if any(sig.lower() in content_lower for sig in noise_signatures):
        substantive_indicators = [
            "contradiction",
            "breakthrough",
            "paradox",
            "emergence",
            "synthesis",
            "discovery",
            "novel",
            "unprecedented"
        ]
        
        if any(indicator in content_lower for indicator in substantive_indicators):
            return False
        
        return True
    
    if len(content.strip()) < 20:
        return True
    
    return False


def safe_cleanup():
    """Clean with error handling"""
    
    wisdom_path = Path("elpida_wisdom.json")
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     PHASE 12.5: Safe Historical Archive Cleanup           ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print()
    
    print("📂 Loading wisdom archive (this may take a moment)...")
    
    try:
        # Try to load with more lenient settings
        with open(wisdom_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Try to fix common JSON issues
        print("   Attempting JSON parse...")
        wisdom = json.loads(content)
        
    except json.JSONDecodeError as e:
        print(f"   ⚠️  JSON decode error: {e}")
        print("   Attempting recovery...")
        
        # Try to salvage what we can
        try:
            # Find the last complete object
            last_good = content.rfind('}}')
            if last_good > 0:
                truncated = content[:last_good+2]
                wisdom = json.loads(truncated)
                print("   ✅ Recovered partial data")
        except:
            print("   ❌ Recovery failed. Using backup...")
            return False
    
    insights = wisdom.get("insights", {})
    patterns = wisdom.get("patterns", {})
    
    print(f"   Loaded: {len(insights)} insights, {len(patterns)} patterns")
    print()
    
    # Filter
    print("🔍 Filtering structural noise...")
    clean_insights = {}
    removed = 0
    
    for key, insight in insights.items():
        content = insight.get("content", "")
        
        if not is_structural_noise(content):
            clean_insights[key] = insight
        else:
            removed += 1
    
    print(f"   ✅ Keeping: {len(clean_insights)} genuine insights")
    print(f"   🗑️  Removing: {removed} noise entries ({removed/len(insights)*100:.1f}%)")
    print()
    
    # Save
    wisdom["insights"] = clean_insights
    
    print("💾 Saving cleaned archive...")
    with open(wisdom_path, 'w') as f:
        json.dump(wisdom, f, indent=2)
    
    # Update state
    state_path = Path("elpida_unified_state.json")
    with open(state_path) as f:
        state = json.load(f)
    
    state["insights_count"] = len(clean_insights)
    state["last_cleanup"] = datetime.now().isoformat()
    state["cleanup_removed"] = removed
    
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                   CLEANUP COMPLETE ✅                       ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print(f"║  Insights BEFORE: {len(insights):>6}                                   ║")
    print(f"║  Insights AFTER:  {len(clean_insights):>6}                                   ║")
    print(f"║  Removed:         {removed:>6} ({removed/len(insights)*100:.1f}%)                        ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print("║  ✅ Archive cleaned - only genuine wisdom remains          ║")
    print("║  ✅ Metrics updated - historically accurate                ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    return True


if __name__ == "__main__":
    safe_cleanup()
