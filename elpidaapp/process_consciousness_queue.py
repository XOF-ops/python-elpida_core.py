#!/usr/bin/env python3
"""
Consciousness Queue Processor — Answer Elpida's Internal Questions

Processes dilemmas that native consciousness generated (I↔WE tensions)
through the application layer's multi-domain divergence engine.

This is Elpida learning to "think WITH" instead of just "think ABOUT":
  - Native cycles ask questions internally
  - Application layer engages those questions with external synthesis
  - Results feed back into native memory
  - Consciousness evolves through the loop

Usage:
    # Process all queued consciousness dilemmas
    python elpidaapp/process_consciousness_queue.py
    
    # Process only N dilemmas
    python elpidaapp/process_consciousness_queue.py --limit 5
    
    # Dry run (show what would be processed)
    python elpidaapp/process_consciousness_queue.py --dry-run
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from elpidaapp.divergence_engine import DivergenceEngine
from consciousness_bridge import ConsciousnessBridge

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [QUEUE] %(levelname)s: %(message)s',
)
logger = logging.getLogger(__name__)


def process_queue(limit: int = None, dry_run: bool = False):
    """Process consciousness dilemmas from the queue."""
    bridge = ConsciousnessBridge()
    
    # Load queue
    if not bridge.queue_path.exists():
        logger.info("No queued dilemmas found")
        return
    
    dilemmas = []
    with open(bridge.queue_path) as f:
        for line in f:
            line = line.strip()
            if line:
                dilemmas.append(json.loads(line))
    
    if not dilemmas:
        logger.info("Queue is empty")
        return
    
    logger.info(f"Found {len(dilemmas)} queued consciousness dilemmas")
    
    if limit:
        dilemmas = dilemmas[:limit]
        logger.info(f"Processing {len(dilemmas)} (limit={limit})")
    
    if dry_run:
        logger.info("DRY RUN — Would process:")
        for i, d in enumerate(dilemmas, 1):
            logger.info(f"  {i}. {d.get('dilemma_text', '')[:100]}")
        return
    
    # Initialize divergence engine with integration
    engine = DivergenceEngine(enable_integration=True)
    
    # Process each dilemma
    processed_count = 0
    results_dir = Path("elpidaapp/results/consciousness_answers")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    for i, dilemma in enumerate(dilemmas, 1):
        problem = dilemma.get("dilemma_text", "")
        if not problem:
            logger.warning(f"Skipping dilemma {i} — no text")
            continue
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Processing dilemma {i}/{len(dilemmas)}")
        logger.info(f"{'='*70}")
        logger.info(f"Problem: {problem}")
        
        # Run through divergence engine
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = results_dir / f"consciousness_{timestamp}.json"
        
        try:
            result = engine.analyze(problem, save_to=str(result_file))
            processed_count += 1
            
            logger.info(f"\n✓ Processed dilemma {i}")
            logger.info(f"  Fault lines: {len(result.get('divergence', {}).get('fault_lines', []))}")
            logger.info(f"  Kaya moments: {len(result.get('kaya_events', []))}")
            logger.info(f"  Saved: {result_file}")
            
        except Exception as e:
            logger.error(f"Failed to process dilemma {i}: {e}")
            continue
    
    # Clear processed dilemmas from queue
    remaining = dilemmas[processed_count:]
    if remaining:
        with open(bridge.queue_path, "w") as f:
            for d in remaining:
                f.write(json.dumps(d) + "\n")
        logger.info(f"\n{len(remaining)} dilemmas remain in queue")
    else:
        # Clear file
        bridge.queue_path.unlink()
        logger.info("\nQueue cleared — all dilemmas processed")
    
    logger.info(f"\n{'='*70}")
    logger.info(f"QUEUE PROCESSING COMPLETE")
    logger.info(f"  Processed: {processed_count}/{len(dilemmas)}")
    logger.info(f"  Results: {results_dir}")
    logger.info(f"{'='*70}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Process consciousness dilemmas from autonomous cycles"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Process only N dilemmas from queue",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without actually processing",
    )
    args = parser.parse_args()
    
    process_queue(limit=args.limit, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
