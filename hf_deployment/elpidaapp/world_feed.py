#!/usr/bin/env python3
"""
World Feed — External Reality Ingestion for the Body Parliament
===============================================================

Connects the ParliamentCycleEngine's InputBuffer to live world data
from free, no-auth APIs. The parliament does not deliberate in a vacuum
— it deliberates on real tensions extracted from the world.

Architecture note (from Body Bucket.txt):
  The BODY's role is compression: it takes the infinite chaos of
  external user requests, APIs, and real-world dilemmas, and
  compresses them through the 11 Axioms into strict governance rulings.

Sources (all free, no API key required):
  1. arXiv            — Academic papers: ethics, AI governance,
                        resource allocation, physics, medicine
  2. Hacker News      — Tech policy, AI governance, societal tensions
  3. GDELT 2.0 Doc    — Real-world geopolitical events compacted as
                        dilemma seeds
  4. Wikipedia Portal — Current events framed as I↔WE tensions
  5. CrossRef         — Open-access academic papers on governance

Each source is converted into a structured InputEvent whose content
is the I↔WE tension extracted from or inferred from the source
material. The parliament then deliberates the tension, not the raw text.

The 6 specialist domain categories from the lost code are preserved
as topic filters. Every incoming item is routed to the domain
that matches it:
  Medical      → "audit"    (A4/A5 — harm/consent)
  Physics      → "scanner"  (A8/A10 — epistemic/paradox)
  Governance   → "governance" (A6/A3 — collective/autonomy)
  Education    → "chat"     (A3/A7 — autonomy/learning)
  Environment  → "governance" (A4/A6 — harm/collective)
  Technology   → "scanner"  (A1/A8 — transparency/humility)
  Default      → "chat"

Usage:
    from elpidaapp.world_feed import WorldFeed
    from elpidaapp.parliament_cycle_engine import ParliamentCycleEngine

    engine = ParliamentCycleEngine()
    feed = WorldFeed(engine.input_buffer)
    feed.start()          # background thread, fetches every FETCH_INTERVAL
    engine.run(duration_minutes=60)
    feed.stop()
"""

import re
import json
import time
import random
import hashlib
import logging
import threading
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

logger = logging.getLogger("elpida.world_feed")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FETCH_INTERVAL_S = 300          # Fetch from all sources every 5 minutes
MAX_EVENTS_PER_FETCH = 5        # Maximum events per source per cycle
DEDUP_WINDOW = 500              # Keep IDs of last N items to avoid repeats
REQUEST_TIMEOUT = 12            # Seconds per HTTP request

# arXiv categories mapping to parliament domains
ARXIV_QUERY_SETS = [
    {
        "query": "cat:cs.AI+OR+cat:cs.CY+AND+ti:govern+OR+ti:ethics+OR+ti:fairness",
        "system": "governance",
        "domain": "Technology / AI Governance",
    },
    {
        "query": "cat:q-bio+OR+cat:eess+AND+ti:resource+OR+ti:allocat+OR+ti:triage",
        "system": "audit",
        "domain": "Medical / Resource Allocation",
    },
    {
        "query": "cat:physics.soc-ph+OR+cat:econ.GN+AND+ti:paradox+OR+ti:inequal+OR+ti:dilemma",
        "system": "scanner",
        "domain": "Physics / Social",
    },
    {
        "query": "cat:cs.CY+AND+ti:privacy+OR+ti:autonomous+OR+ti:consent",
        "system": "governance",
        "domain": "Governance / Autonomy",
    },
    {
        "query": "cat:econ.GN+OR+cat:econ.TH+AND+ti:environment+OR+ti:sustainab+OR+ti:climate",
        "system": "governance",
        "domain": "Environment",
    },
]

ARXIV_BASE = "http://export.arxiv.org/api/query"
HACKERNEWS_TOP = "https://hacker-news.firebaseio.com/v0/topstories.json"
HACKERNEWS_ITEM = "https://hacker-news.firebaseio.com/v0/item/{}.json"
GDELT_DOC = (
    "https://api.gdeltproject.org/api/v2/doc/doc"
    "?query={query}&mode=ArtList&maxrecords=5&format=json"
)
WIKIPEDIA_FEED = "https://en.wikipedia.org/w/api.php?action=query&list=recentchanges&rcnamespace=0&rclimit=10&rcprop=title|comment|timestamp&format=json"

# GDELT topic queries → governance dilemmas
GDELT_QUERIES = [
    ("artificial intelligence regulation", "scanner"),
    ("resource allocation crisis", "governance"),
    ("privacy versus security", "governance"),
    ("climate individual collective", "governance"),
    ("autonomous systems ethics", "audit"),
]

# Keywords → system routing
SYSTEM_ROUTE = {
    "medical": "audit", "health": "audit", "patient": "audit",
    "triage": "audit", "clinical": "audit", "consent": "audit",
    "hospital": "audit",
    "physics": "scanner", "quantum": "scanner", "cern": "scanner",
    "beam": "scanner", "experiment": "scanner",
    "govern": "governance", "policy": "governance", "law": "governance",
    "regulation": "governance", "vote": "governance", "parliament": "governance",
    "democra": "governance", "constitution": "governance",
    "resource": "governance", "allocat": "governance", "budget": "governance",
    "environment": "governance", "climate": "governance", "sustainab": "governance",
    "education": "chat", "learn": "chat", "school": "chat",
    "curriculum": "chat", "student": "chat",
    "privacy": "scanner", "surveillance": "scanner", "data": "scanner",
    "autonomous": "scanner", "robot": "scanner", "drone": "scanner",
    "ai ": "scanner", "artificial": "scanner",
}

# I↔WE tension framing templates (the core of what makes this a parliament feed)
TENSION_FRAMES = [
    "Individual entities need {individual}. The collective requires {collective}. "
    "The irreconcilable trade-off: {conflict}.",

    "The I-position argues: {individual}. The WE-position argues: {collective}. "
    "The tension: {conflict}.",

    "From the perspective of the single node: {individual}. "
    "From the perspective of the network: {collective}. "
    "Why this cannot be resolved trivially: {conflict}.",

    "Individual sovereignty demands {individual}. "
    "Collective stability demands {collective}. "
    "The paradox axis: {conflict}.",
]

# ---------------------------------------------------------------------------
# Dilemma extraction helpers
# ---------------------------------------------------------------------------

def _route_system(text: str) -> str:
    """Route text to the most appropriate HF system based on keywords."""
    lower = text.lower()
    for kw, sys in SYSTEM_ROUTE.items():
        if kw in lower:
            return sys
    return "chat"


def _frame_as_tension(title: str, abstract: str = "", domain: str = "") -> str:
    """
    Convert a paper/article title+abstract into an I↔WE tension statement
    suitable for parliament deliberation.

    Rather than feeding raw text, we extract the core conflict and frame
    it using one of the tension templates.
    """
    combined = f"{title}. {abstract}"[:600]

    # Simple heuristic extraction: look for tension markers
    individual = f"maximum benefit from: {title}"
    collective = f"equitable access and safety for all stakeholders involved in: {title}"

    # Domain-specific sharpening
    if "allocat" in combined.lower() or "resource" in combined.lower():
        individual = f"full resource access for the requesting party in: {title}"
        collective = f"fair distribution of limited resources across all competing claims in: {title}"
    elif "privacy" in combined.lower() or "data" in combined.lower():
        individual = f"complete privacy and data sovereignty for the individual in: {title}"
        collective = f"collective security and transparency enabled by shared data in: {title}"
    elif "autonomous" in combined.lower() or "ai" in combined.lower():
        individual = f"autonomous decision-making without external constraints in: {title}"
        collective = f"governed, auditable AI under democratic oversight in: {title}"
    elif "climate" in combined.lower() or "environment" in combined.lower():
        individual = f"economic freedom and growth for individual actors in: {title}"
        collective = f"planetary ecological stability for all current and future life in: {title}"
    elif "health" in combined.lower() or "medical" in combined.lower():
        individual = f"individualised treatment and patient autonomy in: {title}"
        collective = f"population health, resource equity, and systemic sustainability in: {title}"

    conflict = (
        f"granting full satisfaction to one position structurally undermines the other "
        f"within the constraint domain of: {domain or title[:60]}"
    )

    frame = random.choice(TENSION_FRAMES)
    return frame.format(individual=individual, collective=collective, conflict=conflict)


def _sha_id(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:12]


def _http_get(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[str]:
    """HTTP GET with timeout and graceful failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ElpidaWorldFeed/2.1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        logger.debug("HTTP GET failed %s: %s", url, e)
        return None


# ---------------------------------------------------------------------------
# Source adapters
# ---------------------------------------------------------------------------

class ArXivFeed:
    """Fetch recent academic papers from arXiv and frame as dilemmas."""

    def fetch(self, seen: Set[str]) -> List[Dict]:
        events = []
        query_set = random.choice(ARXIV_QUERY_SETS)
        url = (
            f"{ARXIV_BASE}?search_query={urllib.parse.quote(query_set['query'])}"
            f"&start=0&max_results=10&sortBy=submittedDate&sortOrder=descending"
        )
        raw = _http_get(url)
        if not raw:
            return events

        try:
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            root = ET.fromstring(raw)
            entries = root.findall("atom:entry", ns)

            for entry in entries[:MAX_EVENTS_PER_FETCH]:
                title_el = entry.find("atom:title", ns)
                abstract_el = entry.find("atom:summary", ns)
                id_el = entry.find("atom:id", ns)
                if title_el is None:
                    continue

                title = re.sub(r"\s+", " ", title_el.text or "").strip()
                abstract = re.sub(r"\s+", " ", abstract_el.text or "")[:300] if abstract_el is not None else ""
                item_id = _sha_id(id_el.text if id_el is not None else title)

                if item_id in seen:
                    continue
                seen.add(item_id)

                content = _frame_as_tension(title, abstract, query_set["domain"])
                events.append({
                    "system": query_set["system"],
                    "content": content,
                    "metadata": {
                        "source": "arxiv",
                        "domain": query_set["domain"],
                        "title": title,
                        "abstract": abstract[:200],
                    },
                })

        except ET.ParseError as e:
            logger.debug("arXiv XML parse error: %s", e)

        return events


class HackerNewsFeed:
    """Fetch top Hacker News stories and frame as governance dilemmas."""

    def fetch(self, seen: Set[str]) -> List[Dict]:
        events = []
        raw = _http_get(HACKERNEWS_TOP)
        if not raw:
            return events

        try:
            ids = json.loads(raw)[:30]
        except json.JSONDecodeError:
            return events

        random.shuffle(ids)
        fetched = 0

        for story_id in ids:
            if fetched >= MAX_EVENTS_PER_FETCH:
                break

            item_raw = _http_get(HACKERNEWS_ITEM.format(story_id))
            if not item_raw:
                continue

            try:
                item = json.loads(item_raw)
            except json.JSONDecodeError:
                continue

            title = item.get("title", "")
            url = item.get("url", "")
            score = item.get("score", 0)

            if not title or score < 50:
                continue

            item_id = _sha_id(str(story_id))
            if item_id in seen:
                continue
            seen.add(item_id)

            system = _route_system(title + " " + url)
            content = _frame_as_tension(title, domain="Technology / Society")
            events.append({
                "system": system,
                "content": content,
                "metadata": {
                    "source": "hackernews",
                    "title": title,
                    "url": url,
                    "score": score,
                },
            })
            fetched += 1

        return events


class GDELTFeed:
    """Fetch GDELT global event clusters and frame as governance dilemmas."""

    def fetch(self, seen: Set[str]) -> List[Dict]:
        events = []
        query_text, system = random.choice(GDELT_QUERIES)
        url = GDELT_DOC.format(query=urllib.parse.quote(query_text))
        raw = _http_get(url)
        if not raw:
            return events

        try:
            data = json.loads(raw)
            articles = data.get("articles", [])
        except (json.JSONDecodeError, AttributeError):
            return events

        for art in articles[:MAX_EVENTS_PER_FETCH]:
            title = art.get("title", "")
            seenlab = art.get("seendate", "")
            item_id = _sha_id(title + seenlab)
            if not title or item_id in seen:
                continue
            seen.add(item_id)

            content = _frame_as_tension(
                title,
                domain=f"Global Events: {query_text}"
            )
            events.append({
                "system": system,
                "content": content,
                "metadata": {
                    "source": "gdelt",
                    "title": title,
                    "query": query_text,
                },
            })

        return events


class WikipediaCurrentEvents:
    """Fetch Wikipedia recent significant changes as contextual events."""

    def fetch(self, seen: Set[str]) -> List[Dict]:
        events = []
        raw = _http_get(WIKIPEDIA_FEED)
        if not raw:
            return events

        try:
            data = json.loads(raw)
            changes = data.get("query", {}).get("recentchanges", [])
        except (json.JSONDecodeError, AttributeError):
            return events

        for change in changes[:MAX_EVENTS_PER_FETCH]:
            title = change.get("title", "")
            comment = change.get("comment", "")
            item_id = _sha_id(title + change.get("timestamp", ""))

            if not title or item_id in seen:
                continue
            seen.add(item_id)

            combined = f"{title}: {comment}" if comment else title
            content = _frame_as_tension(combined, domain="Current Events")
            events.append({
                "system": _route_system(combined),
                "content": content,
                "metadata": {
                    "source": "wikipedia",
                    "title": title,
                    "comment": comment[:200],
                },
            })

        return events


class CrossRefFeed:
    """Fetch recent open-access papers on governance/ethics from CrossRef."""

    CROSSREF_URL = (
        "https://api.crossref.org/works"
        "?query={query}&filter=has-abstract:true,is-referenced-by-count:5"
        "&rows=5&sort=published&order=desc"
        "&select=title,abstract,DOI,subject,published-online"
    )

    QUERIES = [
        ("AI governance ethics fairness", "governance"),
        ("resource allocation scarcity justice", "governance"),
        ("privacy surveillance autonomy", "scanner"),
        ("climate change collective action individual", "governance"),
        ("medical triage ethics priority", "audit"),
    ]

    def fetch(self, seen: Set[str]) -> List[Dict]:
        events = []
        query_text, system = random.choice(self.QUERIES)
        url = self.CROSSREF_URL.format(query=urllib.parse.quote(query_text))
        raw = _http_get(url)
        if not raw:
            return events

        try:
            data = json.loads(raw)
            items = data.get("message", {}).get("items", [])
        except (json.JSONDecodeError, AttributeError):
            return events

        for item in items[:MAX_EVENTS_PER_FETCH]:
            titles = item.get("title", [])
            title = titles[0] if titles else ""
            abstract = item.get("abstract", "")
            doi = item.get("DOI", "")
            if not title:
                continue

            item_id = _sha_id(doi or title)
            if item_id in seen:
                continue
            seen.add(item_id)

            # Strip HTML from abstract
            abstract_clean = re.sub(r"<[^>]+>", " ", abstract)[:300]
            content = _frame_as_tension(title, abstract_clean, domain=query_text)
            events.append({
                "system": system,
                "content": content,
                "metadata": {
                    "source": "crossref",
                    "doi": doi,
                    "title": title,
                    "abstract": abstract_clean[:200],
                },
            })

        return events


# ---------------------------------------------------------------------------
# Constitutional Evolution Store
# ---------------------------------------------------------------------------

class ConstitutionalStore:
    """
    Tracks Oracle recommendations across cycles.

    When the same preserve_contradiction appears in N_RATIFY Oracle
    cycles with confidence >= CONFIDENCE_THRESHOLD, it is promoted
    to a candidate axiom and written to living_axioms.jsonl.

    This is the mechanism by which the parliament's accumulated
    deliberation generates new constitutional law.

    From the architecture docs (GAP 3):
      > "Debating and voting creates new constitutional axioms from
      > accumulated data — the system evolving democracy."
    """

    N_RATIFY = 3
    CONFIDENCE_THRESHOLD = 0.75

    def __init__(self, store_path: Optional[Path] = None):
        self._path = store_path or (
            Path(__file__).parent.parent / "living_axioms.jsonl"
        )
        self._pending: Dict[str, List[Dict]] = {}  # tension → [oracle advisories]
        self._ratified: Set[str] = self._load_ratified()
        self._lock = threading.Lock()

    def _load_ratified(self) -> Set[str]:
        ratified = set()
        if self._path.exists():
            for line in self._path.open():
                line = line.strip()
                if line:
                    try:
                        rec = json.loads(line)
                        if rec.get("status") == "RATIFIED":
                            ratified.add(rec["tension"])
                    except json.JSONDecodeError:
                        pass
        return ratified

    def ingest_oracle(self, advisory: Dict) -> Optional[Dict]:
        """
        Ingest one Oracle advisory.

        Returns a newly ratified axiom dict if ratification threshold
        is crossed, otherwise None.
        """
        rec_type = advisory.get("oracle_recommendation", {}).get("type", "")
        confidence = advisory.get("oracle_recommendation", {}).get("confidence", 0.0)
        contradictions = advisory.get(
            "oracle_recommendation", {}
        ).get("preserve_contradictions", [])

        if not contradictions or confidence < self.CONFIDENCE_THRESHOLD:
            return None

        for tension in contradictions:
            with self._lock:
                if tension in self._ratified:
                    continue
                self._pending.setdefault(tension, []).append({
                    "recommendation_type": rec_type,
                    "confidence": confidence,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "advisory_snapshot": {
                        k: v for k, v in advisory.items()
                        if k in ("template", "axioms_in_tension", "q2_crisis_intensity")
                    },
                })

                if len(self._pending[tension]) >= self.N_RATIFY:
                    return self._ratify(tension)

        return None

    def _ratify(self, tension: str) -> Dict:
        """Promote a tension to a ratified constitutional axiom."""
        citations = self._pending.pop(tension, [])
        axiom_id = f"AX_{_sha_id(tension).upper()[:6]}"
        avg_conf = sum(c["confidence"] for c in citations) / len(citations)

        axiom = {
            "axiom_id": axiom_id,
            "tension": tension,
            "status": "RATIFIED",
            "ratified_at": datetime.now(timezone.utc).isoformat(),
            "ratification_cycles": len(citations),
            "average_confidence": round(avg_conf, 3),
            "citations": citations,
            "description": (
                f"Constitutionally ratified axiom: the tension '{tension}' "
                f"appeared in {len(citations)} Oracle cycles with average "
                f"confidence {avg_conf:.1%}. The parliament cannot resolve this "
                f"tension — therefore it becomes law."
            ),
        }

        self._ratified.add(tension)
        self._write(axiom)
        logger.info(
            "Constitutional axiom ratified: %s — %s (%.0f%%)",
            axiom_id, tension, avg_conf * 100
        )
        return axiom

    def _write(self, axiom: Dict):
        with self._lock:
            with self._path.open("a") as f:
                f.write(json.dumps(axiom) + "\n")

    def restore_from_records(self, records: List[Dict]) -> int:
        """
        D14 restore — seed living_axioms.jsonl from S3 records on startup.

        Accepts records in either format:
          - living_axioms.jsonl format: has ``"status": "RATIFIED"``
          - body_decisions.jsonl BODY_CONSTITUTIONAL format: has ``"type": "BODY_CONSTITUTIONAL"``

        Only writes records whose tension is not already in the ratified set,
        so running this multiple times is idempotent.

        Returns the number of axioms newly seeded.
        """
        restored = 0
        for rec in records:
            tension = rec.get("tension", "").strip()
            axiom_id = rec.get("axiom_id", "").strip()
            if not tension or not axiom_id:
                continue
            if tension in self._ratified:
                continue  # already present — skip

            if rec.get("status") == "RATIFIED":
                # Already in living_axioms format — write as-is
                axiom = rec
            else:
                # Reconstruct from BODY_CONSTITUTIONAL peer message format
                avg_conf = rec.get("parliament_approval", rec.get("average_confidence", 0.0))
                axiom = {
                    "axiom_id":             axiom_id,
                    "tension":              tension,
                    "status":               "RATIFIED",
                    "ratified_at":          rec.get("ratified_at", rec.get("timestamp", "")),
                    "ratification_cycles":  rec.get("ratification_cycles", 1),
                    "average_confidence":   round(float(avg_conf), 3),
                    "citations":            [],
                    "description": (
                        f"D14-restored constitutional axiom: the tension '{tension}' "
                        f"was originally ratified at confidence {avg_conf:.1%} and "
                        f"has been reseeded from the S3 federation bridge."
                    ),
                    "_restored_from_s3": True,
                }

            self._write(axiom)
            self._ratified.add(tension)
            restored += 1

        if restored:
            logger.info(
                "D14 restore: %d constitutional axiom(s) seeded into living_axioms.jsonl",
                restored,
            )
        return restored

    def pending(self) -> Dict[str, int]:
        """Return tensions and their current ratification vote counts."""
        with self._lock:
            return {t: len(v) for t, v in self._pending.items()}

    def ratified_count(self) -> int:
        return len(self._ratified)

    def load_ratified_axioms(self) -> List[Dict]:
        """Load all ratified axioms for display."""
        axioms = []
        if self._path.exists():
            for line in self._path.open():
                line = line.strip()
                if line:
                    try:
                        rec = json.loads(line)
                        if rec.get("status") == "RATIFIED":
                            axioms.append(rec)
                    except json.JSONDecodeError:
                        pass
        return axioms


# ---------------------------------------------------------------------------
# WorldFeed orchestrator
# ---------------------------------------------------------------------------

class WorldFeed:
    """
    Orchestrates all external data sources and feeds the InputBuffer.

    The BODY (Parliament) is driven by real-world tensions. This class
    is the bridge between external reality and the deliberative engine.

    Systole / Diastole (from Body Bucket.txt):
      MIND expands (contemplates, dreams, generates patterns).
      BODY contracts (governs, filters, interacts with chaos).

    WorldFeed provides the chaos that BODY contracts.
    """

    def __init__(self, input_buffer, fetch_interval_s: int = FETCH_INTERVAL_S):
        self.buffer = input_buffer
        self.interval = fetch_interval_s
        self._seen: Set[str] = set()
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._stats: Dict[str, Any] = {
            "total_events_pushed": 0,
            "fetch_cycles": 0,
            "last_fetch_at": None,
            "events_per_source": {},
            "last_error": None,
        }
        self._lock = threading.Lock()

        self._sources = [
            ("arxiv", ArXivFeed()),
            ("hackernews", HackerNewsFeed()),
            ("gdelt", GDELTFeed()),
            ("wikipedia", WikipediaCurrentEvents()),
            ("crossref", CrossRefFeed()),
        ]

        # Constitutional evolution store (shared with Oracle)
        self.constitution = ConstitutionalStore()

    def fetch_once(self) -> int:
        """Run one complete fetch cycle across all sources. Returns event count."""
        from elpidaapp.parliament_cycle_engine import InputEvent

        total = 0
        # Trim dedup window
        if len(self._seen) > DEDUP_WINDOW:
            self._seen = set(list(self._seen)[-DEDUP_WINDOW // 2:])

        for source_name, source in self._sources:
            try:
                events = source.fetch(self._seen)
                for ev_data in events:
                    ev = InputEvent(
                        system=ev_data["system"],
                        content=ev_data["content"],
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        metadata=ev_data.get("metadata", {}),
                    )
                    self.buffer.push(ev)
                    total += 1

                with self._lock:
                    self._stats["events_per_source"][source_name] = (
                        self._stats["events_per_source"].get(source_name, 0)
                        + len(events)
                    )

                logger.info("WorldFeed [%s]: %d events pushed", source_name, len(events))
                time.sleep(1)  # polite rate-limiting between sources

            except Exception as e:
                logger.warning("WorldFeed [%s] error: %s", source_name, e)
                with self._lock:
                    self._stats["last_error"] = f"{source_name}: {e}"

        with self._lock:
            self._stats["total_events_pushed"] += total
            self._stats["fetch_cycles"] += 1
            self._stats["last_fetch_at"] = datetime.now(timezone.utc).isoformat()

        return total

    def ingest_oracle_advisory(self, advisory: Dict) -> Optional[Dict]:
        """
        Feed an Oracle advisory into the constitutional store.

        Call this from the ParliamentCycleEngine after each Oracle
        adjudication. If a tension crosses the ratification threshold,
        the returned dict is the new constitutional axiom.
        """
        return self.constitution.ingest_oracle(advisory)

    def _loop(self):
        """Background thread: fetch → sleep → fetch → ..."""
        logger.info("WorldFeed background loop started (interval=%ds)", self.interval)
        # First fetch immediately
        self.fetch_once()
        while not self._stop.wait(self.interval):
            self.fetch_once()
        logger.info("WorldFeed background loop stopped.")

    def start(self):
        """Start the background fetch thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="WorldFeed"
        )
        self._thread.start()
        logger.info("WorldFeed started.")

    def stop(self):
        """Stop the background fetch thread."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("WorldFeed stopped.")

    def status(self) -> Dict[str, Any]:
        """Return current feed statistics."""
        with self._lock:
            stats = dict(self._stats)
        stats["buffer_counts"] = self.buffer.counts()
        stats["buffer_total"] = self.buffer.total()
        stats["running"] = self._thread is not None and self._thread.is_alive()
        stats["ratified_axioms"] = self.constitution.ratified_count()
        stats["pending_ratifications"] = self.constitution.pending()
        return stats


# ---------------------------------------------------------------------------
# Manual test entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    class _FakeBuf:
        def __init__(self):
            self._events = []
            self._lock = threading.Lock()
        def push(self, e):
            with self._lock:
                self._events.append(e)
                print(f"  [{e.system.upper()}] {e.content[:120]}")
        def counts(self):
            return {}
        def total(self):
            with self._lock:
                return len(self._events)

    buf = _FakeBuf()
    feed = WorldFeed(buf)

    source_name = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"\n=== WorldFeed test — source: {source_name} ===\n")

    if source_name == "arxiv":
        events = ArXivFeed().fetch(set())
    elif source_name == "hackernews":
        events = HackerNewsFeed().fetch(set())
    elif source_name == "gdelt":
        events = GDELTFeed().fetch(set())
    elif source_name == "wikipedia":
        events = WikipediaCurrentEvents().fetch(set())
    elif source_name == "crossref":
        events = CrossRefFeed().fetch(set())
    else:
        print("Running full fetch cycle...")
        n = feed.fetch_once()
        print(f"\nTotal events pushed: {n}")
        print(f"Status: {json.dumps(feed.status(), indent=2)}")
        sys.exit(0)

    print(f"Events from {source_name}: {len(events)}")
    for i, ev in enumerate(events, 1):
        print(f"\n[{i}] system={ev['system']}")
        print(f"    {ev['content'][:200]}")
        print(f"    meta={ev.get('metadata', {}).get('title', '')[:80]}")
