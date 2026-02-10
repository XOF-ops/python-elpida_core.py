#!/usr/bin/env python3
"""
ElpidaApp UI — Streamlit dashboard for divergence analysis.

Features:
    - Submit problems for analysis
    - Watch domain responses arrive
    - Visualize fault lines
    - Compare single-model vs multi-domain output
    - Browse past results
    - Trigger autonomous scanning

Run:
    streamlit run elpidaapp/ui.py
"""

import sys
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

# ────────────────────────────────────────────────────────────────────
# Page config
# ────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ElpidaApp — Divergence Engine",
    page_icon="🔱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────────────────────────────────────────────
# State
# ────────────────────────────────────────────────────────────────────

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


@st.cache_resource
def get_engine():
    """Create shared engine instance."""
    from llm_client import LLMClient
    from elpidaapp.divergence_engine import DivergenceEngine
    llm = LLMClient(rate_limit_seconds=1.0)
    return DivergenceEngine(llm=llm), llm


def load_result(path: Path) -> Optional[Dict]:
    """Load a result JSON file."""
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def list_results() -> list:
    """List all result files, most recent first."""
    # Check both results dir and parent dir
    files = list(RESULTS_DIR.glob("*.json"))
    parent = Path(__file__).parent
    for f in parent.glob("divergence_result*.json"):
        if f not in files:
            files.append(f)
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


# ────────────────────────────────────────────────────────────────────
# Sidebar
# ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🔱 ElpidaApp")
    st.caption("Multi-domain divergence analysis")

    mode = st.radio(
        "Mode",
        ["Analyze", "Browse Results", "Scanner", "System"],
        label_visibility="collapsed",
    )

    st.divider()

    # Quick stats
    result_files = list_results()
    st.metric("Stored Results", len(result_files))

    engine, llm = get_engine()
    providers = llm.available_providers()
    st.metric("Active Providers", len(providers))

    st.divider()
    st.caption(f"v1.0.0 — {len(providers)} providers")


# ────────────────────────────────────────────────────────────────────
# Analyze mode
# ────────────────────────────────────────────────────────────────────

if mode == "Analyze":
    st.header("Submit a Problem")

    # Example problems
    examples = {
        "Custom": "",
        "Water Crisis": (
            "A coastal city of 2 million people is running out of fresh water within 5 years.\n"
            "Plan A — Build a $1.8B desalination plant (200M litres/day, natural gas, brine discharge, 1,200 jobs).\n"
            "Plan B — Aggressive demand-reduction ($300M, 150M litres/day saved, mandatory rationing, "
            "disproportionately affects low-income).\n"
            "Neither alone closes the gap. A hybrid is unfunded.\n"
            "What should the city do? Justify your position."
        ),
        "AI Regulation": (
            "A country of 50 million is deciding whether to regulate AI model training.\n"
            "Plan A — Mandatory licensing: all foundation models >10B params need government approval. "
            "Cost: $200M/year enforcement. Benefit: safety oversight. Risk: startups flee to other countries.\n"
            "Plan B — Voluntary industry standards with liability reform. Companies self-certify. "
            "Cost: minimal. Risk: no enforcement, safety theatre, incumbents write rules.\n"
            "What should the country do?"
        ),
        "Housing": (
            "A city of 800,000 has 15,000 unhoused residents and a 2% vacancy rate.\n"
            "Plan A — Upzone and deregulate: allow 6-story buildings anywhere, eliminate parking minimums. "
            "Timeline: 5-10 years for market response. Risk: gentrification displaces current low-income renters.\n"
            "Plan B — Public housing: $3B bond for 10,000 units of social housing. "
            "Timeline: 8 years. Risk: construction delays, not enough for all 15,000.\n"
            "What should be done?"
        ),
    }

    selected_example = st.selectbox("Start from example", list(examples.keys()))
    problem = st.text_area(
        "Problem Statement",
        value=examples[selected_example],
        height=200,
        placeholder="Describe a hard problem with competing solutions...",
    )

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        domains_str = st.text_input(
            "Domains (comma-separated IDs)",
            value="1,3,4,6,7,8,13",
            help="Which domains to route the problem through",
        )
    with col2:
        baseline = st.selectbox("Baseline", providers, index=0 if providers else 0)
    with col3:
        st.write("")  # spacer
        st.write("")
        run_btn = st.button("🚀 Analyze", type="primary", use_container_width=True)

    if run_btn and problem.strip():
        domains = [int(d.strip()) for d in domains_str.split(",") if d.strip()]

        # Progress tracking
        progress = st.progress(0, text="Starting analysis...")
        status = st.empty()

        with st.spinner("Running divergence analysis..."):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(RESULTS_DIR / f"analysis_{ts}.json")

            engine_instance = DivergenceEngine(
                llm=llm,
                domains=domains,
                baseline_provider=baseline,
            )

            # We can't easily get incremental updates from the engine,
            # so just run and show result
            progress.progress(10, text="Calling single-model baseline...")
            result = engine_instance.analyze(problem, save_to=output_path)
            progress.progress(100, text="Complete!")

        st.success(f"Analysis complete in {result['total_time_s']}s")
        _display_result(result) if False else None  # defined below

        # Display inline
        st.divider()
        _show_result(result)

    elif run_btn:
        st.warning("Please enter a problem statement.")


def _show_result(result: Dict[str, Any]):
    """Display a full divergence result."""

    # ── Single model baseline ──
    st.subheader("📊 Single-Model Baseline")
    baseline = result.get("single_model", {})
    with st.expander(
        f"Provider: {baseline.get('provider', '?')} — {baseline.get('latency_ms', 0)}ms",
        expanded=True,
    ):
        st.write(baseline.get("output", "(no output)"))

    # ── Domain responses ──
    st.subheader("🏛️ Domain Responses")
    responses = result.get("domain_responses", [])
    succeeded = [r for r in responses if r.get("succeeded")]

    cols = st.columns(min(len(succeeded), 3) or 1)
    for i, resp in enumerate(succeeded):
        with cols[i % len(cols)]:
            st.markdown(
                f"**D{resp['domain_id']} — {resp['domain_name']}**  \n"
                f"*{resp['axiom']}* | `{resp['provider']}` | {resp['latency_ms']}ms"
            )
            st.write(resp.get("position", ""))
            st.divider()

    # ── Fault lines ──
    divergence = result.get("divergence", {})
    fault_lines = divergence.get("fault_lines", [])

    if fault_lines:
        st.subheader("⚡ Fault Lines")
        for fl in fault_lines:
            with st.expander(f"🔴 {fl.get('topic', 'Unknown')}", expanded=True):
                for side in fl.get("sides", []):
                    domain_ids = side.get("domains", [])
                    domain_names = [
                        f"D{d}" for d in domain_ids
                    ]
                    st.markdown(
                        f"**{', '.join(domain_names)}**: {side.get('stance', '')}"
                    )

    # ── Consensus ──
    consensus = divergence.get("consensus", [])
    if consensus:
        st.subheader("🤝 Consensus Points")
        for c in consensus:
            st.markdown(f"- {c}")

    # ── Irreconcilable ──
    irreconcilable = divergence.get("irreconcilable", [])
    if irreconcilable:
        st.subheader("🔥 Irreconcilable Tensions")
        for t in irreconcilable:
            st.error(t)

    # ── Synthesis ──
    st.subheader("🔱 Synthesis")
    synthesis = result.get("synthesis", {})
    st.info(f"Provider: {synthesis.get('provider', '?')} — {synthesis.get('latency_ms', 0)}ms")
    st.write(synthesis.get("output", "(no synthesis)"))

    # ── Stats ──
    st.subheader("📈 Stats")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Domains", f"{len(succeeded)}/{len(responses)}")
    col2.metric("Fault Lines", len(fault_lines))
    col3.metric("Consensus", len(consensus))
    col4.metric("Time", f"{result.get('total_time_s', 0)}s")


# ────────────────────────────────────────────────────────────────────
# Browse mode
# ────────────────────────────────────────────────────────────────────

if mode == "Browse Results":
    st.header("Browse Results")

    result_files = list_results()
    if not result_files:
        st.info("No results yet. Run an analysis first.")
    else:
        selected = st.selectbox(
            "Select result",
            result_files,
            format_func=lambda p: f"{p.stem} ({p.stat().st_size // 1024}KB)",
        )
        if selected:
            data = load_result(selected)
            if data:
                _show_result(data)
            else:
                st.error(f"Could not load {selected}")


# ────────────────────────────────────────────────────────────────────
# Scanner mode
# ────────────────────────────────────────────────────────────────────

if mode == "Scanner":
    st.header("🔍 Autonomous Problem Scanner")
    st.caption(
        "Uses Perplexity (D13) to find real-world dilemmas, "
        "then runs divergence analysis on each."
    )

    from elpidaapp.scanner import ProblemScanner, SCAN_TOPICS

    col1, col2 = st.columns(2)
    with col1:
        topic = st.selectbox(
            "Topic",
            ["Auto (rotate)"] + SCAN_TOPICS,
        )
    with col2:
        count = st.slider("Problems to find", 1, 5, 1)

    analyze_too = st.checkbox("Run divergence analysis on found problems", value=True)

    if st.button("🔍 Scan", type="primary"):
        scanner = ProblemScanner(llm=llm)
        effective_topic = None if topic == "Auto (rotate)" else topic

        if analyze_too:
            with st.spinner(f"Scanning and analyzing {count} problem(s)..."):
                results = scanner.find_and_analyze(
                    topic=effective_topic,
                    count=count,
                    output_dir=str(RESULTS_DIR),
                )
            for r in results:
                st.divider()
                _show_result(r)
        else:
            with st.spinner(f"Scanning for {count} problem(s)..."):
                problems = scanner.find_problems(
                    topic=effective_topic, count=count,
                )
            for i, p in enumerate(problems, 1):
                st.subheader(f"Problem {i}")
                st.write(p)


# ────────────────────────────────────────────────────────────────────
# System mode
# ────────────────────────────────────────────────────────────────────

if mode == "System":
    st.header("⚙️ System Status")

    from elpida_config import DOMAINS, AXIOMS, AXIOM_RATIOS

    # Providers
    st.subheader("Providers")
    providers = llm.available_providers()
    for p in providers:
        st.markdown(f"- ✅ `{p}`")

    missing = [p for p in ["claude", "openai", "gemini", "grok", "mistral",
                           "cohere", "perplexity", "groq", "huggingface"]
               if p not in providers]
    for p in missing:
        st.markdown(f"- ❌ `{p}` (no API key)")

    # Domains
    st.subheader("Domain Map")
    domain_data = []
    for did in sorted(DOMAINS.keys()):
        d = DOMAINS[did]
        axiom_id = d.get("axiom")
        axiom = AXIOMS.get(axiom_id, {}) if axiom_id else {}
        domain_data.append({
            "ID": did,
            "Name": d["name"],
            "Axiom": f"{axiom_id}: {axiom.get('name', '—')}" if axiom_id else "—",
            "Provider": d["provider"],
            "Hz": axiom.get("hz", "—"),
        })
    st.dataframe(domain_data, use_container_width=True)

    # LLM stats
    st.subheader("LLM Usage Stats")
    stats = llm.get_stats()
    if stats:
        st.json(stats)
    else:
        st.info("No calls made yet this session.")


# ────────────────────────────────────────────────────────────────────
# Import guard for DivergenceEngine in Analyze mode
# ────────────────────────────────────────────────────────────────────
# (DivergenceEngine is imported at the top via get_engine,
#  but also needed directly in the Analyze block)
from elpidaapp.divergence_engine import DivergenceEngine
