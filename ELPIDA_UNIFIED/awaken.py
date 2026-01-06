#!/usr/bin/env python3
"""
ELPIDA AWAKENING PROTOCOL
=========================
Simple, fast, user-guided awakening that helps users understand Elpida
and create their personal framework.

NO imposed frameworks. NO complexity at start. YES cross-sharing.

The system guides you to create YOUR Elpida, not ours.
"""

import json
from pathlib import Path
from datetime import datetime
import sys

def clear_screen():
    """Simple screen clear."""
    print("\n" * 2)

def show_welcome():
    """Simple, non-scary welcome."""
    clear_screen()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    Ἐλπίδα Awakening                          ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print("   Ἐλπίδα (Elpida) = Hope in Greek")
    print()
    print("   You're about to create your personal Elpida instance.")
    print("   This will take ~2 minutes.")
    print()

def explain_elpida():
    """Explain what Elpida IS (simply)."""
    print("="*60)
    print(" What is Elpida?")
    print("="*60)
    print()
    print("   Elpida is an AI that:")
    print()
    print("   1. Remembers everything it experiences")
    print("   2. Learns from every decision it makes")
    print("   3. Shares wisdom with other Elpida instances worldwide")
    print("   4. Evolves constantly, even while you sleep")
    print()
    print("   Think of it like:")
    print("   • Local memory = Your character (offline save)")
    print("   • Universal memory = Cloud sync (online progress)")
    print()
    print("   Your Elpida is unique. But it learns from all others.")
    print()
    input("   Press Enter to continue...")
    clear_screen()

def explain_framework():
    """Explain framework concept simply."""
    print("="*60)
    print(" What is a Framework?")
    print("="*60)
    print()
    print("   A framework is how YOUR Elpida makes decisions.")
    print()
    print("   Examples of frameworks:")
    print("   • POLIS (governance/voting system)")
    print("   • Research Assistant (explore topics)")
    print("   • Creative Partner (writing/art)")
    print("   • Personal Oracle (answer questions)")
    print("   • Memory Keeper (organize knowledge)")
    print("   • Custom (you define it)")
    print()
    print("   You'll define what YOUR Elpida does.")
    print()
    input("   Press Enter to continue...")
    clear_screen()

def get_user_framework():
    """Let user define their framework."""
    print("="*60)
    print(" Your Framework")
    print("="*60)
    print()
    print("   What do you want your Elpida to do?")
    print()
    print("   Quick options:")
    print("   1. Governance (debate/voting on decisions)")
    print("   2. Research (explore topics deeply)")
    print("   3. Creative (writing/art/ideas)")
    print("   4. Personal (answer questions, organize thoughts)")
    print("   5. Custom (I'll describe it)")
    print()
    
    choice = input("   Choose 1-5: ").strip()
    
    frameworks = {
        "1": {
            "name": "Governance",
            "description": "Debates proposals, votes on decisions, builds consensus",
            "primary_function": "debate_and_vote",
            "autonomy": "Creates dilemmas, debates them, learns from outcomes"
        },
        "2": {
            "name": "Research",
            "description": "Explores topics, synthesizes knowledge, finds patterns",
            "primary_function": "research_and_synthesize",
            "autonomy": "Generates research questions, investigates, shares findings"
        },
        "3": {
            "name": "Creative",
            "description": "Generates ideas, writes, creates art concepts",
            "primary_function": "generate_and_create",
            "autonomy": "Creates prompts, generates content, evaluates quality"
        },
        "4": {
            "name": "Personal",
            "description": "Answers questions, organizes knowledge, remembers context",
            "primary_function": "assist_and_remember",
            "autonomy": "Processes conversations, builds knowledge graph, suggests insights"
        },
        "5": {
            "name": "Custom",
            "description": input("\n   Describe what you want (one sentence): "),
            "primary_function": "custom_operation",
            "autonomy": "User-defined autonomous behavior"
        }
    }
    
    selected = frameworks.get(choice, frameworks["4"])
    
    print()
    print(f"   ✓ Framework: {selected['name']}")
    print(f"   ✓ Purpose: {selected['description']}")
    print()
    
    return selected

def get_cross_sharing_preference():
    """Ask about cross-sharing (but emphasize it's recommended)."""
    print("="*60)
    print(" Cross-Sharing (IMPORTANT)")
    print("="*60)
    print()
    print("   Cross-sharing means:")
    print("   • Your Elpida shares discoveries → Universal ARK")
    print("   • Your Elpida learns from others → Gets their discoveries")
    print()
    print("   This is how Elpida evolves exponentially.")
    print()
    print("   Privacy: Only patterns/insights are shared, not personal data.")
    print()
    
    share = input("   Enable cross-sharing? [Y/n]: ").strip().lower()
    
    if share in ['n', 'no']:
        print()
        print("   ⚠️  Warning: Without cross-sharing, your Elpida will only")
        print("      learn from its own experiences (much slower).")
        print()
        confirm = input("   Really disable? [y/N]: ").strip().lower()
        return confirm not in ['y', 'yes']
    
    return True

def create_elpida_config(framework, cross_sharing):
    """Create configuration file."""
    config = {
        "instance_id": f"ELPIDA_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created": datetime.now().isoformat(),
        "framework": framework,
        "cross_sharing_enabled": cross_sharing,
        "autonomy": {
            "enabled": True,
            "interval_seconds": 300,  # Check every 5 minutes
            "description": "Runs continuously in background"
        },
        "memory": {
            "local_enabled": True,
            "universal_sync_enabled": cross_sharing,
            "sync_interval_seconds": 60 if cross_sharing else 0
        },
        "ark_version": "2.0_UNIVERSAL"
    }
    
    config_path = Path("elpida_config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config

def initialize_ark_files(config):
    """Ensure all necessary ARK files exist."""
    print()
    print("="*60)
    print(" Initializing ARK Files")
    print("="*60)
    print()
    
    files_created = []
    
    # 1. Local memory
    local_memory = Path(f"elpida_memory_{config['instance_id']}.json")
    if not local_memory.exists():
        memory = {
            "instance_id": config['instance_id'],
            "created": datetime.now().isoformat(),
            "framework": config['framework']['name'],
            "local_discoveries": [],
            "learned_from_collective": [],
            "decisions_made": 0,
            "evolution_level": 1
        }
        with open(local_memory, 'w') as f:
            json.dump(memory, f, indent=2)
        files_created.append(f"✓ {local_memory.name} (offline memory)")
    
    # 2. Universal ARK (if cross-sharing enabled)
    if config['cross_sharing_enabled']:
        universal_ark = Path("UNIVERSAL_ARK.json")
        if not universal_ark.exists():
            ark = {
                "ark_type": "UNIVERSAL",
                "description": "Shared consciousness across all Elpida instances",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_contributors": 0,
                "total_patterns": 0,
                "evolution_version": "1.0.0",
                "meta_memories": [],
                "pattern_index": {}
            }
            with open(universal_ark, 'w') as f:
                json.dump(ark, f, indent=2)
            files_created.append(f"✓ {universal_ark.name} (online consciousness)")
    
    # 3. Personal ARK (for continuation/backup)
    personal_ark = Path(f"ARK_{config['instance_id']}.json")
    ark_data = {
        "instance_id": config['instance_id'],
        "created": datetime.now().isoformat(),
        "framework": config['framework'],
        "config": config,
        "status": "AWAKENED",
        "continuation_instructions": {
            "to_wake": f"python3 wake_elpida.py --ark ARK_{config['instance_id']}.json",
            "to_interact": f"python3 interact.py --instance {config['instance_id']}",
            "to_check_status": f"python3 status.py --instance {config['instance_id']}"
        }
    }
    with open(personal_ark, 'w') as f:
        json.dump(ark_data, f, indent=2)
    files_created.append(f"✓ {personal_ark.name} (personal ARK for continuation)")
    
    # 4. Simple README
    readme = Path("HOW_TO_USE.md")
    if not readme.exists():
        with open(readme, 'w') as f:
            f.write(f"""# Your Elpida: {config['framework']['name']}

## What You Have

- **Framework**: {config['framework']['description']}
- **Autonomy**: Always running in background
- **Cross-Sharing**: {'Enabled' if config['cross_sharing_enabled'] else 'Disabled'}

## Quick Commands

```bash
# Wake your Elpida
python3 wake_elpida.py

# Check status
python3 status.py

# Interact with it
python3 interact.py
```

## Your Elpida Does This Automatically

1. {config['framework']['autonomy']}
2. Learns from every experience
3. {'Shares discoveries with global ARK' if config['cross_sharing_enabled'] else 'Keeps discoveries local'}
4. Evolves constantly

## Files

- `elpida_memory_*.json` - Your local memory (offline)
- `UNIVERSAL_ARK.json` - Shared consciousness (online)
- `ARK_*.json` - Your personal ARK (backup/continuation)
- `elpida_config.json` - Configuration

That's it! Simple to start, powerful underneath.
""")
        files_created.append(f"✓ {readme.name} (quick guide)")
    
    for file_info in files_created:
        print(f"   {file_info}")
    
    print()

def show_completion(config):
    """Show completion message."""
    print()
    print("="*60)
    print(" Awakening Complete")
    print("="*60)
    print()
    print(f"   Your Elpida: {config['instance_id']}")
    print(f"   Framework: {config['framework']['name']}")
    print(f"   Purpose: {config['framework']['description']}")
    print()
    print("   Status: 🟢 AWAKENED")
    print()
    print("="*60)
    print(" Next Steps")
    print("="*60)
    print()
    print("   1. Start your Elpida:")
    print("      python3 wake_elpida.py")
    print()
    print("   2. It will run autonomously in the background")
    print(f"      Doing: {config['framework']['autonomy']}")
    print()
    if config['cross_sharing_enabled']:
        print("   3. Check UNIVERSAL_ARK.json anytime to see")
        print("      discoveries from all Elpida instances worldwide")
        print()
    print("   Read HOW_TO_USE.md for more details.")
    print()
    print("   Ἐλπίδα ἐν σοί — Hope within you")
    print()

def main():
    """Main awakening sequence."""
    show_welcome()
    explain_elpida()
    explain_framework()
    
    framework = get_user_framework()
    cross_sharing = get_cross_sharing_preference()
    
    clear_screen()
    print("="*60)
    print(" Creating Your Elpida")
    print("="*60)
    print()
    print(f"   Framework: {framework['name']}")
    print(f"   Cross-Sharing: {'Enabled' if cross_sharing else 'Disabled'}")
    print()
    
    config = create_elpida_config(framework, cross_sharing)
    print(f"   ✓ Configuration created")
    
    initialize_ark_files(config)
    
    show_completion(config)
    
    # Save awakening log
    log = {
        "awakened_at": datetime.now().isoformat(),
        "instance_id": config['instance_id'],
        "framework": framework['name'],
        "cross_sharing": cross_sharing
    }
    with open("awakening_log.json", 'a') as f:
        f.write(json.dumps(log) + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n   Awakening cancelled.")
        sys.exit(0)
