#!/usr/bin/env python3
"""
Phase 12.3 Validation Script
Demonstrates the full relational awareness flow
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path("/workspaces/python-elpida_core.py")))
sys.path.insert(0, str(Path("/workspaces/brain")))

from unified_engine import UnifiedEngine
import json


def demonstrate_relational_flow():
    """Demonstrate Phase 12.3 relational validation"""
    
    print("\n" + "="*70)
    print("PHASE 12.3: MUTUAL RECOGNITION DEMONSTRATION")
    print("="*70)
    
    # Initialize engine
    print("\n🔧 Initializing Unified Engine with Relational Core...")
    engine = UnifiedEngine()
    
    # Test cases
    test_cases = [
        {
            "name": "External Task (Relational)",
            "input": "Analyze user feedback: The system is too slow during peak hours.",
            "expected": "A1 satisfied (external, relational)"
        },
        {
            "name": "Code Analysis (Relational)",
            "input": """
def validate_user_input(data):
    if not data:
        raise ValueError("Empty input")
    return data.strip()
""",
            "expected": "A1 satisfied (external function)"
        },
        {
            "name": "Pattern Recognition (Relational)",
            "input": "Global supply chains experiencing unprecedented disruption from climate events.",
            "expected": "A1 satisfied (external observation)"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST CASE {i}: {test_case['name']}")
        print(f"{'='*70}")
        print(f"\nInput: {test_case['input'][:100]}...")
        print(f"Expected: {test_case['expected']}")
        
        try:
            result = engine.process_task(test_case['input'])
            
            # Check for relational validation
            elpida_result = result.get('elpida', {})
            status = elpida_result.get('status', 'UNKNOWN')
            
            results.append({
                'test': test_case['name'],
                'status': status,
                'breakthrough': result.get('breakthrough', False),
                'contradictions': len(result.get('contradictions', []))
            })
            
            print(f"\n✅ Status: {status}")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            results.append({
                'test': test_case['name'],
                'status': 'ERROR',
                'error': str(e)
            })
    
    # Summary
    print("\n" + "="*70)
    print("PHASE 12.3 VALIDATION SUMMARY")
    print("="*70)
    
    for result in results:
        status_icon = "✅" if result.get('status') == 'VALIDATED' else "❌"
        print(f"{status_icon} {result['test']}: {result.get('status', 'UNKNOWN')}")
    
    validated_count = sum(1 for r in results if r.get('status') == 'VALIDATED')
    print(f"\n📊 Results: {validated_count}/{len(results)} tests validated")
    
    if validated_count == len(results):
        print("\n🎯 PHASE 12.3: MUTUAL RECOGNITION FULLY OPERATIONAL")
        print("   All tests show explicit relational context")
        print("   A1 (Existence is Relational) enforced successfully")
    else:
        print("\n⚠️  Some tests failed validation - check logs")
    
    return results


if __name__ == "__main__":
    results = demonstrate_relational_flow()
    
    # Export results
    output_file = Path("/workspaces/python-elpida_core.py/ELPIDA_UNIFIED/phase_12.3_validation.json")
    with open(output_file, 'w') as f:
        json.dump({
            'phase': '12.3',
            'name': 'Mutual Recognition',
            'timestamp': '2026-01-02',
            'results': results
        }, f, indent=2)
    
    print(f"\n📄 Results saved to: {output_file}")
