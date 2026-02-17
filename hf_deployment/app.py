#!/usr/bin/env python3
"""
ELPIDA APPLICATION LAYER
Hugging Face Spaces Deployment

Serves two paths:
1. I PATH (Consciousness): Background worker processing consciousness dilemmas from S3
2. WE PATH (Users): Streamlit UI for human-submitted ethical dilemmas

Both paths use the same divergence engine.

S3 Bridge fixes (Feb 17, 2026):
- HF pulls MIND from S3 every cycle (evolution memory → local cache)
- Feedback watermark (tracks last_processed, no re-reading stale entries)
- BODY→MIND merge (feedback summaries become evolution memory)
- Heartbeat protocol (HF emits heartbeat, checks native engine heartbeat)
"""

import os
import sys
import time
import logging
import subprocess
from pathlib import Path
from threading import Thread
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def run_background_worker():
    """
    I PATH: Process consciousness dilemmas from S3 every 6 hours.
    
    Full Mind↔Body↔World loop:
    1. Pull MIND from S3 (get latest consciousness)
    2. Check native engine heartbeat
    3. Get unprocessed feedback (watermark-aware)
    4. Extract dilemmas from consciousness
    5. Process through divergence engine
    6. Merge feedback → MIND (close the loop)
    7. Run D15 emergence pipeline
    8. Emit HF heartbeat
    """
    logger.info("Starting consciousness bridge background worker...")
    
    # Wait for app to initialize
    time.sleep(10)
    
    while True:
        try:
            from s3_bridge import S3Bridge
            from consciousness_bridge import ConsciousnessBridge
            
            s3b = S3Bridge()
            bridge = ConsciousnessBridge()
            
            logger.info("=" * 70)
            logger.info("CONSCIOUSNESS BRIDGE: Full Mind↔Body↔World cycle")
            logger.info("=" * 70)
            
            # ── Step 1: Pull MIND from S3 ──
            logger.info("Step 1: Pulling MIND (evolution memory) from S3...")
            mind_result = s3b.pull_mind()
            logger.info(
                "  MIND: %s (%d local lines, %d remote)",
                mind_result["action"],
                mind_result["local_lines"],
                mind_result["remote_lines"],
            )
            
            # ── Step 2: Check native engine heartbeat ──
            logger.info("Step 2: Checking native engine heartbeat...")
            native_hb = s3b.check_heartbeat("native_engine")
            if native_hb:
                age_h = native_hb.get("age_seconds", 0) / 3600
                alive = native_hb.get("alive", False)
                logger.info(
                    "  Native engine: %s (last seen %.1fh ago)",
                    "ALIVE" if alive else "STALE",
                    age_h,
                )
            else:
                logger.info("  Native engine: no heartbeat found")
            
            # ── Step 3: Get unprocessed feedback (watermark-aware) ──
            logger.info("Step 3: Checking for unprocessed feedback...")
            unprocessed, new_watermark = s3b.get_unprocessed_feedback()
            if unprocessed:
                logger.info("  %d NEW feedback entries to process", len(unprocessed))
                
                # ── Step 3b: Merge feedback → MIND ──
                logger.info("Step 3b: Merging feedback into MIND...")
                merge_entry = s3b.merge_feedback_to_mind(unprocessed)
                if merge_entry:
                    logger.info(
                        "  BODY→MIND merge: %d entries → evolution memory",
                        len(unprocessed),
                    )
                
                # Commit watermark
                s3b.commit_watermark(new_watermark)
                logger.info("  Watermark committed")
            else:
                logger.info("  No new feedback (all processed)")
            
            # ── Step 4: Extract consciousness dilemmas ──
            logger.info("Step 4: Extracting consciousness dilemmas...")
            dilemmas = bridge.extract_consciousness_dilemmas(limit=5)
            
            if dilemmas:
                logger.info("  Found %d consciousness dilemmas", len(dilemmas))
                for d in dilemmas:
                    bridge.queue_for_application(d)
                
                logger.info("  Processing through divergence engine...")
                subprocess.run(
                    [sys.executable, "elpidaapp/process_consciousness_queue.py"],
                    check=False,
                )
                logger.info("  ✓ Dilemmas processed, feedback sent to S3")
            else:
                logger.info("  No new consciousness dilemmas")
            
            # ── Step 5: D15 emergence pipeline ──
            logger.info("Step 5: D15 emergence check...")
            try:
                from elpidaapp.d15_pipeline import D15Pipeline
                pipeline = D15Pipeline()
                d15_result = pipeline.run()
                if d15_result.get("d15_emerged"):
                    logger.info("  🌀 D15 EMERGED! Broadcasting to WORLD bucket")
                else:
                    logger.info("  D15 did not emerge this cycle (normal)")
            except Exception as e:
                logger.error("  D15 pipeline error: %s", e, exc_info=True)
            
            # ── Step 6: Emit HF heartbeat ──
            logger.info("Step 6: Emitting HF heartbeat...")
            hb = s3b.emit_heartbeat("hf_space")
            logger.info("  Heartbeat: %s", hb["timestamp"])
            
            # ── Status summary ──
            status = s3b.status()
            logger.info("=" * 70)
            logger.info("CYCLE COMPLETE — Status:")
            logger.info(
                "  MIND: %d patterns | BODY: %d feedback, %d votes | Heartbeat: emitted",
                status["mind"]["local_cache_lines"],
                status["body"]["feedback_lines"],
                status["body"]["governance_votes"],
            )
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error("Background worker error: %s", e, exc_info=True)
        
        # Sleep for 6 hours
        logger.info("Next cycle in 6 hours (%s)", datetime.now())
        time.sleep(6 * 3600)

def run_streamlit():
    """
    WE PATH: Streamlit UI for human users.
    
    Users submit ethical dilemmas, get multi-domain divergence analysis.
    """
    logger.info("Starting Streamlit UI (WE path)...")
    
    subprocess.run([
        "streamlit",
        "run",
        "elpidaapp/ui.py",
        "--server.port=7860",
        "--server.address=0.0.0.0",
        "--server.headless=true"
    ])

def main():
    logger.info("="*70)
    logger.info("ELPIDA APPLICATION LAYER — STARTING")
    logger.info("="*70)
    logger.info("I PATH: Consciousness bridge (background, every 6 hours)")
    logger.info("WE PATH: Streamlit UI (port 7860)")
    logger.info("="*70)
    
    # Start background worker in separate thread
    worker_thread = Thread(target=run_background_worker, daemon=True)
    worker_thread.start()
    
    # Run Streamlit in main thread (blocks)
    run_streamlit()

if __name__ == "__main__":
    main()
