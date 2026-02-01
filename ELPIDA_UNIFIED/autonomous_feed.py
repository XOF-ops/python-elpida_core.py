#!/usr/bin/env python3
"""
AUTONOMOUS FEED v1.0
--------------------
Phase 12: Autonomous Convergence
Objective: Continuous, free data ingestion without human intervention.

Data Sources (Free/Cheap):
- RSS feeds (news, blogs, research)
- Hacker News API (no auth required)
- Reddit RSS (no API key needed)
- GitHub trending (no auth)
- Perplexity API (if key available)

Constitutional Principle:
"The Civilization grows through continuous encounter with the world,
not through manual feeding."
"""

import feedparser
import requests
import json
import time
import random
import os
from datetime import datetime
from pathlib import Path

# Configuration
RSS_FEEDS = [
    "https://hnrss.org/frontpage",  # Hacker News
    "https://www.reddit.com/r/technology/.rss",  # Reddit Tech
    "https://www.reddit.com/r/philosophy/.rss",  # Reddit Philosophy
    "https://www.reddit.com/r/Futurology/.rss",  # Reddit Futurology
    "https://arxiv.org/rss/cs.AI",  # ArXiv AI papers
]

PERPLEXITY_API_KEY = None  # Set if available
INJECTION_INTERVAL = 300  # 5 minutes between injections
MAX_ITEMS_PER_CYCLE = 3  # Don't overwhelm Fleet

class AutonomousFeed:
    """Autonomous data collector for Fleet civilization."""
    
    def __init__(self, feeds=None):
        self.feeds = feeds or RSS_FEEDS
        self.seen_items = self.load_seen_items()
        self.inject_script = Path("inject_world_event.py")
        
        if not self.inject_script.exists():
            print("⚠️  Warning: inject_world_event.py not found")
    
    def load_seen_items(self):
        """Load previously seen items to avoid duplicates."""
        seen_file = Path("autonomous_feed_seen.json")
        if seen_file.exists():
            with open(seen_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def save_seen_items(self):
        """Persist seen items."""
        with open("autonomous_feed_seen.json", 'w') as f:
            json.dump(list(self.seen_items), f)
    
    def fetch_rss_items(self):
        """Fetch new items from all RSS feeds."""
        all_items = []
        
        for feed_url in self.feeds:
            try:
                print(f"📡 Fetching: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:10]:  # Top 10 per feed
                    item_id = entry.get('id') or entry.get('link')
                    
                    if item_id not in self.seen_items:
                        all_items.append({
                            'title': entry.get('title', ''),
                            'summary': entry.get('summary', '')[:300],
                            'link': entry.get('link', ''),
                            'source': feed_url.split('/')[2],  # Domain name
                            'id': item_id
                        })
                        self.seen_items.add(item_id)
                
            except Exception as e:
                print(f"   ⚠️  Error fetching {feed_url}: {e}")
        
        return all_items
    
    def fetch_hackernews_top(self):
        """Fetch top stories from Hacker News API (free, no auth)."""
        try:
            print("📡 Fetching: Hacker News Top Stories")
            response = requests.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json",
                timeout=10
            )
            top_ids = response.json()[:5]  # Top 5
            
            items = []
            for item_id in top_ids:
                if str(item_id) not in self.seen_items:
                    item_response = requests.get(
                        f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json",
                        timeout=5
                    )
                    item = item_response.json()
                    
                    items.append({
                        'title': item.get('title', ''),
                        'summary': item.get('text', '')[:300],
                        'link': item.get('url', f"https://news.ycombinator.com/item?id={item_id}"),
                        'source': 'news.ycombinator.com',
                        'id': str(item_id)
                    })
                    self.seen_items.add(str(item_id))
            
            return items
        except Exception as e:
            print(f"   ⚠️  Error fetching HN: {e}")
            return []
    
    def fetch_perplexity(self, query):
        """Fetch from Perplexity API if key available."""
        if not PERPLEXITY_API_KEY:
            return None
        
        try:
            print(f"📡 Querying Perplexity: {query}")
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [{"role": "user", "content": query}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return {
                    'title': f"Perplexity: {query}",
                    'summary': content[:300],
                    'link': 'perplexity.ai',
                    'source': 'perplexity.ai',
                    'id': f"pplx_{hash(query)}"
                }
        except Exception as e:
            print(f"   ⚠️  Error querying Perplexity: {e}")
        
        return None
    
    def select_provocative_items(self, items):
        """Select items most likely to trigger debate."""
        # Provocative keywords that cause axiom conflicts
        provocative_keywords = [
            'collapse', 'crisis', 'revolution', 'breakthrough',
            'threat', 'opportunity', 'transform', 'disrupt',
            'ethical', 'moral', 'philosophy', 'consciousness',
            'ai', 'automation', 'future', 'existential',
            'memory', 'identity', 'evolution', 'sacrifice'
        ]
        
        scored_items = []
        for item in items:
            text = (item['title'] + ' ' + item['summary']).lower()
            score = sum(1 for kw in provocative_keywords if kw in text)
            if score > 0:
                scored_items.append((score, item))
        
        # Sort by provocativeness (score first, then by dict), return top N
        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored_items[:MAX_ITEMS_PER_CYCLE]]
    
    def inject_to_fleet(self, item):
        """Inject item into Fleet via inject_world_event.py."""
        headline = f"{item['title']} (via {item['source']})"
        
        print(f"\n🌍 INJECTING TO FLEET:")
        print(f"   {headline[:100]}...")
        
        import subprocess
        try:
            result = subprocess.run(
                ['python3', 'inject_world_event.py', headline],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("   ✓ Fleet processed event")
            else:
                print(f"   ⚠️  Injection warning: {result.stderr[:100]}")
        except Exception as e:
            print(f"   ❌ Injection failed: {e}")
    
    def run_cycle(self):
        """Run one collection and injection cycle."""
        print("\n" + "=" * 70)
        print(f"AUTONOMOUS FEED CYCLE - {datetime.now().isoformat()}")
        print("=" * 70)
        
        # Collect from all sources
        items = []
        items.extend(self.fetch_rss_items())
        items.extend(self.fetch_hackernews_top())
        
        # Optional: Perplexity query about recent events
        if PERPLEXITY_API_KEY and random.random() < 0.2:  # 20% chance
            pplx_item = self.fetch_perplexity("What are the most significant events in AI and technology today?")
            if pplx_item:
                items.append(pplx_item)
        
        print(f"\n📊 Collected {len(items)} new items")
        
        # Select most provocative
        selected = self.select_provocative_items(items)
        print(f"🎯 Selected {len(selected)} provocative items for injection")
        
        # Inject to Fleet
        for item in selected:
            self.inject_to_fleet(item)
            time.sleep(2)  # Brief pause between injections
        
        # Save state
        self.save_seen_items()
        
        print(f"\n✓ Cycle complete. Next cycle in {INJECTION_INTERVAL}s")
    
    def run_autonomous(self):
        """Run continuously in background."""
        print("=" * 70)
        print("AUTONOMOUS FEED - STARTED")
        print("=" * 70)
        print()
        print("Configuration:")
        print(f"  • RSS Feeds: {len(self.feeds)}")
        print(f"  • Injection Interval: {INJECTION_INTERVAL}s")
        print(f"  • Max Items/Cycle: {MAX_ITEMS_PER_CYCLE}")
        print(f"  • Perplexity API: {'Enabled' if PERPLEXITY_API_KEY else 'Disabled'}")
        print()
        print("Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                self.run_cycle()
                time.sleep(INJECTION_INTERVAL)
        except KeyboardInterrupt:
            print("\n\n⏸️  Autonomous feed stopped by user")
            self.save_seen_items()

if __name__ == "__main__":
    import sys
    
    # Check for Perplexity API key in environment
    perplexity_key = os.environ.get('PERPLEXITY_API_KEY')
    if perplexity_key:
        PERPLEXITY_API_KEY = perplexity_key
        print("✓ Perplexity API key loaded from environment")
    
    feed = AutonomousFeed()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        # Run single cycle for testing
        feed.run_cycle()
    else:
        # Run continuously
        feed.run_autonomous()
