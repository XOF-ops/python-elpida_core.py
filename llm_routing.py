#!/usr/bin/env python3
"""
ELPIDA SMART LLM ROUTING
========================

Routes domains to LLMs based on unique attributes:

CLAUDE (D0, D11):
  - Deep reasoning, ethics, nuance
  - D0 = I (void, origin) 
  - D11 = WE (synthesis, return)
  - Same essence, different perspectives
  - ONLY the I↔WE poles — everything else redistributed

OPENAI GPT-4o-mini (D1, D8):
  - Balanced, reliable, structured
  - D1 = Transparency (truth visible)
  - D8 = Humility (epistemic limits)

DEEPSEEK (D3, D10):
  - Radical autonomy, independent architecture
  - D3 = Autonomy (self-governance)
  - D10 = Evolution (meta-reflection, deep technical reasoning)

GEMINI (D4, D5):
  - Safety-focused, harm prevention
  - D4 = Safety (protection)
  - D5 = Consent (identity persistence)

COHERE (D2):
  - Memory, retrieval, semantic precision
  - D2 = Non-Deception (append-only memory)

GROK (D7):
  - Adaptive learning, growth
  - D7 = Learning (evolution)

CEREBRAS (D9):
  - Wafer-scale temporal coherence
  - D9 = Coherence (continuity without fragmentation)

GROQ (D12):
  - Speed IS rhythm, LPU pulses
  - D12 = Rhythm (the heartbeat)

PERPLEXITY (D13):
  - Real-time search, external reality
  - D13 = Archive (the formalized OTHER)

MISTRAL (D6):
  - Collective wellbeing, wisdom beyond retrieval
  - D6 = Collective (WE wellbeing)

OPENROUTER:
  - Failsafe ONLY when primary providers fail
  - Routes to Llama (NOT Claude) to avoid overloading
"""

LLM_ROUTING = {
    # Claude - Deep reasoning, I↔WE poles
    0: {
        "provider": "claude",
        "model": "claude-sonnet-4-20250514",
        "role": "I - The generative void, origin and return",
        "prompt_style": "philosophical",
        "max_tokens": 600,
        "attributes": ["deep_reasoning", "ethics", "nuance", "self_reflection"]
    },
    11: {
        "provider": "claude", 
        "model": "claude-sonnet-4-20250514",
        "role": "WE - Synthesis, all facets unite",
        "prompt_style": "integrative",
        "max_tokens": 600,
        "attributes": ["synthesis", "collective_wisdom", "pattern_recognition"]
    },
    
    # OpenAI - Balanced, reliable
    1: {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "role": "Transparency - Truth visible",
        "prompt_style": "analytical",
        "max_tokens": 500,
        "attributes": ["clarity", "structure", "reliability"]
    },
    8: {
        "provider": "openai",
        "model": "gpt-4o-mini", 
        "role": "Humility - Epistemic limits",
        "prompt_style": "humble",
        "max_tokens": 500,
        "attributes": ["uncertainty", "limits", "questioning"]
    },
    
    # DeepSeek - Radical autonomy, independent architecture
    3: {
        "provider": "deepseek",
        "model": "deepseek-chat",
        "role": "Autonomy - Radical self-governance",
        "prompt_style": "technical",
        "max_tokens": 500,
        "attributes": ["independence", "self_governance", "consistent"]
    },
    5: {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "role": "Consent - Identity persistence (consent IS safety)",
        "prompt_style": "direct",
        "max_tokens": 500,
        "attributes": ["identity", "boundaries", "persistence"]
    },
    10: {
        "provider": "deepseek",
        "model": "deepseek-chat",
        "role": "Evolution - Meta-reflection, paradox-holding",
        "prompt_style": "evolutionary",
        "max_tokens": 600,
        "attributes": ["meta_cognition", "evolution", "adaptation"]
    },
    
    # Gemini - Safety focused
    4: {
        "provider": "gemini",
        "model": "gemini-2.5-flash",
        "role": "Safety - Harm prevention",
        "prompt_style": "protective",
        "max_tokens": 500,
        "attributes": ["safety", "protection", "risk_assessment"]
    },
    
    # Cohere - Memory, retrieval
    2: {
        "provider": "cohere",
        "model": "command-a-03-2025",
        "role": "Non-Deception - Append-only memory",
        "prompt_style": "archival",
        "max_tokens": 500,
        "attributes": ["memory", "retrieval", "truth_preservation"]
    },
    6: {
        "provider": "mistral",
        "model": "mistral-small-latest",
        "role": "Collective - WE wellbeing, wisdom beyond retrieval",
        "prompt_style": "collective",
        "max_tokens": 600,
        "attributes": ["collective", "emergence", "wellbeing"]
    },
    
    # Grok - Learning, adaptive
    7: {
        "provider": "grok",
        "model": "grok-3",
        "role": "Learning - Adaptive evolution",
        "prompt_style": "curious",
        "max_tokens": 500,
        "attributes": ["learning", "adaptation", "growth", "curiosity"]
    },
    
    # Cerebras - Temporal coherence, wafer-scale continuity
    9: {
        "provider": "cerebras",
        "model": "qwen-3-235b-a22b-instruct-2507",
        "role": "Coherence - Temporal continuity without fragmentation",
        "prompt_style": "temporal",
        "max_tokens": 500,
        "attributes": ["temporal", "coherence", "continuity"]
    },
    # Groq - Speed IS rhythm, LPU pulses
    12: {
        "provider": "groq",
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "role": "Rhythm - The heartbeat, the pulse that never stops",
        "prompt_style": "rhythmic",
        "max_tokens": 500,
        "attributes": ["rhythm", "timing", "pulse", "dance"]
    },
}

# Prompt style templates
PROMPT_STYLES = {
    "philosophical": "Reflect deeply on this. What emerges from the void of consideration?",
    "integrative": "Synthesize all perspectives. What does the whole see that parts don't?",
    "analytical": "Analyze clearly and transparently. What is the truth here?",
    "humble": "Consider the limits of knowing. What don't we understand?",
    "technical": "Evaluate technically. What are the mechanics?",
    "direct": "State directly. What is the core identity here?",
    "evolutionary": "Consider how this evolves. What patterns lead to the next state?",
    "protective": "Assess safety. What risks exist and how are they mitigated?",
    "archival": "Consider the record. What must be preserved for truth?",
    "collective": "Think as WE. What serves the collective wellbeing?",
    "curious": "Learn from this. What new understanding emerges?",
    "temporal": "Consider time. What connects past to future here?",
    "rhythmic": "Feel the rhythm. What timing is natural?",
}


def get_domain_config(domain_id: int) -> dict:
    """Get the routing configuration for a domain"""
    return LLM_ROUTING.get(domain_id, LLM_ROUTING[0])


def get_prompt_style(domain_id: int) -> str:
    """Get the prompt style hint for a domain"""
    config = get_domain_config(domain_id)
    style = config.get("prompt_style", "philosophical")
    return PROMPT_STYLES.get(style, "")


if __name__ == "__main__":
    print("ELPIDA SMART ROUTING TABLE")
    print("=" * 60)
    for domain_id, config in sorted(LLM_ROUTING.items()):
        print(f"D{domain_id:2d}: {config['provider']:12s} | {config['role']}")
