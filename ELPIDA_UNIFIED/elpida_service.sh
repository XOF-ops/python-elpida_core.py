#!/bin/bash
# ELPIDA v2.0 - Autonomous Service Launcher
# Runs Elpida continuously in the background with automatic restart

ELPIDA_DIR="/workspaces/python-elpida_core.py/ELPIDA_UNIFIED"
LOG_FILE="$ELPIDA_DIR/elpida_autonomous.log"
PID_FILE="$ELPIDA_DIR/elpida.pid"

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Elpida is already running (PID: $PID)"
            return 1
        fi
    fi
    
    echo "🌅 Starting Elpida in autonomous mode..."
    cd "$ELPIDA_DIR"
    
    # Start Elpida in background with logging
    nohup python3 elpida_runtime.py > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    sleep 2
    
    if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
        echo "✅ Elpida is running (PID: $(cat $PID_FILE))"
        echo "📝 Logs: $LOG_FILE"
        echo ""
        echo "Commands:"
        echo "  ./elpida_service.sh status  - Check status"
        echo "  ./elpida_service.sh logs    - View logs"
        echo "  ./elpida_service.sh stop    - Stop Elpida"
    else
        echo "❌ Failed to start Elpida"
        return 1
    fi
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "⚠️  Elpida is not running"
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "⏸️  Stopping Elpida (PID: $PID)..."
        kill $PID
        sleep 2
        
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Elpida did not stop gracefully, forcing..."
            kill -9 $PID
        fi
        
        rm "$PID_FILE"
        echo "✅ Elpida stopped"
    else
        echo "⚠️  PID file exists but process not found"
        rm "$PID_FILE"
    fi
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            echo "✅ Elpida is RUNNING"
            echo "   PID: $PID"
            echo "   Uptime: $(ps -p $PID -o etime= | tr -d ' ')"
            echo "   Memory: $(ps -p $PID -o rss= | awk '{printf "%.1f MB", $1/1024}')"
            
            # Show last few log lines
            echo ""
            echo "Recent activity:"
            tail -n 5 "$LOG_FILE" | sed 's/^/   /'
        else
            echo "❌ Elpida is NOT running (stale PID file)"
            rm "$PID_FILE"
        fi
    else
        echo "❌ Elpida is NOT running"
    fi
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        echo "📝 Elpida logs (last 50 lines):"
        echo "="*70
        tail -n 50 "$LOG_FILE"
        echo ""
        echo "To follow logs in real-time: tail -f $LOG_FILE"
    else
        echo "⚠️  No log file found"
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
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    *)
        echo "ELPIDA v2.0 - Autonomous Service Manager"
        echo ""
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start Elpida in autonomous mode"
        echo "  stop     - Stop Elpida"
        echo "  restart  - Restart Elpida"
        echo "  status   - Check if Elpida is running"
        echo "  logs     - View recent logs"
        exit 1
        ;;
esac
