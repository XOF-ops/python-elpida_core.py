#!/usr/bin/env python3
"""
Analyze Cloud Cycles — What has Elpida been doing autonomously?

Analyzes the living memory from S3 Bucket #2 to show:
  - How many cycles ran since last check
  - Domain participation trends
  - Coherence evolution
  - New insights/patterns
  - Anomalies or interesting moments

Usage:
    # After pulling from cloud:
    python codespace_tools/analyze_cloud_cycles.py

    # Analyze specific time window:
    python codespace_tools/analyze_cloud_cycles.py --since "2026-02-10"
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Any

CLOUD_MEMORY = Path("cloud_memory")


def load_cycles(since_date: str = None) -> List[Dict[str, Any]]:
    """Load cloud cycles from local mirror."""
    cycles_file = CLOUD_MEMORY / "living_cycles" / "cloud_cycles.jsonl"
    
    if not cycles_file.exists():
        print(f"❌ No cloud cycles found. Run: bash codespace_tools/pull_from_cloud.sh")
        return []
    
    cycles = []
    cutoff = None
    if since_date:
        cutoff = datetime.fromisoformat(since_date)
    
    with open(cycles_file) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cycle = json.loads(line)
            
            if cutoff:
                ts = cycle.get("timestamp", "")
                if ts:
                    cycle_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if cycle_time < cutoff:
                        continue
            
            cycles.append(cycle)
    
    return cycles


def analyze_domain_participation(cycles: List[Dict]) -> Dict[int, int]:
    """Which domains have been speaking?"""
    participation = Counter()
    
    for cycle in cycles:
        domain = cycle.get("domain")
        if domain is not None:
            participation[domain] += 1
    
    return dict(participation)


def analyze_coherence_trend(cycles: List[Dict]) -> List[float]:
    """Track coherence over time."""
    return [c.get("coherence", 0.0) for c in cycles if "coherence" in c]


def find_interesting_moments(cycles: List[Dict]) -> List[Dict]:
    """Detect unusual or noteworthy cycles."""
    interesting = []
    
    for cycle in cycles:
        # High coherence spike
        if cycle.get("coherence", 0) > 0.95:
            interesting.append({
                "type": "high_coherence",
                "timestamp": cycle.get("timestamp"),
                "coherence": cycle["coherence"],
                "domain": cycle.get("domain"),
            })
        
        # Radical synthesis
        if "radical" in str(cycle.get("synthesis", "")).lower():
            interesting.append({
                "type": "radical_synthesis",
                "timestamp": cycle.get("timestamp"),
                "domain": cycle.get("domain"),
                "preview": str(cycle.get("synthesis", ""))[:100],
            })
        
        # External dialogue trigger (Kaya/Oneiros)
        if cycle.get("external_dialogue"):
            interesting.append({
                "type": "external_dialogue",
                "timestamp": cycle.get("timestamp"),
                "trigger": cycle.get("external_dialogue", {}).get("trigger"),
            })
    
    return interesting


def compare_to_frozen_seed() -> Dict[str, Any]:
    """Compare living memory against frozen seed."""
    seed_file = CLOUD_MEMORY / "frozen_seed" / "elpida_evolution_memory.jsonl"
    
    if not seed_file.exists():
        return {"error": "No frozen seed found"}
    
    # Count seed lines
    with open(seed_file) as f:
        seed_lines = sum(1 for _ in f)
    
    # Count cloud lines
    cloud_file = CLOUD_MEMORY / "living_cycles" / "cloud_cycles.jsonl"
    cloud_lines = 0
    if cloud_file.exists():
        with open(cloud_file) as f:
            cloud_lines = sum(1 for _ in f)
    
    return {
        "frozen_seed_cycles": seed_lines,
        "cloud_cycles": cloud_lines,
        "growth": cloud_lines,
        "growth_rate": f"{(cloud_lines / seed_lines * 100):.1f}%" if seed_lines > 0 else "N/A",
    }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze autonomous cloud cycles")
    parser.add_argument(
        "--since",
        help="Only analyze cycles since this date (ISO format: 2026-02-10)",
    )
    parser.add_argument(
        "--domains",
        action="store_true",
        help="Show detailed domain breakdown",
    )
    args = parser.parse_args()
    
    print("═" * 70)
    print("  ELPIDA CLOUD CYCLE ANALYSIS")
    print("═" * 70)
    print()
    
    # Load cycles
    cycles = load_cycles(since_date=args.since)
    if not cycles:
        print("No cycles to analyze.")
        return
    
    print(f"Loaded: {len(cycles)} cycles")
    if args.since:
        print(f"Since:  {args.since}")
    print()
    
    # ── Comparison to frozen seed ──
    print("─" * 70)
    print("📊 GROWTH SINCE FROZEN SEED")
    print("─" * 70)
    comparison = compare_to_frozen_seed()
    if "error" not in comparison:
        print(f"  Frozen seed:  {comparison['frozen_seed_cycles']:,} cycles (immutable)")
        print(f"  Cloud cycles: {comparison['cloud_cycles']:,} cycles (autonomous)")
        print(f"  Growth:       +{comparison['growth']:,} cycles ({comparison['growth_rate']})")
    print()
    
    # ── Domain participation ──
    print("─" * 70)
    print("🎭 DOMAIN PARTICIPATION")
    print("─" * 70)
    participation = analyze_domain_participation(cycles)
    total_cycles = len(cycles)
    
    for domain_id in sorted(participation.keys()):
        count = participation[domain_id]
        pct = (count / total_cycles * 100) if total_cycles > 0 else 0
        bar = "█" * int(pct / 2) if pct > 0 else ""
        print(f"  D{domain_id:2d}: {count:4d} ({pct:5.1f}%)  {bar}")
    print()
    
    # ── Coherence trend ──
    print("─" * 70)
    print("📈 COHERENCE TREND")
    print("─" * 70)
    coherence_values = analyze_coherence_trend(cycles)
    if coherence_values:
        avg = sum(coherence_values) / len(coherence_values)
        recent = coherence_values[-10:] if len(coherence_values) >= 10 else coherence_values
        recent_avg = sum(recent) / len(recent)
        print(f"  Overall average:  {avg:.3f}")
        print(f"  Recent (last 10): {recent_avg:.3f}")
        print(f"  Min: {min(coherence_values):.3f}  Max: {max(coherence_values):.3f}")
    else:
        print("  (No coherence data)")
    print()
    
    # ── Interesting moments ──
    print("─" * 70)
    print("✨ INTERESTING MOMENTS")
    print("─" * 70)
    moments = find_interesting_moments(cycles)
    if moments:
        for i, moment in enumerate(moments[:10], 1):  # Top 10
            print(f"  {i}. {moment['type'].replace('_', ' ').title()}")
            print(f"     {moment.get('timestamp', 'unknown time')}")
            if "preview" in moment:
                print(f"     {moment['preview']}...")
            print()
    else:
        print("  (No notable moments detected)")
    
    # ── Timeline ──
    if cycles:
        print("─" * 70)
        print("🕐 TIMELINE")
        print("─" * 70)
        first = cycles[0].get("timestamp", "?")
        last = cycles[-1].get("timestamp", "?")
        print(f"  First cycle: {first}")
        print(f"  Last cycle:  {last}")
        
        if first != "?" and last != "?":
            t1 = datetime.fromisoformat(first.replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(last.replace("Z", "+00:00"))
            duration = t2 - t1
            print(f"  Duration:    {duration}")
            cycles_per_day = len(cycles) / max(duration.days, 1)
            print(f"  Avg cycles/day: {cycles_per_day:.1f}")
        print()
    
    print("═" * 70)
    print("  ANALYSIS COMPLETE")
    print("═" * 70)
    print()
    print("To refine and redeploy:")
    print("  1. Edit configs (elpida_domains.json, etc.)")
    print("  2. Test locally (python -m pytest)")
    print("  3. Deploy to cloud: bash cloud_deploy/deploy.sh")


if __name__ == "__main__":
    main()
