#!/bin/bash
# STOP COMPLETE SYSTEM
# Gracefully stops all Elpida components

WORKSPACE="/workspaces/python-elpida_core.py/ELPIDA_UNIFIED"
cd "$WORKSPACE"

echo "🛑 Stopping Complete Elpida System..."
echo ""

# Kill processes by PID files
for pid_file in brain_api.pid unified_runtime.pid autonomous_dilemmas.pid fleet_debate.pid emergence.pid ai_bridge.pid world_feed.pid corruption_guard.pid; do
    if [ -f "$pid_file" ]; then
        PID=$(cat "$pid_file")
        PROCESS_NAME=$(basename "$pid_file" .pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "   Stopping $PROCESS_NAME (PID: $PID)..."
            kill $PID 2>/dev/null || true
        fi
        rm "$pid_file"
    fi
done

# Fallback: kill by process name
pkill -f "brain_api_server.py" 2>/dev/null || true
pkill -f "elpida_unified_runtime.py" 2>/dev/null || true
pkill -f "autonomous_dilemmas.py" 2>/dev/null || true
pkill -f "parliament_continuous.py" 2>/dev/null || true
pkill -f "emergence_monitor.py" 2>/dev/null || true
pkill -f "multi_ai_connector.py" 2>/dev/null || true
pkill -f "world_intelligence_feed.py" 2>/dev/null || true
pkill -f "corruption_guard.py" 2>/dev/null || true

sleep 2

echo ""
echo "✅ All systems stopped"
echo ""

# Show final state
if [ -f "elpida_unified_state.json" ]; then
    echo "📊 FINAL STATE:"
    python3 -c 'import json; s=json.load(open("elpida_unified_state.json")); print(f"   Patterns: {s.get(\"patterns_count\", 0)}"); print(f"   Breakthroughs: {s.get(\"synthesis_breakthroughs\", 0)}"); print(f"   Insights: {s.get(\"insights_count\", 0)}")'
    echo ""
fi

echo "💾 Logs preserved in:"
echo "   - brain_api.log"
echo "   - unified_runtime.log"
echo "   - autonomous_dilemmas.log"
echo "   - fleet_debate.log"
echo "   - emergence.log (EEE - emergent behaviors)"
echo "   - ai_bridge.log (external AI responses)"
echo "   - world_feed.log (if Perplexity was active)"
echo ""
