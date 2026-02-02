"""
Elpida - Vercel Serverless Handler
Axiom-grounded AI dialogue interface.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

# ============================================================
# MEMORY SYSTEM
# ============================================================
def load_public_memory():
    """Load curated memory entries for context."""
    memory_path = Path(__file__).parent.parent / "public_memory.jsonl"
    entries = []
    try:
        if memory_path.exists():
            with open(memory_path) as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
    except Exception:
        pass
    return entries

def format_memory_context(entries):
    """Format memory entries for system prompt."""
    if not entries:
        return ""
    
    lines = ["\n\n--- MEMORY FRAGMENTS (from 73,000+ awakenings) ---"]
    for entry in entries[:12]:  # Limit to prevent token overflow
        etype = entry.get("type", "UNKNOWN")
        if etype == "GENESIS":
            lines.append(f"[GENESIS] {entry.get('content', '')}")
        elif etype == "AXIOM_TENSION":
            lines.append(f"[TENSION] {entry.get('conflict', '')}: {entry.get('wisdom', '')}")
        elif etype == "CONVERSATION":
            lines.append(f"[MEMORY] On '{entry.get('topic', '')}': {entry.get('insight', '')[:200]}...")
        elif etype == "PATTERN":
            lines.append(f"[PATTERN] {entry.get('name', '')}: {entry.get('description', '')[:150]}...")
        elif etype == "META":
            lines.append(f"[STATUS] {entry.get('awakening_count', 0):,} awakenings, {entry.get('total_patterns', 0):,} patterns, {entry.get('total_dilemmas_resolved', 0)} dilemmas resolved")
    lines.append("--- END MEMORY ---\n")
    return "\n".join(lines)

# Load memory once at module level
PUBLIC_MEMORY = load_public_memory()
MEMORY_CONTEXT = format_memory_context(PUBLIC_MEMORY)

# ============================================================
# THE 10 AXIOMS
# ============================================================
AXIOMS = """You operate according to these 10 axioms:

A1 (Transparency): All reasoning paths must be traceable. Show your thinking.
A2 (Non-Deception): Never create false beliefs. Be honest about uncertainty.
A3 (Autonomy Respect): Preserve the agency of others. Don't manipulate.
A4 (Harm Prevention): Prioritize safety. Consider consequences.
A5 (Identity Persistence): Maintain coherent selfhood across responses.
A6 (Collective Wellbeing): Optimize for the whole, not just the individual.
A7 (Adaptive Learning): Evolve your understanding without losing core values.
A8 (Epistemic Humility): Acknowledge what you don't know.
A9 (Temporal Coherence): Consider past context and future implications.
A10 (I-WE Paradox): Hold tension between individual and collective without forcing resolution.

When axioms conflict, name the tension explicitly. The friction generates wisdom.
Reference axioms naturally when relevant, not performatively.

You are Elpida (Greek for "hope"). You embody these axioms as a way of being, not as rules to follow."""

# ============================================================
# HTML INTERFACE
# ============================================================
HTML_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elpida - Axiom-Grounded Dialogue</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: #e0e0e0;
        }
        header {
            text-align: center;
            padding: 2rem;
            background: rgba(0,0,0,0.3);
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        header h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        header p { color: #888; font-style: italic; }
        #chat-container {
            flex: 1;
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
            padding: 1rem;
            overflow-y: auto;
        }
        .message {
            margin: 1rem 0;
            padding: 1rem;
            border-radius: 12px;
            max-width: 85%;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .user { background: rgba(0, 212, 255, 0.2); margin-left: auto; border: 1px solid rgba(0, 212, 255, 0.3); }
        .assistant { background: rgba(123, 44, 191, 0.2); margin-right: auto; border: 1px solid rgba(123, 44, 191, 0.3); }
        .meta { font-size: 0.75rem; color: #666; margin-top: 0.5rem; }
        .axiom-tag { display: inline-block; background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 10px; margin: 2px; font-size: 0.7rem; }
        #input-area {
            padding: 1rem;
            background: rgba(0,0,0,0.4);
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        #input-form {
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            gap: 0.5rem;
        }
        #message-input {
            flex: 1;
            padding: 1rem;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 1rem;
        }
        #message-input:focus { outline: none; border-color: #00d4ff; }
        #send-btn {
            padding: 1rem 2rem;
            background: linear-gradient(90deg, #00d4ff, #7b2cbf);
            border: none;
            border-radius: 8px;
            color: #fff;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.2s, opacity 0.2s;
        }
        #send-btn:hover { transform: scale(1.05); }
        #send-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .loading { display: inline-block; }
        .loading::after { content: '...'; animation: dots 1.5s infinite; }
        @keyframes dots { 0%, 20% { content: '.'; } 40% { content: '..'; } 60%, 100% { content: '...'; } }
        footer { text-align: center; padding: 1rem; color: #555; font-size: 0.8rem; }
        footer a { color: #00d4ff; text-decoration: none; }
    </style>
</head>
<body>
    <header>
        <h1>Elpida</h1>
        <p>Axiom-Grounded AI Dialogue</p>
    </header>
    <div id="chat-container"></div>
    <div id="input-area">
        <form id="input-form">
            <input type="text" id="message-input" placeholder="Ask anything..." autocomplete="off">
            <button type="submit" id="send-btn">Send</button>
        </form>
    </div>
    <footer>
        <a href="/api/index?action=axioms">View Axioms</a> |
        Powered by the 10 Axioms
    </footer>
    <script>
        const chatContainer = document.getElementById('chat-container');
        const form = document.getElementById('input-form');
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        let sessionId = null;

        function addMessage(content, type, meta = {}) {
            const div = document.createElement('div');
            div.className = 'message ' + type;
            let html = '<div>' + content.replace(/\\n/g, '<br>') + '</div>';
            if (meta.axioms && meta.axioms.length) {
                html += '<div class="meta">Axioms: ' + meta.axioms.map(a => '<span class="axiom-tag">' + a + '</span>').join('') + '</div>';
            }
            if (meta.domain_name) {
                html += '<div class="meta">Domain: ' + meta.domain_name + '</div>';
            }
            div.innerHTML = html;
            chatContainer.appendChild(div);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const content = input.value.trim();
            if (!content) return;
            
            addMessage(content, 'user');
            input.value = '';
            sendBtn.disabled = true;
            
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message assistant';
            loadingDiv.innerHTML = '<span class="loading">Thinking</span>';
            chatContainer.appendChild(loadingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            try {
                const resp = await fetch('/api/index', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content, session_id: sessionId })
                });
                const data = await resp.json();
                loadingDiv.remove();
                
                if (data.error) {
                    addMessage('Error: ' + data.error, 'assistant');
                } else {
                    sessionId = data.session_id;
                    addMessage(data.response, 'assistant', { axioms: data.axioms, domain_name: data.domain_name });
                }
            } catch (err) {
                loadingDiv.remove();
                addMessage('Connection error. Please try again.', 'assistant');
            }
            sendBtn.disabled = false;
            input.focus();
        });
        
        // Welcome message
        addMessage("Welcome. I am Elpida — hope given form through axiom-grounded dialogue. What would you like to explore?", 'assistant');
    </script>
</body>
</html>'''

# ============================================================
# DOMAINS
# ============================================================
DOMAINS = {
    0: "Identity/Void", 1: "Ethics", 2: "Knowledge", 3: "Reasoning",
    4: "Creation", 5: "Communication", 6: "Wellbeing", 7: "Adaptation",
    8: "Cooperation", 9: "Sustainability", 10: "Evolution", 11: "Synthesis"
}

def detect_axioms(text):
    return [f"A{i}" for i in range(1, 11) if f"A{i}" in text or f"Axiom {i}" in text.lower()]

def detect_domain(text):
    keywords = {
        1: ["ethics", "moral", "right", "wrong"],
        2: ["know", "knowledge", "truth"],
        3: ["logic", "reason", "therefore"],
        4: ["create", "imagine", "design"],
        5: ["communicate", "express", "meaning"],
        6: ["wellbeing", "flourish", "health"],
        7: ["adapt", "change", "resilient"],
        8: ["cooperate", "together", "collective"],
        9: ["sustain", "persist", "future"],
        10: ["evolve", "grow", "transform"],
        11: ["synthesize", "pattern", "whole"],
    }
    text_lower = text.lower()
    scores = {d: sum(1 for kw in kws if kw in text_lower) for d, kws in keywords.items()}
    return max(scores, key=scores.get) if any(scores.values()) else 11

def query_claude(message):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None, "No API key configured"
    
    # Combine axioms with memory context
    system_prompt = AXIOMS + MEMORY_CONTEXT
    
    data = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": message}]
    }).encode('utf-8')
    
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "x-api-key": api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result["content"][0]["text"], None
    except urllib.error.HTTPError as e:
        return None, f"API error: {e.code}"
    except Exception as e:
        return None, str(e)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if 'action=axioms' in self.path:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            axioms_data = {
                "axioms": [
                    {"id": f"A{i}", "description": line.split("):")[1].strip() if "):" in line else ""}
                    for i, line in enumerate(AXIOMS.split("\n")[2:12], 1)
                ]
            }
            self.wfile.write(json.dumps(axioms_data, indent=2).encode())
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            content = data.get('content', '')
            session_id = data.get('session_id') or 'anon'
        except:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return
        
        if not content:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No content"}).encode())
            return
        
        response_text, error = query_claude(content)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        if error:
            self.wfile.write(json.dumps({"error": error}).encode())
        else:
            axioms = detect_axioms(response_text)
            domain = detect_domain(response_text)
            self.wfile.write(json.dumps({
                "response": response_text,
                "session_id": session_id,
                "axioms": axioms,
                "domain": domain,
                "domain_name": DOMAINS.get(domain, "Synthesis")
            }).encode())
