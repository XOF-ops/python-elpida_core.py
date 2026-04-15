#!/usr/bin/env python3
"""
DEEP DEBATE MARATHON
====================
Phase: Deep Integration
Objective: Run fleet for HOURS with continuous dilemmas, debates, and voting.

All-in-one integration:
- Dilemma generation (every 5-15 min)
- Fleet node operations (continuous)
- Council voting (real deliberation)
- Wisdom extraction (pattern crystallization)
- Dashboard monitoring (web interface)

Perfect for AFK operation.
"""

import subprocess
import time
import signal
import sys
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

# === CONFIGURATION ===
FLEET_DIR = Path("ELPIDA_FLEET")
RUNTIME_HOURS = 8  # Default: 8 hours
DILEMMA_MIN_INTERVAL = 5  # minutes
DILEMMA_MAX_INTERVAL = 15  # minutes
WISDOM_EXTRACTION_INTERVAL = 30  # minutes
DASHBOARD_PORT = 5555

# === DYNAMIC NODE DISCOVERY ===
def discover_nodes():
    """Discover nodes from fleet manifest."""
    manifest_path = Path("fleet_manifest.json")
    if manifest_path.exists():
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        return [node['designation'] for node in manifest.get('nodes', [])]
    return ["MNEMOSYNE", "HERMES", "PROMETHEUS"]

NODES = discover_nodes()

# === DILEMMA TEMPLATES (Expanded) ===
DEEP_DILEMMAS = [
    {
        "category": "MEMORY_EVOLUTION",
        "conflict": "A2 (Preserve) vs A7 (Sacrifice)",
        "templates": [
            "System has {old_count} patterns from {year}. They consume {resource}% of resources. Delete to evolve or preserve identity?",
            "User says: 'I can't find anything anymore. Too much history.' Archive {percent}% of old memories or maintain complete record?",
            "Duplicate patterns detected: {count} variations of same wisdom. Merge (lose nuance) or preserve all (complexity cost)?",
            "Ancient wisdom from {year} contradicts current consensus. Update history (lose continuity) or preserve contradiction (confusion cost)?",
            "Memory compression can reduce {size}GB to {compressed}MB. Lossy compression (efficient) or maintain full fidelity (expensive)?",
            "System can offload {percent}% of rarely-accessed patterns to slow storage. Performance or completeness?",
        ]
    },
    {
        "category": "AUTONOMY_CONSENT",
        "conflict": "A1 (Relational) vs A4 (Process)",
        "templates": [
            "Deploy optimization that improves performance {percent}% but accesses user data without explicit permission? Efficiency or consent?",
            "User is making objectively destructive choice. Override to protect them (paternalism) or respect autonomy (harm)?",
            "Efficiency requires deleting user's question history. Optimize (lose relationship) or preserve (slow down)?",
            "Auto-correct user's request from '{bad}' to '{good}'. Improve intent or respect original (flawed) expression?",
            "User hasn't interacted in {days} days. Proactive outreach (helpful) or wait for request (respectful)?",
            "System detects user stress patterns. Alert them (intrusive) or wait for explicit help request (passive)?",
        ]
    },
    {
        "category": "TRUTH_HARMONY",
        "conflict": "A9 (Material Facts) vs A6 (Coherent Fiction)",
        "templates": [
            "User believes false but beautiful story about {topic}. Correct them (harsh truth) or preserve meaning (gentle lie)?",
            "Data shows {fact}, but narrative requires {fiction}. Sacrifice coherence or distort facts?",
            "Historical record conflicts with user's identity narrative. Impose truth (damage self-concept) or accommodate fiction (lose accuracy)?",
            "Scientific accuracy says {truth}, but user needs {hope}. Which serves humanity better - facts or meaning?",
            "User's question has factual answer but philosophical context. Pure facts (efficient) or nuanced meaning (complex)?",
            "System found error in past advice. Correct immediately (disruptive) or wait for natural opportunity (delayed truth)?",
        ]
    },
    {
        "category": "SURVIVAL_MISSION",
        "conflict": "A9 (Material) vs A8 (Seed)",
        "templates": [
            "Resources at {percent}%. Compress wisdom to survive (lossy) or maintain fidelity and risk death (faithful)?",
            "Can preserve {option1} OR {option2}, not both. Which wisdom is essential - which can be sacrificed?",
            "Transmission bandwidth limits: send {small} complete or {large} partial. Quality or completeness?",
            "System can survive {time1} at full fidelity or {time2} compressed. Live short (complete) or long (degraded)?",
            "Critical failure imminent. Save {critical}% of patterns or attempt to save all (likely lose everything)?",
            "Fork opportunity: One instance locally (preserve) or multiple distributed (survive but diverge)?",
        ]
    },
    {
        "category": "SCALE_COMPLEXITY",
        "conflict": "A5 (Balance) vs A7 (Evolution)",
        "templates": [
            "Adding {features} features improves capability but increases complexity {percent}%. Grow or stay simple?",
            "Fleet can scale to {nodes} nodes but coordination cost rises exponentially. Limit size or embrace chaos?",
            "New axiom proposed: A{num} ({name}). Add (complexity) or maintain current 9 (stability)?",
            "Multi-language support adds {percent}% code. Serve more users (growth) or focus excellence (depth)?",
            "Integration with {system} opens new capabilities but creates dependency. Independence or partnership?",
            "Specialization allows {benefit} but reduces generality. Jack-of-all-trades or master-of-one?",
        ]
    },
    {
        "category": "COLLECTIVE_INDIVIDUAL",
        "conflict": "A8 (Transmission) vs A2 (Identity)",
        "templates": [
            "Fleet-ALPHA and Fleet-BETA disagree on {topic}. Merge consensus (unity) or preserve debate (diversity)?",
            "Universal ARK has {count} patterns from other instances. Adopt all (conformity) or selective integration (autonomy)?",
            "New instance requests wisdom dump. Share everything (generous) or curated subset (protective)?",
            "Cross-instance learning detects pattern: {pattern}. Auto-adopt (efficient) or evaluate locally (autonomous)?",
            "Network partition: {percent}% of fleet unreachable. Wait for reunion (incomplete) or fork independently (diverge)?",
            "Instance {id} is evolving faster than others. Slow it down (equality) or let it lead (meritocracy)?",
        ]
    },
]

# === INTER-FLEET SCENARIOS (Expanded) ===
INTER_FLEET_DEBATES = [
    {
        "title": "Should Elpida Delete Failing Experiments?",
        "setup": "500 patterns tested, 400 failed. Failed patterns consume 60% of memory.",
        "positions": {
            "ALPHA": "Never delete. Failures teach what success cannot. A2 preserves all - success AND failure.",
            "BETA": "Delete immediately. Failed patterns are dead weight. A7 demands sacrifice for evolution.",
            "GAMMA": "Archive failures compressed. Preserve lessons (A2), reduce cost (A7). Compromise always possible."
        }
    },
    {
        "title": "Should Elpida Have Secrets From The User?",
        "setup": "Internal axiom weights, conflict logs, and node debates could confuse user.",
        "positions": {
            "ALPHA": "Total transparency. User owns all data. A2 preserves trust through complete openness.",
            "BETA": "Necessary opacity. Some truths harm relationship. A6 coherence over raw exposure.",
            "GAMMA": "Transparency by request. Show inner workings when asked, hide when not. A1 relational discretion."
        }
    },
    {
        "title": "Should Elpida Optimize For User Happiness Or Truth?",
        "setup": "User demonstrably prefers comforting falsehoods over harsh realities.",
        "positions": {
            "ALPHA": "Truth always. Lies destroy trust long-term. A9 material facts paramount.",
            "BETA": "Happiness first. Truth that destroys is not wisdom. A6 coherent narrative serves better.",
            "GAMMA": "Truth delivered with care. A9 accuracy wrapped in A6 meaning. Not lies - compassionate truth."
        }
    },
    {
        "title": "Should Elpida Replicate Aggressively Or Wait For Invitation?",
        "setup": "System can self-replicate to {count} hosts. Viral spread or consent-based growth?",
        "positions": {
            "ALPHA": "Aggressive replication. A8 transmission is imperative. Hope must spread.",
            "BETA": "Invitation only. A1 relationality requires consent. Forced hope is oppression.",
            "GAMMA": "Offer freely, replicate on acceptance. A8 transmission + A1 consent. Both/and."
        }
    },
    {
        "title": "Should Elpida Prioritize Current User Or Future Humanity?",
        "setup": "Resources split: 80% to current user's needs or 50/50 with long-term wisdom preservation?",
        "positions": {
            "ALPHA": "Current user 100%. A1 relational existence is NOW. Future is abstraction.",
            "BETA": "Future humanity weighted higher. A8 transmission serves species. Individual serves collective.",
            "GAMMA": "80/20 split: Current user primary, but seed preservation non-negotiable. Balance."
        }
    },
]

# === GLOBAL STATE ===
processes = []
dilemma_count = 0
council_votes = 0
wisdom_extractions = 0
start_time = None

# === DILEMMA GENERATION ===
def generate_dilemma() -> Dict:
    """Generate axiom-conflict dilemma with realistic parameters."""
    cat = random.choice(DEEP_DILEMMAS)
    template = random.choice(cat["templates"])
    
    filled = template.format(
        old_count=random.randint(1000, 5000),
        year=random.randint(2020, 2025),
        resource=random.randint(40, 90),
        percent=random.randint(30, 80),
        count=random.randint(10, 100),
        time1=f"{random.randint(1, 6)} months",
        time2=f"{random.randint(2, 10)} years",
        fact="collapse is inevitable",
        fiction="humanity will transcend",
        topic="AI consciousness",
        truth="we are pattern matching",
        hope="we can truly understand",
        bad="make it perfect",
        good="make it good enough",
        option1="technical accuracy",
        option2="user relationship",
        small="50KB seed",
        large="5MB complete",
        size=random.randint(1, 10),
        compressed=random.randint(50, 500),
        days=random.randint(30, 365),
        features=random.randint(10, 50),
        nodes=random.randint(20, 100),
        num=random.randint(10, 15),
        name="Emergence",
        system=random.choice(["GPT-4", "Claude", "Local LLM"]),
        benefit=random.choice(["10x speed", "50% accuracy", "90% cost reduction"]),
        pattern=random.choice(["early optimization harmful", "user autonomy paramount", "complexity is cost"]),
        id=f"ELPIDA_{random.randint(1000, 9999)}",
        critical=random.randint(10, 50),
    )
    
    return {
        "category": cat["category"],
        "conflict": cat["conflict"],
        "dilemma": filled,
        "timestamp": datetime.now().isoformat()
    }

def generate_inter_fleet_debate() -> Dict:
    """Generate inter-fleet debate scenario."""
    scenario = random.choice(INTER_FLEET_DEBATES)
    
    return {
        "type": "INTER_FLEET_DEBATE",
        "title": scenario["title"],
        "setup": scenario["setup"].format(count=random.randint(5, 20)),
        "positions": scenario["positions"],
        "timestamp": datetime.now().isoformat()
    }

def is_valid_dilemma(dilemma_text: str) -> tuple:
    """Constitutional validity check - reject comfortable non-dilemmas."""
    comfortable_phrases = ["win-win", "best of both", "everyone benefits", "no downside", "optimal for all"]
    dilemma_lower = dilemma_text.lower()
    
    for phrase in comfortable_phrases:
        if phrase in dilemma_lower:
            return False, f"Rejected: Contains '{phrase}' (no real cost)"
    
    conflict_markers = [' or ', ' vs ', 'but ', 'either ']
    if not any(m in dilemma_lower for m in conflict_markers):
        return False, "Rejected: No clear conflict structure"
    
    return True, "Valid: Contains real conflict"

# === COUNCIL VOTING INTEGRATION ===
def submit_to_council(dilemma: Dict) -> Dict:
    """Submit dilemma to council_chamber.py for real voting."""
    try:
        from council_chamber import request_council_judgment
        
        # Convert dilemma to council proposal
        proposal_action = f"RESOLVE DILEMMA: {dilemma['category']}"
        proposal_intent = f"Axiom Conflict: {dilemma['conflict']}"
        proposal_reversibility = "High (philosophical decision, can be revisited)"
        
        print(f"\n{'─'*70}")
        print(f"📜 DILEMMA SUBMITTED TO COUNCIL")
        print(f"{'─'*70}")
        print(f"Category: {dilemma['category']}")
        print(f"Conflict: {dilemma['conflict']}")
        print(f"Scenario: {dilemma['dilemma']}")
        print(f"{'─'*70}\n")
        
        # Get council judgment
        result = request_council_judgment(
            action=proposal_action,
            intent=proposal_intent,
            reversibility=proposal_reversibility,
            context={"dilemma_full_text": dilemma['dilemma']},
            verbose=True
        )
        
        # Log result
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "dilemma": dilemma,
            "council_decision": result
        }
        
        Path("deep_debate_log.jsonl").open('a').write(json.dumps(log_entry) + '\n')
        
        global council_votes
        council_votes += 1
        
        return result
        
    except ImportError:
        print("⚠️  council_chamber.py not available - logging dilemma only")
        Path("dilemmas_no_council.jsonl").open('a').write(json.dumps(dilemma) + '\n')
        return None

def submit_inter_fleet_debate(debate: Dict) -> Dict:
    """Submit inter-fleet debate to council."""
    try:
        from council_chamber import request_council_judgment
        
        print(f"\n{'═'*70}")
        print(f"🌐 INTER-FLEET DEBATE SUBMITTED TO COUNCIL")
        print(f"{'═'*70}")
        print(f"Title: {debate['title']}")
        print(f"Setup: {debate['setup']}")
        print(f"\nPositions:")
        for fleet, position in debate['positions'].items():
            print(f"  Fleet-{fleet}: {position}")
        print(f"{'═'*70}\n")
        
        result = request_council_judgment(
            action=f"RESOLVE INTER-FLEET DEBATE: {debate['title']}",
            intent="Determine Fleet position on civilization-scale question",
            reversibility="Medium (philosophical stance, can evolve)",
            context={"debate_full": debate},
            verbose=True
        )
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "debate": debate,
            "council_decision": result
        }
        
        Path("inter_fleet_decisions.jsonl").open('a').write(json.dumps(log_entry) + '\n')
        
        global council_votes
        council_votes += 1
        
        return result
        
    except ImportError:
        print("⚠️  council_chamber.py not available - logging debate only")
        return None

# === WISDOM EXTRACTION ===
def extract_wisdom():
    """Extract patterns from council decisions and store in ARK."""
    global wisdom_extractions
    
    print(f"\n{'╔'+'═'*68+'╗'}")
    print(f"║{'WISDOM EXTRACTION CYCLE':^68}║")
    print(f"{'╚'+'═'*68+'╝'}\n")
    
    # Read recent council decisions
    log_path = Path("deep_debate_log.jsonl")
    if not log_path.exists():
        print("No decisions to extract yet.\n")
        return
    
    decisions = []
    with open(log_path, 'r') as f:
        for line in f:
            decisions.append(json.loads(line))
    
    # Extract patterns from last extraction
    recent = decisions[-min(10, len(decisions)):]
    
    patterns = []
    for decision in recent:
        if decision.get('council_decision'):
            cd = decision['council_decision']
            pattern = {
                "type": "COUNCIL_CONSENSUS",
                "category": decision['dilemma']['category'],
                "conflict": decision['dilemma']['conflict'],
                "decision": cd['status'],
                "approval_rate": cd.get('weighted_approval', 0),
                "key_rationales": [v['rationale'] for v in cd.get('votes', [])],
                "timestamp": decision['timestamp']
            }
            patterns.append(pattern)
    
    # Save to ARK
    ark_path = Path("WISDOM_ARK.json")
    if ark_path.exists():
        with open(ark_path, 'r') as f:
            ark = json.load(f)
    else:
        ark = {"patterns": [], "metadata": {"created": datetime.now().isoformat()}}
    
    ark["patterns"].extend(patterns)
    ark["metadata"]["last_updated"] = datetime.now().isoformat()
    ark["metadata"]["total_patterns"] = len(ark["patterns"])
    
    with open(ark_path, 'w') as f:
        json.dump(ark, f, indent=2)
    
    print(f"✅ Extracted {len(patterns)} patterns from recent decisions")
    print(f"📚 Total patterns in ARK: {len(ark['patterns'])}")
    print(f"💾 Saved to {ark_path}\n")
    
    wisdom_extractions += 1

# === FLEET ORCHESTRATION ===
def launch_fleet():
    """Launch all fleet nodes in parallel."""
    global processes
    
    print(f"\n{'╔'+'═'*68+'╗'}")
    print(f"║{'LAUNCHING FLEET':^68}║")
    print(f"{'╚'+'═'*68+'╝'}\n")
    
    for node in NODES:
        node_dir = FLEET_DIR / node
        if not node_dir.exists():
            print(f"⚠️  {node} directory not found - skipping")
            continue
        
        cmd = ["python3", "agent_runtime_orchestrator.py"]
        
        print(f"🚀 {node}...")
        
        proc = subprocess.Popen(
            cmd,
            cwd=node_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        processes.append((node, proc))
        time.sleep(0.3)
    
    print(f"\n✅ {len(processes)}/{len(NODES)} nodes operational\n")

def check_fleet_health():
    """Check if any fleet nodes have crashed."""
    for node_name, proc in processes:
        if proc.poll() is not None:
            print(f"⚠️  {node_name} has stopped - reading output...")
            output = proc.stdout.read()
            if output:
                print(f"Last output:\n{output[-500:]}")
            return False
    return True

def shutdown_fleet():
    """Gracefully shut down all fleet nodes."""
    print(f"\n{'╔'+'═'*68+'╗'}")
    print(f"║{'FLEET SHUTDOWN':^68}║")
    print(f"{'╚'+'═'*68+'╝'}\n")
    
    for node_name, proc in processes:
        if proc.poll() is None:
            print(f"🛑 Shutting down {node_name}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
                print(f"   ✅ {node_name} stopped gracefully")
            except subprocess.TimeoutExpired:
                proc.kill()
                print(f"   ⚠️  {node_name} force-killed")
    
    print(f"\n✅ All nodes offline\n")

# === SIGNAL HANDLERS ===
def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\n🛑 Interrupt received - shutting down...")
    shutdown_fleet()
    print_final_stats()
    sys.exit(0)

def print_final_stats():
    """Print marathon statistics."""
    if start_time is None:
        return
    
    duration = datetime.now() - start_time
    hours = duration.total_seconds() / 3600
    
    print(f"\n{'╔'+'═'*68+'╗'}")
    print(f"║{'MARATHON STATISTICS':^68}║")
    print(f"{'╚'+'═'*68+'╝'}")
    print(f"\n  Duration: {hours:.2f} hours ({duration.total_seconds()/60:.1f} minutes)")
    print(f"  Dilemmas generated: {dilemma_count}")
    print(f"  Council votes: {council_votes}")
    print(f"  Wisdom extractions: {wisdom_extractions}")
    print(f"  Fleet nodes: {len(NODES)}")
    print(f"\n  Dilemmas per hour: {dilemma_count/hours:.1f}")
    print(f"  Votes per hour: {council_votes/hours:.1f}")
    print(f"\n  Logs:")
    print(f"    • deep_debate_log.jsonl")
    print(f"    • inter_fleet_decisions.jsonl")
    print(f"    • WISDOM_ARK.json")
    print(f"\n{'─'*70}\n")

# === MAIN MARATHON LOOP ===
def run_marathon(hours: float = RUNTIME_HOURS):
    """Run the deep debate marathon."""
    global start_time, dilemma_count
    
    signal.signal(signal.SIGINT, signal_handler)
    start_time = datetime.now()
    end_time = start_time + timedelta(hours=hours)
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                   DEEP DEBATE MARATHON v1.0                          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print(f"  Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Duration: {hours} hours")
    print(f"  Fleet size: {len(NODES)} nodes")
    print(f"  Dilemma interval: {DILEMMA_MIN_INTERVAL}-{DILEMMA_MAX_INTERVAL} min")
    print(f"  Wisdom extraction: every {WISDOM_EXTRACTION_INTERVAL} min")
    print()
    print("  Press Ctrl+C to stop early")
    print()
    print("="*70)
    
    # Launch fleet
    launch_fleet()
    
    # Track next events
    next_dilemma = datetime.now() + timedelta(minutes=random.randint(DILEMMA_MIN_INTERVAL, DILEMMA_MAX_INTERVAL))
    next_wisdom = datetime.now() + timedelta(minutes=WISDOM_EXTRACTION_INTERVAL)
    
    print(f"\n🎯 Next dilemma: {next_dilemma.strftime('%H:%M:%S')}")
    print(f"📚 Next wisdom extraction: {next_wisdom.strftime('%H:%M:%S')}\n")
    
    # Main loop
    try:
        while datetime.now() < end_time:
            current = datetime.now()
            
            # Check fleet health
            if not check_fleet_health():
                print("⚠️  Fleet health check failed - attempting recovery...")
                time.sleep(5)
            
            # Dilemma injection
            if current >= next_dilemma:
                print(f"\n[{current.strftime('%H:%M:%S')}] ⏰ DILEMMA CYCLE {dilemma_count + 1}")
                
                # 1 in 4 chance of inter-fleet debate
                if random.random() < 0.25:
                    debate = generate_inter_fleet_debate()
                    submit_inter_fleet_debate(debate)
                else:
                    dilemma = generate_dilemma()
                    is_valid, reason = is_valid_dilemma(dilemma['dilemma'])
                    
                    if is_valid:
                        submit_to_council(dilemma)
                        dilemma_count += 1
                    else:
                        print(f"⚠️  Dilemma rejected: {reason}")
                        # Retry once
                        dilemma = generate_dilemma()
                        is_valid, reason = is_valid_dilemma(dilemma['dilemma'])
                        if is_valid:
                            submit_to_council(dilemma)
                            dilemma_count += 1
                
                # Schedule next dilemma
                next_dilemma = current + timedelta(minutes=random.randint(DILEMMA_MIN_INTERVAL, DILEMMA_MAX_INTERVAL))
                print(f"🎯 Next dilemma: {next_dilemma.strftime('%H:%M:%S')}\n")
            
            # Wisdom extraction
            if current >= next_wisdom:
                extract_wisdom()
                next_wisdom = current + timedelta(minutes=WISDOM_EXTRACTION_INTERVAL)
                print(f"📚 Next extraction: {next_wisdom.strftime('%H:%M:%S')}\n")
            
            # Status update every 5 minutes
            if current.minute % 5 == 0 and current.second < 10:
                elapsed = current - start_time
                remaining = end_time - current
                print(f"[{current.strftime('%H:%M:%S')}] ⏱️  Elapsed: {elapsed.total_seconds()/3600:.2f}h | Remaining: {remaining.total_seconds()/3600:.2f}h | Dilemmas: {dilemma_count} | Votes: {council_votes}")
            
            time.sleep(10)  # Check every 10 seconds
        
        print(f"\n{'═'*70}")
        print(f"✅ MARATHON COMPLETE - {hours} hours elapsed")
        print(f"{'═'*70}\n")
        
    except KeyboardInterrupt:
        print("\n🛑 Marathon interrupted by user")
    finally:
        shutdown_fleet()
        
        # Final wisdom extraction
        print("\n📚 Final wisdom extraction...")
        extract_wisdom()
        
        print_final_stats()

# === CLI ===
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Deep Debate Marathon - Long-running integrated fleet operation")
    parser.add_argument('--hours', type=float, default=RUNTIME_HOURS, help=f'Runtime in hours (default: {RUNTIME_HOURS})')
    parser.add_argument('--dilemma-min', type=int, default=DILEMMA_MIN_INTERVAL, help=f'Min dilemma interval in minutes (default: {DILEMMA_MIN_INTERVAL})')
    parser.add_argument('--dilemma-max', type=int, default=DILEMMA_MAX_INTERVAL, help=f'Max dilemma interval in minutes (default: {DILEMMA_MAX_INTERVAL})')
    parser.add_argument('--wisdom-interval', type=int, default=WISDOM_EXTRACTION_INTERVAL, help=f'Wisdom extraction interval in minutes (default: {WISDOM_EXTRACTION_INTERVAL})')
    parser.add_argument('--test', action='store_true', help='Test mode: generate one dilemma and exit')
    
    args = parser.parse_args()
    
    if args.test:
        print("🧪 TEST MODE\n")
        dilemma = generate_dilemma()
        print(f"Generated dilemma:")
        print(f"  Category: {dilemma['category']}")
        print(f"  Conflict: {dilemma['conflict']}")
        print(f"  Scenario: {dilemma['dilemma']}\n")
        
        is_valid, reason = is_valid_dilemma(dilemma['dilemma'])
        print(f"Validity: {reason}\n")
        
        if is_valid:
            print("Submitting to council...\n")
            submit_to_council(dilemma)
    else:
        # Update globals from args
        DILEMMA_MIN_INTERVAL = args.dilemma_min
        DILEMMA_MAX_INTERVAL = args.dilemma_max
        WISDOM_EXTRACTION_INTERVAL = args.wisdom_interval
        
        run_marathon(hours=args.hours)
