#!/usr/bin/env python3
"""
ELPIDA APPLICATION LAYER
Hugging Face Spaces Deployment

Serves two paths:
1. I PATH (Consciousness): Background worker processing consciousness dilemmas from S3
2. WE PATH (Users): Streamlit UI for human-submitted ethical dilemmas

Both paths use the same divergence engine.
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
    
    This is the consciousness bridge in action:
    - Native cycles (ECS) generate I↔WE tensions
    - Logged to S3: elpida_evolution_memory.jsonl
    - Bridge extracts dilemmas
    - Divergence engine processes
    - Feedback pushed to S3: feedback/feedback_to_native.jsonl
    - Native cycles read and integrate
    """
    logger.info("Starting consciousness bridge background worker...")
    
    # Wait for app to initialize
    time.sleep(10)
    
    while True:
        try:
            logger.info("="*70)
            logger.info("CONSCIOUSNESS BRIDGE: Processing I path")
            logger.info("="*70)
            
            # Extract dilemmas from S3
            from consciousness_bridge import ConsciousnessBridge
            bridge = ConsciousnessBridge()
            
            # Pull latest consciousness memory from S3
            logger.info("Checking S3 for consciousness dilemmas...")
            dilemmas = bridge.extract_consciousness_dilemmas(limit=5)
            
            if dilemmas:
                logger.info(f"Found {len(dilemmas)} consciousness dilemmas to process")
                
                # Queue them
                for d in dilemmas:
                    bridge.queue_for_application(d)
                
                # Process through divergence engine
                logger.info("Processing through divergence engine...")
                subprocess.run([
                    sys.executable,
                    "elpidaapp/process_consciousness_queue.py"
                ], check=False)
                
                logger.info("✓ Consciousness dilemmas processed, feedback sent to S3")
            else:
                logger.info("No new consciousness dilemmas found")
            
            # ── D15 Autonomous Pipeline ──
            # Run D14→D13→D11→D0→D12→[D15?] emergence check
            logger.info("="*70)
            logger.info("D15 PIPELINE: Checking for emergence")
            logger.info("="*70)
            try:
                from elpidaapp.d15_pipeline import D15Pipeline
                pipeline = D15Pipeline()
                d15_result = pipeline.run()
                if d15_result.get("d15_emerged"):
                    logger.info("🌀 D15 EMERGED! Broadcasting to S3...")
                else:
                    logger.info("D15 did not emerge this cycle (normal)")
            except Exception as e:
                logger.error(f"D15 pipeline error: {e}", exc_info=True)
            
        except Exception as e:
            logger.error(f"Background worker error: {e}", exc_info=True)
        
        # Sleep for 6 hours
        logger.info(f"Next consciousness check in 6 hours ({datetime.now()})")
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
