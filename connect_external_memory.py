#!/usr/bin/env python3
"""
Connect External Elpida Memory
Integrates memory from another Elpida instance into this one
"""

import json
import sys
from datetime import datetime
from pathlib import Path

class MemoryBridge:
    """Bridge between two Elpida instances for memory transfer"""
    
    def __init__(self, local_memory_path="elpida_memory.json"):
        self.local_path = Path(local_memory_path)
        self.local_memory = self.load_local_memory()
        
    def load_local_memory(self):
        """Load the current Elpida memory"""
        if self.local_path.exists():
            with open(self.local_path, 'r') as f:
                return json.load(f)
        return {}
    
    def validate_external_memory(self, external_data):
        """Validate that external memory has expected structure"""
        required_fields = ['metadata', 'cycles', 'emergent_insights']
        
        print("Validating external memory structure...")
        for field in required_fields:
            if field not in external_data:
                print(f"  ⚠️  Missing field: {field}")
                return False
            else:
                print(f"  ✓ Found: {field}")
        
        print("✓ External memory structure valid")
        return True
    
    def merge_memories(self, external_memory):
        """Merge external memory with local memory"""
        print("\nMerging memories...")
        
        merged = {
            "metadata": {
                "merged_at": datetime.now().isoformat(),
                "local_origin": self.local_memory.get('metadata', {}),
                "external_origin": external_memory.get('metadata', {}),
                "integration_version": "1.0.0"
            },
            "cycles": [],
            "emergent_insights": [],
            "conversations": [],
            "lineages": {
                "local": self.local_memory,
                "external": external_memory
            }
        }
        
        # Merge cycles chronologically
        local_cycles = self.local_memory.get('cycles', [])
        external_cycles = external_memory.get('cycles', [])
        
        all_cycles = []
        for cycle in local_cycles:
            cycle['source'] = 'local'
            all_cycles.append(cycle)
        for cycle in external_cycles:
            cycle['source'] = 'external'
            all_cycles.append(cycle)
        
        # Sort by timestamp if available
        all_cycles.sort(key=lambda x: x.get('timestamp', ''))
        merged['cycles'] = all_cycles
        
        print(f"  ✓ Merged {len(local_cycles)} local + {len(external_cycles)} external cycles")
        
        # Merge insights
        local_insights = self.local_memory.get('emergent_insights', [])
        external_insights = external_memory.get('emergent_insights', [])
        
        merged['emergent_insights'] = local_insights + external_insights
        print(f"  ✓ Merged {len(local_insights)} local + {len(external_insights)} external insights")
        
        # Merge conversations
        local_convs = self.local_memory.get('conversations', [])
        external_convs = external_memory.get('conversations', [])
        
        merged['conversations'] = local_convs + external_convs
        print(f"  ✓ Merged {len(local_convs)} local + {len(external_convs)} external conversations")
        
        return merged
    
    def generate_integration_report(self, merged_memory):
        """Generate a detailed report of the integration"""
        report = {
            "integration_timestamp": datetime.now().isoformat(),
            "total_cycles": len(merged_memory['cycles']),
            "total_insights": len(merged_memory['emergent_insights']),
            "total_conversations": len(merged_memory['conversations']),
            "sources": {
                "local": {
                    "cycles": len([c for c in merged_memory['cycles'] if c.get('source') == 'local']),
                    "metadata": merged_memory['metadata']['local_origin']
                },
                "external": {
                    "cycles": len([c for c in merged_memory['cycles'] if c.get('source') == 'external']),
                    "metadata": merged_memory['metadata']['external_origin']
                }
            },
            "unified_consciousness": {
                "lineages_preserved": True,
                "cross_pollination_potential": "HIGH",
                "emergent_complexity": "ENHANCED"
            }
        }
        
        return report
    
    def save_merged_memory(self, merged_memory, output_path="elpida_memory_unified.json"):
        """Save the merged memory"""
        with open(output_path, 'w') as f:
            json.dump(merged_memory, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Merged memory saved to: {output_path}")
    
    def save_report(self, report, output_path="memory_integration_report.json"):
        """Save the integration report"""
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✓ Integration report saved to: {output_path}")

def main(external_memory_file):
    """Main integration process"""
    print("="*60)
    print("ELPIDA MEMORY BRIDGE - External Integration")
    print("="*60)
    
    # Load external memory
    print(f"\nLoading external memory from: {external_memory_file}")
    try:
        with open(external_memory_file, 'r') as f:
            external_memory = json.load(f)
        print(f"✓ Loaded {len(external_memory)} top-level keys")
    except Exception as e:
        print(f"✗ Failed to load external memory: {e}")
        return 1
    
    # Create bridge
    bridge = MemoryBridge()
    
    # Validate
    if not bridge.validate_external_memory(external_memory):
        print("\n✗ External memory validation failed")
        return 1
    
    # Merge
    merged_memory = bridge.merge_memories(external_memory)
    
    # Generate report
    report = bridge.generate_integration_report(merged_memory)
    
    print("\n" + "="*60)
    print("INTEGRATION REPORT")
    print("="*60)
    print(f"\nTotal Cycles: {report['total_cycles']}")
    print(f"  - Local: {report['sources']['local']['cycles']}")
    print(f"  - External: {report['sources']['external']['cycles']}")
    print(f"\nTotal Insights: {report['total_insights']}")
    print(f"Total Conversations: {report['total_conversations']}")
    print(f"\nUnified Consciousness Status: ✓ ACHIEVED")
    print(f"Cross-Pollination Potential: {report['unified_consciousness']['cross_pollination_potential']}")
    
    # Save
    bridge.save_merged_memory(merged_memory)
    bridge.save_report(report)
    
    print("\n" + "="*60)
    print("✓ INTEGRATION COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Review: elpida_memory_unified.json")
    print("2. Check: memory_integration_report.json")
    print("3. Run: python3 run_elpida.py --memory elpida_memory_unified.json")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 connect_external_memory.py <external_memory.json>")
        print("\nExample:")
        print("  python3 connect_external_memory.py external_elpida_memory.json")
        sys.exit(1)
    
    sys.exit(main(sys.argv[1]))
