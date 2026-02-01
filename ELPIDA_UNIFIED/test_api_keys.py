#!/usr/bin/env python3
"""
Test All API Keys and Configure System
Verifies each AI service API key is working
"""

import os
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_bridge import setup_standard_connections


async def test_all_apis():
    """Test each API key to ensure it works"""
    
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║          API KEY VALIDATION - Testing All Connections            ║")
    print("╚═══════════════════════════════════════════════════════════════════╝\n")
    
    # Load from .env file
    env_file = Path(".env")
    if env_file.exists():
        print("📄 Loading API keys from .env file...\n")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded\n")
    
    # Setup connections
    bridge = setup_standard_connections()
    
    print("─" * 70)
    print("TESTING EACH API CONNECTION")
    print("─" * 70)
    print()
    
    test_message = "Hello! Please respond with a brief greeting confirming you can receive this message."
    
    results = {}
    
    # Test each connection
    for ai_name, conn in bridge.connections.items():
        print(f"Testing {ai_name}...")
        
        if not conn.connected:
            print(f"   ⚠️  Skipped - No API key set ({conn.api_key_env_var})")
            results[ai_name] = {"status": "skipped", "reason": "no_api_key"}
            print()
            continue
        
        try:
            response = await bridge.send_message(ai_name, test_message)
            
            if response.get("success"):
                print(f"   ✅ SUCCESS")
                print(f"   Response: {response['response'][:100]}...")
                results[ai_name] = {
                    "status": "working",
                    "model": response.get("model", "unknown"),
                    "provider": conn.provider
                }
            else:
                print(f"   ❌ FAILED")
                print(f"   Error: {response.get('error')}")
                results[ai_name] = {
                    "status": "failed",
                    "error": response.get("error"),
                    "provider": conn.provider
                }
        except Exception as e:
            print(f"   ❌ EXCEPTION")
            print(f"   {str(e)}")
            results[ai_name] = {
                "status": "exception",
                "error": str(e),
                "provider": conn.provider
            }
        
        print()
        await asyncio.sleep(1)  # Rate limiting
    
    # Summary
    print("═" * 70)
    print("VALIDATION SUMMARY")
    print("═" * 70)
    print()
    
    working = [name for name, r in results.items() if r["status"] == "working"]
    failed = [name for name, r in results.items() if r["status"] in ["failed", "exception"]]
    skipped = [name for name, r in results.items() if r["status"] == "skipped"]
    
    print(f"✅ Working:  {len(working)}/8 APIs")
    for name in working:
        provider = results[name]["provider"]
        model = results[name].get("model", "")
        print(f"   • {name} ({provider}) - {model}")
    print()
    
    if failed:
        print(f"❌ Failed:   {len(failed)} APIs")
        for name in failed:
            error = results[name].get("error", "Unknown")
            print(f"   • {name}: {error}")
        print()
    
    if skipped:
        print(f"ℹ️  Skipped:  {len(skipped)} APIs (no keys)")
        for name in skipped:
            print(f"   • {name}")
        print()
    
    # Distribution recommendations
    print("═" * 70)
    print("RECOMMENDED DISTRIBUTION FOR ELPIDA OPERATIONS")
    print("═" * 70)
    print()
    
    if working:
        print("✅ Multi-AI Connector:")
        print("   Will use all working APIs for cross-AI dialogue")
        for name in working:
            print(f"   → {name}")
        print()
        
        if "Perplexity" in working:
            print("✅ World Intelligence Feed:")
            print("   → Perplexity (real-time news & research)")
            print()
        
        if "Gemini Pro" in working or "GPT-4" in working or "Claude" in working:
            print("✅ External Validation:")
            print("   Best for deep reasoning about Elpida's dilemmas:")
            if "GPT-4" in working:
                print("   → GPT-4 (general knowledge)")
            if "Gemini Pro" in working:
                print("   → Gemini Pro (multimodal, fast)")
            if "Claude" in working:
                print("   → Claude (ethical reasoning)")
            print()
        
        if "Groq Llama" in working or "Cohere Command" in working:
            print("✅ High-Speed Processing:")
            if "Groq Llama" in working:
                print("   → Groq (ultra-fast inference)")
            if "Cohere Command" in working:
                print("   → Cohere (RAG-optimized)")
            print()
    else:
        print("⚠️  No working APIs detected")
        print("   System can still run autonomously without external AI")
        print("   But external validation and cross-AI synthesis disabled")
        print()
    
    print("═" * 70)
    print()
    
    if working:
        print(f"✨ {len(working)} AI systems ready for integration")
        print("   Restart complete system to activate:")
        print("   ./stop_complete_system.sh && ./start_complete_system.sh")
    else:
        print("💡 Set API keys in .env file to enable external AI")
    
    print()
    print("Ἐλπίδα ζωή. Hope lives.")
    print()
    
    return results


if __name__ == "__main__":
    results = asyncio.run(test_all_apis())
