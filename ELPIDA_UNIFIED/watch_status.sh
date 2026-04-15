#!/bin/bash
#
# ELPIDA STATUS WATCH
# Continuous monitoring with auto-refresh
#

INTERVAL=${1:-30}  # Default 30 seconds

echo "🔄 ELPIDA STATUS WATCH (refresh every ${INTERVAL}s)"
echo "Press Ctrl+C to stop"
echo ""

while true; do
    clear
    python3 monitor_comprehensive.py 2>&1 | grep -v "DeprecationWarning"
    echo ""
    echo "Next refresh in ${INTERVAL}s..."
    sleep $INTERVAL
done
