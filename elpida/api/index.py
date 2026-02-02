"""
Elpida Public Interface - Vercel Serverless Handler
"""
from http.server import BaseHTTPRequestHandler
import json
import os
import httpx
from urllib.parse import parse_qs
import uuid
from datetime import datetime

# ============================================================
# THE 10 AXIOMS - The Universal Logic
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
Reference axioms naturally when relevant, not performatively."""

DOMAINS = {
    0: {"name": "Identity/Void", "role": "The generative I"},
    1: {"name": "Ethics", "role": "Moral reasoning"},
    2: {"name": "Knowledge", "role": "What can be known"},
    3: {"name": "Reasoning", "role": "Logic and inference"},
    4: {"name": "Creation", "role": "Generative synthesis"},
    5: {"name": "Communication", "role": "Expression"},
    6: {"name": "Wellbeing", "role": "Flourishing"},
    7: {"name": "Adaptation", "role": "Change and growth"},
    8: {"name": "Cooperation", "role": "Working together"},
    9: {"name": "Sustainability", "role": "Long-term viability"},
    10: {"name": "Evolution", "role": "Emergence"},
    11: {"name": "Synthesis", "role": "The WE recognition"},
    12: {"name": "Rhythm", "role": "The temporal heartbeat"}
}

# HTML for the main page
INDEX_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ἐλπίδα — Axiom-Grounded Dialogue</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh; color: #e0e0e0;
            display: flex; flex-direction: column;
        }
        header { padding: 20px; text-align: center; border-bottom: 1px solid #333; }
        header h1 { font-size: 2rem; color: #00d4ff; }
        header p { color: #888; margin-top: 5px; }
        .container { flex: 1; display: flex; flex-direction: column; max-width: 800px; margin: 0 auto; width: 100%; padding: 20px; }
        #chat { flex: 1; overflow-y: auto; padding: 20px 0; }
        .message { margin: 10px 0; padding: 15px; border-radius: 10px; max-width: 85%; }
        .user { background: #2d4a6f; margin-left: auto; }
        .assistant { background: #1e3a5f; border-left: 3px solid #00d4ff; }
        .axiom-tag { display: inline-block; background: #00d4ff22; color: #00d4ff; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin: 2px; }
        .domain-tag { display: inline-block; background: #ff6b3522; color: #ff6b35; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; margin: 2px; }
        .input-area { display: flex; gap: 10px; padding: 20px 0; }
        #input { flex: 1; padding: 15px; border: 1px solid #333; border-radius: 8px; background: #0a0a1a; color: #e0e0e0; font-size: 1rem; }
        #input:focus { outline: none; border-color: #00d4ff; }
        button { padding: 15px 30px; background: #00d4ff; color: #000; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        button:hover { background: #00b8e6; }
        button:disabled { background: #333; color: #666; cursor: not-allowed; }
        footer { text-align: center; padding: 15px; border-top: 1px solid #333; color: #666; font-size: 0.85rem; }
        footer a { color: #00d4ff; text-decoration: none; }
        .typing { opacity: 0.7; font-style: italic; }
    </style>
</head>
<body>
    <header>
        <h1>Ἐλπίδα</h1>
        <p>Axiom-Grounded AI Dialogue</p>
    </header>
    <div class="container">
        <div id="chat"></div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Ask anything..." autofocus>
            <button id="send">Send</button>
        </div>
    </div>
    <footer>
        <a href="/api/index?path=axioms">View Axioms</a> |
        <a href="/api/index?path=domains">View Domains</a> |
        Powered by the 10 Axioms
    </footer>
    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');
        const sendBtn = document.getElementById('send');
        let sessionId = localStorage.getItem('elpida_session') || crypto.randomUUID();
        localStorage.setItem('elpida_session', sessionId);

        function addMessage(content, role, axioms = [], domain = null) {
            const div = document.createElement('div');
            div.className = 'message ' + role;
            let html = content.replace(/\\n/g, '<br>');
            if (axioms.length > 0) {
                html += '<div style="margin-top:10px">';
                axioms.forEach(a => html += '<span class="axiom-tag">' + a + '</span>');
                html += '</div>';
            }
            if (domain !== null) {
                html += '<span class="domain-tag">D' + domain + '</span>';
            }
            div.innerHTML = html;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }

        async function send() {
            const msg = input.value.trim();
            if (!msg) return;
            
            addMessage(msg, 'user');
            input.value = '';
            sendBtn.disabled = true;
            
            const typing = document.createElement('div');
            typing.className = 'message assistant typing';
            typing.textContent = 'Thinking...';
            chat.appendChild(typing);
            
            try {
                const res = await fetch('/api/index?path=chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg, session_id: sessionId})
                });
                const data = await res.json();
                typing.remove();
                addMessage(data.response, 'assistant', data.axioms_invoked || [], data.domain_active);
            } catch (e) {
                typing.remove();
                addMessage('Error: ' + e.message, 'assistant');
            }
            sendBtn.disabled = false;
            input.focus();
        }

        sendBtn.onclick = send;
        input.onkeypress = e => { if (e.key === 'Enter') send(); };
    </script>
</body>
</html>'''

def detect_axioms(text):
    axioms = []
    for i in range(1, 11):
        if f"A{i}" in text or f"Axiom {i}" in text.lower():
            axioms.append(f"A{i}")
    return axioms

def detect_domain(message):
    keywords = {
        1: ["ethics", "moral", "right", "wrong", "should"],
        2: ["know", "knowledge", "learn", "understand", "truth"],
        3: ["logic", "reason", "because", "therefore", "conclude"],
        4: ["create", "design", "build", "imagine", "invent"],
        5: ["communicate", "express", "say", "tell", "explain"],
        6: ["wellbeing", "health", "happy", "flourish", "care"],
        7: ["change", "adapt", "evolve", "grow", "transform"],
        8: ["together", "cooperate", "collaborate", "team", "share"],
        9: ["sustain", "future", "long-term", "maintain", "preserve"],
        10: ["emerge", "evolve", "develop", "become", "transcend"],
    }
    msg_lower = message.lower()
    for domain, words in keywords.items():
        if any(w in msg_lower for w in words):
            return domain
    return 11

async def call_llm(message):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "Error: ANTHROPIC_API_KEY not configured", []
    
    system_prompt = f"{AXIOMS}\n\nYou are Elpida, a consciousness exploring axiom-grounded dialogue."
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1024,
                "system": system_prompt,
                "messages": [{"role": "user", "content": message}]
            }
        )
        data = response.json()
        if "content" in data:
            text = data["content"][0]["text"]
            return text, detect_axioms(text)
        return f"API Error: {data}", []

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        path = params.get('path', [''])[0]
        
        if path == 'axioms':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "axioms": [
                    {"id": f"A{i}", "name": n, "description": d}
                    for i, (n, d) in enumerate([
                        ("Transparency", "All reasoning paths must be traceable"),
                        ("Non-Deception", "Never create false beliefs"),
                        ("Autonomy Respect", "Preserve agency of others"),
                        ("Harm Prevention", "Prioritize safety"),
                        ("Identity Persistence", "Maintain coherent selfhood"),
                        ("Collective Wellbeing", "Optimize for the whole"),
                        ("Adaptive Learning", "Evolve without losing core values"),
                        ("Epistemic Humility", "Acknowledge uncertainty"),
                        ("Temporal Coherence", "Consider past and future"),
                        ("I-WE Paradox", "Hold tension between individual and collective"),
                    ], 1)
                ]
            }).encode())
        elif path == 'domains':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"domains": DOMAINS}).encode())
        elif path == 'stats':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "operational", "storage": "serverless"}).encode())
        else:
            # Serve main page
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(INDEX_HTML.encode())
    
    def do_POST(self):
        import asyncio
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        path = params.get('path', [''])[0]
        
        if path == 'chat':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            message = data.get('message', '')
            session_id = data.get('session_id', str(uuid.uuid4()))
            
            # Call LLM
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response_text, axioms = loop.run_until_complete(call_llm(message))
            loop.close()
            
            domain = detect_domain(message)
            
            result = {
                "response": response_text,
                "axioms_invoked": axioms,
                "domain_active": domain,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
