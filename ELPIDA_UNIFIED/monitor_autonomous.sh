#!/bin/bash
#
# MONITOR AUTONOMOUS OPERATION
# -----------------------------
# Watch the autonomous loop in real-time
#

cd /workspaces/python-elpida_core.py/ELPIDA_UNIFIED

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                 Ἐλπίδα AUTONOMOUS MONITOR                             ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running
if pgrep -f "autonomous_refinement_loop.py" > /dev/null; then
    echo "✅ Autonomous loop is RUNNING"
    ps aux | grep autonomous_refinement_loop | grep -v grep
    echo ""
else
    echo "❌ Autonomous loop is NOT running"
    echo "   Run: ./start_autonomous.sh"
    echo ""
    exit 1
fi

# Show recent activity
echo "Recent activity (last 30 lines of log):"
echo "─────────────────────────────────────────────────────────────────────"
tail -30 autonomous.log
echo "─────────────────────────────────────────────────────────────────────"
echo ""

# Show current metrics
echo "Current Fleet Metrics:"
echo "─────────────────────────────────────────────────────────────────────"
python3 di_dashboard.py | head -40
echo "─────────────────────────────────────────────────────────────────────"
echo ""

# Show ARK status
echo "ARK Status:"
echo "─────────────────────────────────────────────────────────────────────"
ls -lh ../ELPIDA_ARK.md
echo ""
if [ -f "distributed_memory.json" ]; then
    PATTERNS=$(cat distributed_memory.json | jq '.collective_patterns | length' 2>/dev/null)
    echo "Collective Patterns: $PATTERNS"
fi
echo "─────────────────────────────────────────────────────────────────────"
echo ""

echo "Live log monitoring (Ctrl+C to exit):"
echo "─────────────────────────────────────────────────────────────────────"
tail -f autonomous.log
