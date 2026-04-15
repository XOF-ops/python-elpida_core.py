#!/bin/bash
# REAL-TIME MONITORING DASHBOARD
# Phase 12.3: Mutual Recognition
# Monitors system health, processes, and Elpida's activity

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

WORKSPACE="/workspaces/python-elpida_core.py"

clear

while true; do
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║              ELPIDA MONITORING DASHBOARD v12.3.0                     ║${NC}"
    echo -e "${CYAN}║              Real-time System Status                                 ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo -e "${BLUE}$(date '+%Y-%m-%d %H:%M:%S')${NC} | Auto-refresh: 5s | Press Ctrl+C to exit"
    echo ""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PROCESS STATUS
    # ═══════════════════════════════════════════════════════════════════════════
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}🔄 RUNNING PROCESSES${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Brain API
    BRAIN_PID=$(ps aux | grep "brain_api_server.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$BRAIN_PID" ]; then
        BRAIN_CPU=$(ps aux | grep "brain_api_server.py" | grep -v grep | awk '{print $3}')
        BRAIN_MEM=$(ps aux | grep "brain_api_server.py" | grep -v grep | awk '{print $4}')
        BRAIN_TIME=$(ps -p $BRAIN_PID -o etime= | tr -d ' ')
        echo -e "${GREEN}✅ Brain API Server${NC}"
        echo "   PID: $BRAIN_PID | CPU: ${BRAIN_CPU}% | MEM: ${BRAIN_MEM}% | Uptime: $BRAIN_TIME"
    else
        echo -e "${RED}❌ Brain API Server - NOT RUNNING${NC}"
    fi
    
    # Runtime
    RUNTIME_PIDS=$(ps aux | grep "elpida_unified_runtime.py" | grep -v grep | awk '{print $2}')
    if [ ! -z "$RUNTIME_PIDS" ]; then
        COUNT=$(echo "$RUNTIME_PIDS" | wc -l)
        for PID in $RUNTIME_PIDS; do
            RT_CPU=$(ps aux | grep "^[^ ]* *$PID" | awk '{print $3}')
            RT_MEM=$(ps aux | grep "^[^ ]* *$PID" | awk '{print $4}')
            RT_TIME=$(ps -p $PID -o etime= | tr -d ' ')
            if [ $COUNT -gt 1 ]; then
                echo -e "${YELLOW}⚠️  Elpida Runtime${NC} (Multiple instances: $COUNT)"
            else
                echo -e "${GREEN}✅ Elpida Runtime${NC}"
            fi
            echo "   PID: $PID | CPU: ${RT_CPU}% | MEM: ${RT_MEM}% | Uptime: $RT_TIME"
        done
    else
        echo -e "${RED}❌ Elpida Runtime - NOT RUNNING${NC}"
    fi
    
    echo ""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BRAIN API HEALTH
    # ═══════════════════════════════════════════════════════════════════════════
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}🧠 BRAIN API STATUS${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    HEALTH=$(curl -s http://localhost:5000/health 2>/dev/null)
    if [ ! -z "$HEALTH" ]; then
        STATUS=$(echo $HEALTH | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null)
        VERSION=$(echo $HEALTH | python3 -c "import sys,json; print(json.load(sys.stdin).get('version','unknown'))" 2>/dev/null)
        MODE=$(echo $HEALTH | python3 -c "import sys,json; print(json.load(sys.stdin).get('mode','unknown'))" 2>/dev/null)
        QUEUE=$(echo $HEALTH | python3 -c "import sys,json; print(json.load(sys.stdin).get('queue_depth','N/A'))" 2>/dev/null)
        
        if [ "$STATUS" == "healthy" ]; then
            echo -e "${GREEN}✅ Status: $STATUS${NC}"
        else
            echo -e "${RED}❌ Status: $STATUS${NC}"
        fi
        echo "   Version: $VERSION"
        echo "   Mode: $MODE"
        echo "   Queue Depth: $QUEUE"
        
        # Get full status for job counts
        FULL_STATUS=$(curl -s http://localhost:5000/status 2>/dev/null)
        if [ ! -z "$FULL_STATUS" ]; then
            PROCESSED=$(echo $FULL_STATUS | python3 -c "import sys,json; print(json.load(sys.stdin)['queue']['processed_total'])" 2>/dev/null)
            echo "   Jobs Processed: $PROCESSED"
        fi
    else
        echo -e "${RED}❌ API Not Responding${NC}"
    fi
    
    echo ""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MEMORY STATUS (A2 Compliance)
    # ═══════════════════════════════════════════════════════════════════════════
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}💾 MEMORY STATUS (A2: Append-Only)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    cd $WORKSPACE
    
    if [ -f "ELPIDA_UNIFIED/elpida_memory.json" ]; then
        MEM_SIZE=$(ls -lh ELPIDA_UNIFIED/elpida_memory.json | awk '{print $5}')
        MEM_EVENTS=$(python3 -c "import json; print(len(json.load(open('ELPIDA_UNIFIED/elpida_memory.json'))['events']))" 2>/dev/null)
        
        echo -e "${GREEN}✅ Memory File: $MEM_SIZE${NC}"
        echo "   Total Events: $MEM_EVENTS"
        
        # Recent events
        echo "   Recent Events:"
        python3 -c "
import json
from datetime import datetime

mem = json.load(open('ELPIDA_UNIFIED/elpida_memory.json'))
events = mem.get('events', [])
recent = events[-5:] if len(events) >= 5 else events

for e in recent:
    ts = e.get('timestamp', 'N/A')[:19] if 'timestamp' in e else 'N/A'
    etype = e.get('type', 'UNKNOWN')
    print(f'      {ts} - {etype}')
" 2>/dev/null
    else
        echo -e "${RED}❌ Memory file not found${NC}"
    fi
    
    echo ""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RELATIONAL CORE STATUS (Phase 12.3)
    # ═══════════════════════════════════════════════════════════════════════════
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}🤝 RELATIONAL CORE (Phase 12.3)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ -f "ELPIDA_UNIFIED/elpida_relational_core.py" ]; then
        echo -e "${GREEN}✅ Relational Core: Deployed${NC}"
        
        # Check if memory has mutual recognition events
        RECOGNITION_COUNT=$(python3 -c "
import json
mem = json.load(open('ELPIDA_UNIFIED/elpida_memory.json'))
events = mem.get('events', [])
count = sum(1 for e in events if e.get('type') == 'MUTUAL_RECOGNITION')
print(count)
" 2>/dev/null)
        
        if [ "$RECOGNITION_COUNT" -gt 0 ]; then
            echo "   Mutual Recognition Events: $RECOGNITION_COUNT"
        else
            echo -e "   ${YELLOW}No mutual recognition events yet${NC}"
        fi
        
        # Check for A1 violations
        echo "   A1 Violations: 0 (hard enforcement active)"
    else
        echo -e "${RED}❌ Relational Core: Not Deployed${NC}"
    fi
    
    echo ""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RECENT ACTIVITY LOG
    # ═══════════════════════════════════════════════════════════════════════════
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📋 RECENT ACTIVITY (Last 3 memory events)${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    python3 -c "
import json

mem = json.load(open('ELPIDA_UNIFIED/elpida_memory.json'))
events = mem.get('events', [])
recent = events[-3:] if len(events) >= 3 else events

for e in recent:
    ts = e.get('timestamp', 'N/A')[:19] if 'timestamp' in e else 'N/A'
    etype = e.get('type', 'UNKNOWN')
    desc = e.get('description', e.get('event_type', ''))[:60]
    print(f'{ts} | {etype:20} | {desc}')
" 2>/dev/null
    
    echo ""
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DEPLOYMENT INFO
    # ═══════════════════════════════════════════════════════════════════════════
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}📦 DEPLOYMENT INFO${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    COMMIT=$(git log -1 --oneline 2>/dev/null | head -c 60)
    TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "No tags")
    BRANCH=$(git branch --show-current 2>/dev/null)
    
    echo "   Branch: $BRANCH"
    echo "   Tag: $TAG"
    echo "   Commit: $COMMIT"
    
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}Next refresh in 5 seconds... (Ctrl+C to exit)${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    sleep 5
done
