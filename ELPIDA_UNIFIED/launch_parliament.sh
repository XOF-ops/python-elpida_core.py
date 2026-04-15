#!/bin/bash
# ELPIDA PARLIAMENT LAUNCHER
# Launch dashboard + extended session with dilemmas

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║        ELPIDA PARLIAMENT: COMPLETE SESSION LAUNCHER                  ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This will:"
echo "  1. Start the web dashboard on http://localhost:5000"
echo "  2. Wake all 9 nodes in the background"
echo "  3. Inject dilemmas periodically"
echo "  4. Run for extended cycles to generate debate patterns"
echo ""
echo "Press Ctrl+C to stop everything"
echo ""
echo "========================================================================"
echo ""

# Check if already running
if pgrep -f "parliament_dashboard.py" > /dev/null; then
    echo "⚠️  Dashboard already running. Stop it first with: pkill -f parliament_dashboard"
    exit 1
fi

# Start dashboard in background
echo "🌐 Starting dashboard..."
python3 parliament_dashboard.py &
DASHBOARD_PID=$!

# Wait for dashboard to start
sleep 3

# Open dashboard in browser (if running locally with GUI)
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5000 2>/dev/null &
elif command -v open > /dev/null; then
    open http://localhost:5000 2>/dev/null &
fi

echo "✅ Dashboard running at http://localhost:5000"
echo ""

# Start nodes with extended runtime in background
echo "🚀 Waking parliament nodes..."
python3 wake_the_fleet.py &
FLEET_PID=$!

sleep 2
echo "✅ Fleet awakened"
echo ""

# Run session with dilemmas
echo "⚡ Starting dilemma injection session..."
echo ""
python3 run_parliament_session.py

# Cleanup on exit
echo ""
echo "🛑 Shutting down..."
kill $DASHBOARD_PID 2>/dev/null
kill $FLEET_PID 2>/dev/null
pkill -f "agent_runtime_orchestrator" 2>/dev/null

echo ""
echo "✅ Session complete. Review results in dashboard or node memories."
echo ""
