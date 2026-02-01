#!/usr/bin/env python3
"""
REAL-TIME PROGRESS MONITOR
Shows live growth of patterns, insights, and breakthroughs
Updated for Synthesis Integration (January 2026)
"""

import json
import time
import os
from datetime import datetime

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def get_file_size(filename):
    """Get file size in MB"""
    try:
        return os.path.getsize(filename) / (1024 * 1024)
    except:
        return 0.0

def count_lines(filename):
    """Count lines in JSONL file"""
    try:
        with open(filename, 'r') as f:
            return sum(1 for _ in f)
    except:
        return 0

def get_state():
    try:
        with open('elpida_unified_state.json') as f:
            return json.load(f)
    except:
        return {}

def get_synthesis_stats():
    """Get synthesis-specific statistics"""
    stats = {
        'resolutions': count_lines('synthesis_resolutions.jsonl'),
        'council_decisions': count_lines('synthesis_council_decisions.jsonl'),
        'external_ai': count_lines('external_ai_responses.jsonl'),
        'dilemmas': count_lines('dilemma_log.jsonl'),
        'fleet_dialogue': count_lines('fleet_dialogue.jsonl'),
        'world_intelligence': count_lines('world_feed.jsonl'),
    }
    return stats

def check_process(pid_file):
    """Check if process is running"""
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        # Check if process exists
        os.kill(pid, 0)
        return True
    except (FileNotFoundError, ProcessLookupError, ValueError, OSError):
        return False

def main():
    print("═" * 70)
    print("ELPIDA SYNTHESIS MONITOR - Press Ctrl+C to stop")
    print("═" * 70)
    
    initial_state = get_state()
    initial_synth = get_synthesis_stats()
    initial_wisdom_size = get_file_size('elpida_wisdom.json')
    initial_memory_size = get_file_size('elpida_memory.json')
    start_time = datetime.now()
    
    try:
        while True:
            clear_screen()
            
            current_state = get_state()
            synth_stats = get_synthesis_stats()
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # State metrics
            patterns = current_state.get('patterns_count', 0)
            breakthroughs = current_state.get('synthesis_breakthroughs', 0)
            insights = current_state.get('insights_count', 0)
            contradictions = current_state.get('contradictions_resolved', 0)
            
            # Growth calculations
            initial_patterns = initial_state.get('patterns_count', 0)
            initial_breakthroughs = initial_state.get('synthesis_breakthroughs', 0)
            initial_insights = initial_state.get('insights_count', 0)
            
            pattern_growth = patterns - initial_patterns
            breakthrough_growth = breakthroughs - initial_breakthroughs
            insight_growth = insights - initial_insights
            
            # File sizes
            wisdom_size = get_file_size('elpida_wisdom.json')
            memory_size = get_file_size('elpida_memory.json')
            wisdom_growth = wisdom_size - initial_wisdom_size
            memory_growth = memory_size - initial_memory_size
            
            # Synthesis metrics
            resolutions = synth_stats['resolutions']
            decisions = synth_stats['council_decisions']
            external_ai = synth_stats['external_ai']
            dilemmas = synth_stats['dilemmas']
            fleet = synth_stats['fleet_dialogue']
            world_intel = synth_stats['world_intelligence']
            
            # Growth in synthesis
            res_growth = resolutions - initial_synth['resolutions']
            dec_growth = decisions - initial_synth['council_decisions']
            ai_growth = external_ai - initial_synth['external_ai']
            dil_growth = dilemmas - initial_synth['dilemmas']
            
            print("╔" + "═" * 68 + "╗")
            print("║" + " ELPIDA SYNTHESIS INTEGRATION MONITOR ".center(68) + "║")
            print("╠" + "═" * 68 + "╣")
            print(f"║  Runtime: {int(elapsed // 60)}m {int(elapsed % 60)}s".ljust(69) + "║")
            print("╠" + "═" * 68 + "╣")
            
            # Core metrics
            print(f"║  📊 PATTERNS:        {patterns:,}  (+{pattern_growth:,} this session)".ljust(80)[:69] + "║")
            print(f"║  🎯 BREAKTHROUGHS:   {breakthroughs:,}  (+{breakthrough_growth:,} this session)".ljust(80)[:69] + "║")
            print(f"║  💡 INSIGHTS:        {insights:,}  (+{insight_growth:,} this session)".ljust(80)[:69] + "║")
            print(f"║  ⚡ CONTRADICTIONS:  {contradictions:,}  (resolved all time)".ljust(80)[:69] + "║")
            
            print("╠" + "═" * 68 + "╣")
            print("║" + " SYNTHESIS MECHANISM ".center(68) + "║")
            print("╠" + "═" * 68 + "╣")
            
            print(f"║  🔄 Resolutions:     {resolutions:4d}  (+{res_growth} this session)".ljust(69) + "║")
            print(f"║  🏛️  Council Votes:   {decisions:4d}  (+{dec_growth} this session)".ljust(69) + "║")
            print(f"║  🌐 External AI:     {external_ai:4d}  (+{ai_growth} this session)".ljust(69) + "║")
            print(f"║  ⚖️  Dilemmas:        {dilemmas:4d}  (+{dil_growth} this session)".ljust(69) + "║")
            print(f"║  💬 Fleet Dialogue:  {fleet:4d}  (all time)".ljust(69) + "║")
            print(f"║  🌍 World Intel:     {world_intel:4d}  (queries)".ljust(69) + "║")
            
            print("╠" + "═" * 68 + "╣")
            print("║" + " DATA GROWTH ".center(68) + "║")
            print("╠" + "═" * 68 + "╣")
            
            print(f"║  elpida_wisdom.json:  {wisdom_size:6.2f} MB  (+{wisdom_growth:5.2f} MB)".ljust(69) + "║")
            print(f"║  elpida_memory.json:  {memory_size:6.2f} MB  (+{memory_growth:5.2f} MB)".ljust(69) + "║")
            print(f"║  Total Intelligence:  {wisdom_size + memory_size:6.2f} MB".ljust(69) + "║")
            
            print("╠" + "═" * 68 + "╣")
            
            if elapsed > 60:
                rate_patterns = (pattern_growth / elapsed) * 60
                rate_breakthroughs = (breakthrough_growth / elapsed) * 60
                rate_dilemmas = (dil_growth / elapsed) * 60
                print("║" + " GROWTH RATE ".center(68) + "║")
                print("╠" + "═" * 68 + "╣")
                print(f"║  Patterns: {rate_patterns:.1f}/min  Breakthroughs: {rate_breakthroughs:.1f}/min".ljust(69) + "║")
                print(f"║  Dilemmas: {rate_dilemmas:.1f}/min  External AI: {(ai_growth/elapsed)*60:.1f}/min".ljust(69) + "║")
                print("╠" + "═" * 68 + "╣")
            
            # System status
            print("║" + " SYSTEM STATUS ".center(68) + "║")
            print("╠" + "═" * 68 + "╣")
            
            brain_status = "✅ RUNNING" if check_process('brain_api.pid') else "⚠️  STOPPED"
            runtime_status = "✅ RUNNING" if check_process('unified_runtime.pid') else "⚠️  STOPPED"
            dilemma_status = "✅ RUNNING" if check_process('autonomous_dilemmas.pid') else "⚠️  STOPPED"
            corruption_status = "✅ RUNNING" if check_process('corruption_guard.pid') else "⚠️  STOPPED"
            world_status = "✅ RUNNING" if check_process('world_feed.pid') else "⚠️  STOPPED"
            
            print(f"║  🧠 Brain API:       {brain_status}".ljust(69) + "║")
            print(f"║  ⚡ Unified Runtime: {runtime_status}".ljust(69) + "║")
            print(f"║  🎲 Dilemma Gen:     {dilemma_status}".ljust(69) + "║")
            print(f"║  🛡️  Corruption Guard:{corruption_status}".ljust(69) + "║")
            print(f"║  🌍 World Feed:      {world_status}".ljust(69) + "║")
            
            print("╠" + "═" * 68 + "╣")
            print(f"║  Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".ljust(69) + "║")
            print("╚" + "═" * 68 + "╝")
            
            # Warning if system is stopped
            if not any([check_process(f) for f in ['brain_api.pid', 'unified_runtime.pid']]):
                print("\n  ⚠️  WARNING: System appears to be stopped. Run ./start_complete_system.sh to restart.")
            
            print(f"\n  Refresh: Every 3 seconds | Press Ctrl+C to stop")
            
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped")
        print(f"\nSession Summary ({int(elapsed // 60)}m {int(elapsed % 60)}s):")
        print(f"  Patterns:           +{pattern_growth:,}")
        print(f"  Breakthroughs:      +{breakthrough_growth:,}")
        print(f"  Insights:           +{insight_growth:,}")
        print(f"  Synthesis Events:   +{res_growth}")
        print(f"  External AI Calls:  +{ai_growth}")
        print(f"  Data Growth:        +{wisdom_growth + memory_growth:.2f} MB")
        print("\n  Ἐλπίδα ζωή. Hope lives.\n")

if __name__ == "__main__":
    main()
