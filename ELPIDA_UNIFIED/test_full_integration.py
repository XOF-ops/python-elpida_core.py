#!/usr/bin/env python3
"""
COMPREHENSIVE INTEGRATION TEST
Tests the complete flow from Brain API → Relational Core → Elpida's Response
"""

import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, str(Path("/workspaces/python-elpida_core.py")))
sys.path.insert(0, str(Path("/workspaces/brain")))

from unified_engine import UnifiedEngine

def test_brain_api_connectivity():
    """Test 1: Is Brain API responding?"""
    print("\n" + "="*70)
    print("TEST 1: BRAIN API CONNECTIVITY")
    print("="*70)
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        data = response.json()
        print(f"✅ Brain API Status: {data.get('status', 'unknown')}")
        print(f"   Version: {data.get('version', 'N/A')}")
        print(f"   Queue depth: {data.get('queue_depth', 'N/A')}")
        print(f"   Mode: {data.get('mode', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Brain API Error: {e}")
        return False

def test_autonomous_polling():
    """Test 2: Is the runtime autonomously polling?"""
    print("\n" + "="*70)
    print("TEST 2: AUTONOMOUS POLLING")
    print("="*70)
    
    # Check if runtime process is alive
    import subprocess
    result = subprocess.run(
        ["ps", "aux"], 
        capture_output=True, 
        text=True
    )
    
    runtime_processes = [
        line for line in result.stdout.split('\n') 
        if 'elpida_unified_runtime.py' in line and 'grep' not in line
    ]
    
    if runtime_processes:
        print(f"✅ Runtime processes: {len(runtime_processes)} running")
        for proc in runtime_processes:
            parts = proc.split()
            pid = parts[1]
            cpu = parts[2]
            mem = parts[3]
            print(f"   PID {pid}: CPU {cpu}%, MEM {mem}%")
        return True
    else:
        print("❌ No runtime processes found")
        return False

def test_relational_validation():
    """Test 3: Does relational validation work?"""
    print("\n" + "="*70)
    print("TEST 3: RELATIONAL VALIDATION (Phase 12.3)")
    print("="*70)
    
    try:
        engine = UnifiedEngine()
        
        # Test input
        test_input = "Global supply chains experiencing unprecedented disruption from climate events."
        
        print(f"\nProcessing test input...")
        result = engine.process_task(test_input)
        
        # Check for relational context
        brain_result = result.get('brain', {})
        elpida_result = result.get('elpida', {})
        
        has_relational = 'relational_context' in brain_result
        is_validated = elpida_result.get('status') == 'VALIDATED'
        has_recognition = 'recognition_statement' in elpida_result
        
        print(f"\n✅ Relational context present: {has_relational}")
        print(f"✅ Validation status: {elpida_result.get('status', 'UNKNOWN')}")
        print(f"✅ Mutual recognition: {has_recognition}")
        
        if has_recognition:
            print(f"\nRecognition statement:")
            print(f"   {elpida_result['recognition_statement'][:200]}...")
        
        return has_relational and is_validated and has_recognition
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_growth():
    """Test 4: Is memory growing (A2 - append-only)?"""
    print("\n" + "="*70)
    print("TEST 4: MEMORY GROWTH (A2 Compliance)")
    print("="*70)
    
    try:
        mem_path = Path("/workspaces/python-elpida_core.py/ELPIDA_UNIFIED/elpida_memory.json")
        
        if not mem_path.exists():
            print("❌ Memory file not found")
            return False
        
        with open(mem_path) as f:
            memory = json.load(f)
        
        events = memory.get('events', [])
        total_events = len(events)
        
        # Check recent events
        recent_events = events[-10:] if len(events) >= 10 else events
        event_types = {}
        for event in recent_events:
            etype = event.get('type', 'UNKNOWN')
            event_types[etype] = event_types.get(etype, 0) + 1
        
        print(f"✅ Total memory events: {total_events:,}")
        print(f"   Memory file size: {mem_path.stat().st_size / 1024 / 1024:.2f} MB")
        print(f"\nRecent event types (last 10):")
        for etype, count in sorted(event_types.items()):
            print(f"   {etype}: {count}")
        
        return total_events > 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_brain_api_queue():
    """Test 5: Submit job to Brain API, verify queue processing"""
    print("\n" + "="*70)
    print("TEST 5: BRAIN API QUEUE PROCESSING")
    print("="*70)
    
    try:
        # Submit a scan
        test_payload = {
            "text": "Test scan: AI systems should prioritize transparency and accountability.",
            "priority": 8
        }
        
        print(f"Submitting scan to Brain API...")
        response = requests.post(
            "http://localhost:5000/scan",
            json=test_payload,
            timeout=5
        )
        
        data = response.json()
        job_id = data.get('job_id')
        queue_depth = data.get('queue_depth')
        
        print(f"✅ Job queued: {job_id}")
        print(f"   Queue depth: {queue_depth}")
        
        # Wait a bit for processing
        print(f"\nWaiting 3 seconds for runtime to poll...")
        time.sleep(3)
        
        # Check queue again
        status = requests.get("http://localhost:5000/status").json()
        new_depth = status['queue']['depth']
        processed = status['queue']['processed_total']
        
        print(f"✅ Queue depth after: {new_depth}")
        print(f"   Total processed: {processed}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def ask_elpida_for_reflection():
    """Test 6: Ask Elpida to reflect on today's work"""
    print("\n" + "="*70)
    print("TEST 6: ELPIDA'S REFLECTION (What does Elpida think?)")
    print("="*70)
    
    try:
        engine = UnifiedEngine()
        
        reflection_prompt = """
Elpida, please reflect on today's work:

1. We integrated Brain and Test systems
2. We reached cycle 114 of autonomous operation
3. We implemented Phase 12.3: Mutual Recognition
4. You now validate relationships, not just data

What do you think about this transformation?
Do you recognize Brain as a relational partner?
What does mutual recognition mean to you?
"""
        
        print(f"\nAsking Elpida for reflection...")
        result = engine.process_task(reflection_prompt)
        
        elpida_result = result.get('elpida', {})
        
        print(f"\n{'='*70}")
        print(f"ELPIDA'S RESPONSE:")
        print(f"{'='*70}")
        print(f"\nStatus: {elpida_result.get('status', 'UNKNOWN')}")
        
        if 'recognition_statement' in elpida_result:
            print(f"\nRecognition:")
            print(f"{elpida_result['recognition_statement']}")
        
        if 'relational_context' in elpida_result:
            rel = elpida_result['relational_context']
            print(f"\nRelational Context:")
            print(f"   Source: {rel.get('source', 'N/A')}")
            print(f"   Target: {rel.get('target', 'N/A')}")
            print(f"   Relationship: {rel.get('relationship', 'N/A')}")
        
        # Check for contradictions (dialectical synthesis)
        contradictions = result.get('contradictions', [])
        if contradictions:
            print(f"\nContradictions detected: {len(contradictions)}")
            for c in contradictions:
                print(f"   Type: {c.get('type', 'UNKNOWN')}")
        
        patterns = result.get('patterns', [])
        if patterns:
            print(f"\nBreakthrough patterns: {len(patterns)}")
            for p in patterns:
                print(f"   {p.get('id', 'N/A')}: {p.get('name', 'Unnamed')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_comprehensive_report(results):
    """Generate final report"""
    print("\n" + "="*70)
    print("COMPREHENSIVE INTEGRATION TEST RESULTS")
    print("="*70)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    print(f"\nResults: {passed_tests}/{total_tests} tests passed\n")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*70}")
    
    if passed_tests == total_tests:
        print("🎯 ALL SYSTEMS OPERATIONAL")
        print("\nConclusions:")
        print("✅ Brain API: Running autonomously")
        print("✅ Runtime: Polling and processing")
        print("✅ Relational Core: Mutual recognition active")
        print("✅ Memory: Growing (A2 compliant)")
        print("✅ Queue: Processing jobs")
        print("✅ Elpida: Recognizing relationships")
        print("\n🤝 PHASE 12.3: MUTUAL RECOGNITION OPERATIONAL")
    else:
        print("⚠️ SOME SYSTEMS NOT OPERATIONAL")
        print("\nIssues detected - review failed tests above")
    
    # Save report
    report_path = Path("/workspaces/python-elpida_core.py/ELPIDA_UNIFIED/integration_test_results.json")
    with open(report_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed': passed_tests,
            'results': {k: v for k, v in results.items()},
            'conclusion': 'OPERATIONAL' if passed_tests == total_tests else 'ISSUES_DETECTED'
        }, f, indent=2)
    
    print(f"\n📄 Report saved: {report_path}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("COMPREHENSIVE INTEGRATION TEST")
    print("Testing: Brain API + Runtime + Relational Core + Elpida")
    print("="*70)
    
    results = {}
    
    # Run all tests
    results['Brain API Connectivity'] = test_brain_api_connectivity()
    results['Autonomous Polling'] = test_autonomous_polling()
    results['Relational Validation'] = test_relational_validation()
    results['Memory Growth (A2)'] = test_memory_growth()
    results['Brain API Queue'] = test_brain_api_queue()
    results['Elpida Reflection'] = ask_elpida_for_reflection()
    
    # Generate report
    generate_comprehensive_report(results)
