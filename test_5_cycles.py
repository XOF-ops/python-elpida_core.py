#!/usr/bin/env python3
"""Test 5 cycles to verify error logging"""
from native_cycle_engine import NativeCycleEngine

if __name__ == "__main__":
    print("🧪 Running 5-cycle test with error logging...")
    engine = NativeCycleEngine()
    engine.run(num_cycles=5)
    print("\n✅ Test complete - check above for error messages")
