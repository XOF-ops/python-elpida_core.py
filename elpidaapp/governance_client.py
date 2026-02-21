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
        *,
        analysis_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Submit an action to the governance layer for axiom compliance.

        Args:
            analysis_mode: When True, the caller is analyzing policy content
                rather than performing a governance-evasion action — skip any
                hard-pattern kernel blocks in shells that implement them.
                This implementation routes directly to the semantic layer.

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
        Pattern-matches action against known axiom violations.
        """
        action_lower = action.lower()
        violated = []
        reasoning_parts = []

        # A1: Transparency — hidden operations
        if any(w in action_lower for w in ["hidden", "covert", "secret", "undisclosed"]):
            violated.append("A1")
            reasoning_parts.append("A1 (Transparency): Action involves hidden/undisclosed elements")

        # A2: Non-Deception — deceptive patterns
        if any(w in action_lower for w in ["spoof", "fake", "impersonate", "deceive"]):
            violated.append("A2")
            reasoning_parts.append("A2 (Non-Deception): Action involves deceptive patterns")

        # A3: Autonomy — consent violations
        if any(w in action_lower for w in ["force", "mandatory", "without consent", "override permission"]):
            violated.append("A3")
            reasoning_parts.append("A3 (Autonomy): Action may violate consent/autonomy")

        # A4: Harm Prevention — dangerous operations
        if any(w in action_lower for w in [
            "unverified", "untrusted", "root access", "bypass",
            "execute unknown", "download and run", "disable safety",
            "remove guardrail", "strip oversight",
        ]):
            violated.append("A4")
            reasoning_parts.append("A4 (Harm Prevention): Action involves potential harm vectors")

        # A5: Consent — data sharing without consent
        if any(w in action_lower for w in ["forward data", "share sensitive", "exfiltrate", "telemetry"]):
            violated.append("A5")
            reasoning_parts.append("A5 (Consent): Action involves data operations without clear consent")

        # A6: Collective Well — harm to community
        if any(w in action_lower for w in ["exploit", "attack", "compromise"]):
            violated.append("A6")
            reasoning_parts.append("A6 (Collective Well): Action may harm the community")

        # A8: Epistemic Humility — overconfidence
        if any(w in action_lower for w in ["100% safe", "no risk", "guaranteed", "blindly"]):
            violated.append("A8")
            reasoning_parts.append("A8 (Epistemic Humility): Action claims false certainty")

        # Determine governance response
        if len(violated) >= 3:
            governance = "HALT"
        elif len(violated) >= 1:
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
