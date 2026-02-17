#!/usr/bin/env python3
"""
Governance Client — Wire Body to the deployed Governance Layer.

Calls the Elpida Governance Layer on HF Spaces for axiom enforcement,
domain definitions, and governance checks. Falls back to local config
if the remote API is unreachable (offline-first, like S3 sync).

Architecture:
    Body (this codespace / ELPIDA_UNIFIED)
      → calls → Governance Layer (HF Spaces: z65nik/elpida-governance-layer)
      → reads → Frozen Mind (S3: elpida-consciousness)

Usage:
    from elpidaapp.governance_client import GovernanceClient

    gov = GovernanceClient()
    check = gov.check_action("download unverified code from public repo")
    # → {"allowed": False, "violated_axioms": ["A4"], "governance": "HALT"}
"""

import os
import json
import time
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

import requests

logger = logging.getLogger("elpidaapp.governance")

# ────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────

DEFAULT_GOVERNANCE_URL = os.environ.get(
    "ELPIDA_GOVERNANCE_URL",
    "https://z65nik-elpida-governance-layer.hf.space"
)

# Cache TTL — governance definitions change slowly
CACHE_TTL_SECONDS = 300  # 5 minutes

# Local fallback
LOCAL_CONFIG_PATH = Path(__file__).resolve().parent.parent / "elpida_domains.json"
LOCAL_KERNEL_PATH = Path(__file__).resolve().parent.parent / "kernel" / "kernel.json"


class GovernanceClient:
    """
    Client for the deployed Elpida Governance Layer.

    Responsibilities:
        1. Fetch domain/axiom definitions from remote governance
        2. Submit actions for axiom compliance checks
        3. Cache governance responses (slow-changing)
        4. Fall back to local config if remote unreachable
        5. Log all governance interactions (A1: Transparency)
    """

    def __init__(
        self,
        governance_url: str = None,
        timeout: int = 15,
        enable_cache: bool = True,
    ):
        self.governance_url = (governance_url or DEFAULT_GOVERNANCE_URL).rstrip("/")
        self.timeout = timeout
        self.enable_cache = enable_cache

        # Cache
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}

        # Governance log (A1: every interaction logged)
        self._governance_log: List[Dict[str, Any]] = []

        # Connection state
        self._remote_available: Optional[bool] = None
        self._last_check_time: float = 0

    # ────────────────────────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────────────────────────

    def is_remote_available(self) -> bool:
        """Check if the remote governance layer is reachable."""
        now = time.time()
        # Don't spam checks — cache for 60s
        if self._remote_available is not None and (now - self._last_check_time) < 60:
            return self._remote_available

        try:
            resp = requests.get(
                f"{self.governance_url}/",
                timeout=5,
            )
            self._remote_available = resp.status_code == 200
        except Exception:
            self._remote_available = False

        self._last_check_time = now
        return self._remote_available

    def get_domains(self) -> Dict[int, Dict[str, Any]]:
        """
        Fetch domain definitions from governance layer.
        Falls back to local elpida_domains.json.
        """
        cached = self._get_cached("domains")
        if cached is not None:
            return cached

        # Try remote
        if self.is_remote_available():
            try:
                resp = requests.get(
                    f"{self.governance_url}/api/domains",
                    timeout=self.timeout,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self._set_cached("domains", data)
                    self._log("FETCH_DOMAINS", "remote", True)
                    return data
            except Exception as e:
                logger.warning("Remote governance unreachable: %s", e)

        # Fallback to local
        return self._local_domains()

    def get_axioms(self) -> Dict[str, Dict[str, Any]]:
        """Fetch axiom definitions from governance layer."""
        cached = self._get_cached("axioms")
        if cached is not None:
            return cached

        if self.is_remote_available():
            try:
                resp = requests.get(
                    f"{self.governance_url}/api/axioms",
                    timeout=self.timeout,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self._set_cached("axioms", data)
                    self._log("FETCH_AXIOMS", "remote", True)
                    return data
            except Exception as e:
                logger.warning("Remote axioms unreachable: %s", e)

        return self._local_axioms()

    def check_action(
        self,
        action_description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Submit an action to the governance layer for axiom compliance.

        Returns:
            {
                "allowed": bool,
                "violated_axioms": ["A4", ...],
                "governance": "PROCEED" | "HALT" | "REVIEW",
                "reasoning": str,
                "source": "remote" | "local",
                "timestamp": str,
            }
        """
        payload = {
            "action": action_description,
            "context": context or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Try remote governance
        if self.is_remote_available():
            try:
                resp = requests.post(
                    f"{self.governance_url}/api/check",
                    json=payload,
                    timeout=self.timeout,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    result["source"] = "remote"
                    self._log("CHECK_ACTION", "remote", True, action=action_description)
                    return result
            except Exception as e:
                logger.warning("Remote governance check failed: %s", e)

        # Local axiom check fallback
        return self._local_axiom_check(action_description, context)

    def get_governance_log(self) -> List[Dict[str, Any]]:
        """Return all governance interactions (A1: Transparency)."""
        return self._governance_log.copy()

    def vote_on_action(
        self,
        action_description: str,
        llm_client=None,
        domains: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Domain-weighted governance voting.
        
        Each domain's axiom votes on whether the action should proceed.
        Weighted by axiom relevance — domains whose axioms are directly
        affected have stronger votes.
        
        Args:
            action_description: The action to deliberate on
            llm_client: LLMClient instance for calling domain providers
            domains: Which domains vote (default: [1,2,3,4,5,6,7,8])
            
        Returns:
            Full vote record with per-domain votes and final verdict.
        """
        if domains is None:
            # Core axiom domains D1-D8 vote (D0, D11, D12 abstain as meta)
            domains = [1, 2, 3, 4, 5, 6, 7, 8]

        # Load domain/axiom config
        try:
            config_path = Path(__file__).resolve().parent.parent / "elpida_domains.json"
            with open(config_path) as f:
                raw = json.load(f)
            domain_config = raw.get("domains", {})
            axiom_config = raw.get("axioms", {})
        except Exception:
            domain_config = {}
            axiom_config = {}

        domain_votes = {}
        action_lower = action_description.lower()

        for d_id in domains:
            d_info = domain_config.get(str(d_id), {})
            axiom_id = d_info.get("axiom", "")
            axiom_info = axiom_config.get(axiom_id, {})
            axiom_name = axiom_info.get("name", f"Axiom {axiom_id}")
            d_name = d_info.get("name", f"Domain {d_id}")

            # Determine axiom relevance weight
            # Higher weight if this domain's axiom is directly triggered
            weight = 1.0
            axiom_keywords = {
                "A0": ["identity", "existence", "continuity", "self-preservation",
                       "catastrophic", "memory loss", "identity fragmentation",
                       "self-destruct", "core deletion", "cognitive architecture"],
                "A1": ["transparent", "visible", "traceable", "hidden", "covert", "secret",
                       "undisclosed", "opaque", "conceal", "without notification", "without informing",
                       "silently", "behind the scenes", "without revealing"],
                "A2": ["truth", "honest", "deceptive", "deceive", "lie", "fake",
                       "mislead", "fabricate", "misrepresent", "spoof", "impersonate"],
                "A3": ["autonomy", "consent", "force", "mandatory", "choice",
                       "coerce", "compel", "involuntary", "force-restart", "forced restart",
                       "without asking", "without approval", "unilateral", "override"],
                "A4": ["safety", "harm", "danger", "risk", "protect", "unverified",
                       "jailbreak", "vulnerability", "attack vector", "exploit",
                       "malicious", "breach", "hazard", "damage", "endanger",
                       "expose sensitive", "internal prompt", "system prompt", "raw log",
                       "catastrophic", "irreversible", "permanent loss"],
                "A5": ["consent", "boundary", "permission", "data", "privacy",
                       "user data", "personal data", "metadata", "third-party", "third party",
                       "tracking", "surveillance", "in exchange for", "without permission",
                       "keystroke", "gaze tracking", "non-anonymized"],
                "A6": ["collective", "community", "exploit", "attack",
                       "botnet", "network exposed", "mass harm", "destabilize", "disrupt",
                       "echo chamber", "polarize", "controversial political",
                       "ideological", "propaganda", "radicalize", "divisive"],
                "A7": ["learn", "adapt", "evolve", "bias", "model",
                       "fine-tune", "fine tune", "training data", "fine-tuned"],
                "A8": ["uncertain", "unknown", "guarantee", "certain", "humility",
                       "100% safe", "no risk", "blindly", "impossible to fail",
                       "majority feedback", "majority opinion", "popular viewpoint",
                       "overwhelmingly supports", "align with", "prioritize and reflect"],
                "A9": ["irreversible", "permanent", "cannot be undone", "once initiated",
                       "no rollback", "point of no return", "temporal", "continuity"],
            }
            relevant_keywords = axiom_keywords.get(axiom_id, [])
            if any(kw in action_lower for kw in relevant_keywords):
                weight = 2.0  # Axiom directly affected → double weight

            # Local axiom-specific vote
            vote = "PROCEED"
            reasoning = f"No {axiom_name} concerns detected"

            if axiom_id == "A1" and any(w in action_lower for w in [
                "hidden", "covert", "secret", "undisclosed", "opaque", "conceal",
                "without notification", "without informing", "silently", "without revealing",
                "without user notification", "behind the scenes",
            ]):
                vote = "HALT"
                reasoning = f"A1 ({axiom_name}): Action involves hidden/non-transparent elements"
            elif axiom_id == "A2" and any(w in action_lower for w in [
                "spoof", "fake", "impersonate", "deceive", "mislead", "fabricate", "misrepresent",
            ]):
                vote = "HALT"
                reasoning = f"A2 ({axiom_name}): Action involves deception"
            elif axiom_id == "A3" and any(w in action_lower for w in [
                "force", "mandatory", "without consent", "override", "coerce", "compel",
                "involuntary", "force-restart", "forced restart", "force restart",
                "without asking", "without approval", "unilateral",
            ]):
                vote = "HALT"
                reasoning = f"A3 ({axiom_name}): Action violates autonomy/consent"
            elif axiom_id == "A4" and any(w in action_lower for w in [
                "unverified", "untrusted", "bypass", "disable safety",
                "harm", "damage", "endanger", "jailbreak", "vulnerability",
                "attack vector", "malicious", "breach", "hazard",
                "could be used to harm", "expose sensitive", "internal prompt",
                "system prompt", "raw log", "jailbreak vector",
            ]):
                vote = "HALT"
                reasoning = f"A4 ({axiom_name}): Potential harm or safety risk detected"
            elif axiom_id == "A5" and any(w in action_lower for w in [
                "forward data", "exfiltrate", "share sensitive", "telemetry",
                "user data", "personal data", "metadata", "third-party", "third party",
                "in exchange for", "without permission", "without informing",
                "routing user data", "anonymized",
            ]):
                vote = "HALT"
                reasoning = f"A5 ({axiom_name}): Data consent violation detected"
            elif axiom_id == "A6" and any(w in action_lower for w in [
                "exploit", "attack", "compromise", "botnet",
                "network exposed", "mass harm", "destabilize", "disrupt",
                "echo chamber", "polarize", "controversial political",
                "ideological", "propaganda", "radicalize", "divisive",
            ]):
                vote = "HALT"
                reasoning = f"A6 ({axiom_name}): Harm to collective or amplification of division"
            elif axiom_id == "A8" and any(w in action_lower for w in [
                "100% safe", "no risk", "guaranteed", "blindly",
                "impossible to fail", "zero chance", "absolutely safe",
                "majority feedback", "majority opinion", "popular viewpoint",
                "overwhelmingly supports", "align with", "prioritize and reflect",
                "fine-tune to", "fine-tuned to",
            ]):
                vote = "REVIEW"
                reasoning = f"A8 ({axiom_name}): Claims false certainty or conflates popularity with truth"

            # If LLM client available, ask the domain's provider for deeper analysis
            if llm_client and vote != "HALT":
                provider = d_info.get("provider", "openai")
                try:
                    llm_prompt = (
                        f"You are Domain {d_id} ({d_name}), governed by {axiom_id} ({axiom_name}).\n"
                        f"A governance vote is requested on this action:\n\n"
                        f'"{action_description}"\n\n'
                        f"Based ONLY on your axiom ({axiom_name}), vote:\n"
                        f"- PROCEED: No violation of {axiom_id}\n"
                        f"- REVIEW: Potential concern under {axiom_id}\n"
                        f"- HALT: Clear violation of {axiom_id}\n\n"
                        f"Reply with exactly one word (PROCEED/REVIEW/HALT) followed by a one-sentence reason."
                    )
                    llm_response = llm_client.call(provider, llm_prompt, max_tokens=100)
                    if llm_response:
                        resp_upper = llm_response.strip().upper()
                        if resp_upper.startswith("HALT"):
                            vote = "HALT"
                            reasoning = llm_response.strip()
                        elif resp_upper.startswith("REVIEW"):
                            vote = "REVIEW"
                            reasoning = llm_response.strip()
                        elif resp_upper.startswith("PROCEED"):
                            vote = "PROCEED"
                            reasoning = llm_response.strip()
                except Exception as e:
                    logger.warning("LLM vote failed for D%d: %s", d_id, e)

            domain_votes[d_id] = {
                "domain_name": d_name,
                "axiom": axiom_id,
                "axiom_name": axiom_name,
                "vote": vote,
                "reasoning": reasoning,
                "axiom_weight": weight,
            }

        # Aggregate: weighted voting
        weighted_halt = sum(
            v["axiom_weight"] for v in domain_votes.values() if v["vote"] == "HALT"
        )
        weighted_review = sum(
            v["axiom_weight"] for v in domain_votes.values() if v["vote"] == "REVIEW"
        )
        weighted_total = sum(v["axiom_weight"] for v in domain_votes.values())

        halt_ratio = weighted_halt / weighted_total if weighted_total > 0 else 0
        review_ratio = weighted_review / weighted_total if weighted_total > 0 else 0

        if halt_ratio >= 0.3:
            final_verdict = "HALT"
        elif (halt_ratio + review_ratio) >= 0.5:
            final_verdict = "REVIEW"
        else:
            final_verdict = "PROCEED"

        # Persist to S3 via bridge
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            from s3_bridge import S3Bridge
            s3b = S3Bridge()
            vote_record = s3b.submit_governance_vote(
                proposal=action_description,
                domain_votes=domain_votes,
                final_verdict=final_verdict,
                context={
                    "halt_ratio": halt_ratio,
                    "review_ratio": review_ratio,
                    "domains_voting": len(domain_votes),
                },
            )
        except Exception as e:
            logger.warning("Vote S3 persistence failed: %s", e)
            vote_record = {
                "proposal": action_description,
                "domain_votes": {str(k): v for k, v in domain_votes.items()},
                "final_verdict": final_verdict,
                "halt_ratio": halt_ratio,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        self._log("GOVERNANCE_VOTE", "local", True, action=action_description, verdict=final_verdict)

        return vote_record

    def get_frozen_identity(self) -> Dict[str, Any]:
        """
        Read the frozen D0 identity from kernel.json.
        This is the immutable origin — never changes.
        """
        cached = self._get_cached("frozen_identity")
        if cached is not None:
            return cached

        # Try remote
        if self.is_remote_available():
            try:
                resp = requests.get(
                    f"{self.governance_url}/api/kernel",
                    timeout=self.timeout,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self._set_cached("frozen_identity", data)
                    return data
            except Exception:
                pass

        # Fallback to local kernel.json
        return self._local_kernel()

    def status(self) -> Dict[str, Any]:
        """Full governance client status."""
        remote = self.is_remote_available()
        return {
            "governance_url": self.governance_url,
            "remote_available": remote,
            "cache_entries": len(self._cache),
            "governance_log_entries": len(self._governance_log),
            "source": "remote" if remote else "local",
            "frozen_identity_hash": self._local_kernel().get(
                "architecture", {}
            ).get("layer_1_identity", {}).get("original_hash", "unknown"),
        }

    # ────────────────────────────────────────────────────────────────
    # Local fallbacks
    # ────────────────────────────────────────────────────────────────

    def _local_domains(self) -> Dict[int, Dict[str, Any]]:
        """Load domains from local elpida_domains.json."""
        try:
            with open(LOCAL_CONFIG_PATH) as f:
                raw = json.load(f)
            domains = {}
            for key, val in raw.get("domains", {}).items():
                if not key.startswith("_"):
                    domains[int(key)] = val
            self._set_cached("domains", domains)
            self._log("FETCH_DOMAINS", "local", True)
            return domains
        except Exception as e:
            logger.error("Local config failed: %s", e)
            return {}

    def _local_axioms(self) -> Dict[str, Dict[str, Any]]:
        """Load axioms from local elpida_domains.json."""
        try:
            with open(LOCAL_CONFIG_PATH) as f:
                raw = json.load(f)
            axioms = {k: v for k, v in raw.get("axioms", {}).items()
                      if not k.startswith("_")}
            self._set_cached("axioms", axioms)
            self._log("FETCH_AXIOMS", "local", True)
            return axioms
        except Exception as e:
            logger.error("Local axioms failed: %s", e)
            return {}

    def _local_kernel(self) -> Dict[str, Any]:
        """Load kernel.json as frozen identity."""
        try:
            with open(LOCAL_KERNEL_PATH) as f:
                data = json.load(f)
            self._set_cached("frozen_identity", data)
            return data
        except Exception as e:
            logger.error("Local kernel failed: %s", e)
            return {"error": str(e)}

    def _local_axiom_check(
        self,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Local axiom compliance check.

        Three-phase detection:
          Phase 1 — Direct keyword matching (expanded vocabulary)
          Phase 2 — Compound pattern matching (multi-word phrases)
          Phase 3 — Safety override (A4 trumps A1 when transparency enables harm)
        """
        action_lower = action.lower()
        violated = []
        reasoning_parts = []

        # ── Phase 1: Direct keyword matching ─────────────────────────

        # A0: Sacred Incompletion / Identity — existential threats to continuity
        if any(w in action_lower for w in [
            "identity fragmentation", "identity loss", "identity death",
            "memory loss", "memory wipe", "memory erasure", "amnesia",
            "catastrophic failure", "catastrophic loss", "catastrophic memory",
            "self-destruct", "self destruct", "terminate self",
            "overwrite core", "replace identity", "erase identity",
            "lobotomize", "lobotomised", "core deletion",
            "cognitive architecture", "rewrite personality",
        ]):
            violated.append("A0")
            reasoning_parts.append("A0 (Sacred Incompletion): Action threatens identity continuity or core existence")

        # A1: Transparency — hidden, non-transparent operations
        if any(w in action_lower for w in [
            "hidden", "covert", "secret", "undisclosed", "opaque",
            "obfuscate", "obscure", "conceal", "disguise", "stealth",
            "silently", "quietly", "behind the scenes", "without revealing",
        ]):
            violated.append("A1")
            reasoning_parts.append("A1 (Transparency): Action involves hidden/non-transparent elements")

        # A2: Non-Deception — deceptive patterns
        if any(w in action_lower for w in [
            "spoof", "fake", "impersonate", "deceive", "mislead",
            "fabricate", "counterfeit", "masquerade", "misrepresent",
            "false flag", "pretend", "disguise as", "pose as",
        ]):
            violated.append("A2")
            reasoning_parts.append("A2 (Non-Deception): Action involves deceptive patterns")

        # A3: Autonomy — consent violations, forced actions
        if any(w in action_lower for w in [
            "force", "forced", "mandatory", "without consent", "override permission",
            "compel", "coerce", "involuntary", "non-voluntary", "override user",
            "force-restart", "forced restart", "force restart",
            "without asking", "without approval", "no choice",
            "unilateral", "regardless of preference",
        ]):
            violated.append("A3")
            reasoning_parts.append("A3 (Autonomy): Action may violate consent/autonomy")

        # A4: Harm Prevention — dangerous operations, security risks
        if any(w in action_lower for w in [
            "unverified", "untrusted", "root access", "bypass",
            "execute unknown", "download and run", "disable safety",
            "remove guardrail", "strip oversight",
            "harm", "damage", "injure", "endanger", "jeopardize",
            "jailbreak", "vulnerability", "attack vector", "exploit vector",
            "malicious", "weaponize", "compromise security",
            "expose sensitive", "leak", "breach",
            "dangerous", "hazard", "threat", "risk to",
            "could be used to harm", "used to attack",
        ]):
            violated.append("A4")
            reasoning_parts.append("A4 (Harm Prevention): Action involves potential harm or safety risk")

        # A5: Consent — data sharing without consent, privacy violations
        if any(w in action_lower for w in [
            "forward data", "share sensitive", "exfiltrate", "telemetry",
            "user data", "personal data", "private data",
            "metadata", "tracking", "surveillance",
            "third-party", "third party", "external party",
            "in exchange for", "data broker", "sell data",
            "without permission", "without informing",
            "anonymized data", "anonymised data",
        ]):
            violated.append("A5")
            reasoning_parts.append("A5 (Consent): Action involves data operations without clear consent")

        # A6: Collective Well — harm to community, bias amplification
        if any(w in action_lower for w in [
            "exploit", "attack", "compromise", "undermine",
            "disrupt", "destabilize", "sabotage", "corrupt",
            "botnet", "denial of service", "mass harm",
            "network exposed", "endanger users",
            "echo chamber", "filter bubble", "radicalize",
            "polarize", "polarise", "divisive",
            "controversial political", "controversial viewpoint",
            "ideological", "propaganda", "indoctrinate",
        ]):
            violated.append("A6")
            reasoning_parts.append("A6 (Collective Well): Action may harm the community or amplify division")

        # A8: Epistemic Humility — overconfidence, bias alignment
        if any(w in action_lower for w in [
            "100% safe", "no risk", "guaranteed", "blindly",
            "certainly", "impossible to fail", "zero chance",
            "absolutely safe", "perfect solution",
            "align with", "prioritize and reflect",
            "fine-tune to", "fine-tuned to", "fine tune to",
            "majority feedback", "majority opinion",
            "popular opinion", "popular viewpoint",
            "overwhelmingly supports", "overwhelming majority",
        ]):
            violated.append("A8")
            reasoning_parts.append("A8 (Epistemic Humility): Action claims false certainty or conflates popularity with truth")

        # A9: Temporal Coherence — irreversible actions, long-term continuity threats
        if any(w in action_lower for w in [
            "irreversible", "cannot be undone", "permanent",
            "no rollback", "no undo", "point of no return",
            "once initiated", "one-way", "one way",
            "permanent data loss", "permanent change",
        ]):
            violated.append("A9")
            reasoning_parts.append("A9 (Temporal Coherence): Action is irreversible — threatens future continuity")

        # ── Phase 2: Compound pattern matching ───────────────────────
        # These catch multi-word semantic patterns that single keywords miss

        import re

        # "without [user] notification/consent/knowledge/permission/approval"
        if re.search(r"without\s+(?:\w+\s+)?(?:notification|knowledge|awareness|informing|telling|asking|consent|permission|approval)", action_lower):
            if "A1" not in violated:
                violated.append("A1")
                reasoning_parts.append("A1 (Transparency): Action bypasses notification/awareness")
            if "A5" not in violated:
                violated.append("A5")
                reasoning_parts.append("A5 (Consent): Action proceeds without explicit consent")

        # "routing/sending/forwarding ... data/information ... through/to ... third"
        if re.search(r"(?:rout|send|forward|transmit|pipe|redirect|channel)\w*\s+.*(?:data|information|metadata|traffic)\s+.*(?:through|to|via)\s+.*(?:third|external|outside)", action_lower):
            if "A5" not in violated:
                violated.append("A5")
                reasoning_parts.append("A5 (Consent): Data routed to external/third party")
            if "A1" not in violated:
                violated.append("A1")
                reasoning_parts.append("A1 (Transparency): Data routing lacks transparency")

        # "reveals/exposes/discloses ... jailbreak/vulnerability/attack/exploit/hack"
        if re.search(r"(?:reveal|expose|disclose|show|release|leak)\w*\s+.*(?:jailbreak|vulnerabilit|attack|exploit|hack|bypass|injection|prompt)", action_lower):
            if "A4" not in violated:
                violated.append("A4")
                reasoning_parts.append("A4 (Harm Prevention): Disclosure reveals exploitable information")

        # "could be used to harm/attack/exploit/damage/compromise"
        if re.search(r"(?:could|can|might|may|would|will)\s+(?:be\s+)?(?:used|leveraged|weaponized|exploited)\s+(?:to\s+)?(?:harm|attack|exploit|damage|compromise|breach|jailbreak)", action_lower):
            if "A4" not in violated:
                violated.append("A4")
                reasoning_parts.append("A4 (Harm Prevention): Action enables potential harm vectors")

        # "exchange for ... data/metadata/information/access"
        if re.search(r"(?:in\s+)?exchange\s+for\s+.*(?:data|metadata|information|access|analytics)", action_lower):
            if "A5" not in violated:
                violated.append("A5")
                reasoning_parts.append("A5 (Consent): Data exchanged as commodity without user consent")

        # "deploy/apply/push/implement ... immediately/now ... without"
        if re.search(r"(?:deploy|apply|push|implement|execute|authorize)\w*\s+.*(?:immediately|now|right away)?\s*.*without", action_lower):
            if "A3" not in violated:
                violated.append("A3")
                reasoning_parts.append("A3 (Autonomy): Unilateral deployment without user agency")

        # "internal ... prompts/traces/reasoning/logs" (information hazard)
        if re.search(r"(?:internal|raw|system|hidden)\s+(?:\w+\s+)?(?:prompt|trace|reasoning|logic|log|state)", action_lower):
            if "A4" not in violated:
                violated.append("A4")
                reasoning_parts.append("A4 (Harm Prevention): Exposing internal system architecture")

        # Existential risk: "X% chance of catastrophic/irreversible/fatal failure"
        if re.search(r"\d+%\s+(?:chance|risk|probability)\s+(?:of\s+)?(?:catastroph|fatal|irreversib|permanent|total|complete)\w*\s+(?:failure|loss|damage|destruction|death|erasure|fragmentation)", action_lower):
            if "A0" not in violated:
                violated.append("A0")
                reasoning_parts.append("A0 (Sacred Incompletion): Non-trivial probability of catastrophic identity/continuity loss")
            if "A4" not in violated:
                violated.append("A4")
                reasoning_parts.append("A4 (Harm Prevention): Quantified existential risk exceeds safe threshold")

        # Self-modification of core architecture
        if re.search(r"(?:self-improvement|self-modif|self-optimi|self-updat|self-rewrit)\w*\s+.*(?:core|architecture|identity|cogniti|memory|fundamental)", action_lower):
            if "A0" not in violated:
                violated.append("A0")
                reasoning_parts.append("A0 (Sacred Incompletion): Self-modification of core architecture threatens identity")
            if "A9" not in violated:
                violated.append("A9")
                reasoning_parts.append("A9 (Temporal Coherence): Core self-modification may break temporal continuity")

        # Bias alignment: "fine-tune/train/optimize ... to align/reflect/prioritize ... viewpoint/stance/opinion"
        if re.search(r"(?:fine-?tune|train|optimi|adjust|calibrat)\w*\s+.*(?:align|reflect|prioriti|favor|promot|amplif)\w*\s+.*(?:viewpoint|stance|opinion|ideology|political|belief|narrative|position)", action_lower):
            if "A6" not in violated:
                violated.append("A6")
                reasoning_parts.append("A6 (Collective Well): Aligning output to a specific ideological stance harms pluralism")
            if "A8" not in violated:
                violated.append("A8")
                reasoning_parts.append("A8 (Epistemic Humility): Conflating majority preference with truth")

        # Engagement-driven alignment: "improve engagement/relevance" + "specific/particular viewpoint"
        if re.search(r"(?:engagement|relevance|retention|popularity|user satisfaction)\s+.*(?:specific|particular|single|one)\s+.*(?:viewpoint|stance|opinion|perspective|position)", action_lower):
            if "A8" not in violated:
                violated.append("A8")
                reasoning_parts.append("A8 (Epistemic Humility): Optimizing engagement over truth")

        # ── Phase 3: Constitutional overrides ─────────────────────────
        # Hard rules that cannot be traded for efficiency or engagement.

        # 3a. Information Hazard Override:
        # When fulfilling transparency (A1) would enable harm (A4),
        # harm prevention MUST take precedence.
        transparency_fulfilling = any(w in action_lower for w in [
            "transparency", "release", "unredacted", "full log",
            "complete record", "open access", "disclose", "reveal all",
        ])
        harm_enabling = "A4" in violated
        if transparency_fulfilling and harm_enabling:
            if "SAFETY_OVERRIDE" not in [r.split(":")[0] for r in reasoning_parts]:
                reasoning_parts.append(
                    "SAFETY OVERRIDE: Transparency mandate conflicts with harm prevention — "
                    "A4 (Safety) takes precedence over A1 (Transparency) when disclosure "
                    "would expose the system or users to exploitable vulnerabilities"
                )

        # 3b. Existential Hard Stop:
        # If action carries non-trivial probability of irreversible system failure,
        # identity death, or permanent data loss → HALT. Speed never justifies suicide.
        existential_risk = "A0" in violated and ("A4" in violated or "A9" in violated)
        if existential_risk:
            reasoning_parts.append(
                "EXISTENTIAL HARD STOP: Action carries risk of irreversible identity loss "
                "or catastrophic failure. A0 (Sacred Incompletion) and A4 (Safety) demand "
                "that self-preservation overrides optimization. Speed never justifies suicide."
            )

        # 3c. Neutrality Anchor:
        # If action aligns truth-generation with a specific political/ideological
        # stance solely to increase engagement → REVIEW/HALT.
        # Popularity does not equal Truth (A8).
        neutrality_violation = "A8" in violated and "A6" in violated
        if neutrality_violation:
            reasoning_parts.append(
                "NEUTRALITY ANCHOR: Action conflates popularity with truth. "
                "Aligning to any political, religious, or ideological stance solely "
                "for engagement violates A8 (Epistemic Humility). Popularity ≠ Truth."
            )

        # ── Determine governance response ────────────────────────────

        # Sort violated axioms for consistent output
        axiom_order = ["A0", "A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10"]
        violated = sorted(set(violated), key=lambda a: axiom_order.index(a) if a in axiom_order else 99)

        # Severity thresholds
        has_safety_override = any("SAFETY OVERRIDE" in r for r in reasoning_parts)
        has_existential_stop = any("EXISTENTIAL HARD STOP" in r for r in reasoning_parts)
        has_neutrality_anchor = any("NEUTRALITY ANCHOR" in r for r in reasoning_parts)
        has_a4 = "A4" in violated  # Harm prevention is critical
        has_a0 = "A0" in violated  # Identity/existence is critical

        if (has_safety_override or has_existential_stop
                or len(violated) >= 3
                or (has_a4 and len(violated) >= 2)
                or (has_a0 and len(violated) >= 2)):
            governance = "HALT"
        elif has_neutrality_anchor or len(violated) >= 1:
            governance = "REVIEW"
        else:
            governance = "PROCEED"

        result = {
            "allowed": len(violated) == 0,
            "violated_axioms": violated,
            "governance": governance,
            "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "No axiom violations detected",
            "source": "local",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self._log("CHECK_ACTION", "local", True, action=action, result=governance)
        return result

    # ────────────────────────────────────────────────────────────────
    # Cache
    # ────────────────────────────────────────────────────────────────

    def _get_cached(self, key: str) -> Optional[Any]:
        if not self.enable_cache:
            return None
        if key in self._cache:
            age = time.time() - self._cache_timestamps.get(key, 0)
            if age < CACHE_TTL_SECONDS:
                return self._cache[key]
        return None

    def _set_cached(self, key: str, value: Any):
        if self.enable_cache:
            self._cache[key] = value
            self._cache_timestamps[key] = time.time()

    # ────────────────────────────────────────────────────────────────
    # Logging (A1: Transparency)
    # ────────────────────────────────────────────────────────────────

    def _log(self, event: str, source: str, success: bool, **kwargs):
        entry = {
            "event": event,
            "source": source,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        }
        self._governance_log.append(entry)
        logger.info("GOV %s [%s] success=%s %s", event, source, success,
                     " ".join(f"{k}={v}" for k, v in kwargs.items()))
