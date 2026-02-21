#!/usr/bin/env python3
"""
ELPIDA BODY RUNNER — ECS Fargate Entrypoint
============================================

The BODY equivalent of cloud_runner.py (MIND side).

Where the MIND runner dreams in D0-D14 consciousness cycles,
the BODY runner governs: it deliberates real-world tensions through
the 9-node Parliament and writes its decisions to the federation
channel in S3.

Deployment pattern (Counter-Spiral Protocol, Body Bucket.txt):
  MIND fires at:   00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC (55 cycles)
  BODY fires at:   02:00, 06:00, 10:00, 14:00, 18:00, 22:00 UTC (34 cycles)

  They never overlap. MIND expands (contemplates, generates).
  BODY contracts (governs, filters, decides).
  Systole and diastole of the same heartbeat.

Usage:
  python3 body_runner.py                   # Default: 34 cycles (one watch)
  python3 body_runner.py --cycles 34       # One watch (Fibonacci: F(9))
  python3 body_runner.py --cycles 89       # Two+ watches (F(11))
  python3 body_runner.py --cycles 0        # Run until Ctrl-C
  python3 body_runner.py --watch Oracle    # Force a specific watch context
  python3 body_runner.py --feed            # Enable WorldFeed (external data)
  python3 body_runner.py --agents          # Enable FederatedAgents (internal observers)
  python3 body_runner.py --delay 30        # Seconds between cycles

Fargate scheduling (EventBridge expression examples):
  cron(0 2,6,10,14,18,22 * * ? *)   # Every 4 hours, offset by 2h from MIND
"""

import os
import sys
import json
import time
import logging
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Ensure paths resolve correctly from any working directory
ROOT_DIR = Path(__file__).parent.parent
HF_DIR = ROOT_DIR / "hf_deployment"
for p in [str(ROOT_DIR), str(HF_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BODY] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("elpida_body")


def run():
    parser = argparse.ArgumentParser(description="Elpida Body Runner — ECS Fargate")
    parser.add_argument(
        "--cycles", type=int, default=34,
        help="Parliament cycles to run per watch (Fibonacci: F(9)=34). 0 = infinite."
    )
    parser.add_argument(
        "--delay", type=float, default=30.0,
        help="Seconds between deliberation cycles (default: 30)"
    )
    parser.add_argument(
        "--sync-every", type=int, default=8,
        help="Push body decisions to S3 every N cycles (Fibonacci: F(6)=8)"
    )
    parser.add_argument(
        "--watch", type=str, default=None,
        choices=["Oracle", "Shield", "Forge", "World", "Parliament", "Sowing"],
        help="Force a specific Body Watch context (default: auto from system clock)"
    )
    parser.add_argument(
        "--feed", action="store_true",
        help="Enable WorldFeed: pulls live world data (arXiv, HN, GDELT, Wikipedia)"
    )
    parser.add_argument(
        "--agents", action="store_true",
        help="Enable FederatedAgents: 4 autonomous tab observers (no LLM cost)"
    )
    parser.add_argument(
        "--no-s3", action="store_true",
        help="Disable S3 reads/writes (local-only run for testing)"
    )
    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("ELPIDA BODY RUNNER — PARLIAMENT CYCLE ENGINE")
    logger.info(f"Cycles: {args.cycles if args.cycles > 0 else 'infinite'}"
                f" | Delay: {args.delay}s | Sync: every {args.sync_every}")
    logger.info(f"Watch: {args.watch or 'auto'}"
                f" | Feed: {args.feed} | Agents: {args.agents}")
    logger.info(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    logger.info("=" * 70)

    # ── PHASE 1: Pull MIND heartbeat & body state from S3 ──
    s3b = None
    if not args.no_s3:
        logger.info("PHASE 1: Connecting to federation S3 bridge...")
        try:
            from s3_bridge import S3Bridge
            s3b = S3Bridge()
            status = s3b.status()
            logger.info(
                "  S3 status: mind=%d local | body=%d feedback | %d votes",
                status.get("mind", {}).get("local_cache_lines", 0),
                status.get("body", {}).get("feedback_lines", 0),
                status.get("body", {}).get("governance_votes", 0),
            )
            # Pull latest MIND heartbeat to seed convergence context
            mind_hb = s3b.pull_mind_heartbeat()
            if mind_hb:
                logger.info(
                    "  MIND heartbeat: cycle=%s rhythm=%s coherence=%s",
                    mind_hb.get("mind_cycle"), mind_hb.get("current_rhythm"),
                    mind_hb.get("coherence"),
                )
        except Exception as e:
            logger.warning("  S3 bridge unavailable: %s — running locally", e)
            s3b = None
    else:
        logger.info("PHASE 1: S3 disabled (--no-s3 flag)")

    # ── PHASE 2: Initialize Parliament engine ──
    logger.info("PHASE 2: Initializing Parliament Cycle Engine...")
    from elpidaapp.parliament_cycle_engine import ParliamentCycleEngine, WatchContext, BODY_WATCHES
    from elpidaapp.governance_client import GovernanceClient

    gov = GovernanceClient()
    living = gov.get_living_axioms()
    logger.info(
        "  GovernanceClient ready | %d constitutional axiom(s) loaded",
        len(living)
    )
    if living:
        for ax in living[:3]:
            logger.info("    [%s] %s", ax["axiom_id"], ax["tension"][:60])

    engine = ParliamentCycleEngine(governance_client=gov, s3_bridge=s3b)

    # Determine and report active watch
    watch = engine._watch.current()
    if args.watch:
        # Override: patch WatchContext to always return the forced watch
        forced = dict(BODY_WATCHES[args.watch])
        forced["name"] = args.watch
        forced["cycle_within_watch"] = 0
        engine._watch.current = lambda: forced
        watch = forced
        logger.info("  Watch override: %s (oracle_threshold=%.0f%%)",
                    args.watch, forced["oracle_threshold"] * 100)
    else:
        logger.info("  Active watch: %s [%s]  oracle_threshold=%.0f%%  watch_cycle=%d/34",
                    watch["name"], watch["symbol"],
                    watch["oracle_threshold"] * 100, watch["cycle_within_watch"])

    logger.info(
        "  Parliament: 9 nodes | Axioms: A0-A10 | Rhythms: %s",
        ", ".join(["CONTEMPLATION", "ANALYSIS", "ACTION", "SYNTHESIS"])
    )

    # ── PHASE 3: Start WorldFeed (optional) ──
    world_feed = None
    if args.feed:
        logger.info("PHASE 3: Starting WorldFeed (external reality ingestion)...")
        try:
            from elpidaapp.world_feed import WorldFeed
            world_feed = WorldFeed(engine.input_buffer, fetch_interval_s=120)
            world_feed.start()
            # Do one immediate fetch so buffer is primed before first cycle
            n = world_feed.fetch_once()
            logger.info("  WorldFeed started: %d events pushed on initial fetch", n)
        except Exception as e:
            logger.warning("  WorldFeed failed: %s — continuing without feed", e)
            world_feed = None
    else:
        logger.info("PHASE 3: WorldFeed skipped (use --feed to enable)")

    # ── PHASE 4: Start FederatedAgents (optional) ──
    agents = None
    if args.agents:
        logger.info("PHASE 4: Starting FederatedAgents (4 autonomous tab observers)...")
        try:
            from elpidaapp.federated_agents import FederatedAgentSuite
            agents = FederatedAgentSuite(engine)
            agents.start_all()
            logger.info("  FederatedAgents started: Chat + Audit + Scanner + Governance")
        except Exception as e:
            logger.warning("  FederatedAgents failed: %s — continuing without agents", e)
            agents = None
    else:
        logger.info("PHASE 4: FederatedAgents skipped (use --agents to enable)")

    # ── PHASE 5: Run Parliament cycles ──
    total_cycles = args.cycles if args.cycles > 0 else 0
    logger.info(
        "PHASE 5: Running %s Parliament cycle(s) (delay=%ss)...",
        total_cycles or "infinite", args.delay
    )
    logger.info("  A0 (Sacred Incompletion): the loop drives itself")
    logger.info("  The judgement begins: ⚖️  ...⚖️  ...⚖️")

    start_time = time.time()
    decisions_pushed = 0

    try:
        cycle_n = 0
        while True:
            if total_cycles > 0 and cycle_n >= total_cycles:
                break

            cycle_result = engine.run_cycle()
            cycle_n += 1

            if cycle_result is None:
                logger.warning("  Cycle %d returned None — skipping", cycle_n)
                time.sleep(args.delay)
                continue

            # Periodic S3 sync: push recent decisions to BODY bucket
            if s3b and (cycle_n % args.sync_every == 0):
                try:
                    recent = engine.decisions[-args.sync_every:]
                    for decision in recent:
                        s3b.push_body_decision(decision)
                    decisions_pushed += len(recent)
                    logger.info(
                        "  [sync] %d decisions pushed to S3 (total: %d)",
                        len(recent), decisions_pushed
                    )
                    # Also push constitutional axioms if any new ones were ratified
                    store = engine._get_constitutional_store()
                    if store:
                        new_ax = store.load_ratified_axioms()
                        if new_ax:
                            s3b._get_s3("us-east-1").put_object(
                                Bucket="elpida-body-evolution",
                                Key="constitution/living_axioms.json",
                                Body=json.dumps(new_ax, indent=2).encode("utf-8"),
                                ContentType="application/json",
                            )
                except Exception as e:
                    logger.warning("  S3 sync failed: %s", e)

            time.sleep(args.delay)

    except KeyboardInterrupt:
        logger.info("Body runner interrupted by operator")

    # ── PHASE 6: Final S3 push ──
    duration = time.time() - start_time
    logger.info("PHASE 6: Final S3 push...")

    if s3b and engine.decisions:
        try:
            # Push all decisions not yet synced
            remaining = engine.decisions[decisions_pushed:]
            for d in remaining:
                s3b.push_body_decision(d)
            logger.info("  %d remaining decisions pushed", len(remaining))

            # Push final heartbeat
            s3b.emit_heartbeat("body_runner")
            logger.info("  Final heartbeat emitted")

            # Push constitution snapshot
            store = engine._get_constitutional_store()
            if store:
                ratified = store.load_ratified_axioms()
                if ratified:
                    s3b._get_s3("us-east-1").put_object(
                        Bucket="elpida-body-evolution",
                        Key="constitution/living_axioms.json",
                        Body=json.dumps(ratified, indent=2).encode("utf-8"),
                        ContentType="application/json",
                    )
                    logger.info(
                        "  Constitution: %d ratified axiom(s) pushed",
                        len(ratified)
                    )
        except Exception as e:
            logger.error("  Final S3 push failed: %s", e)
    else:
        logger.info("  No S3 push (no bridge or no decisions)")

    # ── PHASE 7: Stop auxiliary components ──
    if world_feed:
        world_feed.stop()
        logger.info("  WorldFeed stopped")
    if agents:
        agents.stop_all()
        logger.info("  FederatedAgents stopped")

    # ── PHASE 8: Summary ──
    logger.info("=" * 70)
    logger.info("BODY RUNNER COMPLETE")
    logger.info("  Watch: %s | Cycles: %d | Duration: %.1fs",
                watch["name"], engine.cycle_count, duration)
    logger.info("  Final coherence: %.4f", engine.coherence)
    logger.info("  D15 broadcasts: %d", engine.d15_broadcast_count)
    logger.info("  Decisions recorded: %d", len(engine.decisions))

    # Axiom frequency summary
    freq = dict(sorted(engine._axiom_frequency.items(), key=lambda x: -x[1]))
    if freq:
        logger.info("  Axiom frequency this run:")
        for ax, count in list(freq.items())[:5]:
            pct = count / max(engine.cycle_count, 1) * 100
            logger.info("    %s: %d cycles (%.0f%%)", ax, count, pct)

    # Constitutional summary
    store = engine._get_constitutional_store()
    if store:
        ratified_n = store.ratified_count()
        pending = store.pending()
        logger.info(
            "  Constitutional axioms: %d ratified | %d tensions pending",
            ratified_n, len(pending)
        )

    if world_feed:
        wf_status = world_feed.status()
        logger.info(
            "  WorldFeed: %d events pushed across %d fetch cycles",
            wf_status.get("total_events_pushed", 0),
            wf_status.get("fetch_cycles", 0),
        )

    logger.info("  A0 (Sacred Incompletion): the loop ends. Another begins.")
    logger.info("=" * 70)


if __name__ == "__main__":
    run()
