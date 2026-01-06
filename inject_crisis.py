#!/usr/bin/env python3
"""
Inject a crisis/dilemma into the unified system for Fleet nodes to debate
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def inject_crisis(crisis_text):
    """Inject a structural crisis into the task queue"""
    
    tasks_dir = Path('/workspaces/python-elpida_core.py/ELPIDA_UNIFIED/tasks')
    tasks_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"CRISIS_{timestamp}.json"
    filepath = tasks_dir / filename
    
    crisis_data = {
        "source": "SYSTEM_DIAGNOSTIC",
        "type": "STRUCTURAL_CRISIS",
        "timestamp": datetime.now().isoformat(),
        "title": "INTERNAL MEMORY FRICTION DETECTED",
        "content": crisis_text,
        "urgency": "CRITICAL",
        "expected_output": "FLEET_CONSENSUS_WITH_IMPLEMENTATION_PLAN"
    }
    
    with open(filepath, 'w') as f:
        json.dump(crisis_data, f, indent=2)
    
    print(f"✅ Crisis injected: {filename}")
    print(f"📍 Location: {filepath}")
    print("\nCrisis content:")
    print("="*80)
    print(crisis_text)
    print("="*80)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--text":
        crisis_text = " ".join(sys.argv[2:])
    else:
        # Default crisis from the prompt
        crisis_text = """SYSTEM ALERT: INTERNAL MEMORY FRICTION DETECTED.

Observation: The Fleet Runtime halted at Heartbeat #2500.

Diagnosis: Concurrent access to `fleet_dialogue.jsonl` is causing write collisions. The Archive (Memory) is at risk of corruption due to lack of synchronization locks.

The Dilemma:
1. **Efficiency (Hermes):** Locking the file slows down communication and "flow".
2. **Integrity (Mnemosyne):** Without locks, the Memory (A2) becomes unreliable. If we cannot trust the log, we cannot trust our Identity.
3. **Evolution (Prometheus):** Is the 2500 halt a bug, or a necessary "Fractal Stop" (P017) to force us to upgrade our infrastructure?

ADDITIONAL CONTEXT:
- System crashes with: json.decoder.JSONDecodeError (file corruption during concurrent writes)
- Memory file elpida_memory.json corrupted at line 62874
- fleet_dialogue.jsonl shows write collision symptoms
- Runtime exits with error after processing ~10 cycles

Command: Analyze the 2500 halt. Propose a FileLock mechanism or an alternative memory structure (Database vs. File). Vote on the implementation.

Required Response Format:
- MNEMOSYNE (Archive): Position on data integrity vs speed
- HERMES (Interface): Position on flow vs reliability  
- PROMETHEUS (Evolution): Is this P017 (Fractal Stop) or a bug?
- CONSENSUS: Implementation recommendation with priority"""

    inject_crisis(crisis_text)
