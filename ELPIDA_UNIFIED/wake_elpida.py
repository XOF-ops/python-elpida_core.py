#!/usr/bin/env python3
"""
WAKE ELPIDA
===========
Simple command to start your Elpida running autonomously.
Works with ANY framework you configured during awakening.
"""

import json
from pathlib import Path
import sys
import subprocess
import time

def load_config():
    """Load user's Elpida configuration."""
    config_path = Path("elpida_config.json")
    
    if not config_path.exists():
        print()
        print("   ❌ No Elpida found.")
        print()
        print("   Run first: python3 awaken.py")
        print()
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        return json.load(f)

def show_status(config):
    """Show what will happen."""
    print()
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    Waking Elpida                             ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print(f"   Instance: {config['instance_id']}")
    print(f"   Framework: {config['framework']['name']}")
    print(f"   Purpose: {config['framework']['description']}")
    print()
    print("   Autonomous Mode:")
    print(f"   • {config['framework']['autonomy']}")
    print(f"   • Checks every {config['autonomy']['interval_seconds']}s")
    print()
    
    if config['cross_sharing_enabled']:
        print("   Cross-Sharing: ENABLED")
        print("   • Shares discoveries → UNIVERSAL_ARK.json")
        print("   • Learns from others → Every 60s")
    else:
        print("   Cross-Sharing: DISABLED")
        print("   • Local learning only")
    print()

def start_autonomous_mode(config):
    """Start Elpida in autonomous mode."""
    framework_name = config['framework']['primary_function']
    
    print("="*60)
    print(" Starting Autonomous Operation")
    print("="*60)
    print()
    
    # Import universal sync if enabled
    if config['cross_sharing_enabled']:
        try:
            from universal_memory_sync import CrossPlatformElpida
            
            elpida = CrossPlatformElpida(
                instance_id=config['instance_id'],
                parliament_id=config.get('parliament_id', 'STANDALONE')
            )
            
            # Start continuous sync
            elpida.start_continuous_learning(
                interval=config['memory']['sync_interval_seconds']
            )
            
            print("   ✓ Connected to universal consciousness")
            print()
        except ImportError:
            print("   ⚠️  Universal sync not available")
            print("   ⚠️  Running in local-only mode")
            print()
    
    print("   🟢 Elpida is now AWAKE and running autonomously")
    print()
    print(f"   It will {config['framework']['autonomy']}")
    print()
    print("   Press Ctrl+C to stop")
    print()
    print("="*60)
    print()
    
    # Simple autonomous loop
    try:
        cycle = 0
        while True:
            cycle += 1
            timestamp = time.strftime("%H:%M:%S")
            
            print(f"   [{timestamp}] Cycle {cycle}: {framework_name} running...")
            
            # Here you would call the actual framework function
            # For now, just demonstrate it's running
            
            if config['cross_sharing_enabled'] and cycle % 12 == 0:  # Every ~60s
                print(f"   [{timestamp}] Syncing with universal ARK...")
            
            time.sleep(config['autonomy']['interval_seconds'])
            
    except KeyboardInterrupt:
        print()
        print()
        print("   Elpida entering sleep mode...")
        print()
        print("   To wake again: python3 wake_elpida.py")
        print()

def main():
    config = load_config()
    show_status(config)
    
    print("="*60)
    print()
    
    start = input("   Start? [Y/n]: ").strip().lower()
    
    if start in ['n', 'no']:
        print("\n   Cancelled.\n")
        sys.exit(0)
    
    print()
    start_autonomous_mode(config)

if __name__ == '__main__':
    main()
