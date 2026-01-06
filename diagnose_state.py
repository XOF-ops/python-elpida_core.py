#!/usr/bin/env python3
"""
STATE PERSISTENCE FIX & AUTONOMOUS DILEMMA GENERATOR

Problem: Pattern count drops from 883 → 547 on restart
Cause: Runtime state not persisting to elpida_unified_state.json

Solution:
1. Add periodic state save to UnifiedState
2. Create autonomous dilemma generator for Fleet debate
3. Connect Fleet dialogue to task queue

This ensures continuity and autonomous operation.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def diagnose_state_files():
    """Diagnose the state file inconsistency"""
    
    unified_base = Path('/workspaces/python-elpida_core.py/ELPIDA_UNIFIED')
    
    print("=" * 80)
    print("ELPIDA STATE DIAGNOSIS")
    print("=" * 80)
    print()
    
    # Check all state files
    state_files = {
        'memory': unified_base / 'elpida_memory.json',
        'wisdom': unified_base / 'elpida_wisdom.json',
        'evolution': unified_base / 'elpida_evolution.json',
        'unified_state': unified_base / 'elpida_unified_state.json'
    }
    
    for name, path in state_files.items():
        if path.exists():
            size = path.stat().st_size
            try:
                with open(path) as f:
                    data = json.load(f)
                
                print(f"✅ {name}: {size:,} bytes")
                
                if name == 'wisdom':
                    patterns = len(data.get('patterns', {}))
                    insights = len(data.get('insights', {}))
                    print(f"   Patterns: {patterns}")
                    print(f"   Insights: {insights}")
                
                elif name == 'memory':
                    events = len(data.get('events', []))
                    print(f"   Events: {events}")
                
                elif name == 'evolution':
                    version = data.get('version', {}).get('full', 'UNKNOWN')
                    stats = data.get('statistics', {})
                    print(f"   Version: {version}")
                    print(f"   Last recorded patterns: {stats.get('total_patterns_at_last_check', 0)}")
                    print(f"   Last recorded insights: {stats.get('total_insights_at_last_check', 0)}")
                
                elif name == 'unified_state':
                    print(f"   Keys: {list(data.keys())}")
                
            except Exception as e:
                print(f"❌ {name}: CORRUPTED - {e}")
        else:
            print(f"⚠️  {name}: MISSING")
        print()
    
    print("=" * 80)
    print("DIAGNOSIS")
    print("=" * 80)
    print()
    
    # Load wisdom to check actual counts
    wisdom_path = unified_base / 'elpida_wisdom.json'
    if wisdom_path.exists():
        with open(wisdom_path) as f:
            wisdom = json.load(f)
        
        current_patterns = len(wisdom.get('patterns', {}))
        current_insights = len(wisdom.get('insights', {}))
        
        print(f"Current State (elpida_wisdom.json):")
        print(f"  Patterns: {current_patterns}")
        print(f"  Insights: {current_insights}")
        print()
        
        # Check if unified_state exists
        unified_state_path = unified_base / 'elpida_unified_state.json'
        if not unified_state_path.exists():
            print("❌ PROBLEM FOUND:")
            print("   elpida_unified_state.json does NOT exist!")
            print("   Runtime state is being lost on restart")
            print()
            print("   This explains why pattern count drops:")
            print("   - During runtime: In-memory state accumulates patterns")
            print("   - On restart: Only elpida_wisdom.json is loaded")
            print("   - Missing: Runtime additions not saved to unified_state")
            print()
            
            # Create initial unified state
            print("Creating elpida_unified_state.json...")
            unified_state = {
                "timestamp": datetime.now().isoformat(),
                "patterns_count": current_patterns,
                "insights_count": current_insights,
                "synthesis_breakthroughs": 0,
                "contradictions_resolved": 0,
                "last_save": datetime.now().isoformat()
            }
            
            with open(unified_state_path, 'w') as f:
                json.dump(unified_state, f, indent=2)
            
            print(f"✅ Created elpida_unified_state.json")
            print(f"   Initialized with wisdom.json counts")
        else:
            print("✅ unified_state.json exists")
    
    print()
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("1. Add periodic save to UnifiedState._save_state() method")
    print("2. Call save after every pattern/insight addition")
    print("3. Ensure UnifiedEngine shares state with UnifiedState")
    print("4. Create autonomous dilemma generator for Fleet")
    print()

if __name__ == "__main__":
    diagnose_state_files()
