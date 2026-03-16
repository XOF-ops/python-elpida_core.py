"""
Domain Internet Grounding
=========================

Gives Elpida's 16 domains access to live web data.
Two search backends, automatic failover:

  1. DuckDuckGo text search (primary — zero API keys)
  2. Wikipedia API (fallback — always available, English content)

Each domain query can be optionally augmented with real-world context
before the LLM prompt is built. The grounding fetches 3-5 results
and extracts the most relevant snippets.

Usage:
    from elpidaapp.domain_grounding import ground_query

    context = ground_query("renewable energy policy EU 2026")
    # Returns a string of web snippets to inject into domain prompts

Architecture:
    - Rate limited: 1 search per 3 seconds (global)
    - Timeout: 8 seconds per search
    - Cache: LRU 128 entries (avoids re-searching same topics)
    - Graceful degradation: returns "" on any failure
    - Language filter: drops non-Latin-script results
"""

import logging
import re
import time
import threading
from functools import lru_cache
from typing import Optional, List, Dict

import requests

logger = logging.getLogger("elpidaapp.grounding")

# Rate limiting — 1 search per 3 seconds
_lock = threading.Lock()
_last_search_time = 0.0
_RATE_LIMIT_S = 3.0
_TIMEOUT_S = 8


def _rate_limit():
    """Enforce global rate limit."""
    global _last_search_time
    with _lock:
        now = time.monotonic()
        elapsed = now - _last_search_time
        if elapsed < _RATE_LIMIT_S:
            time.sleep(_RATE_LIMIT_S - elapsed)
        _last_search_time = time.monotonic()


def _is_english(text: str) -> bool:
    """Check if text is predominantly Latin script (English)."""
    if not text:
        return False
    latin = len(re.findall(r'[a-zA-Z]', text))
    return latin / max(len(text), 1) > 0.5


def _search_ddg(query: str, max_results: int) -> List[Dict[str, str]]:
    """Search via DuckDuckGo DDGS library."""
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results + 2))
        # Filter to English results only
        english = [
            r for r in results
            if _is_english(r.get("title", "") + r.get("body", ""))
        ]
        return [
            {"title": r.get("title", ""), "body": r.get("body", "")}
            for r in english[:max_results]
        ]
    except Exception as e:
        logger.debug("DDG search failed: %s", e)
        return []


def _search_wikipedia(query: str, max_results: int) -> List[Dict[str, str]]:
    """Search via Wikipedia API (always English, always available)."""
    try:
        resp = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "format": "json",
                "utf8": 1,
            },
            headers={"User-Agent": "ElpidaBot/1.0"},
            timeout=_TIMEOUT_S,
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("query", {}).get("search", []):
            title = item.get("title", "")
            # Strip HTML tags from snippet
            snippet = re.sub(r'<[^>]+>', '', item.get("snippet", ""))
            if title and snippet:
                results.append({"title": title, "body": snippet})
        return results[:max_results]
    except Exception as e:
        logger.debug("Wikipedia search failed: %s", e)
        return []


@lru_cache(maxsize=128)
def ground_query(query: str, max_results: int = 3) -> str:
    """
    Search the web for context relevant to a domain query.

    Tries DuckDuckGo first, falls back to Wikipedia API.

    Args:
        query: The search query (typically the problem + domain keywords)
        max_results: Maximum number of results to include (default 3)

    Returns:
        Formatted string of web snippets, or "" on any failure.
    """
    _rate_limit()

    # Try DuckDuckGo first
    results = _search_ddg(query, max_results)

    # Fallback to Wikipedia if DDG returned nothing
    if not results:
        results = _search_wikipedia(query, max_results)

    if not results:
        return ""

    snippets = []
    for r in results[:max_results]:
        title = r["title"].strip()
        body = r["body"].strip()
        if title and body:
            snippets.append(f"• {title}: {body}")

    if not snippets:
        return ""

    return (
        "─── LIVE WEB CONTEXT ───\n"
        + "\n".join(snippets)
        + "\n─── END WEB CONTEXT ───"
    )


def ground_domain_query(
    problem: str,
    domain_name: str,
    domain_keywords: Optional[str] = None,
    max_results: int = 3,
) -> str:
    """
    Build a domain-specific grounding query and search.

    Combines the problem with domain-relevant keywords for
    more targeted results.

    Args:
        problem: The original problem statement
        domain_name: e.g. "Ethics", "Economics", "Security"
        domain_keywords: Optional extra search terms
        max_results: Number of results

    Returns:
        Formatted web context string, or "" on failure.
    """
    # Build a focused search query
    # Take first 100 chars of problem + domain name
    short_problem = problem[:100].strip()
    terms = [short_problem, domain_name]
    if domain_keywords:
        terms.append(domain_keywords)
    query = " ".join(terms)

    return ground_query(query, max_results=max_results)


# Domain-specific search keyword hints
DOMAIN_SEARCH_HINTS = {
    0: None,          # D0 Origin — no grounding (frozen genesis)
    1: "policy ethics",
    2: "technology innovation",
    3: "economics trade",
    4: "philosophy epistemology",
    5: "law legal",
    6: "social community",
    7: "environment climate",
    8: "security defense",
    9: "education knowledge",
    10: "art culture creativity",
    11: "health medicine wellbeing",
    12: "infrastructure systems",
    13: None,          # D13 Archive — uses Perplexity
    14: None,          # D14 Persistence — internal
    15: None,          # D15 Reality Interface — internal
}
