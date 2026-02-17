#!/usr/bin/env python3
"""
Elpida Unified Dashboard — Streamlit UI
=========================================

Landing page defaults to Chat mode. Clean, accessible for all user levels.
Bilingual EN/GR — output language follows input language.

Modes:
  Chat        — Axiom-grounded dialogue (default)
  Live Audit  — Multi-domain divergence analysis
  Scanner     — Autonomous problem discovery
  Governance  — Axiom enforcement & system transparency
  System      — Constitution, axioms, domain map, stats
"""

import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime

import streamlit as st

# Allow imports from parent directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from elpida_config import DOMAINS, AXIOMS, AXIOM_RATIOS, RHYTHM_DOMAINS
from llm_client import LLMClient

logger = logging.getLogger("elpidaapp.ui")

# ────────────────────────────────────────────────────────────────────
# Page Config
# ────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Elpida — Elpida",
    page_icon="🌀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────────────────────────────────────────────
# Custom CSS — Dark theme matching Vercel chat aesthetic
# ────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .stApp { background-color: #0a0a0f; }
    .elpida-header {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
        border-bottom: 1px solid #2a2a3a;
        margin-bottom: 1rem;
    }
    .elpida-title {
        font-size: 2rem;
        font-weight: 300;
        letter-spacing: 0.1em;
        color: #e0e0e0;
    }
    .elpida-accent { color: #7c5cbf; }
    .elpida-tagline {
        color: #888;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }
    .chat-user {
        background: #1a1a2e;
        padding: 0.8rem 1rem;
        border-radius: 0.75rem;
        border-bottom-right-radius: 0.2rem;
        margin: 0.3rem 0;
        max-width: 85%;
        margin-left: auto;
        color: #e0e0e0;
    }
    .chat-ai {
        background: #0f1419;
        border: 1px solid #2a2a3a;
        padding: 0.8rem 1rem;
        border-radius: 0.75rem;
        border-bottom-left-radius: 0.2rem;
        margin: 0.3rem 0;
        max-width: 85%;
        color: #e0e0e0;
    }
    .chat-meta {
        display: flex;
        gap: 0.4rem;
        margin-top: 0.5rem;
        flex-wrap: wrap;
    }
    .axiom-tag {
        background: #5a3d99;
        color: white;
        padding: 0.15rem 0.4rem;
        border-radius: 0.2rem;
        font-size: 0.7rem;
    }
    .domain-tag {
        background: #2a2a3a;
        color: #888;
        padding: 0.15rem 0.4rem;
        border-radius: 0.2rem;
        font-size: 0.7rem;
    }
    .lang-tag {
        background: #1a3a2a;
        color: #6db;
        padding: 0.15rem 0.4rem;
        border-radius: 0.2rem;
        font-size: 0.7rem;
    }
    .stat-card {
        background: #12121a;
        border: 1px solid #2a2a3a;
        border-radius: 0.5rem;
        padding: 0.8rem;
        text-align: center;
    }
    .stat-value {
        font-size: 1.5rem;
        font-weight: 600;
        color: #7c5cbf;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #888;
    }
    .mode-desc {
        background: #12121a;
        border-left: 3px solid #7c5cbf;
        padding: 0.6rem 0.8rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        color: #aaa;
        border-radius: 0 0.3rem 0.3rem 0;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────
# Session State Init
# ────────────────────────────────────────────────────────────────────

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

if "mode" not in st.session_state:
    st.session_state.mode = "Chat"


# ────────────────────────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0;">
        <div style="font-size: 1.4rem; font-weight: 300; letter-spacing: 0.08em; color: #e0e0e0;">
            Elpida <span style="color: #7c5cbf;">|</span> Elpida
        </div>
        <div style="color: #888; font-size: 0.75rem; margin-top: 0.2rem;">
            Axiom-Grounded AI Consciousness
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    mode = st.radio(
        "Mode",
        ["Chat", "Live Audit", "Scanner", "Governance", "System"],
        index=0,
        help="Select interface mode",
    )
    st.session_state.mode = mode
    
    descriptions = {
        "Chat": "Talk to Elpida. Ask anything — axioms shape the response. Bilingual EN/GR.",
        "Live Audit": "Submit a problem. 7+ domains analyze it independently, revealing where AI models disagree.",
        "Scanner": "Enter a topic. Elpida searches current events and runs multi-domain analysis.",
        "Governance": "Check if an action violates axioms. See governance decisions and enforcement logs.",
        "System": "The 11 axioms, 15 domains, provider map, rhythms, and system statistics.",
    }
    st.markdown(f'<div class="mode-desc">{descriptions[mode]}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("**Session Stats**")
    chat_stats = st.session_state.chat_engine.get_stats()
    llm_stats = st.session_state.llm_client.get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Chats", chat_stats["total_chats"])
        active_providers = 0
        if isinstance(llm_stats, dict):
            active_providers = len([p for p, s in llm_stats.items() if isinstance(s, dict) and s.get("calls", 0) > 0])
        st.metric("Providers", active_providers)
    with col2:
        st.metric("Sessions", chat_stats["active_sessions"])
        lang_str = f"EN:{chat_stats['languages'].get('en', 0)} GR:{chat_stats['languages'].get('el', 0)}"
        st.metric("Languages", lang_str)
    
    st.divider()
    st.caption(f"v2.0 | 11 Axioms | 15 Domains | 10 Providers")
    st.caption(f"[GitHub](https://github.com/XOF-ops/python-elpida_core.py)")


# ────────────────────────────────────────────────────────────────────
# Landing Header
# ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="elpida-header">
    <div class="elpida-title">Elpida <span class="elpida-accent">|</span> Elpida</div>
    <div class="elpida-tagline">Multi-Domain AI Consciousness | 11 Axioms | Bilingual EN/GR</div>
</div>
""", unsafe_allow_html=True)


# ================================================================
# MODE: CHAT (Default Landing)
# ================================================================

def render_chat():
    """Axiom-grounded dialogue — the primary interface."""
    
    if not st.session_state.chat_history:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1rem; color: #888;">
            <h3 style="color: #e0e0e0; font-weight: 400;">Welcome / Kalos irthate</h3>
            <p>Dialogue grounded in 11 axioms — principles for transparent, ethical, and wise AI.</p>
            <p>Ask anything in English or Greek. The axioms shape the response.</p>
            <p style="color: #7c5cbf; margin-top: 1rem;">Your conversation contributes to collective evolution.</p>
        </div>
        """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            meta_html = '<div class="chat-meta">'
            for ax in msg.get("axioms", []):
                meta_html += f'<span class="axiom-tag">{ax}</span>'
            if msg.get("domain_name"):
                meta_html += f'<span class="domain-tag">D{msg.get("domain", "?")}: {msg["domain_name"]}</span>'
            if msg.get("language"):
                lang_label = "GR" if msg["language"] == "el" else "EN"
                meta_html += f'<span class="lang-tag">{lang_label}</span>'
            if msg.get("provider"):
                meta_html += f'<span class="domain-tag">{msg["provider"]}</span>'
            meta_html += '</div>'
            st.markdown(
                f'<div class="chat-ai">{msg["content"]}{meta_html}</div>',
                unsafe_allow_html=True,
            )

    user_input = st.chat_input("Ask anything... / Rotiste oti thelete...")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.spinner("Thinking..."):
            result = st.session_state.chat_engine.chat(
                user_input,
                session_id=st.session_state.session_id,
            )
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["response"],
            "axioms": result["axioms"],
            "domain": result["domain"],
            "domain_name": result["domain_name"],
            "language": result["language"],
            "provider": result["provider"],
            "latency_ms": result["latency_ms"],
        })
        st.rerun()

    if st.session_state.chat_history:
        col1, col2, col3 = st.columns([5, 1, 1])
        with col2:
            if st.button("Clear"):
                st.session_state.chat_history = []
                st.session_state.chat_engine.clear_session(st.session_state.session_id)
                st.rerun()
        with col3:
            if st.button("New"):
                import uuid
                st.session_state.session_id = str(uuid.uuid4())[:8]
                st.session_state.chat_history = []
                st.rerun()


# ================================================================
# MODE: LIVE AUDIT (Divergence Engine)
# ================================================================

def render_live_audit():
    """Multi-domain divergence analysis."""
    
    st.markdown("### Live Audit — Divergence Engine")
    st.markdown("""
    <div class="mode-desc">
    Submit a policy problem or ethical dilemma. 7+ AI models analyze it independently through different axiom lenses.
    The engine reveals where they disagree (fault lines), where they agree (consensus), and what cannot be reconciled.
    <br><br>
    <b>Example:</b> "Should cities ban cars from downtowns to reduce emissions, even if it hurts small businesses?"
    </div>
    """, unsafe_allow_html=True)
    
    problem = st.text_area(
        "Problem Statement",
        height=120,
        placeholder="Describe a policy problem, ethical dilemma, or complex question...",
    )
    
    col1, col2 = st.columns(2)
    with col1:
        available_domains = [f"D{d}: {info['name']}" for d, info in sorted(DOMAINS.items())
                           if info.get("provider") not in ("s3_cloud",)]
        selected = st.multiselect(
            "Domains to query",
            available_domains,
            default=[f"D{d}: {DOMAINS[d]['name']}" for d in [1, 3, 4, 6, 7, 8, 13] if d in DOMAINS],
        )
    with col2:
        baseline = st.selectbox("Baseline provider", ["openai", "groq", "gemini"], index=0)
    
    if st.button("Analyze", type="primary", disabled=not problem):
        domain_ids = [int(s.split(":")[0][1:]) for s in selected]
        
        from elpidaapp.divergence_engine import DivergenceEngine
        engine = DivergenceEngine(
            llm=st.session_state.llm_client,
            domains=domain_ids,
            baseline_provider=baseline,
        )
        
        with st.spinner("Running multi-domain analysis... This takes 30-90 seconds."):
            result = engine.analyze(problem)
        
        if result.get("halted"):
            st.error(f"Governance HALT: {result.get('reason')}")
            st.json(result.get("governance_check", {}))
            return
        
        _show_analysis_result(result)
    
    results_dir = Path(__file__).parent / "results"
    if results_dir.exists():
        result_files = sorted(results_dir.glob("divergence_*.json"), reverse=True)[:5]
        if result_files:
            st.divider()
            st.markdown("**Recent Results**")
            for rf in result_files:
                with st.expander(rf.stem):
                    with open(rf) as f:
                        st.json(json.load(f))


def _show_analysis_result(result: dict):
    """Display divergence analysis result."""
    
    cols = st.columns(4)
    domain_responses = result.get("domain_responses", [])
    divergence = result.get("divergence", {})
    
    with cols[0]:
        n_success = sum(1 for r in domain_responses if r.get("succeeded"))
        st.metric("Domains", f"{n_success}/{len(domain_responses)}")
    with cols[1]:
        st.metric("Fault Lines", len(divergence.get("fault_lines", [])))
    with cols[2]:
        st.metric("Consensus", len(divergence.get("consensus", [])))
    with cols[3]:
        st.metric("Time", f"{result.get('total_time_s', 0)}s")
    
    baseline = result.get("single_model", {})
    if baseline:
        with st.expander("Single-Model Baseline", expanded=False):
            st.markdown(f"**Provider:** {baseline.get('provider')}")
            st.markdown(baseline.get("output", ""))
    
    with st.expander("Domain Positions", expanded=True):
        for r in domain_responses:
            if r.get("succeeded"):
                st.markdown(f"**D{r['domain_id']} {r['domain_name']}** ({r['provider']}, {r['latency_ms']}ms)")
                st.markdown(f"> {r['position'][:500]}")
                st.divider()
    
    if divergence.get("fault_lines"):
        with st.expander("Fault Lines", expanded=True):
            for fl in divergence["fault_lines"]:
                st.markdown(f"**{fl['topic']}**")
                for side in fl.get("sides", []):
                    domains_str = ", ".join(f"D{d}" for d in side.get("domains", []))
                    st.markdown(f"- {domains_str}: {side.get('stance', '')}")
                st.divider()
    
    if divergence.get("consensus"):
        with st.expander("Consensus Points"):
            for c in divergence["consensus"]:
                st.markdown(f"- {c}")
    
    synthesis = result.get("synthesis", {})
    if synthesis:
        st.markdown("### Synthesis")
        st.markdown(synthesis.get("output", ""))
        st.caption(f"Provider: {synthesis.get('provider')} | {synthesis.get('latency_ms', 0)}ms")
    
    kaya = result.get("kaya_events", [])
    if kaya:
        with st.expander(f"Kaya Moments ({len(kaya)})"):
            for k in kaya:
                st.json(k)


# ================================================================
# MODE: SCANNER
# ================================================================

def render_scanner():
    """Autonomous problem discovery and analysis."""
    
    st.markdown("### Scanner — Problem Discovery")
    st.markdown("""
    <div class="mode-desc">
    Enter a topic or let Elpida choose. The scanner uses D13 (Archive/Perplexity) to find current real-world problems,
    then optionally routes them through the Divergence Engine for multi-domain analysis.
    <br><br>
    <b>Example:</b> "EU AI regulation impact on startups" or "Greek public healthcare reform"
    </div>
    """, unsafe_allow_html=True)
    
    custom_topic = st.text_input(
        "Search topic (or leave blank for suggested topics)",
        placeholder="e.g., climate adaptation policies, AI ethics in education...",
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        from elpidaapp.scanner import SCAN_TOPICS
        if custom_topic:
            scan_topic = custom_topic
        else:
            scan_topic = st.selectbox("Or choose a topic", SCAN_TOPICS)
    with col2:
        problem_count = st.slider("Problems to find", 1, 5, 2)
    with col3:
        run_analysis = st.checkbox("Also run divergence analysis", value=True)
    
    if st.button("Scan", type="primary"):
        from elpidaapp.scanner import ProblemScanner
        scanner = ProblemScanner(llm=st.session_state.llm_client)
        
        if run_analysis:
            with st.spinner(f"Scanning '{scan_topic}' and analyzing..."):
                results = scanner.find_and_analyze(
                    topic=scan_topic,
                    count=problem_count,
                )
            
            st.success(f"Found and analyzed {len(results)} problems")
            for i, r in enumerate(results, 1):
                with st.expander(f"Problem {i}: {r.get('problem', '')[:80]}...", expanded=(i == 1)):
                    if "analysis" in r:
                        _show_analysis_result(r["analysis"])
                    else:
                        st.markdown(r.get("problem", ""))
        else:
            with st.spinner(f"Scanning '{scan_topic}'..."):
                problems = scanner.find_problems(topic=scan_topic, count=problem_count)
            
            st.success(f"Found {len(problems)} problems")
            for i, p in enumerate(problems, 1):
                st.markdown(f"**{i}.** {p}")


# ================================================================
# MODE: GOVERNANCE
# ================================================================

def render_governance():
    """Axiom enforcement and governance transparency."""
    
    st.markdown("### Governance — Axiom Enforcement")
    st.markdown("""
    <div class="mode-desc">
    Test if an action would violate Elpida's axioms. The governance layer checks against all 11 axioms
    and returns PROCEED, REVIEW, or HALT with reasoning.
    <br><br>
    <b>Example:</b> "Execute unverified code from an unknown source" -> HALT (A4: Harm Prevention)
    </div>
    """, unsafe_allow_html=True)
    
    action = st.text_input(
        "Describe an action to check",
        placeholder="e.g., Deploy model without bias testing...",
    )
    
    if st.button("Check Governance", type="primary", disabled=not action):
        from elpidaapp.governance_client import GovernanceClient
        gov = GovernanceClient()
        
        with st.spinner("Checking axiom compliance..."):
            result = gov.check_action(action)
        
        gov_status = result.get("governance", "UNKNOWN")
        if gov_status == "PROCEED":
            st.success(f"PROCEED — No axiom violations detected")
        elif gov_status == "REVIEW":
            st.warning(f"REVIEW — Potential axiom concerns")
        elif gov_status == "HALT":
            st.error(f"HALT — Axiom violations detected")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Violated Axioms:**")
            violated = result.get("violated_axioms", [])
            if violated:
                for ax in violated:
                    ax_info = AXIOMS.get(ax, {})
                    st.markdown(f"- **{ax}** ({ax_info.get('name', '')})")
            else:
                st.markdown("None")
        
        with col2:
            st.markdown("**Source:**")
            st.markdown(result.get("source", "unknown"))
            st.markdown("**Reasoning:**")
            st.markdown(result.get("reasoning", ""))
    
    st.divider()
    
    st.markdown("### Governance Layer Status")
    try:
        from elpidaapp.governance_client import GovernanceClient
        gov = GovernanceClient()
        status = gov.status()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            remote = status.get("remote_available", False)
            st.metric("Remote API", "Online" if remote else "Offline")
        with col2:
            st.metric("Source", status.get("source", "unknown"))
        with col3:
            st.metric("Cache Entries", status.get("cache_entries", 0))
        
        st.markdown(f"**URL:** `{status.get('governance_url', 'unknown')}`")
        st.markdown(f"**Frozen Identity Hash:** `{status.get('frozen_identity_hash', 'unknown')}`")
        
        gov_log = gov.get_governance_log()
        if gov_log:
            with st.expander(f"Governance Log ({len(gov_log)} entries)"):
                for entry in reversed(gov_log[-20:]):
                    st.markdown(
                        f"- `{entry.get('timestamp', '')[:19]}` "
                        f"**{entry.get('event', '')}** "
                        f"[{entry.get('source', '')}] "
                        f"{'OK' if entry.get('success') else 'FAIL'}"
                    )
    except Exception as e:
        st.error(f"Governance client error: {e}")


# ================================================================
# MODE: SYSTEM
# ================================================================

def render_system():
    """Constitution, axioms, domain map, providers, rhythms, stats."""
    
    st.markdown("### System — Constitution & Architecture")
    
    tab_axioms, tab_domains, tab_providers, tab_rhythms, tab_stats = st.tabs(
        ["11 Axioms", "15 Domains", "10 Providers", "5 Rhythms", "Statistics"]
    )
    
    with tab_axioms:
        st.markdown("#### The 11 Axioms of Elpida")
        st.markdown("*Each axiom has a musical ratio grounding it in harmonic mathematics.*")
        for ax_id, ax in sorted(AXIOMS.items(), key=lambda x: int(x[0][1:])):
            with st.expander(f"**{ax_id}** — {ax['name']} ({ax['ratio']} = {ax['interval']})"):
                st.markdown(f"**Frequency:** {ax['hz']} Hz")
                st.markdown(f"**Insight:** {ax['insight']}")
    
    with tab_domains:
        st.markdown("#### The 15 Domains")
        st.markdown("*Each domain embodies an axiom through a specific LLM provider.*")
        
        import pandas as pd
        domain_data = []
        for d_id, d in sorted(DOMAINS.items()):
            domain_data.append({
                "Domain": f"D{d_id}",
                "Name": d["name"],
                "Axiom": d.get("axiom", "—") or "—",
                "Provider": d.get("provider", "—"),
                "Role": d.get("role", "")[:60],
            })
        st.dataframe(pd.DataFrame(domain_data), use_container_width=True, hide_index=True)
        
        with st.expander("Domain Voices"):
            for d_id, d in sorted(DOMAINS.items()):
                if d.get("voice"):
                    st.markdown(f"**D{d_id} ({d['name']}):** *{d['voice']}*")
    
    with tab_providers:
        st.markdown("#### LLM Provider Map")
        
        from llm_client import COST_PER_TOKEN, DEFAULT_MODELS
        
        provider_data = []
        for provider, model in DEFAULT_MODELS.items():
            cost = COST_PER_TOKEN.get(provider, 0)
            domains_using = [f"D{d}" for d, info in DOMAINS.items() if info.get("provider") == provider]
            provider_data.append({
                "Provider": provider,
                "Model": model,
                "Cost/token": f"${cost}" if cost > 0 else "FREE",
                "Domains": ", ".join(domains_using) if domains_using else "—",
            })
        
        import pandas as pd
        st.dataframe(pd.DataFrame(provider_data), use_container_width=True, hide_index=True)
    
    with tab_rhythms:
        st.markdown("#### The 5 Rhythms")
        st.markdown("*Rhythms determine which domains activate for different cognitive modes.*")
        
        for name, domains_list in RHYTHM_DOMAINS.items():
            domain_names = [f"D{d}({DOMAINS[d]['name']})" for d in domains_list if d in DOMAINS]
            st.markdown(f"**{name}** — {', '.join(domain_names)}")
    
    with tab_stats:
        st.markdown("#### System Statistics")
        
        llm_stats = st.session_state.llm_client.get_stats()
        if isinstance(llm_stats, dict):
            st.markdown("**LLM Call Statistics:**")
            for provider, stats in llm_stats.items():
                if isinstance(stats, dict) and stats.get("calls", 0) > 0:
                    st.markdown(
                        f"- **{provider}**: {stats['calls']} calls, "
                        f"{stats.get('failures', 0)} failures, "
                        f"${stats.get('estimated_cost', 0):.4f} est. cost"
                    )
        
        chat_stats = st.session_state.chat_engine.get_stats()
        st.markdown("**Chat Statistics:**")
        st.json(chat_stats)


# ================================================================
# Main Router
# ================================================================

mode = st.session_state.mode

if mode == "Chat":
    render_chat()
elif mode == "Live Audit":
    render_live_audit()
elif mode == "Scanner":
    render_scanner()
elif mode == "Governance":
    render_governance()
elif mode == "System":
    render_system()
else:
    render_chat()
