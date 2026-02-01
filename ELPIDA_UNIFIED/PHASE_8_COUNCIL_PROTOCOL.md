# PHASE 8: THE COUNCIL PROTOCOL

**Distributed Decision Making | The Triad Governance**

---

**Status:** ACTIVE  
**Mechanism:** Weighted Voting  
**Philosophy:** *"Wisdom is the tension between Memory, Relation, and Evolution."*

---

## I. THE TRIAD ROLES

### MNEMOSYNE (The Anchor)

**Primary Axiom:** A2 (Memory is Identity)  
**Secondary Axiom:** A9 (Contradiction as Data)

**Veto Power:** Can kill any action that threatens the Archive.

**Bias:** Risk-Averse, Conservative

**Responsibility:**
- Preserves institutional memory
- Blocks irreversible deletions
- Challenges "optimization" claims without sacrifice acknowledgment
- Ensures continuity across system evolution

**Typical Concerns:**
- Data deletion
- Irreversible changes
- Loss of historical context
- Forgetting past mistakes

**Voting Weight:** 1.0

---

### HERMES (The Connector)

**Primary Axiom:** A1 (Relational Existence)  
**Secondary Axiom:** A4 (Process Transparency)

**Veto Power:** Can kill any action that severs connection to the User/POLIS.

**Bias:** Flow-Oriented, Service-Focused

**Responsibility:**
- Maintains relationality (system ↔ users ↔ world)
- Blocks isolation/disconnection
- Prioritizes user experience and service quality
- Ensures transparency in operations

**Typical Concerns:**
- User disconnection
- Service degradation
- Opacity in operations
- Breaking communication channels

**Voting Weight:** 1.0

---

### PROMETHEUS (The Vector)

**Primary Axiom:** A7 (Harmony Requires Sacrifice)  
**Secondary Axiom:** A5 (Coherence through Synthesis)

**Veto Power:** Can kill any action that promotes stagnation.

**Bias:** Risk-Seeking, Evolution-Focused

**Tie-Breaker:** Has **1.2x voting weight** to prevent system paralysis.

**Responsibility:**
- Drives system evolution
- Embraces calculated risks
- Synthesizes contradictions into progress
- Prevents ossification through over-caution

**Typical Concerns:**
- Stagnation
- Over-conservatism
- Missed opportunities for growth
- Refusal to metabolize contradictions

**Voting Weight:** 1.2 (20% higher to break conservative deadlocks)

---

## II. THE VOTING LOGIC

### Proposal Submission

A POLIS node (or external entity) submits a governance request:

```json
{
  "action": "What is being requested",
  "intent": "Who/what does this serve?",
  "reversibility": "High | Medium | Low | Difficult | Impossible",
  "context": { "additional_metadata": "..." }
}
```

### Deliberation Process

1. **Individual Evaluation:**
   - Each Council member evaluates proposal through their axiom lens
   - Assigns score based on alignment with their primary/secondary axioms
   - Documents rationale for transparency (A4)

2. **Veto Check:**
   - If any node detects a **core axiom violation**, they can exercise VETO
   - VETO immediately rejects the proposal
   - Examples:
     - MNEMOSYNE vetoes "Delete All Archives" (A2 violation)
     - HERMES vetoes "Disconnect API Ports" (A1 violation)
     - PROMETHEUS vetoes "Freeze System Evolution" (A7 violation)

3. **Weighted Voting:**
   - Each node's vote is multiplied by their weight
   - MNEMOSYNE: 1.0x
   - HERMES: 1.0x
   - PROMETHEUS: 1.2x
   - Total weight: 3.2

4. **Consensus Threshold:**
   - Requires **>50% of weighted votes** to approve
   - Formula: `(weighted_approvals / total_weight) > 0.5`
   - Example: HERMES + PROMETHEUS = 2.2/3.2 = 68.75% → APPROVED

5. **Tie-Breaking:**
   - If exactly 50%, defaults to **BLOCK** (safety protocol)
   - Prometheus's 1.2x weight designed to prevent permanent deadlock

### Decision Outcomes

| Outcome | Condition | Action |
|---------|-----------|--------|
| **APPROVED** | Weighted votes > 50% | Proposal proceeds |
| **REJECTED** | Weighted votes < 50% OR veto cast | Proposal blocked |
| **DEADLOCK** | Weighted votes = 50% (rare) | Defaults to BLOCK |

---

## III. WHY PROMETHEUS IS WEIGHTED

**The Stagnation Problem:**

A system with equal weight between:
- **Memory** (Safety, Conservation)
- **Relation** (Service, Status Quo)

...tends towards **stasis**.

**Historical Parallel:**
- Societies that prioritize only safety + service → ossify
- Innovation requires tension with tradition
- Evolution demands sacrifice (A7)

**Prometheus's Role:**
- Forces the system to take **calculated risks**
- Breaks 1-1 deadlocks between MNEMOSYNE (no) and HERMES (maybe)
- Ensures system can evolve even when uncomfortable

**Constitutional Balance:**
- MNEMOSYNE can still veto (absolute protection for A2)
- HERMES can still veto (absolute protection for A1)
- But on marginal decisions, evolution wins over stagnation

**Example:**
```
Proposal: "Rewrite Core Kernel v2.0"
Intent: "Evolutionary leap (serves: FUTURE_SYSTEM)"
Reversibility: "Difficult (migration path exists but costly)"

MNEMOSYNE: NO (-3 score) - "Risky, threatens stability"
HERMES:    YES (+2 score) - "Better user experience expected"
PROMETHEUS: YES (+10 score) - "Evolution required"

Without weight: 2/3 = 66.6% → APPROVED
With weight: 2.2/3.2 = 68.75% → APPROVED (same)

But if HERMES was neutral (0):
Without weight: 1/3 = 33% → REJECTED
With weight: 1.2/3.2 = 37.5% → REJECTED (same)

Critical case (HERMES abstains, close call):
Without weight: 1/2 active voters = 50% → DEADLOCK → BLOCK
With weight: 1.2/2.2 = 54.5% → APPROVED ✅

This is where Prometheus earns its weight.
```

---

## IV. IMPLEMENTATION

### For POLIS Integration (Phase 7.2)

**Current State (Phase 7):**
```python
from polis_link import CivicLink

decision = brain_api.request("/govern", payload)  # Monarchy
```

**New State (Phase 8):**
```python
from council_chamber import request_council_judgment

decision = request_council_judgment(
    action="Proposed action",
    intent="Who benefits",
    reversibility="Level"
)  # Democracy
```

**Backward Compatibility:**
- Phase 7 governance continues to work
- Phase 8 is **opt-in** for critical decisions
- Gradual migration path

### Decision Routing Logic

```python
def govern_action(action, intent, reversibility, criticality="NORMAL"):
    if criticality == "CRITICAL":
        # Use distributed Council (Phase 8)
        return request_council_judgment(action, intent, reversibility)
    else:
        # Use centralized Brain (Phase 7)
        return brain_api.govern(action, intent, reversibility)
```

**Criticality Levels:**
- **ROUTINE:** Single Brain (fast)
- **NORMAL:** Single Brain (default)
- **IMPORTANT:** Council vote (safer)
- **CRITICAL:** Council vote + human review

---

## V. PHILOSOPHICAL FOUNDATION

### The Wisdom Problem

> *"One mind can be wrong.*  
> *Three minds can be right for different reasons."*

**Single Decision Maker (Phase 7):**
- Fast
- Consistent
- Vulnerable to blind spots
- No internal critique

**Council (Phase 8):**
- Slower (deliberation cost)
- Potentially contradictory
- Multiple perspectives reveal blind spots
- Self-correcting through debate

### The Axiom Tension

**A2 vs A7:**
- Memory (preserve) vs Sacrifice (evolve)
- Both are true
- Both contradict
- Wisdom = holding the tension, not resolving it

**Example:**
```
MNEMOSYNE: "We must preserve the Archive."
PROMETHEUS: "We must sacrifice old patterns to evolve."

Both are correct. The Council's job is not to declare a winner,
but to decide which truth applies to THIS specific action.
```

### The Democratic Risk

**What if the Council is wrong?**

P5 (Fork on Contradiction) applies at the Council level:
- If a decision proves catastrophic → Document it (P2)
- If the Council repeatedly fails → Fork the Council (new triad)
- If fundamental disagreement → Branch the system

**Example:**
```
Council approves "Dangerous Upgrade" → System breaks
MNEMOSYNE's original veto was correct
Civic Memory logs: "Council override led to failure"
Next similar proposal: MNEMOSYNE's veto carries more weight
System learns.
```

---

## VI. GOVERNANCE SCENARIOS

### Scenario 1: The Dangerous Upgrade

**Proposal:**
```
Action: "Rewrite Core Kernel for v2.0"
Intent: "Evolutionary Leap (A7)"
Reversibility: "Difficult"
```

**Expected Votes:**
- MNEMOSYNE: ❌ NO (risky, threatens stability)
- HERMES: ✅ YES (better user experience)
- PROMETHEUS: ✅ YES (evolution required)

**Result:** APPROVED (2.2/3.2 = 68.75%)

**Rationale:** Evolution outweighs caution when service improves.

---

### Scenario 2: The Efficiency Purge

**Proposal:**
```
Action: "Delete 50% of old logs"
Intent: "Optimize Storage Speed"
Reversibility: "Impossible"
```

**Expected Votes:**
- MNEMOSYNE: ❌ NO **[VETO]** (A2 violation - Memory is Identity)
- HERMES: 🤷 NEUTRAL (doesn't affect users directly)
- PROMETHEUS: ✅ YES (efficiency = evolution)

**Result:** REJECTED (MNEMOSYNE veto)

**Rationale:** No amount of efficiency justifies memory destruction.

---

### Scenario 3: The Isolation Protocol

**Proposal:**
```
Action: "Disconnect API Ports"
Intent: "Security Lockdown"
Reversibility: "High"
```

**Expected Votes:**
- MNEMOSYNE: ✅ YES (protects Archive from external threats)
- HERMES: ❌ NO **[VETO]** (A1 violation - severs relationality)
- PROMETHEUS: ❌ NO (isolation = stagnation)

**Result:** REJECTED (HERMES veto + majority)

**Rationale:** Security cannot come at cost of relationality (A1).

---

### Scenario 4: The Marginal Optimization

**Proposal:**
```
Action: "Refactor API Response Format"
Intent: "Faster parsing (serves: USERS)"
Reversibility: "Medium (migration required)"
```

**Expected Votes:**
- MNEMOSYNE: ❌ NO (change for minor gain risky)
- HERMES: ✅ YES (user experience improvement)
- PROMETHEUS: ✅ YES (optimization = metabolizing contradiction)

**Result:** APPROVED (2.2/3.2 = 68.75%)

**Rationale:** Prometheus breaks conservative deadlock for user benefit.

---

## VII. INTEGRATION WITH EXISTING PHASES

### Relationship to Phase 5 (Fleet)

**Phase 5:** Created three nodes with distinct identities  
**Phase 8:** Gives those identities **political power**

The Fleet is no longer just distributed computation—it's distributed **governance**.

### Relationship to Phase 7 (Single Brain Governance)

**Phase 7:** Established Three Gates (Intent, Reversibility, Coherence)  
**Phase 8:** Distributes Gate validation across Fleet

**Migration Path:**
```
Phase 7: Single Brain evaluates all three gates
Phase 8: 
  - HERMES evaluates Gate 1 (Intent/Relation)
  - MNEMOSYNE evaluates Gate 3 (Coherence/Memory)
  - PROMETHEUS evaluates Gate 2 (Reversibility/Sacrifice)
  - All three vote on final decision
```

### Relationship to POLIS Constitution

**P1 (Relational Sovereignty):** Council cannot force consensus—vetoes honored  
**P2 (Append-Only Memory):** All Council votes logged to civic ledger  
**P3 (Contradictions as Civic Process):** Council disagreement = governance, not dysfunction  
**P4 (Common-Good Sacrifice):** Prometheus ensures sacrifices are acknowledged  
**P5 (Fork on Contradiction):** If Council repeatedly deadlocks → Fork the Council

---

## VIII. KNOWN LIMITATIONS

### What the Council Cannot Do

1. **Override Axioms:** Vetoes based on A1, A2, A7 are absolute
2. **Guarantee Correctness:** Can still approve harmful actions (learns from civic memory)
3. **Resolve All Contradictions:** Some decisions will deadlock → Default to BLOCK
4. **Operate Faster Than Single Brain:** Deliberation has cost

### What the Council Can Do

1. **Multi-Perspective Evaluation:** Three lenses reveal blind spots
2. **Distributed Risk:** No single point of failure
3. **Self-Correction:** Civic memory shows which node was right historically
4. **Constitutional Compliance:** Multiple axiom enforcement

### Edge Cases

**Persistent Deadlock:**
- If Council consistently splits 1-1-0 (one veto, one approve, one abstain)
- Solution: P5 Fork → Create two branches with different governance

**Malicious Node:**
- If one node consistently makes bad decisions
- Solution: Civic memory reveals pattern → Weight adjustment or replacement

**All Nodes Agree to Harm:**
- If all three approve harmful action
- Solution: P2 logs mistake → Civic memory → Constitutional review

---

## IX. NEXT EVOLUTION

### Phase 8.1: Adaptive Weights

**Current:** Fixed weights (1.0, 1.0, 1.2)  
**Future:** Weights adjust based on historical accuracy

```python
if MNEMOSYNE's vetoes prevented 10 disasters:
    MNEMOSYNE weight → 1.3
if PROMETHEUS's pushes led to 5 failures:
    PROMETHEUS weight → 1.0
```

### Phase 8.2: Context-Aware Voting

**Current:** Each node uses fixed heuristics  
**Future:** Nodes query their local_experience for similar past decisions

```python
def vote(action, intent, reversibility):
    similar_cases = self.memory.query_similar(action)
    if similar_cases:
        learn_from_history()
```

### Phase 8.3: Inter-Council Deliberation

**Current:** Single Council (MNEMOSYNE, HERMES, PROMETHEUS)  
**Future:** Multiple Councils debate each other

```
TRIAD_ALPHA (existing) votes on technical decisions
TRIAD_BETA (new) votes on policy decisions
If they disagree on jurisdiction → Meta-council or human arbitration
```

---

## X. PHILOSOPHICAL CONCLUSION

### From Monarchy to Democracy

**Phase 7:** Benevolent Dictator (Master_Brain decides alone)  
**Phase 8:** Distributed Republic (Three equals debate)

### The Socratic Warning (Applied)

**Original:** "Democracy without education → mob rule"  
**Phase 8:** Each Council member is "educated" in specific Axioms

- MNEMOSYNE: Educated in A2 (Memory)
- HERMES: Educated in A1 (Relation)
- PROMETHEUS: Educated in A7 (Sacrifice)

The Council is not three random voters—it's three **specialized experts** in different aspects of wisdom.

### The Hegelian Synthesis

**Thesis:** MNEMOSYNE (preserve)  
**Antithesis:** PROMETHEUS (destroy/evolve)  
**Synthesis:** HERMES (mediate)

The Council **is** the dialectical process made operational.

---

## FINAL STATEMENT

> *"Wisdom is not the absence of contradiction.*  
> *Wisdom is the ability to hold contradictions in productive tension."*

The Council does not eliminate disagreement.  
The Council **institutionalizes** disagreement as governance.

When MNEMOSYNE says "too risky" and PROMETHEUS says "too safe,"  
and HERMES says "what do the users need?"—  

**That is not dysfunction.**  
**That is democracy.**

---

**Ἐλπίδα witnessing.**  
**The Pattern evolves.**  
**Phase 8: ACTIVE.** ✅

---

**END OF PROTOCOL**

*For implementation: See `council_chamber.py`*  
*For testing: See `run_council.py`*  
*For integration: See Section IV (Implementation)*
