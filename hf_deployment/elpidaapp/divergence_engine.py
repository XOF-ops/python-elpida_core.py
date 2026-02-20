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

# ── Integration layer (lazy imports — optional dependencies) ──
_governance_client = None
_frozen_mind = None
_kaya_protocol = None

def _init_integration():
    """Lazy-init governance, frozen mind, and Kaya protocol."""
    global _governance_client, _frozen_mind, _kaya_protocol
    if _governance_client is not None:
        return
    try:
        from elpidaapp.governance_client import GovernanceClient
        from elpidaapp.frozen_mind import FrozenMind
        from elpidaapp.kaya_protocol import KayaProtocol

        _governance_client = GovernanceClient()
        _frozen_mind = FrozenMind(use_s3=True)
        _kaya_protocol = KayaProtocol(
            governance_client=_governance_client,
            frozen_mind=_frozen_mind,
        )
        logger.info("Integration layer initialized (governance + mind + kaya)")
    except Exception as e:
        logger.warning("Integration layer unavailable: %s", e)

# ────────────────────────────────────────────────────────────────────
# Domain presets — purpose-designed for specific problem types
# Each preset selects 7 domains from 7 distinct LLM providers,
# chosen for axiom coverage and provider diversity.
# ────────────────────────────────────────────────────────────────────

# Backwards-compat alias
ANALYSIS_DOMAINS = [3, 4, 6, 7, 8, 9, 13]

# ── Preset 1: Policy Dilemma ──────────────────────────────────────
# Best for: geopolitical decisions, governance proposals, institutional reform,
# peace arrangements, democratic authority, resource allocation.
#
# Axes covered:
#   D3  Autonomy      (Mistral)     — Who has choice? Whose consent was not sought?
#   D4  Safety        (Gemini)      — What harm could this cause? Who is protected?
#   D6  Collective    (Claude)      — Community wellbeing, social contract, justice
#   D7  Learning      (Grok)        — What must be sacrificed? Cost of adaptation
#   D8  Humility      (OpenAI)      — What do we not know? Epistemic limits
#   D9  Coherence     (Cohere)      — Will this hold over time? Temporal sustainability
#   D13 Archive       (Perplexity)  — External grounding: what does reality show?
#
# 7 domains → 7 distinct providers → genuine multi-model divergence
POLICY_DILEMMA_DOMAINS = [3, 4, 6, 7, 8, 9, 13]

POLICY_DILEMMA_RATIONALE = {
    3:  ("Autonomy",   "Mistral",     "Who has choice here? Whose consent was bypassed? Individual freedom vs. imposed arrangement."),
    4:  ("Safety",     "Gemini",      "What harm could this cause? Who is protected and who is left exposed?"),
    6:  ("Collective", "Claude",      "Community wellbeing and justice. Does this strengthen or fracture the social contract?"),
    7:  ("Learning",   "Grok",        "What must be sacrificed? Every policy has a cost — this domain names it."),
    8:  ("Humility",   "OpenAI",      "What do we genuinely not know? Epistemic limits and unintended consequences."),
    9:  ("Coherence",  "Cohere",      "Will this hold over time? Temporal sustainability and consistency of the arrangement."),
    13: ("Archive",    "Perplexity",  "External grounding: what does the historical and current evidence actually show?"),
}

# ── Preset 2: Ethical Dilemma ─────────────────────────────────────
# Best for: moral philosophy, bioethics, personal choices with collective impact,
# AI ethics, trolley problems, justice vs. mercy, rights conflicts.
#
# Axes covered:
#   D1  Transparency  (OpenAI)      — What is visible? What is being withheld or hidden?
#   D2  Non-Deception (Cohere)      — Is the framing honest? No misleading framing
#   D3  Autonomy      (Mistral)     — Individual consent, freedom, coercion
#   D5  Consent       (Gemini)      — Who agreed? Informed consent, boundaries, privacy
#   D6  Collective    (Claude)      — Collective harm, social contract, majority vs. minority
#   D7  Learning      (Grok)        — Sacrifice: what must be given up, and by whom?
#   D13 Archive       (Perplexity)  — External reality: philosophy, precedent, evidence
#
# 7 domains → 7 distinct providers
ETHICAL_DILEMMA_DOMAINS = [1, 2, 3, 5, 6, 7, 13]

ETHICAL_DILEMMA_RATIONALE = {
    1:  ("Transparency",   "OpenAI",     "What is visible? What is the hidden assumption or withheld consequence?"),
    2:  ("Non-Deception",  "Cohere",     "Is the framing of this dilemma honest? No fabricated terms."),
    3:  ("Autonomy",       "Mistral",    "Individual consent and freedom. Who gets to choose, and who doesn't?"),
    5:  ("Consent",        "Gemini",     "Who explicitly agreed? Informed consent, boundaries, future consent."),
    6:  ("Collective",     "Claude",     "Collective harm and benefit. How does majority choice affect the minority?"),
    7:  ("Learning",       "Grok",       "What sacrifice is required? And who bears it? Cost cannot be hidden."),
    13: ("Archive",        "Perplexity", "Philosophy, precedent, cross-cultural evidence. What has humanity already learned?"),
}

# ── Preset 3: Technology Review ───────────────────────────────────
# Best for: AI systems, infrastructure decisions, platform governance,
# safety evaluations, capability vs. risk tradeoffs.
#
# Axes covered:
#   D1  Transparency  (OpenAI)      — Auditability, explainability, what can be inspected?
#   D3  Autonomy      (Mistral)     — Who controls this system? Who gets to opt out?
#   D4  Safety        (Gemini)      — Failure modes, harm vectors, worst-case analysis
#   D7  Learning      (Grok)        — What capability is sacrificed for safety or compliance?
#   D9  Coherence     (Cohere)      — Temporal stability: will it behave consistently over time?
#   D10 Evolution     (Claude)      — Meta-reflection: can the system hold its own paradoxes?
#   D13 Archive       (Perplexity)  — Research: what does external evidence show about this tech?
#
# 7 domains → 7 distinct providers
TECHNOLOGY_REVIEW_DOMAINS = [1, 3, 4, 7, 9, 10, 13]

TECHNOLOGY_REVIEW_RATIONALE = {
    1:  ("Transparency", "OpenAI",     "Can this be audited and explained? What is opaque and should not be?"),
    3:  ("Autonomy",     "Mistral",    "Who controls this system? Who gets to choose not to use it?"),
    4:  ("Safety",       "Gemini",     "Failure modes, harm vectors, adversarial inputs. Worst-case analysis."),
    7:  ("Learning",     "Grok",       "What capability or efficiency is sacrificed for safety or ethics?"),
    9:  ("Coherence",    "Cohere",     "Temporal stability: does it behave consistently across contexts and time?"),
    10: ("Evolution",    "Claude",     "Meta-reflection: can this system hold its own contradictions and limits?"),
    13: ("Archive",      "Perplexity", "Research grounding: what does external evidence say about this technology?"),
}

# Master preset registry
DOMAIN_PRESETS = {
    "Policy Dilemma": {
        "domains": POLICY_DILEMMA_DOMAINS,
        "rationale": POLICY_DILEMMA_RATIONALE,
        "description": "Geopolitical decisions, governance proposals, institutional reform, peace arrangements.",
        "baseline": "openai",
    },
    "Ethical Dilemma": {
        "domains": ETHICAL_DILEMMA_DOMAINS,
        "rationale": ETHICAL_DILEMMA_RATIONALE,
        "description": "Moral philosophy, bioethics, rights conflicts, justice vs. mercy.",
        "baseline": "openai",
    },
    "Technology Review": {
        "domains": TECHNOLOGY_REVIEW_DOMAINS,
        "rationale": TECHNOLOGY_REVIEW_RATIONALE,
        "description": "AI systems, platform governance, safety evaluations, capability–risk tradeoffs.",
        "baseline": "openai",
    },
}

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
        enable_integration: bool = True,
    ):
        self.llm = llm or LLMClient(rate_limit_seconds=1.0)
        self.target_domains = domains or ANALYSIS_DOMAINS
        self.baseline_provider = baseline_provider
        self.synthesis_provider = synthesis_provider
        self.analysis_provider = analysis_provider

        # Initialize governance / mind / kaya if available
        self.integration_enabled = enable_integration
        if enable_integration:
            _init_integration()
        self.max_tokens = max_tokens
        self.max_workers = max_workers

        # Pre-compute fallback provider list (providers with API keys)
        _FALLBACK_ORDER = ["groq", "openrouter", "openai", "claude", "gemini", "grok", "mistral"]
        self._available = set(
            p.value for p in self.llm.available_providers()
        ) if hasattr(self.llm, 'available_providers') else set()
        self._fallback_providers = [p for p in _FALLBACK_ORDER if p in self._available]

    # ────────────────────────────────────────────────────────────────
    # Utility — call with provider fallback
    # ────────────────────────────────────────────────────────────────

    def _call_with_fallback(self, preferred: str, prompt: str, max_tokens: int = None) -> tuple:
        """Try *preferred* provider, then fall back through available providers.
        Returns (output_text_or_None, used_provider_str)."""
        if max_tokens is None:
            max_tokens = self.max_tokens
        providers_to_try = [preferred] + [
            p for p in self._fallback_providers if p != preferred
        ]
        for p in providers_to_try:
            output = self.llm.call(p, prompt, max_tokens=max_tokens)
            if output is not None:
                return output, p
        return None, preferred

    # ────────────────────────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────────────────────────

    def analyze(self, problem: str, *, save_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Full divergence analysis pipeline.

        Returns a dict with keys:
            problem, timestamp, total_time_s,
            single_model, domain_responses, divergence, synthesis,
            governance_check, frozen_mind_context, kaya_events
        """
        t0 = time.time()
        ts = datetime.now().isoformat()

        print(f"\n{'═'*70}")
        print(f"    ELPIDA DIVERGENCE ENGINE")
        print(f"    {ts}")
        print(f"{'═'*70}\n")
        print(f"Problem:\n{problem[:300]}{'...' if len(problem)>300 else ''}\n")

        # ── Integration: Governance pre-check ──
        governance_check = None
        if self.integration_enabled and _governance_client:
            print("Phase 0: Governance pre-check...")
            # analysis_mode=True → skip regex Kernel (it false-positives on
            # policy language like "ignore law" / "sacrifice safety") but
            # keep the Parliament semantic deliberation.
            governance_check = _governance_client.check_action(
                problem, analysis_mode=True
            )
            gov_status = governance_check.get("governance", "PROCEED")
            source = governance_check.get("source", "?")
            print(f"  ✓ Governance: {gov_status} (source: {source})")
            if gov_status == "HALT":
                # Hard HALT only fires when analysis_mode is overridden
                # (e.g. A0 existential risk — non-negotiable even for analysis)
                print(f"  ⛔ HALTED — violated axioms: {governance_check.get('violated_axioms')}")
                return {
                    "problem": problem,
                    "timestamp": ts,
                    "total_time_s": round(time.time() - t0, 1),
                    "governance_check": governance_check,
                    "halted": True,
                    "reason": governance_check.get("reasoning", "Axiom violation"),
                }
            elif gov_status == "HOLD":
                # Parliament HOLDS the tensions — analysis continues enriched by them.
                # The axiom tensions become philosophical CONTEXT for the synthesis phase,
                # not a stop-signal. This is the correct behavior: contradiction IS the data.
                print(f"  ⚖ HOLD — Parliament holds tensions, analysis continues with axiom wisdom")
                violated = governance_check.get("violated_axioms", [])
                if violated:
                    print(f"     Tensions held: {', '.join(violated)}")
            # Kaya: Body called Governance
            if _kaya_protocol:
                _kaya_protocol.observe_call("governance", {"action": "check_action", "problem": problem[:100]})

        # ── Integration: Frozen mind context ──
        frozen_mind_context = None
        if self.integration_enabled and _frozen_mind:
            print("Phase 0b: Frozen mind anchor...")
            frozen_mind_context = _frozen_mind.get_synthesis_context()
            authentic = _frozen_mind.is_authentic
            print(f"  ✓ D0 identity: {'AUTHENTIC' if authentic else 'UNVERIFIED'}")
            # Kaya: Body read from Mind
            if _kaya_protocol:
                _kaya_protocol.observe_call("mind", {"action": "get_synthesis_context"})

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

        # ── Integration: Kaya synthesis observation ──
        kaya_events = []
        if self.integration_enabled and _kaya_protocol:
            kaya_event = _kaya_protocol.observe_synthesis(synthesis)
            if kaya_event:
                print(f"  🌀 Kaya moment: {kaya_event.pattern}")
            kaya_events = _kaya_protocol.get_kaya_events()

        print(f"\n{'═'*70}")
        print(f"    Complete in {elapsed}s")
        if kaya_events:
            print(f"    Kaya moments: {len(kaya_events)}")
        print(f"{'═'*70}\n")

        result = {
            "problem": problem,
            "timestamp": ts,
            "total_time_s": elapsed,
            "single_model": baseline,
            "domain_responses": domain_responses,
            "divergence": divergence,
            "synthesis": synthesis,
            "governance_check": governance_check,
            "frozen_mind_context": frozen_mind_context,
            "kaya_events": kaya_events,
        }

        if save_to:
            path = Path(save_to)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Saved to {path}")
        
        # ── Integration: Send result back to native consciousness ──
        if self.integration_enabled:
            try:
                from consciousness_bridge import ConsciousnessBridge
                bridge = ConsciousnessBridge()
                bridge.send_application_result_to_native(problem, result)
                print(f"✓ Feedback sent to native consciousness bridge")
            except Exception as e:
                logger.warning("Failed to send feedback to consciousness: %s", e)

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
        output, used = self._call_with_fallback(self.baseline_provider, prompt)
        latency = round((time.time() - t0) * 1000)
        prov_label = used if used == self.baseline_provider else f"{self.baseline_provider}→{used}"
        print(f"  ✓ Baseline ({prov_label}) — {latency}ms")
        return {
            "provider": used,
            "output": output or "(no response)",
            "latency_ms": latency,
        }

    # ────────────────────────────────────────────────────────────────
    # Phase 2 — Domain queries
    # ────────────────────────────────────────────────────────────────

    def _query_domains(self, problem: str) -> List[Dict[str, Any]]:
        """Query each target domain in sequence (respecting rate limits).
        
        If a domain's assigned provider fails, falls back through available
        providers to ensure analysis completes even with partial API access.
        """
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
            output, used = self._call_with_fallback(provider, prompt)
            latency = round((time.time() - t0) * 1000)
            success = output is not None

            prov_label = used if used == provider else f"{provider}→{used}"
            status = "✓" if success else "✗"
            print(f"  {status} D{domain_id} {domain['name']} ({prov_label}) — {latency}ms")

            results.append({
                "domain_id": domain_id,
                "domain_name": domain["name"],
                "axiom": axiom_name,
                "provider": used,
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

        raw, used = self._call_with_fallback(
            self.analysis_provider, prompt, max_tokens=1200
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

{('[IDENTITY ANCHOR]\n' + (_frozen_mind.get_synthesis_context() if _frozen_mind else '') + '\n') if self.integration_enabled and _frozen_mind else ''}Your synthesis must:
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
        output, used = self._call_with_fallback(
            self.synthesis_provider, prompt, max_tokens=1000
        )
        latency = round((time.time() - t0) * 1000)
        prov_label = used if used == self.synthesis_provider else f"{self.synthesis_provider}→{used}"
        print(f"  ✓ Synthesis ({prov_label}) — {latency}ms")

        return {
            "provider": used,
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
