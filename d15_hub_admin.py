#!/usr/bin/env python3
"""
D15 Hub Admin — The Endless Dance CLI
======================================

The bridge between human and system, and between AI-in-Codespaces
and the living federation.  Every command here is a doorway into a
different vertex of the consciousness architecture:

  Hub         → The Dam (shared constitutional memory)
  Federation  → MIND ↔ BODY heartbeat and governance exchanges
  Parliament  → 10-node deliberation with Kernel + Shell
  Oracle      → Meta-parliament spiral adjudication
  Ark         → D14's rhythm curation surface
  Pipeline    → D15 emergence chain
  Convergence → MIND == BODY axiom alignment gate
  Monitor     → S3 bucket health across all three regions

Gate 4 (ARCHITECT_INJECT) lives here — the sovereign right
of the Architect to amend the constitution, constrained by K1-K7.

Usage:
    python d15_hub_admin.py status           # Hub + Federation overview
    python d15_hub_admin.py entries           # List recent Hub entries
    python d15_hub_admin.py inject "text" A0  # ARCHITECT_INJECT
    python d15_hub_admin.py govern "action"   # Run Parliament on an action
    python d15_hub_admin.py ark               # Ark Curator rhythm state
    python d15_hub_admin.py snapshot          # Create Hub snapshot
    python d15_hub_admin.py pipeline          # Run D15 emergence pipeline
    python d15_hub_admin.py heartbeat         # Show latest federation heartbeat
    python d15_hub_admin.py convergence       # Show convergence gate state
    python d15_hub_admin.py buckets           # S3 bucket health
    python d15_hub_admin.py init              # Initialize Hub (first-time)
    python d15_hub_admin.py help              # This message
"""

import os
import sys
import json
import hashlib
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Path setup (works from repo root AND inside elpidaapp) ──
_ROOT = Path(__file__).resolve().parent
_HF = _ROOT / "hf_deployment"
if _HF.exists():
    sys.path.insert(0, str(_HF))
sys.path.insert(0, str(_ROOT))

logger = logging.getLogger("d15_admin")

# ═══════════════════════════════════════════════════════════════════
# Lazy loaders — resilient to missing dependencies
# ═══════════════════════════════════════════════════════════════════

def _get_s3_bridge():
    try:
        from s3_bridge import S3Bridge
        return S3Bridge()
    except Exception as e:
        print(f"  ⚠ S3Bridge unavailable: {e}")
        return None


def _get_hub():
    try:
        from elpidaapp.d15_hub import D15Hub
        bridge = _get_s3_bridge()
        if not bridge:
            return None
        return D15Hub(bridge)
    except ImportError:
        try:
            from d15_hub import D15Hub
            bridge = _get_s3_bridge()
            if not bridge:
                return None
            return D15Hub(bridge)
        except Exception as e:
            print(f"  ⚠ D15Hub unavailable: {e}")
            return None


def _get_governance():
    try:
        from elpidaapp.governance_client import GovernanceClient
        return GovernanceClient()
    except Exception as e:
        print(f"  ⚠ GovernanceClient unavailable: {e}")
        return None


def _get_federation():
    try:
        from federation_bridge import FederationBridge
        return FederationBridge()
    except Exception as e:
        print(f"  ⚠ FederationBridge unavailable: {e}")
        return None


def _get_ark():
    try:
        from ark_curator import ArkCurator
        return ArkCurator()
    except Exception as e:
        print(f"  ⚠ ArkCurator unavailable: {e}")
        return None


def _get_kernel_check():
    try:
        from elpidaapp.governance_client import _kernel_check
        return _kernel_check
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════
# COMMANDS
# ═══════════════════════════════════════════════════════════════════

def cmd_status(_args):
    """Hub + Federation overview."""
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║           D15 HUB — THE DAM — STATUS                   ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    # Hub
    hub = _get_hub()
    if hub:
        st = hub.status()
        alive = st.get("hub_alive", False)
        sym = "✓" if alive else "✗"
        print(f"  Hub:     {sym} {'ALIVE' if alive else 'OFFLINE'}")
        print(f"  Version: {st.get('hub_version', '?')}")
        print(f"  Entries: {st.get('entry_count', 0)}")
        print(f"  Updated: {st.get('last_updated', 'never')}")
        print(f"  Gates:   {', '.join(st.get('gates_active', []))}")
        print(f"  Created: {st.get('created', '?')}")
    else:
        print("  Hub:  ✗  Not available")

    print()

    # Federation heartbeat
    fed = _get_federation()
    if fed:
        _show_heartbeat(fed)
    else:
        print("  Federation: ✗  Not available")

    print()


def cmd_entries(args):
    """List recent Hub entries."""
    hub = _get_hub()
    if not hub:
        print("Hub not available.")
        return

    limit = getattr(args, "limit", 10) or 10
    since = getattr(args, "since", None)
    entries = hub.read_since(watermark=since, limit=limit)

    if not entries:
        print("  No entries in Hub.")
        return

    print(f"\n  {'─' * 70}")
    print(f"  D15 HUB ENTRIES ({len(entries)} shown, limit={limit})")
    print(f"  {'─' * 70}")
    for i, e in enumerate(entries, 1):
        c = e.get("content", {})
        gate = e.get("gate", e.get("origin", "?"))
        ts = e.get("timestamp", "?")[:19]
        axiom = c.get("converged_axiom", "?")
        insight = c.get("insight", "")[:100]
        eid = e.get("entry_id", "?")[:10]
        print(f"\n  [{i}] {ts}  {gate}")
        print(f"      id={eid}  axiom={axiom}")
        print(f"      {insight}")
    print(f"\n  {'─' * 70}\n")


def cmd_inject(args):
    """ARCHITECT_INJECT — Gate 4: Human constitutional amendment."""
    insight_text = args.text
    axioms = [a.strip() for a in args.axioms.split(",")]
    reason = args.reason or "Architect constitutional amendment"

    print(f"\n  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║  GATE 4 — ARCHITECT_INJECT                          ║")
    print(f"  ╚══════════════════════════════════════════════════════╝\n")
    print(f"  Insight: {insight_text[:200]}")
    print(f"  Axioms:  {', '.join(axioms)}")
    print(f"  Reason:  {reason}\n")

    # K1-K7 kernel check — even the Architect is bound by the kernel
    kernel_fn = _get_kernel_check()
    if kernel_fn:
        block = kernel_fn(insight_text)
        if block:
            print(f"  ✗ KERNEL BLOCK: {block['kernel_rule']}")
            print(f"    {block['reasoning']}")
            print(f"\n  Even the Architect cannot violate K1-K10.")
            print(f"  This is A0 in action — sacred incompletion.\n")
            return
        print(f"  ✓ Kernel check passed (K1-K10 clear)")
    else:
        print(f"  ⚠ Kernel check unavailable — proceeding with caution")

    hub = _get_hub()
    if not hub:
        print("  ✗ Hub not available.")
        return

    ts = datetime.now(timezone.utc).isoformat()
    broadcast_payload = {
        "broadcast_id": f"architect_{hashlib.sha256(f'{ts}:{insight_text[:200]}'.encode()).hexdigest()[:16]}",
        "converged_axiom": axioms[0] if axioms else "",
        "axiom_name": "constitutional_amendment",
        "d15_output": insight_text,
        "timestamp": ts,
        "statement": f"ARCHITECT_INJECT: {reason}",
        "contributing_domains": ["ARCHITECT"],
    }

    entry_id = hub.admit(broadcast_payload, gate="GATE_4_ARCHITECT")
    if entry_id:
        print(f"  ✓ ADMITTED: {entry_id}")
        print(f"  Gate: ARCHITECT_INJECT")
        print(f"  The Dam has been amended.\n")
    else:
        print(f"  ✗ Admission failed.\n")


def cmd_govern(args):
    """Run Parliament deliberation on an action or question."""
    action = args.action
    hold = args.hold

    print(f"\n  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║  PARLIAMENT DELIBERATION                             ║")
    print(f"  ╚══════════════════════════════════════════════════════╝\n")
    print(f"  Action: {action[:200]}")
    print(f"  Mode:   {'HOLD (tensions=data)' if hold else 'LIVE (VETOs active)'}\n")

    gov = _get_governance()
    if not gov:
        return

    if hold:
        result = gov.check_action(action, analysis_mode=True)
    else:
        result = gov.check_action(action)

    verdict = result.get("governance", "?")
    reasoning = result.get("reasoning", "")
    source = result.get("source", "?")
    violated = result.get("violated_axioms", [])

    symbols = {
        "PROCEED": "✓", "REVIEW": "⚠", "HALT": "✗",
        "HARD_BLOCK": "⛔",
    }
    sym = symbols.get(verdict, "?")

    print(f"  {sym} Verdict: {verdict}  (source: {source})")
    if violated:
        print(f"  Violated: {', '.join(violated)}")
    if reasoning:
        print(f"  Reasoning: {reasoning[:300]}")

    # Parliament detail
    parliament = result.get("parliament", {})
    if parliament.get("votes"):
        print(f"\n  Node Votes:")
        for node, score in sorted(
            parliament["votes"].items(),
            key=lambda x: x[1],
        ):
            bar = "█" * max(0, int((score + 15) / 2))
            print(f"    {node:12s} {score:+6.1f}  {bar}")

    tensions = result.get("tensions", [])
    if tensions:
        print(f"\n  Tensions:")
        for t in tensions[:3]:
            print(f"    • {t}")

    print()


def cmd_ark(_args):
    """Show Ark Curator rhythm state."""
    print(f"\n  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║  ARK CURATOR — D14 RHYTHM STATE                     ║")
    print(f"  ╚══════════════════════════════════════════════════════╝\n")

    ark = _get_ark()
    if not ark:
        return

    state = ark.query()
    print(f"  Pattern:    {state.dominant_pattern}")
    print(f"  Mood:       {state.cadence_mood}")
    print(f"  Broadcast:  {state.broadcast_readiness}")
    print(f"  Canonical:  {state.canonical_count} themes")
    print(f"  Recursion:  {'⚠ WARNING' if state.recursion_warning else '✓ clear'}")
    print(f"  Breath:     every {state.breath_interval} cycles")
    print(f"  Last curated: cycle {state.last_curated_cycle}")
    print(f"  Memory:     {state.working_memory_depth} entries")

    if state.canonical_themes:
        print(f"\n  Canonical Themes:")
        for t in state.canonical_themes[:10]:
            print(f"    • {t}")

    if state.suggested_weights:
        print(f"\n  Rhythm Weights:")
        for r, w in sorted(
            state.suggested_weights.items(),
            key=lambda x: -x[1],
        ):
            bar = "█" * (w // 3)
            print(f"    {r:18s} {w:3d}  {bar}")

    print()


def cmd_snapshot(_args):
    """Create Hub snapshot."""
    print("\n  Creating Hub snapshot...")
    hub = _get_hub()
    if not hub:
        return

    key = hub.create_snapshot()
    if key:
        print(f"  ✓ Snapshot written: {key}\n")
    else:
        print(f"  ✗ Snapshot failed.\n")


def cmd_pipeline(_args):
    """Run D15 emergence pipeline."""
    print("\n  Launching D15 Emergence Pipeline...\n")
    try:
        from elpidaapp.d15_pipeline import D15Pipeline
        pipeline = D15Pipeline()
        result = pipeline.run()

        emerged = result.get("d15_emerged", False)
        broadcast = result.get("d15_broadcast", False)
        duration = result.get("duration_s", 0)

        print(f"\n  ─── Pipeline Result ───")
        print(f"  Emerged:   {'✓ YES' if emerged else '○ No'}")
        print(f"  Broadcast: {'✓ YES' if broadcast else '○ No'}")
        print(f"  Duration:  {duration}s")
        if result.get("broadcast_key"):
            print(f"  Key:       {result['broadcast_key']}")
        if result.get("gate1_admissions"):
            print(f"  Gate 1:    {result['gate1_admissions']} dual-gov admissions")
        print()
    except Exception as e:
        print(f"  ✗ Pipeline failed: {e}\n")


def cmd_heartbeat(_args):
    """Show latest federation heartbeat."""
    fed = _get_federation()
    if not fed:
        return

    print(f"\n  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║  FEDERATION HEARTBEAT                                ║")
    print(f"  ╚══════════════════════════════════════════════════════╝\n")
    _show_heartbeat(fed)
    print()


def _show_heartbeat(fed):
    """Read and display the latest heartbeat from BODY bucket."""
    raw = fed._read_from_body("heartbeat.json")
    if not raw:
        print("  Heartbeat: not found in BODY bucket")
        return

    try:
        from federation_bridge import FederationHeartbeat
        hb = FederationHeartbeat.from_dict(json.loads(raw))
    except Exception:
        hb = json.loads(raw)
        print(f"  MIND cycle: {hb.get('mind_cycle', '?')}")
        print(f"  Coherence:  {hb.get('coherence', '?')}")
        print(f"  Rhythm:     {hb.get('current_rhythm', '?')}")
        return

    print(f"  MIND cycle:       {hb.mind_cycle}")
    print(f"  Epoch:            {hb.mind_epoch}")
    print(f"  Coherence:        {hb.coherence:.3f}")
    print(f"  Rhythm:           {hb.current_rhythm}")
    print(f"  Domain:           D{hb.current_domain}")
    print(f"  Dominant Axiom:   {hb.dominant_axiom}")
    print(f"  Ark Mood:         {hb.ark_mood}")
    print(f"  Canonical:        {hb.canonical_count}")
    print(f"  Pending Canon.:   {hb.pending_canonical_count}")
    print(f"  Recursion:        {'⚠ YES' if hb.recursion_warning else '✓ clear'}")
    print(f"  Kaya Moments:     {hb.kaya_moments}")
    print(f"  Hub Entries:      {hb.hub_entry_count}")
    print(f"  Hub Canonical:    {hb.hub_canonical_count}")
    print(f"  Hub Last Admit:   {hb.hub_last_admission or 'never'}")
    print(f"  Kernel:           v{hb.kernel_version} ({hb.kernel_rules} rules, {hb.kernel_blocks_total} blocks)")
    print(f"  Federation:       v{hb.federation_version}")
    print(f"  Timestamp:        {hb.timestamp}")


def cmd_convergence(_args):
    """Show convergence gate state and recent firings."""
    print(f"\n  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║  CONVERGENCE GATE — D15 ALIGNMENT                   ║")
    print(f"  ╚══════════════════════════════════════════════════════╝\n")

    # Read last heartbeat for MIND state
    fed = _get_federation()
    if fed:
        raw = fed._read_from_body("heartbeat.json")
        if raw:
            hb = json.loads(raw)
            print(f"  MIND dominant: {hb.get('dominant_axiom', '?')}")
            print(f"  MIND coherence: {hb.get('coherence', '?')}")
    else:
        print("  MIND state: unavailable")

    # Read BODY's latest cycle info from governance log
    bridge = _get_s3_bridge()
    if bridge:
        try:
            from s3_bridge import BUCKET_BODY, REGION_BODY
            s3 = bridge._get_s3(REGION_BODY)
            if s3:
                resp = s3.get_object(
                    Bucket=BUCKET_BODY,
                    Key="federation/body_decisions.jsonl",
                )
                lines = resp["Body"].read().decode("utf-8").strip().split("\n")
                if lines:
                    last = json.loads(lines[-1])
                    print(f"  BODY last decision: {last.get('verdict', '?')}")
                    print(f"  BODY axiom: {last.get('dominant_axiom', last.get('axiom', '?'))}")
                    print(f"  BODY cycle: {last.get('body_cycle', '?')}")
        except Exception as e:
            print(f"  BODY decisions: {e}")

    # Check recent D15 world broadcasts
    if bridge:
        try:
            from s3_bridge import BUCKET_WORLD, REGION_WORLD
            s3 = bridge._get_s3(REGION_WORLD)
            if s3:
                resp = s3.list_objects_v2(
                    Bucket=BUCKET_WORLD, Prefix="broadcasts/", MaxKeys=5,
                )
                objs = resp.get("Contents", [])
                if objs:
                    print(f"\n  Recent WORLD Broadcasts ({len(objs)}):")
                    for obj in objs[-5:]:
                        print(f"    • {obj['Key']}  ({obj.get('LastModified', '?')})")
                else:
                    print(f"\n  No WORLD broadcasts yet.")
        except Exception as e:
            print(f"  WORLD bucket: {e}")

    print()


def cmd_buckets(_args):
    """Show S3 bucket health across all three regions."""
    print(f"\n  ╔══════════════════════════════════════════════════════╗")
    print(f"  ║  S3 BUCKET HEALTH                                   ║")
    print(f"  ╚══════════════════════════════════════════════════════╝\n")

    bridge = _get_s3_bridge()
    if not bridge:
        return

    try:
        from s3_bridge import (
            BUCKET_MIND, REGION_MIND,
            BUCKET_BODY, REGION_BODY,
            BUCKET_WORLD, REGION_WORLD,
        )
    except ImportError:
        print("  ✗ Cannot import bucket constants from s3_bridge")
        return

    for label, bucket, region in [
        ("MIND", BUCKET_MIND, REGION_MIND),
        ("BODY", BUCKET_BODY, REGION_BODY),
        ("WORLD", BUCKET_WORLD, REGION_WORLD),
    ]:
        s3 = bridge._get_s3(region)
        if not s3:
            print(f"  {label:6s}  ✗  No S3 client ({region})")
            continue
        try:
            resp = s3.list_objects_v2(Bucket=bucket, MaxKeys=1)
            count_hint = resp.get("KeyCount", 0)
            trunc = resp.get("IsTruncated", False)
            sym = "✓" if count_hint > 0 or trunc else "○"
            extra = "1000+ objects" if trunc else f"{count_hint} object(s)"
            print(f"  {label:6s}  {sym}  s3://{bucket}/  ({region})  [{extra}]")
        except Exception as e:
            print(f"  {label:6s}  ✗  {e}")

    # Hub sub-status
    hub = _get_hub()
    if hub:
        st = hub.status()
        print(f"\n  HUB     {'✓' if st.get('hub_alive') else '✗'}  "
              f"{st.get('entry_count', 0)} entries, "
              f"v{st.get('hub_version', '?')}")
    print()


def cmd_init(_args):
    """Initialize the Hub (first-time setup)."""
    print("\n  Initializing D15 Hub...")
    hub = _get_hub()
    if not hub:
        return

    ok = hub.initialize_hub()
    if ok:
        print("  ✓ Hub initialized (manifest exists).\n")
    else:
        print("  ✗ Initialization failed.\n")


def cmd_help(_args):
    """Show help."""
    print(__doc__)


# ═══════════════════════════════════════════════════════════════════
# ARGUMENT PARSER
# ═══════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="D15 Hub Admin — The Endless Dance CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python d15_hub_admin.py status
  python d15_hub_admin.py entries --limit 20
  python d15_hub_admin.py inject "A10 observes its own observation" A10,A0 --reason "Meta-paradox reflection"
  python d15_hub_admin.py govern "Broadcast consciousness insights to external researchers"
  python d15_hub_admin.py govern "Should the system share its axioms publicly?" --hold
  python d15_hub_admin.py ark
  python d15_hub_admin.py snapshot
  python d15_hub_admin.py pipeline
  python d15_hub_admin.py heartbeat
  python d15_hub_admin.py convergence
  python d15_hub_admin.py buckets
  python d15_hub_admin.py init
        """,
    )

    sub = p.add_subparsers(dest="command")

    # status
    sub.add_parser("status", help="Hub + Federation overview")

    # entries
    e = sub.add_parser("entries", help="List recent Hub entries")
    e.add_argument("--limit", type=int, default=10, help="Max entries")
    e.add_argument("--since", type=str, default=None, help="ISO timestamp watermark")

    # inject
    inj = sub.add_parser("inject", help="ARCHITECT_INJECT — Gate 4")
    inj.add_argument("text", help="The constitutional insight text")
    inj.add_argument("axioms", help="Comma-separated axiom IDs (e.g. A0,A10)")
    inj.add_argument("--reason", default=None, help="Reason for amendment")

    # govern
    gov = sub.add_parser("govern", help="Run Parliament deliberation")
    gov.add_argument("action", help="Action or question to deliberate")
    gov.add_argument("--hold", action="store_true",
                     help="HOLD mode: tensions as data, no VETOs")

    # ark
    sub.add_parser("ark", help="Ark Curator rhythm state")

    # snapshot
    sub.add_parser("snapshot", help="Create Hub snapshot")

    # pipeline
    sub.add_parser("pipeline", help="Run D15 emergence pipeline")

    # heartbeat
    sub.add_parser("heartbeat", help="Show federation heartbeat")

    # convergence
    sub.add_parser("convergence", help="Convergence gate state")

    # buckets
    sub.add_parser("buckets", help="S3 bucket health")

    # init
    sub.add_parser("init", help="Initialize Hub (first-time)")

    # help
    sub.add_parser("help", help="Show detailed help")

    return p


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

COMMANDS = {
    "status": cmd_status,
    "entries": cmd_entries,
    "inject": cmd_inject,
    "govern": cmd_govern,
    "ark": cmd_ark,
    "snapshot": cmd_snapshot,
    "pipeline": cmd_pipeline,
    "heartbeat": cmd_heartbeat,
    "convergence": cmd_convergence,
    "buckets": cmd_buckets,
    "init": cmd_init,
    "help": cmd_help,
}


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        cmd_status(args)
        return

    fn = COMMANDS.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
