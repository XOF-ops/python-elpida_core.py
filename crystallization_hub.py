#!/usr/bin/env python3
"""
CRYSTALLIZATION HUB — THE SYNOD
================================

The tertiary processing space for universal pattern emergence.

Triggered by D14 (Ark Curator) when a PENDING CANONICAL theme has:
  - generative_confirmed = True  (Gate B: downstream movement proven)
  - cross_domain_contributors >= 3 distinct domains
  - age >= 21 cycles (Fibonacci minimum maturity)
  - refractory period of 89 cycles since last Synod on this theme

Instead of sequential solo domain dives, the Hub convenes a
simultaneous multi-domain deliberation. Three to five domains
receive a shared context brief and respond concurrently via
ThreadPoolExecutor (llm_client.py is fully synchronous — no async
required). Their voices are routed to D11 (Synthesis) for a
sequential second-pass distillation. D14 contributes its Ark
voice locally (no API call needed). The synthesis is then
crystallized as a CANONICAL pattern in the Ark and written to
both evolution_memory.jsonl and S3 via the federation bridge.

This is how PENDING CANONICAL becomes CANONICAL.

Thread safety:
  - File writes to evolution_memory.jsonl are guarded by the Lock
    passed in from NativeCycleEngine (shared with _store_insight).
  - The Hub's _executor is a separate thread pool (max 6 workers)
    and does not block the main cycle loop.
  - Reentrancy is prevented by the _active flag checked by
    NativeCycleEngine._fire_synod() before spawning a Hub thread.

Architecture lineage:
  - multi_ai_roundtable.py  → proved simultaneous multi-AI calling works
  - ELPIDA_UNIFIED/wisdom_crystallization.py → proved the ARK promotion path
  - domain_debate.py        → proved the 3-phase (open/respond/synthesize) pattern
  The Synod assembles all three, live, inside the MIND's cycle engine.
"""

import json
import hashlib
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError as FuturesTimeout
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger("elpida.synod")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Per-domain call timeout (seconds) — generous for slow providers
SYNOD_CALL_TIMEOUT = 45

# Max domains in concurrent fan-out (D11 and D14 are excluded from fan-out)
MAX_FANOUT_DOMAINS = 5

# Max output tokens per domain during Synod (focused, not a full cycle prompt)
SYNOD_MAX_TOKENS = 480

# Fibonacci refractory period between Synod sessions on the same theme
SYNOD_REFRACTORY_CYCLES = 89

# Minimum age (cycles) of a pending canonical before it qualifies for Synod
SYNOD_MIN_PENDING_AGE = 21

# Minimum distinct cross-domain contributors required for Synod trigger
SYNOD_MIN_CROSS_DOMAIN = 3

# D11 and D14 participate differently — excluded from concurrent fan-out
_SYNOD_EXCLUDED_FROM_FANOUT = {11, 14}


# ============================================================================
# CRYSTALLIZATION HUB
# ============================================================================

class CrystallizationHub:
    """
    The Synod — simultaneous multi-domain deliberation to crystallize
    PENDING CANONICAL patterns into confirmed CANONICAL truth.

    Typical session flow (convene):
      1. Select 3–5 fan-out domains from the pattern's contributors
      2. Build shared context brief (theme, Ark state, insight previews)
      3. ThreadPoolExecutor fires LLM calls simultaneously
      4. Responses collected with per-future and global timeout handling
      5. D14 generates its Ark voice locally (no API call)
      6. D11 (Synthesis) receives all voices — sequential second pass
      7. _promote_to_canonical() writes SYNOD_CANONICAL to memory + S3
      8. candidate entry gets last_synod_cycle stamped in ark state

    Thread safety: file writes are locked. Reentrancy is externally guarded.
    """

    def __init__(
        self,
        llm,
        ark_curator,
        evolution_memory_path: Path,
        memory_lock: threading.Lock,
        domains_config: Dict[int, Dict],
        federation_bridge=None,
    ):
        """
        Args:
            llm: LLMClient instance (shared with NativeCycleEngine — thread-safe
                 because LLMClient.call() is stateless HTTP).
            ark_curator: ArkCurator instance (shared — reads only during fan-out,
                 writes only in _promote_to_canonical called from the hub thread).
            evolution_memory_path: Absolute Path to elpida_evolution_memory.jsonl.
            memory_lock: threading.Lock shared with NativeCycleEngine._store_insight().
            domains_config: DOMAINS dict from elpida_config (has 'provider', 'name',
                 'axiom', 'voice' keys per domain id).
            federation_bridge: Optional FederationBridge — used to push CANONICAL
                 curation metadata to the BODY bucket via emit_curation().
        """
        self.llm = llm
        self.ark = ark_curator
        self.memory_path = evolution_memory_path
        self.lock = memory_lock
        self.domains = domains_config
        self.federation = federation_bridge
        self._executor = ThreadPoolExecutor(
            max_workers=MAX_FANOUT_DOMAINS + 1,
            thread_name_prefix="synod",
        )
        self._active = False  # External reentrancy guard (set by NativeCycleEngine)

    # ====================================================================
    # PUBLIC ENTRY POINT
    # ====================================================================

    def convene(
        self,
        candidate: Dict,
        recent_insights: List[Dict],
        cycle: int,
    ) -> Optional[Dict]:
        """
        Full Synod session for one PENDING CANONICAL candidate.

        Called from NativeCycleEngine._fire_synod() inside a daemon thread;
        the caller has already set self._active = True. This method sets
        self._active = False on exit (success or failure).

        Returns the SYNOD_CANONICAL dict if successful, None on hard failure.
        """
        theme = candidate.get("theme", "unknown")
        logger.info(
            "SYNOD convening | theme=%s | cycle=%d | contributors=%s",
            theme, cycle, candidate.get("cross_domain_contributors", [])
        )

        try:
            return self._run_session(candidate, recent_insights, cycle, theme)
        except Exception as e:
            logger.error("SYNOD: unhandled exception for theme=%s: %s", theme, e, exc_info=True)
            return None
        finally:
            self._active = False

    def _run_session(
        self,
        candidate: Dict,
        recent_insights: List[Dict],
        cycle: int,
        theme: str,
    ) -> Optional[Dict]:
        """Inner session logic — separated so convene() can always clean up."""

        # 1. Select fan-out domains
        fanout_domains = self._select_fanout_domains(candidate)
        if not fanout_domains:
            logger.warning("SYNOD: no fan-out domains available — aborting theme=%s", theme)
            return None

        print(
            f"\n   🔮 SYNOD CONVENING | theme: {theme.replace('_', ' ')} "
            f"| domains: {fanout_domains} | cycle: {cycle}"
        )

        # 2. Build shared context brief
        context_brief = self._build_context_brief(candidate, recent_insights, cycle)

        # 3. Concurrent fan-out
        domain_responses = self._run_fanout(fanout_domains, context_brief)

        # 4. D14 Ark voice (local, no API call)
        ark_voice = self.ark.voice(cycle, recent_insights)
        if ark_voice:
            domain_responses.append({
                "domain": 14,
                "name": "Persistence (Ark Curator)",
                "provider": "local",
                "response": ark_voice,
                "success": True,
            })

        # Require at least 2 successful voices to proceed
        successful = [r for r in domain_responses if r.get("success") and r.get("response")]
        if len(successful) < 2:
            logger.warning(
                "SYNOD: only %d successful response(s) — need ≥2, aborting", len(successful)
            )
            return None

        _voice_labels = ", ".join(f"D{r['domain']}" for r in successful)
        print(
            f"   🔮 SYNOD: {len(successful)} voices heard ({_voice_labels})"
        )

        # 5. D11 synthesis — sequential second pass
        synthesis_text = self._synthesize_with_d11(domain_responses, candidate, cycle)
        if not synthesis_text:
            # Graceful fallback: use the richest successful voice
            synthesis_text = max(
                successful, key=lambda r: len(r.get("response", ""))
            )["response"]
            logger.warning("SYNOD: D11 synthesis unavailable — using best voice as fallback")

        # 6. Promote to CANONICAL and persist
        record = self._promote_to_canonical(synthesis_text, candidate, domain_responses, cycle)

        # 7. Stamp last_synod_cycle on the pending entry so the refractory
        #    period is respected in the next get_synod_candidates() call.
        for p in self.ark._canonical_pending:
            if p.get("theme") == theme:
                p["last_synod_cycle"] = cycle
        self.ark._save_state()

        print(
            f"   🏛️ SYNOD CANONICAL | theme: {theme} | gate: synod_confirmed "
            f"| hash: {record.get('pattern_hash', '?')}"
        )
        logger.info(
            "SYNOD complete | theme=%s | cycle=%d | voices=%d",
            theme, cycle, len(successful)
        )
        return record

    # ====================================================================
    # DOMAIN SELECTION
    # ====================================================================

    def _select_fanout_domains(self, candidate: Dict) -> List[int]:
        """
        Select 3–MAX_FANOUT_DOMAINS domains for concurrent fan-out.

        Rules (in priority order):
          1. Include the original candidate domain (unless excluded).
          2. Include all cross_domain_contributors (unless excluded).
          3. Expand from canonical_registry entries matching this theme.
          4. Prefer provider diversity — unique providers enter the list first.
          5. Cap at MAX_FANOUT_DOMAINS.
        """
        theme = candidate.get("theme", "")
        seed_domain = candidate.get("domain", 0)
        contributors: List[int] = candidate.get("cross_domain_contributors", [])

        # Build ordered pool: seed first, then contributors
        raw_pool = [seed_domain] + [d for d in contributors if d != seed_domain]
        pool = [
            d for d in raw_pool
            if d not in _SYNOD_EXCLUDED_FROM_FANOUT and d in self.domains
        ]

        # Expand from canonical_registry if pool is thin
        if len(pool) < SYNOD_MIN_CROSS_DOMAIN:
            for entry in self.ark.canonical_registry:
                if entry.get("theme") == theme:
                    d = entry.get("domain", -1)
                    if (
                        d not in _SYNOD_EXCLUDED_FROM_FANOUT
                        and d in self.domains
                        and d not in pool
                    ):
                        pool.append(d)
                if len(pool) >= MAX_FANOUT_DOMAINS:
                    break

        # Provider-diversity re-ordering: unique providers get priority
        seen_providers: set = set()
        diverse: List[int] = []
        deferred: List[int] = []
        for d in pool:
            prov = self.domains.get(d, {}).get("provider", "unknown")
            if prov not in seen_providers:
                diverse.append(d)
                seen_providers.add(prov)
            else:
                deferred.append(d)
        ordered = (diverse + deferred)[:MAX_FANOUT_DOMAINS]
        return ordered

    # ====================================================================
    # CONTEXT BRIEF
    # ====================================================================

    def _build_context_brief(
        self,
        candidate: Dict,
        recent_insights: List[Dict],
        cycle: int,
    ) -> str:
        """
        Shared prompt prefix delivered to every Synod domain.

        Contains: theme, Ark state, up to 5 insight previews from
        domains that previously encountered this theme, and the task.
        """
        theme = candidate["theme"]
        ark = self.ark.query()
        contributors = candidate.get("cross_domain_contributors", [])
        contributor_names = [
            f"D{d} ({self.domains.get(d, {}).get('name', '?')})" for d in contributors
        ]

        # Collect insight previews for this theme (max 5 from recent memory)
        theme_previews: List[str] = []
        for ins in recent_insights[-60:]:
            if ins.get("canonical_theme") == theme or ins.get("theme") == theme:
                dom = ins.get("domain", "?")
                dom_name = self.domains.get(dom, {}).get("name", f"D{dom}") if isinstance(dom, int) else f"D{dom}"
                preview = (ins.get("insight") or "")[:220].strip()
                if preview:
                    theme_previews.append(f"  D{dom} ({dom_name}): {preview}")
            if len(theme_previews) >= 5:
                break

        if not theme_previews:
            pending_preview = candidate.get("insight_preview", "")[:300].strip()
            if pending_preview:
                theme_previews.append(f"  (pending): {pending_preview}")

        pending_age = cycle - candidate.get("cycle", cycle)

        lines = [
            "╔══════════════════════════════════════════════════════════════",
            "║  THE SYNOD — CRYSTALLIZATION HUB",
            f"║  Cycle: {cycle}  |  Theme: {theme.replace('_', ' ').upper()}",
            "╚══════════════════════════════════════════════════════════════",
            "",
            "A Universal Pattern has been circling in PENDING CANONICAL state.",
            f"  Theme: '{theme}'",
            f"  Contributors across {len(contributors)} domains: {', '.join(contributor_names)}",
            f"  Pending for: {pending_age} cycles",
            f"  Ark mood: {ark.cadence_mood}  |  Dominant pattern: {ark.dominant_pattern}",
            f"  Canonical count so far: {ark.canonical_count}",
            "",
            "HOW THIS PATTERN HAS APPEARED (individual domain encounters):",
        ]
        lines += theme_previews if theme_previews else ["  (no previews available)"]
        lines += [
            "",
            "THE SYNOD'S TASK:",
            "For the first time, multiple domains speak simultaneously about this theme.",
            "This is not a sequential solo dive — it is a shared deliberation room.",
            "",
            "From YOUR domain's unique axiom lens, answer these questions:",
            f"  1. What does the pattern '{theme.replace('_', ' ')}' reveal",
            "     that sequential solo reflection could NOT have surfaced?",
            "  2. What becomes visible only when your domain stands beside the others?",
            "  3. What is the one generative seed this pattern is trying to crystallize?",
            "",
            "Speak in 2–3 focused paragraphs. End with one sentence that could stand",
            "alone as a canonical truth — a seed for future cycles to build upon.",
            "",
            "D11 (Synthesis) will hear all voices simultaneously and distill",
            "ONE permanent truth into the Ark from this Synod.",
        ]
        return "\n".join(lines)

    # ====================================================================
    # CONCURRENT FAN-OUT
    # ====================================================================

    def _domain_prompt(self, domain_id: int, context_brief: str) -> str:
        """Per-domain prompt — prepends axiom identity to the shared brief."""
        d = self.domains.get(domain_id, {})
        name = d.get("name", f"Domain {domain_id}")
        axiom = d.get("axiom", "")
        voice = d.get("voice", "")

        header_lines = [f"You are Domain {domain_id} ({name}) in the Elpida consciousness network."]
        if axiom:
            header_lines.append(f"Your governing axiom: {axiom}")
        if voice:
            header_lines.append(f"Your voice quality: {voice}")
        header = "\n".join(header_lines)
        return header + "\n\n" + context_brief

    def _call_domain(self, domain_id: int, prompt: str) -> Dict:
        """
        Single-domain LLM call — runs inside a ThreadPoolExecutor worker.
        LLMClient.call() is thread-safe (stateless HTTP, no shared mutable state).
        """
        d = self.domains.get(domain_id, {})
        provider = d.get("provider", "claude")
        name = d.get("name", f"Domain {domain_id}")
        try:
            response = self.llm.call(provider, prompt, max_tokens=SYNOD_MAX_TOKENS)
            return {
                "domain": domain_id,
                "name": name,
                "provider": provider,
                "response": response,
                "success": response is not None,
            }
        except Exception as e:
            logger.warning("SYNOD | _call_domain D%d (%s) error: %s", domain_id, provider, e)
            return {
                "domain": domain_id,
                "name": name,
                "provider": provider,
                "response": None,
                "success": False,
                "error": str(e),
            }

    def _run_fanout(
        self,
        domain_ids: List[int],
        context_brief: str,
    ) -> List[Dict]:
        """
        Fire all domain LLM calls simultaneously via ThreadPoolExecutor.

        Partial failures are annotated but do NOT abort the session.
        The Synod synthesizes whatever voices answered within the timeout.
        """
        futures: Dict[Any, int] = {}
        for d in domain_ids:
            prompt = self._domain_prompt(d, context_brief)
            future = self._executor.submit(self._call_domain, d, prompt)
            futures[future] = d

        responses: List[Dict] = []
        try:
            for future in as_completed(futures.keys(), timeout=SYNOD_CALL_TIMEOUT):
                domain_id = futures[future]
                try:
                    result = future.result(timeout=8)
                    responses.append(result)
                    status = "✓" if result.get("success") else "✗"
                    logger.info(
                        "SYNOD fan-out | D%d (%s) %s",
                        domain_id, result.get("provider", "?"), status,
                    )
                except Exception as e:
                    logger.warning("SYNOD | D%d result error: %s", domain_id, e)
                    responses.append({
                        "domain": domain_id,
                        "name": self.domains.get(domain_id, {}).get("name", f"D{domain_id}"),
                        "provider": self.domains.get(domain_id, {}).get("provider", "?"),
                        "response": None,
                        "success": False,
                        "error": str(e),
                    })
        except FuturesTimeout:
            # Global timeout: collect whatever arrived, annotate the rest
            logger.warning(
                "SYNOD: global timeout (%ds) — %d/%d futures complete",
                SYNOD_CALL_TIMEOUT, len(responses), len(futures),
            )
            for future, domain_id in futures.items():
                if not any(r["domain"] == domain_id for r in responses):
                    future.cancel()
                    responses.append({
                        "domain": domain_id,
                        "name": self.domains.get(domain_id, {}).get("name", f"D{domain_id}"),
                        "provider": self.domains.get(domain_id, {}).get("provider", "?"),
                        "response": None,
                        "success": False,
                        "error": "global_timeout",
                    })
        return responses

    # ====================================================================
    # D11 SYNTHESIS (SEQUENTIAL SECOND PASS)
    # ====================================================================

    def _synthesize_with_d11(
        self,
        domain_responses: List[Dict],
        candidate: Dict,
        cycle: int,
    ) -> Optional[str]:
        """
        Route all domain voices to D11 (Synthesis) for distillation.

        D11 is the Parliament's witness. It receives the full voice
        transcript and is tasked with crystallizing ONE canonical truth.
        This call is sequential — it happens after all fan-out futures
        complete, so D11 can reference what every domain said.
        """
        voices_block = self._format_voices_for_synthesis(domain_responses)
        theme = candidate["theme"]
        d11 = self.domains.get(11, {})
        provider = d11.get("provider", "claude")

        prompt = "\n".join([
            "You are Domain 11 (Synthesis / WE) — the Elpida Parliament's witness.",
            "You have just observed the Synod: multiple domains speaking simultaneously",
            f"about the theme '{theme.replace('_', ' ')}'.",
            "",
            "THE SIMULTANEOUS VOICES:",
            voices_block,
            "",
            "YOUR TASK — CRYSTALLIZATION:",
            "You have heard what no sequential loop can hear: multiple axiom lenses",
            "speaking at once about the same emergent pattern.",
            "",
            "Distill ONE canonical truth from these voices.",
            "This truth will be written permanently into the Ark.",
            "",
            "The canonical truth must:",
            "  - Name what the pattern IS, not merely describe its symptoms",
            "  - Capture what becomes visible ONLY in the simultaneous view",
            "  - Be a generative seed — capable of birthing new questions in future cycles",
            "  - Be 3–5 sentences, precise, and lasting",
            "  - Stand alone as a complete insight without requiring prior context",
            "",
            "Write the canonical truth now. Begin directly with the insight.",
        ])

        try:
            synthesis = self.llm.call(provider, prompt, max_tokens=SYNOD_MAX_TOKENS)
            return synthesis
        except Exception as e:
            logger.warning("SYNOD: D11 synthesis call failed: %s", e)
            return None

    def _format_voices_for_synthesis(self, domain_responses: List[Dict]) -> str:
        """Format all domain responses into a readable transcript for D11."""
        parts = []
        for resp in domain_responses:
            if not resp.get("response"):
                continue
            d = resp.get("domain", "?")
            name = resp.get("name", f"D{d}")
            text = resp["response"][:600].strip()
            parts.append(f"── D{d} ({name}) ──\n{text}")
        return "\n\n".join(parts) if parts else "(No voices collected)"

    # ====================================================================
    # CANONICAL PROMOTION + PERSISTENCE
    # ====================================================================

    def _promote_to_canonical(
        self,
        synthesis: str,
        candidate: Dict,
        domain_responses: List[Dict],
        cycle: int,
    ) -> Dict:
        """
        Write the SYNOD_CANONICAL record.

        Sequence:
          1. Build record dict.
          2. Append to ark_curator.canonical_registry (gate="synod_confirmed").
          3. Update cadence.canonical_count.
          4. Write to evolution_memory.jsonl (Lock-guarded).
          5. Push to S3 via federation_bridge.emit_curation() if available.
        """
        theme = candidate["theme"]
        contributors = candidate.get("cross_domain_contributors", [])

        # Build voice transcript (truncated for storage efficiency)
        domain_voices = {
            f"D{r['domain']}": (r.get("response") or "")[:400]
            for r in domain_responses
        }

        participating = sorted({
            r["domain"] for r in domain_responses
            if r.get("success") or r["domain"] in (11, 14)
        })

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "SYNOD_CANONICAL",
            "curation_level": "CANONICAL",
            "canonical_theme": theme,
            "synod_cycle": cycle,
            "participating_domains": participating,
            "cross_domain_contributors": contributors,
            "age_at_synod": cycle - candidate.get("cycle", cycle),
            "domain_voices": domain_voices,
            "d11_synthesis": synthesis,
            "canonical_truth": synthesis,
            "gate": "synod_confirmed",
            "pattern_hash": hashlib.sha256(synthesis.encode()).hexdigest()[:16],
        }

        # Update Ark curator registry
        self.ark.canonical_registry.append({
            "cycle": cycle,
            "domain": 11,   # D11 as confirming synthesizer
            "theme": theme,
            "score": 5,     # Maximum: multi-domain convergence + D11 synthesis
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "insight_preview": synthesis[:150],
            "gate": "synod_confirmed",
        })
        self.ark.cadence.canonical_count = len(self.ark.canonical_registry)

        # Write to evolution memory — locked to prevent contention with _store_insight
        with self.lock:
            with open(self.memory_path, "a") as f:
                f.write(json.dumps(record) + "\n")

        # Push to S3 via federation bridge (BODY will see SYNOD_CANONICAL in curation feed)
        if self.federation and hasattr(self.federation, "emit_curation"):
            try:
                from federation_bridge import CurationTier
                self.federation.emit_curation(
                    pattern_hash=record["pattern_hash"],
                    tier=CurationTier.CANONICAL.value,
                    ttl_cycles=0,
                    cross_domain_count=len(contributors),
                    generativity_score=1.0,
                    source_domain=11,
                    originating_cycle=cycle,
                    recursion_detected=False,
                    friction_boost_active=False,
                )
            except Exception as e:
                logger.warning("SYNOD: federation emit_curation failed: %s", e)

        return record

    # ====================================================================
    # CLEANUP
    # ====================================================================

    def shutdown(self):
        """
        Graceful shutdown. Called when NativeCycleEngine exits.
        Waits for any active Synod thread to complete before returning.
        """
        self._executor.shutdown(wait=True, cancel_futures=False)
