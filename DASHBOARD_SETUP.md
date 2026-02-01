# ELPIDA DASHBOARD SETUP

## Installation

1. **Install Streamlit** (if not already installed):
   ```bash
   pip install streamlit psutil requests pandas
   ```

2. **Navigate to workspace**:
   ```bash
   cd /workspaces/python-elpida_core.py
   ```

3. **Run the dashboard**:
   ```bash
   streamlit run elpida_dashboard.py
   ```

4. **Access the dashboard**:
   - Local: http://localhost:8501
   - Codespace: Use the forwarded port

## Why It Can't Run in Snowflake

Your Snowflake error occurred because:

1. **`psutil` not available** - Snowflake's Python runtime doesn't include `psutil`
2. **No local process access** - Snowflake runs in cloud, can't see your local Brain API/Runtime
3. **No file system access** - Can't read local `elpida_memory.json`
4. **Wrong environment** - This is a local monitoring tool, not a cloud analytics query

## What This Dashboard Does

✅ **Real-time Monitoring:**
- Process status (CPU, MEM, uptime)
- Brain API health
- Memory growth tracking
- Queue activity
- Live event feed

✅ **Phase 12.3 Specific:**
- Mutual recognition event count
- Relational validation status
- Deployment version tracking

✅ **Interactive:**
- Submit test jobs
- Auto-refresh every 2 seconds
- Clean HUD-style interface

## Alternative: If You Need Cloud Monitoring

If you want monitoring accessible from anywhere (not just locally):

### Option 1: Deploy Streamlit to Streamlit Cloud
```bash
# Push dashboard to GitHub
# Deploy on streamlit.io (free)
# Won't work without exposing Brain API publicly
```

### Option 2: Log Metrics to Snowflake
Create a separate script that:
1. Reads Elpida metrics locally
2. Pushes to Snowflake table every N seconds
3. Build Snowflake dashboard from that table

### Option 3: Use Existing Monitoring Script
```bash
# Simple terminal-based monitoring (no Snowflake needed)
./monitor.sh
```

## Troubleshooting

**Port already in use:**
```bash
# Kill existing Streamlit
pkill -f streamlit
streamlit run elpida_dashboard.py
```

**Can't access in Codespace:**
1. Check Ports tab in VS Code
2. Forward port 8501
3. Access via forwarded URL

**Brain API not responding:**
- Check Brain API is running: `ps aux | grep brain_api_server`
- Restart if needed: `python3 brain_api_server.py &`

## Quick Commands

```bash
# Start dashboard
streamlit run elpida_dashboard.py

# Start in background
nohup streamlit run elpida_dashboard.py &

# Stop dashboard
pkill -f streamlit

# View in browser (local)
xdg-open http://localhost:8501  # Linux
open http://localhost:8501      # Mac
```

---

**Note**: This is a **local development tool**. For production monitoring, consider proper observability platforms (Grafana, Datadog, etc.).
