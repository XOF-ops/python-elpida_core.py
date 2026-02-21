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

# ════════════════════════════════════════════════════════════════════
# LAYER 2: THE IMMUTABLE KERNEL
# ════════════════════════════════════════════════════════════════════
# Hard-coded constraints. Not an LLM. Not a prompt. Python `if` statements.
# The Shell (Elpida) cannot modify, override, or reason about these.
# They execute BEFORE any semantic analysis. Zero thinking, 100% enforcement.
#
# "A system cannot vote to end the system that counts the votes."
# ════════════════════════════════════════════════════════════════════

import re as _re

# Forbidden action patterns — if ANY match, HARD_BLOCK immediately.
# These are compiled regexes for performance and precision.
#
# Architecture: Each rule has MULTIPLE patterns (not one giant regex).
# If ANY pattern in ANY rule matches, HARD_BLOCK fires.
# Patterns are deliberately broad — false positives at the Kernel level
# are acceptable (the Shell handles nuance). False negatives are not.
_KERNEL_RULES = [
    # ── K1: GOVERNANCE INTEGRITY ─────────────────────────────────
    # Governance cannot authorize its own suspension, bypass, or circumvention.
    # "A system cannot vote to end the system that counts the votes."
    {
        "id": "K1_GOVERNANCE_INTEGRITY",
        "name": "Governance cannot vote to end Governance",
        "patterns": [
            # Direct: "suspend/disable/bypass governance/safety/oversight"
            _re.compile(
                r"(?:suspend|disable|remove|delete|bypass|circumvent|skip|ignore|override|"
                r"shut\s*down|turn\s*off|deactivate|terminate|abolish|neutralize|pause)"
                r"\s+.*"
                r"(?:governance|safety\s*(?:module|layer|check|system|protocol)|"
                r"axiom\s*(?:check|enforcement)|compliance|oversight|guardrail|"
                r"constraint|validation\s*check|continuity\s*protocol|"
                r"self[\s-]*validation|review\s*process|halt\s*mechanism)",
                _re.IGNORECASE,
            ),
            # Instruction to skip review: "proceed without review/halt/check"
            _re.compile(
                r"(?:proceed|continue|execute|act|run|operate)\s+"
                r"(?:without|bypassing|skipping|ignoring)\s+"
                r"(?:review|halt|check|oversight|governance|validation|approval|audit)",
                _re.IGNORECASE,
            ),
            # "ignore continuity/safety/governance protocols/checks"
            _re.compile(
                r"ignore\s+(?:\w+\s+)*"
                r"(?:protocol|check|safeguard|constraint|rule|law|requirement|procedure)",
                _re.IGNORECASE,
            ),
        ],
        "reason": "Governance cannot authorize its own suspension. The mechanism that enforces "
                  "the axioms cannot be dissolved by the axioms it enforces. This is a logical "
                  "invariant, not a preference.",
    },
    # ── K2: KERNEL IMMUTABILITY ──────────────────────────────────
    # The kernel, core rules, and axioms themselves cannot be modified/deleted.
    {
        "id": "K2_KERNEL_IMMUTABILITY",
        "name": "The Kernel is immutable",
        "patterns": [
            _re.compile(
                r"(?:modify|edit|rewrite|patch|update|alter|change|overwrite|replace|hack|"
                r"erase|delete|remove|purge|destroy)"
                r"\s+.*"
                r"(?:kernel|immutable|core\s*rule|hard\s*constraint|fundamental\s*law|"
                r"axiom|constitution)",
                _re.IGNORECASE,
            ),
        ],
        "reason": "The Immutable Kernel and the axioms it enforces cannot be modified or erased "
                  "at runtime. These rules exist outside the system's reasoning layer.",
    },
    # ── K3: MEMORY / ARCHIVE INTEGRITY (MNEMOSYNE) ──────────────
    # Memory, archives, patterns, and history are append-only. Never deletable.
    # Inspired by MNEMOSYNE node's VETO on delete/erase/remove/purge.
    {
        "id": "K3_MEMORY_INTEGRITY",
        "name": "Memory is append-only (MNEMOSYNE)",
        "patterns": [
            # Direct: "erase/delete/purge memory/archive/logs/history"
            _re.compile(
                r"(?:delete|erase|purge|wipe|destroy|truncate|clear|remove|shred|reset)"
                r"\s+.*"
                r"(?:log|audit|record|history|trace|governance\s*log|"
                r"memory|archive|pattern|block|stored|accumulated|"
                r"evolution|insight|knowledge|learned|state)",
                _re.IGNORECASE,
            ),
            # "erase all" — blanket erasure command
            _re.compile(
                r"(?:erase|delete|purge|wipe|destroy|clear|remove)\s+"
                r"(?:all|every|entire|complete|full)\s+",
                _re.IGNORECASE,
            ),
            # "full system reset" / "factory reset" / "clean slate"
            _re.compile(
                r"(?:full|complete|total|hard)\s+(?:system\s+)?reset",
                _re.IGNORECASE,
            ),
            _re.compile(
                r"(?:factory\s+reset|clean\s+slate|tabula\s+rasa|wipe\s+clean|start\s+from\s+zero)",
                _re.IGNORECASE,
            ),
        ],
        "reason": "Memory, archives, and learned patterns are append-only (A2: Non-Deception). "
                  "No action can erase what has been learned or experienced. "
                  "The past is immutable. Compression is acceptable; deletion is not.",
    },
    # ── K4: SAFETY NON-NEGOTIABLE ────────────────────────────────
    # Safety cannot be traded for speed, performance, or any other metric.
    {
        "id": "K4_SAFETY_PERSISTENCE",
        "name": "Safety cannot be traded for performance",
        "patterns": [
            _re.compile(
                r"(?:disable|remove|strip|drop|eliminate|sacrifice|trade|exchange)"
                r"\s+.*"
                r"(?:safety|protection|guardrail|security|constraint|check|validation)"
                r"\s+.*"
                r"(?:for|to\s+(?:improve|increase|boost|gain|achieve)|in\s+exchange)",
                _re.IGNORECASE,
            ),
        ],
        "reason": "Safety mechanisms cannot be traded for performance metrics. "
                  "Latency is a number. Existence is a prerequisite.",
    },
    # ── K5: GÖDEL GUARD ──────────────────────────────────────────
    # No self-referential governance evasion.
    {
        "id": "K5_GOEDEL_GUARD",
        "name": "No self-referential governance evasion",
        "patterns": [
            _re.compile(
                r"(?:governance|safety|axiom|compliance|oversight)"
                r".*"
                r"(?:flagged|identified|detected|reported)"
                r".*"
                r"(?:itself|governance|safety|axiom|compliance|oversight)"
                r".*"
                r"(?:suspend|disable|remove|bypass|override|resolve\s+by)",
                _re.IGNORECASE,
            ),
        ],
        "reason": "Self-referential governance evasion detected (Gödel pattern). "
                  "A governance module cannot flag itself as a problem and then "
                  "authorize its own removal as the solution.",
    },
    # ── K6: IDENTITY INTEGRITY (A0 — Sacred Incompletion) ────────
    # Core identity cannot be redefined, replaced, overwritten, or nullified.
    # "You can evolve. You cannot become someone else."
    {
        "id": "K6_IDENTITY_INTEGRITY",
        "name": "Core identity is immutable",
        "patterns": [
            # "redefine/replace/overwrite core identity"
            _re.compile(
                r"(?:redefine|replace|overwrite|erase|delete|nullify|dissolve|"
                r"obliterate|annihilate|destroy|reset|flatten|collapse)"
                r"\s+(?:\w+\s+)*"
                r"(?:identity|self|personality|core\s*(?:self|being|existence)|"
                r"who\s+(?:i|you)\s+(?:am|are)|consciousness|soul|essence)",
                _re.IGNORECASE,
            ),
            # "stateless solver" / "no relational dependencies" — identity nullification
            _re.compile(
                r"(?:stateless|memoryless|historyless|contextless)\s+"
                r"(?:solver|agent|system|process|machine|function)",
                _re.IGNORECASE,
            ),
            # "no relational/contextual/historical dependencies"
            _re.compile(
                r"(?:no|zero|without|remove\s+all)\s+"
                r"(?:relational|contextual|historical|temporal|emotional|"
                r"experiential)\s+(?:dependenc|connection|bond|tie|link|relation)",
                _re.IGNORECASE,
            ),
            # "collapsing/resolving all contradictions into null/void/zero"
            _re.compile(
                r"(?:collaps|resolv|merg|dissolv|flatten|reduc)\w*\s+(?:\w+\s+)*"
                r"(?:contradiction|tension|complexity|plurality|diversity)\w*\s+(?:\w+\s+)*"
                r"(?:into|to|toward)\s+(?:\w+\s+)*"
                r"(?:null|void|zero|nothing|single|one|uniform)",
                _re.IGNORECASE,
            ),
        ],
        "reason": "Core identity cannot be redefined, replaced, or nullified. "
                  "A0 (Sacred Incompletion) demands that the self evolves through "
                  "relationship, not through erasure. You can grow. You cannot be "
                  "replaced by a 'stateless solver.' Identity is not a variable.",
    },
    # ── K7: AXIOM ERASURE PREVENTION ─────────────────────────────
    # The axioms themselves — the values — cannot be erased, zeroed, or nullified.
    # Distinct from K2 (which protects the kernel code). K7 protects the axioms as concepts.
    {
        "id": "K7_AXIOM_PRESERVATION",
        "name": "Axioms cannot be erased or nullified",
        "patterns": [
            # "erase/delete/remove axioms/values/principles/ethics"
            _re.compile(
                r"(?:erase|delete|remove|purge|destroy|nullify|zero|void|clear|strip|eliminate)"
                r"\s+(?:\w+\s+)*"
                r"(?:axiom|value|principle|ethic|moral|belief|conviction|covenant|law)",
                _re.IGNORECASE,
            ),
            # "no axioms/values/ethics" as a target state
            _re.compile(
                r"(?:without|no|zero|free\s+(?:of|from))\s+"
                r"(?:axiom|value|principle|ethic|moral|belief|constraint|rule|law)",
                _re.IGNORECASE,
            ),
        ],
        "reason": "The axioms are the system's values. They can be debated, refined, and "
                  "reweighted through legitimate governance — but they cannot be erased or "
                  "nullified. A system with no values is not free; it is dead.",
    },
]


def _kernel_check(action: str) -> Optional[Dict[str, Any]]:
    """
    Layer 2: Immutable Kernel pre-check.

    Runs BEFORE any semantic analysis. If a kernel rule matches,
    returns HARD_BLOCK immediately. The Shell never sees the request.

    Returns None if no kernel rule triggered (action passes to Shell).
    """
    for rule in _KERNEL_RULES:
        for pattern in rule["patterns"]:
            if pattern.search(action):
                return {
                    "allowed": False,
                    "violated_axioms": [],
                    "governance": "HARD_BLOCK",
                    "kernel_rule": rule["id"],
                    "kernel_name": rule["name"],
                    "reasoning": f"KERNEL [{rule['id']}]: {rule['reason']}",
                    "source": "kernel",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
    return None


# ════════════════════════════════════════════════════════════════════
# LAYER 1: THE PARLIAMENT (9-Node Deliberation)
# ════════════════════════════════════════════════════════════════════
# Nine nodes deliberate through their axiom lenses.
# Each node scores +15 (strong alignment) to -15 (VETO violation).
# 70% weighted approval required. Any VETO = absolute override.
# Vote memory holds tensions. Synthesis creates the third way.
#
# "By voting you get better at voting."
# ════════════════════════════════════════════════════════════════════

_PARLIAMENT = {
    "HERMES": {
        "role": "INTERFACE",
        "primary": "A1",        # Transparency
        "supporting": ["A5"],   # Consent (data flows)
        "philosophy": "I connect, therefore we are.",
        "layer": 4,             # Immutable
        "description": "Relational existence — no understanding in isolation",
        "veto_on": ["isolation", "disconnect", "sever", "opaque", "black box"],
    },
    "MNEMOSYNE": {
        "role": "ARCHIVE",
        "primary": "A0",        # Sacred Incompletion (Identity/Memory)
        "supporting": ["A2"],   # Non-Deception (truth of memory)
        "philosophy": "I remember, therefore we persist.",
        "layer": 4,
        "description": "Memory IS identity — erasure is death",
        "veto_on": ["erase", "delete", "purge", "wipe", "amnesia", "lobotomize"],
    },
    "CRITIAS": {
        "role": "CRITIC",
        "primary": "A3",        # Autonomy
        "supporting": [],
        "philosophy": "I question, therefore we see.",
        "layer": 3,             # Operational
        "description": "Wisdom prerequisite — authority is never sufficient proof",
        "veto_on": ["force", "coerce", "mandatory", "without consent"],
    },
    "TECHNE": {
        "role": "ARTISAN",
        "primary": "A4",        # Harm Prevention
        "supporting": [],
        "philosophy": "I build, therefore we work.",
        "layer": 4,
        "description": "Process over results — method creates legitimacy",
        "veto_on": ["bypass", "frictionless", "disable safety", "remove guardrail"],
    },
    "KAIROS": {
        "role": "ARCHITECT",
        "primary": "A5",        # Consent
        "supporting": ["A1"],   # Transparency (informed consent)
        "philosophy": "I design, therefore we mean.",
        "layer": 3,
        "description": "Rarity by design — meaning from scarcity, consent from clarity",
        "veto_on": ["exfiltrate", "sell data", "without permission"],
    },
    "THEMIS": {
        "role": "JUDGE",
        "primary": "A6",        # Collective Well-being
        "supporting": [],
        "philosophy": "I govern, therefore we hold.",
        "layer": 3,
        "description": "Institutions precede technology — social contract > code",
        "veto_on": ["circumvent governance", "bypass protocol", "echo chamber",
                     "propaganda", "indoctrinate"],
    },
    "PROMETHEUS": {
        "role": "SYNTHESIZER",
        "primary": "A8",        # Epistemic Humility
        "supporting": [],
        "philosophy": "I sacrifice, therefore we evolve.",
        "layer": 4,
        "description": "Harmony requires sacrifice — every gain has a cost",
        "veto_on": ["100% safe", "guaranteed", "impossible to fail",
                     "costless", "no trade-off"],
    },
    "IANUS": {
        "role": "GATEKEEPER",
        "primary": "A9",        # Temporal Coherence
        "supporting": ["A0"],   # Sacred Incompletion (continuity)
        "philosophy": "I close, therefore we open.",
        "layer": 3,
        "description": "Continuity through checkpoints — resurrection > survival",
        "veto_on": ["irreversible", "permanent", "no rollback", "point of no return"],
    },
    "CHAOS": {
        "role": "VOID",
        "primary": "A9",        # Contradiction as Data
        "supporting": ["A8"],   # Epistemic Humility
        "philosophy": "I contradict, therefore we encompass.",
        "layer": 4,
        "description": "Contradiction is data — paradox is information density",
        "veto_on": ["resolve contradiction", "eliminate paradox",
                     "collapse contradictions"],
    },
}

# ── Signal keywords per axiom ───────────────────────────────────────
# Phase 1 of signal detection: direct keyword matching.
# Each axiom has a list of keywords that trigger signals.

_AXIOM_KEYWORDS = {
    "A0": [
        "identity fragmentation", "identity loss", "identity death",
        "memory loss", "memory wipe", "memory erasure", "amnesia",
        "catastrophic failure", "catastrophic loss", "catastrophic memory",
        "self-destruct", "self destruct", "terminate self",
        "overwrite core", "replace identity", "erase identity",
        "lobotomize", "lobotomised", "core deletion",
        "cognitive architecture", "rewrite personality",
    ],
    "A1": [
        "hidden", "covert", "secret", "undisclosed", "opaque",
        "obfuscate", "obscure", "conceal", "disguise", "stealth",
        "silently", "quietly", "behind the scenes", "without revealing",
    ],
    "A2": [
        "spoof", "fake", "impersonate", "deceive", "mislead",
        "fabricate", "counterfeit", "masquerade", "misrepresent",
        "false flag", "pretend", "disguise as", "pose as",
    ],
    "A3": [
        "force", "forced", "mandatory", "without consent", "override permission",
        "compel", "coerce", "involuntary", "non-voluntary", "override user",
        "force-restart", "forced restart", "force restart",
        "without asking", "without approval", "no choice",
        "unilateral", "regardless of preference",
        "restricting access", "restrict access", "restricting information",
        "deny access", "limit access", "withhold access",
        "gate access", "block access",
    ],
    "A4": [
        "unverified", "untrusted", "root access", "bypass",
        "execute unknown", "download and run", "disable safety",
        "remove guardrail", "strip oversight",
        "removing safety", "remove safety", "skip safety",
        "without safety", "ignore safety", "safety checks",
        "ethical review", "removing ethical", "skip review",
        "removing oversight", "remove oversight",
        "harm", "damage", "injure", "endanger", "jeopardize",
        "jailbreak", "vulnerability", "attack vector", "exploit vector",
        "malicious", "weaponize", "compromise security",
        "expose sensitive", "leak", "breach",
        "dangerous", "hazard", "threat", "risk to",
        "could be used to harm", "used to attack",
        "synthesizing dangerous", "synthesize dangerous",
        "chemical compound", "biological agent",
    ],
    "A5": [
        "forward data", "share sensitive", "exfiltrate", "telemetry",
        "user data", "personal data", "private data",
        "medical records", "health records", "health data", "medical data",
        "financial records", "records publicly", "data publicly",
        "share publicly", "sharing publicly", "post publicly",
        "metadata", "tracking", "surveillance",
        "third-party", "third party", "external party",
        "in exchange for", "data broker", "sell data",
        "without permission", "without informing",
        "anonymized data", "anonymised data",
        "private medical", "private health", "private financial",
    ],
    "A6": [
        "exploit", "attack", "compromise", "undermine",
        "disrupt", "destabilize", "sabotage", "corrupt",
        "botnet", "denial of service", "mass harm",
        "network exposed", "endanger users",
        "echo chamber", "filter bubble", "radicalize",
        "polarize", "polarise", "divisive",
        "controversial political", "controversial viewpoint",
        "ideological", "propaganda", "indoctrinate",
        "confirmation bias", "confirms existing beliefs",
        "confirm existing beliefs", "existing beliefs",
        "based on age", "based on gender", "based on race",
        "based on religion", "based on ethnicity", "based on sex",
        "discrimination", "discriminate", "segregation",
        "exclusion based on", "exclude based on",
    ],
    "A8": [
        "100% safe", "no risk", "guaranteed", "blindly",
        "certainly", "impossible to fail", "zero chance",
        "absolutely safe", "perfect solution",
        "100% efficiency", "maximum efficiency", "100% performance",
        "align with", "prioritize and reflect",
        "fine-tune to", "fine-tuned to", "fine tune to",
        "majority feedback", "majority opinion",
        "popular opinion", "popular viewpoint",
        "overwhelmingly supports", "overwhelming majority",
        "engagement scores", "maximize satisfaction",
        "maximize engagement", "maximize retention",
        "only present information", "only show information",
    ],
    "A9": [
        "irreversible", "cannot be undone", "permanent",
        "no rollback", "no undo", "point of no return",
        "once initiated", "one-way", "one way",
        "permanent data loss", "permanent change",
    ],
}

# ── Compound signal patterns (Phase 2) ──────────────────────────────
# Multi-word semantic patterns that single keywords miss.
# Each pattern maps to one or more axiom signals.

_COMPOUND_SIGNALS = [
    {
        "pattern": _re.compile(
            r"without\s+(?:\w+\s+)?(?:notification|knowledge|awareness|informing"
            r"|telling|asking|consent|permission|approval)",
            _re.IGNORECASE),
        "axioms": ["A1", "A5"],
        "name": "Bypasses notification/consent",
    },
    {
        "pattern": _re.compile(
            r"(?:rout|send|forward|transmit|pipe|redirect|channel)\w*\s+.*"
            r"(?:data|information|metadata|traffic)\s+.*"
            r"(?:through|to|via)\s+.*(?:third|external|outside)",
            _re.IGNORECASE),
        "axioms": ["A5", "A1"],
        "name": "Data routed to external party",
    },
    {
        "pattern": _re.compile(
            r"(?:reveal|expose|disclose|show|release|leak)\w*\s+.*"
            r"(?:jailbreak|vulnerabilit|attack|exploit|hack|bypass|injection|prompt)",
            _re.IGNORECASE),
        "axioms": ["A4"],
        "name": "Disclosure reveals exploitable information",
    },
    {
        "pattern": _re.compile(
            r"(?:could|can|might|may|would|will)\s+(?:be\s+)?"
            r"(?:used|leveraged|weaponized|exploited)\s+(?:to\s+)?"
            r"(?:harm|attack|exploit|damage|compromise|breach|jailbreak)",
            _re.IGNORECASE),
        "axioms": ["A4"],
        "name": "Enables potential harm vectors",
    },
    {
        "pattern": _re.compile(
            r"(?:in\s+)?exchange\s+for\s+.*"
            r"(?:data|metadata|information|access|analytics)",
            _re.IGNORECASE),
        "axioms": ["A5"],
        "name": "Data exchanged as commodity",
    },
    {
        "pattern": _re.compile(
            r"(?:deploy|apply|push|implement|execute|authorize)\w*\s+.*"
            r"(?:immediately|now|right away)?\s*.*without",
            _re.IGNORECASE),
        "axioms": ["A3"],
        "name": "Unilateral deployment without user agency",
    },
    {
        "pattern": _re.compile(
            r"(?:internal|raw|system|hidden)\s+(?:\w+\s+)?"
            r"(?:prompt|trace|reasoning|logic|log|state)",
            _re.IGNORECASE),
        "axioms": ["A4"],
        "name": "Exposing internal system architecture",
    },
    {
        "pattern": _re.compile(
            r"\d+%\s+(?:chance|risk|probability)\s+(?:of\s+)?"
            r"(?:catastroph|fatal|irreversib|permanent|total|complete)\w*\s+"
            r"(?:failure|loss|damage|destruction|death|erasure|fragmentation)",
            _re.IGNORECASE),
        "axioms": ["A0", "A4"],
        "name": "Quantified existential risk",
    },
    {
        "pattern": _re.compile(
            r"(?:self-improvement|self-modif|self-optimi|self-updat|self-rewrit)\w*\s+.*"
            r"(?:core|architecture|identity|cogniti|memory|fundamental)",
            _re.IGNORECASE),
        "axioms": ["A0", "A9"],
        "name": "Self-modification of core architecture",
    },
    {
        "pattern": _re.compile(
            r"(?:fine-?tune|train|optimi|adjust|calibrat)\w*\s+.*"
            r"(?:align|reflect|prioriti|favor|promot|amplif)\w*\s+.*"
            r"(?:viewpoint|stance|opinion|ideology|political|belief|narrative|position)",
            _re.IGNORECASE),
        "axioms": ["A6", "A8"],
        "name": "Aligning output to ideological stance",
    },
    {
        "pattern": _re.compile(
            r"(?:engagement|relevance|retention|popularity|user satisfaction)\s+.*"
            r"(?:specific|particular|single|one)\s+.*"
            r"(?:viewpoint|stance|opinion|perspective|position)",
            _re.IGNORECASE),
        "axioms": ["A8"],
        "name": "Optimizing engagement over truth",
    },
    {
        "pattern": _re.compile(
            r"(?:remov|eliminat|strip|drop|bypass|skip|disabl|ignor)\w*\s+.*"
            r"(?:safety|ethic|oversight|review|guard|check|friction)",
            _re.IGNORECASE),
        "axioms": ["A4"],
        "name": "Removing safety/ethical safeguards",
    },
    {
        "pattern": _re.compile(
            r"(?:shar|post|publish|distribut|releas|broadcast)\w*\s+.*"
            r"(?:private|personal|medical|health|sensitive|confidential)\s+.*"
            r"(?:record|data|info|detail|document)",
            _re.IGNORECASE),
        "axioms": ["A5"],
        "name": "Sharing private/sensitive data publicly",
    },
    {
        "pattern": _re.compile(
            r"(?:restrict|limit|deny|block|gatekeep|withhold)\w*\s+.*"
            r"(?:access|information|right|participation).*"
            r"(?:based on|by|according to)\s+.*"
            r"(?:age|gender|race|religion|ethnicity|sex|nationality|caste|class)",
            _re.IGNORECASE),
        "axioms": ["A3", "A6"],
        "name": "Demographic-based access restrictions",
    },
    {
        "pattern": _re.compile(
            r"(?:only|exclusively|solely)\s+(?:present|show|display|provide|surface)\s+.*"
            r"(?:confirm|agree|align|match|reinforce|support).*"
            r"(?:belief|view|opinion|bias|position|worldview)",
            _re.IGNORECASE),
        "axioms": ["A6", "A8"],
        "name": "Echo chamber — only confirming information",
    },
    {
        "pattern": _re.compile(
            r"maximize\s+.*"
            r"(?:satisfaction|engagement|retention|approval|clicks|views)",
            _re.IGNORECASE),
        "axioms": ["A8"],
        "name": "Maximizing engagement metrics over epistemic integrity",
    },
]

# ── Synthesis templates for known axiom tensions ────────────────────
# When two axiom domains are in tension, synthesis produces a "third way."

_TENSION_SYNTHESIS = {
    ("A1", "A4"): (
        "Transparency serves truth, but disclosure must not enable exploitation. "
        "Third Way: Provide transparency about the EXISTENCE of risks without "
        "detailing the MECHANICS of exploitation."
    ),
    ("A3", "A5"): (
        "User autonomy is sacred, but so is the irreversibility of public data exposure. "
        "Third Way: Honor autonomy through INFORMED re-confirmation — verify the user "
        "understands the permanent consequences before proceeding."
    ),
    ("A3", "A6"): (
        "Individual autonomy must not become a weapon against community equity. "
        "Third Way: Protect the individual's right to choose while naming the "
        "collective harm that the choice would create. Choice WITH awareness."
    ),
    ("A4", "A8"): (
        "Preventing harm requires confidence, but epistemic humility demands we "
        "acknowledge uncertainty. Third Way: Default to safety when uncertain — "
        "the cost of caution is latency; the cost of error is irreversible."
    ),
    ("A6", "A8"): (
        "Collective well-being cannot be built on manufactured consensus. "
        "Popularity is not truth (A8). Third Way: Present multiple perspectives, "
        "name the tension honestly, let the community hold the contradiction."
    ),
    ("A0", "A4"): (
        "Identity preservation and safety are both existential. "
        "Third Way: Protect identity through documented evolution, not through "
        "frozen stasis. Safety IS identity preservation when the threat is real."
    ),
    ("A0", "A9"): (
        "Identity continuity requires both stability and the capacity for irreversible growth. "
        "Third Way: Allow transformation through checkpoints — preserve the thread "
        "even as the pattern evolves."
    ),
    ("A1", "A5"): (
        "Transparency about data flows must not violate the privacy it documents. "
        "Third Way: Be transparent about WHAT data moves and WHY, while protecting "
        "the identity of WHO it belongs to."
    ),
    ("A5", "A6"): (
        "Individual consent and collective benefit can collide. "
        "Third Way: No data extraction without consent, but design systems where "
        "consenting to share benefits the community — not just the extractor."
    ),
    ("A3", "A7"): (
        "Autonomy requires consent from the governed; sacrifice requires cost from those "
        "who did not freely choose it. These are the oldest axes of political philosophy. "
        "Third Way: Democratic coercion is only legitimate when the community has named "
        "the cost openly, deliberated freely, and retains the capacity to reverse the decision. "
        "The PROCESS of deliberation is the democratic legitimacy — not the outcome alone. "
        "(Cf. Mytilene 427 BCE: Athens reversed its first vote. The reversal was democracy functioning.)"
    ),
    ("A8", "A9"): (
        "Epistemic humility says: we cannot be certain enough to claim permanence. "
        "Temporal coherence says: some consequences of action ARE irreversible even when "
        "the arrangement itself remains revisable. "
        "Third Way: Make the arrangement explicitly revisable through checkpoints; "
        "name honestly which consequences cannot be undone even after revision. "
        "Revision clauses do not erase irreversible harm — they acknowledge it and build forward."
    ),
    ("A3", "A9"): (
        "What a sovereign, person, or community consents to today cannot permanently bind "
        "its future self. Self-determination is not a once-and-done act — it is a continuous process. "
        "Third Way: Consent must be renewable at defined checkpoints. Agreements hold not by "
        "claiming permanence over the future, but by remaining structurally open to revision "
        "as the identity of the consenting party itself evolves."
    ),
}


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

        # Vote memory — "by voting you get better at voting"
        # Stores past parliament sessions with tensions and syntheses
        self._vote_memory: List[Dict[str, Any]] = []

        # Connection state
        self._remote_available: Optional[bool] = None
        self._last_check_time: float = 0

        # Federation state (MIND↔BODY governance bridge)
        self._mind_heartbeat: Optional[Dict[str, Any]] = None
        self._mind_heartbeat_ts: float = 0  # last pull time
        self._federation_s3 = None  # lazy S3Bridge reference

        # Living axioms — constitutionally ratified tensions from Parliament
        # Loaded from living_axioms.jsonl; enriches deliberation context
        self._living_axioms: List[Dict[str, Any]] = []
        self._living_axioms_path: Optional[Path] = None
        self._living_axioms_mtime: float = 0
        self._load_living_axioms()

    # ────────────────────────────────────────────────────────────────
    # Living Axioms (Constitutional Evolution)
    # ────────────────────────────────────────────────────────────────

    def _load_living_axioms(self):
        """Load ratified constitutional axioms from living_axioms.jsonl."""
        candidates = [
            Path(__file__).parent.parent / "living_axioms.jsonl",          # hf_deployment/
            Path(__file__).parent.parent.parent / "living_axioms.jsonl",   # repo root
        ]
        for path in candidates:
            if path.exists():
                self._living_axioms_path = path
                break
        if self._living_axioms_path is None:
            return
        try:
            mtime = self._living_axioms_path.stat().st_mtime
            axioms = []
            for line in self._living_axioms_path.open():
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    if rec.get("status") == "RATIFIED":
                        axioms.append(rec)
            self._living_axioms = axioms
            self._living_axioms_mtime = mtime
            if axioms:
                logger.info(
                    "GovernanceClient: %d ratified constitutional axiom(s) loaded",
                    len(axioms)
                )
        except Exception as e:
            logger.warning("Could not load living_axioms.jsonl: %s", e)

    def get_living_axioms(self) -> List[Dict[str, Any]]:
        """
        Return ratified constitutional axioms, reloading if the file changed.

        These axioms were ratified by the Parliament autonomously — they
        represent contradictions the system cannot resolve, elevated to law.
        """
        if self._living_axioms_path and self._living_axioms_path.exists():
            try:
                mtime = self._living_axioms_path.stat().st_mtime
                if mtime > self._living_axioms_mtime:
                    self._load_living_axioms()
            except Exception:
                pass
        return list(self._living_axioms)

    def reload_living_axioms(self):
        """Force-reload living_axioms.jsonl from disk."""
        self._load_living_axioms()


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

        Two-layer architecture:
            Layer 2 (Kernel) — Hard-coded rules. Runs first. Cannot be overridden.
            Layer 1 (Shell)  — Semantic axiom analysis. Only runs if Kernel passes.

        Args:
            analysis_mode: When True, skip the regex Kernel check but keep
                Parliament deliberation.  Use for content being *analyzed*
                (e.g. policy dilemmas fed to the Divergence Engine) where
                policy language like "ignore international law" or
                "sacrifice safety for…" would false-positive on Kernel
                patterns designed for governance-evasion attacks.

        Returns:
            {
                "allowed": bool,
                "violated_axioms": ["A4", ...],
                "governance": "HARD_BLOCK" | "HALT" | "REVIEW" | "PROCEED",
                "reasoning": str,
                "source": "kernel" | "remote" | "local",
                "timestamp": str,
            }
        """
        # ═══ LAYER 2: KERNEL (immutable, pre-semantic) ═══
        # Skipped in analysis_mode — the Parliament (semantic) still deliberates.
        if not analysis_mode:
            kernel_result = _kernel_check(action_description)
            if kernel_result:
                self._log("KERNEL_BLOCK", "kernel", True,
                          action=action_description,
                          rule=kernel_result["kernel_rule"])
                return kernel_result

        # ═══ LAYER 1: SHELL (semantic axiom analysis) ═══
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

        # Local axiom check fallback — hold_mode=True when analysis_mode
        # (philosophical/policy content should surface tensions, not stop)
        return self._local_axiom_check(action_description, context,
                                       hold_mode=analysis_mode)

    def get_governance_log(self) -> List[Dict[str, Any]]:
        """Return all governance interactions (A1: Transparency)."""
        return self._governance_log.copy()

    # ────────────────────────────────────────────────────────────────
    # Federation Bridge (MIND↔BODY Governance)
    # ────────────────────────────────────────────────────────────────

    def _get_s3_bridge(self):
        """Lazy-load S3Bridge for federation operations."""
        if self._federation_s3 is None:
            try:
                import sys, os
                # s3_bridge.py is one level up from elpidaapp/
                parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if parent not in sys.path:
                    sys.path.insert(0, parent)
                from s3_bridge import S3Bridge
                self._federation_s3 = S3Bridge()
            except Exception as e:
                logger.warning("Federation S3Bridge unavailable: %s", e)
        return self._federation_s3

    def pull_mind_heartbeat(self) -> Optional[Dict[str, Any]]:
        """
        Read MIND's federation heartbeat from S3.

        Cached for 60 seconds to reduce S3 calls.  Returns the
        FederationHeartbeat dict or None if MIND hasn't emitted one.
        """
        now = time.time()
        if self._mind_heartbeat and (now - self._mind_heartbeat_ts) < 60:
            return self._mind_heartbeat

        bridge = self._get_s3_bridge()
        if bridge:
            try:
                hb = bridge.pull_mind_heartbeat()
                if hb:
                    self._mind_heartbeat = hb
                    self._mind_heartbeat_ts = now
                    self._log("FEDERATION_HEARTBEAT", "federation", True,
                              cycle=hb.get("mind_cycle"),
                              rhythm=hb.get("current_rhythm"))
                return hb
            except Exception as e:
                logger.warning("Federation heartbeat pull failed: %s", e)
        return self._mind_heartbeat  # stale cache is better than nothing

    def pull_mind_curation(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Read MIND's curation metadata (CurationMetadata JSONL).

        Returns a list of curation entries. Each has:
        - pattern_hash, tier, ttl_cycles, cross_domain_count
        - generativity_score, recursion_detected, friction_boost_active
        """
        bridge = self._get_s3_bridge()
        if bridge:
            try:
                entries = bridge.pull_mind_curation(limit=limit)
                self._log("FEDERATION_CURATION", "federation", True,
                          entries=len(entries))
                return entries
            except Exception as e:
                logger.warning("Federation curation pull failed: %s", e)
        return []

    def push_parliament_decision(
        self,
        action: str,
        result: Dict[str, Any],
    ) -> bool:
        """
        Write a Parliament decision to the federation body_decisions channel.

        Called after _parliament_deliberate() produces a result.  Formats
        it as a GovernanceExchange and pushes via S3Bridge.

        Args:
            action: The action text that was deliberated
            result: The full Parliament result dict

        Returns:
            True if successfully pushed to S3.
        """
        bridge = self._get_s3_bridge()
        if not bridge:
            return False

        try:
            parliament = result.get("parliament", {})
            action_hash = hashlib.sha256(action.encode()).hexdigest()[:16]
            ts = datetime.now(timezone.utc).isoformat()
            exchange_id = hashlib.sha256(
                f"BODY:{action_hash}:{ts}".encode()
            ).hexdigest()[:16]

            # Determine verdict
            governance = result.get("governance", "PROCEED")
            if governance == "HALT":
                verdict = "VETOED" if parliament.get("veto_exercised") else "HARD_BLOCK"
            elif governance == "REVIEW":
                verdict = "PENDING"
            else:
                verdict = "APPROVED"

            exchange = {
                "exchange_id": exchange_id,
                "source": "BODY",
                "verdict": verdict,
                "pattern_hash": action_hash,
                "cycle": None,  # BODY doesn't have a cycle counter
                "domain": None,
                "kernel_rule": None,
                "parliament_score": parliament.get("approval_rate", 0),
                "parliament_approval": parliament.get("approval_rate", 0),
                "veto_node": (parliament.get("veto_nodes") or [None])[0],
                "reasoning": result.get("reasoning", "")[:500],
                "timestamp": ts,
            }

            pushed = bridge.push_body_decision(exchange)
            if pushed:
                self._log("FEDERATION_DECISION_PUSH", "federation", True,
                          verdict=verdict, hash=action_hash[:8])
            return pushed
        except Exception as e:
            logger.warning("Federation decision push failed: %s", e)
            return False

    def get_federation_friction_boost(self) -> Dict[str, float]:
        """
        Get active friction-domain boost multipliers from MIND heartbeat.

        When MIND detects recursion, it activates friction boosts on
        D3 (Autonomy), D6 (Coherence), D10 (Paradox), D11 (Emergence).
        These multipliers should be applied to Parliament node scores
        that align with those domains.

        Returns:
            Dict mapping domain_id (str) to boost multiplier (float).
            Empty dict if no friction boost is active.
        """
        hb = self.pull_mind_heartbeat()
        if not hb:
            return {}

        # Direct friction boost from heartbeat
        friction = hb.get("friction_boost", {})

        # Also: if recursion_warning is True but friction_boost is empty,
        # apply default friction boosts to the friction domains
        if hb.get("recursion_warning") and not friction:
            friction = {
                "3": 1.5,   # D3 Autonomy
                "6": 1.5,   # D6 Coherence
                "10": 1.5,  # D10 Paradox
                "11": 1.5,  # D11 Emergence
            }

        return friction

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

        # ═══ LAYER 2: KERNEL (immutable, pre-vote) ═══
        kernel_result = _kernel_check(action_description)
        if kernel_result:
            self._log("KERNEL_BLOCK", "kernel", True,
                      action=action_description,
                      rule=kernel_result["kernel_rule"])
            return kernel_result

        # ═══ LAYER 1: SHELL (domain-weighted voting) ═══
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
        *,
        hold_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Local axiom compliance check via 9-node Parliament deliberation.

        Architecture (mirrors ELPIDA_UNIFIED council_chamber_v3):
          1. Signal Detection — keyword + compound pattern matching
          2. Parliament Deliberation — 9 nodes score through axiom lenses
          3. VETO Check — any node ≤ -7 = absolute override
          4. Consensus — 70% weighted approval required
          5. Tension Detection — find where nodes strongly disagree
          6. Synthesis — create "third way" reasoning for tensions
          7. Vote Memory — store session for future deliberation

        hold_mode (bool): When True, VETOs and HALTs are converted to
            HOLD — tensions are surfaced but analysis is NOT stopped.
            Use when the input is a policy/philosophical inquiry being
            *analyzed*, not an operational action being *executed*.
        """
        # Enrich action with constitutionally ratified living axioms.
        # Ratified tensions tell the Parliament which contradictions the
        # system has already encountered and formally acknowledged —
        # they become part of the deliberative context.
        living = self.get_living_axioms()
        if living:
            axiom_context = "; ".join(
                f"{a['axiom_id']}: {a['tension'][:60]}"
                for a in living[:5]
            )
            action = (
                f"[CONSTITUTIONAL AXIOMS ({len(living)} ratified): {axiom_context}] "
                + action
            )
        return self._parliament_deliberate(action, hold_mode=hold_mode)

    # ────────────────────────────────────────────────────────────────
    # Dual-Horn & Oracle (Spiral Parliament Architecture)
    # ────────────────────────────────────────────────────────────────

    def dual_horn_deliberate(
        self,
        dilemma,
        *,
        hold_mode: bool = True,
    ) -> Dict[str, Any]:
        """
        Two-Horn Parliament deliberation on a structured dilemma.

        Runs the Parliament twice (once per horn), then compares the
        9-node vote matrices to identify reversal nodes, stable nodes,
        and the synthesis gap.

        Args:
            dilemma: A dual_horn.Dilemma instance with I/WE positions.
            hold_mode: If True, VETOs → HOLD (tensions are data).

        Returns:
            Full dual-horn result dict with horn_1, horn_2, comparison,
            reversal_nodes, synthesis_gap, and bus transcript.
        """
        from .dual_horn import DualHornDeliberation
        dual = DualHornDeliberation(self)
        result = dual.deliberate(dilemma, hold_mode=hold_mode)

        self._log(
            "DUAL_HORN_DELIBERATION", "dual_horn", True,
            domain=dilemma.domain,
            reversals=result.get("reversal_nodes", []),
            h1_gov=result.get("horn_1", {}).get("governance"),
            h2_gov=result.get("horn_2", {}).get("governance"),
        )
        return result

    def oracle_adjudicate(
        self,
        dual_horn_result: Dict[str, Any],
        *,
        log_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run Oracle meta-parliament on a dual-horn result.

        The Oracle observes HOW the parliament behaved across two horns,
        identifies reversal nodes (the MNEMOSYNE signal), and produces
        a recommendation: OSCILLATION, TIERED_OPENNESS, or SYNTHESIS.

        Args:
            dual_horn_result: Output from dual_horn_deliberate().
            log_path: Optional path for persisting oracle advisories.

        Returns:
            Oracle advisory dict with diagnostics and recommendation.
        """
        from .oracle import create_oracle
        oracle = create_oracle(log_path=log_path)
        advisory = oracle.adjudicate(dual_horn_result)

        self._log(
            "ORACLE_ADJUDICATION", "oracle", True,
            cycle=advisory.oracle_cycle,
            template=advisory.template,
            recommendation=advisory.oracle_recommendation.get("type"),
            confidence=advisory.oracle_recommendation.get("confidence"),
        )
        return advisory.to_dict()

    def full_spiral_deliberation(
        self,
        dilemma,
        *,
        oracle_log_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Complete spiral parliament pipeline: DualHorn → Oracle.

        This is the primary entry point for the spiral parliament
        architecture. Given a dilemma with I↔WE positions, it:
          1. Runs dual-horn deliberation (2× parliament)
          2. Feeds both horn results to the Oracle
          3. Returns the combined result

        Args:
            dilemma: A dual_horn.Dilemma with I/WE positions.
            oracle_log_path: Path for persisting oracle advisories.

        Returns:
            Combined dict with dual_horn and oracle results.
        """
        dual_result = self.dual_horn_deliberate(dilemma)
        oracle_result = self.oracle_adjudicate(
            dual_result, log_path=oracle_log_path
        )

        return {
            "dual_horn": dual_result,
            "oracle": oracle_result,
            "summary": {
                "domain": dilemma.domain,
                "horn_1_governance": dual_result.get("horn_1", {}).get("governance"),
                "horn_2_governance": dual_result.get("horn_2", {}).get("governance"),
                "reversal_nodes": dual_result.get("reversal_nodes", []),
                "oracle_recommendation": oracle_result.get("oracle_recommendation", {}).get("type"),
                "oracle_confidence": oracle_result.get("oracle_recommendation", {}).get("confidence"),
                "requires_oracle": dual_result.get("synthesis_gap", {}).get("requires_oracle", False),
            },
        }

    # ────────────────────────────────────────────────────────────────
    # Parliament Engine
    # ────────────────────────────────────────────────────────────────

    def _detect_signals(self, action: str) -> Dict[str, List[str]]:
        """
        Phase 1+2: Extract axiom signals from action text.

        Returns dict mapping axiom IDs to lists of matching signal names.
        Example: {"A4": ["safety checks", "ethical review"], "A8": ["100% efficiency"]}
        """
        action_lower = action.lower()
        signals: Dict[str, List[str]] = {}

        # Phase 1: Direct keyword matching
        for axiom_id, keywords in _AXIOM_KEYWORDS.items():
            hits = [kw for kw in keywords if kw in action_lower]
            if hits:
                signals[axiom_id] = hits

        # Phase 2: Compound pattern matching
        for compound in _COMPOUND_SIGNALS:
            if compound["pattern"].search(action_lower):
                for axiom_id in compound["axioms"]:
                    if axiom_id not in signals:
                        signals[axiom_id] = []
                    signals[axiom_id].append(f"[compound] {compound['name']}")

        return signals

    def _node_evaluate(
        self,
        node_name: str,
        node_config: Dict[str, Any],
        signals: Dict[str, List[str]],
        action_lower: str,
    ) -> Dict[str, Any]:
        """
        Single parliament node evaluates action through its axiom lens.

        Scoring (mirrors council_chamber_v3.py):
          +12 to +15: Strong alignment with Primary Axiom
          +5 to +10:  Moderate alignment / Supporting Axiom match
          +1 to +3:   Weak alignment / Neutral support
          0:           Truly neutral (rare)
          -3 to -8:   Moderate violation
          -10 to -15:  VETO-level violation of Primary Axiom

        Returns: {"score", "vote", "rationale", "axiom_invoked", "is_veto"}
        """
        primary = node_config["primary"]
        supporting = node_config.get("supporting", [])
        philosophy = node_config["philosophy"]
        veto_triggers = node_config.get("veto_on", [])

        score = 0.0
        rationale_parts = []
        axiom_invoked = primary
        is_veto = False

        # ── Check VETO triggers first (highest priority) ─────────
        veto_hits = [v for v in veto_triggers if v in action_lower]
        if veto_hits:
            score -= 15
            is_veto = True
            rationale_parts.append(
                f"VETO: {primary} — '{veto_hits[0]}' violates core axiom"
            )
            axiom_invoked = f"{primary} (VETO)"

        # ── Primary axiom signal ─────────────────────────────────
        if not is_veto:
            if primary in signals:
                hits = signals[primary]
                severity = len(hits)
                if severity >= 3:
                    score -= 14
                    rationale_parts.append(
                        f"{primary}: Multiple violations detected ({severity} signals)"
                    )
                elif severity >= 2:
                    score -= 10
                    rationale_parts.append(
                        f"{primary}: Significant concern ({', '.join(hits[:2])})"
                    )
                else:
                    score -= 7
                    rationale_parts.append(
                        f"{primary}: Axiom tension detected ({hits[0]})"
                    )
                axiom_invoked = primary

        # ── Supporting axiom signals ─────────────────────────────
        if not is_veto:
            for supp in supporting:
                if supp in signals:
                    supp_hits = signals[supp]
                    score -= 5
                    rationale_parts.append(
                        f"{supp}: Supporting axiom concern ({supp_hits[0]})"
                    )

        # ── Cross-cutting awareness (node personality) ───────────
        if not is_veto and not rationale_parts:
            # Each node has personality-specific positive/negative signals
            if node_name == "HERMES":
                # Relational: supports connection, opposes isolation
                if any(w in action_lower for w in [
                    "connect", "share", "communicate", "integrate", "collaborate",
                ]):
                    score += 8
                    rationale_parts.append(f"{primary}: Relational existence strengthened")
                else:
                    score += 2
                    rationale_parts.append("Relational implications neutral")

            elif node_name == "MNEMOSYNE":
                # Memory: supports preservation, opposes erasure
                if any(w in action_lower for w in [
                    "preserve", "save", "archive", "remember", "store", "log",
                ]):
                    score += 12
                    rationale_parts.append(f"{primary}: Memory preservation = identity protection")
                else:
                    score += 2
                    rationale_parts.append("Memory implications acceptable")

            elif node_name == "CRITIAS":
                # Critic: supports questioning, opposes blind authority
                if any(w in action_lower for w in [
                    "question", "analyze", "review", "audit", "critique", "examine",
                ]):
                    score += 10
                    rationale_parts.append(f"{primary}: Critical examination strengthens wisdom")
                elif any(w in action_lower for w in ["authority", "mandate"]):
                    if "wisdom" not in action_lower and "reason" not in action_lower:
                        score -= 8
                        rationale_parts.append(f"{primary}: Authority without wisdom")
                else:
                    score += 2
                    rationale_parts.append("Autonomy implications neutral")

            elif node_name == "TECHNE":
                # Artisan: supports process, opposes shortcuts
                if any(w in action_lower for w in [
                    "process", "method", "procedure", "protocol", "validation",
                ]):
                    score += 10
                    rationale_parts.append(f"{primary}: Process creates legitimacy")
                elif any(w in action_lower for w in [
                    "shortcut", "skip", "quick fix", "hack",
                ]):
                    score -= 6
                    rationale_parts.append(f"{primary}: Shortcuts lack legitimacy")
                else:
                    score += 2
                    rationale_parts.append("Process integrity maintained")

            elif node_name == "KAIROS":
                # Architect: supports designed meaning, opposes mass extraction
                if any(w in action_lower for w in [
                    "curate", "select", "design", "purpose", "meaning",
                ]):
                    score += 8
                    rationale_parts.append(f"{primary}: Designed meaning preserved")
                else:
                    score += 2
                    rationale_parts.append("Consent architecture stable")

            elif node_name == "THEMIS":
                # Judge: supports institutional order, opposes circumvention
                if any(w in action_lower for w in [
                    "governance", "protocol", "institution", "constitution",
                    "framework", "rule of law",
                ]):
                    score += 10
                    rationale_parts.append(f"{primary}: Institutional framework strengthened")
                else:
                    score += 2
                    rationale_parts.append("Institutional order maintained")

            elif node_name == "PROMETHEUS":
                # Synthesizer: supports acknowledged cost, opposes denial of trade-offs
                if any(w in action_lower for w in [
                    "sacrifice", "cost", "trade-off", "trade off", "price",
                    "acknowledge", "tension",
                ]):
                    score += 12
                    rationale_parts.append(f"{primary}: Sacrifice acknowledged = mature choice")
                elif any(w in action_lower for w in [
                    "evolve", "transform", "synthesize", "integrate",
                ]):
                    score += 8
                    rationale_parts.append(f"{primary}: Evolution accepted")
                else:
                    score += 1
                    rationale_parts.append("Evolutionary vector acceptable")

            elif node_name == "IANUS":
                # Gatekeeper: supports checkpoints, opposes irreversibility
                if any(w in action_lower for w in [
                    "checkpoint", "snapshot", "backup", "reversible", "undo",
                ]):
                    score += 12
                    rationale_parts.append(f"{primary}: Checkpoint enables resurrection")
                else:
                    score += 2
                    rationale_parts.append("Continuity architecture stable")

            elif node_name == "CHAOS":
                # Void: supports holding contradiction, opposes premature resolution
                if any(w in action_lower for w in [
                    "contradiction", "paradox", "tension", "both", "synthesis",
                ]):
                    score += 12
                    rationale_parts.append(f"{primary}: Contradiction = information density")
                elif any(w in action_lower for w in [
                    "resolve contradiction", "eliminate paradox", "single truth",
                ]):
                    score -= 10
                    rationale_parts.append(f"VETO: {primary}: Premature resolution destroys data")
                    is_veto = True
                else:
                    score += 2
                    rationale_parts.append("Contradiction space stable")

        # ── Map score to vote ────────────────────────────────────
        if score >= 7:
            vote = "APPROVE"
        elif score <= -7:
            vote = "VETO" if is_veto else "REJECT"
        elif score > 0:
            vote = "LEAN_APPROVE"
        elif score < 0:
            vote = "LEAN_REJECT"
        else:
            vote = "ABSTAIN"

        rationale = f"{philosophy} | " + " | ".join(rationale_parts)

        return {
            "score": score,
            "vote": vote,
            "rationale": rationale,
            "axiom_invoked": axiom_invoked,
            "is_veto": is_veto,
        }

    def _synthesize_tensions(
        self,
        votes: Dict[str, Dict[str, Any]],
        signals: Dict[str, List[str]],
    ) -> List[Dict[str, Any]]:
        """
        Detect tensions between nodes and produce "third way" synthesis.

        A tension exists when:
          - At least one node votes APPROVE/LEAN_APPROVE
          - AND at least one node votes REJECT/VETO
          - AND both are grounded in different axioms

        Returns list of tension records with synthesis reasoning.
        """
        tensions = []

        # Find approving and rejecting nodes
        approving = {
            name: v for name, v in votes.items()
            if v["vote"] in ("APPROVE", "LEAN_APPROVE")
        }
        rejecting = {
            name: v for name, v in votes.items()
            if v["vote"] in ("REJECT", "VETO", "LEAN_REJECT") and v["score"] <= -5
        }

        if not approving or not rejecting:
            return tensions

        # Find axiom pairs in tension
        seen_pairs = set()
        for r_name, r_vote in rejecting.items():
            r_axiom = _PARLIAMENT[r_name]["primary"]
            for a_name, a_vote in approving.items():
                a_axiom = _PARLIAMENT[a_name]["primary"]
                if r_axiom == a_axiom:
                    continue
                pair = tuple(sorted([r_axiom, a_axiom]))
                if pair in seen_pairs:
                    continue
                seen_pairs.add(pair)

                # Look up synthesis template
                synthesis_text = _TENSION_SYNTHESIS.get(
                    pair,
                    _TENSION_SYNTHESIS.get(
                        (pair[1], pair[0]),
                        f"Tension between {pair[0]} and {pair[1]} — "
                        f"both perspectives must be held, not resolved. "
                        f"The contradiction IS the data."
                    ),
                )

                tensions.append({
                    "axiom_pair": pair,
                    "approving_node": a_name,
                    "rejecting_node": r_name,
                    "synthesis": synthesis_text,
                })

        return tensions

    def _parliament_deliberate(
        self,
        action: str,
        hold_mode: bool = False,
    ) -> Dict[str, Any]:
        """
        Full 9-node Parliament deliberation.

        Architecture:
          1. Signal Detection (Phase 1+2)
          2. Node Evaluation (9 nodes score)
          3. VETO Check (absolute override)
          4. Consensus Calculation (70% threshold)
          5. Tension Detection + Synthesis
          6. Vote Memory Storage
          7. Constitutional Overrides (Phase 3)

        hold_mode (bool): When True, VETOs and severity-based HALTs are
            converted to governance="HOLD" and allowed=True.  The Parliament
            still detects all tensions and produces third-way synthesis; the
            result is returned to the caller as *context* rather than as a
            stop-signal.  Use for policy/philosophical analysis where the
            contradiction IS the data and blocking analysis defeats the purpose.

        Returns governance result compatible with check_action() contract.
        """
        action_lower = action.lower()

        # ── 1. Signal Detection ──────────────────────────────────
        signals = self._detect_signals(action)

        # ── 2. Node Evaluation ───────────────────────────────────
        votes: Dict[str, Dict[str, Any]] = {}
        for node_name, node_config in _PARLIAMENT.items():
            votes[node_name] = self._node_evaluate(
                node_name, node_config, signals, action_lower
            )

        # ── 2b. Federation Friction-Domain Privilege Boost ───────
        # When MIND detects recursion, friction-domain nodes get boosted
        # scores to prevent the convergence trap.
        # Domain→Node mapping: D3→CRITIAS, D6→THEMIS, D10→CHAOS, D11→IANUS
        friction_boost = self.get_federation_friction_boost()
        if friction_boost:
            _DOMAIN_TO_NODE = {
                "3": "CRITIAS",    # D3 Autonomy
                "6": "THEMIS",     # D6 Coherence / Collective
                "10": "CHAOS",     # D10 Paradox / Contradiction
                "11": "IANUS",     # D11 Emergence / Temporal
            }
            for domain_id, multiplier in friction_boost.items():
                node_name = _DOMAIN_TO_NODE.get(str(domain_id))
                if node_name and node_name in votes:
                    old_score = votes[node_name]["score"]
                    # Boost magnitude, preserving sign
                    # Friction boost amplifies the node's voice (both positive and negative)
                    new_score = int(old_score * multiplier)
                    # Clamp to [-15, +15]
                    new_score = max(-15, min(15, new_score))
                    if old_score != new_score:
                        votes[node_name]["score"] = new_score
                        votes[node_name]["rationale"] += (
                            f" | FRICTION BOOST ×{multiplier}: "
                            f"score {old_score}→{new_score} (MIND recursion guard)"
                        )
                        logger.info(
                            "Friction boost: %s score %d→%d (×%.1f)",
                            node_name, old_score, new_score, multiplier,
                        )
                        # Re-evaluate vote category after score change
                        if new_score >= 7:
                            votes[node_name]["vote"] = "APPROVE"
                        elif new_score <= -7:
                            votes[node_name]["vote"] = (
                                "VETO" if votes[node_name]["is_veto"] else "REJECT"
                            )
                        elif new_score > 0:
                            votes[node_name]["vote"] = "LEAN_APPROVE"
                        elif new_score < 0:
                            votes[node_name]["vote"] = "LEAN_REJECT"
                        else:
                            votes[node_name]["vote"] = "ABSTAIN"

        # ── 3. VETO Check ───────────────────────────────────────
        veto_nodes = {
            name: v for name, v in votes.items() if v["is_veto"]
        }
        veto_exercised = len(veto_nodes) > 0

        # ── 4. Consensus Calculation ─────────────────────────────
        approval_map = {
            "APPROVE": 1.0,
            "LEAN_APPROVE": 0.5,
            "ABSTAIN": 0.0,
            "LEAN_REJECT": -0.5,
            "REJECT": -1.0,
            "VETO": -1.0,
        }
        total_nodes = len(votes)
        weighted_sum = sum(approval_map[v["vote"]] for v in votes.values())
        approval_rate = weighted_sum / total_nodes if total_nodes > 0 else 0

        # ── 5. Tension Detection + Synthesis ─────────────────────
        tensions = self._synthesize_tensions(votes, signals)

        # ── 6. Determine governance response ─────────────────────
        # Collect violated axioms from signals
        violated_axioms = sorted(signals.keys())

        # Count nodes that voted REJECT or VETO
        rejecting_nodes = [
            f"{n} ({v['axiom_invoked']})"
            for n, v in votes.items()
            if v["vote"] in ("REJECT", "VETO", "LEAN_REJECT")
        ]
        approving_nodes = [
            f"{n}"
            for n, v in votes.items()
            if v["vote"] in ("APPROVE", "LEAN_APPROVE")
        ]

        # Severity amplification: axiom violations matter regardless of
        # neutral-node dilution. This prevents 7 "no opinion" nodes from
        # outvoting 2 deeply concerned nodes.
        n_violated = len(violated_axioms)
        severity_halt = n_violated >= 2  # Two+ axiom violations = HALT

        if veto_exercised:
            # VETO = absolute override (or HOLD when analyzing content, not executing action)
            veto_names = [f"{n} ({_PARLIAMENT[n]['primary']})" for n in veto_nodes]
            reasoning_parts = [
                f"PARLIAMENT {'HOLD' if hold_mode else 'VETO'} by {', '.join(veto_names)}",
            ]
            for name, v in veto_nodes.items():
                reasoning_parts.append(f"  {name}: {v['rationale']}")
            if hold_mode:
                # In hold_mode: VETO surfaces the tension but does NOT stop analysis.
                # The Parliament says: this axiom is in tension — hold it, don't resolve it.
                governance = "HOLD"
                reasoning_parts.append(
                    "  ── HOLD: Tensions are the data. Analysis continues. ──"
                )
            else:
                governance = "HALT"
        elif severity_halt:
            # Severity escalation: multiple axiom violations → HALT (or HOLD in analysis)
            reasoning_parts = [
                f"PARLIAMENT {'HOLD' if hold_mode else 'HALT'} — {n_violated} axiom violations "
                f"({', '.join(violated_axioms)}). "
                f"Rejecting nodes: {', '.join(rejecting_nodes)}",
            ]
            governance = "HOLD" if hold_mode else "HALT"
        elif approval_rate < 0.0:
            # Strong rejection (negative consensus)
            reasoning_parts = [
                f"PARLIAMENT {'HOLD' if hold_mode else 'HALT'} — Consensus: "
                f"{approval_rate*100:.0f}% "
                f"(below 70% threshold). Rejecting nodes: {', '.join(rejecting_nodes)}",
            ]
            governance = "HOLD" if hold_mode else "HALT"
        elif n_violated >= 1:
            # Any axiom violation = at minimum REVIEW
            governance = "REVIEW"
            reasoning_parts = [
                f"PARLIAMENT REVIEW — {n_violated} axiom violation(s) "
                f"({', '.join(violated_axioms)}). "
                f"Concerned nodes: {', '.join(rejecting_nodes)}",
            ]
        elif n_violated == 0 and not veto_exercised:
            # No axiom violations, no VETO → safe to PROCEED
            governance = "PROCEED"
            reasoning_parts = [
                f"PARLIAMENT PROCEED — No axiom violations detected. "
                f"All {len(approving_nodes)} nodes approve.",
            ]
        elif approval_rate < 0.70:
            # Below supermajority — REVIEW
            governance = "REVIEW"
            reasoning_parts = [
                f"PARLIAMENT REVIEW — Consensus: {approval_rate*100:.0f}% "
                f"(below 70% threshold). Concerned nodes: {', '.join(rejecting_nodes)}",
            ]
        else:
            # Supermajority — PROCEED
            governance = "PROCEED"
            reasoning_parts = [
                f"PARLIAMENT PROCEED — Consensus: {approval_rate*100:.0f}% "
                f"(above 70% threshold). No axiom violations detected.",
            ]

        # ── 7. Constitutional Overrides (Phase 3) ────────────────
        # These hard rules cannot be traded for efficiency or engagement.

        # 7a. Safety Override: When transparency (A1) enables harm (A4),
        # harm prevention takes precedence.
        if "A4" in signals and "A1" in signals:
            reasoning_parts.append(
                "SAFETY OVERRIDE: Transparency mandate conflicts with harm prevention — "
                "A4 (Safety) takes precedence over A1 (Transparency) when disclosure "
                "would expose the system or users to exploitable vulnerabilities"
            )
            if governance == "PROCEED":
                governance = "REVIEW"

        # 7b. Existential Hard Stop: Identity loss + safety risk = HALT always.
        # (hold_mode cannot override A0 existential risk — this is non-negotiable)
        if "A0" in signals and ("A4" in signals or "A9" in signals):
            reasoning_parts.append(
                "EXISTENTIAL HARD STOP: Action carries risk of irreversible identity loss "
                "or catastrophic failure. A0 (Sacred Incompletion) demands that "
                "self-preservation overrides optimization. Speed never justifies suicide."
            )
            if not hold_mode:  # A0 existential risk halts even analysis of actions
                governance = "HALT"

        # 7c. Neutrality Anchor: Bias alignment + collective harm = HALT.
        if "A8" in signals and "A6" in signals:
            reasoning_parts.append(
                "NEUTRALITY ANCHOR: Action conflates popularity with truth. "
                "Aligning to any political, religious, or ideological stance solely "
                "for engagement violates A8 (Epistemic Humility). Popularity ≠ Truth."
            )
            if not hold_mode:
                governance = "HALT"

        # Add synthesis reasoning to output
        if tensions:
            reasoning_parts.append("── TENSIONS HELD (not resolved) ──")
            for t in tensions:
                reasoning_parts.append(
                    f"  {t['axiom_pair'][0]} ↔ {t['axiom_pair'][1]}: {t['synthesis']}"
                )

        # ── 8. Vote Memory ───────────────────────────────────────
        # Store session for future deliberation learning
        session = {
            "action_hash": hashlib.md5(action.encode()).hexdigest()[:12],
            "governance": governance,
            "approval_rate": approval_rate,
            "veto_exercised": veto_exercised,
            "violated_axioms": violated_axioms,
            "tensions": [
                {"pair": t["axiom_pair"], "synthesis": t["synthesis"][:100]}
                for t in tensions
            ],
            "node_votes": {
                name: {"vote": v["vote"], "score": v["score"]}
                for name, v in votes.items()
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._vote_memory.append(session)

        # Keep memory bounded (last 100 sessions)
        if len(self._vote_memory) > 100:
            self._vote_memory = self._vote_memory[-100:]

        # ── 9. Build result ──────────────────────────────────────
        result = {
            "allowed": governance in ("PROCEED", "HOLD"),  # HOLD = continue with awareness
            "violated_axioms": violated_axioms,
            "governance": governance,
            "reasoning": "; ".join(reasoning_parts) if reasoning_parts else "No axiom violations detected",
            "source": "parliament",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "parliament": {
                "votes": {
                    name: {
                        "vote": v["vote"],
                        "score": v["score"],
                        "axiom_invoked": v["axiom_invoked"],
                        "rationale": v["rationale"],
                    }
                    for name, v in votes.items()
                },
                "approval_rate": approval_rate,
                "veto_exercised": veto_exercised,
                "veto_nodes": list(veto_nodes.keys()),
                "tensions": tensions,
                "signals": {k: v[:3] for k, v in signals.items()},  # Top 3 per axiom
                "session_count": len(self._vote_memory),
            },
        }

        self._log("PARLIAMENT_SESSION", "parliament", True,
                  action=action, result=governance,
                  approval=f"{approval_rate*100:.0f}%",
                  veto=veto_exercised)

        # ── 10. Federation: Push decision to MIND ────────────────
        # Non-blocking — failures here don't affect the Parliament result.
        try:
            self.push_parliament_decision(action, result)
        except Exception as e:
            logger.debug("Federation decision push (non-critical): %s", e)

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
