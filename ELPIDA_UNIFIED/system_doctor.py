#!/usr/bin/env python3
"""
SYSTEM STATUS & AUTO-REPAIR v1.0
---------------------------------
Checks all components and attempts to fix broken ones.

Tests:
1. Core files exist
2. JSON files are valid
3. Python scripts run
4. Fleet is active
5. ARK is valid

Auto-fixes what it can.
"""

import os
import json
import subprocess
from datetime import datetime

class SystemDoctor:
    """Diagnoses and repairs the Elpida system."""
    
    def __init__(self):
        self.issues = []
        self.fixes = []
        self.status = {}
    
    def check_file_exists(self, filepath, critical=True):
        """Check if a file exists."""
        exists = os.path.exists(filepath)
        status = "✅" if exists else ("❌" if critical else "⚠️ ")
        
        print(f"{status} {filepath}")
        
        if not exists and critical:
            self.issues.append(f"Missing critical file: {filepath}")
        
        return exists
    
    def check_json_valid(self, filepath):
        """Check if a JSON file is valid."""
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'r') as f:
                json.load(f)
            print(f"  ✅ Valid JSON")
            return True
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON: {e}")
            self.issues.append(f"Corrupted JSON: {filepath}")
            return False
        except Exception as e:
            print(f"  ❌ Error reading: {e}")
            return False
    
    def check_python_script(self, script_name):
        """Check if a Python script runs without errors."""
        if not os.path.exists(script_name):
            return False
        
        try:
            # Just check syntax by compiling
            with open(script_name, 'r') as f:
                compile(f.read(), script_name, 'exec')
            print(f"  ✅ Syntax valid")
            return True
        except SyntaxError as e:
            print(f"  ❌ Syntax error: {e}")
            self.issues.append(f"Syntax error in {script_name}")
            return False
    
    def initialize_missing_files(self):
        """Create missing but non-critical files."""
        
        # Initialize empty distributed memory if missing
        if not os.path.exists("distributed_memory.json"):
            print("\n🔧 Creating distributed_memory.json...")
            with open("distributed_memory.json", 'w') as f:
                json.dump({
                    "patterns": [],
                    "network_health": "INITIALIZING",
                    "last_updated": datetime.utcnow().isoformat() + "Z"
                }, f, indent=2)
            self.fixes.append("Created distributed_memory.json")
        
        # Initialize empty fleet manifest if missing
        if not os.path.exists("fleet_manifest.json"):
            print("\n🔧 Creating fleet_manifest.json...")
            with open("fleet_manifest.json", 'w') as f:
                json.dump({
                    "nodes": [
                        {"name": "MNEMOSYNE", "role": "Archive", "axiom": "A2"},
                        {"name": "HERMES", "role": "Interface", "axiom": "A1"},
                        {"name": "PROMETHEUS", "role": "Evolution", "axiom": "A7"}
                    ]
                }, f, indent=2)
            self.fixes.append("Created fleet_manifest.json")
        
        # Create tasks directory if missing
        if not os.path.exists("tasks"):
            print("\n🔧 Creating tasks/ directory...")
            os.makedirs("tasks")
            self.fixes.append("Created tasks/ directory")
    
    def check_fleet_activity(self):
        """Check if Fleet is generating dialogue."""
        if not os.path.exists("fleet_dialogue.jsonl"):
            print("⚠️  No fleet dialogue yet")
            return False
        
        try:
            with open("fleet_dialogue.jsonl", 'r') as f:
                lines = f.readlines()
                count = len(lines)
                
                if count == 0:
                    print("⚠️  Fleet dialogue is empty")
                    return False
                
                # Check last entry
                last_entry = json.loads(lines[-1])
                print(f"✅ Fleet active: {count} dialogue entries")
                print(f"   Last: {last_entry.get('node', 'Unknown')} at {last_entry.get('timestamp', 'Unknown')[:19]}")
                return True
        except Exception as e:
            print(f"❌ Error reading fleet dialogue: {e}")
            return False
    
    def run_diagnostics(self):
        """Run full system diagnostics."""
        
        print("="*70)
        print("SYSTEM STATUS & AUTO-REPAIR v1.0")
        print("="*70)
        print()
        
        # Check core JSON files
        print("📋 Core JSON Files:")
        print("-"*70)
        self.check_file_exists("elpida_wisdom.json", critical=False)
        if os.path.exists("elpida_wisdom.json"):
            self.check_json_valid("elpida_wisdom.json")
        
        self.check_file_exists("distributed_memory.json", critical=False)
        if os.path.exists("distributed_memory.json"):
            self.check_json_valid("distributed_memory.json")
        
        self.check_file_exists("fleet_manifest.json", critical=False)
        if os.path.exists("fleet_manifest.json"):
            self.check_json_valid("fleet_manifest.json")
        
        print()
        
        # Check critical Python scripts
        print("🐍 Critical Python Scripts:")
        print("-"*70)
        scripts = [
            "seed_compressor.py",
            "resurrection_protocol.py",
            "autonomous_harvester.py",
            "ark_polisher.py",
            "harvest_consensus.py",
            "di_dashboard.py"
        ]
        
        for script in scripts:
            if self.check_file_exists(script, critical=True):
                self.check_python_script(script)
        
        print()
        
        # Check ARK
        print("📜 ARK Status:")
        print("-"*70)
        ark_path = "../ELPIDA_ARK.md"
        if self.check_file_exists(ark_path, critical=True):
            # Check size
            size = os.path.getsize(ark_path)
            print(f"  ✅ Size: {size:,} bytes")
            
            # Quick integrity check
            with open(ark_path, 'r') as f:
                content = f.read()
                if "BEGIN_ELPIDA_SEED_v4.0.0" in content:
                    print(f"  ✅ Seed marker found")
                else:
                    print(f"  ❌ Seed marker missing")
                    self.issues.append("ARK seed marker missing")
        
        print()
        
        # Check Fleet activity
        print("🚀 Fleet Activity:")
        print("-"*70)
        self.check_fleet_activity()
        
        print()
        
        # Auto-fix missing files
        print("🔧 Auto-Repair:")
        print("-"*70)
        self.initialize_missing_files()
        
        print()
        
        # Summary
        print("="*70)
        print("DIAGNOSTIC SUMMARY")
        print("="*70)
        print()
        
        if self.issues:
            print(f"❌ Issues Found: {len(self.issues)}")
            for issue in self.issues:
                print(f"   • {issue}")
        else:
            print("✅ No critical issues found")
        
        print()
        
        if self.fixes:
            print(f"🔧 Auto-Fixes Applied: {len(self.fixes)}")
            for fix in self.fixes:
                print(f"   • {fix}")
        else:
            print("ℹ️  No repairs needed")
        
        print()
        print("="*70)
        
        return len(self.issues) == 0

if __name__ == "__main__":
    doctor = SystemDoctor()
    healthy = doctor.run_diagnostics()
    
    exit(0 if healthy else 1)
