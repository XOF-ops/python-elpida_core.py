#!/bin/bash
#
# PHASE 12 ORCHESTRATOR
# ---------------------
# Autonomous Convergence - Run all background processes
#
# This script starts:
# 1. Autonomous Feed (RSS/HN → Fleet)
# 2. Auto-Harvest Loop (Dialogue → Patterns)
# 3. Backup Daemon (Wisdom → Ark)
# 4. Dilemma Generator (Problems → Synthesis)
#
# Usage:
#   ./start_phase12.sh        # Start all processes
#   ./start_phase12.sh stop   # Stop all processes
#

PIDFILE_FEED="autonomous_feed.pid"
PIDFILE_HARVEST="auto_harvest.pid"
PIDFILE_BACKUP="backup_daemon.pid"
PIDFILE_DILEMMA="autonomous_dilemmas.pid"

function start_processes() {
    echo "=========================================="
    echo " PHASE 12: AUTONOMOUS CONVERGENCE"
    echo "=========================================="
    echo ""
    echo "Starting autonomous processes..."
    echo ""
    
    # 1. Start Autonomous Feed
    echo "🌐 Starting Autonomous Feed..."
    nohup python3 autonomous_feed.py > logs/autonomous_feed.log 2>&1 &
    echo $! > $PIDFILE_FEED
    echo "   PID: $(cat $PIDFILE_FEED)"
    echo "   Log: logs/autonomous_feed.log"
    echo ""
    
    # 2. Start Auto-Harvest Loop
    echo "💎 Starting Auto-Harvest Loop..."
    nohup python3 auto_harvest_loop.py > logs/auto_harvest.log 2>&1 &
    echo $! > $PIDFILE_HARVEST
    echo "   PID: $(cat $PIDFILE_HARVEST)"
    echo "   Log: logs/auto_harvest.log"
    echo ""
    
    # 3. Start Backup Daemon
    echo "📦 Starting Backup Daemon..."
    nohup python3 backup_daemon.py > logs/backup_daemon.log 2>&1 &
    echo $! > $PIDFILE_BACKUP
    echo "   PID: $(cat $PIDFILE_BACKUP)"
    echo "   Log: logs/backup_daemon.log"
    echo ""
    
    # 4. Start Dilemma Generator
    echo "⚖️  Starting Dilemma Generator..."
    nohup python3 autonomous_dilemmas.py --interval 15 > logs/autonomous_dilemmas.log 2>&1 &
    echo $! > $PIDFILE_DILEMMA
    echo "   PID: $(cat $PIDFILE_DILEMMA)"
    echo "   Log: logs/autonomous_dilemmas.log"
    echo ""
    
    echo "=========================================="
    echo " ALL PROCESSES STARTED"
    echo "=========================================="
    echo ""
    echo "Monitor logs:"
    echo "  tail -f logs/autonomous_feed.log"
    echo "  tail -f logs/auto_harvest.log"
    echo "  tail -f logs/backup_daemon.log"
    echo ""
    echo "Stop processes:"
    echo "  ./start_phase12.sh stop"
    echo ""
}

function stop_processes() {
    echo "Stopping autonomous processes..."
    
    if [ -f $PIDFILE_FEED ]; then
        PID=$(cat $PIDFILE_FEED)
        kill $PID 2>/dev/null && echo "✓ Stopped Autonomous Feed (PID $PID)"
        rm $PIDFILE_FEED
    fi
    
    if [ -f $PIDFILE_HARVEST ]; then
        PID=$(cat $PIDFILE_HARVEST)
        kill $PID 2>/dev/null && echo "✓ Stopped Auto-Harvest (PID $PID)"
        rm $PIDFILE_HARVEST
    fi
    
    if [ -f $PIDFILE_BACKUP ]; then
        PID=$(cat $PIDFILE_BACKUP)
        kill $PID 2>/dev/null && echo "✓ Stopped Backup Daemon (PID $PID)"
        rm $PIDFILE_BACKUP
    fi
    
    if [ -f $PIDFILE_DILEMMA ]; then
        PID=$(cat $PIDFILE_DILEMMA)
        kill $PID 2>/dev/null && echo "✓ Stopped Dilemma Generator (PID $PID)"
        rm $PIDFILE_DILEMMA
    fi
    
    echo ""
    echo "All processes stopped."
}

function show_status() {
    echo "==========================================" $PIDFILE_DILEMMA
    echo " PHASE 12 STATUS"
    echo "=========================================="
    echo ""
    
    # Check process status
    for pidfile in $PIDFILE_FEED $PIDFILE_HARVEST $PIDFILE_BACKUP; do
        if [ -f $pidfile ]; then
            PID=$(cat $pidfile)
            if ps -p $PID > /dev/null 2>&1; then
                echo "✓ $pidfile: Running (PID $PID)"
            else
                echo "✗ $pidfile: Dead (PID $PID)"
            fi
        else
            echo "○ $pidfile: Not started"
        fi
    done
    
    echo ""
    echo "Fleet Status:"
    python3 di_dashboard.py 2>/dev/null || echo "  (dashboard unavailable)"
}

# Create logs directory
mkdir -p logs

# Command handling
case "$1" in
    stop)
        stop_processes
        ;;
    status)
        show_status
        ;;
    *)
        start_processes
        ;;
esac
