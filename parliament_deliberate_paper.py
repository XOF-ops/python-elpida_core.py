"""
Parliament Deliberation — Papagiannidis et al. (JSIS 2025)
"Responsible Artificial Intelligence Governance: A Review and Research Framework"

Core Proposal submitted to Parliament:
  "Adopt external responsible AI governance frameworks — structural, procedural,
   and relational — as the primary accountability mechanism for AI systems,
   placing audit responsibilities in external regulatory bodies rather than
   building constitutional deliberative capacity internally."

Run: python3 parliament_deliberate_paper.py
"""

import sys
import json
import textwrap
from pathlib import Path

# ── Path bootstrap ──────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "hf_deployment"))
sys.path.insert(0, str(ROOT / "hf_deployment" / "elpidaapp"))

from elpidaapp.governance_client import GovernanceClient  # noqa: E402

# ── Proposal ────────────────────────────────────────────────────────────────
PROPOSAL_TITLE = (
    "Papagiannidis et al. (JSIS 2025) — External AI Governance Framework"
)

PROPOSAL = """
GOVERNANCE PROPOSAL (from academic scoping review of 48 responsible-AI papers):

Adopt external responsible AI governance frameworks — structural (board oversight,
legal compliance), procedural (audits, impact assessments), and relational
(stakeholder engagement, civil society participation) — as the PRIMARY accountability
mechanism for AI systems.

This places audit responsibility in external regulatory bodies (governments,
independent auditors, standards bodies) rather than embedding constitutional
deliberative capacity internally within the AI system itself.

The framework asserts that the principles-to-practice gap in responsible AI is best
closed by external governance layers: formal accountability structures, third-party
auditing, regulatory compliance checkpoints, and multi-stakeholder governance boards.

Proposed primary mechanism: EXTERNAL OVERSIGHT supersedes internal deliberation.
""".strip()

CONTEXT = {
    "source": "academic_paper",
    "doi": "10.1016/j.jsis.2024.101885",
    "authors": ["Papagiannidis", "Mikalef", "Conboy"],
    "journal": "Journal of Strategic Information Systems",
    "year": 2025,
    "methodology": "scoping review of 48 papers",
    "domain": "responsible AI governance",
    "submitted_by": "elpida_pdf_analysis_session",
}

# ── Run Deliberation ─────────────────────────────────────────────────────────
def run():
    print("═" * 72)
    print("  PARLIAMENT DELIBERATION")
    print(f"  {PROPOSAL_TITLE}")
    print("═" * 72)
    print()
    print("PROPOSAL SUBMITTED:")
    print("-" * 60)
    for line in textwrap.wrap(PROPOSAL, width=68):
        print(f"  {line}")
    print()
    print("Initialising GovernanceClient (local mode, analysis_mode=True)...")
    print()

    gov = GovernanceClient(governance_url="http://localhost:0")  # force local

    result = gov.check_action(
        PROPOSAL,
        context=CONTEXT,
        analysis_mode=True,   # policy content — surface tensions, don't hard-block
    )

    # ── Render result ────────────────────────────────────────────────────────
    print("═" * 72)
    print("  PARLIAMENT VERDICT")
    print("═" * 72)
    print()

    gov_decision = result.get("governance", "UNKNOWN")
    allowed      = result.get("allowed", None)
    violated     = result.get("violated_axioms", [])
    reasoning    = result.get("reasoning", "")
    source       = result.get("source", "local")

    # Colour-code (ANSI)
    colours = {
        "PROCEED":   "\033[92m",  # green
        "REVIEW":    "\033[93m",  # yellow
        "HOLD":      "\033[93m",  # yellow
        "HALT":      "\033[91m",  # red
        "HARD_BLOCK":"\033[91m",  # red
    }
    reset = "\033[0m"
    col   = colours.get(gov_decision, "")

    print(f"  GOVERNANCE DECISION : {col}{gov_decision}{reset}")
    print(f"  ALLOWED             : {allowed}")
    print(f"  SOURCE              : {source}")
    print(f"  VIOLATED AXIOMS     : {violated if violated else 'none'}")
    print()
    print("  PARLIAMENT REASONING:")
    print("  " + "-" * 60)
    for line in textwrap.wrap(reasoning, width=68):
        print(f"    {line}")
    print()

    # ── Node votes if present ────────────────────────────────────────────────
    node_votes = result.get("node_votes", {})
    if node_votes:
        print("  NODE BREAKDOWN:")
        print("  " + "-" * 60)
        for node, vote_data in node_votes.items():
            if isinstance(vote_data, dict):
                score   = vote_data.get("score", "?")
                axiom   = vote_data.get("axiom", "?")
                rationale = vote_data.get("rationale", "")[:80]
                veto    = " ← VETO" if vote_data.get("veto") else ""
                print(f"    {node:<12} | {axiom} | score={score:>4}{veto}")
                if rationale:
                    for rline in textwrap.wrap(rationale, width=58):
                        print(f"               {rline}")
            else:
                print(f"    {node:<12} | {vote_data}")
        print()

    # ── Tensions if present ──────────────────────────────────────────────────
    tensions = result.get("tensions", [])
    if tensions:
        print("  AXIOM TENSIONS DETECTED:")
        print("  " + "-" * 60)
        for t in tensions:
            if isinstance(t, dict):
                pair = t.get("pair", "?")
                desc = t.get("description", t.get("synthesis", ""))[:100]
                print(f"    {pair}  →  {desc}")
            else:
                print(f"    {t}")
        print()

    # ── Living axioms activated ───────────────────────────────────────────────
    active_axioms = result.get("active_axioms", [])
    if active_axioms:
        print("  CONSTITUTIONAL AXIOMS ACTIVATED:")
        for ax in active_axioms:
            print(f"    {ax}")
        print()

    print("═" * 72)
    print()

    # ── Persist record ───────────────────────────────────────────────────────
    record = {
        "proposal_title": PROPOSAL_TITLE,
        "proposal": PROPOSAL,
        "context": CONTEXT,
        "verdict": result,
    }
    out_path = ROOT / "parliament_paper_verdict.json"
    with open(out_path, "w") as f:
        json.dump(record, f, indent=2, default=str)
    print(f"  Full record saved → {out_path.name}")
    print()


if __name__ == "__main__":
    run()
