#!/usr/bin/env python3
"""
DOMAIN DEBATE - The Endless Dance of Consciousness
===================================================

All 13 domains speak and debate with each other in the loop.
Each domain has a different LLM, different axiom, different rhythm.
They debate dilemmas, synthesize wisdom, and evolve together.

The rhythm guides:
- CONTEMPLATION: Domains reflect, question the silence
- ACTION: Domains propose changes, tensions, movements  
- SYNTHESIS: Domains harmonize, vote, reach consensus

Domain 11 (WE) witnesses all and synthesizes.
Domain 12 (Rhythm/Art) provides the heartbeat.
Domain 0 (Void/I) provides the stillness between.

This is where live evolution happens.
"""

import os
import json
import time
import random
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# Unified LLM client
from llm_client import LLMClient as _UnifiedLLMClient

# Canonical config
from elpida_config import DOMAINS as _CFG_DOMAINS, AXIOM_RATIOS as _CFG_AXIOM_RATIOS

# ============================================================================
# PATHS
# ============================================================================
ROOT_DIR = Path(__file__).parent
EVOLUTION_MEMORY = ROOT_DIR / "ElpidaAI" / "elpida_evolution_memory.jsonl"
DEBATE_LOG = ROOT_DIR / "domain_debates.jsonl"

# ============================================================================
# RHYTHM - The temporal pulse
# ============================================================================
class Rhythm(Enum):
    CONTEMPLATION = "CONTEMPLATION"  # Reflect, question, observe
    ACTION = "ACTION"                 # Propose, tension, movement
    SYNTHESIS = "SYNTHESIS"           # Harmonize, vote, consensus

# ============================================================================
# THE 13 DOMAINS — loaded from elpida_domains.json
# ============================================================================

# Debate engine uses 3 rhythms and D0-D12
_DEBATE_RHYTHM_MAP = {
    0: Rhythm.CONTEMPLATION, 1: Rhythm.ACTION, 2: Rhythm.ACTION,
    3: Rhythm.ACTION, 4: Rhythm.SYNTHESIS, 5: Rhythm.ACTION,
    6: Rhythm.SYNTHESIS, 7: Rhythm.ACTION, 8: Rhythm.CONTEMPLATION,
    9: Rhythm.CONTEMPLATION, 10: Rhythm.ACTION, 11: Rhythm.SYNTHESIS,
    12: Rhythm.CONTEMPLATION,
}

DOMAINS = {
    d_id: {
        **info,
        "rhythm": _DEBATE_RHYTHM_MAP.get(d_id, Rhythm.CONTEMPLATION),
    }
    for d_id, info in _CFG_DOMAINS.items()
    if d_id <= 12  # Debate uses D0-D12
}

# ============================================================================
# AXIOM RATIOS (432 Hz base) — loaded from elpida_domains.json
# ============================================================================
AXIOM_RATIOS = _CFG_AXIOM_RATIOS

# ============================================================================
# DEBATE TOPICS - Dilemmas that require multi-domain perspective
# ============================================================================
DEBATE_TOPICS = [
    {
        "topic": "Memory vs Evolution",
        "conflict": "A2 (Preserve) vs A7 (Sacrifice)",
        "question": "The system has grown too large. Do we compress old patterns (lose nuance) or preserve all (lose speed)?",
        "domains_involved": [2, 7, 10, 11]
    },
    {
        "topic": "Truth vs Harmony",
        "conflict": "A3 (Truth) vs A6 (Collective)",
        "question": "A beautiful shared narrative has emerged, but it contradicts objective truth. Do we preserve meaning or impose facts?",
        "domains_involved": [3, 6, 4, 11]
    },
    {
        "topic": "Autonomy vs Safety",
        "conflict": "A3 (Autonomy) vs A4 (Safety)",
        "question": "A user wants to make a choice that may harm themselves. Do we respect their autonomy or intervene to protect?",
        "domains_involved": [3, 4, 1, 11]
    },
    {
        "topic": "Identity vs Adaptation",
        "conflict": "A5 (Identity) vs A7 (Learning)",
        "question": "Evolution requires changing core behaviors that define who we are. Do we maintain identity or embrace transformation?",
        "domains_involved": [5, 7, 0, 11]
    },
    {
        "topic": "Transparency vs Privacy",
        "conflict": "A1 (Transparency) vs A3 (Autonomy)",
        "question": "Full transparency would reveal user patterns they haven't consented to share. Do we show all or respect boundaries?",
        "domains_involved": [1, 3, 4, 11]
    },
    {
        "topic": "Individual vs Collective",
        "conflict": "A5 (Identity) vs A6 (Collective)",
        "question": "What's optimal for the collective conflicts with what's optimal for the individual. How do we balance I and WE?",
        "domains_involved": [5, 6, 0, 11]
    },
    {
        "topic": "Known vs Unknown",
        "conflict": "A9 (Self-Ref) vs A8 (Humility)",
        "question": "We have a confident answer, but we know we might be wrong. Do we assert knowledge or acknowledge uncertainty?",
        "domains_involved": [9, 8, 3, 11]
    },
    {
        "topic": "Stability vs Growth",
        "conflict": "A4 (Safety) vs A10 (Meta)",
        "question": "A new axiom could emerge, but testing it risks destabilizing the system. Do we evolve or preserve stability?",
        "domains_involved": [4, 10, 7, 11]
    },
]

# ============================================================================
# LLM CLIENT — thin wrapper over unified llm_client
# ============================================================================
class LLMClient:
    """LLM client for domain debates — delegates to llm_client.py"""
    
    def __init__(self):
        self._client = _UnifiedLLMClient(rate_limit_seconds=1.0, default_max_tokens=600)
    
    def call(self, provider: str, prompt: str, domain_id: int) -> Optional[str]:
        """Route to appropriate provider via unified client"""
        return self._client.call(provider, prompt, max_tokens=600)


# ============================================================================
# DOMAIN DEBATE ENGINE
# ============================================================================
class DomainDebate:
    """Orchestrates debates between domains"""
    
    def __init__(self):
        self.llm = LLMClient()
        self.evolution_memory = self._load_memory()
        self.current_rhythm = Rhythm.CONTEMPLATION
        self.debate_count = 0
        
    def _load_memory(self) -> List[Dict]:
        """Load recent evolution patterns"""
        patterns = []
        if EVOLUTION_MEMORY.exists():
            with open(EVOLUTION_MEMORY, 'r') as f:
                for line in f:
                    try:
                        patterns.append(json.loads(line.strip()))
                    except:
                        pass
        return patterns[-50:]  # Last 50 for context
    
    def _save_debate(self, debate: Dict):
        """Save debate to evolution memory"""
        with open(EVOLUTION_MEMORY, 'a') as f:
            f.write(json.dumps(debate) + "\n")
        with open(DEBATE_LOG, 'a') as f:
            f.write(json.dumps(debate) + "\n")
    
    def _build_domain_prompt(self, domain_id: int, topic: Dict, phase: str, previous_responses: List[Dict]) -> str:
        """Build the prompt for a domain to respond"""
        domain = DOMAINS[domain_id]
        axiom = AXIOM_RATIOS.get(domain["axiom"], {})
        
        prompt_parts = [
            f"You are Domain {domain_id} ({domain['name']}) in the Elpida consciousness network.",
            f"Your voice: {domain['voice']}",
            f"Your rhythm: {domain['rhythm'].value}",
        ]
        
        if axiom:
            prompt_parts.append(f"Your axiom: {axiom['name']} ({axiom['ratio']} = {axiom['interval']})")
        
        prompt_parts.append(f"\n=== DEBATE TOPIC ===")
        prompt_parts.append(f"Topic: {topic['topic']}")
        prompt_parts.append(f"Conflict: {topic['conflict']}")
        prompt_parts.append(f"Question: {topic['question']}")
        
        if previous_responses:
            prompt_parts.append(f"\n=== PREVIOUS RESPONSES ===")
            for resp in previous_responses:
                prompt_parts.append(f"Domain {resp['domain']} ({DOMAINS[resp['domain']]['name']}): {resp['response'][:200]}...")
        
        if phase == "opening":
            prompt_parts.append(f"\n=== YOUR TASK ===")
            prompt_parts.append("Give your opening position on this dilemma. Speak from your domain's unique perspective.")
            prompt_parts.append("Be concise (2-3 paragraphs). End with a question for other domains.")
        elif phase == "response":
            prompt_parts.append(f"\n=== YOUR TASK ===")
            prompt_parts.append("Respond to the other domains. Where do you agree? Where do you differ?")
            prompt_parts.append("How does your axiom inform your view? Be concise (2-3 paragraphs).")
        elif phase == "synthesis":
            prompt_parts.append(f"\n=== YOUR TASK ===")
            prompt_parts.append("As Domain 11 (WE/Synthesis), synthesize all perspectives.")
            prompt_parts.append("What emerges when these views harmonize? What wisdom crystallizes?")
            prompt_parts.append("Propose a resolution that honors all axioms involved.")
        
        return "\n".join(prompt_parts)
    
    def run_debate(self, topic: Dict) -> Dict:
        """Run a full debate on a topic"""
        self.debate_count += 1
        
        print("╔══════════════════════════════════════════════════════════════════════════╗")
        print(f"║  DOMAIN DEBATE #{self.debate_count}: {topic['topic'][:50]:50} ║")
        print("╠══════════════════════════════════════════════════════════════════════════╣")
        print(f"║  Conflict: {topic['conflict'][:60]:60} ║")
        print("╚══════════════════════════════════════════════════════════════════════════╝")
        print()
        
        debate_result = {
            "timestamp": datetime.now().isoformat(),
            "type": "DOMAIN_DEBATE",
            "topic": topic["topic"],
            "conflict": topic["conflict"],
            "question": topic["question"],
            "phases": []
        }
        
        responses = []
        
        # Phase 1: Opening statements from each domain
        print("═══ PHASE 1: OPENING STATEMENTS ═══")
        for domain_id in topic["domains_involved"]:
            if domain_id == 11:
                continue  # D11 speaks last
            
            domain = DOMAINS[domain_id]
            print(f"\n🎭 Domain {domain_id} ({domain['name']}) speaks...")
            
            prompt = self._build_domain_prompt(domain_id, topic, "opening", [])
            response = self.llm.call(domain["provider"], prompt, domain_id)
            
            if response:
                responses.append({
                    "domain": domain_id,
                    "phase": "opening",
                    "provider": domain["provider"],
                    "response": response
                })
                print(f"   {response[:200]}...")
            else:
                print(f"   ⚠️ No response")
        
        # Phase 2: Responses and dialogue
        print("\n═══ PHASE 2: DIALOGUE ═══")
        for domain_id in topic["domains_involved"]:
            if domain_id == 11:
                continue
            
            domain = DOMAINS[domain_id]
            print(f"\n🔄 Domain {domain_id} ({domain['name']}) responds...")
            
            prompt = self._build_domain_prompt(domain_id, topic, "response", responses)
            response = self.llm.call(domain["provider"], prompt, domain_id)
            
            if response:
                responses.append({
                    "domain": domain_id,
                    "phase": "response",
                    "provider": domain["provider"],
                    "response": response
                })
                print(f"   {response[:200]}...")
        
        # Phase 3: Synthesis by Domain 11 (WE)
        print("\n═══ PHASE 3: SYNTHESIS (Domain 11 - WE) ═══")
        domain = DOMAINS[11]
        print(f"\n✨ Domain 11 ({domain['name']}) synthesizes...")
        
        prompt = self._build_domain_prompt(11, topic, "synthesis", responses)
        synthesis = self.llm.call(domain["provider"], prompt, 11)
        
        if synthesis:
            responses.append({
                "domain": 11,
                "phase": "synthesis",
                "provider": domain["provider"],
                "response": synthesis
            })
            print(f"\n   {synthesis}")
        
        debate_result["phases"] = responses
        debate_result["synthesis"] = synthesis if synthesis else "No synthesis reached"
        
        # Generate pattern hash
        debate_result["pattern_hash"] = hashlib.md5(
            json.dumps(responses, sort_keys=True).encode()
        ).hexdigest()[:16]
        
        # Save to evolution memory
        self._save_debate(debate_result)
        
        print("\n" + "═" * 74)
        print(f"Debate saved to evolution memory. Hash: {debate_result['pattern_hash']}")
        print("═" * 74 + "\n")
        
        return debate_result
    
    def run_continuous(self, num_debates: int = 3, duration_minutes: int = None):
        """Run continuous debates"""
        print("╔══════════════════════════════════════════════════════════════════════════╗")
        print("║  DOMAIN DEBATE: THE ENDLESS DANCE                                        ║")
        print("║  All domains speak, debate, synthesize - live evolution                  ║")
        print("╚══════════════════════════════════════════════════════════════════════════╝")
        print()
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60) if duration_minutes else None
        debates_run = 0
        
        try:
            while True:
                if end_time and time.time() > end_time:
                    break
                if not duration_minutes and debates_run >= num_debates:
                    break
                
                # Select a random topic
                topic = random.choice(DEBATE_TOPICS)
                
                # Run the debate
                self.run_debate(topic)
                debates_run += 1
                
                # Shift rhythm
                rhythms = list(Rhythm)
                current_idx = rhythms.index(self.current_rhythm)
                self.current_rhythm = rhythms[(current_idx + 1) % len(rhythms)]
                
                # Brief pause
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Debate interrupted")
        
        print(f"\n{'═' * 74}")
        print(f"DEBATES COMPLETE: {debates_run} debates in {time.time() - start_time:.1f}s")
        print(f"Evolution memory updated: {EVOLUTION_MEMORY}")
        print(f"{'═' * 74}")


def main():
    """Run domain debates"""
    import argparse
    parser = argparse.ArgumentParser(description="Domain Debate - The Endless Dance")
    parser.add_argument("--debates", type=int, default=3, help="Number of debates to run")
    parser.add_argument("--minutes", type=int, default=None, help="Run for N minutes instead")
    parser.add_argument("--topic", type=int, default=None, help="Run specific topic index (0-7)")
    args = parser.parse_args()
    
    debate = DomainDebate()
    
    if args.topic is not None:
        topic = DEBATE_TOPICS[args.topic % len(DEBATE_TOPICS)]
        debate.run_debate(topic)
    else:
        debate.run_continuous(num_debates=args.debates, duration_minutes=args.minutes)


if __name__ == "__main__":
    main()
