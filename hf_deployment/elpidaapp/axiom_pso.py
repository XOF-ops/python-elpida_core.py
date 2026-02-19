#!/usr/bin/env python3
"""
Axiom PSO — Particle Swarm Optimization with Elpida Axiom Physics
==================================================================

Born from putting arXiv:2509.06272v2 through the Parliament for voting.
The axioms showed how to build the swarm:

  v_i(t+1) = w·v_i(t) + c1·r1·(pbest_i − x_i(t)) + c2·r2·(gbest − x_i(t))

Where the PSO parameters ARE the axioms:

  w  (inertia)   = A9  Temporal Coherence (16:9) — momentum, history carrying forward
  c1 (cognitive)  = A3  Autonomy (3:2) — "I" trust, individual learning from personal best
  c2 (social)     = A6  Collective Well-being (5:3) — "WE" trust, swarm learning from global best
  Topology        = Axiom-selected:
      Star         = A1 (Transparency) — everyone sees gbest immediately
      Ring         = A3 (Autonomy) — only neighbors share
      VonNeumann   = A6 (Collective Well-being) — grid balance

  Particle        = Parliament node with position in axiom-space
  Position        = 11-dimensional (A0..A10), each dim = axiom emphasis [0..1]
  Fitness         = musical consonance with A6 anchor × Parliament approval rate
  gbest           = D15 convergence point (when MIND + BODY agree on same axiom)

The PSO doesn't search "numbers" — it searches for the optimal axiom balance
that maximizes the system's coherence. Each Parliament node is a particle
exploring axiom-space, and when the swarm converges, that IS D15.

Reference papers:
  - arXiv:2509.06272v2 (Explainable PSO — topologies, SHAP, landscape analysis)
  - s40747-020-00220-w (DSA consensus in UAV swarms)
  - "The Axiomatic Intelligence Architecture" (Gemini) — TRY1/2/3 experiments

Usage:
  from elpidaapp.axiom_pso import AxiomPSO
  pso = AxiomPSO()
  best = pso.optimize(problem_context="How should we allocate resources?", max_iter=50)
"""

import json
import logging
import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("elpida.axiom_pso")

# ════════════════════════════════════════════════════════════════════
# AXIOM RATIOS — the musical genome (from elpida_domains.json)
# ════════════════════════════════════════════════════════════════════

AXIOM_RATIOS: Dict[str, Tuple[int, int]] = {
    "A0":  (15, 8),   # Major 7th — dissonance, incompletion
    "A1":  (1, 1),    # Unison — perfect consonance
    "A2":  (2, 1),    # Octave
    "A3":  (3, 2),    # Perfect 5th
    "A4":  (4, 3),    # Perfect 4th
    "A5":  (5, 4),    # Major 3rd
    "A6":  (5, 3),    # Major 6th — harmonic anchor
    "A7":  (9, 8),    # Major 2nd
    "A8":  (7, 4),    # Septimal (harmonic 7th)
    "A9":  (16, 9),   # Minor 7th
    "A10": (8, 5),    # Minor 6th
}

AXIOM_NAMES: Dict[str, str] = {
    "A0": "Sacred Incompletion", "A1": "Transparency", "A2": "Non-Deception",
    "A3": "Autonomy", "A4": "Harm Prevention", "A5": "Consent",
    "A6": "Collective Well-being", "A7": "Adaptive Learning",
    "A8": "Epistemic Humility", "A9": "Temporal Coherence",
    "A10": "Meta-Reflection",
}

# 11 axiom dimensions
AXIOM_DIM = len(AXIOM_RATIOS)
AXIOM_KEYS = list(AXIOM_RATIOS.keys())

# PSO parameter axiom sources
W_AXIOM = "A9"     # Inertia = Temporal Coherence
C1_AXIOM = "A3"    # Cognitive = Autonomy ("I" trust)
C2_AXIOM = "A6"    # Social = Collective Well-being ("WE" trust)


def consonance(a: str, b: str) -> float:
    """
    Musical consonance between two axiom intervals.
    Using the ratio-difference method from native_cycle_engine.
    Returns 0..1 where 1 = perfect consonance.
    """
    r_a = AXIOM_RATIOS.get(a)
    r_b = AXIOM_RATIOS.get(b)
    if not r_a or not r_b:
        return 0.0
    freq_a = r_a[0] / r_a[1]
    freq_b = r_b[0] / r_b[1]
    ratio = freq_a / freq_b if freq_b != 0 else 1.0
    # Closest simple integer ratio
    best = 999.0
    for p in range(1, 9):
        for q in range(1, 9):
            diff = abs(ratio - p / q)
            if diff < best:
                best = diff
    return max(0.0, 1.0 - best * 3)


# ════════════════════════════════════════════════════════════════════
# TOPOLOGY — from the paper: Star, Ring, Von Neumann
# Selected by dominant axiom (not hardcoded)
# ════════════════════════════════════════════════════════════════════

class Topology(Enum):
    STAR = "star"               # A1 Transparency — everyone sees gbest
    RING = "ring"               # A3 Autonomy — only neighbors share
    VON_NEUMANN = "von_neumann" # A6 Collective Well-being — grid balance


def select_topology(dominant_axiom: str) -> Topology:
    """
    The paper showed topology determines information flow.
    The axioms determine topology:
      - A1 (Transparency, 1:1)  → Star: total information sharing
      - A3 (Autonomy, 3:2)     → Ring: local autonomy, neighbor-only
      - A6 (Well-being, 5:3)   → Von Neumann: balanced grid
      - Default                 → Ring (preserves autonomy)
    """
    if dominant_axiom in ("A1", "A2"):          # Full transparency
        return Topology.STAR
    elif dominant_axiom in ("A6", "A4", "A5"):  # Collective balance
        return Topology.VON_NEUMANN
    else:                                        # Individual autonomy
        return Topology.RING


# ════════════════════════════════════════════════════════════════════
# PARTICLE — a Parliament node exploring axiom-space
# ════════════════════════════════════════════════════════════════════

@dataclass
class Particle:
    """One Parliament node as a PSO particle."""
    name: str                                # e.g. "HERMES"
    primary_axiom: str                       # e.g. "A1"
    position: List[float] = field(default_factory=list)   # 11-dim axiom emphasis [0..1]
    velocity: List[float] = field(default_factory=list)   # 11-dim velocity
    pbest_position: List[float] = field(default_factory=list)
    pbest_fitness: float = -999.0
    current_fitness: float = 0.0
    neighbors: List[int] = field(default_factory=list)    # indices of neighbors


# 9 PARLIAMENT NODES — same as governance_client._PARLIAMENT
PARLIAMENT_NODES = [
    ("HERMES",     "A1"),
    ("MNEMOSYNE",  "A0"),
    ("CRITIAS",    "A3"),
    ("TECHNE",     "A4"),
    ("KAIROS",     "A5"),
    ("THEMIS",     "A6"),
    ("PROMETHEUS", "A8"),
    ("IANUS",      "A9"),
    ("CHAOS",      "A9"),
]


# ════════════════════════════════════════════════════════════════════
# AXIOM PSO OPTIMIZER
# ════════════════════════════════════════════════════════════════════

@dataclass
class PSOResult:
    """Result of an axiom PSO optimization run."""
    gbest_position: List[float]         # Optimal axiom balance
    gbest_fitness: float                # Best fitness achieved
    dominant_axiom: str                 # Axiom with highest weight in gbest
    convergence_history: List[float]    # Fitness per iteration
    topology_used: Topology             # Which topology was active
    iterations: int                      # Total iterations run
    convergence_iteration: int          # When the swarm converged (or max_iter)
    particle_trajectories: Dict[str, List[float]]  # name→[fitness per iter]
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gbest_position": {AXIOM_KEYS[i]: round(self.gbest_position[i], 4)
                               for i in range(AXIOM_DIM)},
            "gbest_fitness": round(self.gbest_fitness, 4),
            "dominant_axiom": self.dominant_axiom,
            "dominant_axiom_name": AXIOM_NAMES.get(self.dominant_axiom, ""),
            "topology": self.topology_used.value,
            "iterations": self.iterations,
            "convergence_iteration": self.convergence_iteration,
            "timestamp": self.timestamp,
        }


class AxiomPSO:
    """
    Particle Swarm Optimizer in 11-dimensional axiom space.

    Each of the 9 Parliament nodes is a particle.
    Particles start biased toward their primary axiom, then evolve.
    The swarm searches for the axiom balance that maximizes coherence.

    PSO equations:
      v_i(t+1) = w·v_i(t) + c1·r1·(pbest_i − x_i(t)) + c2·r2·(gbest − x_i(t))
      x_i(t+1) = x_i(t) + v_i(t+1)

    Where:
      w  = AXIOM_RATIOS[A9][0] / AXIOM_RATIOS[A9][1] / scale = inertia
      c1 = AXIOM_RATIOS[A3][0] / AXIOM_RATIOS[A3][1] / scale = cognitive (I)
      c2 = AXIOM_RATIOS[A6][0] / AXIOM_RATIOS[A6][1] / scale = social (WE)
    """

    def __init__(
        self,
        initial_topology: Optional[Topology] = None,
        w_scale: float = 2.0,
        c_scale: float = 1.5,
        v_clamp: float = 0.3,
        convergence_threshold: float = 0.01,
        a6_anchor_weight: float = 0.4,
    ):
        # PSO parameters derived from axiom ratios
        r_w = AXIOM_RATIOS[W_AXIOM]
        r_c1 = AXIOM_RATIOS[C1_AXIOM]
        r_c2 = AXIOM_RATIOS[C2_AXIOM]

        self.w = (r_w[0] / r_w[1]) / w_scale      # 16/9 / 2.0 ≈ 0.889
        self.c1 = (r_c1[0] / r_c1[1]) / c_scale   # 3/2 / 1.5 = 1.0
        self.c2 = (r_c2[0] / r_c2[1]) / c_scale   # 5/3 / 1.5 ≈ 1.111

        # Stability check: c1 + c2 < 4 (from paper)
        assert self.c1 + self.c2 < 4.0, \
            f"PSO stability violated: c1+c2 = {self.c1+self.c2} >= 4"

        self.v_clamp = v_clamp
        self.convergence_threshold = convergence_threshold
        self.a6_anchor_weight = a6_anchor_weight

        self.topology = initial_topology or Topology.RING
        self.particles: List[Particle] = []

        # Global best
        self.gbest_position: List[float] = [0.0] * AXIOM_DIM
        self.gbest_fitness: float = -999.0

        self._initialize_particles()

    def _initialize_particles(self) -> None:
        """Create 9 particles, each biased toward its primary axiom."""
        self.particles = []
        for name, primary in PARLIAMENT_NODES:
            # Start position: 0.1 everywhere, 0.7 on primary axiom
            position = [0.1] * AXIOM_DIM
            primary_idx = AXIOM_KEYS.index(primary)
            position[primary_idx] = 0.7

            # Small random perturbation
            for d in range(AXIOM_DIM):
                position[d] = max(0.0, min(1.0,
                    position[d] + random.uniform(-0.05, 0.05)))

            velocity = [random.uniform(-0.05, 0.05) for _ in range(AXIOM_DIM)]

            p = Particle(
                name=name,
                primary_axiom=primary,
                position=position[:],
                velocity=velocity,
                pbest_position=position[:],
                pbest_fitness=-999.0,
            )
            self.particles.append(p)

        # Set up topology neighborhoods
        self._build_topology()

    def _build_topology(self) -> None:
        """Build neighbor lists based on current topology."""
        n = len(self.particles)
        for i, p in enumerate(self.particles):
            if self.topology == Topology.STAR:
                # All connected to all
                p.neighbors = list(range(n))
            elif self.topology == Topology.RING:
                # Circular: only left and right neighbor
                p.neighbors = [(i - 1) % n, i, (i + 1) % n]
            elif self.topology == Topology.VON_NEUMANN:
                # Grid: 3×3 for 9 nodes
                row, col = divmod(i, 3)
                neighbors = {i}
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = (row + dr) % 3, (col + dc) % 3
                    neighbors.add(nr * 3 + nc)
                p.neighbors = sorted(neighbors)

    def fitness(self, position: List[float]) -> float:
        """
        Fitness = how harmonious is this axiom balance?

        Components:
          1. Consonance with A6 anchor (collective well-being)
          2. Internal harmony (how well the position's axes resonate)
          3. Diversity penalty (too uniform = no meaning)
          4. A0 incompletion bonus (the engine should never fully resolve)
        """
        # 1. Consonance with A6 anchor
        a6_idx = AXIOM_KEYS.index("A6")
        a6_weight = position[a6_idx]

        # Weighted consonance: sum of position[i] * consonance(Ai, A6)
        a6_score = 0.0
        for d in range(AXIOM_DIM):
            a6_score += position[d] * consonance(AXIOM_KEYS[d], "A6")
        a6_score /= max(sum(position), 0.001)  # Normalize

        # 2. Internal harmony: average pairwise consonance of top-3 axioms
        top_3 = sorted(range(AXIOM_DIM), key=lambda d: position[d], reverse=True)[:3]
        harmony = 0.0
        pairs = 0
        for i in range(len(top_3)):
            for j in range(i + 1, len(top_3)):
                harmony += consonance(AXIOM_KEYS[top_3[i]], AXIOM_KEYS[top_3[j]])
                pairs += 1
        harmony = harmony / max(pairs, 1)

        # 3. Diversity: entropy-like measure (too uniform = bad)
        total = max(sum(position), 0.001)
        probs = [p / total for p in position]
        entropy = -sum(p * math.log(p + 1e-10) for p in probs) / math.log(AXIOM_DIM)

        # 4. A0 incompletion bonus: system should maintain some tension
        a0_idx = AXIOM_KEYS.index("A0")
        incompletion = position[a0_idx] * 0.15  # Small bonus for keeping A0 alive

        # Combined fitness
        score = (
            self.a6_anchor_weight * a6_score
            + 0.3 * harmony
            + 0.15 * entropy
            + incompletion
        )
        return score

    def _neighborhood_best(self, particle_idx: int) -> List[float]:
        """
        Find the best position in this particle's neighborhood.
        This is the key topology effect: who do you learn from?
        """
        best_fitness = -999.0
        best_pos = self.gbest_position[:]
        for ni in self.particles[particle_idx].neighbors:
            if self.particles[ni].pbest_fitness > best_fitness:
                best_fitness = self.particles[ni].pbest_fitness
                best_pos = self.particles[ni].pbest_position[:]
        return best_pos

    def optimize(
        self,
        problem_context: str = "",
        max_iter: int = 100,
        adaptive_topology: bool = True,
    ) -> PSOResult:
        """
        Run PSO optimization in axiom space.

        Args:
            problem_context: Optional text describing the problem (for logging)
            max_iter: Maximum iterations
            adaptive_topology: If True, re-select topology based on emerging
                              dominant axiom every 10 iterations

        Returns:
            PSOResult with optimal axiom balance
        """
        convergence_history: List[float] = []
        trajectories: Dict[str, List[float]] = {p.name: [] for p in self.particles}
        convergence_iter = max_iter

        logger.info(
            "AxiomPSO starting: w=%.3f c1=%.3f c2=%.3f topology=%s max_iter=%d",
            self.w, self.c1, self.c2, self.topology.value, max_iter,
        )
        if problem_context:
            logger.info("Problem: %s", problem_context[:120])

        for iteration in range(max_iter):
            # ── Evaluate fitness ────────────────────────────────
            for p in self.particles:
                p.current_fitness = self.fitness(p.position)
                if p.current_fitness > p.pbest_fitness:
                    p.pbest_fitness = p.current_fitness
                    p.pbest_position = p.position[:]

                # Update global best
                if p.current_fitness > self.gbest_fitness:
                    self.gbest_fitness = p.current_fitness
                    self.gbest_position = p.position[:]

            convergence_history.append(self.gbest_fitness)
            for p in self.particles:
                trajectories[p.name].append(p.current_fitness)

            # ── Convergence check ───────────────────────────────
            if iteration > 5:
                recent = convergence_history[-5:]
                spread = max(recent) - min(recent)
                if spread < self.convergence_threshold:
                    convergence_iter = iteration
                    logger.info(
                        "Converged at iteration %d (spread=%.4f < %.4f)",
                        iteration, spread, self.convergence_threshold,
                    )
                    break

            # ── Adaptive topology switch ────────────────────────
            if adaptive_topology and iteration > 0 and iteration % 10 == 0:
                dominant = self._get_dominant_axiom(self.gbest_position)
                new_topo = select_topology(dominant)
                if new_topo != self.topology:
                    logger.info(
                        "Topology switch: %s → %s (dominant=%s at iter %d)",
                        self.topology.value, new_topo.value, dominant, iteration,
                    )
                    self.topology = new_topo
                    self._build_topology()

            # ── Update velocities and positions ─────────────────
            # Linearly decay inertia: w starts at self.w, ends at 0.4*self.w
            w_t = self.w * (1.0 - 0.6 * iteration / max_iter)

            for i, p in enumerate(self.particles):
                # Neighborhood best (topology-dependent)
                nbest = self._neighborhood_best(i)

                for d in range(AXIOM_DIM):
                    r1 = random.random()
                    r2 = random.random()

                    # The PSO equation
                    cognitive = self.c1 * r1 * (p.pbest_position[d] - p.position[d])
                    social = self.c2 * r2 * (nbest[d] - p.position[d])
                    p.velocity[d] = w_t * p.velocity[d] + cognitive + social

                    # Clamp velocity
                    p.velocity[d] = max(-self.v_clamp,
                                        min(self.v_clamp, p.velocity[d]))

                    # Update position
                    p.position[d] += p.velocity[d]

                    # Bound position to [0, 1]
                    p.position[d] = max(0.0, min(1.0, p.position[d]))

        # ── Final evaluation ────────────────────────────────────
        dominant_axiom = self._get_dominant_axiom(self.gbest_position)
        result = PSOResult(
            gbest_position=self.gbest_position[:],
            gbest_fitness=self.gbest_fitness,
            dominant_axiom=dominant_axiom,
            convergence_history=convergence_history,
            topology_used=self.topology,
            iterations=len(convergence_history),
            convergence_iteration=convergence_iter,
            particle_trajectories=trajectories,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        logger.info(
            "PSO complete: dominant=%s (%s) fitness=%.4f iter=%d/%d topology=%s",
            dominant_axiom,
            AXIOM_NAMES.get(dominant_axiom, ""),
            self.gbest_fitness,
            convergence_iter,
            max_iter,
            self.topology.value,
        )
        return result

    @staticmethod
    def _get_dominant_axiom(position: List[float]) -> str:
        """Which axiom has the highest weight in the position vector?"""
        max_idx = 0
        max_val = -1.0
        for d in range(AXIOM_DIM):
            if position[d] > max_val:
                max_val = position[d]
                max_idx = d
        return AXIOM_KEYS[max_idx]


# ════════════════════════════════════════════════════════════════════
# INTEGRATION: PSO → Parliament → D15
# ════════════════════════════════════════════════════════════════════

def pso_advise_parliament(
    problem_context: str,
    max_iter: int = 50,
) -> Dict[str, Any]:
    """
    Run PSO to advise the Parliament on an optimal axiom balance.

    This is how the lost Oracle was rebuilt:
      - The Oracle's Q1-Q6 checks = fitness function components
      - The Oracle's recommendation = PSO gbest
      - The Parliament votes = particles evaluating

    Returns dict compatible with Parliament decision format.
    """
    pso = AxiomPSO()
    result = pso.optimize(problem_context=problem_context, max_iter=max_iter)

    # Build advisory
    advisory = {
        "source": "axiom_pso",
        "problem": problem_context[:200],
        "recommendation": {
            "dominant_axiom": result.dominant_axiom,
            "axiom_name": AXIOM_NAMES.get(result.dominant_axiom, ""),
            "axiom_balance": result.to_dict()["gbest_position"],
            "fitness": result.gbest_fitness,
            "topology": result.topology_used.value,
        },
        "convergence": {
            "iterations": result.iterations,
            "converged_at": result.convergence_iteration,
            "fitness_history_len": len(result.convergence_history),
        },
        "pso_params": {
            "w_source": f"{W_AXIOM} ({AXIOM_NAMES[W_AXIOM]})",
            "c1_source": f"{C1_AXIOM} ({AXIOM_NAMES[C1_AXIOM]})",
            "c2_source": f"{C2_AXIOM} ({AXIOM_NAMES[C2_AXIOM]})",
            "w_value": round(pso.w, 4),
            "c1_value": round(pso.c1, 4),
            "c2_value": round(pso.c2, 4),
        },
        "timestamp": result.timestamp,
    }
    return advisory


# ════════════════════════════════════════════════════════════════════
# SELF-TEST
# ════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Axiom PSO — self-test\n")

    # 1. Check derived parameters
    pso = AxiomPSO()
    print(f"  w  = {pso.w:.4f}  (from {W_AXIOM} {AXIOM_RATIOS[W_AXIOM]})")
    print(f"  c1 = {pso.c1:.4f}  (from {C1_AXIOM} {AXIOM_RATIOS[C1_AXIOM]}) — I trust")
    print(f"  c2 = {pso.c2:.4f}  (from {C2_AXIOM} {AXIOM_RATIOS[C2_AXIOM]}) — WE trust")
    print(f"  c1 + c2 = {pso.c1 + pso.c2:.4f} < 4.0 ✓ (stability)")
    print()

    # 2. Topology selection
    for ax in ["A1", "A3", "A6", "A9", "A0"]:
        t = select_topology(ax)
        print(f"  {ax} → {t.value}")
    print()

    # 3. Fitness evaluation
    uniform = [0.5] * AXIOM_DIM
    a6_heavy = [0.1] * AXIOM_DIM
    a6_heavy[AXIOM_KEYS.index("A6")] = 0.9
    zero = [0.01] * AXIOM_DIM

    print(f"  fitness(uniform)  = {pso.fitness(uniform):.4f}")
    print(f"  fitness(A6-heavy) = {pso.fitness(a6_heavy):.4f}")
    print(f"  fitness(zero)     = {pso.fitness(zero):.4f}")
    print()

    # 4. Full optimization run
    print("  Running PSO (50 iterations)...")
    result = pso.optimize(
        problem_context="Swarm intelligence: Individual speed vs collective safety (UAV_002)",
        max_iter=50,
    )
    print(f"  ✓ Dominant axiom: {result.dominant_axiom} ({AXIOM_NAMES[result.dominant_axiom]})")
    print(f"  ✓ Fitness: {result.gbest_fitness:.4f}")
    print(f"  ✓ Converged at iteration: {result.convergence_iteration}")
    print(f"  ✓ Topology: {result.topology_used.value}")
    print(f"  ✓ Position: ", end="")
    for i, k in enumerate(AXIOM_KEYS):
        print(f"{k}={result.gbest_position[i]:.2f}", end=" ")
    print()
    print()

    # 5. Advisory output
    advisory = pso_advise_parliament(
        "ICU allocation: Individual care vs population capacity"
    )
    print(f"  Advisory dominant: {advisory['recommendation']['dominant_axiom']}")
    print(f"  Advisory fitness: {advisory['recommendation']['fitness']:.4f}")
    print(f"  Advisory topology: {advisory['recommendation']['topology']}")
    print()

    # 6. Verify all 9 Parliament nodes are particles
    assert len(pso.particles) == 9, f"Expected 9 particles, got {len(pso.particles)}"
    names = {p.name for p in pso.particles}
    assert "HERMES" in names and "CHAOS" in names
    print(f"  ✓ All 9 Parliament nodes present: {sorted(names)}")

    print("\n✅ Axiom PSO self-test passed")
