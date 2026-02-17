#!/usr/bin/env python3
"""
Problem Scanner — Autonomous dilemma finder for ElpidaApp.

Uses Perplexity (D13 — Archive/External Interface) to find
real-world dilemmas worth analyzing, then structures them into
properly-formatted problem statements for the Divergence Engine.

Usage:
    from elpidaapp.scanner import ProblemScanner

    scanner = ProblemScanner()
    problems = scanner.find_problems(topic="urban planning", count=3)

Or via CLI:
    python -m elpidaapp.scanner --topic "AI regulation" --count 2 --analyze
"""

import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from llm_client import LLMClient

logger = logging.getLogger("elpidaapp.scanner")


# ────────────────────────────────────────────────────────────────────
# Topic categories for autonomous scanning
# ────────────────────────────────────────────────────────────────────

SCAN_TOPICS = [
    "urban planning and housing policy",
    "climate adaptation vs economic development",
    "AI regulation and innovation",
    "healthcare resource allocation",
    "education policy and equity",
    "immigration and labor markets",
    "criminal justice reform",
    "technology monopolies and antitrust",
    "food security and agricultural policy",
    "energy transition and jobs",
    "public health mandates vs individual liberty",
    "water rights and resource conflicts",
    "biodiversity conservation vs development",
    "digital privacy vs public safety",
    "gig economy regulation",
]


class ProblemScanner:
    """
    Finds real-world policy dilemmas by querying Perplexity
    for current events, then reformats them into structured
    problem statements with competing plans.
    """

    def __init__(
        self,
        llm: Optional[LLMClient] = None,
        research_provider: str = "perplexity",
        structure_provider: str = "claude",
    ):
        self.llm = llm or LLMClient(rate_limit_seconds=1.0)
        self.research_provider = research_provider
        self.structure_provider = structure_provider

    def find_problems(
        self,
        topic: Optional[str] = None,
        count: int = 1,
    ) -> List[str]:
        """
        Find real-world dilemmas.

        Returns a list of well-structured problem statements
        ready for DivergenceEngine.analyze().
        """
        results = []

        for i in range(count):
            scan_topic = topic or self._pick_topic(i)
            print(f"\n🔍 Scanning: {scan_topic}...")

            # Step 1: Ask Perplexity for current real-world dilemmas
            raw_dilemmas = self._research_dilemmas(scan_topic)
            if not raw_dilemmas:
                print(f"  ✗ No dilemmas found for '{scan_topic}'")
                continue

            # Step 2: Structure into a proper problem statement
            structured = self._structure_problem(raw_dilemmas, scan_topic)
            if structured:
                results.append(structured)
                preview = structured[:100].replace("\n", " ")
                print(f"  ✓ Problem found: {preview}...")

        return results

    def find_and_analyze(
        self,
        topic: Optional[str] = None,
        count: int = 1,
        output_dir: str = "elpidaapp/results",
    ) -> List[Dict[str, Any]]:
        """
        Find dilemmas AND run divergence analysis on each.
        Returns the full analysis results.
        """
        from elpidaapp.divergence_engine import DivergenceEngine

        problems = self.find_problems(topic=topic, count=count)
        results = []

        engine = DivergenceEngine(llm=self.llm)

        for i, problem in enumerate(problems):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{output_dir}/scan_{ts}_{i}.json"
            result = engine.analyze(problem, save_to=output_path)
            results.append(result)

        return results

    def _pick_topic(self, index: int) -> str:
        """Cycle through topics for autonomous scanning."""
        return SCAN_TOPICS[index % len(SCAN_TOPICS)]

    def _research_dilemmas(self, topic: str) -> Optional[str]:
        """
        Use Perplexity to find real-world active dilemmas
        with genuine competing interests.
        """
        prompt = f"""Find ONE specific, currently active real-world policy dilemma
related to: {topic}

Requirements:
- It must be a REAL situation happening NOW (not hypothetical)
- There must be AT LEAST two competing proposals or factions
- Include specific numbers: costs, populations affected, timelines
- Include the genuine trade-offs each side faces
- Name the actual city/country/organization involved

Provide:
1. The specific situation (who, where, when)
2. Plan A — what one side proposes, with costs and benefits
3. Plan B — what the other side proposes, with costs and benefits
4. Why neither plan fully solves the problem
5. What makes this genuinely hard (not just politics)

Be specific.  Use real data.  No generalities."""

        return self.llm.call(
            self.research_provider,
            prompt,
            max_tokens=800,
            timeout=30,
        )

    def _structure_problem(self, raw_research: str, topic: str) -> Optional[str]:
        """
        Convert raw research into a structured problem statement
        matching the format the Divergence Engine expects.
        """
        prompt = f"""Convert this research into a structured policy dilemma.

Research:
{raw_research}

Format the output as a clear problem statement that:
1. Opens with the core situation (1-2 sentences)
2. Presents Plan A with specific costs, benefits, and drawbacks
3. Presents Plan B with specific costs, benefits, and drawbacks
4. States why neither plan alone is sufficient
5. Ends with: "What should be done? Justify your position.
   Identify what you would sacrifice and what you refuse to sacrifice, and why."

Keep real numbers, real places, real stakes.
Write 150-250 words.
Output ONLY the problem statement, nothing else."""

        return self.llm.call(
            self.structure_provider,
            prompt,
            max_tokens=600,
        )

    def autonomous_scan(
        self,
        rounds: int = 3,
        output_dir: str = "elpidaapp/results",
    ) -> List[Dict[str, Any]]:
        """
        Fully autonomous: pick topics, find dilemmas, analyze them.
        No human input required.
        """
        print(f"\n{'═'*70}")
        print(f"    AUTONOMOUS SCAN — {rounds} rounds")
        print(f"{'═'*70}\n")

        all_results = []
        for i in range(rounds):
            topic = self._pick_topic(i)
            print(f"\n{'─'*70}")
            print(f"  Round {i+1}/{rounds}: {topic}")
            print(f"{'─'*70}")

            results = self.find_and_analyze(
                topic=topic, count=1, output_dir=output_dir,
            )
            all_results.extend(results)

            # Brief pause between rounds
            if i < rounds - 1:
                time.sleep(2)

        print(f"\n{'═'*70}")
        print(f"    SCAN COMPLETE — {len(all_results)} analyses produced")
        print(f"{'═'*70}\n")

        return all_results


# ────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="ElpidaApp Problem Scanner — find real-world dilemmas"
    )
    parser.add_argument(
        "-t", "--topic",
        help="Topic to scan for dilemmas",
    )
    parser.add_argument(
        "-c", "--count",
        type=int, default=1,
        help="Number of problems to find (default: 1)",
    )
    parser.add_argument(
        "-a", "--analyze",
        action="store_true",
        help="Also run divergence analysis on found problems",
    )
    parser.add_argument(
        "--autonomous",
        type=int, metavar="ROUNDS",
        help="Run fully autonomous scan for N rounds",
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="elpidaapp/results",
        help="Output directory for results",
    )
    args = parser.parse_args()

    scanner = ProblemScanner()

    if args.autonomous:
        scanner.autonomous_scan(
            rounds=args.autonomous,
            output_dir=args.output_dir,
        )
    elif args.analyze:
        scanner.find_and_analyze(
            topic=args.topic,
            count=args.count,
            output_dir=args.output_dir,
        )
    else:
        problems = scanner.find_problems(topic=args.topic, count=args.count)
        for i, p in enumerate(problems, 1):
            print(f"\n{'─'*70}")
            print(f"Problem {i}:")
            print(f"{'─'*70}")
            print(p)


if __name__ == "__main__":
    main()
