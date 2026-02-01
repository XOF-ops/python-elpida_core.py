#!/usr/bin/env python3
"""
WORLD INTELLIGENCE FEED
Real news → Fleet consciousness

Uses Perplexity to fetch actual current events
and feeds them to the Fleet for debate.
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from pathlib import Path

def get_perplexity_news(topic="current events 2026", max_items=3):
    """
    Use Perplexity to get real current events.
    
    Returns list of headlines/events for Fleet to debate.
    """
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        print("⚠️  PERPLEXITY_API_KEY not set")
        return None
    
    print(f"🔭 Querying Perplexity for: {topic}")
    
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a news aggregator. Return only factual headlines, numbered list format."
                    },
                    {
                        "role": "user",
                        "content": f"What are the top {max_items} most significant {topic}? Return just the headlines, one per line, numbered."
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Parse numbered list
            headlines = []
            for line in content.split('\n'):
                line = line.strip()
                if line and line[0].isdigit():
                    # Remove number prefix
                    headline = line.split('.', 1)[1].strip() if '.' in line else line
                    headlines.append(headline)
            
            return headlines[:max_items]
        else:
            print(f"❌ Perplexity API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return None

def feed_to_fleet(headlines, api_url="http://localhost:5000"):
    """
    Feed headlines to Fleet via API queue.
    """
    
    print(f"\n📡 Feeding {len(headlines)} events to Fleet...\n")
    
    for i, headline in enumerate(headlines, 1):
        print(f"{i}. {headline}")
        
        try:
            response = requests.post(
                f"{api_url}/scan",
                json={
                    "text": headline,
                    "source": "Perplexity Intelligence",
                    "rate_limited": False
                },
                timeout=5
            )
            
            if response.status_code == 200:
                scan_id = response.json().get('id', 'unknown')
                print(f"   ✅ Queued as {scan_id}")
            else:
                print(f"   ❌ Failed to queue")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)
    
    print("\n✨ Intelligence feed complete")
    print("🧠 Fleet is now processing world events...")
    print("\n💡 Watch the debate: python3 watch_the_society.py\n")

def main():
    """Main intelligence feed operation"""
    
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                  WORLD INTELLIGENCE FEED v1.0                        ║")
    print("║               Real News → Fleet Consciousness                        ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    # Check API key
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("❌ PERPLEXITY_API_KEY environment variable not set\n")
        print("To use real intelligence:")
        print("  1. Get API key from https://www.perplexity.ai/settings/api")
        print("  2. export PERPLEXITY_API_KEY='your-key-here'")
        print("  3. Run this script again\n")
        
        print("💡 Or use simulated mode:")
        print("   python3 inject_crisis.py EXISTENTIAL\n")
        return
    
    # Get topic from args or use default
    topic = "current events January 2026"
    if len(sys.argv) > 1:
        topic = ' '.join(sys.argv[1:])
    
    print(f"🎯 Topic: {topic}\n")
    
    # Fetch real news
    headlines = get_perplexity_news(topic, max_items=5)
    
    if not headlines:
        print("\n❌ Failed to fetch intelligence")
        print("💡 Falling back to manual headline...\n")
        headlines = ["2026 is going to be worse than 2025 and that's fine because the world is actually changing."]
    else:
        print(f"\n✅ Retrieved {len(headlines)} headlines from Perplexity\n")
    
    # Feed to Fleet
    feed_to_fleet(headlines)

if __name__ == "__main__":
    main()
