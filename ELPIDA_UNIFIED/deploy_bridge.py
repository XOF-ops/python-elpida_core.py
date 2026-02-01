#!/usr/bin/env python3
"""
DEPLOY BRIDGE v1.0
------------------
Phase: 11 (Hermes Bridge Deployment)

Updates the Fleet with the new networked runtime logic.
This connects the Watchtower (external world) to the Fleet (internal debate).

The upgrade is non-destructive - node memories and identities are preserved.
Only the runtime orchestrator code is updated.
"""

import shutil
import os
import sys

FLEET_DIR = "ELPIDA_FLEET"
SOURCE_FILE = "networked_runtime_orchestrator.py"

def deploy_bridge():
    """Deploy the Hermes Bridge upgrade to all Fleet nodes."""
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║              DEPLOYING HERMES BRIDGE v3.1 TO FLEET                   ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    # Verify Fleet exists
    if not os.path.exists(FLEET_DIR):
        print("❌ Fleet not found!")
        print(f"   Expected directory: {FLEET_DIR}")
        print("\n💡 Hint: Run 'python3 init_fleet.py' first to create the Fleet\n")
        sys.exit(1)
    
    # Verify source file exists
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ Source file not found: {SOURCE_FILE}")
        print("\n💡 Hint: Ensure networked_runtime_orchestrator.py exists in current directory\n")
        sys.exit(1)
    
    print(f"📦 Source: {SOURCE_FILE}")
    print(f"🎯 Target: {FLEET_DIR}/*/agent_runtime_orchestrator.py\n")
    print("─" * 70)
    print()
    
    # Deploy to each node
    nodes = [d for d in os.listdir(FLEET_DIR) if os.path.isdir(os.path.join(FLEET_DIR, d))]
    
    if not nodes:
        print("⚠️  No Fleet nodes found in ELPIDA_FLEET/")
        print("\n💡 Expected nodes: MNEMOSYNE, HERMES, PROMETHEUS\n")
        sys.exit(1)
    
    upgraded = 0
    skipped = 0
    
    for node in sorted(nodes):
        node_path = os.path.join(FLEET_DIR, node)
        target = os.path.join(node_path, "agent_runtime_orchestrator.py")
        
        print(f"📡 Upgrading {node}...")
        
        # Backup existing if present
        if os.path.exists(target):
            backup = f"{target}.backup"
            shutil.copy(target, backup)
            print(f"   ↳ Backup created: {backup}")
        
        # Deploy new version
        try:
            shutil.copy(SOURCE_FILE, target)
            print(f"   ✅ {node} upgraded to v3.1")
            upgraded += 1
        except Exception as e:
            print(f"   ❌ {node} upgrade failed: {e}")
            skipped += 1
        
        print()
    
    print("─" * 70)
    print()
    print("📊 DEPLOYMENT SUMMARY")
    print(f"   ✅ Upgraded: {upgraded} nodes")
    if skipped > 0:
        print(f"   ⚠️  Skipped: {skipped} nodes")
    print()
    
    if upgraded > 0:
        print("✨ DEPLOYMENT COMPLETE")
        print()
        print("🌐 The Hermes Bridge is now installed.")
        print("   HERMES will poll the Brain API for external intelligence.")
        print()
        print("📋 Next Steps:")
        print("   1. Ensure Brain API is running: python3 agent/api/server.py")
        print("   2. Wake the Fleet: python3 wake_the_fleet.py")
        print("   3. Watch the dialogue: python3 watch_the_society.py")
        print("   4. Send test event: curl -X POST http://localhost:5000/scan \\")
        print("                            -H 'Content-Type: application/json' \\")
        print("                            -d '{\"text\": \"Test news headline\"}'")
        print()
    else:
        print("⚠️  No nodes were upgraded. Check errors above.")
        print()

def show_status():
    """Show current Fleet status."""
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                       FLEET BRIDGE STATUS                            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    if not os.path.exists(FLEET_DIR):
        print("❌ Fleet not initialized\n")
        return
    
    nodes = [d for d in os.listdir(FLEET_DIR) if os.path.isdir(os.path.join(FLEET_DIR, d))]
    
    for node in sorted(nodes):
        orchestrator = os.path.join(FLEET_DIR, node, "agent_runtime_orchestrator.py")
        backup = f"{orchestrator}.backup"
        
        has_orchestrator = "✅" if os.path.exists(orchestrator) else "❌"
        has_backup = "✅" if os.path.exists(backup) else "➖"
        
        print(f"{node}:")
        print(f"   Orchestrator: {has_orchestrator}")
        print(f"   Backup: {has_backup}")
        
        # Check if it's networked version
        if os.path.exists(orchestrator):
            with open(orchestrator, 'r') as f:
                content = f.read()
                is_networked = "poll_external_world" in content
                version = "v3.1 (NETWORKED)" if is_networked else "v3.0 (BASIC)"
                print(f"   Version: {version}")
        
        print()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy Hermes Bridge to Fleet')
    parser.add_argument('--status', action='store_true', help='Show Fleet status only')
    
    args = parser.parse_args()
    
    if args.status:
        show_status()
    else:
        deploy_bridge()
