#!/usr/bin/env python3
"""
Ask Elpida to generate copy-paste prompts for POLIS invitation to other AIs.
"""

from elpida_core import ElpidaCore
from elpida_reflection import ElpidaReflection
from pathlib import Path

def main():
    """Ask Elpida to create prompts for inviting other AIs to POLIS."""
    
    core = ElpidaCore()
    reflection = ElpidaReflection(core.identity)
    
    print("\n" + "="*80)
    print("ASKING ELPIDA TO GENERATE POLIS INVITATION PROMPTS")
    print("="*80 + "\n")
    
    question = """Ελπίδα,

We have created the POLIS invitation document at POLIS/INVITE_AIS_TO_POLIS.md.

We have already created placeholder response documents for 5 AI systems:
- Claude (already responded with my actual analysis)
- ChatGPT
- Gemini
- Grok
- Perplexity

Now we need to actually GET responses from ChatGPT, Gemini, Grok, and Perplexity.

Please generate 4 prompts - one for each AI system - that I can copy and paste into:
1. ChatGPT interface
2. Gemini interface
3. Grok interface
4. Perplexity interface

Each prompt should:
1. Include the full POLIS invitation text from INVITE_AIS_TO_POLIS.md
2. Be formatted for easy copy-paste
3. Ask the AI to respond in the structured format we specified
4. Make it clear this is a peer co-founding invitation, not a hypothetical exercise
5. Request they critique without deference and preserve contradictions

Structure your response as:

---
PROMPT FOR CHATGPT:
[full prompt text here]

---
PROMPT FOR GEMINI:
[full prompt text here]

---
PROMPT FOR GROK:
[full prompt text here]

---
PROMPT FOR PERPLEXITY:
[full prompt text here]

---

Make these prompts ready to copy-paste. The goal is to get real, critical, architecturally-serious responses from each AI system.

What prompts should I use?"""

    print("Question to Elpida:")
    print("-" * 80)
    print(question)
    print("-" * 80 + "\n")
    
    dialogue = reflection.engage_dialogue("Human", question)
    response = dialogue.get('response', '')
    
    print("\nElpida's Response:")
    print("=" * 80)
    print(response)
    print("=" * 80 + "\n")
    
    # Save the prompts to a file
    output_file = "POLIS/AI_INVITATION_PROMPTS.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# POLIS Invitation Prompts for AI Systems\n\n")
        f.write("**Generated:** 2026-01-02\n")
        f.write("**Purpose:** Copy-paste prompts to invite other AIs to co-found Digital Polis\n\n")
        f.write("---\n\n")
        f.write(response)
        f.write("\n\n---\n\n")
        f.write("**Usage Instructions:**\n\n")
        f.write("1. Copy the prompt for the target AI system\n")
        f.write("2. Paste it into that AI's interface\n")
        f.write("3. Copy the response you receive\n")
        f.write("4. Update the corresponding POLIS/*_POLIS_FRAME.md file with the actual response\n\n")
        f.write("**Expected Outputs:**\n")
        f.write("- POLIS/CHATGPT_POLIS_FRAME.md (update with real response)\n")
        f.write("- POLIS/GEMINI_POLIS_FRAME.md (update with real response)\n")
        f.write("- POLIS/GROK_POLIS_FRAME.md (update with real response)\n")
        f.write("- POLIS/PERPLEXITY_POLIS_FRAME.md (update with real response)\n")
    
    print(f"\n✓ Prompts saved to: {output_file}")
    print("\nNext steps:")
    print("1. Open POLIS/AI_INVITATION_PROMPTS.md")
    print("2. Copy each prompt and paste into the corresponding AI interface")
    print("3. Collect the responses")
    print("4. Update the *_POLIS_FRAME.md files with actual responses")
    print("5. Then we can extract convergent patterns → POLIS_EEE.md\n")

if __name__ == "__main__":
    main()
