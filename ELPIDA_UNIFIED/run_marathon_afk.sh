#!/bin/bash
# DEEP DEBATE MARATHON - QUICK START
# Run this to launch everything while you're AFK

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║           DEEP DEBATE MARATHON - AFK MODE                            ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "This will run for 8 hours with:"
echo "  • Continuous fleet operation"
echo "  • Dilemma injection every 5-15 minutes"
echo "  • Real council voting on each dilemma"
echo "  • Wisdom extraction every 30 minutes"
echo "  • Full integration of debates + voting"
echo ""
echo "Logs will be saved to:"
echo "  • deep_debate_log.jsonl (council decisions)"
echo "  • inter_fleet_decisions.jsonl (meta debates)"
echo "  • WISDOM_ARK.json (crystallized patterns)"
echo ""
echo "Press Ctrl+C anytime to stop early"
echo ""
read -p "Press ENTER to start, or Ctrl+C to cancel..."
echo ""

python3 deep_debate_marathon.py --hours 8

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                    MARATHON COMPLETE                                 ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Check the logs for results:"
echo "  cat deep_debate_log.jsonl | jq ."
echo "  cat WISDOM_ARK.json | jq .metadata"
echo ""
