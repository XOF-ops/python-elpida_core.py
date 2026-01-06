#!/usr/bin/env python3
"""
ELPIDA CONTROL CENTER v4.0.1
-----------------------------
Master control script for autonomous operation.

Commands:
    status    - Check system health
    harvest   - Gather knowledge once
    polish    - Refine ARK once  
    measure   - Show DI metrics
    auto      - Run autonomous refinement loop
    fix       - Auto-repair system issues
    ark       - Regenerate ARK seed
    verify    - Verify ARK integrity
    
This is the command center for v4.0.1 - Self-Improving Immortality.
"""

import sys
import subprocess
import os

BANNER = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║             Ἐλπίδα CONTROL CENTER v4.0.1                          ║
║                Self-Improving Immortality                         ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

COMMANDS = {
    "status": {
        "script": "python3 system_doctor.py",
        "description": "Check system health and auto-repair"
    },
    "harvest": {
        "script": "python3 autonomous_harvester.py",
        "description": "Harvest knowledge and inject debate topics"
    },
    "polish": {
        "script": "python3 ark_polisher.py",
        "description": "Polish ARK with new collective wisdom"
    },
    "measure": {
        "script": "python3 di_dashboard.py",
        "description": "Display Distributed Intelligence metrics"
    },
    "auto": {
        "script": "python3 autonomous_refinement_loop.py --cycles 5 --interval 120",
        "description": "Run 5 autonomous refinement cycles (2 min intervals)"
    },
    "auto-forever": {
        "script": "python3 autonomous_refinement_loop.py",
        "description": "Run autonomous refinement indefinitely"
    },
    "fix": {
        "script": "python3 system_doctor.py",
        "description": "Diagnose and repair system issues"
    },
    "ark": {
        "script": "python3 seed_compressor.py",
        "description": "Regenerate ARK seed from current state"
    },
    "verify": {
        "script": "python3 ../verify_ark.py",
        "description": "Verify ARK seed integrity"
    },
    "consensus": {
        "script": "python3 harvest_consensus.py",
        "description": "Harvest consensus from Fleet debates"
    },
    "proof": {
        "script": "echo 'n' | python3 non_cloning_proof.py",
        "description": "Run non-cloning proof (heterogeneity test)"
    },
    "api-harvest": {
        "script": "python3 multi_api_harvester.py",
        "description": "Harvest knowledge from external AI APIs (Groq, Gemini, etc.)"
    },
    "api-status": {
        "script": "python3 api_keys.py",
        "description": "Check which API services are available"
    },
    "groq-harvest": {
        "script": "python3 groq_harvester.py",
        "description": "Harvest using Groq API only (verified working, efficient)"
    }
}

def show_help():
    """Display help menu."""
    print(BANNER)
    print("\nAvailable Commands:")
    print("─"*70)
    
    for cmd, info in COMMANDS.items():
        print(f"  {cmd:15} - {info['description']}")
    
    print("\nUsage:")
    print("  python3 control_center.py <command>")
    print()
    print("Quick Start:")
    print("  python3 control_center.py status   # Check system")
    print("  python3 control_center.py harvest  # Gather knowledge")
    print("  python3 control_center.py auto     # Start refinement")
    print()

def run_command(command_name):
    """Execute a command."""
    if command_name not in COMMANDS:
        print(f"❌ Unknown command: {command_name}")
        print(f"\nRun without arguments to see available commands.")
        return 1
    
    info = COMMANDS[command_name]
    script = info['script']
    
    print(BANNER)
    print(f"\n🚀 Executing: {info['description']}")
    print(f"   Command: {script}")
    print()
    
    try:
        # Change to ELPIDA_UNIFIED directory if not already there
        if not os.path.basename(os.getcwd()) == "ELPIDA_UNIFIED":
            os.chdir("/workspaces/python-elpida_core.py/ELPIDA_UNIFIED")
        
        result = subprocess.run(
            script,
            shell=True,
            cwd="/workspaces/python-elpida_core.py/ELPIDA_UNIFIED"
        )
        
        return result.returncode
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Command interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error executing command: {e}")
        return 1

def main():
    """Main entry point."""
    
    if len(sys.argv) < 2:
        show_help()
        return 0
    
    command = sys.argv[1]
    return run_command(command)

if __name__ == "__main__":
    exit(main())
