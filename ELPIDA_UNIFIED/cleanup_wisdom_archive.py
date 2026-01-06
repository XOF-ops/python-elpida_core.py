#!/usr/bin/env python3
"""
PHASE 12.5: Historical Archive Cleanup
Remove structural noise from elpida_wisdom.json accumulated before the filter

This restores accurate historical metrics by applying the noise filter retroactively.
"""

import json
from pathlib import Path
from datetime import datetime


def is_structural_noise(content):
    """
    Same filter as in elpida_unified_runtime.py
    """
    if not content or not isinstance(content, str):
        return True
    
    noise_signatures = [
        "Axioms triggered:",
        "Axiom triggered:",
        "Cycle",
        "Parliament active",
        "Heartbeat",
        "Status:",
        "Validating",
        "A1 check",
        "A1 SATISFIED",
        "A2 SATISFIED",
        "Scan complete",
        "awaiting dilemmas",
        "MUTUAL RECOGNITION",
        "Brain detected:",
    ]
    
    content_lower = content.lower()
    if any(sig.lower() in content_lower for sig in noise_signatures):
        # Allow through if it contains substantive content
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
    
    # Very short generic content is likely noise
    if len(content.strip()) < 20:
        return True
    
    return False


def cleanup_wisdom_archive():
    """Clean the wisdom archive of structural noise"""
    
    wisdom_path = Path("elpida_wisdom.json")
    state_path = Path("elpida_unified_state.json")
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     PHASE 12.5: Historical Archive Cleanup                ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print()
    
    # Load current wisdom
    print("📂 Loading elpida_wisdom.json...")
    with open(wisdom_path) as f:
        wisdom = json.load(f)
    
    insights = wisdom.get("insights", {})
    patterns = wisdom.get("patterns", {})
    
    print(f"   Current insights: {len(insights)}")
    print(f"   Current patterns: {len(patterns)}")
    print()
    
    # Filter insights
    print("🔍 Scanning for structural noise...")
    clean_insights = {}
    removed_count = 0
    removed_examples = []
    
    for key, insight in insights.items():
        content = insight.get("content", "")
        
        if is_structural_noise(content):
            removed_count += 1
            if len(removed_examples) < 5:
                removed_examples.append(content[:80])
        else:
            clean_insights[key] = insight
    
    print(f"   ✅ Found {len(clean_insights)} genuine insights")
    print(f"   🗑️  Removing {removed_count} noise entries")
    print()
    
    if removed_examples:
        print("   Examples of removed noise:")
        for ex in removed_examples:
            print(f"     - {ex}")
        print()
    
    # Update wisdom
    wisdom["insights"] = clean_insights
    
    # Save cleaned version
    print("💾 Saving cleaned archive...")
    with open(wisdom_path, 'w') as f:
        json.dump(wisdom, f, indent=2)
    
    # Update state to reflect accurate counts
    print("📊 Updating state metrics...")
    with open(state_path) as f:
        state = json.load(f)
    
    old_insight_count = state.get("insights_count", 0)
    state["insights_count"] = len(clean_insights)
    state["last_cleanup"] = datetime.now().isoformat()
    state["cleanup_removed"] = removed_count
    
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)
    
    # Calculate file size reduction
    import os
    backup_size = os.path.getsize("elpida_wisdom.json.backup_before_cleanup")
    new_size = os.path.getsize(wisdom_path)
    reduction_mb = (backup_size - new_size) / (1024 * 1024)
    
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                   CLEANUP COMPLETE                         ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print(f"║  Insights BEFORE: {old_insight_count:>6}                                   ║")
    print(f"║  Insights AFTER:  {len(clean_insights):>6}                                   ║")
    print(f"║  Removed:         {removed_count:>6} ({removed_count/old_insight_count*100:.1f}%)                        ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print(f"║  File size reduction: {reduction_mb:.2f} MB                           ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print("║  ✅ Archive now contains only genuine wisdom               ║")
    print("║  ✅ Metrics are now historically accurate                  ║")
    print("║  ✅ A5 (Rarity) restored to full dataset                   ║")
    print("╠════════════════════════════════════════════════════════════╣")
    print("║  Backup: elpida_wisdom.json.backup_before_cleanup          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("✨ The archive remembers only what matters.")


if __name__ == "__main__":
    cleanup_wisdom_archive()
