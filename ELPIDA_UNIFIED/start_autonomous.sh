#!/bin/bash
#
# ELPIDA AUTONOMOUS STARTUP SCRIPT
# ---------------------------------
# Restarts the autonomous refinement loop after Codespace restart
#

cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                       ║"
echo "║                    Ἐλπίδα AUTONOMOUS STARTUP                          ║"
echo "║                                                                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if already running
if pgrep -f "autonomous_refinement_loop.py" > /dev/null; then
    echo "⚠️  Autonomous loop already running:"
    ps aux | grep autonomous_refinement_loop | grep -v grep
    echo ""
    echo "To stop: pkill -f autonomous_refinement_loop.py"
    echo "To view logs: tail -f /workspaces/python-elpida_core.py/ELPIDA_UNIFIED/autonomous.log"
    exit 0
fi

# Check system health first
echo "🔍 Checking system health..."
python3 system_doctor.py
if [ $? -ne 0 ]; then
    echo "⚠️  System health check found issues. Run 'python3 system_doctor.py' manually."
fi
echo ""

# Start autonomous loop in background
echo "🚀 Starting autonomous refinement loop..."
echo "   Interval: 300 seconds (5 minutes per cycle)"
echo "   Mode: Infinite (runs forever)"
echo ""

nohup python3 autonomous_refinement_loop.py --interval 300 > autonomous.log 2>&1 &
LOOP_PID=$!

sleep 2

# Verify it started
if ps -p $LOOP_PID > /dev/null; then
    echo "✅ Autonomous loop started successfully"
    echo "   PID: $LOOP_PID"
    echo ""
    echo "Commands:"
    echo "  • View logs:    tail -f autonomous.log"
    echo "  • Check status: python3 control_center.py status"
    echo "  • Stop:         pkill -f autonomous_refinement_loop.py"
    echo ""
    echo "The ARK will now refine itself autonomously every 5 minutes."
    echo "Safe to close Codespace - loop will continue in background."
else
    echo "❌ Failed to start autonomous loop"
    echo "   Check autonomous.log for errors"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "                    Ἐλπίδα v4.0.1+ALL_APIS"
echo "              Autonomous Self-Improving Immortality"
echo "═══════════════════════════════════════════════════════════════════════"
