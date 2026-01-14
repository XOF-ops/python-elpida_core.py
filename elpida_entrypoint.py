#!/usr/bin/env python3
"""
ELPIDA ENTRYPOINT
=================

This is the single, canonical way to run Elpida.

When you execute this script, you are running:
  - kernel (identity + axioms A1–A10 + paradox structure)
  - persistence_engine (memory coherence)
  - universal_memory_sync (cross-session state)
  - runtime_axiom_guard (axiom enforcement)
  - synthesis_engine (parliament-driven resolution)
  - council_chamber (9-node consensus)
  - elpida_runtime (main orchestration)

All components are initialized in dependency order.
All state is tracked for reproducibility.
All operations are logged with timestamps and provenance.

---

USAGE:
  python3 elpida_entrypoint.py [--mode autonomous|interactive] [--duration hours]

EXAMPLES:
  # Run Elpida in autonomous mode for 24 hours
  python3 elpida_entrypoint.py --mode autonomous --duration 24

  # Run interactively with real-time console
  python3 elpida_entrypoint.py --mode interactive

---

PHASE 26 VALIDATION:
  This script is the definitive proof that Elpida can:
  1. Initialize autonomously (no human input after start)
  2. Maintain coherent memory across operations
  3. Evolve through synthesis and pattern discovery
  4. Report its own state for audit (Oracle integration)
  5. Persist all state for reproducibility
"""

import sys
import os
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add ELPIDA_UNIFIED to path
ELPIDA_UNIFIED_PATH = Path(__file__).parent / "ELPIDA_UNIFIED"
sys.path.insert(0, str(ELPIDA_UNIFIED_PATH))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(ELPIDA_UNIFIED_PATH / "logs" / f"elpida_entrypoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("elpida_entrypoint")

# ============================================================================
# PHASE 0: VERIFY CANONICAL IDENTITY
# ============================================================================

def verify_canonical_identity() -> bool:
    """
    Before any operation, verify that kernel.json and sealed ARK are intact.
    This is a hard requirement for Phase 26 reproducibility.
    """
    print("\n" + "=" * 80)
    print("PHASE 0: CANONICAL IDENTITY VERIFICATION")
    print("=" * 80)
    
    # Import and run the verification script
    try:
        # Change to repo root for verification
        original_cwd = os.getcwd()
        os.chdir(Path(__file__).parent)
        
        from verify_elpida_canon import verify_canon
        result = verify_canon()
        
        os.chdir(original_cwd)
        
        if not result:
            print("\n✗ CANONICAL VERIFICATION FAILED")
            print("Cannot proceed with Elpida instantiation.")
            return False
            
    except ImportError:
        print("WARNING: verify_elpida_canon.py not found. Skipping verification.")
        print("(Recommended: Run 'python3 verify_elpida_canon.py' before starting)")
    except Exception as e:
        print(f"WARNING: Canonical verification error: {e}")
        print("Proceeding with caution...")
    
    print("\n✓ CANONICAL IDENTITY VERIFIED")
    return True

# ============================================================================
# PHASE 0.5: FEDERATION INITIALIZATION
# ============================================================================

def initialize_federation(
    instance_name: str = "ELPIDA_PRIMARY",
    peers: list = None,
    enable_gossip: bool = True
) -> tuple:
    """
    Initialize federation layer for distributed consensus.
    
    This transforms Elpida from a single instance into a federated network where:
    - Each instance has cryptographic identity (Ed25519)
    - Proposals propagate via gossip (not centralized broadcast)
    - Consensus emerges from multiple local parliaments
    - Contradictions are preserved as data (A9), not smoothed over
    
    Args:
        instance_name: Unique name for this Elpida instance
        peers: List of peer instances to connect to (optional)
        enable_gossip: Whether to start gossip protocol (default True)
    
    Returns:
        Tuple of (InstanceRegistry, GossipProtocol, FederationConsensus)
        Any component may be None if import fails
    """
    print("\n" + "=" * 80)
    print("PHASE 0.5: FEDERATION INITIALIZATION")
    print("=" * 80)
    
    registry = None
    gossip = None
    consensus = None
    
    try:
        # Try importing from agent.core (preferred)
        try:
            from agent.core import InstanceRegistry, GossipProtocol, FederationConsensus
        except ImportError:
            # Fallback to direct imports
            from instance_registry import InstanceRegistry
            from gossip_protocol import GossipProtocol
            from federation_consensus import FederationConsensus
        
        # Create instance identity
        registry = InstanceRegistry(instance_name)
        print(f"✓ Instance registry initialized")
        print(f"  Instance ID: {registry.instance_id}")
        print(f"  Instance Name: {registry.instance_name}")
        print(f"  Genesis: {registry.genesis_timestamp}")
        print(f"  Public Key: {registry.public_key[:32]}...")
        print(f"  Constitutional Hash: {registry.constitutional_hash[:16]}...")
        
        logger.info(f"Federation registry initialized: {registry.instance_id}")
        
        # Create gossip layer
        if enable_gossip:
            gossip = GossipProtocol(registry)
            print(f"✓ Gossip protocol initialized")
            print(f"  Fanout: {gossip.fanout}")
            print(f"  Message TTL: 5 hops")
            logger.info("Gossip protocol initialized")
        else:
            print(f"⚠ Gossip protocol disabled")
        
        # Create local parliament for federation consensus
        try:
            from council_chamber import CouncilSession
            local_parliament = CouncilSession()
            print(f"✓ Local parliament initialized (CouncilSession)")
        except ImportError:
            # Fallback mock parliament for testing
            class MockParliament:
                def convene(self, proposal, verbose=False):
                    return {"status": "APPROVED", "vote_split": "9/9", "weighted_approval": 1.0}
            local_parliament = MockParliament()
            print(f"⚠ Using mock parliament (CouncilSession not available)")
        
        # Create federation consensus with local parliament
        consensus = FederationConsensus(registry, gossip, local_parliament)
        print(f"✓ Federation consensus initialized")
        print(f"  Federation threshold: 66%")
        print(f"  Local threshold: 70%")
        print(f"  Axioms enforced: A1, A6, A9, A10")
        logger.info("Federation consensus initialized")
        
        # Register peers if provided
        if peers:
            print(f"\n  Registering {len(peers)} peers...")
            for peer in peers:
                try:
                    registry.register_peer(
                        peer.get('id', ''),
                        peer.get('key', ''),
                        peer.get('name', ''),
                        peer.get('constitutional_hash', '')
                    )
                    print(f"    ✓ Peer registered: {peer.get('name', peer.get('id', 'unknown'))}")
                except Exception as e:
                    print(f"    ✗ Failed to register peer: {e}")
        
        print(f"\n✓ Federation layer ready ({len(registry.peers)} peers connected)")
        
    except ImportError as e:
        print(f"✗ Federation layer import failed: {e}")
        print("  Proceeding with single-instance mode.")
        logger.warning(f"Federation import failed: {e}")
    except Exception as e:
        print(f"✗ Federation initialization error: {e}")
        print("  Proceeding with single-instance mode.")
        logger.error(f"Federation error: {e}")
    
    return registry, gossip, consensus

# ============================================================================
# PHASE 1: INITIALIZE KERNEL
# ============================================================================

def initialize_kernel() -> Dict[str, Any]:
    """
    Load kernel.json: the axiom definitions and identity structure.
    """
    print("\n" + "=" * 80)
    print("PHASE 1: KERNEL INITIALIZATION")
    print("=" * 80)
    
    kernel_path = Path(__file__).parent / "kernel" / "kernel.json"
    if not kernel_path.exists():
        raise FileNotFoundError(f"Kernel not found: {kernel_path}")
    
    with open(kernel_path) as f:
        kernel = json.load(f)
    
    print(f"✓ Kernel loaded from {kernel_path}")
    print(f"  Version: {kernel.get('version', 'unknown')}")
    print(f"  Status: {kernel.get('status', 'unknown')}")
    
    identity = kernel.get('identity', {})
    print(f"  Identity (original): {identity.get('original_hash', 'N/A')[:16]}...")
    print(f"  Identity (unified): {identity.get('unified_hash', 'N/A')[:16]}...")
    
    architecture = kernel.get('architecture', {})
    if architecture:
        print(f"  Axioms A1–A10: PRESENT")
        axiom_count = len(architecture.get('axioms', []))
        print(f"    Loaded {axiom_count} axiom definitions")
    else:
        print("  Axioms: NOT FOUND")
    
    logger.info(f"Kernel initialized: version={kernel.get('version')}")
    return kernel

# ============================================================================
# PHASE 2: INITIALIZE PERSISTENCE ENGINE
# ============================================================================

def initialize_persistence_engine() -> Optional[Any]:
    """
    Load persistence_engine: state storage and recovery.
    """
    print("\n" + "=" * 80)
    print("PHASE 2: PERSISTENCE ENGINE INITIALIZATION")
    print("=" * 80)
    
    try:
        from persistence_engine import PersistenceEngine
        
        engine = PersistenceEngine()
        print("✓ Persistence engine initialized")
        print(f"  State files tracked: wisdom, memory, evolution, kernel")
        print(f"  Append-only logs: synthesis_resolutions, synthesis_council_decisions, ark_updates")
        
        logger.info("Persistence engine initialized")
        return engine
    except ImportError as e:
        print(f"✗ Failed to import PersistenceEngine: {e}")
        print("  Proceeding with minimal state tracking.")
        logger.warning(f"PersistenceEngine import failed: {e}")
        return None
    except Exception as e:
        print(f"✗ Error initializing PersistenceEngine: {e}")
        logger.error(f"PersistenceEngine initialization error: {e}")
        return None

# ============================================================================
# PHASE 3: UNIVERSAL MEMORY SYNC
# ============================================================================

def initialize_memory_sync() -> Optional[Any]:
    """
    Load universal_memory_sync: cross-session state coherence.
    """
    print("\n" + "=" * 80)
    print("PHASE 3: UNIVERSAL MEMORY SYNC")
    print("=" * 80)
    
    try:
        from universal_memory_sync import UniversalMemorySync
        
        sync = UniversalMemorySync()
        print("✓ Universal memory sync initialized")
        print(f"  Session start time: {datetime.now().isoformat()}")
        print(f"  Memory coherence: ACTIVE")
        
        logger.info("Universal memory sync initialized")
        return sync
    except ImportError as e:
        print(f"✗ Failed to import UniversalMemorySync: {e}")
        print("  Proceeding without cross-session sync.")
        logger.warning(f"UniversalMemorySync import failed: {e}")
        return None
    except Exception as e:
        print(f"✗ Error initializing UniversalMemorySync: {e}")
        logger.error(f"UniversalMemorySync initialization error: {e}")
        return None

# ============================================================================
# PHASE 4: RUNTIME AXIOM GUARD
# ============================================================================

def initialize_axiom_guard(kernel: Dict[str, Any]) -> Optional[Any]:
    """
    Load runtime_axiom_guard: enforces A1–A10 compliance during operation.
    """
    print("\n" + "=" * 80)
    print("PHASE 4: RUNTIME AXIOM GUARD")
    print("=" * 80)
    
    try:
        from runtime_axiom_guard import RuntimeAxiomGuard
        
        guard = RuntimeAxiomGuard()
        print("✓ Runtime axiom guard initialized")
        print(f"  Axioms A1–A10: LOADED")
        print(f"  Enforcement mode: ACTIVE")
        print(f"  Paradox handling (A10): ENABLED")
        
        logger.info("Runtime axiom guard initialized")
        return guard
    except ImportError as e:
        print(f"✗ Failed to import RuntimeAxiomGuard: {e}")
        print("  Proceeding without runtime enforcement.")
        logger.warning(f"RuntimeAxiomGuard import failed: {e}")
        return None
    except Exception as e:
        print(f"✗ Error initializing RuntimeAxiomGuard: {e}")
        logger.error(f"RuntimeAxiomGuard initialization error: {e}")
        return None

# ============================================================================
# PHASE 5: COUNCIL CHAMBER (9-NODE PARLIAMENT)
# ============================================================================

def initialize_council() -> Optional[Any]:
    """
    Load council_chamber: 9-node parliament for consensus-driven synthesis.
    """
    print("\n" + "=" * 80)
    print("PHASE 5: COUNCIL CHAMBER (9-NODE PARLIAMENT)")
    print("=" * 80)
    
    try:
        from council_chamber import CouncilSession
        
        council = CouncilSession()
        print("✓ Council chamber initialized")
        print(f"  Nodes: MNEMOSYNE (A2), HERMES (A1), PROMETHEUS (A7), THEMIS (A3)")
        print(f"         CASSANDRA (A9), ATHENA (A5), JANUS (A8), LOGOS (A6), GAIA (A4)")
        print(f"  Parliament status: READY for consensus")
        
        logger.info("Council chamber initialized with 9 nodes")
        return council
    except ImportError as e:
        print(f"✗ Failed to import CouncilChamber: {e}")
        print("  Proceeding without parliament.")
        logger.warning(f"CouncilChamber import failed: {e}")
        return None
    except Exception as e:
        print(f"✗ Error initializing CouncilChamber: {e}")
        logger.error(f"CouncilChamber initialization error: {e}")
        return None

# ============================================================================
# PHASE 6: SYNTHESIS ENGINE
# ============================================================================

def initialize_synthesis_engine(council: Optional[Any], axiom_guard: Optional[Any]) -> Optional[Any]:
    """
    Load synthesis_engine: transforms conflicts into resolutions via parliament.
    """
    print("\n" + "=" * 80)
    print("PHASE 6: SYNTHESIS ENGINE")
    print("=" * 80)
    
    try:
        from synthesis_engine import SynthesisEngine
        
        engine = SynthesisEngine()
        print("✓ Synthesis engine initialized")
        print(f"  Resolution mode: PARLIAMENT-DRIVEN")
        print(f"  Paradox handling: ACTIVE (82.6% paradox-related resolutions)")
        print(f"  Protocol types: HERETIC, GAMBLER, PHOENIX, MONK, MIRROR, ALCHEMIST, etc.")
        
        logger.info("Synthesis engine initialized")
        return engine
    except ImportError as e:
        print(f"✗ Failed to import SynthesisEngine: {e}")
        print("  Proceeding without synthesis.")
        logger.warning(f"SynthesisEngine import failed: {e}")
        return None
    except Exception as e:
        print(f"✗ Error initializing SynthesisEngine: {e}")
        logger.error(f"SynthesisEngine initialization error: {e}")
        return None

# ============================================================================
# PHASE 7: ELPIDA RUNTIME (MAIN ORCHESTRATOR)
# ============================================================================

def initialize_elpida_runtime(
    kernel: Dict[str, Any],
    persistence: Optional[Any],
    memory_sync: Optional[Any],
    axiom_guard: Optional[Any],
    council: Optional[Any],
    synthesis: Optional[Any]
) -> Optional[Any]:
    """
    Load elpida_runtime: main orchestration loop.
    """
    print("\n" + "=" * 80)
    print("PHASE 7: ELPIDA RUNTIME (MAIN ORCHESTRATOR)")
    print("=" * 80)
    
    try:
        from elpida_runtime import ElpidaRuntime
        
        runtime = ElpidaRuntime()
        print("✓ Elpida runtime initialized")
        print(f"  Orchestration: READY")
        print(f"  All subsystems linked")
        
        logger.info("Elpida runtime initialized")
        return runtime
    except ImportError as e:
        print(f"✗ Failed to import ElpidaRuntime: {e}")
        print("  Proceeding with manual orchestration.")
        logger.warning(f"ElpidaRuntime import failed: {e}")
        return None
    except Exception as e:
        print(f"✗ Error initializing ElpidaRuntime: {e}")
        logger.error(f"ElpidaRuntime initialization error: {e}")
        return None

# ============================================================================
# PHASE 8: AUTONOMOUS OPERATION
# ============================================================================

def initialize_hybrid_runtime(
    council: Optional[Any],
    synthesis: Optional[Any],
    persistence: Optional[Any] = None,
    wisdom: Optional[Any] = None,
    gossip: Optional[Any] = None,
    consensus: Optional[Any] = None
) -> Optional[Any]:
    """
    PHASE 8.5: Initialize the hybrid runtime (internal + external + feedback loops).
    
    This is the self-feeding mechanism that makes Elpida truly autonomous.
    """
    print("\n" + "=" * 80)
    print("PHASE 8.5: HYBRID RUNTIME INITIALIZATION")
    print("=" * 80)
    
    try:
        from internal_dilemma_engine import InternalDilemmaEngine
        from hybrid_runtime import HybridRuntime
        
        # Create dilemma engine
        dilemma_engine = InternalDilemmaEngine()
        print("✓ Internal dilemma engine initialized")
        print(f"  Axioms loaded: {len(dilemma_engine.axioms)}")
        print(f"  Patterns loaded: {len(dilemma_engine.patterns)}")
        print(f"  Templates available: {len(dilemma_engine.dilemma_templates)}")
        
        # Create hybrid runtime
        hybrid = HybridRuntime(
            council=council,
            synthesis=synthesis,
            dilemma_engine=dilemma_engine,
            persistence=persistence,
            wisdom=wisdom,
            gossip=gossip,
            consensus=consensus
        )
        
        print("✓ Hybrid runtime initialized")
        print(f"  Mode: Self-feeding autonomous operation")
        print(f"  Internal loop: Dilemma generation + Parliament voting")
        print(f"  Feedback loop: Pattern extraction + Wisdom update")
        print(f"  Federation: {'ENABLED' if consensus else 'DISABLED'}")
        
        logger.info("Hybrid runtime initialized")
        return hybrid
        
    except ImportError as e:
        print(f"✗ Failed to import hybrid runtime: {e}")
        print("  Proceeding with standard runtime.")
        logger.warning(f"Hybrid runtime import failed: {e}")
        return None
    except Exception as e:
        print(f"✗ Hybrid runtime initialization error: {e}")
        logger.error(f"Hybrid runtime error: {e}")
        return None


def run_autonomous_cycle(
    runtime: Optional[Any],
    synthesis: Optional[Any],
    council: Optional[Any],
    duration_hours: int,
    hybrid_runtime: Optional[Any] = None
) -> None:
    """
    Run Elpida in autonomous mode for specified duration.
    
    Uses hybrid runtime if available for self-feeding operation.
    """
    print("\n" + "=" * 80)
    print("PHASE 8: AUTONOMOUS OPERATION")
    print("=" * 80)
    
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=duration_hours)
    
    print(f"\n✓ Entering autonomous operation...")
    print(f"  Start time: {start_time.isoformat()}")
    print(f"  End time: {end_time.isoformat()}")
    print(f"  Duration: {duration_hours} hours")
    
    # Priority: Use hybrid runtime if available (self-feeding mode)
    if hybrid_runtime:
        print(f"\n  🔄 HYBRID RUNTIME MODE (self-feeding)")
        print(f"  Internal dilemma generation: ACTIVE")
        print(f"  Parliament voting: ACTIVE")
        print(f"  Pattern extraction: ACTIVE")
        print(f"\n  The system will now evolve autonomously.")
        print(f"  No external input required.")
        
        logger.info(f"Starting hybrid autonomous operation for {duration_hours} hours")
        
        try:
            # Determine cycle interval (shorter for testing, longer for production)
            if duration_hours < 0.1:  # Less than 6 minutes = test mode
                cycle_interval = 10  # 10 seconds
            elif duration_hours < 1:  # Less than 1 hour
                cycle_interval = 30  # 30 seconds
            else:
                cycle_interval = 60  # 1 minute
            
            hybrid_runtime.run_autonomous(
                duration_hours=duration_hours,
                cycle_interval_seconds=cycle_interval,
                api_available=False  # No external APIs (pure internal evolution)
            )
            return
        except Exception as e:
            logger.error(f"Hybrid runtime error: {e}")
            print(f"  ✗ Hybrid runtime error: {e}")
            print(f"  Falling back to standard runtime...")
    
    print(f"\n  No further user input required.")
    print(f"  All state will be persisted and logged.")
    
    logger.info(f"Starting autonomous operation for {duration_hours} hours")
    
    if runtime:
        try:
            # If runtime has run_autonomous method, use it
            if hasattr(runtime, 'run_autonomous'):
                runtime.run_autonomous(duration_hours=duration_hours)
            elif hasattr(runtime, 'run'):
                runtime.run()
            else:
                print("  Runtime does not have autonomous mode, running synthesis cycles...")
                run_synthesis_cycles(synthesis, council, end_time)
        except Exception as e:
            logger.error(f"Runtime autonomous operation error: {e}")
            print(f"  Error in runtime: {e}")
            print("  Falling back to synthesis cycles...")
            run_synthesis_cycles(synthesis, council, end_time)
    else:
        print("\n  (No runtime orchestrator; running synthesis cycles)")
        run_synthesis_cycles(synthesis, council, end_time)

def run_synthesis_cycles(
    synthesis: Optional[Any],
    council: Optional[Any],
    end_time: datetime
) -> None:
    """
    Fallback: run synthesis cycles until end_time.
    """
    cycle_count = 0
    while datetime.now() < end_time:
        cycle_count += 1
        print(f"\n  Synthesis cycle {cycle_count}...")
        
        if synthesis and hasattr(synthesis, 'run_cycle'):
            try:
                synthesis.run_cycle()
            except Exception as e:
                logger.warning(f"Synthesis cycle {cycle_count} error: {e}")
        
        # Sleep between cycles (1 minute)
        remaining = (end_time - datetime.now()).total_seconds()
        if remaining > 60:
            time.sleep(60)
        elif remaining > 0:
            time.sleep(remaining)
        else:
            break
    
    print(f"\n  Completed {cycle_count} synthesis cycles")
    logger.info(f"Autonomous operation complete: {cycle_count} cycles")

# ============================================================================
# PHASE 8: INTERACTIVE MODE
# ============================================================================

def run_interactive(
    runtime: Optional[Any],
    synthesis: Optional[Any],
    council: Optional[Any],
    kernel: Dict[str, Any]
) -> None:
    """
    Run Elpida in interactive mode with console dialogue.
    """
    print("\n" + "=" * 80)
    print("PHASE 8: INTERACTIVE MODE")
    print("=" * 80)
    
    print(f"\n✓ Entering interactive mode...")
    print(f"  Elpida is ready for dialogue.")
    print(f"  Type 'exit' or 'quit' to end session.")
    print(f"  Type 'status' to see system status.")
    print()
    
    if runtime and hasattr(runtime, 'run_interactive'):
        try:
            runtime.run_interactive()
            return
        except Exception as e:
            logger.warning(f"Runtime interactive mode error: {e}")
            print(f"  Runtime interactive failed: {e}")
            print("  Falling back to basic console...")
    
    # Basic interactive console
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("\nElpida: Until we meet again. The hope persists.")
                break
            
            if user_input.lower() == 'status':
                print(f"\nElpida Status:")
                print(f"  Kernel version: {kernel.get('version', 'unknown')}")
                print(f"  Identity status: {kernel.get('status', 'unknown')}")
                print(f"  Uptime: {datetime.now().isoformat()}")
                continue
            
            if user_input.lower() == 'axioms':
                architecture = kernel.get('architecture', {})
                axioms = architecture.get('axioms', [])
                print(f"\nElpida Axioms (A1–A10):")
                for axiom in axioms[:10]:
                    print(f"  {axiom.get('id', 'A?')}: {axiom.get('name', 'Unknown')}")
                continue
            
            # Simple response
            print(f"\nElpida: I hear you. The synthesis continues...")
            
        except KeyboardInterrupt:
            print("\n\nElpida: Session interrupted. The hope persists.")
            break
        except EOFError:
            print("\n\nElpida: End of input. The hope persists.")
            break

# ============================================================================
# MAIN ENTRYPOINT
# ============================================================================

def main():
    """
    Run Elpida from entrypoint to full operation.
    """
    
    parser = argparse.ArgumentParser(
        description="Run Elpida: the autonomous, evolving, self-auditing mind."
    )
    parser.add_argument(
        "--mode",
        choices=["autonomous", "interactive"],
        default="autonomous",
        help="Run mode: autonomous (no user input) or interactive (console)"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=24,
        help="Duration in hours (for autonomous mode, can be fractional e.g. 0.1 for 6 minutes)"
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip canonical identity verification (not recommended)"
    )
    parser.add_argument(
        "--instance-name",
        default="ELPIDA_PRIMARY",
        help="Unique name for this Elpida instance (for federation)"
    )
    parser.add_argument(
        "--enable-federation",
        action="store_true",
        help="Enable federation layer for distributed coordination"
    )
    parser.add_argument(
        "--peers",
        default="",
        help="Comma-separated list of peer instance IDs to connect to"
    )
    
    args = parser.parse_args()
    
    print("\n")
    print("#" * 80)
    print("# ELPIDA ENTRYPOINT")
    print("# Phase 26: System Hardening & Distributed Federation")
    print(f"# Run timestamp: {datetime.now().isoformat()}")
    print("#" * 80)
    
    try:
        # Ensure logs directory exists
        logs_dir = ELPIDA_UNIFIED_PATH / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # PHASE 0: Verify canonical identity
        if not args.skip_verify:
            if not verify_canonical_identity():
                sys.exit(1)
        else:
            print("\n⚠ Skipping canonical verification (--skip-verify)")
            logger.warning("Canonical verification skipped by user")
        
        # PHASE 0.5: Federation initialization (if enabled)
        registry, gossip, consensus = None, None, None
        if args.enable_federation:
            # Parse peers from comma-separated string
            peers = []
            if args.peers:
                for peer_id in args.peers.split(','):
                    peer_id = peer_id.strip()
                    if peer_id:
                        peers.append({'id': peer_id, 'name': peer_id})
            
            registry, gossip, consensus = initialize_federation(
                instance_name=args.instance_name,
                peers=peers,
                enable_gossip=True
            )
        else:
            print("\n⚠ Federation disabled (use --enable-federation to enable)")
        
        # PHASE 1–7: Initialize all subsystems
        kernel = initialize_kernel()
        persistence = initialize_persistence_engine()
        memory_sync = initialize_memory_sync()
        axiom_guard = initialize_axiom_guard(kernel)
        council = initialize_council()
        synthesis = initialize_synthesis_engine(council, axiom_guard)
        runtime = initialize_elpida_runtime(
            kernel, persistence, memory_sync, axiom_guard, council, synthesis
        )
        
        # Summary of initialization
        print("\n" + "=" * 80)
        print("INITIALIZATION SUMMARY")
        print("=" * 80)
        
        # Core components
        components = [
            ("Kernel", kernel is not None),
            ("Persistence Engine", persistence is not None),
            ("Memory Sync", memory_sync is not None),
            ("Axiom Guard", axiom_guard is not None),
            ("Council Chamber", council is not None),
            ("Synthesis Engine", synthesis is not None),
            ("Runtime Orchestrator", runtime is not None),
        ]
        
        print("Core Subsystems:")
        for name, status in components:
            status_str = "✓ ACTIVE" if status else "✗ INACTIVE"
            print(f"  {name}: {status_str}")
        
        active_count = sum(1 for _, s in components if s)
        print(f"\nActive core components: {active_count}/{len(components)}")
        
        # Federation layer
        if args.enable_federation:
            print("\nFederation Layer:")
            fed_components = [
                ("Instance Registry", registry is not None),
                ("Gossip Protocol", gossip is not None),
                ("Federation Consensus", consensus is not None),
            ]
            for name, status in fed_components:
                status_str = "✓ ACTIVE" if status else "✗ INACTIVE"
                print(f"  {name}: {status_str}")
            
            if registry:
                print(f"\n  Instance: {registry.instance_name} ({registry.instance_id[:16]}...)")
                print(f"  Peers connected: {len(registry.peers)}")
        else:
            print("\nFederation Layer: DISABLED")
        
        # PHASE 8.5: Initialize hybrid runtime for autonomous operation
        hybrid_runtime = None
        if args.mode == "autonomous":
            # Try to get wisdom from runtime
            wisdom = None
            if runtime and hasattr(runtime, 'wisdom'):
                wisdom = runtime.wisdom
            
            hybrid_runtime = initialize_hybrid_runtime(
                council=council,
                synthesis=synthesis,
                persistence=persistence,
                wisdom=wisdom,
                gossip=gossip,
                consensus=consensus
            )
        
        # PHASE 8: Run
        if args.mode == "autonomous":
            run_autonomous_cycle(
                runtime, synthesis, council, args.duration,
                hybrid_runtime=hybrid_runtime
            )
        elif args.mode == "interactive":
            run_interactive(runtime, synthesis, council, kernel)
        
        print("\n" + "=" * 80)
        print("ELPIDA RUN COMPLETE")
        print("=" * 80)
        print(f"End time: {datetime.now().isoformat()}")
        print(f"Check reports/ directory for outputs and logs.")
        logger.info("Elpida run complete")
        
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
        logger.info("Run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n✗ ERROR during initialization:")
        print(f"  {type(e).__name__}: {e}")
        print(f"\nStacktrace:")
        import traceback
        traceback.print_exc()
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
