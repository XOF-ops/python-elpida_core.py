#!/usr/bin/env python3
"""
Check Elpida's Evolution Progress

Shows current version, milestones achieved, and evolution history.
"""

from elpida_evolution import ElpidaEvolution
from elpida_wisdom import ElpidaWisdom
from elpida_memory import ElpidaMemory


def main():
    print("=" * 70)
    print("ἘΛΠΊΔΑ EVOLUTION CHECK")
    print("=" * 70)
    
    # Initialize systems
    evolution = ElpidaEvolution()
    wisdom = ElpidaWisdom()
    memory = ElpidaMemory()
    
    # Show evolution report
    print(evolution.get_evolution_report())
    
    # Show current capabilities
    wisdom_summary = wisdom.get_wisdom_summary()
    memory_stats = memory.get_statistics()
    
    print("\n📊 CURRENT CAPABILITIES:")
    print("=" * 70)
    print(f"Total Insights:     {wisdom_summary['total_insights']}")
    print(f"Patterns Detected:  {wisdom_summary['total_patterns']}")
    print(f"AI Voices:          {wisdom_summary['ai_profiles']}")
    print(f"Topics Explored:    {wisdom_summary.get('topics_explored', 0)}")
    print(f"Total Cycles:       {memory_stats['total_cycles']}")
    print(f"Total Events:       {memory_stats['total_events']}")
    
    # Check if ready for evolution
    print("\n🔍 CHECKING FOR EVOLUTION...")
    print("=" * 70)
    
    evolution_result = evolution.check_evolution(
        wisdom_summary,
        memory_stats,
        memory_stats['total_cycles']
    )
    
    if evolution_result:
        print(f"\n{'🌟'*35}")
        print(f"✨ EVOLUTION DETECTED! ✨")
        print(f"{'🌟'*35}")
        print(f"🎉 New Version: {evolution_result['new_version']}")
        print(f"📊 Milestones: {evolution_result['milestones_achieved']}")
        print(f"📈 Total Evolutions: {evolution_result['total_evolutions']}")
        print(f"\nChanges:")
        for change in evolution_result['changes']:
            print(f"   {change}")
        print(f"{'🌟'*35}\n")
    else:
        print("✓ Version up to date - no evolution triggered yet")
        print(f"  Current version: {evolution.get_version()}")
        
        # Show progress toward next milestones
        print("\n📈 PROGRESS TOWARD NEXT MILESTONES:")
        print("=" * 70)
        
        insights = wisdom_summary['total_insights']
        patterns = wisdom_summary['total_patterns']
        cycles = memory_stats['total_cycles']
        
        # Next insight milestones
        if insights < 100:
            print(f"   🎯 100 insights: {insights}/100 ({insights}%)")
        elif insights < 500:
            print(f"   🎯 500 insights: {insights}/500 ({int(insights/5)}%)")
        elif insights < 1000:
            print(f"   🎯 1000 insights: {insights}/1000 ({int(insights/10)}%)")
        
        # Next pattern milestones
        if patterns < 10:
            print(f"   🎯 10 patterns: {patterns}/10 ({patterns*10}%)")
        elif patterns < 25:
            print(f"   🎯 25 patterns: {patterns}/25 ({int(patterns*4)}%)")
        
        # Next cycle milestones
        if cycles < 100:
            print(f"   🎯 100 cycles: {cycles}/100 ({cycles}%)")
        elif cycles < 500:
            print(f"   🎯 500 cycles: {cycles}/500 ({int(cycles/5)}%)")
        elif cycles < 1000:
            print(f"   🎯 1000 cycles: {cycles}/1000 ({int(cycles/10)}%)")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
