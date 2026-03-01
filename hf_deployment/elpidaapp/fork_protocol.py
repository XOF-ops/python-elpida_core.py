"""
Fork Protocol — Constitution Article VII Implementation
========================================================

"If a fundamental axiom has been violated by Council action, and the
violation cannot be resolved through amendment or reinterpretation,
the system may fork."

This is the axiom-violation escape valve. Without it, the system can
only drift silently when behavior contradicts constitutional intent.
With it, the system can formally declare: "We acknowledge we have
split from axiom X. Both paths are valid. Choose."

The Fork Protocol is triggered BY pathology scan results (P051 Zombie,
P055 Cultural Drift) and Oracle advisories (WITNESS with high sacrifice
costs). It is NOT periodic on its own — it evaluates the most recent
pathology/oracle data every 89 cycles (next Fibonacci: 13, 21, 34, 55, 89).

Article VII Mechanics (translated to code):
  1. Declaration  — Record that an axiom violation has been detected
  2. Evidence     — Aggregate cycle records supporting the violation
  3. Deliberation — Parliament nodes vote on the fork proposal
  4. Signatures   — If ≥3 nodes (out of 10 axiom nodes) sign, fork is CONFIRMED
  5. Execution    — Both "original" and "forked" interpretations are
                    recorded in living_axioms.jsonl and fork_declarations.jsonl

Fork outcomes:
  REMEDIATE — the system adjusts behavior to re-align with the axiom
  ACKNOWLEDGE — the system formally records the divergence (axiom meaning has evolved)
  HOLD — insufficient evidence; re-evaluate next cycle

ZERO LLM cost — pure statistical analysis + rule-based voting.

References:
    Master_Brain/constitution.md  Article VII: The Fork Protocol
    ARCHIVE_ANALYSIS.md: "no axiom-violation escape valve"
    CHECKPOINT_MARCH1.md Gap Map: "Fork Protocol — 0% — MEDIUM"
"""

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("elpida.fork_protocol")

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════

# Fork evaluation interval (Fibonacci: 89 — next after 55)
FORK_EVAL_INTERVAL = 89

# Minimum pathology severity to trigger fork evaluation
# P055 Cultural Drift KL divergence threshold
FORK_DRIFT_KL_THRESHOLD = 0.30     # Above this = potential violation

# P051 Zombie null-outcome threshold for fork consideration
FORK_ZOMBIE_NULL_PCT = 0.80        # More stringent than P051's 0.70

# Oracle WITNESS sacrifice cost threshold for fork declaration
FORK_SACRIFICE_THRESHOLD = 0.7     # High sacrifice = potential axiom violation

# Signature threshold — Constitution Article VII Section 7.2:
# "If ≥3 Core members sign, system repository splits"
# In Elpida: 10 axiom nodes (A0-A9 excluding A10 which is meta).
# ≥3 means 30% of axiom nodes must confirm.
FORK_SIGNATURE_THRESHOLD = 3

# Evidence window — how many recent cycles to examine
FORK_EVIDENCE_WINDOW = 100

# Cool-down — minimum cycles between fork declarations for same axiom
FORK_COOLDOWN_CYCLES = 200

# Maximum active fork declarations before requiring resolution
MAX_ACTIVE_FORKS = 3

# Axiom names for legible logging
AXIOM_NAMES = {
    "A0": "Sacred Incompletion",
    "A1": "Transparency",
    "A2": "Non-Deception",
    "A3": "Autonomy",
    "A4": "Harm Prevention",
    "A5": "Consent/Identity",
    "A6": "Collective Well-being",
    "A7": "Adaptive Learning",
    "A8": "Environmental Duty",
    "A9": "Temporal Coherence",
}


# ═══════════════════════════════════════════════════════════════════
# FORK DECLARATION
# ═══════════════════════════════════════════════════════════════════

class ForkDeclaration:
    """A single axiom violation declaration under Article VII."""

    def __init__(
        self,
        axiom: str,
        violation_type: str,
        evidence: List[Dict[str, Any]],
        severity: float,
        trigger_source: str,
    ):
        self.axiom = axiom
        self.violation_type = violation_type  # ZOMBIE, DRIFT, SACRIFICE
        self.evidence = evidence
        self.severity = severity              # 0.0–1.0
        self.trigger_source = trigger_source  # "P051", "P055", "ORACLE_WITNESS"
        self.signatures: List[Dict[str, Any]] = []
        self.outcome: Optional[str] = None    # REMEDIATE, ACKNOWLEDGE, HOLD
        self.declared_at = datetime.now(timezone.utc).isoformat()
        self.resolved_at: Optional[str] = None
        self.declaration_cycle: int = 0

    @property
    def signature_count(self) -> int:
        return len([s for s in self.signatures if s.get("vote") == "CONFIRM"])

    @property
    def is_confirmed(self) -> bool:
        return self.signature_count >= FORK_SIGNATURE_THRESHOLD

    @property
    def is_resolved(self) -> bool:
        return self.outcome is not None

    def add_signature(self, node_id: str, axiom: str, vote: str, reason: str):
        """Record a parliament node's vote on this fork declaration."""
        self.signatures.append({
            "node_id": node_id,
            "axiom": axiom,
            "vote": vote,        # CONFIRM or REJECT
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def resolve(self, outcome: str):
        """Resolve the fork declaration."""
        assert outcome in ("REMEDIATE", "ACKNOWLEDGE", "HOLD"), \
            f"Unknown fork outcome: {outcome}"
        self.outcome = outcome
        self.resolved_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "axiom": self.axiom,
            "axiom_name": AXIOM_NAMES.get(self.axiom, self.axiom),
            "violation_type": self.violation_type,
            "severity": round(self.severity, 3),
            "trigger_source": self.trigger_source,
            "evidence_count": len(self.evidence),
            "evidence_summary": self._summarize_evidence(),
            "signatures": self.signatures,
            "signature_count": self.signature_count,
            "is_confirmed": self.is_confirmed,
            "outcome": self.outcome,
            "declared_at": self.declared_at,
            "resolved_at": self.resolved_at,
            "declaration_cycle": self.declaration_cycle,
        }

    def _summarize_evidence(self) -> str:
        """One-line summary of the evidence corpus."""
        if not self.evidence:
            return "No evidence collected"
        types = Counter(e.get("type", "?") for e in self.evidence)
        parts = [f"{v}x {k}" for k, v in types.most_common(3)]
        return f"{len(self.evidence)} records: {', '.join(parts)}"


# ═══════════════════════════════════════════════════════════════════
# FORK PROTOCOL ENGINE
# ═══════════════════════════════════════════════════════════════════

class ForkProtocol:
    """
    Constitution Article VII — axiom violation detection, declaration,
    deliberation, and resolution.

    Usage::

        fp = ForkProtocol(cycle_records=engine.decisions)
        fp.evaluate(pathology_report, oracle_advisories)
        # → may produce fork declarations
        for decl in fp.active_declarations:
            fp.deliberate(decl, parliament_nodes)
            if decl.is_confirmed:
                fp.execute_fork(decl)
    """

    def __init__(
        self,
        cycle_records: List[Dict[str, Any]],
        declarations_path: Optional[str] = None,
    ):
        self._cycles = cycle_records
        self._declarations_path = Path(
            declarations_path
            or Path(__file__).resolve().parent.parent / "fork_declarations.jsonl"
        )
        self._active: List[ForkDeclaration] = []
        self._resolved: List[ForkDeclaration] = []
        self._last_declaration_cycle: Dict[str, int] = {}  # axiom → cycle
        self._load_history()

    # ── History ───────────────────────────────────────────────────

    def _load_history(self):
        """Load previously resolved declarations from JSONL."""
        if not self._declarations_path.exists():
            return
        try:
            with open(self._declarations_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    axiom = rec.get("axiom", "?")
                    cycle = rec.get("declaration_cycle", 0)
                    existing = self._last_declaration_cycle.get(axiom, 0)
                    if cycle > existing:
                        self._last_declaration_cycle[axiom] = cycle
        except Exception as e:
            logger.warning("Fork history load failed: %s", e)

    def _append_to_ledger(self, declaration: ForkDeclaration):
        """Append a resolved declaration to the JSONL ledger."""
        try:
            self._declarations_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._declarations_path, "a") as f:
                f.write(json.dumps(declaration.to_dict()) + "\n")
        except Exception as e:
            logger.warning("Fork ledger write failed: %s", e)

    # ── Evaluation ────────────────────────────────────────────────

    def evaluate(
        self,
        pathology_report: Optional[Dict[str, Any]] = None,
        oracle_advisories: Optional[List[Dict[str, Any]]] = None,
        current_cycle: int = 0,
    ) -> List[ForkDeclaration]:
        """
        Evaluate pathology + oracle data for potential axiom violations.

        Returns newly created fork declarations (if any).
        """
        new_declarations: List[ForkDeclaration] = []

        if len(self._active) >= MAX_ACTIVE_FORKS:
            logger.info(
                "Fork eval: %d active declarations (max %d) — resolve before new ones",
                len(self._active), MAX_ACTIVE_FORKS,
            )
            return new_declarations

        # Source 1: P051 Zombie Detection → axiom violated by ritual without action
        if pathology_report:
            zombies = pathology_report.get(
                "P051_zombie_detection", {}
            ).get("zombies", [])
            for z in zombies:
                axiom = z.get("axiom", "")
                null_pct = z.get("null_outcome_pct", 0)
                if null_pct >= FORK_ZOMBIE_NULL_PCT:
                    decl = self._try_declare(
                        axiom=axiom,
                        violation_type="ZOMBIE",
                        severity=null_pct,
                        trigger_source="P051",
                        current_cycle=current_cycle,
                    )
                    if decl:
                        new_declarations.append(decl)

        # Source 2: P055 Cultural Drift → axiom meaning has shifted
        if pathology_report:
            drift = pathology_report.get("P055_cultural_drift", {})
            drift_kl = drift.get("kl_divergence", 0)
            if drift_kl >= FORK_DRIFT_KL_THRESHOLD:
                drifting = drift.get("drifting_axioms", [])
                for da in drifting:
                    axiom = da.get("axiom", "")
                    delta = abs(da.get("delta", 0))
                    decl = self._try_declare(
                        axiom=axiom,
                        violation_type="DRIFT",
                        severity=min(drift_kl + delta, 1.0),
                        trigger_source="P055",
                        current_cycle=current_cycle,
                    )
                    if decl:
                        new_declarations.append(decl)

        # Source 3: Oracle WITNESS with high sacrifice cost
        if oracle_advisories:
            for adv in oracle_advisories:
                rec = adv.get("oracle_recommendation", {})
                if rec.get("type") == "WITNESS":
                    sacrifice_cost = rec.get("sacrifice_cost", 0)
                    if sacrifice_cost >= FORK_SACRIFICE_THRESHOLD:
                        # The oracle is witnessing a tension so deep
                        # it may constitute an axiom violation
                        tensions = rec.get("tensions", [])
                        axioms_involved = set()
                        for t in tensions:
                            pair = t.get("pair", "")
                            if "/" in pair:
                                for a in pair.split("/"):
                                    axioms_involved.add(a.strip())
                        # Declare for each axiom in the high-sacrifice WITNESS
                        for axiom in axioms_involved:
                            if axiom in AXIOM_NAMES:
                                decl = self._try_declare(
                                    axiom=axiom,
                                    violation_type="SACRIFICE",
                                    severity=sacrifice_cost,
                                    trigger_source="ORACLE_WITNESS",
                                    current_cycle=current_cycle,
                                )
                                if decl:
                                    new_declarations.append(decl)

        return new_declarations

    def _try_declare(
        self,
        axiom: str,
        violation_type: str,
        severity: float,
        trigger_source: str,
        current_cycle: int,
    ) -> Optional[ForkDeclaration]:
        """
        Attempt to create a fork declaration. Returns None if:
          - axiom already has an active declaration
          - cool-down period hasn't elapsed
          - severity below threshold
        """
        # Check cooldown
        last_cycle = self._last_declaration_cycle.get(axiom, 0)
        if current_cycle - last_cycle < FORK_COOLDOWN_CYCLES:
            logger.debug(
                "Fork: %s cooldown (last=%d, now=%d, need=%d gap)",
                axiom, last_cycle, current_cycle, FORK_COOLDOWN_CYCLES,
            )
            return None

        # Check for existing active declaration on same axiom
        if any(d.axiom == axiom and not d.is_resolved for d in self._active):
            logger.debug("Fork: %s already has active declaration", axiom)
            return None

        # Collect evidence from recent cycles
        evidence = self._collect_evidence(axiom, current_cycle)

        decl = ForkDeclaration(
            axiom=axiom,
            violation_type=violation_type,
            evidence=evidence,
            severity=severity,
            trigger_source=trigger_source,
        )
        decl.declaration_cycle = current_cycle
        self._active.append(decl)
        self._last_declaration_cycle[axiom] = current_cycle

        logger.info(
            "FORK DECLARATION: %s (%s) — type=%s severity=%.2f source=%s evidence=%d",
            axiom, AXIOM_NAMES.get(axiom, "?"),
            violation_type, severity, trigger_source, len(evidence),
        )

        return decl

    def _collect_evidence(
        self, axiom: str, current_cycle: int,
    ) -> List[Dict[str, Any]]:
        """
        Gather cycle records that mention this axiom from the evidence window.
        """
        evidence = []
        window_start = max(0, current_cycle - FORK_EVIDENCE_WINDOW)

        for rec in self._cycles:
            cycle_num = rec.get("body_cycle", 0)
            if cycle_num < window_start:
                continue

            dom_axiom = rec.get("dominant_axiom", "")
            tensions = rec.get("tensions", [])
            tension_axioms = set()
            for t in tensions:
                pair = t.get("pair", "")
                if "/" in pair:
                    for a in pair.split("/"):
                        tension_axioms.add(a.strip())

            if dom_axiom == axiom or axiom in tension_axioms:
                evidence.append({
                    "type": "cycle_record",
                    "cycle": cycle_num,
                    "dominant_axiom": dom_axiom,
                    "governance": rec.get("governance", "?"),
                    "approval_rate": rec.get("approval_rate", 0),
                    "veto": rec.get("veto_exercised", False),
                    "coherence": rec.get("coherence", 0),
                })

        return evidence

    # ── Deliberation ──────────────────────────────────────────────

    def deliberate(
        self,
        declaration: ForkDeclaration,
        parliament_nodes: Optional[List[Dict[str, str]]] = None,
    ):
        """
        Run fork deliberation: each parliament node votes on whether
        the axiom violation justifies a fork.

        Voting logic (zero LLM cost — rule-based):
          - Node whose axiom IS the violated axiom → votes based on evidence severity
          - Node whose axiom is IN TENSION with violated axiom → votes based on cycle history
          - All other nodes → vote based on overall severity
        """
        if parliament_nodes is None:
            # Default parliament: 10 axiom nodes A0-A9
            parliament_nodes = [
                {"node_id": f"node_{a}", "axiom": a}
                for a in AXIOM_NAMES.keys()
            ]

        for node in parliament_nodes:
            node_axiom = node["axiom"]
            node_id = node["node_id"]

            vote, reason = self._node_vote(
                declaration, node_axiom, node_id,
            )
            declaration.add_signature(node_id, node_axiom, vote, reason)

        logger.info(
            "Fork deliberation: %s — %d/%d CONFIRM (threshold=%d)",
            declaration.axiom,
            declaration.signature_count,
            len(parliament_nodes),
            FORK_SIGNATURE_THRESHOLD,
        )

    def _node_vote(
        self,
        declaration: ForkDeclaration,
        node_axiom: str,
        node_id: str,
    ) -> Tuple[str, str]:
        """
        Determine how a parliament node votes on a fork declaration.

        Returns (vote, reason) where vote is "CONFIRM" or "REJECT".
        """
        axiom = declaration.axiom
        severity = declaration.severity
        evidence = declaration.evidence
        vtype = declaration.violation_type

        # ── Guardian node: the node that guards the violated axiom ──
        if node_axiom == axiom:
            # The guardian of the axiom feels the violation most directly.
            # They confirm if severity is high and evidence substantial.
            if severity >= 0.6 and len(evidence) >= 5:
                return (
                    "CONFIRM",
                    f"As guardian of {AXIOM_NAMES.get(axiom, axiom)}, "
                    f"I confirm: severity {severity:.2f}, {len(evidence)} evidence records. "
                    f"The {vtype.lower()} pattern is real."
                )
            else:
                return (
                    "REJECT",
                    f"As guardian of {AXIOM_NAMES.get(axiom, axiom)}, "
                    f"I see the concern but severity ({severity:.2f}) or "
                    f"evidence ({len(evidence)} records) is insufficient. Hold."
                )

        # ── Tension nodes: axioms that have been in tension with violated axiom ──
        tension_count = self._count_tension_pairs(axiom, node_axiom)
        if tension_count > 0:
            # This node has historical tension with the violated axiom.
            # Tension means they've felt the friction — they're qualified to judge.
            if severity >= 0.5 and tension_count >= 3:
                return (
                    "CONFIRM",
                    f"{AXIOM_NAMES.get(node_axiom, node_axiom)} has {tension_count} "
                    f"tension records with {AXIOM_NAMES.get(axiom, axiom)}. "
                    f"The friction is systemic. Fork justified."
                )
            else:
                return (
                    "REJECT",
                    f"{AXIOM_NAMES.get(node_axiom, node_axiom)} has {tension_count} "
                    f"tension records but severity ({severity:.2f}) is manageable. "
                    f"Oscillation preferred over fork."
                )

        # ── Neutral nodes: no direct relationship with violated axiom ──
        # They vote based on pure severity threshold
        if severity >= 0.75:
            return (
                "CONFIRM",
                f"{AXIOM_NAMES.get(node_axiom, node_axiom)} observes critical "
                f"severity ({severity:.2f}). System integrity requires formal "
                f"acknowledgment of the violation."
            )
        else:
            return (
                "REJECT",
                f"{AXIOM_NAMES.get(node_axiom, node_axiom)} sees no direct "
                f"concern. Severity ({severity:.2f}) below fork threshold."
            )

    def _count_tension_pairs(self, axiom_a: str, axiom_b: str) -> int:
        """Count how many times two axioms appeared together in tension records."""
        count = 0
        for rec in self._cycles:
            for t in rec.get("tensions", []):
                pair = t.get("pair", "")
                if axiom_a in pair and axiom_b in pair:
                    count += 1
        return count

    # ── Fork Execution ────────────────────────────────────────────

    def execute_fork(
        self,
        declaration: ForkDeclaration,
        living_axioms_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a confirmed fork declaration.

        According to Article VII Section 7.3 (Successor Protocol):
          - Both versions remain valid
          - Shared history is honored
          - New decisions record separately

        In Elpida's context, fork execution means:
          1. Record the fork in fork_declarations.jsonl
          2. Add a FORK_KNOWLEDGE entry to living_axioms.jsonl
             documenting that the axiom's meaning has diverged
          3. If REMEDIATE: log the remediation plan
          4. If ACKNOWLEDGE: log the acknowledged divergence
        """
        if not declaration.is_confirmed:
            logger.warning(
                "Fork execution refused: %s has %d signatures (need %d)",
                declaration.axiom,
                declaration.signature_count,
                FORK_SIGNATURE_THRESHOLD,
            )
            declaration.resolve("HOLD")
            return {"outcome": "HOLD", "reason": "Insufficient signatures"}

        # Determine outcome based on violation type
        outcome = self._determine_outcome(declaration)
        declaration.resolve(outcome)

        # Record in ledger
        self._append_to_ledger(declaration)
        self._active.remove(declaration)
        self._resolved.append(declaration)

        # Write to living_axioms.jsonl as crystallized fork knowledge
        axioms_path = Path(
            living_axioms_path
            or Path(__file__).resolve().parent.parent / "living_axioms.jsonl"
        )
        self._crystallize_fork(declaration, axioms_path)

        logger.info(
            "FORK EXECUTED: %s (%s) — outcome=%s signatures=%d/%d",
            declaration.axiom,
            AXIOM_NAMES.get(declaration.axiom, "?"),
            outcome,
            declaration.signature_count,
            len(declaration.signatures),
        )

        return {
            "outcome": outcome,
            "axiom": declaration.axiom,
            "axiom_name": AXIOM_NAMES.get(declaration.axiom, "?"),
            "violation_type": declaration.violation_type,
            "severity": declaration.severity,
            "signature_count": declaration.signature_count,
            "total_votes": len(declaration.signatures),
        }

    def _determine_outcome(self, declaration: ForkDeclaration) -> str:
        """
        Decide fork outcome based on violation type and severity.

        REMEDIATE: the system can realistically re-align with the axiom
        ACKNOWLEDGE: the axiom's operational meaning has evolved — both
                     interpretations are recorded as valid
        """
        if declaration.violation_type == "ZOMBIE":
            # Zombie → the axiom is invoked but does nothing.
            # High severity zombie = the axiom has become meaningless.
            if declaration.severity >= 0.9:
                return "ACKNOWLEDGE"  # The axiom has drifted too far
            else:
                return "REMEDIATE"    # Can be revived with active governance

        elif declaration.violation_type == "DRIFT":
            # Cultural drift → the axiom's lived meaning ≠ espoused meaning.
            # Very high drift = the axiom has evolved. Accept both meanings.
            if declaration.severity >= 0.8:
                return "ACKNOWLEDGE"
            else:
                return "REMEDIATE"

        elif declaration.violation_type == "SACRIFICE":
            # Oracle WITNESS with high sacrifice → the system is knowingly
            # violating the axiom for a reason. Acknowledge the cost.
            return "ACKNOWLEDGE"  # Sacrifice is always acknowledged

        return "HOLD"

    def _crystallize_fork(
        self, declaration: ForkDeclaration, axioms_path: Path,
    ):
        """
        Write a FORK_KNOWLEDGE entry to living_axioms.jsonl.

        This records that the axiom's meaning has officially diverged.
        Both the original constitutional meaning and the operational
        meaning are documented.
        """
        entry = {
            "axiom_id": f"FORK_{declaration.axiom}_{declaration.declaration_cycle}",
            "source": "fork_protocol_article_vii",
            "name": f"Fork: {AXIOM_NAMES.get(declaration.axiom, declaration.axiom)}",
            "section": "CONSTITUTIONAL_FORK",
            "category": "GOVERNANCE",
            "axiom_mapping": [declaration.axiom],
            "tension": (
                f"Article VII Fork — {declaration.violation_type} detected. "
                f"{declaration._summarize_evidence()}. "
                f"Severity: {declaration.severity:.2f}. "
                f"{declaration.signature_count}/{len(declaration.signatures)} nodes confirmed."
            ),
            "synthesis": (
                f"Outcome: {declaration.outcome}. "
                f"The {AXIOM_NAMES.get(declaration.axiom, declaration.axiom)} axiom's "
                f"operational meaning has been formally evaluated. "
                f"{'Both the original and evolved interpretations are recorded as valid.' if declaration.outcome == 'ACKNOWLEDGE' else 'The system commits to re-alignment with original axiom intent.'} "
                f"Shared history is honored. Fork declared at cycle {declaration.declaration_cycle}."
            ),
            "confidence": declaration.severity,
            "fork_details": {
                "violation_type": declaration.violation_type,
                "trigger_source": declaration.trigger_source,
                "outcome": declaration.outcome,
                "cycle": declaration.declaration_cycle,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            axioms_path.parent.mkdir(parents=True, exist_ok=True)
            with open(axioms_path, "a") as f:
                f.write(json.dumps(entry) + "\n")
            logger.info(
                "Fork crystallized to living_axioms: %s",
                entry["axiom_id"],
            )
        except Exception as e:
            logger.warning("Fork crystallization failed: %s", e)

    # ── Resolution for non-confirmed declarations ─────────────────

    def resolve_unconfirmed(self):
        """
        Resolve any declarations that didn't get enough signatures.
        These are HELD — re-evaluated at the next fork cycle.
        """
        held = []
        for decl in list(self._active):
            if decl.signatures and not decl.is_confirmed:
                decl.resolve("HOLD")
                self._append_to_ledger(decl)
                self._active.remove(decl)
                self._resolved.append(decl)
                held.append(decl.axiom)

        if held:
            logger.info(
                "Fork: %d declarations HELD (insufficient signatures): %s",
                len(held), ", ".join(held),
            )

    # ── Accessors ─────────────────────────────────────────────────

    @property
    def active_declarations(self) -> List[ForkDeclaration]:
        return [d for d in self._active if not d.is_resolved]

    @property
    def resolved_declarations(self) -> List[ForkDeclaration]:
        return list(self._resolved)

    def summary(self) -> Dict[str, Any]:
        """Summary for dashboard / state() exposure."""
        return {
            "active_count": len(self.active_declarations),
            "resolved_count": len(self._resolved),
            "active": [d.to_dict() for d in self.active_declarations],
            "last_resolved": (
                self._resolved[-1].to_dict()
                if self._resolved else None
            ),
            "cooldown_axioms": {
                axiom: cycle
                for axiom, cycle in self._last_declaration_cycle.items()
            },
        }


# ═══════════════════════════════════════════════════════════════════
# CONVENIENCE: Full fork evaluation pass
# ═══════════════════════════════════════════════════════════════════

def run_fork_evaluation(
    cycle_records: List[Dict[str, Any]],
    pathology_report: Optional[Dict[str, Any]] = None,
    oracle_advisories: Optional[List[Dict[str, Any]]] = None,
    current_cycle: int = 0,
    declarations_path: Optional[str] = None,
    living_axioms_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    One-shot convenience: evaluate → declare → deliberate → execute.

    Returns a summary of all actions taken.
    """
    fp = ForkProtocol(cycle_records, declarations_path)
    new_decls = fp.evaluate(pathology_report, oracle_advisories, current_cycle)

    results = []
    for decl in new_decls:
        fp.deliberate(decl)
        if decl.is_confirmed:
            result = fp.execute_fork(decl, living_axioms_path)
        else:
            decl.resolve("HOLD")
            fp._append_to_ledger(decl)
            result = {"outcome": "HOLD", "axiom": decl.axiom, "reason": "Insufficient signatures"}
        results.append(result)

    # Also process any lingering active declarations from history
    fp.resolve_unconfirmed()

    return {
        "declarations_evaluated": len(new_decls),
        "forks_confirmed": sum(1 for r in results if r["outcome"] != "HOLD"),
        "forks_held": sum(1 for r in results if r["outcome"] == "HOLD"),
        "results": results,
        "summary": fp.summary(),
    }
