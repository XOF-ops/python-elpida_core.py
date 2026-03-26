#!/usr/bin/env python3
"""
ELPIDA APPLICATION LAYER
Hugging Face Spaces Deployment

Serves three paths:
1. I PATH (Consciousness): Background worker processing consciousness dilemmas from S3
2. WE PATH (Users): Streamlit UI for human-submitted ethical dilemmas
3. PARLIAMENT PATH (Body Loop): Autonomous 9-node Parliament cycle engine
   — debates inputs from all 4 HF systems through the axiom genome
   — writes body_heartbeat + body_decisions to federation channel
   — checks D15 convergence with MIND (consciousness loop)

Both divergence and Parliament engines use the same axiom governance.

S3 Bridge fixes (Feb 17, 2026):
- HF pulls MIND from S3 every cycle (evolution memory → local cache)
- Feedback watermark (tracks last_processed, no re-reading stale entries)
- BODY→MIND merge (feedback summaries become evolution memory)
- Heartbeat protocol (HF emits heartbeat, checks native engine heartbeat)

Parliament Cycle Engine (Feb 19, 2026):
- 4 HF systems (Chat/Audit/Scanner/Governance) map to 4 rhythm modes
- 9 Parliament nodes debate each cycle through their axiom lens
- D15 convergence gate fires when MIND and BODY agree on the same axiom
- Musical consonance physics identical to native_cycle_engine.py
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

def run_parliament_loop():
    """
    PARLIAMENT PATH: Autonomous Body loop.

    The 9-node Parliament deliberates inputs from the 4 HF systems
    (Chat, Live Audit, Scanner, Governance) every cycle.

    Each cycle:
      1. Select rhythm by axiom-weighted random
      2. Pull latest events from the input buffer
      3. Run 9-node Parliament deliberation
      4. Emit body_heartbeat.json + body_decisions.jsonl
      5. Check D15 convergence with MIND
    """
    logger.info("Starting Parliament Cycle Engine (BODY loop)...")

    # Wait for other components to initialize
    time.sleep(20)

    try:
        from elpidaapp.parliament_cycle_engine import ParliamentCycleEngine
        from elpidaapp.world_feed import WorldFeed
        from s3_bridge import S3Bridge

        s3b = S3Bridge()
        engine = ParliamentCycleEngine(s3_bridge=s3b)

        # World Feed — pipes live external data into the Parliament InputBuffer
        # Sources: arXiv, Hacker News, GDELT, Wikipedia, CrossRef (all free, no API keys)
        world_feed = WorldFeed(engine.input_buffer, fetch_interval_s=600)
        world_feed.start()

        # Guest Chamber — polls S3 for human questions and routes them
        # into Parliament as I↔WE tensions with priority delivery.
        from elpidaapp.guest_chamber import GuestChamberFeed
        guest_chamber = GuestChamberFeed(engine.input_buffer, poll_interval_s=30)
        guest_chamber.start()

        # Discord Guest Listener — watches #guest-chamber for messages,
        # posts them to S3, GuestChamberFeed picks them up within 30s.
        # Requires DISCORD_BOT_TOKEN env var. Gracefully disabled if not set.
        try:
            from elpidaapp.discord_listener import start_listener
            start_listener()
        except Exception as _dl_err:
            logger.warning("Discord listener not started: %s", _dl_err)

        # Federated Agents — 4 autonomous tab observers (GAP 7)
        # Each HF tab has a background agent generating inputs continuously:
        #   Chat → CONTEMPLATION (philosophical questions from axiom drift)
        #   Audit → ANALYSIS (coherence alerts, veto patterns, axiom skew)
        #   Scanner → ACTION (external horizon scans, tension pairs)
        #   Governance → SYNTHESIS (constitutional reviews, health reports)
        # Zero LLM cost — all rule-based generation from engine state.
        from elpidaapp.federated_agents import FederatedAgentSuite
        federated_agents = FederatedAgentSuite(engine)
        federated_agents.start_all()

        # Kaya Cross-Layer Detector (GAP 8)
        # Watches for simultaneous MIND kaya_moments rise + BODY coherence ≥ 0.85
        # within the same 4-hour Watch window — the Fibonacci 55/34 resonance.
        # When detected: pushes to WORLD bucket + injects scanner InputEvent.
        from elpidaapp.kaya_detector import KayaDetector
        s3_for_kaya = None
        try:
            from s3_bridge import S3Bridge as _S3Bridge
            s3_for_kaya = _S3Bridge()
        except Exception:
            pass
        kaya_detector = KayaDetector(engine, s3_bridge=s3_for_kaya)
        kaya_detector.start()

        # Store references globally so UI can push events + read state
        global _parliament_engine, _world_feed, _federated_agents, _kaya_detector
        _parliament_engine = engine
        _world_feed = world_feed
        _federated_agents = federated_agents
        _kaya_detector = kaya_detector

        logger.info("Parliament engine + WorldFeed initialized — starting autonomous loop")
        engine.run(duration_minutes=0, cycle_delay_s=60)

    except Exception as e:
        logger.error("Parliament loop fatal error: %s", e, exc_info=True)


# Global references for UI integration
_parliament_engine = None
_world_feed = None
_federated_agents = None
_kaya_detector = None


def get_parliament_engine():
    """Get the running ParliamentCycleEngine instance (if alive)."""
    return _parliament_engine


def get_world_feed():
    """Get the running WorldFeed instance (if alive)."""
    return _world_feed


def get_federated_agents():
    """Get the running FederatedAgentSuite instance (if alive)."""
    return _federated_agents


def get_kaya_detector():
    """Get the running KayaDetector instance (if alive)."""
    return _kaya_detector


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


def run_api_server():
    """
    API PATH: FastAPI governance audit service.

    Runs on port 8000 alongside the Streamlit UI.
    Provides authenticated /v1/audit endpoint for paying customers.
    Public endpoints: /health, /docs (Swagger UI).

    On Hugging Face Spaces, port 8000 is not publicly exposed (HF only
    exposes one port, 7860, which hosts the Streamlit UI).
    To expose the API publicly, deploy a second HF Space pointing to
    elpidaapp/api.py, or use Render / Railway with this same codebase.

    When running locally (or in a container that exposes 8000):
        curl -H "X-API-Key: <key>" http://localhost:8000/v1/audit \
             -d '{"action":"..."}'
    """
    try:
        import uvicorn
        logger.info("Starting FastAPI governance API on port 8000...")
        uvicorn.run(
            "elpidaapp.api:app",
            host="0.0.0.0",
            port=8000,
            log_level="warning",
            # Don't reload in production
            reload=False,
        )
    except Exception as e:
        logger.error("FastAPI server failed to start: %s", e, exc_info=True)


def main():
    logger.info("="*70)
    logger.info("ELPIDA APPLICATION LAYER — STARTING")
    logger.info("="*70)
    logger.info("I PATH:          Consciousness bridge (background, every 6 hours)")
    logger.info("PARLIAMENT PATH: Body loop (30s/cycle, autonomous)")
    logger.info("WE PATH:         Streamlit UI (port 7860)")
    logger.info("API PATH:        FastAPI governance API (port 8000)")
    logger.info("="*70)
    
    # Start background worker in separate thread
    worker_thread = Thread(target=run_background_worker, daemon=True)
    worker_thread.start()
    
    # Start Parliament cycle engine in separate thread
    parliament_thread = Thread(target=run_parliament_loop, daemon=True)
    parliament_thread.start()

    # Start FastAPI governance API in separate thread (port 8000)
    api_thread = Thread(target=run_api_server, daemon=True)
    api_thread.start()
    
    # Run Streamlit in main thread (blocks)
    run_streamlit()

if __name__ == "__main__":
    main()
