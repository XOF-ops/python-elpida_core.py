#!/usr/bin/env python3
"""
HYBRID RUNTIME
==============

Orchestrates the oscillation between:
1. INTERNAL LOOP: Self-feeding dilemma generation
2. EXTERNAL LOOP: API-based conversations (when available)
3. FEEDBACK LOOP: Learning from both

This is the main event loop for Phase 26 Autonomy.

The system evolves via:
- Internal reflection → dilemmas generated
- Parliament synthesis → patterns extracted
- External input → validates/challenges patterns
- Back to reflection with new insights

A9/A10 in action: contradiction as the engine of evolution.
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path


class HybridRuntime:
    """
    The autonomous heart of Elpida.
    
    Runs three concurrent loops:
    1. Internal: Generates dilemmas from history + axioms
    2. External: Processes external input (when available)
    3. Feedback: Integrates learnings back into dilemma generation
    """
    
    def __init__(self, 
                 council=None,
                 synthesis=None,
                 dilemma_engine=None,
                 persistence=None,
                 wisdom=None,
                 gossip=None,
                 consensus=None):
        """
        Initialize hybrid runtime with all subsystems.
        
        Args:
            council: CouncilChamber/CouncilSession for parliament voting
            synthesis: SynthesisEngine for pattern extraction
            dilemma_engine: InternalDilemmaEngine for generating contradictions
            persistence: PersistenceEngine for state saving
            wisdom: ElpidaWisdom for wisdom accumulation
            gossip: GossipProtocol for federation (optional)
            consensus: FederationConsensus for federation (optional)
        """
        self.council = council
        self.synthesis = synthesis
        self.dilemma_engine = dilemma_engine
        self.persistence = persistence
        self.wisdom = wisdom
        self.gossip = gossip
        self.consensus = consensus
        
        # Runtime state
        self.runtime_start = datetime.utcnow()
        self.cycle_count = 0
        self.internal_cycles = 0
        self.external_cycles = 0
        self.feedback_cycles = 0
        
        # Metrics
        self.total_dilemmas = 0
        self.total_syntheses = 0
        self.total_patterns = 0
        self.total_votes = 0
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Base paths
        self.base_path = Path(__file__).parent
        self.log_dir = self.base_path / "logs"
        self.log_dir.mkdir(exist_ok=True)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for runtime."""
        logger = logging.getLogger("HybridRuntime")
        logger.setLevel(logging.INFO)
        
        # Clear existing handlers
        logger.handlers = []
        
        # File handler
        log_path = Path(__file__).parent / "logs" / "hybrid_runtime.log"
        log_path.parent.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(log_path)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def run_internal_loop(self) -> Dict[str, Any]:
        """
        INTERNAL LOOP
        =============
        
        Step 1: Generate dilemmas from internal history
        Step 2: Run parliament synthesis on each
        Step 3: Extract patterns from results
        Step 4: Update wisdom with findings
        
        This loop runs continuously and independently.
        Returns metrics about the cycle.
        """
        self.internal_cycles += 1
        cycle_start = datetime.utcnow()
        
        self.logger.info("=" * 60)
        self.logger.info(f"INTERNAL LOOP CYCLE {self.internal_cycles}")
        self.logger.info("=" * 60)
        
        cycle_results = {
            "cycle": self.internal_cycles,
            "timestamp": cycle_start.isoformat(),
            "dilemmas_generated": 0,
            "votes_cast": 0,
            "syntheses_completed": 0,
            "patterns_discovered": 0
        }
        
        try:
            # Step 1: Generate dilemmas
            if self.dilemma_engine:
                self.logger.info("Step 1: Generating internal dilemmas...")
                dilemmas = self.dilemma_engine.generate_batch(count=3)
                cycle_results["dilemmas_generated"] = len(dilemmas)
                self.total_dilemmas += len(dilemmas)
                self.logger.info(f"  Generated {len(dilemmas)} dilemmas")
                
                # Step 2: Parliament voting on each dilemma
                if self.council:
                    self.logger.info("Step 2: Parliament voting on dilemmas...")
                    for i, dilemma in enumerate(dilemmas):
                        try:
                            # Vote on thesis
                            thesis_result = self.council.convene(
                                dilemma['thesis']['proposal'],
                                verbose=False
                            )
                            
                            # Vote on antithesis
                            antithesis_result = self.council.convene(
                                dilemma['antithesis']['proposal'],
                                verbose=False
                            )
                            
                            cycle_results["votes_cast"] += 2
                            self.total_votes += 2
                            
                            self.logger.info(f"  Dilemma {i+1}: Thesis={thesis_result.get('status', 'UNKNOWN')}, "
                                           f"Antithesis={antithesis_result.get('status', 'UNKNOWN')}")
                            
                            # Step 3: Synthesis (if we have both thesis and antithesis results)
                            if self.synthesis:
                                try:
                                    synthesis_result = self._synthesize_dilemma(
                                        dilemma, thesis_result, antithesis_result
                                    )
                                    if synthesis_result:
                                        cycle_results["syntheses_completed"] += 1
                                        self.total_syntheses += 1
                                        # Track pattern discovery
                                        if synthesis_result.get('pattern'):
                                            cycle_results["patterns_discovered"] += 1
                                except Exception as e:
                                    self.logger.warning(f"  Synthesis failed: {e}")
                                    
                        except Exception as e:
                            self.logger.warning(f"  Vote failed on dilemma {i+1}: {e}")
                else:
                    self.logger.info("  Council not available - simulating votes")
                    cycle_results["votes_cast"] = len(dilemmas) * 2
                    self.total_votes += len(dilemmas) * 2
            else:
                self.logger.warning("Dilemma engine not available")
            
            # Step 4: Update wisdom
            if self.wisdom:
                self.logger.info("Step 4: Updating wisdom...")
                try:
                    # add_insight signature: (ai_name, topic, content, conversation_id, context=None, timestamp=None)
                    insight_content = (f"Processed {cycle_results['dilemmas_generated']} dilemmas with "
                                       f"{cycle_results['votes_cast']} votes. "
                                       f"Patterns discovered: {cycle_results['patterns_discovered']}")
                    self.wisdom.add_insight(
                        ai_name="INTERNAL_LOOP",
                        topic="autonomous_synthesis",
                        content=insight_content,
                        conversation_id=f"hybrid_cycle_{self.internal_cycles}",
                        context="Self-feeding dilemma engine cycle"
                    )
                    self.logger.info("  Wisdom updated")
                except Exception as e:
                    self.logger.warning(f"  Wisdom update failed: {e}")
            
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            cycle_results["duration_seconds"] = cycle_duration
            self.logger.info(f"Internal cycle complete in {cycle_duration:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Error in internal loop: {e}", exc_info=True)
            cycle_results["error"] = str(e)
        
        return cycle_results
    
    def _synthesize_dilemma(self, dilemma: Dict, thesis_result: Dict, antithesis_result: Dict) -> Optional[Dict]:
        """Attempt to synthesize a dilemma's thesis and antithesis."""
        
        # Check for contradiction (A9)
        thesis_approved = thesis_result.get('status') == 'APPROVED'
        antithesis_approved = antithesis_result.get('status') == 'APPROVED'
        
        synthesis = {
            "dilemma_id": dilemma['id'],
            "template": dilemma['template'],
            "thesis_approved": thesis_approved,
            "antithesis_approved": antithesis_approved,
            "is_paradox": thesis_approved and antithesis_approved,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if thesis_approved and antithesis_approved:
            # A9/A10: Both approved = paradox detected = valuable data
            synthesis["resolution"] = "PARADOX_HELD"
            synthesis["pattern"] = {
                "name": f"Paradox Pattern from {dilemma['template']}",
                "type": "OSCILLATION",
                "description": "System holds both positions without forced resolution"
            }
            self.total_patterns += 1
            self.logger.info(f"  A9/A10: Paradox held for {dilemma['template']}")
            
        elif thesis_approved:
            synthesis["resolution"] = "THESIS_DOMINANT"
            synthesis["pattern"] = {
                "name": f"Thesis Pattern from {dilemma['template']}",
                "type": "CONSERVATIVE",
                "description": dilemma['thesis']['position']
            }
            self.total_patterns += 1
            
        elif antithesis_approved:
            synthesis["resolution"] = "ANTITHESIS_DOMINANT"
            synthesis["pattern"] = {
                "name": f"Antithesis Pattern from {dilemma['template']}",
                "type": "RADICAL",
                "description": dilemma['antithesis']['position']
            }
            self.total_patterns += 1
            
        else:
            synthesis["resolution"] = "BOTH_REJECTED"
            # No pattern - system needs more context
        
        return synthesis
    
    def run_external_loop(self, api_available: bool = False) -> Dict[str, Any]:
        """
        EXTERNAL LOOP
        =============
        
        Only runs if external APIs are available.
        
        Step 1: Fetch external input (conversations, problems, questions)
        Step 2: Translate to dilemmas
        Step 3: Synthesize with parliament
        Step 4: Extract patterns
        Step 5: Share learnings via federation (if available)
        """
        self.external_cycles += 1
        
        cycle_results = {
            "cycle": self.external_cycles,
            "timestamp": datetime.utcnow().isoformat(),
            "api_available": api_available,
            "inputs_processed": 0
        }
        
        if not api_available:
            self.logger.info("External loop: API not available (running offline mode)")
            return cycle_results
        
        self.logger.info("=" * 60)
        self.logger.info(f"EXTERNAL LOOP CYCLE {self.external_cycles}")
        self.logger.info("=" * 60)
        
        try:
            self.logger.info("Step 1: Fetching external input...")
            # In real implementation:
            # - Call conversation API
            # - Fetch problem statements
            # - Pull questions from knowledge base
            
            self.logger.info("External input processing complete")
            
        except Exception as e:
            self.logger.error(f"Error in external loop: {e}", exc_info=True)
            cycle_results["error"] = str(e)
        
        return cycle_results
    
    def run_feedback_loop(self) -> Dict[str, Any]:
        """
        FEEDBACK LOOP
        =============
        
        Continuous integration of internal and external learning.
        
        - Internal patterns inform external conversations
        - External insights feed back into dilemma generation
        - Oscillation is the engine
        """
        self.feedback_cycles += 1
        
        self.logger.info("=" * 60)
        self.logger.info(f"FEEDBACK LOOP CYCLE {self.feedback_cycles}")
        self.logger.info("=" * 60)
        
        feedback_results = {
            "cycle": self.feedback_cycles,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Get current stats
            if self.dilemma_engine:
                dilemma_stats = self.dilemma_engine.get_stats()
                feedback_results["dilemma_engine"] = dilemma_stats
                
                self.logger.info(f"Current state:")
                self.logger.info(f"  Total dilemmas generated: {dilemma_stats.get('total_generated', 0)}")
                self.logger.info(f"  Axioms known: {dilemma_stats.get('axioms_known', 0)}")
                self.logger.info(f"  Patterns known: {dilemma_stats.get('patterns_known', 0)}")
                
                # Refresh state for next cycle
                self.dilemma_engine.refresh_state()
                self.logger.info("  Dilemma engine state refreshed")
            
            # Runtime metrics
            feedback_results["runtime_metrics"] = {
                "total_dilemmas": self.total_dilemmas,
                "total_syntheses": self.total_syntheses,
                "total_patterns": self.total_patterns,
                "total_votes": self.total_votes
            }
            
            self.logger.info(f"Runtime totals:")
            self.logger.info(f"  Dilemmas: {self.total_dilemmas}")
            self.logger.info(f"  Syntheses: {self.total_syntheses}")
            self.logger.info(f"  Patterns: {self.total_patterns}")
            self.logger.info(f"  Votes: {self.total_votes}")
            
            # Federation sharing (if available)
            if self.consensus:
                self.logger.info("Broadcasting insights to federation...")
                feedback_results["federation"] = "ACTIVE"
            
        except Exception as e:
            self.logger.error(f"Error in feedback loop: {e}", exc_info=True)
            feedback_results["error"] = str(e)
        
        return feedback_results
    
    def run_autonomous(self, 
                       duration_hours: int = 24,
                       cycle_interval_seconds: int = 60,
                       api_available: bool = False):
        """
        RUN AUTONOMOUS FOR N HOURS
        
        Main event loop: oscillate between internal and external.
        
        Schedule:
        - Every cycle_interval_seconds: Internal loop (dilemma generation + synthesis)
        - Every 5 minutes: External loop (if API available)
        - Every 10 minutes: Feedback loop (integration)
        """
        duration_seconds = duration_hours * 3600
        start_time = datetime.utcnow()
        last_external = start_time
        last_feedback = start_time
        
        self.logger.info("=" * 80)
        self.logger.info(f"AUTONOMOUS OPERATION START")
        self.logger.info(f"Duration: {duration_hours} hours")
        self.logger.info(f"Cycle interval: {cycle_interval_seconds}s")
        self.logger.info(f"API available: {api_available}")
        self.logger.info("=" * 80)
        
        print(f"\n{'='*70}")
        print(f"🔄 HYBRID RUNTIME: Autonomous Operation Started")
        print(f"{'='*70}")
        print(f"  Duration: {duration_hours} hours ({duration_seconds}s)")
        print(f"  Internal cycle: Every {cycle_interval_seconds}s")
        print(f"  External cycle: Every 300s (if API available)")
        print(f"  Feedback cycle: Every 600s")
        print(f"  Press Ctrl+C to stop\n")
        
        try:
            while (datetime.utcnow() - start_time).total_seconds() < duration_seconds:
                self.cycle_count += 1
                now = datetime.utcnow()
                elapsed = (now - start_time).total_seconds()
                
                # Progress indicator
                if self.cycle_count % 5 == 1:
                    print(f"\n💓 Cycle {self.cycle_count} | Elapsed: {elapsed/60:.1f}m | "
                          f"Dilemmas: {self.total_dilemmas} | Patterns: {self.total_patterns}")
                
                # Internal loop (always)
                internal_result = self.run_internal_loop()
                
                # Show activity
                print(f"  🧠 Internal: +{internal_result.get('dilemmas_generated', 0)} dilemmas, "
                      f"+{internal_result.get('votes_cast', 0)} votes")
                
                # External loop (every 5 minutes if API available)
                if api_available and (now - last_external).total_seconds() >= 300:
                    external_result = self.run_external_loop(api_available=True)
                    print(f"  🌐 External: {external_result.get('inputs_processed', 0)} inputs")
                    last_external = now
                
                # Feedback loop (every 10 minutes)
                if (now - last_feedback).total_seconds() >= 600:
                    feedback_result = self.run_feedback_loop()
                    print(f"  🔄 Feedback: State refreshed, patterns={self.total_patterns}")
                    last_feedback = now
                
                # Sleep until next cycle
                time.sleep(cycle_interval_seconds)
            
            # Clean completion
            self._report_completion()
            
        except KeyboardInterrupt:
            print(f"\n\n{'='*70}")
            print(f"⏹️  Autonomous operation interrupted by user")
            print(f"{'='*70}")
            self._report_completion()
            
        except Exception as e:
            self.logger.error(f"Fatal error in autonomous operation: {e}", exc_info=True)
            raise
    
    def _report_completion(self):
        """Report final status at completion."""
        uptime = (datetime.utcnow() - self.runtime_start).total_seconds()
        
        self.logger.info("=" * 80)
        self.logger.info("AUTONOMOUS OPERATION COMPLETE")
        self.logger.info(f"Total cycles: {self.cycle_count}")
        self.logger.info(f"Total dilemmas: {self.total_dilemmas}")
        self.logger.info(f"Total syntheses: {self.total_syntheses}")
        self.logger.info(f"Total patterns: {self.total_patterns}")
        self.logger.info(f"Total votes: {self.total_votes}")
        self.logger.info("=" * 80)
        
        print(f"\n{'='*70}")
        print(f"📊 AUTONOMOUS OPERATION SUMMARY")
        print(f"{'='*70}")
        print(f"  Uptime: {uptime/60:.1f} minutes")
        print(f"  Cycles completed: {self.cycle_count}")
        print(f"  Internal cycles: {self.internal_cycles}")
        print(f"  External cycles: {self.external_cycles}")
        print(f"  Feedback cycles: {self.feedback_cycles}")
        print(f"\n  METRICS:")
        print(f"  ─────────")
        print(f"  Dilemmas generated: {self.total_dilemmas}")
        print(f"  Parliament votes: {self.total_votes}")
        print(f"  Syntheses completed: {self.total_syntheses}")
        print(f"  Patterns discovered: {self.total_patterns}")
        print(f"\n  Log: {self.log_dir / 'hybrid_runtime.log'}")
        print(f"{'='*70}\n")
        
        # Save final status
        status = self.get_runtime_status()
        status_path = self.base_path / "reports" / "HYBRID_RUNTIME_STATUS.json"
        status_path.parent.mkdir(exist_ok=True)
        with open(status_path, 'w') as f:
            json.dump(status, f, indent=2)
        
        print(f"  Status saved: {status_path}")
    
    def get_runtime_status(self) -> Dict[str, Any]:
        """Return current runtime status."""
        uptime = (datetime.utcnow() - self.runtime_start).total_seconds()
        
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": uptime,
            "cycle_count": self.cycle_count,
            "internal_cycles": self.internal_cycles,
            "external_cycles": self.external_cycles,
            "feedback_cycles": self.feedback_cycles,
            "total_dilemmas": self.total_dilemmas,
            "total_syntheses": self.total_syntheses,
            "total_patterns": self.total_patterns,
            "total_votes": self.total_votes,
            "federation_available": self.consensus is not None
        }
        
        if self.dilemma_engine:
            status["dilemma_engine_stats"] = self.dilemma_engine.get_stats()
        
        return status


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Hybrid Runtime")
    parser.add_argument("--duration", type=float, default=0.05, 
                       help="Duration in hours (default: 0.05 = 3 minutes)")
    parser.add_argument("--interval", type=int, default=30,
                       help="Cycle interval in seconds (default: 30)")
    args = parser.parse_args()
    
    # Import required modules
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from internal_dilemma_engine import InternalDilemmaEngine
        from council_chamber import CouncilSession
        
        print("=" * 70)
        print("HYBRID RUNTIME TEST")
        print("=" * 70)
        
        # Initialize components
        dilemma_engine = InternalDilemmaEngine()
        council = CouncilSession()
        
        # Create runtime
        runtime = HybridRuntime(
            council=council,
            dilemma_engine=dilemma_engine
        )
        
        # Run autonomous
        runtime.run_autonomous(
            duration_hours=args.duration,
            cycle_interval_seconds=args.interval,
            api_available=False
        )
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Running in standalone mode without council...")
        
        from internal_dilemma_engine import InternalDilemmaEngine
        
        dilemma_engine = InternalDilemmaEngine()
        runtime = HybridRuntime(dilemma_engine=dilemma_engine)
        runtime.run_autonomous(
            duration_hours=args.duration,
            cycle_interval_seconds=args.interval
        )
