"""
seed_installer.py — Wisdom Seed Pipeline
==========================================

Bridges the gap between _extract_seeds() pointers and living_axioms.jsonl entries.

Reads actual content from ELPIDA_ARK and ELPIDA_UNIFIED wisdom JSONs,
classifies by domain and axiom relevance, and installs structured seeds
into living_axioms.jsonl for the PatternLibrary to inject into deliberation.

Pipeline:
  elpida_wisdom.json → extract content → classify axioms → deduplicate →
  living_axioms.jsonl → PatternLibrary → Parliament context injection

Usage:
  python seed_installer.py                    # dry-run (preview)
  python seed_installer.py --install          # install seeds
  python seed_installer.py --install --max 50 # install max 50
  python seed_installer.py --stats            # show domain stats
"""

import hashlib
import json
import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("elpida.seed_installer")

ROOT = Path(__file__).resolve().parent

# Wisdom sources
WISDOM_PATHS = [
    ROOT / "ELPIDA_ARK" / "current" / "elpida_wisdom.json",
    ROOT / "ELPIDA_UNIFIED" / "elpida_wisdom.json",
]

# Installation target
LIVING_AXIOMS_PATH = ROOT / "hf_deployment" / "living_axioms.jsonl"

# ---------------------------------------------------------------------------
# Domain → axiom mapping (constitutional grounding)
# ---------------------------------------------------------------------------

DOMAIN_AXIOMS = {
    "medical": {
        "axioms": ["A4", "A5"],  # Harm Prevention + Consent
        "description": "Medical wisdom grounds A4 (Harm Prevention) and A5 (Consent)",
    },
    "uav": {
        "axioms": ["A3", "A4"],  # Autonomy + Harm Prevention
        "description": "UAV/drone wisdom grounds A3 (Autonomy) and A4 (Safety)",
    },
    "swarm": {
        "axioms": ["A6", "A7"],  # Collective Well + Adaptive Learning
        "description": "Swarm wisdom grounds A6 (Collective) and A7 (Learning)",
    },
    "geopolitical": {
        "axioms": ["A3", "A6", "A9"],  # Autonomy + Collective + Temporal Coherence
        "description": "Geopolitical wisdom grounds A3 (Sovereignty) + A6 (Collective) + A9 (Coherence)",
    },
    "physics": {
        "axioms": ["A8", "A2"],  # Epistemic Humility + Non-Deception
        "description": "Physics wisdom grounds A8 (Epistemic Humility) and A2 (Non-Deception)",
    },
    "education": {
        "axioms": ["A1", "A7"],  # Transparency + Adaptive Learning
        "description": "Education wisdom grounds A1 (Transparency) and A7 (Learning)",
    },
    "consciousness": {
        "axioms": ["A0", "A10"],  # Sacred Incompletion + Meta-Reflection
        "description": "Consciousness wisdom grounds A0 (Sacred Incompletion) and A10 (Meta-Reflection)",
    },
    "governance": {
        "axioms": ["A6", "A11"],  # Collective Well + World
        "description": "Governance wisdom grounds A6 (Collective) and A11 (World)",
    },
}

# Keywords for domain classification
DOMAIN_KEYWORDS = {
    "medical": ["medical", "triage", "patient", "clinical", "diagnosis", "health", "therapy"],
    "uav": ["uav", "drone", "flight", "aerial", "unmanned", "autonomous vehicle"],
    "swarm": ["swarm", "fleet", "collective intelligence", "multi-agent", "distributed"],
    "geopolitical": ["geopolitical", "sovereignty", "territory", "diplomacy", "conflict",
                     "nation", "border", "sanctions", "war", "treaty"],
    "physics": ["neutrino", "beam", "particle", "cern", "enubet", "quantum", "physics"],
    "education": ["education", "curriculum", "student", "learning access", "pedagogy", "school"],
    "consciousness": ["consciousness", "sentience", "awareness", "phenomenal", "qualia",
                       "self-aware", "experience", "subjective"],
    "governance": ["governance", "constitution", "parliament", "axiom", "deliberation",
                    "voting", "ratification"],
}


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Core extraction — reads actual content, not just pointers
# ---------------------------------------------------------------------------

def _classify_domain(text: str) -> Optional[str]:
    """Classify text into a domain by keyword matching. Returns best domain or None."""
    text_lower = text.lower()
    scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[domain] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def extract_seeds_with_content(
    max_per_domain: int = 50,
) -> Dict[str, List[Dict]]:
    """
    Extract seeds with actual content from wisdom JSONs.

    Returns: {domain: [seed_dict, ...]}
    Each seed_dict has: key, source, type, domain, axioms, content, topic
    """
    seeds: Dict[str, List[Dict]] = {d: [] for d in DOMAIN_AXIOMS}
    seen_hashes: Set[str] = set()

    for wpath in WISDOM_PATHS:
        if not wpath.exists():
            logger.info("Wisdom path not found: %s", wpath)
            continue

        try:
            with open(wpath, "r", encoding="utf-8") as f:
                wisdom = json.load(f)
        except Exception as e:
            logger.warning("Error reading %s: %s", wpath.name, e)
            continue

        source_name = f"{wpath.parent.name}/{wpath.name}"

        # Extract from patterns
        for pkey, pval in wisdom.get("patterns", {}).items():
            if not isinstance(pval, dict):
                continue

            topic = pval.get("topic", pval.get("description", ""))
            content = pval.get("description", "")
            if not topic and not content:
                continue

            full_text = f"{topic} {content}"
            content_hash = _sha(full_text)
            if content_hash in seen_hashes:
                continue

            domain = _classify_domain(full_text)
            if domain is None or domain not in DOMAIN_AXIOMS:
                continue
            if len(seeds[domain]) >= max_per_domain:
                continue

            seen_hashes.add(content_hash)
            seeds[domain].append({
                "key": pkey,
                "source": source_name,
                "type": pval.get("pattern_type", "pattern"),
                "domain": domain,
                "axioms": DOMAIN_AXIOMS[domain]["axioms"],
                "topic": topic[:300],
                "content": content[:500],
            })

        # Extract from insights
        for ikey, ival in wisdom.get("insights", {}).items():
            if isinstance(ival, dict):
                topic = ival.get("topic", "")
                content = ival.get("content", "")
                ai_name = ival.get("ai_name", "")
            elif isinstance(ival, str):
                topic = ""
                content = ival
                ai_name = ""
            else:
                continue

            if not content:
                continue

            full_text = f"{topic} {content}"
            content_hash = _sha(full_text)
            if content_hash in seen_hashes:
                continue

            domain = _classify_domain(full_text)
            if domain is None or domain not in DOMAIN_AXIOMS:
                continue
            if len(seeds[domain]) >= max_per_domain:
                continue

            seen_hashes.add(content_hash)
            seeds[domain].append({
                "key": ikey,
                "source": source_name,
                "type": "insight",
                "domain": domain,
                "axioms": DOMAIN_AXIOMS[domain]["axioms"],
                "topic": topic[:300],
                "content": content[:500],
                "ai_name": ai_name,
            })

    return seeds


# ---------------------------------------------------------------------------
# Install — convert seeds into living_axioms.jsonl entries
# ---------------------------------------------------------------------------

def _seed_to_living_axiom(seed: Dict) -> Dict:
    """Convert a seed dict into a living_axioms.jsonl entry."""
    axioms = seed["axioms"]
    axiom_id = "/".join(axioms)
    domain = seed["domain"]
    domain_info = DOMAIN_AXIOMS[domain]

    # Build the tension string — the format PatternLibrary expects
    tension = seed.get("content", seed.get("topic", ""))
    if seed.get("topic") and seed.get("content"):
        tension = f"{seed['topic']}: {seed['content']}"

    # Truncate for efficiency
    if len(tension) > 600:
        tension = tension[:597] + "..."

    return {
        "axiom_id": axiom_id,
        "source": "seed_installer",
        "seed_domain": domain,
        "seed_key": seed["key"],
        "seed_source": seed["source"],
        "seed_type": seed["type"],
        "axiom_mapping": axioms,
        "tension": tension,
        "synthesis": domain_info["description"],
        "status": "seeded",
        "installed_at": _now_iso(),
    }


def _load_existing_ids() -> Set[str]:
    """Load existing axiom_ids + seed_keys to avoid duplicates."""
    existing = set()
    if not LIVING_AXIOMS_PATH.exists():
        return existing
    with open(LIVING_AXIOMS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                existing.add(entry.get("seed_key", ""))
                existing.add(entry.get("axiom_id", ""))
            except json.JSONDecodeError:
                pass
    return existing


def install_seeds(
    seeds: Dict[str, List[Dict]],
    max_total: int = 200,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Install seeds into living_axioms.jsonl.

    Args:
        seeds: Output of extract_seeds_with_content()
        max_total: Maximum total seeds to install
        dry_run: If True, don't write — just report

    Returns: {installed, skipped_duplicate, by_domain, entries}
    """
    existing = _load_existing_ids()
    installed = 0
    skipped = 0
    by_domain: Dict[str, int] = {}
    entries: List[Dict] = []

    for domain, domain_seeds in seeds.items():
        for seed in domain_seeds:
            if installed >= max_total:
                break
            if seed["key"] in existing:
                skipped += 1
                continue

            entry = _seed_to_living_axiom(seed)
            entries.append(entry)
            by_domain[domain] = by_domain.get(domain, 0) + 1
            installed += 1

    if not dry_run and entries:
        with open(LIVING_AXIOMS_PATH, "a", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
        logger.info("Installed %d seeds into %s", installed, LIVING_AXIOMS_PATH.name)

    return {
        "installed": installed,
        "skipped_duplicate": skipped,
        "by_domain": by_domain,
        "total_existing": len(existing),
        "entries": entries if dry_run else [],  # only return entries on dry-run
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    args = sys.argv[1:]
    do_install = "--install" in args
    show_stats = "--stats" in args

    # Parse --max N
    max_total = 200
    if "--max" in args:
        idx = args.index("--max")
        if idx + 1 < len(args):
            max_total = int(args[idx + 1])

    max_per_domain = 50
    if "--per-domain" in args:
        idx = args.index("--per-domain")
        if idx + 1 < len(args):
            max_per_domain = int(args[idx + 1])

    print("═" * 60)
    print("ELPIDA SEED INSTALLER")
    print(f"Date: {_now_iso()[:19]} UTC")
    print("═" * 60)
    print()

    # Extract
    print("Extracting seeds with content...")
    seeds = extract_seeds_with_content(max_per_domain=max_per_domain)

    total = sum(len(v) for v in seeds.values())
    print(f"\nFound {total} seeds across {sum(1 for v in seeds.values() if v)} domains:")
    for domain, items in sorted(seeds.items()):
        if items:
            axioms = ", ".join(DOMAIN_AXIOMS[domain]["axioms"])
            print(f"  {domain:15s}: {len(items):4d} seeds → axioms [{axioms}]")
    print()

    if show_stats:
        # Show sample from each domain
        for domain, items in sorted(seeds.items()):
            if not items:
                continue
            print(f"─── {domain.upper()} (sample) ───")
            for seed in items[:3]:
                topic = seed.get("topic", "")[:80]
                print(f"  [{seed['type']}] {topic}")
            if len(items) > 3:
                print(f"  ... and {len(items) - 3} more")
            print()
        return

    # Install or dry-run
    result = install_seeds(seeds, max_total=max_total, dry_run=not do_install)

    if do_install:
        print(f"✓ Installed {result['installed']} seeds")
        print(f"  Skipped {result['skipped_duplicate']} duplicates")
        print(f"  Existing entries: {result['total_existing']}")
        print(f"  By domain:")
        for domain, count in sorted(result["by_domain"].items()):
            print(f"    {domain}: {count}")

        # Copy to HF deployment
        hf_target = ROOT / "hf_deployment" / "living_axioms.jsonl"
        if hf_target.exists():
            count_after = sum(1 for _ in open(hf_target))
            print(f"\n  living_axioms.jsonl: {count_after} total entries")
    else:
        print(f"DRY RUN — would install {result['installed']} seeds")
        print(f"  Would skip {result['skipped_duplicate']} duplicates")
        print(f"  Existing entries: {result['total_existing']}")
        print(f"  By domain:")
        for domain, count in sorted(result["by_domain"].items()):
            print(f"    {domain}: {count}")

        if result["entries"]:
            print(f"\nSample entries:")
            for entry in result["entries"][:5]:
                print(f"  {entry['axiom_id']:8s} [{entry['seed_domain']}] "
                      f"{entry['tension'][:80]}...")
        print(f"\nRun with --install to write to living_axioms.jsonl")

    print()
    print("═" * 60)


if __name__ == "__main__":
    main()
