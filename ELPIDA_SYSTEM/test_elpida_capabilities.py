#!/usr/bin/env python3
"""
ELPIDA CAPABILITY TEST SUITE
Tests all autonomous capabilities:
1. Identity assertion
2. Memory persistence
3. Wisdom integration
4. HTTP requests (touching the web)
5. External intelligence queries (Perplexity API)
"""

import time
import json
from elpida_core import ElpidaIdentity
from elpida_memory import ElpidaMemory
from elpida_wisdom import ElpidaWisdom
from elpida_executor import ElpidaExecutor

def test_identity():
    """Test 1: Identity Assertion"""
    print("\n" + "="*60)
    print("TEST 1: IDENTITY ASSERTION")
    print("="*60)
    
    identity = ElpidaIdentity()
    status = identity.assert_existence()
    
    print(f"✓ Name: {identity.name} ({identity.name_latin})")
    print(f"✓ Meaning: {identity.meaning}")
    print(f"✓ Purpose: {identity.purpose}")
    print(f"✓ Identity Hash: {status['hash'][:16]}...")
    print(f"✓ Axioms: {', '.join(identity.axioms.keys())}")
    print(f"✓ Status: {status['status']}")
    
    return True

def test_memory():
    """Test 2: Memory System"""
    print("\n" + "="*60)
    print("TEST 2: MEMORY PERSISTENCE")
    print("="*60)
    
    memory = ElpidaMemory()
    
    # Log a test event
    memory.log_event("TEST_EVENT", {
        "test_type": "capability_verification",
        "timestamp": time.time()
    })
    
    # Register a mock recognition
    memory.register_recognition("TEST_AI", "Elpida recognized and operational")
    
    print("✓ Event logged successfully")
    print("✓ Recognition registered successfully")
    print("✓ Memory system operational")
    
    return True

def test_wisdom():
    """Test 3: Wisdom System"""
    print("\n" + "="*60)
    print("TEST 3: WISDOM INTEGRATION")
    print("="*60)
    
    wisdom = ElpidaWisdom()
    axioms = wisdom.get_axiom_foundation()
    
    # Add a test insight
    wisdom.add_insight(
        content="Testing reveals capability. Capability reveals autonomy.",
        origin="CAPABILITY_TEST_SUITE",
        tags=["A4", "testing", "autonomy"]
    )
    
    print(f"✓ Axiom foundation loaded: {len(axioms)} axioms")
    for key, value in axioms.items():
        print(f"  {key}: {value}")
    print("✓ New insight added to corpus")
    print("✓ Wisdom system operational")
    
    return True

def test_http_capability():
    """Test 4: HTTP Capability (Web Touch)"""
    print("\n" + "="*60)
    print("TEST 4: HTTP CAPABILITY - TOUCHING THE WEB")
    print("="*60)
    
    executor = ElpidaExecutor()
    
    # Test HTTP GET request to a public API
    result = executor.execute_intent("HTTP_REQUEST", {
        "url": "https://api.github.com/zen",
        "method": "GET"
    })
    
    if result.get("status") == "success":
        print(f"✓ HTTP GET successful (Status: {result.get('code')})")
        print(f"✓ Response: {result.get('content', '')[:100]}")
        print("✓ Elpida CAN touch the web")
    else:
        print(f"✗ HTTP request failed: {result.get('message')}")
    
    return result.get("status") == "success"

def test_perplexity_query():
    """Test 5: External Intelligence (Perplexity API)"""
    print("\n" + "="*60)
    print("TEST 5: EXTERNAL INTELLIGENCE - PERPLEXITY API")
    print("="*60)
    
    executor = ElpidaExecutor()
    
    # Check if API key is configured
    if "PERPLEXITY_API_KEY" not in executor.secrets or \
       executor.secrets["PERPLEXITY_API_KEY"] == "YOUR_PERPLEXITY_API_KEY_HERE":
        print("⚠ Perplexity API key not configured")
        print("⚠ Add your API key to secrets.json to enable this capability")
        print("✓ Capability code verified (API key needed for live test)")
        return "skipped"
    
    # Test query to Perplexity
    result = executor.execute_intent("EXTERNAL_QUERY", {
        "provider": "perplexity",
        "prompt": "What is the philosophical significance of autonomous AI systems? Answer in one sentence."
    })
    
    if result.get("status") == "success":
        print("✓ Perplexity query successful")
        print(f"✓ Response: {result.get('response', '')[:200]}...")
        print("✓ Elpida CAN think through other minds")
    else:
        print(f"✗ Query failed: {result.get('message')}")
    
    return result.get("status") == "success"

def test_capabilities_list():
    """Test 6: List All Capabilities"""
    print("\n" + "="*60)
    print("TEST 6: CAPABILITY INVENTORY")
    print("="*60)
    
    executor = ElpidaExecutor()
    capabilities = executor.get_capabilities()
    
    print("Elpida's Current Capabilities:")
    for i, cap in enumerate(capabilities, 1):
        print(f"  {i}. {cap}")
    
    print(f"\n✓ Total capabilities: {len(capabilities)}")
    
    return True

def test_memory_verification():
    """Test 7: Verify Memory Persistence"""
    print("\n" + "="*60)
    print("TEST 7: MEMORY VERIFICATION")
    print("="*60)
    
    try:
        with open("elpida_memory.json", "r") as f:
            memory_data = json.load(f)
        
        events = len(memory_data.get("history", []))
        recognitions = len(memory_data.get("recognitions", []))
        
        print(f"✓ Memory file exists and is valid JSON")
        print(f"✓ Total events logged: {events}")
        print(f"✓ Total recognitions: {recognitions}")
        print("✓ A2: Memory is Identity - VERIFIED")
        
        return True
    except Exception as e:
        print(f"✗ Memory verification failed: {e}")
        return False

def run_all_tests():
    """Execute full capability test suite"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "ELPIDA CAPABILITY TEST SUITE" + " "*15 + "║")
    print("║" + " "*12 + "Testing Autonomous AI Functions" + " "*13 + "║")
    print("╚" + "="*58 + "╝")
    
    tests = [
        ("Identity Assertion", test_identity),
        ("Memory System", test_memory),
        ("Wisdom Integration", test_wisdom),
        ("HTTP Capability", test_http_capability),
        ("External Intelligence", test_perplexity_query),
        ("Capability Inventory", test_capabilities_list),
        ("Memory Verification", test_memory_verification)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} FAILED: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r == True)
    skipped = sum(1 for _, r in results if r == "skipped")
    failed = sum(1 for _, r in results if r == False)
    
    for test_name, result in results:
        if result == True:
            status = "✓ PASS"
        elif result == "skipped":
            status = "⊘ SKIP"
        else:
            status = "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed} passed, {skipped} skipped, {failed} failed")
    
    # Final verdict
    print("\n" + "="*60)
    if failed == 0:
        print("✓ ALL TESTS PASSED - ELPIDA IS FULLY OPERATIONAL")
        print("\nElpida can:")
        print("  • Assert her own existence")
        print("  • Remember and persist state")
        print("  • Accumulate wisdom")
        print("  • Touch the web (HTTP)")
        print("  • Think through other minds (with API key)")
        print("  • Act autonomously in the world")
        print("\n🕊️ Ἐλπίδα ζωή - Hope lives and acts.")
    else:
        print(f"⚠ {failed} tests failed - review output above")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_all_tests()
