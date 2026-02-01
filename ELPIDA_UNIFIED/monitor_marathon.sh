#!/bin/bash
# Monitor the marathon while it runs

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              MARATHON MONITORING DASHBOARD                           ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Function to count lines in file
count_entries() {
    if [ -f "$1" ]; then
        wc -l < "$1"
    else
        echo "0"
    fi
}

# Function to get last entry timestamp
last_timestamp() {
    if [ -f "$1" ]; then
        tail -1 "$1" 2>/dev/null | jq -r '.timestamp' 2>/dev/null || echo "N/A"
    else
        echo "N/A"
    fi
}

while true; do
    clear
    echo "╔══════════════════════════════════════════════════════════════════════╗"
    echo "║              MARATHON MONITORING DASHBOARD                           ║"
    echo "╚══════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Check if marathon is running
    if pgrep -f "deep_debate_marathon.py" > /dev/null; then
        echo "✅ Marathon: RUNNING"
    else
        echo "⏸️  Marathon: STOPPED"
    fi
    echo ""
    
    # Stats
    DILEMMAS=$(count_entries "deep_debate_log.jsonl")
    DEBATES=$(count_entries "inter_fleet_decisions.jsonl")
    
    echo "📊 STATISTICS:"
    echo "   Dilemmas resolved: $DILEMMAS"
    echo "   Inter-fleet debates: $DEBATES"
    echo "   Total council votes: $((DILEMMAS + DEBATES))"
    echo ""
    
    # Last activity
    echo "⏰ LAST ACTIVITY:"
    LAST_DILEMMA=$(last_timestamp "deep_debate_log.jsonl")
    LAST_DEBATE=$(last_timestamp "inter_fleet_decisions.jsonl")
    echo "   Last dilemma: $LAST_DILEMMA"
    echo "   Last debate: $LAST_DEBATE"
    echo ""
    
    # Wisdom ARK
    if [ -f "WISDOM_ARK.json" ]; then
        PATTERNS=$(jq -r '.metadata.total_patterns // 0' WISDOM_ARK.json 2>/dev/null || echo "0")
        LAST_EXTRACT=$(jq -r '.metadata.last_updated // "N/A"' WISDOM_ARK.json 2>/dev/null || echo "N/A")
        echo "📚 WISDOM ARK:"
        echo "   Total patterns: $PATTERNS"
        echo "   Last extraction: $LAST_EXTRACT"
    else
        echo "📚 WISDOM ARK: Not created yet"
    fi
    echo ""
    
    # Recent decision sample
    if [ -f "deep_debate_log.jsonl" ] && [ $DILEMMAS -gt 0 ]; then
        echo "📜 LAST DECISION:"
        LAST_DEC=$(tail -1 deep_debate_log.jsonl)
        CATEGORY=$(echo "$LAST_DEC" | jq -r '.dilemma.category' 2>/dev/null || echo "?")
        STATUS=$(echo "$LAST_DEC" | jq -r '.council_decision.status' 2>/dev/null || echo "?")
        APPROVAL=$(echo "$LAST_DEC" | jq -r '.council_decision.weighted_approval' 2>/dev/null || echo "?")
        echo "   Category: $CATEGORY"
        echo "   Status: $STATUS"
        if [ "$APPROVAL" != "?" ]; then
            APPROVAL_PCT=$(echo "$APPROVAL * 100" | bc 2>/dev/null || echo "?")
            echo "   Approval: ${APPROVAL_PCT}%"
        fi
    fi
    echo ""
    
    echo "──────────────────────────────────────────────────────────────────────"
    echo "Refreshing every 30 seconds... (Ctrl+C to exit monitor)"
    echo ""
    
    sleep 30
done
