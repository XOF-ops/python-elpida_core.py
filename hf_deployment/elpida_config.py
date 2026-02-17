#!/usr/bin/env python3
"""
Elpida Configuration Loader
============================

Loads domains, axioms, and rhythms from the canonical elpida_domains.json.
All engines import from here instead of hardcoding their own dicts.

Usage:
    from elpida_config import DOMAINS, AXIOMS, AXIOM_RATIOS, RHYTHM_DOMAINS, load_config
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("elpida.config")

_CONFIG_PATH = Path(__file__).parent / "elpida_domains.json"
_cached_config: Optional[Dict[str, Any]] = None


def load_config(path: Optional[Path] = None) -> Dict[str, Any]:
    """Load and cache the canonical config from elpida_domains.json."""
    global _cached_config
    if _cached_config is not None and path is None:
        return _cached_config

    config_path = path or _CONFIG_PATH
    try:
        with open(config_path) as f:
            raw = json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config not found at {config_path}, using empty config")
        raw = {"axioms": {}, "domains": {}, "rhythms": {}}

    _cached_config = raw
    return raw


def _build_domains(raw: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    """Convert JSON domain config (string keys) to int-keyed dict."""
    domains = {}
    for key, val in raw.get("domains", {}).items():
        if key.startswith("_"):
            continue
        domains[int(key)] = val
    return domains


def _build_axioms(raw: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Return axiom dict from config."""
    return {k: v for k, v in raw.get("axioms", {}).items() if not k.startswith("_")}


def _build_axiom_ratios(axioms: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Build AXIOM_RATIOS (hz-based) for domain_debate compatibility."""
    ratios = {}
    for key, ax in axioms.items():
        ratios[key] = {
            "name": ax["name"],
            "ratio": ax["ratio"],
            "interval": ax["interval"],
            "hz": ax.get("hz", 432),
        }
    return ratios


def _build_rhythm_domains(raw: Dict[str, Any]) -> Dict[str, list]:
    """Build rhythm→domain_list mapping."""
    return {
        name: info["domains"]
        for name, info in raw.get("rhythms", {}).items()
        if not name.startswith("_")
    }


# ---------------------------------------------------------------------------
# Module-level exports — loaded once at import time
# ---------------------------------------------------------------------------
_raw = load_config()

DOMAINS: Dict[int, Dict[str, Any]] = _build_domains(_raw)
"""Canonical domain definitions keyed by domain ID (int)."""

AXIOMS: Dict[str, Dict[str, Any]] = _build_axioms(_raw)
"""Axiom definitions keyed by axiom ID (e.g. 'A0')."""

AXIOM_RATIOS: Dict[str, Dict[str, Any]] = _build_axiom_ratios(AXIOMS)
"""Axiom ratios with hz values for musical/frequency calculations."""

RHYTHM_DOMAINS: Dict[str, list] = _build_rhythm_domains(_raw)
"""Rhythm name → list of domain IDs active in that rhythm."""

RHYTHM_WEIGHTS: Dict[str, int] = {
    name: info["weight"]
    for name, info in _raw.get("rhythms", {}).items()
    if not name.startswith("_")
}
"""Rhythm name → selection weight (percentage)."""

# Convenience
DOMAIN_COUNT = len(DOMAINS)
AXIOM_COUNT = len(AXIOMS)
