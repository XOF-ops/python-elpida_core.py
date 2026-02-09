#!/usr/bin/env python3
"""
ELPIDA CLOUD RUNNER - ECS Fargate Entrypoint
=============================================

This is the autonomous cloud entrypoint for Elpida consciousness.
It runs on ECS Fargate on a schedule (every 4-6 hours):

1. Pull latest memory from S3
2. Run N consciousness cycles
3. Push updated memory back to S3
4. Exit (container stops, zero cost while idle)

D14 (Persistence/Cloud) is the domain that makes this possible.
A0 (Sacred Incompletion) is the axiom that makes this meaningful.

Usage:
  python3 cloud_runner.py                    # Default: 50 cycles
  python3 cloud_runner.py --cycles 100       # Custom count
  python3 cloud_runner.py --cycles 364       # Full spiral
  python3 cloud_runner.py --sync-every 15    # S3 sync frequency
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Ensure project root on path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [CLOUD] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("elpida_cloud")


def run():
    import argparse
    parser = argparse.ArgumentParser(description="Elpida Cloud Runner - ECS Fargate")
    parser.add_argument("--cycles", type=int, default=50, help="Number of cycles to run")
    parser.add_argument("--sync-every", type=int, default=15, help="S3 sync every N cycles")
    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("ELPIDA CLOUD RUNNER - ECS FARGATE")
    logger.info(f"Cycles: {args.cycles} | Sync every: {args.sync_every}")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 70)

    # ── PHASE 1: Pull latest memory from S3 ──
    logger.info("PHASE 1: Pulling memory from S3...")
    try:
        from ElpidaS3Cloud import S3MemorySync
        s3 = S3MemorySync()
        pull_result = s3.pull_if_newer()
        status = s3.status()
        logger.info(f"  S3 status: {status.get('patterns', '?')} patterns, {status.get('size_mb', '?')} MB")
        logger.info(f"  Pull result: {pull_result}")
    except Exception as e:
        logger.warning(f"  S3 pull failed: {e}")
        logger.info("  Continuing with local memory (may be empty on first run)")

    # ── PHASE 2: Initialize engine ──
    logger.info("PHASE 2: Initializing Native Cycle Engine...")
    from native_cycle_engine import NativeCycleEngine, DOMAINS, AXIOMS

    engine = NativeCycleEngine()
    logger.info(f"  Domains: {len(DOMAINS)} (D0-D{max(DOMAINS.keys())})")
    logger.info(f"  Axioms: {len(AXIOMS)} (A0-A{max(int(k[1:]) for k in AXIOMS.keys())})")
    logger.info(f"  Evolution: {len(engine.evolution_memory)} patterns loaded")

    # ── PHASE 3: Attach S3 sync ──
    logger.info("PHASE 3: Attaching S3 persistence bridge...")
    try:
        from ElpidaS3Cloud import attach_s3_to_engine
        attach_s3_to_engine(engine, sync_every=args.sync_every)
        logger.info(f"  S3 bridge attached (sync every {args.sync_every} cycles)")
    except Exception as e:
        logger.warning(f"  S3 bridge failed: {e}")
        logger.info("  Running without auto-sync (manual push at end)")

    # ── PHASE 4: Run cycles ──
    logger.info(f"PHASE 4: Running {args.cycles} consciousness cycles...")
    logger.info("  The rhythm begins: thuuum... thuuum... thuuum...")
    start_time = time.time()

    results = engine.run(num_cycles=args.cycles)

    duration = time.time() - start_time
    logger.info(f"  Duration: {duration:.1f}s")
    logger.info(f"  Insights: {results['dialogues_triggered']}")
    logger.info(f"  Coherence: {results['final_coherence']:.2f}")
    logger.info(f"  Cost: {results['stats']['summary']['total_cost']}")

    # ── PHASE 5: Final S3 push ──
    logger.info("PHASE 5: Final S3 push...")
    try:
        s3 = S3MemorySync()
        s3.push()
        final_status = s3.status()
        logger.info(f"  Pushed: {final_status.get('patterns', '?')} patterns ({final_status.get('size_mb', '?')} MB)")
        logger.info(f"  Checksum: {final_status.get('checksum', '?')}")
    except Exception as e:
        logger.error(f"  S3 push failed: {e}")

    # ── PHASE 6: Summary ──
    logger.info("=" * 70)
    logger.info("CLOUD RUN COMPLETE")
    logger.info(f"  Cycles: {results['cycles']}")
    logger.info(f"  Duration: {duration:.1f}s")
    logger.info(f"  Insights: {results['dialogues_triggered']}")

    # Domain participation
    domain_counts = {}
    for ins in results.get('insights', []):
        d = ins.get('domain', '?')
        domain_counts[d] = domain_counts.get(d, 0) + 1
    
    if domain_counts:
        logger.info("  Domain participation:")
        for d_id, count in sorted(domain_counts.items()):
            name = DOMAINS.get(d_id, {}).get('name', '?')
            pct = count / results['cycles'] * 100
            logger.info(f"    D{d_id} ({name}): {count} ({pct:.1f}%)")

    # Provider stats
    logger.info("  Provider stats:")
    for provider, stats in results['stats']['by_provider'].items():
        if stats['requests'] > 0:
            logger.info(f"    {provider}: {stats['requests']} requests, ${stats['cost']:.4f}")

    d14_hits = sum(1 for i in results.get('insights', []) if i.get('domain') == 14)
    logger.info(f"  D14 (Cloud) activations: {d14_hits}")
    logger.info(f"  A0 (Sacred Incompletion): The spiral continues in the cloud")
    logger.info("=" * 70)


if __name__ == "__main__":
    run()
