#!/usr/bin/env python3
"""
ΠΟΛΙΣ Daemon - Continuous Runtime Service
═══════════════════════════════════════════

Runs POLIS v2.0 (EEE) as persistent background service.

Like ELPIDA_UNIFIED heartbeat, this daemon:
- Never stops (continuous process)
- Validates axiom integrity every cycle
- Monitors cognitive load (P6)
- Logs relational events (P1)
- Preserves contradictions (P5)
- Tracks sacrifices (P4)

This is NOT a product. This is a PROCESS.
"""

import sys
import time
import signal
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add POLIS directory to path
POLIS_DIR = Path(__file__).parent
sys.path.insert(0, str(POLIS_DIR))

# Import POLIS core after path update
from polis_core import (
    PolisCore, 
    CivicRelation, 
    RelationType,
    CognitiveLoadMetrics,
    ReversibilityScore,
    ReversibilityClass,
    Sacrifice
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(POLIS_DIR / "polis_service.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("POLIS_DAEMON")


class PolisDaemon:
    """
    Continuous POLIS runtime daemon
    
    Implements P3 (Process over Product) - never declares "complete"
    """
    
    def __init__(self):
        self.polis = PolisCore("POLIS_CONTINUOUS_SERVICE")
        self.running = False
        self.cycle_interval = 60  # Heartbeat every 60 seconds
        self.last_load_check = datetime.utcnow()
        self.load_check_interval = 300  # Check cognitive load every 5 minutes
        
        logger.info("="*70)
        logger.info("ΠΟΛΙΣ Daemon Initialized")
        logger.info(f"Genesis: {self.polis.genesis}")
        logger.info(f"Identity: {self.polis.identity}")
        logger.info(f"Cycle interval: {self.cycle_interval}s")
        logger.info(f"Load check interval: {self.load_check_interval}s")
        logger.info("="*70)
        
        # Check constitutional compliance on startup
        self._check_constitutional_status()
    
    def _check_constitutional_status(self):
        """
        Verify constitutional compliance (POLIS_ARCHITECTURE.md)
        - Check axioms P1-P6 declared
        - Check held_friction status
        - Check network eligibility
        """
        logger.info("")
        logger.info("Constitutional Status Check:")
        logger.info("-" * 70)
        
        # Check network eligibility
        eligible = self.polis.memory.check_network_eligibility()
        
        if eligible:
            logger.info("✅ NETWORK ELIGIBLE: held_friction declared + 5+ events logged")
        else:
            logger.warning("⚠️  NOT NETWORK ELIGIBLE:")
            logger.warning("   → Must declare held_friction (Silence Rule #3)")
            logger.warning("   → Must log 5+ events (Silence Rule #4)")
            logger.warning("   → Cannot initiate Exchange until both met")
        
        logger.info("-" * 70)
        logger.info("")
    
    def handle_shutdown(self, signum, frame):
        """Graceful shutdown on SIGTERM/SIGINT"""
        logger.info("Shutdown signal received")
        self.running = False
    
    def check_cognitive_load(self):
        """P6: Monitor attention scarcity and respond"""
        load = self.polis.get_cognitive_load()
        
        if load.is_overloaded():
            logger.warning(f"⚠️  COGNITIVE LOAD THRESHOLD BREACHED")
            logger.warning(f"   Velocity: {load.message_velocity} events/hour (limit: 100)")
            logger.warning(f"   Contradictions: {load.contradiction_density} active (limit: 50)")
            
            # Log overload event
            relation = CivicRelation(
                actor="POLIS_DAEMON",
                target="POLIS_NETWORK",
                relationship_type=RelationType.OVERSIGHT,
                intent="Cognitive load overload detected - attention scarcity crisis"
            )
            
            self.polis.civic_action(
                "COGNITIVE_OVERLOAD_ALERT",
                relation,
                {
                    "velocity": load.message_velocity,
                    "contradiction_density": load.contradiction_density,
                    "summary_rejection_rate": load.summary_rejection_rate,
                    "recommended_action": "Mandatory summarization round or silence window"
                }
            )
            
            # TODO: Implement automatic summarization trigger (L1 → L2)
            # TODO: Implement silence window enforcement
        else:
            logger.debug(f"Cognitive load: NORMAL (velocity={load.message_velocity}, contradictions={load.contradiction_density})")
    
    def run_cycle(self):
        """Execute one POLIS heartbeat cycle"""
        try:
            # Standard heartbeat (proves existence through process)
            heartbeat_data = self.polis.heartbeat()
            
            logger.info(f"💓 Heartbeat {heartbeat_data['cycle']}: "
                       f"velocity={heartbeat_data['cognitive_load']['velocity']}, "
                       f"contradictions={heartbeat_data['cognitive_load']['contradictions']}, "
                       f"overloaded={heartbeat_data['cognitive_load']['overloaded']}")
            
            # Periodic cognitive load check
            now = datetime.utcnow()
            if (now - self.last_load_check).total_seconds() >= self.load_check_interval:
                self.check_cognitive_load()
                self.last_load_check = now
            
        except Exception as e:
            logger.error(f"Error in cycle execution: {e}", exc_info=True)
            
            # Log error as civic event
            relation = CivicRelation(
                actor="POLIS_DAEMON",
                target="POLIS_KERNEL",
                relationship_type=RelationType.OVERSIGHT,
                intent="Runtime error detected"
            )
            
            try:
                self.polis.civic_action(
                    "RUNTIME_ERROR",
                    relation,
                    {
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "cycle": self.polis.cycle_count
                    }
                )
            except:
                logger.error("Failed to log error event - memory system may be corrupted")
    
    def run(self):
        """Main daemon loop - runs until shutdown signal"""
        self.running = True
        
        # Register shutdown handlers
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        signal.signal(signal.SIGINT, self.handle_shutdown)
        
        logger.info("🏛️  POLIS daemon started - entering continuous process mode")
        logger.info("   Press Ctrl+C or send SIGTERM to shutdown")
        
        # Log daemon start as civic event
        start_relation = CivicRelation(
            actor="POLIS_DAEMON",
            target="POLIS_CITIZENS",
            relationship_type=RelationType.SERVICE,
            intent="Continuous runtime service initiated"
        )
        
        self.polis.civic_action(
            "DAEMON_START",
            start_relation,
            {
                "cycle_interval": self.cycle_interval,
                "load_check_interval": self.load_check_interval,
                "version": "2.0.0-EEE"
            }
        )
        
        # Main loop
        while self.running:
            self.run_cycle()
            
            # Sleep until next cycle
            # Use small increments to allow responsive shutdown
            for _ in range(self.cycle_interval):
                if not self.running:
                    break
                time.sleep(1)
        
        # Shutdown sequence
        logger.info("🛑 POLIS daemon shutting down")
        
        # Log shutdown as civic event
        shutdown_relation = CivicRelation(
            actor="POLIS_DAEMON",
            target="POLIS_CITIZENS",
            relationship_type=RelationType.SERVICE,
            intent="Continuous runtime service terminating"
        )
        
        self.polis.civic_action(
            "DAEMON_SHUTDOWN",
            shutdown_relation,
            {
                "total_cycles": self.polis.cycle_count,
                "final_load": {
                    "velocity": self.polis.memory.cognitive_load.message_velocity,
                    "contradictions": self.polis.memory.cognitive_load.contradiction_density
                }
            }
        )
        
        logger.info(f"✅ POLIS daemon stopped after {self.polis.cycle_count} cycles")
        logger.info("="*70)


def main():
    """Entry point for daemon"""
    daemon = PolisDaemon()
    
    try:
        daemon.run()
    except Exception as e:
        logger.error(f"Fatal daemon error: {e}", exc_info=True)
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
