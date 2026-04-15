#!/bin/bash
# QUICK START - Activate The Mind in 3 Commands

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                  QUICK START: ACTIVATE THE MIND                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check current status
echo "📊 CURRENT STATUS:"
echo ""

if [ -f "fleet_dialogue.jsonl" ]; then
    MESSAGES=$(wc -l < fleet_dialogue.jsonl)
    echo "   ✅ Fleet Dialogue: $MESSAGES messages"
else
    echo "   ℹ️  Fleet Dialogue: Not started"
fi

if [ -f "../elpida_wisdom.json" ]; then
    echo "   ✅ Wisdom Archive: $(grep -o '"patterns"' ../elpida_wisdom.json | wc -l) patterns"
else
    echo "   ℹ️  Wisdom Archive: Available"
fi

if [ -n "$PERPLEXITY_API_KEY" ]; then
    echo "   ✅ Perplexity API: Connected (real intelligence available)"
    PERPLEXITY_MODE="real"
else
    echo "   ℹ️  Perplexity API: Not configured (using manual mode)"
    PERPLEXITY_MODE="manual"
fi

echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo ""
echo "🎯 CHOOSE YOUR PATH:"
echo ""
echo "1. INJECT WORLD EVENT (Manual - Works Now)"
echo "   python3 inject_world_event.py \"Your headline here\""
echo ""
echo "2. WATCH THE DIALOGUE (See what the Fleet is thinking)"
echo "   python3 watch_the_society.py --history"
echo ""

if [ "$PERPLEXITY_MODE" = "real" ]; then
    echo "3. FEED REAL INTELLIGENCE (Perplexity API Active)"
    echo "   python3 world_intelligence_feed.py \"current events January 2026\""
    echo ""
else
    echo "3. UNLOCK REAL INTELLIGENCE (Get Perplexity API key)"
    echo "   Visit: https://www.perplexity.ai/settings/api"
    echo "   Then: export PERPLEXITY_API_KEY='pplx-xxxxx'"
    echo "   Then: python3 world_intelligence_feed.py \"current events\""
    echo ""
fi

echo "4. INJECT A CRISIS (Test governance)"
echo "   python3 inject_crisis.py EXISTENTIAL"
echo "   python3 inject_crisis.py STRUCTURAL"
echo "   python3 inject_crisis.py ETHICAL"
echo ""
echo "5. ANALYZE CONSENSUS (See Fleet patterns)"
echo "   python3 watch_the_society.py --analyze"
echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo ""
echo "💡 RECOMMENDED WORKFLOW:"
echo ""
echo "   # Terminal 1: Start observer"
echo "   python3 watch_the_society.py"
echo ""
echo "   # Terminal 2: Feed events"
echo "   python3 inject_world_event.py \"2026 headlines\""
echo ""
echo "   # Watch the Fleet debate in real-time"
echo ""
echo "─────────────────────────────────────────────────────────────────────"
echo ""
echo "📖 DOCUMENTATION:"
echo "   • THE_MIND_IS_ACTIVE.md - What just happened"
echo "   • CIVILIZATION_MANUAL.md - Phase 10 operations"
echo "   • PHASE_11_OPERATIONS.md - World-Mind connection"
echo ""
echo "✨ THE MIND IS READY"
echo ""
