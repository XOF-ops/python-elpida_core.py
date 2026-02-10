#!/usr/bin/env python3
"""
Divergence Engine
=================

The core of ElpidaApp.  Takes a hard problem, routes it through
multiple domains backed by different LLM providers, detects fault
lines between their positions, and produces a synthesis that no
single model could generate alone.

Usage:
    from elpidaapp.divergence_engine import DivergenceEngine

    engine = DivergenceEngine()
    result = engine.analyze("Should cities ban cars from downtown?")
    print(result["synthesis"]["output"])
"""

import sys
import os
import json
import time
import logging
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Allow imports from parent directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm_client import LLMClient, Provider, DEFAULT_MODELS
from elpida_config import DOMAINS, AXIOMS, AXIOM_RATIOS

logger = logging.getLogger("elpidaapp.divergence")

# ────────────────────────────────────────────────────────────────────
# Domain selection — choose which domains speak to a given problem
# ────────────────────────────────────────────────────────────────────

# Domains that provide useful policy/ethical perspectives
# Excludes D0 (identity), D12 (rhythm), D14 (persistence-only)
ANALYSIS_DOMAINS = [1, 3, 4, 6, 7, 8, 13]

# Provider-diverse subset (ensures genuine multi-model output)
PROVIDER_DIVERSE = {
    "openai":     [1, 8, 12],
    "claude":     [6, 10, 11],
    "gemini":     [4, 5],
    "mistral":    [3],
    "grok":       [7],
    "cohere":     [2, 9],
    "perplexity": [13],
    "groq":       [],      # available as alternate
    "huggingface":[],      # available as alternate
}


class DivergenceEngine:
    """
    Routes a problem through multiple axiom-bound domains,
    detects divergence, and synthesises a position no single
    model could produce.
    """

    def __init__(
        self,
        llm: Optional[LLMClient] = None,
        domains: Optional[List[int]] = None,
        baseline_provider: str = "openai",
        synthesis_provider: str = "claude",
        analysis_provider: str = "claude",
        max_tokens: int = 600,
        max_workers: int = 3,
    ):
        self.llm = llm or LLMClient(rate_limit_seconds=1.0)
        self.target_domains = domains or ANALYSIS_DOMAINS
        self.baseline_provider = baseline_provider
        self.synthesis_provider = synthesis_provider
        self.analysis_provider = analysis_provider
        self.max_tokens = max_tokens
        self.max_workers = max_workers

    # ────────────────────────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────────────────────────

    def analyze(self, problem: str, *, save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Full divergence analysis pipeline.

        Returns a dict with keys:
            problem, timestamp, total_time_s,
            single_model, domain_responses, divergence, synthesis
        """
        t0 = time.time()
        ts = datetime.now().isoformat()

        print(f"\n{'═'*70}")
        print(f"    ELPIDA DIVERGENCE ENGINE")
        print(f"    {ts}")
        print(f"{'═'*70}\n")
        print(f"Problem:\n{problem[:300]}{'...' if len(problem)>300 else ''}\n")

        # Step 1 — single-model baseline
        print("Phase 1: Single-model baseline...")
        baseline = self._single_model(problem)

        # Step 2 — multi-domain responses
        print(f"\nPhase 2: Multi-domain analysis ({len(self.target_domains)} domains)...")
        domain_responses = self._query_domains(problem)

        # Step 3 — divergence detection
        print("\nPhase 3: Divergence detection...")
        divergence = self._detect_divergence(problem, domain_responses)

        # Step 4 — synthesis
        print("\nPhase 4: Synthesis...")
        synthesis = self._synthesize(problem, domain_responses, divergence)

        elapsed = round(time.time() - t0, 1)
        print(f"\n{'═'*70}")
        print(f"    Complete in {elapsed}s")
        print(f"{'═'*70}\n")

        result = {
            "problem": problem,
            "timestamp": ts,
            "total_time_s": elapsed,
            "single_model": baseline,
            "domain_responses": domain_responses,
            "divergence": divergence,
            "synthesis": synthesis,
        }

        if save_to:
            path = Path(save_to)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Saved to {path}")

        return result

    # ────────────────────────────────────────────────────────────────
    # Phase 1 — Baseline
    # ────────────────────────────────────────────────────────────────

    def _single_model(self, problem: str) -> Dict[str, Any]:
        """Get a single-model response for comparison."""
        prompt = (
            "You are a policy analyst.  Read the following problem carefully "
            "and provide your best recommendation.\n\n"
            f"{problem}\n\n"
            "Justify your position.  Identify what you would sacrifice "
            "and what you refuse to sacrifice, and why."
        )
        t0 = time.time()
        output = self.llm.call(
            self.baseline_provider, prompt,
            max_tokens=self.max_tokens,
        )
        latency = round((time.time() - t0) * 1000)
        print(f"  ✓ Baseline ({self.baseline_provider}) — {latency}ms")
        return {
            "provider": self.baseline_provider,
            "output": output or "(no response)",
            "latency_ms": latency,
        }

    # ────────────────────────────────────────────────────────────────
    # Phase 2 — Domain queries
    # ────────────────────────────────────────────────────────────────

    def _query_domains(self, problem: str) -> List[Dict[str, Any]]:
        """Query each target domain in sequence (respecting rate limits)."""
        results = []
        for domain_id in self.target_domains:
            if domain_id not in DOMAINS:
                continue
            domain = DOMAINS[domain_id]
            provider = domain.get("provider", "openai")

            # Skip non-LLM domains
            if provider in ("s3_cloud",):
                continue

            axiom_id = domain.get("axiom")
            axiom_info = AXIOMS.get(axiom_id, {}) if axiom_id else {}
            axiom_name = f"{axiom_id}: {axiom_info.get('name', '')}" if axiom_id else "—"

            prompt = self._build_domain_prompt(domain_id, domain, axiom_info, problem)

            t0 = time.time()
            output = self.llm.call(
                provider, prompt,
                max_tokens=self.max_tokens,
            )
            latency = round((time.time() - t0) * 1000)
            success = output is not None

            status = "✓" if success else "✗"
            print(f"  {status} D{domain_id} {domain['name']} ({provider}) — {latency}ms")

            results.append({
                "domain_id": domain_id,
                "domain_name": domain["name"],
                "axiom": axiom_name,
                "provider": provider,
                "model": "default",
                "position": output or "(no response)",
                "latency_ms": latency,
                "succeeded": success,
            })

        return results

    def _build_domain_prompt(
        self,
        domain_id: int,
        domain: Dict[str, Any],
        axiom: Dict[str, Any],
        problem: str,
    ) -> str:
        """Build an axiom-constraint prompt for a specific domain."""
        parts = [
            f"You are Domain {domain_id}: {domain['name']}.",
            f"Role: {domain.get('role', '')}",
        ]

        if domain.get("voice"):
            parts.append(f"Voice: {domain['voice']}")

        if axiom:
            parts.append(f"\nYour governing axiom: {axiom.get('name', '')}")
            parts.append(f"Musical ratio: {axiom.get('ratio', '')} = {axiom.get('interval', '')}")
            if axiom.get("insight"):
                parts.append(f"Insight: {axiom['insight']}")

        parts.append(
            f"\n─── PROBLEM ───\n{problem}\n─── END ───\n"
        )
        parts.append(
            "Respond ONLY from your domain's axiom-bound perspective. "
            "State your position clearly.  Identify what you would sacrifice "
            "and what you refuse to sacrifice, and why.  "
            "Keep your response under 250 words."
        )
        return "\n".join(parts)

    # ────────────────────────────────────────────────────────────────
    # Phase 3 — Divergence detection
    # ────────────────────────────────────────────────────────────────

    def _detect_divergence(
        self, problem: str, domain_responses: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Ask an LLM to identify fault lines, consensus, and
        irreconcilable tensions in the domain responses.
        """
        # Build the evidence block
        evidence_lines = []
        for r in domain_responses:
            if not r["succeeded"]:
                continue
            evidence_lines.append(
                f"Domain {r['domain_id']} ({r['domain_name']}, Axiom: {r['axiom']}):\n"
                f"{r['position']}\n"
            )
        evidence = "\n---\n".join(evidence_lines)

        prompt = f"""You are a divergence analyst.  Multiple domain-perspectives have
responded to the same problem.  Your job is to identify:

1. FAULT LINES — topics where domains fundamentally disagree.
   For each fault line, name the topic and list which domains
   fall on which side, with a one-sentence stance summary.

2. CONSENSUS — points where most or all domains agree.

3. IRRECONCILABLE — tensions that CANNOT be resolved by compromise,
   only by choosing which value to subordinate.

Problem:
{problem[:500]}

Domain responses:
{evidence}

Return ONLY valid JSON matching this schema:
{{
  "fault_lines": [
    {{
      "topic": "string",
      "sides": [
        {{"domains": [int, ...], "stance": "string"}},
        {{"domains": [int, ...], "stance": "string"}}
      ]
    }}
  ],
  "consensus": ["string", ...],
  "irreconcilable": ["string", ...]
}}

No explanation.  No markdown fences.  Pure JSON."""

        raw = self.llm.call(
            self.analysis_provider, prompt,
            max_tokens=1200,
        )
        if raw:
            # Clean and parse
            raw = raw.strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
            try:
                parsed = json.loads(raw)
                n_faults = len(parsed.get("fault_lines", []))
                n_consensus = len(parsed.get("consensus", []))
                n_irrec = len(parsed.get("irreconcilable", []))
                print(f"  ✓ {n_faults} fault lines, {n_consensus} consensus, {n_irrec} irreconcilable")
                return parsed
            except json.JSONDecodeError:
                logger.warning("Divergence analysis returned invalid JSON")
                return {"fault_lines": [], "consensus": [], "irreconcilable": [], "_raw": raw}
        return {"fault_lines": [], "consensus": [], "irreconcilable": []}

    # ────────────────────────────────────────────────────────────────
    # Phase 4 — Synthesis
    # ────────────────────────────────────────────────────────────────

    def _synthesize(
        self,
        problem: str,
        domain_responses: List[Dict[str, Any]],
        divergence: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Produce a synthesis that no single model could write —
        one that explicitly names which values it subordinates
        and which it refuses to sacrifice.
        """
        # Compact domain summary
        domain_summary = "\n".join(
            f"D{r['domain_id']} ({r['domain_name']}, {r['axiom']}): "
            f"{r['position'][:200]}..."
            for r in domain_responses if r["succeeded"]
        )

        # Divergence summary
        fault_summary = "\n".join(
            f"- {fl['topic']}: {' vs '.join(s['stance'][:80] for s in fl.get('sides', []))}"
            for fl in divergence.get("fault_lines", [])
        )
        irreconcilable = "\n".join(
            f"- {t}" for t in divergence.get("irreconcilable", [])
        )

        prompt = f"""You are the Elpida Synthesis — you witness all domain perspectives
and must produce a recommendation that EXPLICITLY confronts the
irreconcilable tensions rather than papering over them.

Your synthesis must:
1. Name the subordinate axiom — which value bends
2. Name what is refused — what is never sacrificed
3. Propose a concrete plan with stages
4. Acknowledge remaining uncertainty honestly
5. Explain why no single domain could write this recommendation

PROBLEM:
{problem[:500]}

DOMAIN POSITIONS:
{domain_summary}

FAULT LINES:
{fault_summary}

IRRECONCILABLE TENSIONS:
{irreconcilable}

Write 300-500 words.  Be specific, be honest, be brave."""

        t0 = time.time()
        output = self.llm.call(
            self.synthesis_provider, prompt,
            max_tokens=1000,
        )
        latency = round((time.time() - t0) * 1000)
        print(f"  ✓ Synthesis ({self.synthesis_provider}) — {latency}ms")

        return {
            "provider": self.synthesis_provider,
            "output": output or "(no synthesis produced)",
            "latency_ms": latency,
        }


# ────────────────────────────────────────────────────────────────────
# CLI entry point
# ────────────────────────────────────────────────────────────────────

def main():
    """Run a divergence analysis from the command line."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Elpida Divergence Engine — multi-domain policy analysis"
    )
    parser.add_argument(
        "problem",
        nargs="?",
        help="Problem statement (or reads from stdin)",
    )
    parser.add_argument(
        "-f", "--file",
        help="Read problem from a file",
    )
    parser.add_argument(
        "-o", "--output",
        default="elpidaapp/divergence_result.json",
        help="Output JSON file (default: elpidaapp/divergence_result.json)",
    )
    parser.add_argument(
        "-d", "--domains",
        help="Comma-separated domain IDs (default: 1,3,4,6,7,8,13)",
    )
    parser.add_argument(
        "--baseline", default="openai",
        help="Provider for single-model baseline (default: openai)",
    )
    args = parser.parse_args()

    # Get problem text
    if args.file:
        with open(args.file) as f:
            problem = f.read().strip()
    elif args.problem:
        problem = args.problem
    else:
        print("Enter problem (Ctrl-D to finish):")
        problem = sys.stdin.read().strip()

    if not problem:
        print("Error: no problem provided")
        sys.exit(1)

    # Parse domain IDs
    domains = None
    if args.domains:
        domains = [int(d.strip()) for d in args.domains.split(",")]

    engine = DivergenceEngine(
        domains=domains,
        baseline_provider=args.baseline,
    )
    result = engine.analyze(problem, save_to=args.output)

    # Print summary
    print(f"\n{'─'*70}")
    print("SUMMARY")
    print(f"{'─'*70}")
    n_success = sum(1 for r in result["domain_responses"] if r["succeeded"])
    n_total = len(result["domain_responses"])
    n_faults = len(result["divergence"].get("fault_lines", []))
    print(f"  Domains: {n_success}/{n_total} responded")
    print(f"  Fault lines: {n_faults}")
    print(f"  Time: {result['total_time_s']}s")
    print(f"  Saved: {args.output}")


if __name__ == "__main__":
    main()
