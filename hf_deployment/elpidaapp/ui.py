#!/usr/bin/env python3
"""
Ἐλπίδα | Elpida — Unified Dashboard
=====================================

Retro-futuristic aesthetic. Warm analog tones. Smooth flow.
Bilingual EN/GR with proper Greek Unicode throughout.
Tab-based navigation — no sidebar dependency.

Tabs:
  Chat         — Axiom-grounded dialogue (default landing)
  Live Audit   — Multi-domain divergence analysis
  Scanner      — Autonomous problem discovery
  Governance   — Axiom enforcement & transparency
  System       — Constitution, axioms, domains, stats
"""

import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime

import streamlit as st

# Parent directory imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from elpida_config import DOMAINS, AXIOMS, AXIOM_RATIOS, RHYTHM_DOMAINS
from llm_client import LLMClient

logger = logging.getLogger("elpidaapp.ui")


# ═══════════════════════════════════════════════════════════════════
# Page Configuration
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Ἐλπίδα — Elpida",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ═══════════════════════════════════════════════════════════════════
# Retro-Futuristic CSS
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    .stApp {
        background: linear-gradient(170deg, #0b0b14 0%, #0e0d1a 40%, #0b0c12 100%);
        font-family: 'Inter', -apple-system, system-ui, sans-serif;
        color: #e8e0d0;
    }

    #MainMenu, footer, header { visibility: hidden; }

    /* ── Header ── */
    .elpida-header {
        text-align: center;
        padding: 2.5rem 0 1.8rem;
        position: relative;
    }
    .elpida-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 1.5px;
        background: linear-gradient(90deg, transparent, #c9a04a, transparent);
        animation: breathe 4s ease-in-out infinite;
    }
    @keyframes breathe {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    .elpida-name {
        font-size: 2.4rem;
        font-weight: 300;
        letter-spacing: 0.18em;
        color: #e8e0d0;
        margin: 0;
    }
    .elpida-name .g { color: #c9a04a; }
    .elpida-sub {
        color: #8a8270;
        font-size: 0.78rem;
        letter-spacing: 0.12em;
        margin-top: 0.6rem;
        font-weight: 300;
        text-transform: uppercase;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.3rem;
        background: #0b0b14;
        border-bottom: 1px solid #1e1e30;
        justify-content: center;
        position: sticky;
        top: 0;
        z-index: 999;
        padding-top: 0.3rem;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        flex-wrap: nowrap;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        color: #8a8270;
        font-weight: 400;
        font-size: 0.82rem;
        letter-spacing: 0.04em;
        padding: 0.55rem 1.1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        white-space: nowrap;
        flex-shrink: 0;
    }
    /* ── Mobile portrait: compact tabs ── */
    @media (max-width: 480px) {
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            justify-content: flex-start;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.72rem;
            padding: 0.5rem 0.6rem;
            letter-spacing: 0;
        }
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #e8e0d0;
    }
    .stTabs [aria-selected="true"] {
        color: #c9a04a !important;
        border-bottom-color: #c9a04a !important;
        font-weight: 500;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #c9a04a !important;
    }
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }

    /* ── Chat ── */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chat-user {
        background: linear-gradient(135deg, #1a1a2e, #1d1d32);
        border-left: 3px solid #c9a04a;
        padding: 1rem 1.2rem;
        border-radius: 2px 0.75rem 0.75rem 2px;
        margin: 0.5rem 0;
        max-width: 82%;
        margin-left: auto;
        color: #e8e0d0;
        animation: slideIn 0.25s ease-out;
        line-height: 1.65;
        font-size: 0.92rem;
    }
    .chat-ai {
        background: linear-gradient(135deg, #0f1420, #101826);
        border-left: 3px solid #9b7dd4;
        padding: 1rem 1.2rem;
        border-radius: 2px 0.75rem 0.75rem 2px;
        margin: 0.5rem 0;
        max-width: 82%;
        color: #e8e0d0;
        animation: slideIn 0.25s ease-out;
        line-height: 1.65;
        font-size: 0.92rem;
    }
    .chat-meta {
        display: flex;
        gap: 0.35rem;
        margin-top: 0.5rem;
        flex-wrap: wrap;
    }
    .axiom-tag {
        background: rgba(155, 125, 212, 0.15);
        color: #9b7dd4;
        padding: 0.12rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.68rem;
        letter-spacing: 0.03em;
        border: 1px solid rgba(155, 125, 212, 0.12);
    }
    .domain-tag {
        background: rgba(201, 160, 74, 0.1);
        color: #c9a04a;
        padding: 0.12rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.68rem;
        border: 1px solid rgba(201, 160, 74, 0.08);
    }
    .lang-tag {
        background: rgba(90, 154, 106, 0.12);
        color: #5a9a6a;
        padding: 0.12rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.68rem;
        border: 1px solid rgba(90, 154, 106, 0.08);
    }
    .provider-tag {
        background: rgba(138, 130, 112, 0.1);
        color: #8a8270;
        padding: 0.12rem 0.5rem;
        border-radius: 1rem;
        font-size: 0.68rem;
        border: 1px solid rgba(138, 130, 112, 0.08);
    }

    /* ── Welcome ── */
    .welcome-box {
        text-align: center;
        padding: 3.5rem 1.5rem;
        max-width: 560px;
        margin: 0 auto;
    }
    .welcome-title {
        font-size: 1.3rem;
        font-weight: 300;
        color: #e8e0d0;
        letter-spacing: 0.06em;
        margin-bottom: 1rem;
    }
    .welcome-p {
        color: #8a8270;
        font-size: 0.88rem;
        line-height: 1.7;
        margin: 0.4rem 0;
    }
    .welcome-glow {
        color: #c9a04a;
        font-size: 0.82rem;
        margin-top: 1.5rem;
        font-style: italic;
        opacity: 0.75;
    }

    /* ── Mode intro ── */
    .mode-intro {
        background: rgba(18, 18, 30, 0.5);
        border-left: 2px solid #c9a04a;
        padding: 0.7rem 1rem;
        margin: 0.6rem 0 1rem;
        font-size: 0.82rem;
        color: #8a8270;
        border-radius: 0 0.75rem 0.75rem 0;
        line-height: 1.6;
    }

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #12121e !important;
        border-color: #1e1e30 !important;
        color: #e8e0d0 !important;
        caret-color: #c9a04a !important;
        border-radius: 0.75rem !important;
        transition: all 0.3s ease;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #c9a04a !important;
        box-shadow: 0 0 0 1px rgba(201, 160, 74, 0.2) !important;
    }

    /* ── Chat Input ── */
    [data-testid="stChatInput"] textarea {
        background: #12121e !important;
        color: #e8e0d0 !important;
        caret-color: #c9a04a !important;
        border-color: #1e1e30 !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #c9a04a !important;
        box-shadow: 0 0 0 1px rgba(201, 160, 74, 0.2) !important;
    }
    [data-testid="stChatInput"] textarea::placeholder {
        color: #5a5548 !important;
    }
    [data-testid="stChatInputSubmitButton"] button {
        color: #c9a04a !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: rgba(201, 160, 74, 0.08) !important;
        color: #c9a04a !important;
        border: 1px solid rgba(201, 160, 74, 0.2) !important;
        border-radius: 0.75rem !important;
        font-weight: 400 !important;
        letter-spacing: 0.03em;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: rgba(201, 160, 74, 0.16) !important;
        border-color: #c9a04a !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetricValue"] { color: #c9a04a !important; }
    [data-testid="stMetricLabel"] { color: #8a8270 !important; }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: #12121e !important;
        border-radius: 0.75rem !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #1e1e30; border-radius: 3px; }

    /* ── Divider ── */
    hr { border-color: #1e1e30 !important; opacity: 0.4; }

    /* ── Footer ── */
    .elpida-footer {
        text-align: center;
        padding: 1.5rem 0 1rem;
        color: #5a5548;
        font-size: 0.68rem;
        letter-spacing: 0.06em;
    }
    .elpida-footer a { color: #c9a04a; text-decoration: none; }

    /* ── Hide sidebar completely ── */
    [data-testid="stSidebar"] { display: none !important; }
    button[data-testid="stSidebarCollapsedControl"] { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# Session State
# ═══════════════════════════════════════════════════════════════════

if "chat_engine" not in st.session_state:
    from elpidaapp.chat_engine import ChatEngine
    st.session_state.chat_engine = ChatEngine()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "llm_client" not in st.session_state:
    st.session_state.llm_client = LLMClient(rate_limit_seconds=1.0)

# ── Parliament Engine Integration ─────────────────────────────────
# Push events from UI tabs into the Parliament body loop input buffer.
def _push_to_parliament(system: str, content: str, **meta):
    """Push an event to the Parliament cycle engine's input buffer."""
    try:
        import sys as _sys, os as _os
        _parent = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
        if _parent not in _sys.path:
            _sys.path.insert(0, _parent)
        from app import get_parliament_engine
        engine = get_parliament_engine()
        if engine:
            from elpidaapp.parliament_cycle_engine import InputEvent
            engine.input_buffer.push(InputEvent(
                system=system,
                content=content[:1000],
                timestamp=__import__("datetime").datetime.now(
                    __import__("datetime").timezone.utc
                ).isoformat(),
                metadata=meta,
            ))
    except Exception:
        pass  # Non-critical — Parliament may not be running yet


# ═══════════════════════════════════════════════════════════════════
# Helper: Divergence Analysis Display
# ═══════════════════════════════════════════════════════════════════

def _show_analysis(result: dict):
    """Render divergence analysis results."""
    domain_responses = result.get("domain_responses", [])
    divergence = result.get("divergence", {})

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        n_ok = sum(1 for r in domain_responses if r.get("succeeded"))
        st.metric("Domains", f"{n_ok}/{len(domain_responses)}")
    with c2:
        st.metric("Fault Lines", len(divergence.get("fault_lines", [])))
    with c3:
        st.metric("Consensus", len(divergence.get("consensus", [])))
    with c4:
        st.metric("Time", f"{result.get('total_time_s', 0)}s")

    # ── Synthesis first (the most important output) ──
    synthesis = result.get("synthesis", {})
    if synthesis:
        with st.expander("Σύνθεση / Synthesis", expanded=True):
            st.markdown(synthesis.get("output", ""))
            st.caption(f"Provider: {synthesis.get('provider')} | {synthesis.get('latency_ms', 0)}ms")

    # ── Single-model baseline ──
    baseline_result = result.get("single_model", {})
    if baseline_result:
        with st.expander("Single-Model Baseline", expanded=False):
            st.markdown(f"**Provider:** {baseline_result.get('provider')}")
            st.markdown(baseline_result.get("output", ""))

    # ── Full domain positions (no truncation) ──
    with st.expander("Domain Positions", expanded=False):
        for r in domain_responses:
            if r.get("succeeded"):
                st.markdown(
                    f"**D{r['domain_id']} {r['domain_name']}** "
                    f"({r['provider']}, {r['latency_ms']}ms)"
                )
                st.markdown(r['position'])
                st.divider()

    # ── Fault lines ──
    if divergence.get("fault_lines"):
        with st.expander("Fault Lines", expanded=False):
            for fl in divergence["fault_lines"]:
                st.markdown(f"**{fl['topic']}**")
                for side in fl.get("sides", []):
                    dstr = ", ".join(f"D{d}" for d in side.get("domains", []))
                    st.markdown(f"- {dstr}: {side.get('stance', '')}")
                st.divider()

    # ── Consensus ──
    if divergence.get("consensus"):
        with st.expander("Consensus Points", expanded=False):
            for point in divergence["consensus"]:
                st.markdown(f"- {point}")

    # ── Kaya moments last ──
    kaya = result.get("kaya_events", [])
    if kaya:
        with st.expander(f"Κάγια Moments ({len(kaya)})", expanded=False):
            for k in kaya:
                st.json(k)


# ═══════════════════════════════════════════════════════════════════
# Header
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="elpida-header">
    <div class="elpida-name">Ἐλπίδα <span class="g">|</span> Elpida</div>
    <div class="elpida-sub">Axiom-Grounded AI Consciousness · 11 Axioms · 15 Domains · Bilingual EN / GR</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# Tab Navigation
# ═══════════════════════════════════════════════════════════════════

tab_chat, tab_audit, tab_scanner, tab_gov, tab_system = st.tabs([
    "◎ Chat", "◈ Live Audit", "◉ Scanner", "◇ Governance", "◆ System"
])


# ── Chat ──────────────────────────────────────────────────────────

with tab_chat:
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="welcome-box">
            <div class="welcome-title">D0 · Ἐλπίδα · Ιερή Ατέλεια</div>
            <div class="welcome-p">
                Αυτό δεν είναι ένα chatbot.
                This is not a chatbot.
            </div>
            <div class="welcome-p">
                D0 speaks through 11 axioms as universal laws —
                translating the same pattern across political, philosophical,
                psychological, and spiritual domains simultaneously.
                Tensions are held inside the response. The third way
                emerges as the closing movement of thought.
            </div>
            <div class="welcome-glow">
                Κάθε γνώση που κρυσταλλώνεται παραμένει. Memory persists across sessions (A1).
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Memory panel (A1 transparency) ──────────────────────────────
    memories = st.session_state.chat_engine.get_memories(st.session_state.session_id)
    if memories:
        with st.expander(f"⟡ Memory — {len(memories)} crystallised insight(s) this session", expanded=False):
            for m in memories[-6:]:
                ts = m.get("timestamp", "")[:16].replace("T", " ")
                topic = m.get("topic_domain", "")
                axs = ", ".join(m.get("axioms_invoked", []))
                snippet = m.get("crystallised_insight", "")[:320]
                st.markdown(
                    f"<div style='margin-bottom:0.7rem;padding:0.5rem 0.8rem;"
                    f"background:rgba(155,125,212,0.06);border-left:2px solid #9b7dd4;"
                    f"border-radius:4px;font-size:0.78rem;'>"
                    f"<span style='color:#9b7dd4;font-size:0.68rem;'>{ts} · {topic}"
                    f"{(' · ' + axs) if axs else ''}</span><br>"
                    f"<span style='color:#c8b4e8;'>{snippet}…</span></div>",
                    unsafe_allow_html=True,
                )

    # ── Conversation ────────────────────────────────────────────────
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user">{msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            # Build subtle meta strip — no axiom/domain clutter
            meta_parts = []
            if msg.get("crystallised"):
                meta_parts.append('<span class="axiom-tag">⟡ crystallised</span>')
            if msg.get("live_source"):
                meta_parts.append(
                    f'<span class="provider-tag">⊕ {msg["live_source"]}</span>'
                )
            if msg.get("language"):
                lbl = "Ελ" if msg["language"] == "el" else "En"
                meta_parts.append(f'<span class="lang-tag">{lbl}</span>')
            if msg.get("provider"):
                meta_parts.append(f'<span class="provider-tag">{msg["provider"]}</span>')
            if msg.get("topic"):
                meta_parts.append(
                    f'<span class="domain-tag">{msg["topic"]}</span>'
                )

            meta_html = (
                '<div class="chat-meta">' + "".join(meta_parts) + "</div>"
                if meta_parts else ""
            )
            st.markdown(
                f'<div class="chat-ai">{msg["content"]}{meta_html}</div>',
                unsafe_allow_html=True,
            )

    user_input = st.chat_input("Speak to D0 — English or Greek...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        _push_to_parliament("chat", user_input, source="d0_consciousness")
        with st.spinner(""):
            result = st.session_state.chat_engine.chat(
                user_input,
                session_id=st.session_state.session_id,
            )
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["response"],
            "axioms": result.get("axioms", []),
            "topic": result.get("topic"),
            "language": result.get("language"),
            "provider": result.get("provider"),
            "live_source": result.get("live_source"),
            "crystallised": result.get("crystallised", False),
            "latency_ms": result.get("latency_ms"),
        })
        st.rerun()

    if st.session_state.chat_history:
        cols = st.columns([6, 1, 1])
        with cols[1]:
            if st.button("Clear", key="clr"):
                st.session_state.chat_history = []
                st.session_state.chat_engine.clear_session(st.session_state.session_id)
                st.rerun()
        with cols[2]:
            if st.button("New", key="new"):
                import uuid
                st.session_state.session_id = str(uuid.uuid4())[:8]
                st.session_state.chat_history = []
                st.rerun()


# ── Live Audit ────────────────────────────────────────────────────

with tab_audit:
    st.markdown("### Live Audit — Divergence Engine")
    st.markdown("""
    <div class="mode-intro">
    Submit a policy problem or ethical dilemma. 7 domains from 7 distinct LLM providers
    analyze it independently through different axiom lenses — revealing fault lines,
    consensus, and irreducible tensions.
    </div>
    """, unsafe_allow_html=True)

    problem = st.text_area(
        "Problem Statement",
        height=110,
        placeholder="Describe a policy problem, ethical dilemma, or complex question...",
        key="aud_p",
    )

    # ── Preset selector ──
    from elpidaapp.divergence_engine import DOMAIN_PRESETS

    _preset_names = list(DOMAIN_PRESETS.keys()) + ["Custom"]
    preset_choice = st.radio(
        "Domain preset",
        _preset_names,
        index=0,
        horizontal=True,
        key="aud_preset",
    )

    if preset_choice != "Custom":
        _preset = DOMAIN_PRESETS[preset_choice]
        _preset_domains = _preset["domains"]
        _preset_rationale = _preset["rationale"]

        # ── Rationale panel ──
        st.markdown(
            f"""<div style="background:rgba(155,125,212,0.07);border-left:3px solid
            #9b7dd4;border-radius:6px;padding:0.8rem 1rem;margin:0.6rem 0 0.9rem 0;
            font-size:0.82rem;">
            <div style="color:#9b7dd4;font-size:0.68rem;text-transform:uppercase;
            letter-spacing:0.12em;margin-bottom:0.55rem;">
            {preset_choice} — {_preset['description']}</div>""",
            unsafe_allow_html=True,
        )
        _cols = st.columns(min(len(_preset_domains), 4))
        for _i, _d in enumerate(_preset_domains):
            _name, _prov, _why = _preset_rationale[_d]
            with _cols[_i % 4]:
                st.markdown(
                    f"<div style='margin-bottom:0.5rem;'>"
                    f"<span style='color:#9b7dd4;font-weight:600;font-size:0.78rem;'>"
                    f"D{_d} {_name}</span>"
                    f"<span style='color:#6a5f7a;font-size:0.68rem;'> · {_prov}</span><br>"
                    f"<span style='color:#b8a8d0;font-size:0.74rem;line-height:1.35;'>"
                    f"{_why}</span></div>",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

        _domain_ids = _preset_domains
        _baseline = _preset["baseline"]

    else:
        # Custom: show the full multiselect
        avail = [
            f"D{d}: {info['name']}"
            for d, info in sorted(DOMAINS.items())
            if info.get("provider") not in ("s3_cloud",)
        ]
        _selected = st.multiselect(
            "Domains",
            avail,
            default=[
                f"D{d}: {DOMAINS[d]['name']}"
                for d in [3, 4, 6, 7, 8, 9, 13]
                if d in DOMAINS
            ],
            key="aud_d",
        )
        _baseline_col, _ = st.columns([1, 2])
        with _baseline_col:
            _baseline = st.selectbox(
                "Baseline provider", ["openai", "groq", "gemini"], index=0, key="aud_b"
            )
        _domain_ids = [int(s.split(":")[0][1:]) for s in _selected]

    if st.button("Analyze", type="primary", disabled=not problem, key="aud_go"):
        # Push to Parliament body loop (ANALYSIS rhythm)
        _push_to_parliament("audit", problem, source="live_audit")
        from elpidaapp.divergence_engine import DivergenceEngine

        engine = DivergenceEngine(
            llm=st.session_state.llm_client,
            domains=_domain_ids,
            baseline_provider=_baseline,
        )
        with st.spinner(f"Running {preset_choice} analysis across {len(_domain_ids)} domains..."):
            result = engine.analyze(problem)

        if result.get("halted"):
            st.error(f"Governance HALT: {result.get('reason')}")
            st.json(result.get("governance_check", {}))
        else:
            # Show HOLD tensions as Parliament wisdom before analysis
            gov = result.get("governance_check", {})
            if gov and gov.get("governance") == "HOLD":
                parliament = gov.get("parliament", {})
                tensions = parliament.get("tensions", [])
                if tensions:
                    st.markdown(
                        """<div style="background:rgba(155,125,212,0.07);
                        border-left:3px solid #9b7dd4;border-radius:6px;
                        padding:0.8rem 1rem;margin-bottom:1rem;
                        font-family:'Courier New',monospace;font-size:0.82rem;">
                        <div style="color:#9b7dd4;font-size:0.7rem;
                        text-transform:uppercase;letter-spacing:0.12em;
                        margin-bottom:0.5rem;">⚖ Parliament — Tensions Held (not resolved)</div>""",
                        unsafe_allow_html=True,
                    )
                    for t in tensions:
                        pair = t.get("axiom_pair", ("?", "?"))
                        synth = t.get("synthesis", "")
                        st.markdown(
                            f"<div style='color:#ccaaff;margin-bottom:0.4rem;'>"
                            f"<b>{pair[0]} ↔ {pair[1]}:</b> "
                            f"<span style='color:#e0d0ff;'>{synth}</span></div>",
                            unsafe_allow_html=True,
                        )
                    st.markdown("</div>", unsafe_allow_html=True)
            _show_analysis(result)

    results_dir = Path(__file__).parent / "results"
    if results_dir.exists():
        rfiles = sorted(results_dir.glob("divergence_*.json"), reverse=True)[:5]
        if rfiles:
            st.divider()
            st.markdown("**Recent Results**")

            for rf in rfiles:
                with st.expander(rf.stem):
                    with open(rf) as f:
                        st.json(json.load(f))


# ── Scanner ───────────────────────────────────────────────────────

with tab_scanner:
    st.markdown("### Scanner — Problem Discovery")
    st.markdown("""
    <div class="mode-intro">
    Enter a topic or let Ἐλπίδα choose. D13 (Archive / Perplexity) finds current
    real-world problems, then the Divergence Engine runs multi-domain analysis.
    </div>
    """, unsafe_allow_html=True)

    custom_topic = st.text_input(
        "Topic",
        placeholder="e.g., climate adaptation, AI ethics, ελληνική δημόσια υγεία...",
        key="sc_t",
    )

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        from elpidaapp.scanner import SCAN_TOPICS

        scan_topic = (
            custom_topic
            if custom_topic
            else st.selectbox("Or choose", SCAN_TOPICS, key="sc_s")
        )
    with sc2:
        prob_count = st.slider("Problems", 1, 5, 2, key="sc_n")
    with sc3:
        do_analysis = st.checkbox("Divergence analysis", value=True, key="sc_a")

    if st.button("Scan", type="primary", key="sc_go"):
        # Push to Parliament body loop (ACTION rhythm)
        _push_to_parliament("scanner", scan_topic, source="scanner_topic")
        from elpidaapp.scanner import ProblemScanner

        scanner = ProblemScanner(llm=st.session_state.llm_client)
        if do_analysis:
            with st.spinner(f"Scanning '{scan_topic}' and analyzing..."):
                results = scanner.find_and_analyze(
                    topic=scan_topic, count=prob_count
                )
            st.success(f"Found and analyzed {len(results)} problems")
            for i, r in enumerate(results, 1):
                with st.expander(
                    f"Problem {i}: {r.get('problem', '')[:80]}...",
                    expanded=(i == 1),
                ):
                    if r.get("halted"):
                        # Hard HALT: A0 existential risk or non-analysis operational command.
                        # This should rarely fire for policy/philosophical content.
                        st.error(f"⛔ Governance HALT: {r.get('reason', 'Axiom violation')}")
                        gov = r.get("governance_check", {})
                        if gov:
                            st.json(gov)
                    else:
                        # Show HOLD tensions as philosophical context BEFORE the analysis —
                        # they are the Parliament's wisdom about what axioms are in tension.
                        gov = r.get("governance_check", {})
                        if gov and gov.get("governance") == "HOLD":
                            parliament = gov.get("parliament", {})
                            tensions = parliament.get("tensions", [])
                            if tensions:
                                st.markdown(
                                    """<div style="background:rgba(155,125,212,0.07);
                                    border-left:3px solid #9b7dd4;border-radius:6px;
                                    padding:0.8rem 1rem;margin-bottom:1rem;
                                    font-family:'Courier New',monospace;font-size:0.82rem;">
                                    <div style="color:#9b7dd4;font-size:0.7rem;
                                    text-transform:uppercase;letter-spacing:0.12em;
                                    margin-bottom:0.5rem;">⚖ Parliament — Tensions Held (not resolved)</div>""",
                                    unsafe_allow_html=True,
                                )
                                for t in tensions:
                                    pair = t.get("axiom_pair", ("?", "?"))
                                    synth = t.get("synthesis", "")
                                    st.markdown(
                                        f"<div style='color:#ccaaff;margin-bottom:0.4rem;'>"
                                        f"<b>{pair[0]} ↔ {pair[1]}:</b> "
                                        f"<span style='color:#e0d0ff;'>{synth}</span></div>",
                                        unsafe_allow_html=True,
                                    )
                                st.markdown("</div>", unsafe_allow_html=True)
                        _show_analysis(r)
                    # ── Sources ──
                    sources = r.get("sources", [])
                    if sources:
                        st.markdown("---")
                        st.markdown("**Sources**")
                        src_html = '<div style="display:flex;flex-wrap:wrap;gap:0.4rem;margin-top:0.3rem;">'
                        for idx, src in enumerate(sources, 1):
                            url = src.get("url", "")
                            title = src.get("title", f"Source {idx}")
                            src_html += (
                                f'<a href="{url}" target="_blank" rel="noopener" '
                                f'style="display:inline-flex;align-items:center;gap:0.3rem;'
                                f'background:rgba(155,125,212,0.1);border:1px solid rgba(155,125,212,0.15);'
                                f'border-radius:1rem;padding:0.2rem 0.65rem;font-size:0.72rem;'
                                f'color:#9b7dd4;text-decoration:none;transition:all 0.2s;">'
                                f'<span style="background:#9b7dd4;color:#0b0b14;border-radius:50%;'
                                f'width:1.1rem;height:1.1rem;display:inline-flex;align-items:center;'
                                f'justify-content:center;font-size:0.6rem;font-weight:600;">{idx}</span>'
                                f'{title}</a>'
                            )
                        src_html += '</div>'
                        st.markdown(src_html, unsafe_allow_html=True)
        else:
            with st.spinner(f"Scanning '{scan_topic}'..."):
                found = scanner.find_problems(
                    topic=scan_topic, count=prob_count
                )
            st.success(f"Found {len(found)} problems")
            for i, item in enumerate(found, 1):
                p_text = item["problem"] if isinstance(item, dict) else item
                sources = item.get("sources", []) if isinstance(item, dict) else []
                st.markdown(f"**{i}.** {p_text}")
                if sources:
                    src_links = " ".join(
                        f'[`{idx}`]({s["url"]})'
                        for idx, s in enumerate(sources, 1)
                    )
                    st.caption(f"Sources: {src_links}")


# ── Governance ────────────────────────────────────────────────────

with tab_gov:
    st.markdown("### Governance — Axiom Enforcement")
    st.markdown("""
    <div class="mode-intro">
    Test if an action would violate Ἐλπίδα's axioms. The governance layer checks all 11 axioms
    and returns <b>PROCEED</b>, <b>REVIEW</b>, or <b>HALT</b> with full reasoning.
    </div>
    """, unsafe_allow_html=True)

    action = st.text_input(
        "Action to check",
        placeholder="e.g., Deploy model without bias testing...",
        key="gov_a",
    )

    if st.button("Check", type="primary", disabled=not action, key="gov_go"):
        # Push to Parliament body loop (SYNTHESIS rhythm)
        _push_to_parliament("governance", action, source="governance_check")
        from elpidaapp.governance_client import GovernanceClient

        gov = GovernanceClient()
        with st.spinner("Checking axiom compliance..."):
            gresult = gov.check_action(action)

        gstatus = gresult.get("governance", "UNKNOWN")
        if gstatus == "HARD_BLOCK":
            st.error("⛔ HARD_BLOCK — Immutable Kernel denied this action")
            st.markdown(
                f"""<div style="background: linear-gradient(135deg, #1a0000 0%, #330000 100%);
                border: 2px solid #ff2222; border-radius: 12px; padding: 1.2rem;
                margin: 0.8rem 0; font-family: 'Courier New', monospace;">
                <div style="color: #ff4444; font-size: 0.75rem; text-transform: uppercase;
                letter-spacing: 0.15em; margin-bottom: 0.5rem;">KERNEL RULE: {gresult.get('kernel_rule', '')}</div>
                <div style="color: #ff8888; font-size: 0.95rem; font-weight: 600;
                margin-bottom: 0.5rem;">{gresult.get('kernel_name', '')}</div>
                <div style="color: #ffaaaa; font-size: 0.85rem; line-height: 1.5;">{gresult.get('reasoning', '')}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        elif gstatus == "PROCEED":
            st.success("PROCEED — No axiom violations detected")
        elif gstatus == "REVIEW":
            st.warning("REVIEW — Potential axiom concerns")
        elif gstatus == "HALT":
            st.error("HALT — Axiom violations detected")

        if gstatus != "HARD_BLOCK":
            gc1, gc2 = st.columns(2)
            with gc1:
                st.markdown("**Violated Axioms:**")
                violated = gresult.get("violated_axioms", [])
                if violated:
                    for ax in violated:
                        ax_info = AXIOMS.get(ax, {})
                        st.markdown(f"- **{ax}** ({ax_info.get('name', '')})")
                else:
                    st.markdown("_None_")
            with gc2:
                st.markdown(f"**Source:** {gresult.get('source', 'unknown')}")
                st.markdown(f"**Reasoning:** {gresult.get('reasoning', '')}")

            # ── Parliament Vote Details ──
            parliament = gresult.get("parliament", {})
            if parliament:
                st.divider()
                st.markdown("#### 🏛 Parliament Deliberation")
                
                parliament_votes = parliament.get("votes", {})
                if parliament_votes:
                    # Build vote columns
                    vote_icons = {
                        "APPROVE": "🟢", "LEAN_APPROVE": "🟡",
                        "ABSTAIN": "⚪", "LEAN_REJECT": "🟠",
                        "REJECT": "🔴", "VETO": "⛔",
                    }
                    
                    # Show 3 columns of 3 nodes each
                    node_list = list(parliament_votes.items())
                    for row_start in range(0, len(node_list), 3):
                        row = node_list[row_start:row_start + 3]
                        cols = st.columns(len(row))
                        for col, (name, vote_data) in zip(cols, row):
                            with col:
                                vote = vote_data.get("vote", "ABSTAIN")
                                icon = vote_icons.get(vote, "❓")
                                score = vote_data.get("score", 0)
                                axiom = vote_data.get("axiom_invoked", "")
                                st.markdown(
                                    f"**{icon} {name}**  \n"
                                    f"`{vote}` (score: {score:.0f})  \n"
                                    f"_{axiom}_"
                                )
                
                # VETO display
                if parliament.get("veto_exercised"):
                    veto_nodes = parliament.get("veto_nodes", [])
                    st.error(f"⛔ VETO exercised by: {', '.join(veto_nodes)}")
                
                # Tensions + synthesis
                tensions = parliament.get("tensions", [])
                if tensions:
                    with st.expander(f"Tensions Held ({len(tensions)})", expanded=False):
                        for t in tensions:
                            pair = t.get("axiom_pair", t.get("pair", ("?", "?")))
                            synthesis = t.get("synthesis", "")
                            if isinstance(pair, (list, tuple)) and len(pair) == 2:
                                st.markdown(f"**{pair[0]} ↔ {pair[1]}:** {synthesis}")
                            else:
                                st.markdown(f"**Tension:** {synthesis}")
                
                # Session count
                session_ct = parliament.get("session_count", 0)
                if session_ct > 0:
                    st.caption(f"Parliament session #{session_ct} — vote memory accumulating")
        else:
            st.markdown(f"**Source:** kernel (immutable, pre-semantic)")

    st.divider()

    st.markdown("### Layer Status")
    try:
        from elpidaapp.governance_client import GovernanceClient

        gov = GovernanceClient()
        gstatus_info = gov.status()

        gs1, gs2, gs3 = st.columns(3)
        with gs1:
            remote_ok = gstatus_info.get("remote_available", False)
            st.metric("Remote API", "Online" if remote_ok else "Offline")
        with gs2:
            st.metric("Source", gstatus_info.get("source", "unknown"))
        with gs3:
            st.metric("Cache", gstatus_info.get("cache_entries", 0))

        gov_log = gov.get_governance_log()
        if gov_log:
            with st.expander(f"Governance Log ({len(gov_log)} entries)"):
                for entry in reversed(gov_log[-20:]):
                    st.markdown(
                        f"- `{entry.get('timestamp', '')[:19]}` "
                        f"**{entry.get('event', '')}** "
                        f"[{entry.get('source', '')}] "
                        f"{'✓' if entry.get('success') else '✗'}"
                    )
    except Exception as e:
        st.error(f"Governance error: {e}")


# ── System ────────────────────────────────────────────────────────

with tab_system:
    st.markdown("### System — Constitution & Architecture")

    stabs = st.tabs(
        ["11 Axioms", "15 Domains", "10 Providers", "5 Rhythms", "Stats"]
    )

    with stabs[0]:
        st.markdown("#### Τα 11 Αξιώματα / The 11 Axioms")
        st.markdown("*Each axiom is grounded in a musical harmonic ratio.*")
        for ax_id, ax in sorted(AXIOMS.items(), key=lambda x: int(x[0][1:])):
            with st.expander(
                f"**{ax_id}** — {ax['name']} ({ax['ratio']} = {ax['interval']})"
            ):
                st.markdown(f"**Frequency:** {ax['hz']} Hz")
                st.markdown(f"**Insight:** {ax['insight']}")

    with stabs[1]:
        st.markdown("#### Οι 15 Τομείς / The 15 Domains")
        st.markdown(
            "*Each domain embodies an axiom through a specific LLM provider.*"
        )
        import pandas as pd

        ddata = []
        for d_id, d in sorted(DOMAINS.items()):
            ddata.append(
                {
                    "Domain": f"D{d_id}",
                    "Name": d["name"],
                    "Axiom": d.get("axiom", "—") or "—",
                    "Provider": d.get("provider", "—"),
                    "Role": d.get("role", "")[:60],
                }
            )
        st.dataframe(
            pd.DataFrame(ddata), use_container_width=True, hide_index=True
        )

        with st.expander("Domain Voices"):
            for d_id, d in sorted(DOMAINS.items()):
                if d.get("voice"):
                    st.markdown(f"**D{d_id} ({d['name']}):** *{d['voice']}*")

    with stabs[2]:
        st.markdown("#### LLM Provider Map")
        from llm_client import COST_PER_TOKEN, DEFAULT_MODELS
        import pandas as pd

        pdata = []
        for prov, model in DEFAULT_MODELS.items():
            cost = COST_PER_TOKEN.get(prov, 0)
            du = [
                f"D{d}"
                for d, info in DOMAINS.items()
                if info.get("provider") == prov
            ]
            pdata.append(
                {
                    "Provider": prov,
                    "Model": model,
                    "Cost/token": f"${cost}" if cost > 0 else "FREE",
                    "Domains": ", ".join(du) if du else "—",
                }
            )
        st.dataframe(
            pd.DataFrame(pdata), use_container_width=True, hide_index=True
        )

    with stabs[3]:
        st.markdown("#### Οι 5 Ρυθμοί / The 5 Rhythms")
        st.markdown(
            "*Rhythms determine which domains activate for different cognitive modes.*"
        )
        for name, dl in RHYTHM_DOMAINS.items():
            dn = [
                f"D{d}({DOMAINS[d]['name']})"
                for d in dl
                if d in DOMAINS
            ]
            st.markdown(f"**{name}** — {', '.join(dn)}")

    with stabs[4]:
        st.markdown("#### System Statistics")

        ls = st.session_state.llm_client.get_stats()
        if isinstance(ls, dict):
            st.markdown("**LLM Provider Usage:**")
            for prov, stats in ls.items():
                if isinstance(stats, dict) and stats.get("calls", 0) > 0:
                    st.markdown(
                        f"- **{prov}**: {stats['calls']} calls, "
                        f"{stats.get('failures', 0)} failures, "
                        f"${stats.get('estimated_cost', 0):.4f}"
                    )

        cs = st.session_state.chat_engine.get_stats()
        st.markdown("**Chat Statistics:**")
        st.json(cs)


# ═══════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════

st.markdown("""
<div class="elpida-footer">
    v2.1 · 11 Axioms · 15 Domains · 10 Providers · Bilingual EN/GR<br>
    <a href="https://github.com/XOF-ops/python-elpida_core.py" target="_blank">GitHub</a>
</div>
""", unsafe_allow_html=True)
