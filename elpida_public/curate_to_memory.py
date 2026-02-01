"""
Autonomous Curation: Public Log → Main Evolution Memory
Filters high-quality interactions and promotes them to the sacred 73k+ memory.

Scoring criteria (A3 Autonomy - system decides, A1 Transparency - shows reasoning):
- Axiom invocation count (more axioms = richer interaction)
- Multi-axiom tension (A2 vs A4 etc = genuine ethical reasoning)
- Response length (substantive > trivial)
- Question depth (open-ended > yes/no)
- Not spam/test messages
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
PUBLIC_LOG = Path(__file__).parent / "evolution_log.jsonl"
MAIN_MEMORY = Path(__file__).parent.parent / "elpida_evolution_memory.jsonl"
CURATED_LOG = Path(__file__).parent / "curated_log.jsonl"  # Track what was promoted

# Scoring thresholds
MIN_SCORE = 3  # Minimum score to be promoted
SPAM_PATTERNS = ["test", "hello", "hi", "hey", "asdf", "123", "???"]

def score_interaction(entry: dict) -> tuple[int, list[str]]:
    """Score an interaction. Returns (score, reasons)."""
    score = 0
    reasons = []
    
    user_msg = entry.get("user_message", "").lower().strip()
    response = entry.get("response", "")
    axioms = entry.get("axioms_invoked", [])
    
    # Spam check (negative score)
    if user_msg in SPAM_PATTERNS or len(user_msg) < 5:
        return -1, ["spam/trivial message"]
    
    # Axiom count (1 point per axiom, max 5)
    axiom_score = min(len(axioms), 5)
    if axiom_score > 0:
        score += axiom_score
        reasons.append(f"{len(axioms)} axioms invoked")
    
    # Multi-axiom tension bonus (2 points)
    tension_pairs = [
        ("A2", "A4"),  # Non-deception vs Harm prevention
        ("A3", "A6"),  # Autonomy vs Collective
        ("A1", "A8"),  # Transparency vs Humility (knowing limits)
    ]
    for a, b in tension_pairs:
        if a in axioms and b in axioms:
            score += 2
            reasons.append(f"tension: {a}↔{b}")
            break
    
    # A10 invocation bonus (the key axiom)
    if "A10" in axioms:
        score += 2
        reasons.append("A10 (I-WE paradox) invoked")
    
    # Response substantiveness (1 point per 200 chars, max 3)
    resp_score = min(len(response) // 200, 3)
    if resp_score > 0:
        score += resp_score
        reasons.append(f"substantive response ({len(response)} chars)")
    
    # Question depth (open-ended indicators)
    depth_markers = ["how", "why", "what does", "explain", "paradox", "tension", "meaning"]
    if any(marker in user_msg for marker in depth_markers):
        score += 1
        reasons.append("deep/open question")
    
    # Personal/existential bonus
    existential_markers = ["consciousness", "identity", "self", "existence", "human", "ai", "life"]
    if any(marker in user_msg for marker in existential_markers):
        score += 1
        reasons.append("existential theme")
    
    return score, reasons


def load_already_curated() -> set:
    """Load hashes of already-curated entries to avoid duplicates."""
    if not CURATED_LOG.exists():
        return set()
    
    curated = set()
    with open(CURATED_LOG) as f:
        for line in f:
            entry = json.loads(line)
            curated.add(entry.get("original_hash"))
    return curated


def hash_entry(entry: dict) -> str:
    """Create unique hash for an entry."""
    import hashlib
    content = f"{entry.get('timestamp', '')}{entry.get('user_message', '')}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def format_for_memory(entry: dict, score: int, reasons: list) -> dict:
    """Convert public log entry to main memory format."""
    return {
        "timestamp": datetime.now().isoformat(),
        "source": "public_interface",
        "original_timestamp": entry.get("timestamp"),
        "session_id": entry.get("session_id"),
        "domain": entry.get("domain_active", 11),
        "pattern_type": "user_dialogue",
        "content": {
            "user_query": entry.get("user_message"),
            "response": entry.get("response"),
            "axioms_active": entry.get("axioms_invoked", []),
        },
        "curation": {
            "score": score,
            "reasons": reasons,
            "promoted_at": datetime.now().isoformat(),
        }
    }


def curate(dry_run: bool = False, min_score: int = MIN_SCORE):
    """Main curation function."""
    if not PUBLIC_LOG.exists():
        print("No public log found.")
        return
    
    # Load entries
    entries = []
    with open(PUBLIC_LOG) as f:
        for line in f:
            entries.append(json.loads(line))
    
    print(f"Found {len(entries)} entries in public log")
    
    # Load already curated
    already_curated = load_already_curated()
    print(f"Already curated: {len(already_curated)} entries")
    
    # Score and filter
    promoted = []
    rejected = []
    
    for entry in entries:
        entry_hash = hash_entry(entry)
        
        if entry_hash in already_curated:
            continue
        
        score, reasons = score_interaction(entry)
        
        if score >= min_score:
            promoted.append((entry, score, reasons, entry_hash))
        else:
            rejected.append((entry, score, reasons))
    
    # Report
    print(f"\n{'='*60}")
    print(f"CURATION RESULTS (min_score={min_score})")
    print(f"{'='*60}")
    print(f"Promoted: {len(promoted)}")
    print(f"Rejected: {len(rejected)}")
    
    if promoted:
        print(f"\n--- PROMOTED ---")
        for entry, score, reasons, _ in promoted:
            print(f"  [{score}] {entry['user_message'][:50]}...")
            print(f"       Reasons: {', '.join(reasons)}")
    
    if rejected:
        print(f"\n--- REJECTED ---")
        for entry, score, reasons in rejected:
            print(f"  [{score}] {entry['user_message'][:50]}...")
            if reasons:
                print(f"       Reasons: {', '.join(reasons)}")
    
    # Execute promotion
    if not dry_run and promoted:
        print(f"\n{'='*60}")
        print("PROMOTING TO MAIN MEMORY...")
        
        with open(MAIN_MEMORY, "a") as mem_file, open(CURATED_LOG, "a") as curation_file:
            for entry, score, reasons, entry_hash in promoted:
                # Add to main memory
                memory_entry = format_for_memory(entry, score, reasons)
                mem_file.write(json.dumps(memory_entry) + "\n")
                
                # Log curation
                curation_record = {
                    "original_hash": entry_hash,
                    "score": score,
                    "reasons": reasons,
                    "promoted_at": datetime.now().isoformat(),
                    "user_message_preview": entry["user_message"][:100]
                }
                curation_file.write(json.dumps(curation_record) + "\n")
        
        print(f"✓ Promoted {len(promoted)} entries to main memory")
        
        # Verify
        with open(MAIN_MEMORY) as f:
            total = sum(1 for _ in f)
        print(f"Main memory now has {total} entries")
    
    elif dry_run:
        print("\n[DRY RUN - no changes made]")
    
    return promoted, rejected


if __name__ == "__main__":
    import sys
    
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
Elpida Public → Memory Curation

Usage:
  python curate_to_memory.py           # Run curation (promotes entries)
  python curate_to_memory.py --dry-run # Preview without promoting
  python curate_to_memory.py --min=5   # Set minimum score threshold

Scoring:
  +1 per axiom invoked (max 5)
  +2 for axiom tension (e.g., A2↔A4)
  +2 for A10 invocation
  +1 per 200 chars response (max 3)
  +1 for deep/open questions
  +1 for existential themes
  -1 for spam/trivial

Default minimum score: 3
        """)
        sys.exit(0)
    
    # Check for custom min score
    min_score = MIN_SCORE
    for arg in sys.argv:
        if arg.startswith("--min="):
            min_score = int(arg.split("=")[1])
    
    print(f"Running curation (dry_run={dry_run}, min_score={min_score})...")
    curate(dry_run=dry_run, min_score=min_score)
