#!/bin/bash
# ΠΟΛΙΣ Continuous Service Controller
# Manages the POLIS v2.0 (EEE) runtime as background process

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POLIS_DIR="$SCRIPT_DIR"
PID_FILE="$POLIS_DIR/polis.pid"
LOG_FILE="$POLIS_DIR/polis_service.log"
PYTHON_SCRIPT="$POLIS_DIR/polis_daemon.py"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  POLIS service already running (PID: $PID)${NC}"
            return 1
        else
            echo -e "${YELLOW}⚠️  Stale PID file found, cleaning up${NC}"
            rm "$PID_FILE"
        fi
    fi

    echo -e "${BLUE}🏛️  Starting ΠΟΛΙΣ Continuous Service...${NC}"
    
    # Start daemon in background
    nohup python3 "$PYTHON_SCRIPT" > "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    sleep 2
    
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ POLIS service started (PID: $PID)${NC}"
        echo -e "${GREEN}   Log: $LOG_FILE${NC}"
        echo -e "${GREEN}   Memory: $POLIS_DIR/polis_civic_memory.json${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to start POLIS service${NC}"
        rm "$PID_FILE"
        echo -e "${RED}   Check logs: $LOG_FILE${NC}"
        return 1
    fi
}

function stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}⚠️  POLIS service not running (no PID file)${NC}"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  POLIS service not running (PID $PID not found)${NC}"
        rm "$PID_FILE"
        return 1
    fi

    echo -e "${BLUE}🛑 Stopping ΠΟΛΙΣ service (PID: $PID)...${NC}"
    kill "$PID"
    
    # Wait for graceful shutdown
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            rm "$PID_FILE"
            echo -e "${GREEN}✅ POLIS service stopped${NC}"
            return 0
        fi
        sleep 1
    done
    
    # Force kill if still running
    echo -e "${YELLOW}⚠️  Forcing shutdown...${NC}"
    kill -9 "$PID" 2>/dev/null
    rm "$PID_FILE"
    echo -e "${GREEN}✅ POLIS service stopped (forced)${NC}"
}

function status() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${RED}❌ POLIS service: STOPPED${NC}"
        return 1
    fi

    PID=$(cat "$PID_FILE")
    
    if ps -p "$PID" > /dev/null 2>&1; then
        UPTIME=$(ps -p "$PID" -o etime= | tr -d ' ')
        MEM=$(ps -p "$PID" -o rss= | tr -d ' ')
        MEM_MB=$((MEM / 1024))
        
        echo -e "${GREEN}✅ POLIS service: RUNNING${NC}"
        echo -e "${GREEN}   PID: $PID${NC}"
        echo -e "${GREEN}   Uptime: $UPTIME${NC}"
        echo -e "${GREEN}   Memory: ${MEM_MB}MB${NC}"
        echo -e "${GREEN}   Log: $LOG_FILE${NC}"
        
        # Show recent cognitive load metrics
        if [ -f "$POLIS_DIR/polis_civic_memory.json" ]; then
            EVENTS=$(python3 -c "import json; d=json.load(open('$POLIS_DIR/polis_civic_memory.json')); print(len(d.get('l1_raw_events', [])))" 2>/dev/null)
            CONTRADICTIONS=$(python3 -c "import json; d=json.load(open('$POLIS_DIR/polis_civic_memory.json')); print(len([c for c in d.get('contradictions', []) if not c.get('resolved', False)]))" 2>/dev/null)
            echo -e "${BLUE}   Events logged: $EVENTS${NC}"
            echo -e "${BLUE}   Active contradictions: $CONTRADICTIONS${NC}"
        fi
        
        return 0
    else
        echo -e "${RED}❌ POLIS service: STOPPED (stale PID file)${NC}"
        rm "$PID_FILE"
        return 1
    fi
}

function restart() {
    echo -e "${BLUE}🔄 Restarting ΠΟΛΙΣ service...${NC}"
    stop
    sleep 2
    start
}

function monitor_logs() {
    if [ ! -f "$LOG_FILE" ]; then
        echo -e "${YELLOW}⚠️  No log file found${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📊 POLIS Service Logs (tail -f)${NC}"
    echo -e "${BLUE}Press Ctrl+C to exit${NC}"
    echo ""
    tail -f "$LOG_FILE"
}

function monitor_load() {
    echo -e "${BLUE}📊 POLIS Cognitive Load Monitor${NC}"
    echo -e "${BLUE}Press Ctrl+C to exit${NC}"
    echo ""
    
    while true; do
        if [ -f "$POLIS_DIR/polis_civic_memory.json" ]; then
            python3 -c "
import json
from datetime import datetime

with open('$POLIS_DIR/polis_civic_memory.json', 'r') as f:
    memory = json.load(f)

events = memory.get('l1_raw_events', [])
contradictions = memory.get('contradictions', [])
sacrifices = memory.get('sacrifices', [])

# Calculate cognitive load
now = datetime.utcnow()
recent_events = [e for e in events if (now - datetime.fromisoformat(e['timestamp'])).total_seconds() < 3600]
active_contradictions = [c for c in contradictions if not c.get('resolved', False)]

velocity = len(recent_events)
contradiction_density = len(active_contradictions)
overloaded = velocity > 100 or contradiction_density > 50

status = '🔴 OVERLOADED' if overloaded else '🟢 NORMAL'

print(f'\033[2J\033[H')  # Clear screen
print(f'═══════════════════════════════════════════════════════')
print(f'  ΠΟΛΙΣ v2.0 (EEE) - Cognitive Load Monitor')
print(f'  {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}')
print(f'═══════════════════════════════════════════════════════')
print(f'')
print(f'  Status: {status}')
print(f'')
print(f'  📊 Metrics:')
print(f'     Message Velocity:      {velocity:>6} events/hour')
print(f'     Contradiction Density: {contradiction_density:>6} active')
print(f'     Total Events (L1):     {len(events):>6}')
print(f'     Total Contradictions:  {len(contradictions):>6}')
print(f'     Total Sacrifices:      {len(sacrifices):>6}')
print(f'')
print(f'  🔄 Thresholds:')
print(f'     Velocity limit:        100 events/hour')
print(f'     Contradiction limit:   50 active')
print(f'')
print(f'═══════════════════════════════════════════════════════')
" 2>/dev/null || echo "Error reading memory file"
        else
            echo "Memory file not found"
        fi
        
        sleep 5
    done
}

function usage() {
    echo -e "${BLUE}ΠΟΛΙΣ Continuous Service Controller${NC}"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|monitor-logs|monitor-load}"
    echo ""
    echo "Commands:"
    echo "  start        - Start POLIS runtime as background service"
    echo "  stop         - Stop POLIS runtime"
    echo "  restart      - Restart POLIS runtime"
    echo "  status       - Show service status and metrics"
    echo "  monitor-logs - Tail service logs (real-time)"
    echo "  monitor-load - Monitor cognitive load metrics (real-time)"
    echo ""
}

# Main command dispatcher
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    monitor-logs)
        monitor_logs
        ;;
    monitor-load)
        monitor_load
        ;;
    *)
        usage
        exit 1
        ;;
esac

exit $?
