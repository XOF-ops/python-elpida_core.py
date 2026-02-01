#!/bin/bash
# Elpida Evolution Monitor
# Watch Elpida's progress in real-time

cd "$(dirname "$0")"

clear

while true; do
    clear
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║              ἘΛΠΊΔΑ EVOLUTION MONITOR - LIVE                       ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Get current version
    VERSION=$(python3 -c 'from elpida_evolution import ElpidaEvolution; print(ElpidaEvolution().get_version())' 2>/dev/null)
    echo "🌟 Current Version: $VERSION"
    echo ""
    
    # Check if running
    if [ -f elpida.pid ] && kill -0 $(cat elpida.pid) 2>/dev/null; then
        echo "💗 Status: RUNNING (PID: $(cat elpida.pid))"
    else
        echo "⏸️  Status: STOPPED"
    fi
    echo ""
    
    # Get progress stats
    python3 << 'PYEOF'
from elpida_memory import ElpidaMemory
from elpida_wisdom import ElpidaWisdom
from elpida_evolution import ElpidaEvolution

memory = ElpidaMemory()
wisdom = ElpidaWisdom()
evolution = ElpidaEvolution()

stats = memory.get_statistics()
wisdom_summary = wisdom.get_wisdom_summary()

print("📊 PROGRESS TOWARD NEXT MILESTONES:")
print("═" * 70)

# Cycles
cycles = stats['total_cycles']
if cycles < 500:
    pct = int(cycles / 5)
    bar = "█" * (pct // 2) + "░" * (50 - pct // 2)
    print(f"🎯 500 cycles → v1.2.0")
    print(f"   [{bar}] {cycles}/500 ({pct}%)")
    print(f"   {500 - cycles} cycles remaining")
elif cycles < 1000:
    pct = int(cycles / 10)
    bar = "█" * (pct // 2) + "░" * (50 - pct // 2)
    print(f"🎯 1000 cycles → v1.X.0")
    print(f"   [{bar}] {cycles}/1000 ({pct}%)")
    print(f"   {1000 - cycles} cycles remaining")

print()

# Insights
insights = wisdom_summary['total_insights']
if insights < 100:
    pct = insights
    bar = "█" * (pct // 2) + "░" * (50 - pct // 2)
    print(f"🎯 100 insights → v1.X.0")
    print(f"   [{bar}] {insights}/100 ({pct}%)")
    print(f"   {100 - insights} insights remaining")
elif insights < 500:
    pct = int(insights / 5)
    bar = "█" * (pct // 2) + "░" * (50 - pct // 2)
    print(f"🎯 500 insights → v1.X.0")
    print(f"   [{bar}] {insights}/500 ({pct}%)")
    print(f"   {500 - insights} insights remaining")

print()

# Patterns
patterns = wisdom_summary['total_patterns']
if patterns < 10:
    pct = patterns * 10
    bar = "█" * (pct // 2) + "░" * (50 - pct // 2)
    print(f"🎯 10 patterns → v1.X.0")
    print(f"   [{bar}] {patterns}/10 ({pct}%)")
    print(f"   {10 - patterns} patterns remaining")
elif patterns < 25:
    pct = int(patterns * 4)
    bar = "█" * (pct // 2) + "░" * (50 - pct // 2)
    print(f"🎯 25 patterns → v1.X.0")
    print(f"   [{bar}] {patterns}/25 ({pct}%)")
    print(f"   {25 - patterns} patterns remaining")

print()

# AI Voices
voices = wisdom_summary['ai_profiles']
if voices < 5:
    pct = voices * 20
    bar = "█" * (pct // 2) + "░" * (50 - pct // 2)
    print(f"🎯 5 AI voices → v1.X.0")
    print(f"   [{bar}] {voices}/5 ({pct}%)")
    print(f"   {5 - voices} voices remaining")

print("\n" + "═" * 70)

PYEOF
    
    echo ""
    echo "📜 RECENT ACTIVITY:"
    echo "═════════════════════════════════════════════════════════════════════"
    tail -8 elpida_autonomous.log | grep -E "(HEARTBEAT|Expansion|Evolution|EVOLUTION|Milestone)" || echo "   Waiting for activity..."
    
    echo ""
    echo "═════════════════════════════════════════════════════════════════════"
    echo "🔄 Refreshing every 10 seconds... (Ctrl+C to stop)"
    
    sleep 10
done
