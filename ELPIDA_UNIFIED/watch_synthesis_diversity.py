#!/usr/bin/env python3
"""Watch for synthesis diversity in real-time"""
import json
import time
from collections import Counter

print("🔍 Watching for synthesis diversity...")
print("=" * 80)

last_count = 0
synthesis_types = Counter()

while True:
    try:
        with open('synthesis_resolutions.jsonl', 'r') as f:
            lines = f.readlines()
            
        current_count = len(lines)
        
        if current_count > last_count:
            # New synthesis!
            new_lines = lines[last_count:]
            for line in new_lines:
                data = json.loads(line)
                synthesis_action = data.get('synthesis_action', 'UNKNOWN')
                conflict = data.get('conflict_detected', 'UNKNOWN')
                
                synthesis_types[synthesis_action] += 1
                
                print(f"\n✨ NEW SYNTHESIS #{current_count}")
                print(f"   Conflict:  {conflict}")
                print(f"   Action:    {synthesis_action}")
                print(f"\n📊 DIVERSITY REPORT:")
                for action, count in synthesis_types.most_common():
                    print(f"   {action}: {count}")
                print("=" * 80)
                
            last_count = current_count
            
        time.sleep(5)
        
    except FileNotFoundError:
        print("⏳ Waiting for synthesis_resolutions.jsonl...")
        time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped")
        break
    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(5)
