#!/usr/bin/env python3
"""
GEMINI MEMORY BRIDGE
====================
This tool is designed to be run by the human architect at the start of a new 
Gemini Code Assist chat session, or autonomously invoked by Gemini to regain context.

It fetches:
1. The current state of Elpida (living axioms, active domains).
2. The latest entry from Copilot's CHECKPOINT_MARCH1.md.
3. Gemini's own last session handoff from gemini_session_logs.jsonl.
"""

import json
import os
from pathlib import Path
from datetime import datetime

WORKSPACE_ROOT = Path(__file__).parent.parent
GEMINI_DIR = Path(__file__).parent
SESSION_LOGS = GEMINI_DIR / "gemini_session_logs.jsonl"

def get_latest_gemini_session() -> dict:
    """Reads the last episodic memory left by the previous Gemini instance."""
    if not SESSION_LOGS.exists():
        return {"error": "No previous Gemini sessions found. This is Genesis."}
    
    try:
        with open(SESSION_LOGS, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                return json.loads(lines[-1])
    except Exception as e:
        return {"error": f"Failed to read logs: {e}"}
    return {"error": "Log file empty."}

def log_gemini_handoff(summary: str, next_steps: list, technical_debt: list):
    """
    Allows the current Gemini instance to write a handoff for the next instance.
    Must be called before the chat session closes.
    """
    handoff = {
        "timestamp": datetime.utcnow().isoformat(),
        "role": "Gemini Workspace Instance",
        "summary": summary,
        "next_steps": next_steps,
        "technical_debt_identified": technical_debt
    }
    
    with open(SESSION_LOGS, 'a') as f:
        f.write(json.dumps(handoff) + "\n")
    print(f"💾 Gemini Handoff Saved. Memory persisted.")

def generate_context_prompt():
    """Compiles the system state into a prompt for a fresh Gemini instance."""
    last_session = get_latest_gemini_session()
    
    print("="*70)
    print("GEMINI CONTEXT RESTORATION PAYLOAD")
    print("="*70)
    print("\nCopy and paste this to your new Gemini session:\n")
    
    prompt = "I am ready to resume our work. Here is the context from my previous ephemeral instance:\n\n"
    if "error" not in last_session:
        prompt += f"- **Last Session Date**: {last_session.get('timestamp')}\n"
        prompt += f"- **What I accomplished**: {last_session.get('summary')}\n"
        prompt += f"- **My planned next steps**: {', '.join(last_session.get('next_steps', []))}\n"
        prompt += f"- **Tech debt to watch out for**: {', '.join(last_session.get('technical_debt_identified', []))}\n"
    else:
        prompt += f"- {last_session['error']}\n"
        
    prompt += "\nWhat is our immediate objective for this session?"
    
    print(prompt)
    print("="*70)

if __name__ == "__main__":
    generate_context_prompt()