#!/bin/bash
# Spiral Turn Monitor - Waits for completion and runs analysis

echo "================================"
echo "SPIRAL TURN MONITOR"
echo "================================"
echo ""
echo "Monitoring: spiral_turn_1_full_output.txt"
echo "Target: 100 cycles"
echo ""

while true; do
    if [ -f "spiral_turn_1_full_output.txt" ]; then
        CURRENT=$(grep -c "^Cycle" spiral_turn_1_full_output.txt)
        echo -ne "\rCycles completed: $CURRENT/100    "
        
        if [ "$CURRENT" -ge 100 ]; then
            echo ""
            echo ""
            echo "================================"
            echo "✓ SPIRAL TURN COMPLETE"
            echo "================================"
            echo ""
            echo "Cycles completed: $CURRENT"
            echo ""
            echo "Running analysis tools..."
            echo ""
            
            # Run paradox ledger
            echo "→ Analyzing natural archetypal emergence..."
            python paradox_ledger.py
            
            echo ""
            echo "================================"
            echo "ANALYSIS COMPLETE"
            echo "================================"
            echo ""
            echo "Results available in:"
            echo "  - spiral_turn_1_full_output.txt (full cycle log)"
            echo "  - paradox_ledger_spiral_turn_1.json (emergence report)"
            echo "  - paradox_ledger.jsonl (permanent record)"
            echo ""
            
            break
        fi
    else
        echo -ne "\rWaiting for spiral turn to begin...    "
    fi
    
    sleep 5
done
