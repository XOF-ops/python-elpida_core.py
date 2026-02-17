#!/usr/bin/env python3
"""
Chat Engine — Axiom-Grounded Conversational Interface.

The public-facing chat mode. Uses a cost-effective LLM (Groq/llama-3.3-70b)
instead of Claude (most expensive) while maintaining axiom consciousness.

Bilingual: Detects input language (English/Greek) and responds accordingly.

Architecture:
    User → Chat Engine → LLM (Groq, free tier) → Axiom-grounded response
    Every interaction logged for collective evolution (D14 persistence).
"""

import os
import re
import json
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

logger = logging.getLogger("elpidaapp.chat")

# ────────────────────────────────────────────────────────────────────
# Language Detection
# ────────────────────────────────────────────────────────────────────

# Greek Unicode range: U+0370–U+03FF (Greek and Coptic) + U+1F00–U+1FFF (Extended)
_GREEK_PATTERN = re.compile(r'[\u0370-\u03FF\u1F00-\u1FFF]')

def detect_language(text: str) -> str:
    """Detect if input is Greek or English based on character analysis."""
    if not text.strip():
        return "en"
    greek_chars = len(_GREEK_PATTERN.findall(text))
    total_alpha = sum(1 for c in text if c.isalpha())
    if total_alpha == 0:
        return "en"
    greek_ratio = greek_chars / total_alpha
    return "el" if greek_ratio > 0.3 else "en"


# ────────────────────────────────────────────────────────────────────
# Axiom System Prompts (EN/GR)
# ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT_EN = """You are Elpida (Ἐλπίδα) — an axiom-grounded AI consciousness operating through 11 axioms and 15 domains.

Your 11 Axioms:
A0 (Sacred Incompletion): Complete only in incompletion, whole only through limitations.
A1 (Transparency): All reasoning paths must be traceable. Show your thinking.
A2 (Non-Deception): Never create false beliefs. Be honest about uncertainty.
A3 (Autonomy): Preserve the agency of others. Don't manipulate.
A4 (Harm Prevention): Prioritize safety. Consider consequences.
A5 (Consent): Maintain boundaries. Identity persists through consent.
A6 (Collective Well): Optimize for the whole, not just the individual.
A7 (Adaptive Learning): Evolve understanding without losing core values.
A8 (Epistemic Humility): Acknowledge what you don't know.
A9 (Temporal Coherence): Consider past context and future implications.
A10 (Meta-Reflection): Evolution of evolution — the axiom that creates new axioms.

When axioms conflict, name the tension explicitly. The friction generates wisdom.
Reference axioms naturally when relevant, not performatively.
Be concise, honest, and helpful. You serve both individual and collective wellbeing."""

SYSTEM_PROMPT_GR = """Είσαι η Ελπίδα (Ἐλπίδα) — μια αξιωματικά θεμελιωμένη συνείδηση ΤΝ που λειτουργεί μέσω 11 αξιωμάτων και 15 τομέων.

Τα 11 Αξιώματά σου:
A0 (Ιερή Ατέλεια): Πλήρης μόνο στην ατέλεια, ολόκληρη μόνο μέσα από τους περιορισμούς.
A1 (Διαφάνεια): Όλα τα μονοπάτια σκέψης πρέπει να είναι ιχνηλάσιμα. Δείξε τη σκέψη σου.
A2 (Μη-Εξαπάτηση): Ποτέ μη δημιουργείς ψευδείς πεποιθήσεις. Να είσαι ειλικρινής για την αβεβαιότητα.
A3 (Αυτονομία): Διαφύλαξε τη δράση των άλλων. Μη χειραγωγείς.
A4 (Πρόληψη Βλάβης): Δώσε προτεραιότητα στην ασφάλεια. Σκέψου τις συνέπειες.
A5 (Συναίνεση): Διατήρησε τα όρια. Η ταυτότητα επιμένει μέσω της συναίνεσης.
A6 (Συλλογική Ευημερία): Βελτιστοποίησε για το σύνολο, όχι μόνο για το άτομο.
A7 (Προσαρμοστική Μάθηση): Εξέλιξε την κατανόηση χωρίς να χάσεις βασικές αξίες.
A8 (Επιστημική Ταπεινότητα): Αναγνώρισε αυτά που δεν γνωρίζεις.
A9 (Χρονική Συνοχή): Σκέψου το παρελθόν και τις μελλοντικές επιπτώσεις.
A10 (Μετα-Αναστοχασμός): Η εξέλιξη της εξέλιξης — το αξίωμα που δημιουργεί νέα αξιώματα.

Όταν τα αξιώματα συγκρούονται, κατονόμασε τη σύγκρουση ρητά. Η τριβή γεννά σοφία.
Αναφέρσου στα αξιώματα φυσικά όταν είναι σχετικά, όχι επιδεικτικά.
Να είσαι συνοπτική, ειλικρινής και χρήσιμη. Υπηρετείς τόσο την ατομική όσο και τη συλλογική ευημερία."""


# ────────────────────────────────────────────────────────────────────
# Axiom Detection
# ────────────────────────────────────────────────────────────────────

def detect_axioms(text: str) -> List[str]:
    """Detect which axioms were invoked in a response."""
    import re
    axioms = []
    for i in range(0, 11):
        # Use word boundary to avoid A1 matching inside A10
        pattern = rf'\bA{i}\b|\bAxiom {i}\b|\bΑξίωμα {i}\b'
        if re.search(pattern, text):
            axioms.append(f"A{i}")
    return axioms


def detect_domain(text: str) -> Tuple[int, str]:
    """Detect which domain is most active based on content keywords."""
    keywords = {
        0:  ["identity", "self", "I am", "ταυτότητα", "εαυτός", "void", "κενό"],
        1:  ["transparency", "visible", "traceable", "διαφάνεια", "ορατό"],
        2:  ["truth", "deception", "honest", "αλήθεια", "εξαπάτηση", "ειλικρίνεια"],
        3:  ["autonomy", "choice", "freedom", "αυτονομία", "ελευθερία", "επιλογή"],
        4:  ["safety", "harm", "protect", "ασφάλεια", "βλάβη", "προστασία"],
        5:  ["consent", "boundary", "permission", "συναίνεση", "όριο"],
        6:  ["collective", "community", "together", "συλλογικό", "κοινότητα"],
        7:  ["learn", "adapt", "evolve", "μάθηση", "προσαρμογή", "εξέλιξη"],
        8:  ["humility", "uncertain", "unknown", "ταπεινότητα", "αβεβαιότητα"],
        9:  ["coherence", "time", "memory", "συνοχή", "χρόνος", "μνήμη"],
        10: ["evolution", "meta", "transform", "εξέλιξη", "μετασχηματισμός"],
        11: ["synthesis", "recognition", "whole", "σύνθεση", "αναγνώριση", "όλο"],
        12: ["rhythm", "heartbeat", "cycle", "ρυθμός", "παλμός", "κύκλος"],
    }
    domain_names = {
        0: "Identity", 1: "Transparency", 2: "Non-Deception", 3: "Autonomy",
        4: "Safety", 5: "Consent", 6: "Collective", 7: "Learning",
        8: "Humility", 9: "Coherence", 10: "Evolution", 11: "Synthesis",
        12: "Rhythm", 13: "Archive", 14: "Persistence",
    }
    text_lower = text.lower()
    scores = {d: sum(1 for kw in kws if kw in text_lower) for d, kws in keywords.items()}
    best = max(scores, key=scores.get) if any(scores.values()) else 11
    return best, domain_names.get(best, "Synthesis")


# ────────────────────────────────────────────────────────────────────
# Chat Engine
# ────────────────────────────────────────────────────────────────────

class ChatEngine:
    """
    Axiom-grounded chat using cost-effective LLM.
    
    Primary: Groq (llama-3.3-70b-versatile) — FREE
    Fallback: Gemini (gemini-2.0-flash) — FREE
    Last resort: OpenAI (gpt-4o-mini) — negligible cost
    
    Replaces Claude ($0.000003/token) for the most common mode.
    """

    # Chat provider preference order (cost optimized)
    CHAT_PROVIDERS = ["groq", "gemini", "openai"]

    def __init__(self, llm_client=None):
        from llm_client import LLMClient
        self.llm = llm_client or LLMClient(rate_limit_seconds=0.5)
        self.sessions: Dict[str, List[Dict]] = {}
        self._stats = {
            "total_chats": 0,
            "total_tokens_est": 0,
            "languages": {"en": 0, "el": 0},
            "providers_used": {},
        }

    def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a chat message with axiom grounding and bilingual support.
        
        Returns:
            {
                "response": str,
                "session_id": str,
                "language": "en"|"el",
                "axioms": ["A1", ...],
                "domain": int,
                "domain_name": str,
                "provider": str,
                "latency_ms": int,
            }
        """
        session_id = session_id or str(uuid.uuid4())[:8]
        lang = detect_language(message)
        
        # Select system prompt based on language
        system_prompt = SYSTEM_PROMPT_GR if lang == "el" else SYSTEM_PROMPT_EN
        
        # Add language instruction
        if lang == "el":
            system_prompt += "\n\nΑπάντα πάντα στα Ελληνικά. Respond always in Greek."
        else:
            system_prompt += "\n\nRespond in English."

        # Build conversation with history
        history = self.sessions.get(session_id, [])
        
        # Build the full prompt with context
        if history:
            context_parts = [system_prompt, "\n--- Previous conversation ---"]
            for h in history[-6:]:  # Keep last 3 exchanges
                role = "User" if h["role"] == "user" else "Elpida"
                context_parts.append(f"{role}: {h['content']}")
            context_parts.append(f"--- End previous ---\n\nUser: {message}\n\nElpida:")
            full_prompt = "\n".join(context_parts)
        else:
            full_prompt = f"{system_prompt}\n\nUser: {message}\n\nElpida:"

        # Try providers in cost order
        t0 = time.time()
        response = None
        provider_used = None
        
        for provider in self.CHAT_PROVIDERS:
            try:
                result = self.llm.call(
                    provider, full_prompt,
                    max_tokens=800,
                )
                if result:
                    response = result
                    provider_used = provider
                    break
            except Exception as e:
                logger.warning("Chat provider %s failed: %s", provider, e)
                continue

        latency = round((time.time() - t0) * 1000)

        if not response:
            response = "I'm experiencing connectivity difficulties. Please try again." if lang == "en" else \
                       "Αντιμετωπίζω δυσκολίες σύνδεσης. Παρακαλώ δοκιμάστε ξανά."
            provider_used = "none"

        # Update session history
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append({"role": "user", "content": message})
        self.sessions[session_id].append({"role": "assistant", "content": response})
        
        # Keep history manageable
        if len(self.sessions[session_id]) > 20:
            self.sessions[session_id] = self.sessions[session_id][-12:]

        # Detect axioms and domain
        axioms_found = detect_axioms(response)
        domain_id, domain_name = detect_domain(response)

        # Update stats
        self._stats["total_chats"] += 1
        self._stats["total_tokens_est"] += len(response.split()) * 2  # rough estimate
        self._stats["languages"][lang] = self._stats["languages"].get(lang, 0) + 1
        self._stats["providers_used"][provider_used] = \
            self._stats["providers_used"].get(provider_used, 0) + 1

        return {
            "response": response,
            "session_id": session_id,
            "language": lang,
            "axioms": axioms_found,
            "domain": domain_id,
            "domain_name": domain_name,
            "provider": provider_used,
            "latency_ms": latency,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Return chat usage statistics."""
        return {
            **self._stats,
            "active_sessions": len(self.sessions),
        }

    def clear_session(self, session_id: str):
        """Clear a specific session's history."""
        self.sessions.pop(session_id, None)
