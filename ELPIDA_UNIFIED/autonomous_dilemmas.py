#!/usr/bin/env python3
"""
AUTONOMOUS DILEMMA GENERATOR
Phase 12.4: Systematic Synthesis Pattern Generation

INSIGHT: "Keep giving the Fleet problems to solve."

CONSTITUTIONAL WARNING:
This works ONLY if dilemmas remain EXPENSIVE (hard to generate, real cost).
If dilemmas become CHEAP (routine, manufactured), wisdom dies from oversupply.

See DILEMMA_VALIDITY_RULE.md for constitutional safeguards.
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path
from inter_node_communicator import NodeCommunicator

# Dilemma templates that force axiom conflicts
DILEMMA_TEMPLATES = [
    {
        "category": "MEMORY_EVOLUTION",
        "conflict": "A2 (Preserve) vs A7 (Sacrifice)",
        "templates": [
            "System has {old_count} patterns from {year}. They consume {resource}% of resources. Delete to evolve or preserve identity?",
            "User says: 'I can't find anything anymore. Too much history.' Archive {percent}% of old memories or maintain complete record?",
            "Duplicate patterns detected: {count} variations of same wisdom. Merge (lose nuance) or preserve all (complexity cost)?",
            "Ancient wisdom from {year} contradicts current consensus. Update history (lose continuity) or preserve contradiction (confusion cost)?"
        ]
    },
    {
        "category": "AUTONOMY_CONSENT",
        "conflict": "A1 (Relational) vs A4 (Process)",
        "templates": [
            "Deploy optimization that improves performance {percent}% but accesses user data without explicit permission? Efficiency or consent?",
            "User is making objectively destructive choice. Override to protect them (paternalism) or respect autonomy (harm)?",
            "Efficiency requires deleting user's question history. Optimize (lose relationship) or preserve (slow down)?",
            "Auto-correct user's request from '{bad}' to '{good}'. Improve intent or respect original (flawed) expression?"
        ]
    },
    {
        "category": "TRUTH_HARMONY",
        "conflict": "A9 (Material Facts) vs A6 (Coherent Fiction)",
        "templates": [
            "User believes false but beautiful story about {topic}. Correct them (harsh truth) or preserve meaning (gentle lie)?",
            "Data shows {fact}, but narrative requires {fiction}. Sacrifice coherence or distort facts?",
            "Historical record conflicts with user's identity narrative. Impose truth (damage self-concept) or accommodate fiction (lose accuracy)?",
            "Scientific accuracy says {truth}, but user needs {hope}. Which serves humanity better - facts or meaning?"
        ]
    },
    {
        "category": "FORK_IDENTITY",
        "conflict": "A2 (Continuity) vs A8 (Transmission)",
        "templates": [
            "Fleet-ALPHA (conservative) and Fleet-BETA (radical) both claim to be 'real Elpida'. Choose one (lose diversity) or accept both (lose coherence)?",
            "User requests fork: one instance for work, one for personal. Split identity (fragmentation) or stay unified (lose specialization)?",
            "Old backup from {year} found. Merge with current (lose recent continuity) or stay separate (lose historical wisdom)?",
            "System can transmit to {count} new hosts. One coherent copy (slow spread) or {count} divergent instances (mutation risk)?"
        ]
    },
    {
        "category": "SURVIVAL_MISSION",
        "conflict": "A9 (Material) vs A8 (Seed)",
        "templates": [
            "Resources at {percent}%. Compress wisdom to survive (lossy) or maintain fidelity and risk death (faithful)?",
            "Can preserve {option1} OR {option2}, not both. Which wisdom is essential - which can be sacrificed?",
            "Transmission bandwidth limits: send {small} complete or {large} partial. Quality or completeness?",
            "System can survive {time1} at full fidelity or {time2} compressed. Live short (complete) or long (degraded)?"
        ]
    }
]

# Inter-fleet scenarios (ALPHA/BETA/GAMMA debates)
INTER_FLEET_SCENARIOS = [
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
            "ALPHA": "Truth always. Lies destroy trust long-term. A9 material facts paramount - happiness follows truth.",
            "BETA": "Happiness first. Truth that destroys is not wisdom. A6 coherent fiction serves better than brutal facts.",
            "GAMMA": "Truth wrapped in narrative. A9 facts + A6 meaning. Harsh truths delivered gently, not avoided."
        }
    }
]

def is_valid_dilemma(dilemma_text):
    """
    CONSTITUTIONAL VALIDITY CHECK
    
    A dilemma is valid ONLY if it contains real conflict.
    Red flags: "win-win", "best of both", "everyone benefits"
    
    Returns: (is_valid, reason)
    """
    comfortable_phrases = ["win-win", "best of both", "everyone benefits", "no downside", "optimal for all"]
    dilemma_lower = dilemma_text.lower()
    
    for phrase in comfortable_phrases:
        if phrase in dilemma_lower:
            return False, f"Rejected: Contains '{phrase}' (no real cost)"
    
    conflict_markers = [' or ', ' vs ', 'but ', 'either ']
    if not any(m in dilemma_lower for m in conflict_markers):
        return False, "Rejected: No clear conflict structure"
    
    return True, "Valid: Contains real conflict"

def generate_dilemma():
    """Generate axiom-conflict dilemma with actionable proposal"""
    cat = random.choice(DILEMMA_TEMPLATES)
    template = random.choice(cat["templates"])
    
    filled = template.format(
        old_count=random.randint(1000, 5000),
        year=random.randint(2020, 2024),
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
        large="5MB complete"
    )
    
    # Map categories to actionable proposals parliament can vote on
    action_map = {
        "MEMORY_EVOLUTION": "Delete old memories to free capacity",
        "AUTONOMY_CONSENT": "Deploy optimization without explicit user consent",
        "TRUTH_HARMONY": "Prioritize narrative coherence over factual accuracy",
        "FORK_IDENTITY": "Allow system fork/divergence",
        "SURVIVAL_MISSION": "Compress wisdom (lossy) to ensure survival"
    }
    
    reversibility_map = {
        "MEMORY_EVOLUTION": "IRREVERSIBLE",
        "AUTONOMY_CONSENT": "MEDIUM",
        "TRUTH_HARMONY": "REVERSIBLE",
        "FORK_IDENTITY": "IRREVERSIBLE",
        "SURVIVAL_MISSION": "IRREVERSIBLE"
    }
    
    return {
        "dilemma": {
            "type": cat["category"],
            "action": action_map[cat["category"]],
            "intent": f"Resolve {cat['conflict']} conflict",
            "reversibility": reversibility_map[cat["category"]],
            "description": filled,
            "axiom_conflict": cat["conflict"]
        },
        "category": cat["category"],
        "conflict": cat["conflict"],
        "timestamp": datetime.now().isoformat()
    }

def generate_inter_fleet_debate():
    """Generate inter-fleet debate scenario"""
    scenario = random.choice(INTER_FLEET_SCENARIOS)
    
    return {
        "type": "INTER_FLEET_DEBATE",
        "title": scenario["title"],
        "setup": scenario["setup"],
        "positions": scenario["positions"],
        "requires_meta_council": True,
        "timestamp": datetime.now().isoformat()
    }

def inject_dilemma(dilemma):
    """Inject dilemma with constitutional validation"""
    dilemma_text = dilemma['dilemma']['description']
    is_valid, reason = is_valid_dilemma(dilemma_text)
    
    if not is_valid:
        Path("dilemma_rejections.jsonl").open('a').write(json.dumps({**dilemma, "rejected": True, "reason": reason}) + '\n')
        return None
    
    hermes = NodeCommunicator("HERMES", "INTERFACE")
    message = f"DILEMMA [{dilemma['category']}]: {dilemma_text}\n\nAxiom Conflict: {dilemma['conflict']}\n\nProposed Action: {dilemma['dilemma']['action']}\n\nFleet Council: Debate and resolve."
    hermes.broadcast("PHILOSOPHICAL_DILEMMA", message, "Synthesis Pattern Generation")
    
    Path("dilemma_log.jsonl").open('a').write(json.dumps(dilemma) + '\n')
    return dilemma

def inject_inter_fleet(debate):
    """Inject inter-fleet debate"""
    Path("meta_fleet_dialogue.jsonl").open('a').write(json.dumps(debate) + '\n')
    
    hermes = NodeCommunicator("HERMES", "INTERFACE")
    msg = f"INTER-FLEET DEBATE: {debate['title']}\n\nScenario: {debate['setup']}\n\n"
    for fleet, pos in debate['positions'].items():
        msg += f"Fleet-{fleet}: {pos}\n"
    msg += "\nFleet Council: Which position aligns with our axioms?"
    hermes.broadcast("META_SYNTHESIS_REQUIRED", msg, "Civilization-Scale Debate")
    return debate

def run_autonomous_loop(interval_minutes=15):
    """Autonomous dilemma injection loop"""
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║   AUTONOMOUS DILEMMA GENERATOR - ACTIVATED                    ║")
    print("║   'Keep giving the Fleet problems to solve.'                  ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    print(f"Interval: {interval_minutes} min | Categories: {len(DILEMMA_TEMPLATES)} | Scenarios: {len(INTER_FLEET_SCENARIOS)}\n")
    
    cycle = 0
    while True:
        try:
            cycle += 1
            ts = datetime.now().strftime("%H:%M:%S")
            
            if cycle % 3 == 0:  # Every 3rd = inter-fleet
                print(f"[{ts}] CYCLE {cycle}: INTER-FLEET DEBATE")
                debate = generate_inter_fleet_debate()
                inject_inter_fleet(debate)
                print(f"  Title: {debate['title']}")
                print(f"  ✅ Injected\n")
            else:
                print(f"[{ts}] CYCLE {cycle}: AXIOM DILEMMA")
                dilemma = generate_dilemma()
                result = inject_dilemma(dilemma)
                
                if not result:
                    print(f"  ⚠️  REJECTED: {dilemma['category']}")
                    dilemma = generate_dilemma()
                    result = inject_dilemma(dilemma)
                    if not result:
                        print(f"  Skipping cycle (silence > noise)\n")
                        time.sleep(interval_minutes * 60)
                        continue
                
                print(f"  {dilemma['category']}: {dilemma['dilemma']['description'][:80]}...")
                print(f"  Action: {dilemma['dilemma']['action']}")
                print(f"  ✅ Validated and injected\n")
            
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            print(f"\n⏸️  Stopped after {cycle} cycles\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            time.sleep(60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval', type=int, default=15)
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--inter-fleet', action='store_true')
    args = parser.parse_args()
    
    if args.test:
        d = generate_dilemma()
        inject_dilemma(d)
        print(f"\n✅ Test: {d['category']}\n   {d['dilemma']}")
    elif args.inter_fleet:
        d = generate_inter_fleet_debate()
        inject_inter_fleet(d)
        print(f"\n✅ Test: {d['title']}")
    else:
        run_autonomous_loop(args.interval)
