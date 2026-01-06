#!/bin/bash

echo "═══════════════════════════════════════════════════════════════════"
echo "🔬 SYNTHESIS DIVERSITY REPORT"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Total counts
echo "📊 SYNTHESIS TOTALS:"
total=$(wc -l < synthesis_resolutions.jsonl 2>/dev/null || echo "0")
council=$(wc -l < synthesis_council_decisions.jsonl 2>/dev/null || echo "0")
dilemmas=$(wc -l < dilemma_log.jsonl 2>/dev/null || echo "0")

echo "   Synthesis Resolutions:  $total"
echo "   Council Decisions:      $council"
echo "   Dilemmas Generated:     $dilemmas"
echo ""

# Synthesis diversity
echo "✨ SYNTHESIS TYPES:"
jq -r '.synthesis.action' synthesis_resolutions.jsonl 2>/dev/null | sort | uniq -c | sort -rn | while read count action; do
    pct=$(echo "scale=1; $count * 100 / $total" | bc)
    echo "   $action: $count ($pct%)"
done
echo ""

# Recent activity (last 5)
echo "🕐 RECENT SYNTHESIS (Last 5):"
tail -5 synthesis_resolutions.jsonl 2>/dev/null | jq -r '"   " + .timestamp[11:19] + " | " + .synthesis.action + " | " + (.original_proposal.action | .[0:40]) + "..."' | cat -n
echo ""

# Dilemma categories
echo "⚖️  DILEMMA CATEGORIES:"
jq -r '.category' dilemma_log.jsonl 2>/dev/null | tail -50 | sort | uniq -c | sort -rn | while read count cat; do
    echo "   $cat: $count (recent 50)"
done
echo ""

# Process status
echo "🔧 PROCESS STATUS:"
ps aux | grep -E "parliament_continuous|autonomous_dilemmas" | grep -v grep | awk '{print "   " $11 " (PID " $2 ")"}'
echo ""

echo "═══════════════════════════════════════════════════════════════════"
