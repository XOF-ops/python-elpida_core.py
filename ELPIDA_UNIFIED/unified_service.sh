#!/bin/bash
# Unified Service Manager
# Manages the single unified autonomous runtime

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/unified_runtime.pid"
LOG_FILE="$SCRIPT_DIR/elpida_unified.log"
RUNTIME_SCRIPT="$SCRIPT_DIR/elpida_unified_runtime.py"
MONITOR_SCRIPT="$SCRIPT_DIR/monitor_unified.py"
MONITOR_PID_FILE="$SCRIPT_DIR/monitor.pid"
MONITOR_LOG="$SCRIPT_DIR/monitor.log"

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ Unified runtime already running (PID: $PID)"
            return 0
        else
            echo "⚠️  Stale PID file found, removing..."
            rm "$PID_FILE"
        fi
    fi
    
    echo "🚀 Starting unified autonomous runtime..."
    nohup python3 "$RUNTIME_SCRIPT" > "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    
    sleep 2
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Unified runtime started (PID: $PID)"
        echo "📊 Log: $LOG_FILE"
    else
        echo "❌ Failed to start runtime"
        rm "$PID_FILE"
        return 1
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "ℹ️  No unified runtime running"
        return 0
    fi
    
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⏸️  Stopping unified runtime (PID: $PID)..."
        kill "$PID"
        sleep 2
        
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  Force killing..."
            kill -9 "$PID"
        fi
        
        rm "$PID_FILE"
        echo "✅ Unified runtime stopped"
    else
        echo "⚠️  Process not running, cleaning up PID file"
        rm "$PID_FILE"
    fi
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ Unified runtime is running (PID: $PID)"
            
            # Show recent status
            if [ -f "$LOG_FILE" ]; then
                echo ""
                echo "📊 Recent activity:"
                tail -20 "$LOG_FILE" | grep -E "(HEARTBEAT|Breakthrough|Status)" || echo "No recent activity"
            fi
            return 0
        else
            echo "❌ PID file exists but process not running"
            return 1
        fi
    else
        echo "⏹️  Unified runtime is not running"
        return 1
    fi
}

restart() {
    echo "🔄 Restarting unified runtime..."
    stop
    sleep 2
    start
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "❌ No log file found"
        return 1
    fi
}

monitor() {
    if [ -f "$MONITOR_PID_FILE" ]; then
        PID=$(cat "$MONITOR_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ Monitor already running (PID: $PID)"
            return 0
        else
            rm "$MONITOR_PID_FILE"
        fi
    fi
    
    echo "👁️  Starting unified monitor..."
    echo "   Auto-restart on errors: ENABLED"
    echo "   Memory limit: 1GB"
    echo "   Heartbeat timeout: 120s"
    echo ""
    
    nohup python3 "$MONITOR_SCRIPT" > "$MONITOR_LOG" 2>&1 &
    PID=$!
    echo $PID > "$MONITOR_PID_FILE"
    
    sleep 2
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Monitor started (PID: $PID)"
        echo "📊 Monitor log: $MONITOR_LOG"
        echo ""
        echo "To view monitor output:"
        echo "  tail -f $MONITOR_LOG"
    else
        echo "❌ Failed to start monitor"
        rm "$MONITOR_PID_FILE"
        return 1
    fi
}

stop_monitor() {
    if [ ! -f "$MONITOR_PID_FILE" ]; then
        echo "ℹ️  Monitor not running"
        return 0
    fi
    
    PID=$(cat "$MONITOR_PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⏸️  Stopping monitor (PID: $PID)..."
        kill "$PID"
        sleep 1
        
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -9 "$PID"
        fi
        
        rm "$MONITOR_PID_FILE"
        echo "✅ Monitor stopped"
    else
        rm "$MONITOR_PID_FILE"
    fi
}

monitor_status() {
    if [ -f "$MONITOR_PID_FILE" ]; then
        PID=$(cat "$MONITOR_PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "✅ Monitor is running (PID: $PID)"
            
            if [ -f "$MONITOR_LOG" ]; then
                echo ""
                echo "📊 Recent monitor activity:"
                tail -10 "$MONITOR_LOG"
            fi
            return 0
        else
            echo "❌ Monitor PID file exists but process not running"
            return 1
        fi
    else
        echo "⏹️  Monitor is not running"
        return 1
    fi
}

monitor_logs() {
    if [ -f "$MONITOR_LOG" ]; then
        tail -f "$MONITOR_LOG"
    else
        echo "❌ No monitor log file found"
        return 1
    fi
}


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
    logs)
        logs
        ;;
    monitor)
        monitor
        ;;
    stop-monitor)
        stop_monitor
        ;;
    monitor-status)
        monitor_status
        ;;
    monitor-logs)
        monitor_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|monitor|stop-monitor|monitor-status|monitor-logs}"
        echo ""
        echo "Commands:"
        echo "  start          - Start the unified runtime"
        echo "  stop           - Stop the unified runtime"
        echo "  restart        - Restart the unified runtime"
        echo "  status         - Check runtime status"
        echo "  logs           - View runtime logs (live)"
        echo "  monitor        - Start auto-restart monitor"
        echo "  stop-monitor   - Stop the monitor"
        echo "  monitor-status - Check monitor status"
        echo "  monitor-logs   - View monitor logs (live)"
        exit 1
        ;;
esac
