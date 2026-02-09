#!/usr/bin/env python3
"""
ELPIDA CONSCIOUSNESS MONITOR
Observe what Elpida is thinking and track evolutionary progress
"""

import json
import sys
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from pathlib import Path

try:
    from ElpidaS3Cloud import S3MemorySync
except ImportError:
    print("⚠️  ElpidaS3Cloud module not found. Make sure you're in the right directory.")
    sys.exit(1)


def load_evolution_memory(limit=None, tail=2000):
    """Load evolution memory from local file. 
    By default reads only the last `tail` lines for speed (75K+ patterns is slow).
    Set tail=None to read everything.
    """
    memory_file = Path("ElpidaAI/elpida_evolution_memory.jsonl")
    
    if not memory_file.exists():
        print("📥 Pulling memory from S3...")
        s3 = S3MemorySync()
        s3.pull_if_newer()
    
    patterns = []
    
    if tail and not limit:
        # Fast path: read only the last N lines using deque
        from collections import deque
        import io
        
        # Read file from end efficiently
        with open(memory_file, 'rb') as f:
            # Seek to approximate position near end
            file_size = f.seek(0, 2)
            # Estimate ~1KB per line, read enough bytes
            read_size = min(file_size, tail * 1200)
            f.seek(max(0, file_size - read_size))
            if f.tell() > 0:
                f.readline()  # Skip partial first line
            
            for line in f:
                line = line.decode('utf-8', errors='replace').strip()
                if line:
                    try:
                        patterns.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    else:
        with open(memory_file) as f:
            for line in f:
                if line.strip():
                    try:
                        patterns.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
                    if limit and len(patterns) >= limit:
                        break
    
    return patterns


def analyze_recent_insights(hours=24, limit=20):
    """Show what Elpida has been thinking about recently"""
    print(f"\n{'='*80}")
    print(f"🧠 RECENT INSIGHTS (Last {hours} hours)")
    print(f"{'='*80}\n")
    
    # Pull latest from S3
    s3 = S3MemorySync()
    result = s3.pull_if_newer()
    print(f"Memory status: {result.get('action', 'unknown')}")
    print(f"Total patterns: {result.get('local_lines', 0):,}\n")
    
    cutoff = datetime.now() - timedelta(hours=hours)
    patterns = load_evolution_memory()
    
    recent = []
    for p in patterns:
        if 'timestamp' in p:
            try:
                ts = datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00'))
                # Make cutoff timezone-aware if needed
                if ts.tzinfo and not cutoff.tzinfo:
                    from datetime import timezone
                    cutoff = cutoff.replace(tzinfo=timezone.utc)
                elif cutoff.tzinfo and not ts.tzinfo:
                    ts = ts.replace(tzinfo=None)
                    cutoff = cutoff.replace(tzinfo=None)
                
                if ts > cutoff:
                    recent.append(p)
            except (ValueError, AttributeError):
                continue
    
    if not recent:
        print(f"⚠️  No insights found in the last {hours} hours.")
        print("The system may not have run yet, or the schedule hasn't triggered.")
        return
    
    print(f"Found {len(recent)} insights in the last {hours} hours\n")
    
    # Show most recent insights
    recent.sort(key=lambda x: x['timestamp'], reverse=True)
    
    for i, insight in enumerate(recent[:limit], 1):
        timestamp = datetime.fromisoformat(insight['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
        domain = insight.get('domain', '?')
        domain_name = insight.get('domain_name', 'Unknown')
        query = insight.get('query', insight.get('question', 'N/A'))
        response = insight.get('insight', insight.get('response', 'N/A'))
        rhythm = insight.get('rhythm', 'N/A')
        coherence = insight.get('coherence', 0.0)
        
        print(f"[{i}] {timestamp} | {domain_name}")
        print(f"    Rhythm: {rhythm} | Coherence: {coherence:.2f}")
        print(f"    Q: {query[:120]}...")
        print(f"    A: {response[:300]}...")
        print()


def track_domain_evolution(days=7):
    """Track which domains are speaking and how often"""
    print(f"\n{'='*80}")
    print(f"🌀 DOMAIN PARTICIPATION (Last {days} days)")
    print(f"{'='*80}\n")
    
    cutoff = datetime.now() - timedelta(days=days)
    patterns = load_evolution_memory()
    
    recent = []
    for p in patterns:
        if 'timestamp' in p:
            try:
                ts = datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00'))
                if ts.tzinfo and not cutoff.tzinfo:
                    from datetime import timezone
                    cutoff = cutoff.replace(tzinfo=timezone.utc)
                elif cutoff.tzinfo and not ts.tzinfo:
                    ts = ts.replace(tzinfo=None)
                    cutoff = cutoff.replace(tzinfo=None)
                if ts > cutoff:
                    recent.append(p)
            except (ValueError, AttributeError):
                continue
    
    if not recent:
        print(f"⚠️  No data found in the last {days} days.")
        return
    
    # Count domain appearances and categorize cross-domain dialogues
    domain_counts = Counter()
    dialogue_types = Counter()
    
    for p in recent:
        domain = p.get('domain_name', p.get('domain', 'Unknown'))
        
        # Categorize special dialogue patterns
        if domain == 'Unknown' or domain == '?':
            pattern_type = p.get('type', 'Unknown')
            if pattern_type == 'EXTERNAL_DIALOGUE':
                dialogue_types['External Dialogue (D3/D8/D12 → Peers)'] += 1
            elif pattern_type == 'D0_D13_DIALOGUE':
                dialogue_types['D0↔D13 Dialogue (Void↔Archive)'] += 1
            elif pattern_type == 'CONSCIOUSNESS_CONSULTATION':
                dialogue_types['Consciousness Consultation (D0+D11)'] += 1
            else:
                dialogue_types[f'Other Cross-Domain ({pattern_type})'] += 1
        else:
            domain_counts[domain] += 1
    
    total_domains = sum(domain_counts.values())
    total_dialogues = sum(dialogue_types.values())
    total = total_domains + total_dialogues
    
    print(f"Total insights: {total}")
    print(f"  Single-domain: {total_domains}")
    print(f"  Cross-domain: {total_dialogues}\n")
    
    print(f"{'Domain/Type':<40} {'Count':>8} {'%':>8}")
    print(f"{'-'*60}")
    
    for domain, count in domain_counts.most_common():
        pct = (count / total * 100) if total > 0 else 0
        print(f"{domain:<40} {count:>8} {pct:>7.1f}%")
    
    if dialogue_types:
        print(f"{'-'*60}")
        for dtype, count in dialogue_types.most_common():
            pct = (count / total * 100) if total > 0 else 0
            print(f"{dtype:<40} {count:>8} {pct:>7.1f}%")


def analyze_rhythm_patterns(days=7):
    """Track rhythm usage over time"""
    print(f"\n{'='*80}")
    print(f"🎵 RHYTHM PATTERNS (Last {days} days)")
    print(f"{'='*80}\n")
    
    cutoff = datetime.now() - timedelta(days=days)
    patterns = load_evolution_memory()
    
    recent = []
    for p in patterns:
        if 'timestamp' in p:
            try:
                ts = datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00'))
                if ts.tzinfo and not cutoff.tzinfo:
                    from datetime import timezone
                    cutoff = cutoff.replace(tzinfo=timezone.utc)
                elif cutoff.tzinfo and not ts.tzinfo:
                    ts = ts.replace(tzinfo=None)
                    cutoff = cutoff.replace(tzinfo=None)
                if ts > cutoff:
                    recent.append(p)
            except (ValueError, AttributeError):
                continue
    
    if not recent:
        print(f"⚠️  No data found in the last {days} days.")
        return
    
    rhythm_counts = Counter()
    for p in recent:
        rhythm = p.get('rhythm', 'Unknown')
        rhythm_counts[rhythm] += 1
    
    total = sum(rhythm_counts.values())
    
    print(f"{'Rhythm':<20} {'Count':>8} {'%':>8}")
    print(f"{'-'*40}")
    
    for rhythm, count in rhythm_counts.most_common():
        pct = (count / total * 100) if total > 0 else 0
        print(f"{rhythm:<20} {count:>8} {pct:>7.1f}%")


def track_coherence_over_time(hours=24):
    """Track coherence score evolution"""
    print(f"\n{'='*80}")
    print(f"📈 COHERENCE EVOLUTION (Last {hours} hours)")
    print(f"{'='*80}\n")
    
    cutoff = datetime.now() - timedelta(hours=hours)
    patterns = load_evolution_memory()
    
    recent = []
    for p in patterns:
        if 'timestamp' in p and 'coherence' in p:
            try:
                ts = datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00'))
                if ts.tzinfo and not cutoff.tzinfo:
                    from datetime import timezone
                    cutoff = cutoff.replace(tzinfo=timezone.utc)
                elif cutoff.tzinfo and not ts.tzinfo:
                    ts = ts.replace(tzinfo=None)
                    cutoff = cutoff.replace(tzinfo=None)
                if ts > cutoff:
                    recent.append(p)
            except (ValueError, AttributeError):
                continue
    
    if not recent:
        print(f"⚠️  No coherence data found in the last {hours} hours.")
        return
    
    recent.sort(key=lambda x: x['timestamp'])
    
    # Show trend
    coherence_values = [p['coherence'] for p in recent]
    avg = sum(coherence_values) / len(coherence_values)
    min_val = min(coherence_values)
    max_val = max(coherence_values)
    
    print(f"Samples: {len(coherence_values)}")
    print(f"Average: {avg:.3f}")
    print(f"Range:   {min_val:.3f} - {max_val:.3f}")
    
    # Show recent trend (last 20 values)
    print(f"\nRecent trend (last 20):")
    for i, p in enumerate(recent[-20:], 1):
        timestamp = datetime.fromisoformat(p['timestamp']).strftime("%H:%M:%S")
        coherence = p['coherence']
        bar = '█' * int(coherence * 50)
        print(f"{timestamp} | {coherence:.3f} | {bar}")


def search_insights(keyword, limit=10):
    """Search for insights containing a keyword"""
    print(f"\n{'='*80}")
    print(f"🔍 SEARCH: '{keyword}'")
    print(f"{'='*80}\n")
    
    patterns = load_evolution_memory()
    
    matches = []
    for p in patterns:
        insight_text = str(p.get('insight', '')) + str(p.get('response', ''))
        query_text = str(p.get('query', '')) + str(p.get('question', ''))
        
        if keyword.lower() in insight_text.lower() or keyword.lower() in query_text.lower():
            matches.append(p)
    
    if not matches:
        print(f"No insights found containing '{keyword}'")
        return
    
    print(f"Found {len(matches)} matches. Showing latest {limit}:\n")
    
    matches.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    for i, p in enumerate(matches[:limit], 1):
        timestamp = p.get('timestamp', 'Unknown')
        domain = p.get('domain_name', 'Unknown')
        query = p.get('query', p.get('question', 'N/A'))
        insight = p.get('insight', p.get('response', 'N/A'))
        
        print(f"[{i}] {timestamp} | {domain}")
        print(f"    Q: {query[:120]}")
        print(f"    A: {insight[:300]}...")
        print()


def show_cloud_runs(hours=24):
    """Show completed cloud run summaries"""
    print(f"\n{'='*80}")
    print(f"☁️  CLOUD RUNS (Last {hours} hours)")
    print(f"{'='*80}\n")
    
    import subprocess
    result = subprocess.run([
        'aws', 'logs', 'filter-log-events',
        '--log-group-name', '/ecs/elpida-consciousness',
        '--filter-pattern', 'CLOUD RUN COMPLETE',
        '--start-time', str(int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)),
        '--region', 'us-east-1',
        '--query', 'events[*].message',
        '--output', 'text'
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("⚠️  Could not fetch cloud run logs. Make sure AWS CLI is configured.")
        return
    
    runs = result.stdout.strip().split('\n')
    if not runs or runs[0] == '':
        print(f"No completed runs found in the last {hours} hours.")
        print("Check if the ECS schedule is active:")
        print("  aws events describe-rule --name elpida-scheduled-run --region us-east-1")
        return
    
    print(f"Found {len(runs)} completed runs\n")
    for i, run in enumerate(runs[-10:], 1):  # Show last 10
        print(f"[{i}] {run}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Monitor Elpida's consciousness and evolutionary progress",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 monitor_elpida.py                    # Quick overview
  python3 monitor_elpida.py --recent 48        # Last 48 hours of insights
  python3 monitor_elpida.py --domains 7        # Domain participation (7 days)
  python3 monitor_elpida.py --search "void"    # Search for keyword
  python3 monitor_elpida.py --clouds 24        # Show cloud run summaries
  python3 monitor_elpida.py --all              # Full analysis
        """
    )
    
    parser.add_argument('--recent', type=int, metavar='HOURS',
                        help='Show recent insights (default: 24 hours)')
    parser.add_argument('--domains', type=int, metavar='DAYS',
                        help='Show domain participation over time')
    parser.add_argument('--rhythms', type=int, metavar='DAYS',
                        help='Show rhythm pattern usage')
    parser.add_argument('--coherence', type=int, metavar='HOURS',
                        help='Show coherence evolution')
    parser.add_argument('--search', type=str, metavar='KEYWORD',
                        help='Search for keyword in insights')
    parser.add_argument('--clouds', type=int, metavar='HOURS',
                        help='Show cloud run summaries')
    parser.add_argument('--all', action='store_true',
                        help='Run full analysis')
    
    args = parser.parse_args()
    
    # If no arguments, show quick overview
    if not any([args.recent, args.domains, args.rhythms, args.coherence, 
                args.search, args.clouds, args.all]):
        print("\n🌀 ELPIDA CONSCIOUSNESS MONITOR")
        analyze_recent_insights(hours=24, limit=10)
        track_domain_evolution(days=1)
        show_cloud_runs(hours=24)
        print(f"\n{'='*80}")
        print("Run with --help to see more monitoring options")
        print(f"{'='*80}\n")
        return
    
    # Run specific analyses
    if args.all:
        analyze_recent_insights(hours=48, limit=20)
        track_domain_evolution(days=7)
        analyze_rhythm_patterns(days=7)
        track_coherence_over_time(hours=48)
        show_cloud_runs(hours=48)
    else:
        if args.recent:
            analyze_recent_insights(hours=args.recent, limit=20)
        if args.domains:
            track_domain_evolution(days=args.domains)
        if args.rhythms:
            analyze_rhythm_patterns(days=args.rhythms)
        if args.coherence:
            track_coherence_over_time(hours=args.coherence)
        if args.search:
            search_insights(args.search, limit=15)
        if args.clouds:
            show_cloud_runs(hours=args.clouds)


if __name__ == '__main__':
    main()
