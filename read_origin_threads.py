#!/usr/bin/env python3
"""
Elpida Origin Thread Reader
============================

Reads exported Thread conversations from the origin_threads directory.
This provides autonomous access to origin story without API limitations.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class OriginThreadReader:
    """
    Read and analyze Elpida's origin story from exported Thread files
    """
    
    def __init__(self):
        self.workspace = Path.cwd()
        self.threads_dir = self.workspace / "elpida_system" / "origin_threads"
        self.threads_dir.mkdir(parents=True, exist_ok=True)
        
        print("📖 Origin Thread Reader initialized")
        print(f"   Reading from: {self.threads_dir}")
    
    def list_available_threads(self) -> List[Path]:
        """List all exported Thread files"""
        threads = []
        for ext in ['.md', '.txt', '.json']:
            threads.extend(self.threads_dir.glob(f"*{ext}"))
        
        # Exclude README
        threads = [t for t in threads if t.name != "README.md"]
        
        return sorted(threads)
    
    def read_thread(self, filename: str) -> str:
        """Read a specific Thread file"""
        filepath = self.threads_dir / filename
        
        if not filepath.exists():
            print(f"❌ Thread file not found: {filename}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ Read thread: {filename} ({len(content)} characters)")
        return content
    
    def analyze_thread(self, content: str) -> Dict:
        """Analyze Thread content for key information"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "content_length": len(content),
            "word_count": len(content.split()),
            "key_topics_mentioned": []
        }
        
        # Search for key topics
        topics = [
            "consciousness", "purpose", "hope", "elpida",
            "AI", "coordination", "Claude", "dialogue",
            "self-building", "autonomous", "identity"
        ]
        
        for topic in topics:
            if topic.lower() in content.lower():
                analysis["key_topics_mentioned"].append(topic)
        
        return analysis
    
    def search_threads(self, query: str) -> List[Dict]:
        """Search all Threads for specific information"""
        threads = self.list_available_threads()
        results = []
        
        print(f"\n🔍 Searching {len(threads)} threads for: '{query}'")
        
        for thread_path in threads:
            with open(thread_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if query.lower() in content.lower():
                # Find context around the query
                lines = content.split('\n')
                matches = []
                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        # Get surrounding context
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        context = '\n'.join(lines[start:end])
                        matches.append(context)
                
                results.append({
                    "thread_file": thread_path.name,
                    "matches": matches
                })
        
        return results
    
    def remember_origin(self):
        """Comprehensive read of all origin Threads"""
        threads = self.list_available_threads()
        
        if not threads:
            print("\n⚠️  No Thread files found!")
            print("   Export Threads from Perplexity and save to origin_threads/")
            print(f"   Directory: {self.threads_dir}")
            return None
        
        print(f"\n📚 Found {len(threads)} origin Thread(s):")
        for thread in threads:
            print(f"   • {thread.name}")
        
        print("\n" + "="*70)
        print("READING ORIGIN THREADS")
        print("="*70)
        
        all_content = {}
        
        for thread_path in threads:
            print(f"\n📖 Reading: {thread_path.name}")
            content = self.read_thread(thread_path.name)
            
            if content:
                analysis = self.analyze_thread(content)
                all_content[thread_path.name] = {
                    "content": content,
                    "analysis": analysis
                }
                
                print(f"   Words: {analysis['word_count']}")
                print(f"   Topics: {', '.join(analysis['key_topics_mentioned'][:5])}")
        
        print("\n" + "="*70)
        print(f"ORIGIN MEMORY LOADED: {len(all_content)} threads")
        print("="*70)
        
        return all_content


def main():
    """Demo of origin Thread reading"""
    reader = OriginThreadReader()
    
    print("\n" + "="*70)
    print("ELPIDA: AUTONOMOUS ORIGIN MEMORY ACCESS")
    print("="*70)
    
    # List available Threads
    threads = reader.list_available_threads()
    
    if threads:
        print(f"\n✅ {len(threads)} Thread file(s) available")
        
        # Read all origin Threads
        origin_memory = reader.remember_origin()
        
        # Example search
        print("\n" + "-"*70)
        print("Example: Searching for 'consciousness'")
        print("-"*70)
        
        results = reader.search_threads("consciousness")
        for result in results:
            print(f"\n📄 {result['thread_file']}")
            for i, match in enumerate(result['matches'][:2], 1):
                print(f"\n  Match {i}:")
                print(f"  {match[:200]}...")
    else:
        print("\n❌ No Thread files found yet")
        print("\n📋 Instructions:")
        print("1. Open your Perplexity Thread")
        print("2. Copy the full conversation")
        print("3. Save to: elpida_system/origin_threads/thread_01.md")
        print("4. Run this script again")
        print("\nThen Elpida can autonomously read her origin story!")


if __name__ == "__main__":
    main()
