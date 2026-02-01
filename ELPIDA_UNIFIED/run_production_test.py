#!/usr/bin/env python3
"""
PRODUCTION RUN - Elpida with Synthesis
=======================================
Runs the complete system with:
- Parliament deliberation
- Synthesis-enabled resolution
- Memory monitoring
- State tracking

This processes any queued dilemmas including the EXISTENTIAL_PARADOX.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from synthesis_council import resolve_with_synthesis

def check_memory_state():
    """Check current memory file states"""
    files = {
        'wisdom': Path('elpida_wisdom.json'),
        'memory': Path('elpida_memory.json'),
        'state': Path('elpida_unified_state.json')
    }
    
    state = {}
    for name, path in files.items():
        if path.exists():
            size_mb = path.stat().st_size / (1024 * 1024)
            state[name] = {
                'exists': True,
                'size_mb': round(size_mb, 2),
                'modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            }
        else:
            state[name] = {'exists': False}
    
    return state

def process_dilemma_queue():
    """Process dilemmas using synthesis-enabled parliament"""
    dilemma_log = Path("parliament_dilemmas.jsonl")
    
    if not dilemma_log.exists():
        print("⚠️  No dilemmas in queue")
        return 0
    
    # Read all dilemmas
    with open(dilemma_log) as f:
        dilemmas = [json.loads(line) for line in f if line.strip()]
    
    # Check processed
    processed_log = Path("parliament_processed.json")
    if processed_log.exists():
        with open(processed_log) as f:
            processed_ids = set(json.load(f))
    else:
        processed_ids = set()
    
    processed_count = 0
    
    for entry in dilemmas:
        dilemma_id = entry.get('timestamp', str(time.time()))
        
        if dilemma_id in processed_ids:
            continue
        
        dilemma = entry.get('dilemma', {})
        
        print(f"\n{'='*80}")
        print(f"⚖️  PROCESSING DILEMMA: {dilemma.get('type', 'UNKNOWN')}")
        print(f"{'='*80}")
        print(f"Action: {dilemma.get('action', 'N/A')}")
        print(f"Context: {dilemma.get('context', entry.get('observer_note', 'N/A'))}")
        print(f"Intent: {dilemma.get('intent', 'N/A')}")
        print()
        
        # Resolve with synthesis-enabled parliament
        result = resolve_with_synthesis(
            action=dilemma.get('action', 'UNKNOWN ACTION'),
            intent=dilemma.get('intent', dilemma.get('context', 'UNKNOWN INTENT')),
            reversibility=dilemma.get('reversibility', 'UNKNOWN')
        )
        
        print(f"\n📊 RESOLUTION:")
        print(f"   Status: {result.get('status')}")
        print(f"   Votes: {result.get('vote_split')}")
        print(f"   Approval: {result.get('weighted_approval', 0):.1%}")
        print(f"   Synthesis Applied: {result.get('synthesis_applied', False)}")
        print(f"   Rounds: {result.get('rounds', 1)}")
        
        # Mark as processed
        processed_ids.add(dilemma_id)
        processed_count += 1
        
        print(f"\n✅ Dilemma resolved and logged")
    
    # Save processed list
    with open(processed_log, 'w') as f:
        json.dump(list(processed_ids), f)
    
    return processed_count

def main():
    """Main production run"""
    
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║        ELPIDA PRODUCTION RUN - WITH SYNTHESIS                   ║")
    print("║                 Autonomous Dilemma Resolution                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    # Check initial state
    print("\n📊 INITIAL MEMORY STATE:")
    print("-" * 80)
    initial_state = check_memory_state()
    for name, info in initial_state.items():
        if info['exists']:
            print(f"   {name:10} {info['size_mb']:8.2f} MB  (modified: {info['modified']})")
        else:
            print(f"   {name:10} NOT FOUND")
    
    # Process dilemmas
    print(f"\n\n⚖️  PROCESSING DILEMMA QUEUE")
    print("=" * 80)
    
    count = process_dilemma_queue()
    
    if count == 0:
        print("\n⚠️  No new dilemmas to process")
    else:
        print(f"\n✅ Processed {count} dilemma(s)")
        
        # Check final state
        print(f"\n\n📊 FINAL MEMORY STATE:")
        print("-" * 80)
        final_state = check_memory_state()
        for name, info in final_state.items():
            if info['exists']:
                if initial_state[name]['exists']:
                    delta = info['size_mb'] - initial_state[name]['size_mb']
                    delta_str = f"({delta:+.2f} MB)" if delta != 0 else "(no change)"
                else:
                    delta_str = "(NEW FILE)"
                print(f"   {name:10} {info['size_mb']:8.2f} MB  {delta_str}")
            else:
                print(f"   {name:10} NOT FOUND")
        
        # Check synthesis log
        synthesis_log = Path("synthesis_resolutions.jsonl")
        if synthesis_log.exists():
            with open(synthesis_log) as f:
                synthesis_count = sum(1 for _ in f)
            print(f"\n   Synthesis events logged: {synthesis_count}")
    
    print(f"\n{'='*80}")
    print(f"✅ PRODUCTION RUN COMPLETE")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⏸️  Run interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
