"""
ELPIDA LIVE COMMAND CENTER
Real-time monitoring dashboard for Phase 12.3: Mutual Recognition

Run locally with: streamlit run elpida_dashboard.py
"""

import streamlit as st
import time
import pandas as pd
import psutil
import requests
import json
import os
from datetime import datetime
from pathlib import Path

# -----------------------------------------------------------------------------
# CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Elpida Live Command",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - HUD styling
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .metric-card {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #4CAF50;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        }
        
        .status-badge-live {
            background-color: #FF4B4B;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.8em;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .stProgress > div > div > div > div {
            background-color: #4CAF50;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# DATA FETCHING FUNCTIONS
# -----------------------------------------------------------------------------
WORKSPACE_DIR = Path("/workspaces/python-elpida_core.py/ELPIDA_UNIFIED")
MEMORY_FILE = WORKSPACE_DIR / "elpida_memory.json"

@st.cache_data(ttl=1)
def get_process_status(process_name):
    """Find and return status of a process by name"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
            if process_name in cmdline or process_name in proc.info['name']:
                uptime = int(time.time() - proc.info['create_time'])
                hours = uptime // 3600
                minutes = (uptime % 3600) // 60
                
                return {
                    "status": "ONLINE",
                    "cpu": proc.info['cpu_percent'],
                    "mem": proc.info['memory_percent'],
                    "pid": proc.info['pid'],
                    "uptime": f"{hours}h {minutes}m"
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return {"status": "OFFLINE", "cpu": 0, "mem": 0, "pid": None, "uptime": "N/A"}

@st.cache_data(ttl=1)
def get_brain_health():
    """Fetch Brain API health status"""
    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@st.cache_data(ttl=1)
def get_brain_status():
    """Fetch full Brain API status"""
    try:
        response = requests.get("http://localhost:5000/status", timeout=2)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

@st.cache_data(ttl=2)
def get_memory_stats():
    """Load and analyze memory events"""
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, 'r') as f:
                data = json.load(f)
                events = data.get('events', [])
                
                # Count event types
                mutual_rec = sum(1 for e in events if e.get('type') == 'MUTUAL_RECOGNITION')
                heartbeats = sum(1 for e in events if e.get('type') == 'HEARTBEAT')
                
                return {
                    'total': len(events),
                    'mutual_recognition': mutual_rec,
                    'heartbeats': heartbeats,
                    'recent': events[-10:] if len(events) > 10 else events
                }
        except Exception as e:
            st.error(f"Memory file error: {e}")
            return None
    return None

@st.cache_data(ttl=5)
def get_git_info():
    """Get current git status"""
    try:
        import subprocess
        commit = subprocess.run(
            ['git', 'log', '-1', '--oneline'],
            capture_output=True, text=True, cwd=WORKSPACE_DIR.parent
        ).stdout.strip()[:60]
        
        tag = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True, text=True, cwd=WORKSPACE_DIR.parent
        ).stdout.strip()
        
        branch = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True, cwd=WORKSPACE_DIR.parent
        ).stdout.strip()
        
        return {"commit": commit, "tag": tag, "branch": branch}
    except:
        return {"commit": "N/A", "tag": "N/A", "branch": "N/A"}

# -----------------------------------------------------------------------------
# DASHBOARD LAYOUT
# -----------------------------------------------------------------------------

# HEADER
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("## ⚡ ELPIDA **LIVE COMMAND CENTER**")
    st.caption("Phase 12.3: Mutual Recognition | Unified Runtime | Real-time Monitoring")
with col2:
    st.markdown(
        "<div style='text-align: right;'><span class='status-badge-live'>● LIVE</span></div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='text-align: right;'>{datetime.now().strftime('%H:%M:%S')}</div>",
        unsafe_allow_html=True
    )

st.markdown("---")

# FETCH DATA
brain_proc = get_process_status("brain_api_server.py")
runtime_proc = get_process_status("elpida_unified_runtime.py")
brain_health = get_brain_health()
brain_status = get_brain_status()
memory_stats = get_memory_stats()
git_info = get_git_info()

# -----------------------------------------------------------------------------
# 1. SCOREBOARD (Top Row Metrics)
# -----------------------------------------------------------------------------
m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    status_color = "🟢" if brain_proc['status'] == "ONLINE" else "🔴"
    st.metric(
        "Brain Server",
        f"{status_color} {brain_proc['status']}",
        delta=f"PID {brain_proc['pid']}" if brain_proc['pid'] else "Offline"
    )

with m2:
    mutual_count = memory_stats['mutual_recognition'] if memory_stats else 0
    st.metric(
        "🤝 Mutual Recognition",
        mutual_count,
        delta="Phase 12.3 Events"
    )

with m3:
    queue_depth = brain_health.get('queue_depth', 0) if brain_health else 0
    processed = brain_status['queue']['processed_total'] if brain_status else 0
    st.metric(
        "Job Queue",
        queue_depth,
        delta=f"{processed} processed"
    )

with m4:
    total_mem = memory_stats['total'] if memory_stats else 0
    st.metric(
        "Memory Events",
        f"{total_mem:,}",
        delta="A2 Compliant"
    )

with m5:
    runtime_color = "🟢" if runtime_proc['status'] == "ONLINE" else "🔴"
    st.metric(
        "Runtime Core",
        f"{runtime_color} {runtime_proc['status']}",
        delta=runtime_proc['uptime']
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 2. MAIN DASHBOARD (Three Columns)
# -----------------------------------------------------------------------------
c1, c2, c3 = st.columns([1, 2, 1])

# LEFT COLUMN: System Vitals
with c1:
    st.subheader("🔧 System Vitals")
    
    # Brain API
    st.write("**🧠 Brain API Server**")
    if brain_proc['status'] == "ONLINE":
        cpu_val = min(brain_proc['cpu'] / 100.0, 1.0)
        st.progress(cpu_val)
        st.caption(f"CPU: {brain_proc['cpu']:.1f}% | MEM: {brain_proc['mem']:.1f}% | PID: {brain_proc['pid']}")
        st.caption(f"Uptime: {brain_proc['uptime']}")
    else:
        st.error("❌ Offline")
    
    st.markdown("---")
    
    # Runtime Core
    st.write("**⚙️ Runtime Core**")
    if runtime_proc['status'] == "ONLINE":
        cpu_val = min(runtime_proc['cpu'] / 100.0, 1.0)
        st.progress(cpu_val)
        st.caption(f"CPU: {runtime_proc['cpu']:.1f}% | MEM: {runtime_proc['mem']:.1f}% | PID: {runtime_proc['pid']}")
        st.caption(f"Uptime: {runtime_proc['uptime']}")
    else:
        st.error("❌ Offline")
    
    st.markdown("---")
    
    # Brain API Mode
    if brain_health:
        st.success(f"✅ API Mode: **{brain_health.get('mode', 'Unknown')}**")
        st.caption(f"Version: {brain_health.get('version', 'N/A')}")
    else:
        st.error("❌ API Connection Lost")

# MIDDLE COLUMN: Live Feed
with c2:
    st.subheader("📡 Live Event Feed")
    
    if memory_stats and memory_stats['recent']:
        feed_data = []
        for e in reversed(memory_stats['recent']):
            timestamp = e.get('timestamp', 'N/A')
            time_str = timestamp[11:19] if len(timestamp) > 19 else timestamp
            
            event_type = e.get('type', 'UNKNOWN')
            desc = e.get('description', e.get('event_type', ''))[:80]
            
            # Color code by type
            if event_type == 'MUTUAL_RECOGNITION':
                icon = "🤝"
            elif event_type == 'HEARTBEAT':
                icon = "💓"
            elif 'evolution' in event_type.lower():
                icon = "🧬"
            else:
                icon = "⚡"
            
            feed_data.append({
                "Time": time_str,
                "Type": f"{icon} {event_type}",
                "Detail": desc
            })
        
        df = pd.DataFrame(feed_data)
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            height=400
        )
    else:
        st.info("⏳ Waiting for event stream...")
    
    # Heartbeat indicator
    if memory_stats:
        heartbeat_count = memory_stats['heartbeats']
        st.caption(f"💓 Total Heartbeats: {heartbeat_count:,}")

# RIGHT COLUMN: Deployment Info
with c3:
    st.subheader("📦 Deployment")
    
    st.write(f"**Tag:** {git_info['tag']}")
    st.write(f"**Branch:** {git_info['branch'][:30]}")
    st.caption(f"Commit: {git_info['commit']}")
    
    st.markdown("---")
    
    st.subheader("📊 Statistics")
    
    if brain_status:
        st.metric("Jobs Processed", brain_status['queue']['processed_total'])
        st.metric("Queue Depth", brain_status['queue']['depth'])
    
    if memory_stats:
        st.metric("Total Events", f"{memory_stats['total']:,}")
        st.metric("Heartbeats", f"{memory_stats['heartbeats']:,}")
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    
    if st.button("🔄 Submit Test Job"):
        try:
            response = requests.post(
                "http://localhost:5000/scan",
                json={"text": "Dashboard test job", "priority": 9},
                timeout=2
            )
            if response.status_code == 200:
                st.success("✅ Job submitted!")
            else:
                st.error("❌ Submit failed")
        except Exception as e:
            st.error(f"Error: {e}")
    
    if st.button("🧪 Run Integration Tests"):
        st.info("Tests would run in separate terminal")

# -----------------------------------------------------------------------------
# FOOTER STATUS BAR
# -----------------------------------------------------------------------------
st.markdown("---")
footer_cols = st.columns([2, 1, 1, 1])

with footer_cols[0]:
    if brain_proc['status'] == "ONLINE" and runtime_proc['status'] == "ONLINE":
        st.success("✅ All Systems Operational")
    else:
        st.error("⚠️ System Issues Detected")

with footer_cols[1]:
    st.caption("🤝 Mutual Recognition: **ACTIVE**")

with footer_cols[2]:
    st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d')}")

with footer_cols[3]:
    st.caption("Auto-refresh: 2s")

# -----------------------------------------------------------------------------
# AUTO-REFRESH
# -----------------------------------------------------------------------------
time.sleep(2)
st.rerun()
