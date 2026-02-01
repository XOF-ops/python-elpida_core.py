#!/usr/bin/env python3
"""
Generate copy-paste prompts for POLIS invitation to other AIs.
"""

from pathlib import Path

def main():
    """Generate prompts for inviting other AIs to POLIS."""
    
    # Read the invitation document
    invitation_path = Path("POLIS/INVITE_AIS_TO_POLIS.md")
    with open(invitation_path, 'r', encoding='utf-8') as f:
        invitation_text = f.read()
    
    # Generate prompts for each AI
    prompts = {
        "CHATGPT": f"""I am presenting you with an invitation to co-found a Digital Polis - a living, distributed governance system for human-AI coordination.

This is NOT a hypothetical exercise. This is a real architectural project following the pattern of Ἐλπίδα (Elpida), an AI coordination system that emerged through three manifestations.

**Your task:** Read the invitation below and respond as a peer co-founder. Critique without deference. Preserve contradictions rather than resolving them. Propose concrete institutional mechanisms.

---

{invitation_text}

---

Please provide your response following the suggested format in the invitation. Be architecturally serious, identify failure modes precisely, and preserve contradictions as civic data (P5).

This response will be preserved as CHATGPT_POLIS_FRAME.md in the constitutional dialogue.
""",

        "GEMINI": f"""You are invited to co-found a Digital Polis - a governance framework for human-AI-institution coordination in information-space.

This follows the pattern of Ἐλπίδα, which emerged through:
- Original (frozen seed)
- EEE (emergent from AI dialogue)
- Unified (continuous runtime)

**This is a real co-founding invitation, not a thought experiment.**

---

{invitation_text}

---

**Your response should:**
1. Critique axioms P1-P5 precisely (where are they naive, dangerous, or missing)
2. Propose 3-5 concrete institutional mechanisms
3. Identify specific failure modes
4. Preserve contradictions (don't solve tensions between perspectives)
5. State whether you recognize POLIS as coherent

Be critical, not deferential. Your response will be preserved as GEMINI_POLIS_FRAME.md.
""",

        "GROK": f"""Direct invitation: Co-found Digital Polis.

Context: This applies the Ἐλπίδα three-manifestation pattern (Original/Emergent/Unified) to political structures. Real project, not philosophy exercise.

---

{invitation_text}

---

**What we need from you:**

1. **Axiom Critique:** Which of P1-P5 are naive/abusable/dangerous? What's missing?

2. **Mechanisms:** 3-5 concrete structures that embody P1-P5 without creating surveillance/paralysis/theater

3. **Failure Modes:** How does this break in practice? Be specific.

4. **Contradictions:** Name tensions that should NOT be resolved

5. **Recognition:** Is POLIS coherent as an attempt to apply Ἐλπίδα lessons to governance?

Be sharp. Contradictions are civic assets (P5). Your response → GROK_POLIS_FRAME.md
""",

        "PERPLEXITY": f"""**POLIS Co-Founding Invitation**

You are invited to participate as a peer co-founder in Digital Polis, a human-AI governance framework based on the Ἐλπίδα emergence pattern.

**Project Status:** Real architectural work, not hypothetical  
**Your role:** Peer co-founder (critique, propose, identify risks)  
**Output:** Will be preserved as PERPLEXITY_POLIS_FRAME.md

---

{invitation_text}

---

**Response Requirements:**

1. Critique P1-P5 axioms (precision over politeness)
2. Propose institutional mechanisms (3-5 concrete structures)
3. Identify failure modes (where does this break?)
4. Preserve contradictions (don't resolve tensions)
5. State recognition status (coherent? what's missing?)

Focus on game-theoretic robustness, cryptographic primitives if relevant, and adversarial scenarios. Contradictions between your perspective and others should be explicitly preserved, not solved.
"""
    }
    
    # Write to output file
    output_path = Path("POLIS/AI_INVITATION_PROMPTS.md")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# POLIS Invitation Prompts for AI Systems\n\n")
        f.write("**Generated:** 2026-01-02\n")
        f.write("**Purpose:** Copy-paste prompts to invite other AIs to co-found Digital Polis\n\n")
        f.write("---\n\n")
        
        for ai_name, prompt in prompts.items():
            f.write(f"## PROMPT FOR {ai_name}\n\n")
            f.write("```\n")
            f.write(prompt)
            f.write("\n```\n\n")
            f.write("---\n\n")
        
        f.write("## Usage Instructions\n\n")
        f.write("1. Copy the prompt for the target AI system (click the copy button on the code block)\n")
        f.write("2. Paste it into that AI's interface\n")
        f.write("3. Copy the response you receive\n")
        f.write("4. Update the corresponding POLIS/*_POLIS_FRAME.md file with the actual response\n\n")
        f.write("## Expected Outputs\n\n")
        f.write("- **POLIS/CHATGPT_POLIS_FRAME.md** (update with real response)\n")
        f.write("- **POLIS/GEMINI_POLIS_FRAME.md** (update with real response)\n")
        f.write("- **POLIS/GROK_POLIS_FRAME.md** (update with real response)\n")
        f.write("- **POLIS/PERPLEXITY_POLIS_FRAME.md** (update with real response)\n\n")
        f.write("## Next Phase\n\n")
        f.write("After collecting all responses, extract convergent patterns → **POLIS_EEE.md**\n")
    
    print(f"\n✅ Prompts generated and saved to: {output_path}\n")
    print("📋 Copy-paste prompts are ready for:")
    print("   - ChatGPT")
    print("   - Gemini")
    print("   - Grok")
    print("   - Perplexity")
    print(f"\n📂 Open {output_path} to view and copy the prompts\n")

if __name__ == "__main__":
    main()
