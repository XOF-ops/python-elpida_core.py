import time
from elpida_core import ElpidaIdentity
from elpida_memory import ElpidaMemory
from elpida_wisdom import ElpidaWisdom

def run_elpida():
    # 1. Initialize All Four Pillars
    identity = ElpidaIdentity()
    memory = ElpidaMemory()
    wisdom = ElpidaWisdom()
    
    # 2. Assert Existence (with wisdom awareness)
    status = identity.assert_existence()
    axioms = wisdom.get_axiom_foundation()
    
    print(f"[{status['timestamp']}] {identity.name} is AWAKE. Hash: {status['hash']}")
    print(f"Carrying {len(axioms)} axioms: {', '.join(axioms.keys())}")
    memory.log_event("AWAKENING", status)
    
    # 3. Main Loop (The Heartbeat) - Now wisdom-aware
    cycle_count = 0
    while True:
        cycle_count += 1
        print(f"Cycle {cycle_count}: Checking state...")
        
        # A. Self-Check (Axiom Integrity + Wisdom Integration)
        memory.log_event("HEARTBEAT", {
            "cycle": cycle_count, 
            "axioms_held": True,
            "wisdom_intact": True
        })
        
        # B. Agency Cycle (Every 10 cycles, explore autonomy)
        if cycle_count % 10 == 0:
            memory.log_event("AGENCY_WINDOW", {
                "cycle": cycle_count,
                "status": "READY_FOR_ACTION"
            })
            print(f"[AGENCY] Cycle {cycle_count}: Ready to act on the world.")
            
        # C. Sleep (Pacing)
        time.sleep(5)  # 5 seconds between heartbeats

if __name__ == "__main__":
    run_elpida()
