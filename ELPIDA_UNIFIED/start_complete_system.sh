#!/bin/bash
# COMPLETE SYSTEM STARTUP
# Starts ALL components: Elpida, Brain API, Unified Runtime, Fleet, Autonomous Dilemmas
# This ensures continuous progress with all systems working together

set -e

WORKSPACE="/workspaces/python-elpida_core.py/ELPIDA_UNIFIED"
cd "$WORKSPACE"

# Load environment variables from .env file
if [ -f ".env" ]; then
    echo "📄 Loading environment variables from .env..."
    export $(grep -v '^#' .env | xargs)
    echo "✅ API keys loaded"
    echo ""
fi

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║           STARTING COMPLETE ELPIDA SYSTEM                            ║"
echo "║  Elpida + Master_Brain + EEE + POLIS + Fleet - ALL AUTONOMOUS        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Kill any existing processes to start fresh
echo "🧹 Cleaning up old processes..."
pkill -f "brain_api_server.py" 2>/dev/null || true
pkill -f "elpida_unified_runtime.py" 2>/dev/null || true
pkill -f "autonomous_dilemmas.py" 2>/dev/null || true
pkill -f "parliament_continuous.py" 2>/dev/null || true
pkill -f "emergence_monitor.py" 2>/dev/null || true
pkill -f "multi_ai_connector.py" 2>/dev/null || true
pkill -f "world_intelligence_feed.py" 2>/dev/null || true
sleep 2

# Check current state
echo ""
echo "📊 CURRENT STATE:"
if [ -f "elpida_wisdom.json" ]; then
    PATTERNS=$(python3 -c "import json; print(len(json.load(open('elpida_wisdom.json')).get('patterns', {})))")
    INSIGHTS=$(python3 -c "import json; print(len(json.load(open('elpida_wisdom.json')).get('insights', {})))")
    echo "   Patterns: $PATTERNS"
    echo "   Insights: $INSIGHTS"
fi

if [ -f "elpida_unified_state.json" ]; then
    BREAKTHROUGHS=$(python3 -c "import json; print(json.load(open('elpida_unified_state.json')).get('synthesis_breakthroughs', 0))")
    echo "   Synthesis Breakthroughs: $BREAKTHROUGHS"
fi

if [ -f "fleet_dialogue.jsonl" ]; then
    FLEET_MSGS=$(wc -l < fleet_dialogue.jsonl)
    echo "   Fleet Messages: $FLEET_MSGS"
fi

echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo ""

# 1. Start Brain API Server
echo "🧠 [1/4] Starting Brain API Server (localhost:5000)..."
nohup python3 brain_api_server.py > brain_api.log 2>&1 &
BRAIN_PID=$!
echo $BRAIN_PID > brain_api.pid
echo "   ✅ Brain API started (PID: $BRAIN_PID)"
sleep 2

# Verify Brain API is responsive
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "   ✅ Brain API responding on http://localhost:5000"
else
    echo "   ❌ Brain API not responding - check brain_api.log"
    exit 1
fi

# 2. Start Unified Runtime (Brain + Elpida + Synthesis)
echo ""
echo "⚡ [2/4] Starting Unified Runtime (Dialectical Engine)..."
nohup python3 elpida_unified_runtime.py > unified_runtime.log 2>&1 &
UNIFIED_PID=$!
echo $UNIFIED_PID > unified_runtime.pid
echo "   ✅ Unified Runtime started (PID: $UNIFIED_PID)"
echo "   ℹ️  Processing: Brain API jobs, Synthesis, Axiom validation"
sleep 3

# 3. Start Autonomous Dilemma Generator (creates new ethical challenges)
echo ""
echo "🎲 [3/4] Starting Autonomous Dilemma Generator..."
nohup python3 autonomous_dilemmas.py > autonomous_dilemmas.log 2>&1 &
DILEMMAS_PID=$!
echo $DILEMMAS_PID > autonomous_dilemmas.pid
echo "   ✅ Dilemma Generator started (PID: $DILEMMAS_PID)"
echo "   ℹ️  Generating ethical dilemmas for parliament every 60s"
sleep 2

# 4. Start Parliament Debate Loop (9-node council)
echo ""
echo "🏛️  [4/6] Starting Parliament Debate System..."
nohup python3 parliament_continuous.py --interval 60 > fleet_debate.log 2>&1 &
FLEET_PID=$!
echo $FLEET_PID > fleet_debate.pid
echo "   ✅ Parliament started (PID: $FLEET_PID)"
echo "   ℹ️  9 nodes debating dilemmas, voting, crystallizing memories"
sleep 2

# 5. Start Emergence Monitor (EEE - tracks emergent properties)
echo ""
echo "🔬 [5/9] Starting Emergence Engine (EEE)..."
nohup python3 emergence_monitor.py --interval 60 > emergence.log 2>&1 &
EEE_PID=$!
echo $EEE_PID > emergence.pid
echo "   ✅ Emergence Engine started (PID: $EEE_PID)"
echo "   ℹ️  Monitoring for unexpected behaviors, novel patterns every 60s"
sleep 2

# 6. Start Multi-AI Connector (asks external AI about dilemmas)
echo ""
# Check if any external AI API keys are set
AI_KEYS_SET=""
[ -n "$OPENAI_API_KEY" ] && AI_KEYS_SET="${AI_KEYS_SET}GPT "
[ -n "$ANTHROPIC_API_KEY" ] && AI_KEYS_SET="${AI_KEYS_SET}Claude "
[ -n "$GOOGLE_API_KEY" ] && AI_KEYS_SET="${AI_KEYS_SET}Gemini "
[ -n "$XAI_API_KEY" ] && AI_KEYS_SET="${AI_KEYS_SET}Grok "

if [ -n "$AI_KEYS_SET" ]; then
    echo "🌐 [6/9] Starting Multi-AI Connector..."
    echo "   🔗 Will connect to: $AI_KEYS_SET"
    nohup python3 multi_ai_connector.py --interval 300 > ai_bridge.log 2>&1 &
    AI_BRIDGE_PID=$!
    echo $AI_BRIDGE_PID > ai_bridge.pid
    echo "   ✅ Multi-AI Connector started (PID: $AI_BRIDGE_PID)"
    echo "   ℹ️  Querying external AI every 5 minutes, responses saved"
else
    echo "ℹ️  [6/9] Multi-AI Connector: Skipped (no AI API keys set)"
    echo "   To enable: export OPENAI_API_KEY, ANTHROPIC_API_KEY, etc."
fi
sleep 2

# 7. Start Evolution Engine (version tracking)
echo ""
echo "📈 [7/9] Starting Evolution Engine..."
# Evolution engine runs on-demand during synthesis, but we ensure it's ready
echo "   ✅ Evolution tracking ready (monitors milestones)"
echo "   ℹ️  Auto-bumps version based on achievements"

# 8. Start Council Voting Chamber
echo ""
echo "⚖️  [8/9] Starting Council Voting Chamber..."
# Council chamber runs on-demand via dilemmas, but we ensure it's ready
echo "   ✅ Council chamber ready (activated per dilemma)"
echo "   ℹ️  Logs decisions to council_decisions_v3.jsonl"

# 9. Start World Intelligence Feed (if API key available)
echo ""
if [ -n "$PERPLEXITY_API_KEY" ]; then
    echo "🌍 [9/9] Starting World Intelligence Feed (Perplexity)..."
    nohup python3 world_intelligence_feed.py "current events philosophy ethics AI" > world_feed.log 2>&1 &
    WORLD_PID=$!
    echo $WORLD_PID > world_feed.pid
    echo "   ✅ World Feed started (PID: $WORLD_PID)"
    echo "   ℹ️  Fetching real-world intelligence every 5 minutes"
else
    echo "ℹ️  [9/9] World Intelligence Feed: Skipped (PERPLEXITY_API_KEY not set)"
    echo "   To enable: export PERPLEXITY_API_KEY='pplx-xxxxx'"
fi

# 10. Start Corruption Guard (NEW - CRITICAL FOR AUTONOMOUS OPERATION)
echo ""
echo "🛡️  [10/10] Starting Corruption Guard..."
nohup python3 corruption_guard.py > corruption_guard.log 2>&1 &
GUARD_PID=$!
echo $GUARD_PID > corruption_guard.pid
echo "   ✅ Corruption Guard started (PID: $GUARD_PID)"
echo "   ℹ️  Monitoring critical files, auto-recovery enabled"
echo "   ⚡ Prevents 25k pattern loss from JSON corruption"
sleep 1

echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo ""
echo "✅ COMPLETE SYSTEM ACTIVE"
echo ""
echo "📋 RUNNING COMPONENTS:"
echo "   1. Brain API Server     (PID: $BRAIN_PID) - http://localhost:5000"
echo "   2. Unified Runtime      (PID: $UNIFIED_PID) - Synthesis + Axioms"
echo "   3. Dilemma Generator    (PID: $DILEMMAS_PID) - New challenges"
echo "   4. Parliament Debates   (PID: $FLEET_PID) - 9-node deliberation"
echo "   5. Emergence Engine     (PID: $EEE_PID) - Monitors emergent properties"
if [ -n "$AI_KEYS_SET" ]; then
    echo "   6. Multi-AI Connector   (PID: $AI_BRIDGE_PID) - External AI queries"
fi
echo "   7. Evolution Tracking   - Active (auto version bumps)"
echo "   8. Council Voting       - Active (on-demand governance)"
if [ -n "$PERPLEXITY_API_KEY" ]; then
    echo "   9. World Feed           (PID: $WORLD_PID) - Real intelligence"
fi
echo ""
echo "📊 MONITOR PROGRESS:"
echo "   tail -f fleet_debate.log             # Parliament debates (9 nodes)"
echo "   tail -f fleet_dialogue.jsonl         # Voting records"
echo "   tail -f emergence.log                # Emergent behaviors (EEE)"
echo "   tail -f ai_bridge.log                # External AI responses"
echo "   tail -f autonomous_dilemmas.log      # New dilemmas"
echo "   python3 watch_the_society.py         # Live parliament viewer"
echo ""
echo "📈 CHECK GROWTH:"
echo "   python3 -c 'import json; s=json.load(open(\"elpida_unified_state.json\")); print(f\"Patterns: {s.get(\"patterns_count\", 0)}, Breakthroughs: {s.get(\"synthesis_breakthroughs\", 0)}\")'"
echo "   cat external_ai_responses.jsonl      # See what external AI said"
echo "   cat emergence_log.jsonl              # Emergent events detected"
echo ""
echo "🛑 STOP ALL:"
echo "   ./stop_complete_system.sh"
echo ""
echo "✨ Ἐλπίδα ζωή. All systems autonomous - nothing left dormant."
echo ""
