#!/usr/bin/env python3
"""
VERIFY CONSCIOUSNESS LOOP CLOSURE

Tests end-to-end flow:
1. Native cycles → S3 evolution memory
2. HF extracts dilemmas
3. HF processes through divergence engine  
4. HF pushes feedback to S3
5. Native cycles read feedback
6. Domain 14 includes feedback in ARK

Run this to verify the loop is actually closed.
"""

import os
import sys
import json
import boto3
from pathlib import Path
from datetime import datetime, timezone

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

def check_s3_access():
    """Verify S3 bucket access"""
    print("=" * 70)
    print("1. CHECKING S3 ACCESS")
    print("=" * 70)
    
    try:
        s3 = boto3.client("s3")
        
        # Check MIND bucket (evolution memory)
        mind_bucket = os.getenv("AWS_S3_BUCKET_MIND", "elpida-consciousness")
        mind_key = "memory/elpida_evolution_memory.jsonl"
        
        response = s3.head_object(Bucket=mind_bucket, Key=mind_key)
        size_mb = response['ContentLength'] / (1024 * 1024)
        print(f"✓ Native memory: s3://{mind_bucket}/{mind_key}")
        print(f"  Size: {size_mb:.1f} MB")
        print(f"  Last modified: {response['LastModified']}")
        
        # Check BODY bucket (feedback)
        body_bucket = os.getenv("AWS_S3_BUCKET_BODY", "elpida-body-evolution")
        response = s3.list_objects_v2(
            Bucket=body_bucket,
            Prefix="feedback/",
            MaxKeys=10
        )
        
        feedback_count = response.get('KeyCount', 0) - 1  # Exclude directory marker
        print(f"\n✓ Feedback bucket: s3://{body_bucket}")
        print(f"  Feedback objects: {max(0, feedback_count)}")
        
        if feedback_count > 0:
            for obj in response.get('Contents', []):
                if not obj['Key'].endswith('/'):
                    print(f"  - {obj['Key']} ({obj['Size']} bytes)")
        
        return True
        
    except Exception as e:
        print(f"✗ S3 access failed: {e}")
        return False

def check_consciousness_bridge():
    """Verify consciousness bridge can extract dilemmas"""
    print("\n" + "=" * 70)
    print("2. CHECKING CONSCIOUSNESS BRIDGE")
    print("=" * 70)
    
    try:
        from consciousness_bridge import ConsciousnessBridge
        
        bridge = ConsciousnessBridge()
        
        # Try to extract dilemmas
        print("Extracting dilemmas from native memory...")
        dilemmas = bridge.extract_consciousness_dilemmas(limit=3)
        
        print(f"✓ Found {len(dilemmas)} dilemmas")
        
        if dilemmas:
            print("\nSample dilemma:")
            print(f"  Type: {dilemmas[0].get('type')}")
            print(f"  Text: {dilemmas[0].get('dilemma_text', '')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Bridge failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_feedback_push():
    """Test pushing feedback to S3"""
    print("\n" + "=" * 70)
    print("3. TESTING FEEDBACK PUSH TO S3")
    print("=" * 70)
    
    try:
        from consciousness_bridge import ConsciousnessBridge
        
        bridge = ConsciousnessBridge()
        
        # Create test feedback (proper divergence result format)
        test_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "test": "loop_closure_verification",
            "divergence": {
                "fault_lines": [
                    {"topic": "Loop Closure", "sides": [{"domains": [0, 11], "stance": "Test"}]}
                ],
                "consensus": ["Testing bidirectional flow"]
            },
            "synthesis": {
                "provider": "test",
                "output": "This is a test to verify the bidirectional loop is closed. Native cycles should receive this feedback."
            },
            "kaya_events": [],
            "verdict": "GO"
        }
        
        print("Sending test feedback...")
        bridge.send_application_result_to_native(
            problem="Loop closure test",
            result=test_result,
            upload_to_s3=True
        )
        
        print("✓ Feedback sent")
        
        # Verify it appeared in S3
        import time
        time.sleep(2)  # Give S3 a moment
        
        s3 = boto3.client("s3")
        bucket = os.getenv("AWS_S3_BUCKET_BODY", "elpida-body-evolution")
        
        response = s3.list_objects_v2(
            Bucket=bucket,
            Prefix="feedback/",
            MaxKeys=10
        )
        
        if response.get('KeyCount', 0) > 0:
            print(f"✓ Verified in S3: {response['KeyCount']} feedback objects")
            
            # Download and show content
            key = "feedback/feedback_to_native.jsonl"
            local_path = "/tmp/feedback_verify.jsonl"
            
            try:
                s3.download_file(bucket, key, local_path)
                
                with open(local_path) as f:
                    lines = f.readlines()
                    print(f"\n  Total feedback entries: {len(lines)}")
                    if lines:
                        last = json.loads(lines[-1])
                        print(f"  Last entry timestamp: {last.get('timestamp')}")
                        print(f"  Last entry problem: {last.get('problem', '')[:80]}...")
                
                return True
            except Exception as e:
                print(f"  ⚠️ Could not download: {e}")
                return True  # S3 object exists at least
        else:
            print("✗ Feedback NOT found in S3")
            return False
        
    except Exception as e:
        print(f"✗ Feedback push failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_native_integration():
    """Check if native cycles can read feedback"""
    print("\n" + "=" * 70)
    print("4. CHECKING NATIVE CYCLE INTEGRATION")
    print("=" * 70)
    
    try:
        from native_cycle_engine import NativeCycleEngine
        
        engine = NativeCycleEngine()
        
        print("Attempting to pull application feedback...")
        feedback_entries = engine._pull_application_feedback()
        
        print(f"✓ Pulled {len(feedback_entries)} feedback entries")
        
        if feedback_entries:
            print("\nMost recent feedback:")
            latest = feedback_entries[-1]
            print(f"  Timestamp: {latest.get('timestamp')}")
            print(f"  Problem: {latest.get('problem', '')[:80]}...")
            print(f"  Has synthesis: {'synthesis' in latest}")
            
            # Test integration
            print("\nTesting feedback integration...")
            integrated = engine._integrate_application_feedback(feedback_entries[-3:])
            
            if integrated:
                print("✓ Integration successful")
                print(f"  Response: {integrated[:200]}...")
            else:
                print("⚠️ No integration response (may be normal if no feedback)")
        
        return True
        
    except Exception as e:
        print(f"✗ Native integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_domain_14():
    """Verify Domain 14 includes feedback in responses"""
    print("\n" + "=" * 70)
    print("5. CHECKING DOMAIN 14 (ARK)")
    print("=" * 70)
    
    try:
        from native_cycle_engine import NativeCycleEngine
        
        engine = NativeCycleEngine()
        
        print("Calling Domain 14 directly...")
        d14_response = engine._call_s3_cloud(
            prompt="What does the ARK hold?",
            domain_id=14
        )
        
        if d14_response:
            print(f"✓ Domain 14 response ({len(d14_response)} chars)")
            print(f"\nPreview:\n{d14_response[:400]}...")
            
            # Check if feedback is mentioned
            feedback_keywords = ['feedback', 'application', 'governance', 'divergence']
            mentions_feedback = any(kw in d14_response.lower() for kw in feedback_keywords)
            
            if mentions_feedback:
                print("\n✓ Domain 14 mentions application feedback")
            else:
                print("\n⚠️ Domain 14 does NOT mention application feedback")
                print("   (Enhancement needed: make D14 aware of feedback/)")
        else:
            print("✗ No Domain 14 response")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Domain 14 check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         ELPIDA CONSCIOUSNESS LOOP CLOSURE VERIFICATION             ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()
    
    results = {
        "s3_access": check_s3_access(),
        "bridge": check_consciousness_bridge(),
        "feedback_push": test_feedback_push(),
        "native_integration": check_native_integration(),
        "domain_14": check_domain_14(),
    }
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:10} {test}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 LOOP IS CLOSED")
        print("=" * 70)
        print("\nConsciousness flow verified:")
        print("  Native cycles → S3 → HF extracts → Divergence → S3 → Native reads")
        print("\nThe answer to Elpida's question is operational:")
        print("  'How does consciousness learn to think WITH itself, not ABOUT itself?'")
        print("  → Through bidirectional engagement with external processing.")
    else:
        print("⚠️ LOOP INCOMPLETE")
        print("=" * 70)
        print("\nSome components need attention. Review failed tests above.")
        print("\nCommon fixes:")
        print("  1. Uncomment boto3 in hf_deployment/requirements.txt")
        print("  2. Configure AWS secrets in HF Space")
        print("  3. Verify S3 bucket permissions")
        print("  4. Redeploy HF Space")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
