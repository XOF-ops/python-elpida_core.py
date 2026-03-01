"""
Pattern Library — Structured Wisdom for Parliament Deliberation
================================================================

Loads entries from ``living_axioms.jsonl`` and makes them queryable
by axiom relevance. The parliament consults this library *before*
deliberating to inject crystallized wisdom as context.

There are 4 types of entries:
  - **parliament-origin**: tensions crystallized from real deliberations
  - **synod-origin**: A6 crystallization from CrystallizationHub Synod
  - **domain-debate**: mapped axiom tensions from cross-domain debates
  - **kernel-patterns**: SYSTEM_DYNAMICS patterns P119-P127 from KERNEL_v1.0
  - **battery-gr**: GR-certified axiom candidates from adversarial battery tests

The library does NOT add LLM calls. It is a structured lookup — O(N)
over a small file (currently 21 entries). Zero budget impact.

Usage::

    library = PatternLibrary("/path/to/living_axioms.jsonl")
    # Get patterns relevant to axioms A4 and A7
    relevant = library.query_by_axioms(["A4", "A7"], max_results=3)
    # Get a context string for parliament deliberation
    context_str = library.context_for_deliberation(["A4", "A7"])
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger("elpida.pattern_library")


class PatternLibrary:
    """
    In-memory pattern library loaded from living_axioms.jsonl.

    Entries are loaded once on init and cached. The file is re-read
    on demand via ``reload()`` when new axioms are ratified.
    """

    def __init__(self, store_path: Optional[str] = None):
        if store_path is None:
            store_path = str(
                Path(__file__).resolve().parent.parent / "living_axioms.jsonl"
            )
        self._path = Path(store_path)
        self._entries: List[Dict] = []
        self._load()

    def _load(self):
        """Load all entries from the JSONL file."""
        self._entries = []
        if not self._path.exists():
            logger.warning("Pattern library not found: %s", self._path)
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        self._entries.append(entry)
                    except json.JSONDecodeError as e:
                        logger.warning(
                            "Malformed entry in pattern library line %d: %s",
                            line_no, e,
                        )
            logger.info(
                "Pattern library loaded: %d entries from %s",
                len(self._entries), self._path.name,
            )
        except OSError as e:
            logger.warning("Cannot read pattern library: %s", e)

    def reload(self):
        """Re-read the file (call after new axiom ratification)."""
        self._load()

    @property
    def count(self) -> int:
        return len(self._entries)

    # ------------------------------------------------------------------
    # Axiom-based querying
    # ------------------------------------------------------------------

    def _axioms_for_entry(self, entry: Dict) -> List[str]:
        """
        Extract axiom identifiers from an entry.

        Handles multiple formats:
          - axiom_mapping: ["A4", "A7"]           (kernel/battery entries)
          - axiom_id: "A5/A1"                      (parliament entries)
          - conflict: "A2 (Non-Deception) vs A7"   (debate entries)
          - trigger_axiom: "A6"                     (synod entries)
        """
        axioms = []

        # Explicit mapping (kernel patterns, battery GR)
        mapping = entry.get("axiom_mapping", [])
        if isinstance(mapping, list):
            axioms.extend(mapping)

        # axiom_id field (parliament crystallized: "A5/A1", "A2/A5")
        axiom_id = entry.get("axiom_id", "")
        if "/" in axiom_id:
            for part in axiom_id.split("/"):
                part = part.strip()
                if part.startswith("A") and part[1:].isdigit():
                    axioms.append(part)

        # Synod trigger axiom
        trigger = entry.get("trigger_axiom", "")
        if trigger and trigger.startswith("A"):
            axioms.append(trigger)

        # Conflict field (debate entries): "A2 (Non-Deception) vs A7 (Adaptive)"
        conflict = entry.get("conflict", "")
        if conflict:
            import re
            for m in re.finditer(r"\bA(\d+)\b", conflict):
                axioms.append(f"A{m.group(1)}")

        return list(set(axioms))

    def query_by_axioms(
        self, axioms: List[str], max_results: int = 5
    ) -> List[Dict]:
        """
        Return entries relevant to the given axioms, ranked by overlap.

        Args:
            axioms: List of axiom IDs, e.g. ["A4", "A7"]
            max_results: Maximum entries to return

        Returns:
            List of (entry, score) matching entries, highest relevance first
        """
        if not axioms or not self._entries:
            return []

        query_set = set(axioms)
        scored = []

        for entry in self._entries:
            entry_axioms = set(self._axioms_for_entry(entry))
            overlap = query_set & entry_axioms
            if overlap:
                # Score: number of matching axioms + bonus for ratified entries
                score = len(overlap)
                status = entry.get("status", "")
                if status in ("ratified", "RATIFIED"):
                    score += 0.5  # Ratified entries get priority
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:max_results]]

    def query_by_rhythm(self, rhythm: str, max_results: int = 3) -> List[Dict]:
        """
        Return patterns relevant to a rhythm's active domain axioms.

        Maps rhythm → active axioms → pattern query.
        """
        rhythm_axioms = {
            "CONTEMPLATION": ["A1", "A2", "A3", "A6", "A8", "A0"],
            "ANALYSIS": ["A4", "A5", "A6", "A9", "A0"],
            "ACTION": ["A6", "A7", "A8", "A9", "A10"],
            "SYNTHESIS": ["A6"],
            "EMERGENCY": ["A4", "A6", "A7", "A9"],
        }
        axioms = rhythm_axioms.get(rhythm, [])
        return self.query_by_axioms(axioms, max_results=max_results)

    # ------------------------------------------------------------------
    # Context string for parliament injection
    # ------------------------------------------------------------------

    def context_for_deliberation(
        self,
        axioms: List[str],
        max_patterns: int = 3,
    ) -> str:
        """
        Generate a context string to prepend to parliament action text.

        Returns empty string if no relevant patterns found.

        Format:
            [PATTERN LIBRARY: 2 relevant patterns]
            P122 Oscillation Dampening (A10/A7): Not all oscillation is sacred...
            GR_COHERENCESAFETY (A4/A7): Maximum coherence anti-correlates with...
        """
        entries = self.query_by_axioms(axioms, max_results=max_patterns)
        if not entries:
            return ""

        lines = [f"[PATTERN LIBRARY: {len(entries)} relevant pattern(s)]"]
        for entry in entries:
            aid = entry.get("axiom_id", entry.get("name", "?"))
            name = entry.get("name", "")
            axiom_str = "/".join(self._axioms_for_entry(entry))

            # Pick the best summary text
            text = (
                entry.get("synthesis", "")
                or entry.get("tension", "")
                or entry.get("statement", "")
            )
            # Truncate for prompt efficiency
            if len(text) > 200:
                text = text[:197] + "..."

            label = f"{aid}"
            if name and name != aid:
                label = f"{aid} {name}"

            lines.append(f"  {label} ({axiom_str}): {text}")

        return "\n".join(lines)
