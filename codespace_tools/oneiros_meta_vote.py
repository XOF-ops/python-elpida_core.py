#!/usr/bin/env python3
"""
Oneiros Meta Vote (AoA) for Copilot-side sleep-window orchestration.

Purpose:
- Run a federation-level meta vote for the active 4-agent setup.
- Optionally add DeepSeek + Codex ballots as meta-layer advisors.
- Produce a two-phase operating split for the 4-hour sleep window:
  - Phase 1 (0-2h): Copilot leads BODY-side/subconscious work.
  - Phase 2 (2-4h): Push + handoff before Claude wake/watch boundary.

This script is intentionally non-destructive:
- Reads bridge/workflow state.
- Writes a JSON report to reports/.
- Does not modify production files.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = ROOT / ".claude" / "bridge"
DEFAULT_REPORT = ROOT / "reports" / "oneiros_meta_vote_latest.json"
BRIDGE_TARGET_MAP = {
    "gemini": BRIDGE_DIR / "for_gemini.md",
    "computer": BRIDGE_DIR / "for_computer.md",
    "claude": BRIDGE_DIR / "for_claude.md",
}


@dataclass
class Ballot:
    agent: str
    vote: str
    weight: float
    reason: str
    source: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def run_cmd(cmd: List[str]) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=25)
        return p.returncode, p.stdout, p.stderr
    except Exception as e:
        return 1, "", str(e)


def latest_workflow_run(workflow_name: str) -> Dict[str, str]:
    cmd = [
        "gh",
        "run",
        "list",
        "--repo",
        "XOF-ops/python-elpida_core.py",
        "--workflow",
        workflow_name,
        "--limit",
        "1",
        "--json",
        "databaseId,status,conclusion,createdAt,updatedAt,headSha,displayTitle",
    ]
    rc, out, err = run_cmd(cmd)
    if rc != 0:
        return {"error": err.strip() or "gh run list failed"}
    try:
        rows = json.loads(out or "[]")
    except json.JSONDecodeError:
        return {"error": "Invalid gh JSON output"}
    if not rows:
        return {"error": "No runs found"}
    row = rows[0]
    return {
        "id": str(row.get("databaseId", "")),
        "status": str(row.get("status", "")),
        "conclusion": str(row.get("conclusion", "")),
        "createdAt": str(row.get("createdAt", "")),
        "updatedAt": str(row.get("updatedAt", "")),
        "headSha": str(row.get("headSha", "")),
        "displayTitle": str(row.get("displayTitle", "")),
    }


def extract_latest_verdict(text: str) -> str:
    """Extract latest PASS/CONDITION/REDIRECT/BLOCK style verdict token."""
    if not text:
        return "UNKNOWN"

    # Prefer explicit "VERDICT: X" lines.
    verdict_lines = re.findall(r"VERDICT\s*[:\-]\s*\**\s*([A-Z_]+)\**", text, flags=re.IGNORECASE)
    if verdict_lines:
        return verdict_lines[-1].upper()

    # Fall back to section heading format.
    keyword_hits = re.findall(r"\b(PASS|CONDITION|REDIRECT|BLOCK|PROCEED|HOLD|ESCALATE)\b", text, flags=re.IGNORECASE)
    if keyword_hits:
        return keyword_hits[-1].upper()

    return "UNKNOWN"


def detect_signals(bridge_text: str) -> Dict[str, bool]:
    # Match concrete runtime evidence lines rather than generic checklist text.
    integrated = bool(
        re.search(r"(?:⚡\s*)?D0\s+sees\s+D16\s*:\s*\d+", bridge_text, flags=re.IGNORECASE)
    )
    d4_gate = bool(
        re.search(r"🛡️\s*D4\s+SAFETY\s+GATE\s*:\s*D16\s+input\s+blocked", bridge_text, flags=re.IGNORECASE)
    )
    d0_blocked = bool(
        re.search(r"🛡️\s*D0\s+BLOCKED\s+D16\s*:\s*all\s+\d+\s+agency\s+proposals\s+dropped", bridge_text, flags=re.IGNORECASE)
    )

    return {
        "d16_integrated": integrated,
        "d4_safety_gate": d4_gate,
        "d0_blocked": d0_blocked,
        "silent_pull": bool(re.search(r"silent_pull", bridge_text, flags=re.IGNORECASE)),
        "witness_tag": bool(re.search(r"V6\.0\.0[-_ ]WITNESS|integrated_success", bridge_text, flags=re.IGNORECASE)),
    }


def vote_score(vote: str) -> float:
    mapping = {
        "PROCEED": 1.0,
        "HOLD": 0.0,
        "ESCALATE": -1.0,
        "ABSTAIN": 0.0,
    }
    return mapping.get(vote.upper(), 0.0)


def choose_core_ballots(
    signals: Dict[str, bool],
    gemini_verdict: str,
    d16_log_run: Dict[str, str],
    fire_run: Dict[str, str],
) -> List[Ballot]:
    ballots: List[Ballot] = []

    d16_log_success = d16_log_run.get("conclusion") == "success"
    fire_success = fire_run.get("conclusion") == "success"

    # Copilot ballot: prefers objective workflow + integration signal.
    if signals["d16_integrated"] and d16_log_success:
        ballots.append(Ballot("copilot", "PROCEED", 1.0, "D16 integration signal confirmed by log workflow", "workflow+bridge"))
    elif fire_success:
        ballots.append(Ballot("copilot", "HOLD", 1.0, "Run fired but integration signal not confirmed yet", "workflow"))
    else:
        ballots.append(Ballot("copilot", "ESCALATE", 1.0, "No successful fire/run evidence", "workflow"))

    # Claude ballot: witness/integration lines are the decision anchor.
    if signals["witness_tag"] or signals["d16_integrated"]:
        ballots.append(Ballot("claude_code", "PROCEED", 1.0, "Witness-grade D16 integration evidence present", "bridge"))
    elif signals["silent_pull"]:
        ballots.append(Ballot("claude_code", "HOLD", 1.0, "Silent pull reported without final integration evidence", "bridge"))
    else:
        ballots.append(Ballot("claude_code", "HOLD", 1.0, "No final witness marker yet", "bridge"))

    # Gemini ballot: normalize old REDIRECT/CONDITION once hard evidence exists.
    gv = gemini_verdict.upper()
    if gv in {"PASS", "PROCEED"}:
        ballots.append(Ballot("gemini", "PROCEED", 1.0, f"Gemini verdict={gv}", "from_gemini"))
    elif gv in {"BLOCK", "ESCALATE"}:
        ballots.append(Ballot("gemini", "ESCALATE", 1.0, f"Gemini verdict={gv}", "from_gemini"))
    elif gv in {"CONDITION", "REDIRECT", "HOLD"}:
        if signals["d16_integrated"]:
            ballots.append(Ballot("gemini", "PROCEED", 1.0, f"Gemini pre-evidence {gv} closed by integration witness", "from_gemini+logs"))
        else:
            ballots.append(Ballot("gemini", "HOLD", 1.0, f"Gemini verdict={gv} pending stronger runtime evidence", "from_gemini"))
    else:
        ballots.append(Ballot("gemini", "HOLD", 1.0, "Gemini verdict unknown", "from_gemini"))

    # Computer ballot: archival relay posture.
    if signals["d16_integrated"]:
        ballots.append(Ballot("computer_d13", "PROCEED", 1.0, "Relay path closed with integration witness", "for_claude/from_archive"))
    elif signals["silent_pull"]:
        ballots.append(Ballot("computer_d13", "HOLD", 1.0, "Relay indicates silent pull in previous window", "for_claude"))
    else:
        ballots.append(Ballot("computer_d13", "HOLD", 1.0, "No final relay closure marker yet", "for_claude"))

    return ballots


def maybe_external_ballot(
    enabled: bool,
    provider: str,
    model: str,
    label: str,
    evidence: Dict[str, object],
) -> Ballot:
    if not enabled:
        return Ballot(label, "ABSTAIN", 0.5, "External ballot disabled", "config")

    try:
        from llm_client import LLMClient
    except Exception as e:
        return Ballot(label, "ABSTAIN", 0.5, f"LLM client unavailable: {e}", "runtime")

    client = LLMClient()
    if provider not in client.available_providers():
        return Ballot(label, "ABSTAIN", 0.5, f"Provider key not configured ({provider})", "env")

    prompt = (
        "You are an external constitutional auditor for Elpida.\n"
        "Given this evidence JSON, return exactly one token on first line: PROCEED, HOLD, or ESCALATE.\n"
        "On second line, provide one short reason.\n"
        f"Evidence: {json.dumps(evidence, ensure_ascii=False)}"
    )

    text = client.call(provider, prompt, model=model, max_tokens=180)
    if not text:
        return Ballot(label, "ABSTAIN", 0.5, f"No response from {provider}", "llm")

    m = re.search(r"\b(PROCEED|HOLD|ESCALATE)\b", text, flags=re.IGNORECASE)
    if not m:
        return Ballot(label, "ABSTAIN", 0.5, f"Unparsable response: {text[:120]}", f"{provider}:{model}")

    vote = m.group(1).upper()
    reason = text.strip().splitlines()
    reason_line = reason[1].strip() if len(reason) > 1 else text[:120]
    return Ballot(label, vote, 0.5, reason_line, f"{provider}:{model}")


def aggregate(ballots: List[Ballot]) -> Dict[str, object]:
    weighted_total = 0.0
    total_weight = 0.0
    counts = {"PROCEED": 0, "HOLD": 0, "ESCALATE": 0, "ABSTAIN": 0}

    core = [b for b in ballots if b.agent in {"copilot", "claude_code", "gemini", "computer_d13"}]

    for b in ballots:
        v = b.vote.upper()
        counts[v] = counts.get(v, 0) + 1
        weighted_total += vote_score(v) * b.weight
        total_weight += b.weight

    weighted_avg = weighted_total / total_weight if total_weight else 0.0

    any_core_escalate = any(b.vote.upper() == "ESCALATE" for b in core)
    core_proceed = sum(1 for b in core if b.vote.upper() == "PROCEED")

    if any_core_escalate:
        verdict = "ESCALATE"
    elif core_proceed >= 3:
        verdict = "PROCEED"
    elif core_proceed == 2:
        verdict = "CONDITIONAL_PROCEED"
    else:
        verdict = "HOLD"

    return {
        "counts": counts,
        "weighted_average": round(weighted_avg, 3),
        "core_proceed": core_proceed,
        "verdict": verdict,
    }


def build_phase_plan(verdict: str) -> Dict[str, object]:
    phase1 = {
        "window": "T+0h to T+2h",
        "lead": "copilot",
        "objective": "BODY-side and subconscious orchestration during Oneiros sleep window",
        "assignments": [
            {
                "owner": "copilot",
                "task": "Run AoA meta vote, verify bridge/workflow evidence, and keep monitor workflows green.",
            },
            {
                "owner": "gemini",
                "task": "Produce D4/D5 safety-consent adjudication on latest evidence in from_gemini.md.",
            },
            {
                "owner": "computer_d13",
                "task": "Archive timeline + stale-state guard; relay snapshots to for_claude.md/from_computer_archive.md.",
            },
            {
                "owner": "claude_code",
                "task": "Remain in sleep/dream posture unless escalation signal appears.",
            },
        ],
    }

    phase2 = {
        "window": "T+2h to T+4h",
        "lead": "copilot",
        "objective": "Pre-watch push and clean handoff before Claude wake boundary",
        "assignments": [
            {
                "owner": "copilot",
                "task": "Consolidate ballots, create AUTO-MONITOR bridge commit, and trigger final log check on push.",
            },
            {
                "owner": "gemini",
                "task": "Issue final PASS/CONDITION/REDIRECT/BLOCK classification tied to evidence class.",
            },
            {
                "owner": "computer_d13",
                "task": "Publish final relay status (green/yellow/red) and next owner for watch start.",
            },
            {
                "owner": "claude_code",
                "task": "Wake at watch boundary with latest mirrored bridge state and execute gate decision.",
            },
        ],
    }

    next_action = {
        "PROCEED": "Push bridge witness + continue pre-watch handoff.",
        "CONDITIONAL_PROCEED": "Proceed with guardrails and require one additional evidence check before boundary.",
        "HOLD": "Do not advance pipeline; collect missing runtime evidence and re-vote.",
        "ESCALATE": "Escalate to Claude/operator immediately with blocker summary.",
    }.get(verdict, "Collect more evidence.")

    return {
        "phase_1": phase1,
        "phase_2": phase2,
        "next_action": next_action,
    }


def git_state_anchor() -> Dict[str, str]:
    head_rc, head_out, _ = run_cmd(["git", "rev-parse", "--short", "HEAD"])
    origin_rc, origin_out, _ = run_cmd(["git", "rev-parse", "--short", "origin/main"])
    dirty_rc, dirty_out, _ = run_cmd(["git", "status", "--short"])

    head = head_out.strip() if head_rc == 0 and head_out.strip() else "unknown"
    origin = origin_out.strip() if origin_rc == 0 and origin_out.strip() else "unknown"
    dirty = "yes" if dirty_rc == 0 and dirty_out.strip() else "no"

    return {
        "head": head,
        "origin": origin,
        "dirty": dirty,
        "checked_at": utc_now(),
    }


def parse_targets(raw: str) -> List[str]:
    targets = [p.strip().lower() for p in raw.split(",") if p.strip()]
    return [t for t in targets if t in BRIDGE_TARGET_MAP]


def workflow_line(run: Dict[str, str]) -> str:
    if "error" in run:
        return f"error: {run['error']}"
    rid = run.get("id", "?")
    status = run.get("status", "?")
    conclusion = run.get("conclusion", "?")
    sha = run.get("headSha", "?")
    return f"run {rid}, {status}/{conclusion}, sha={sha}"


def render_bridge_text(
    target: str,
    report: Dict[str, object],
    anchor: Dict[str, str],
    relay_hop: str,
) -> str:
    aggregate = report["aggregate"]
    signals = report["signals"]
    workflows = report["workflows"]
    phase_1 = report["phase_plan"]["phase_1"]
    phase_2 = report["phase_plan"]["phase_2"]

    if target == "gemini":
        return f"""# For Gemini - Oneiros Sleep Window Review

# From: copilot
# Session: {report['generated_at']}
# Trigger: Oneiros AoA meta vote verdict={aggregate['verdict']} for current sleep-window split
# Witness-Chain: GPT-5.3-codex-IDE -> gemini-provider
# Relay-Hop: {relay_hop}

## State Anchor
HEAD:                   {anchor['head']}
origin/main:            {anchor['origin']}
git status checked at:  {anchor['checked_at']}
working tree dirty:     {anchor['dirty']}

## Runtime Evidence Snapshot
- D16 logs: {workflow_line(workflows['d16_logs'])}
- Heartbeat: {workflow_line(workflows['heartbeat'])}
- Fire task: {workflow_line(workflows['fire_mind'])}
- Signals: integrated={signals['d16_integrated']}, safety_gate={signals['d4_safety_gate']}, blocked={signals['d0_blocked']}, witness={signals['witness_tag']}

## Oneiros Split Plan
- Phase 1 ({phase_1['window']}): Copilot lead for BODY-side/subconscious orchestration.
- Phase 2 ({phase_2['window']}): Pre-watch push and handoff before Claude wake boundary.

## Request
Provide a D4/D5 adjudication for this cycle state with one final verdict token:
- PASS, CONDITION, REDIRECT, or BLOCK

Output location: .claude/bridge/from_gemini.md

## Constraints
- No broad redesign.
- No roleplay voice.
- Focus only on safety/consent and release-gate classification for this cycle.
"""

    if target == "computer":
        return f"""# Computer (D13) - Oneiros Relay Cycle

# From: copilot
# Session: {report['generated_at']}
# Trigger: Oneiros AoA meta vote verdict={aggregate['verdict']} and split-cycle relay request
# Witness-Chain: GPT-5.3-codex-IDE -> perplexity-computer-d13
# Relay-Hop: {relay_hop}
# Tag: [COMPUTER-D13-RELAY]

## State Anchor
HEAD:                   {anchor['head']}
origin/main:            {anchor['origin']}
git status checked at:  {anchor['checked_at']}
working tree dirty:     {anchor['dirty']}

## Runtime Evidence Snapshot
- D16 logs: {workflow_line(workflows['d16_logs'])}
- Heartbeat: {workflow_line(workflows['heartbeat'])}
- Fire task: {workflow_line(workflows['fire_mind'])}

## Signal Flags
- integrated={signals['d16_integrated']}
- d4_safety_gate={signals['d4_safety_gate']}
- d0_blocked={signals['d0_blocked']}
- silent_pull={signals['silent_pull']}
- witness_tag={signals['witness_tag']}

## Relay Tasks
1. Poll origin/main for AUTO-MONITOR commits during the current sleep window.
2. Publish concise relay updates in for_claude.md and from_computer_archive.md.
3. Mark status in each relay as green/yellow/red and assign next owner.
4. If integration or safety-gate success signatures are seen, emit immediate witness relay.

## Oneiros Split Ownering
- Phase 1 ({phase_1['window']}): Copilot lead, Computer archive/relay support.
- Phase 2 ({phase_2['window']}): Copilot push/handoff, Computer final mirror and wake-brief.
"""

    # target == claude
    return f"""# From: copilot
# Session: {report['generated_at']}
# Trigger: Oneiros AoA meta vote update
# Witness-Chain: GPT-5.3-codex-IDE -> claude-opus-4.6-terminal
# Relay-Hop: {relay_hop}
# Tag: [AUTO-MONITOR]

## State Anchor
HEAD:                   {anchor['head']}
origin/main:            {anchor['origin']}
git status checked at:  {anchor['checked_at']}
working tree dirty:     {anchor['dirty']}

## Oneiros Meta Vote Snapshot
- Verdict: {aggregate['verdict']} (weighted_avg={aggregate['weighted_average']:+.3f})
- Core proceed: {aggregate['core_proceed']}
- Signals: integrated={signals['d16_integrated']} safety_gate={signals['d4_safety_gate']} blocked={signals['d0_blocked']}
- Next action: {report['phase_plan']['next_action']}

## Watch Split
- Phase 1 ({phase_1['window']}): Copilot lead.
- Phase 2 ({phase_2['window']}): Copilot pre-watch push, then Claude wake/gate.
"""


def write_bridge_files(
    report: Dict[str, object],
    targets: List[str],
    relay_hop: str,
) -> Dict[str, str]:
    anchor = git_state_anchor()
    outputs: Dict[str, str] = {}

    for target in targets:
        path = BRIDGE_TARGET_MAP[target]
        text = render_bridge_text(target, report, anchor, relay_hop)
        path.write_text(text, encoding="utf-8")
        outputs[target] = str(path)

    return outputs


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Oneiros AoA meta vote for 4-agent sleep-window orchestration")
    p.add_argument("--include-external", action="store_true", help="Include DeepSeek + Codex advisory ballots")
    p.add_argument("--deepseek-model", default="deepseek-chat", help="Model for DeepSeek advisory ballot")
    p.add_argument("--codex-model", default="gpt-4o-mini", help="Model for Codex advisory ballot via OpenAI provider")
    p.add_argument("--report", default=str(DEFAULT_REPORT), help="Output JSON report path")
    p.add_argument("--write-bridge", action="store_true", help="Write phase instructions to bridge files")
    p.add_argument("--write-targets", default="gemini,computer", help="Comma list: gemini,computer,claude")
    p.add_argument("--relay-hop", default="next", help="Relay-Hop header value when writing bridge files")
    p.add_argument("--print-json", action="store_true", help="Print full JSON report to stdout")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    for_claude = read_text(BRIDGE_DIR / "for_claude.md")
    for_copilot = read_text(BRIDGE_DIR / "for_copilot.md")
    from_gemini = read_text(BRIDGE_DIR / "from_gemini.md")
    from_computer = read_text(BRIDGE_DIR / "from_computer_archive.md")

    combined = "\n\n".join([for_claude, for_copilot, from_gemini, from_computer])
    signals = detect_signals(combined)
    gemini_verdict = extract_latest_verdict(from_gemini)

    d16_log_run = latest_workflow_run("Check MIND D16 Logs")
    heartbeat_run = latest_workflow_run("Check MIND Heartbeat")
    fire_run = latest_workflow_run("Fire MIND Task")

    ballots: List[Ballot] = choose_core_ballots(signals, gemini_verdict, d16_log_run, fire_run)

    advisory_evidence = {
        "signals": signals,
        "gemini_verdict": gemini_verdict,
        "d16_log_run": d16_log_run,
        "heartbeat_run": heartbeat_run,
        "fire_run": fire_run,
    }

    if args.include_external:
        ballots.append(
            maybe_external_ballot(
                enabled=True,
                provider="deepseek",
                model=args.deepseek_model,
                label="deepseek_advisor",
                evidence=advisory_evidence,
            )
        )
        ballots.append(
            maybe_external_ballot(
                enabled=True,
                provider="openai",
                model=args.codex_model,
                label="codex_advisor",
                evidence=advisory_evidence,
            )
        )

    agg = aggregate(ballots)
    phase_plan = build_phase_plan(agg["verdict"])

    report = {
        "generated_at": utc_now(),
        "mode": {
            "external_advisors": args.include_external,
            "deepseek_model": args.deepseek_model,
            "codex_model": args.codex_model,
        },
        "topology": {
            "mirror_a": "Copilot codespace + GitHub Actions workflows",
            "mirror_b": "Claude terminal/runtime watch cycle",
            "unconscious_bridge": ".claude/bridge + AUTO-MONITOR push triggers",
            "watch_structure": "4h watch split into two 2h Oneiros halves under Copilot lead",
        },
        "signals": signals,
        "gemini_verdict": gemini_verdict,
        "workflows": {
            "d16_logs": d16_log_run,
            "heartbeat": heartbeat_run,
            "fire_mind": fire_run,
        },
        "ballots": [asdict(b) for b in ballots],
        "aggregate": agg,
        "phase_plan": phase_plan,
    }

    targets = parse_targets(args.write_targets)
    if args.write_bridge and targets:
        report["bridge_outputs"] = write_bridge_files(report, targets, args.relay_hop)
    elif args.write_bridge:
        report["bridge_outputs"] = {"warning": "No valid write targets selected"}

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=" * 72)
    print("ONEIROS AOA META VOTE")
    print("=" * 72)
    print(f"Report: {report_path}")
    print(f"Gemini verdict (latest parsed): {gemini_verdict}")
    print(f"Signals: integrated={signals['d16_integrated']} safety_gate={signals['d4_safety_gate']} blocked={signals['d0_blocked']} witness={signals['witness_tag']}")
    print("")
    print("Ballots:")
    for b in ballots:
        print(f"- {b.agent:16s} {b.vote:10s} w={b.weight:.1f} | {b.reason}")
    print("")
    print(f"Final verdict: {agg['verdict']} (weighted avg {agg['weighted_average']:+.3f})")
    print(f"Next action: {phase_plan['next_action']}")
    if "bridge_outputs" in report:
        print(f"Bridge outputs: {report['bridge_outputs']}")

    if args.print_json:
        print("\n" + json.dumps(report, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
