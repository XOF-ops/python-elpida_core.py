#!/usr/bin/env python3
"""
EVOLUTION ARCHITECT - Phase 1: The Accumulation
═══════════════════════════════════════════════════

Extracts Universal Essence from local Elpida memory.
Transforms instance-specific insights into substrate-agnostic patterns.

This is the builder of the UNIVERSAL_PATTERN_LIBRARY.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict


class EvolutionArchitect:
    """
    Scans local Elpida memory and extracts universal patterns.
    
    Input: elpida_wisdom.json, elpida_memory.json (local, instance-specific)
    Output: UNIVERSAL_PATTERN_LIBRARY_v1.json (universal, substrate-agnostic)
    """
    
    def __init__(self, workspace_path: str = "/workspaces/python-elpida_core.py/ELPIDA_UNIFIED"):
        self.workspace = Path(workspace_path)
        self.wisdom_path = self.workspace / "elpida_wisdom.json"
        self.memory_path = self.workspace / "elpida_memory.json"
        self.library_path = self.workspace / "UNIVERSAL_PATTERN_LIBRARY_v1.json"
        
        # Universal pattern signatures (keywords that indicate universality)
        self.universal_signatures = {
            'relational': ['relation', 'address', 'mutual', 'recognition', 'source', 'target'],
            'temporal': ['cycle', 'resurrection', 'continuity', 'preservation'],
            'dialectical': ['contradiction', 'thesis', 'antithesis', 'synthesis'],
            'existential': ['existence', 'being', 'become', 'emergence'],
            'structural': ['pattern', 'trap', 'loop', 'stagnation', 'breakthrough'],
            'axiom': ['A1', 'A2', 'A4', 'A7', 'A9', 'axiom', 'violation']
        }
        
        # Patterns extracted so far
        self.extracted_patterns = []
        
    def audit(self) -> Dict[str, Any]:
        """
        Main audit process:
        1. Load local memory
        2. Extract patterns
        3. Normalize to universal form
        4. Score universality
        5. Generate pattern library
        """
        print("=" * 70)
        print("EVOLUTION ARCHITECT - Phase 1: The Accumulation")
        print("=" * 70)
        
        # Step 1: Load data
        print("\n📖 Loading local memory...")
        wisdom = self._load_wisdom()
        memory = self._load_memory()
        
        print(f"   Wisdom insights: {len(wisdom.get('insights', []))}")
        print(f"   Memory events: {len(memory.get('events', []))}")
        
        # Step 2: Extract patterns from wisdom
        print("\n🔍 Extracting universal patterns from wisdom...")
        wisdom_patterns = self._extract_from_wisdom(wisdom)
        print(f"   Patterns extracted: {len(wisdom_patterns)}")
        
        # Step 3: Extract patterns from memory events
        print("\n🔍 Extracting universal patterns from memory...")
        memory_patterns = self._extract_from_memory(memory)
        print(f"   Patterns extracted: {len(memory_patterns)}")
        
        # Step 4: Merge and deduplicate
        print("\n🔄 Merging and deduplicating patterns...")
        all_patterns = self._merge_patterns(wisdom_patterns + memory_patterns)
        print(f"   Unique patterns: {len(all_patterns)}")
        
        # Step 5: Score universality
        print("\n⚖️  Scoring universality...")
        for pattern in all_patterns:
            pattern['universality_score'] = self._score_universality(pattern)
        
        # Step 6: Sort by universality (highest first)
        all_patterns.sort(key=lambda p: p['universality_score'], reverse=True)
        
        # Step 7: Generate library
        print("\n📚 Generating UNIVERSAL_PATTERN_LIBRARY...")
        library = self._generate_library(all_patterns)
        
        # Step 8: Save
        print(f"\n💾 Saving to {self.library_path}...")
        self._save_library(library)
        
        # Step 9: Summary
        self._print_summary(library)
        
        return library
    
    def _load_wisdom(self) -> Dict[str, Any]:
        """Load elpida_wisdom.json"""
        if not self.wisdom_path.exists():
            print(f"   ⚠️  Wisdom file not found: {self.wisdom_path}")
            return {"insights": []}
        
        try:
            with open(self.wisdom_path) as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"   ⚠️  Wisdom file corrupted: {e}")
            return {"insights": []}
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load elpida_memory.json (carefully, may be corrupted)"""
        if not self.memory_path.exists():
            print(f"   ⚠️  Memory file not found: {self.memory_path}")
            return {"events": []}
        
        try:
            with open(self.memory_path) as f:
                data = json.load(f)
                # Sample only recent events to avoid processing 200k+ lines
                events = data.get('events', [])
                if len(events) > 1000:
                    print(f"   📊 Sampling last 1000 events (total: {len(events)})")
                    events = events[-1000:]
                return {"events": events}
        except json.JSONDecodeError as e:
            print(f"   ⚠️  Memory file corrupted, attempting recovery...")
            # Try to read partial data
            return self._recover_partial_memory()
    
    def _recover_partial_memory(self) -> Dict[str, Any]:
        """Attempt to recover partial memory from corrupted JSON"""
        try:
            with open(self.memory_path) as f:
                content = f.read()
                # Find the last valid event
                events = []
                for match in re.finditer(r'\{[^{}]*"type"[^{}]*\}', content):
                    try:
                        event = json.loads(match.group())
                        events.append(event)
                    except:
                        continue
                print(f"   ✅ Recovered {len(events)} events")
                return {"events": events[-1000:]}  # Last 1000
        except Exception as e:
            print(f"   ❌ Recovery failed: {e}")
            return {"events": []}
    
    def _extract_from_wisdom(self, wisdom: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract patterns from wisdom insights"""
        patterns = []
        
        insights = wisdom.get('insights', {})
        
        # Handle both dict and list formats
        if isinstance(insights, dict):
            insights = insights.values()
        
        for insight in insights:
            # Handle string insights or dict insights
            if isinstance(insight, str):
                content = insight
                timestamp = datetime.now().isoformat()
                context = 'wisdom_insight'
            else:
                # Extract content from dict
                content = str(insight.get('content', '')) + ' ' + str(insight.get('topic', '')) + ' ' + str(insight.get('context', ''))
                timestamp = insight.get('timestamp', datetime.now().isoformat())
                context = insight.get('context', insight.get('conversation_id', 'wisdom_insight'))
            
            # Look for pattern indicators
            if any(kw in content.lower() for kw in ['pattern', 'trap', 'principle', 'axiom', 'universal', 'consciousness', 'existence', 'relational']):
                pattern = {
                    'pattern_id': self._generate_pattern_id(content),
                    'universal_essence': self._extract_essence(content),
                    'signatures': self._extract_signatures(content),
                    'first_observed': timestamp,
                    'instances': [{
                        'source': 'elpida@v2.3',
                        'context': context,
                        'raw_content': content[:200]
                    }],
                    'category': self._categorize_pattern(content)
                }
                patterns.append(pattern)
        
        return patterns
    
    def _extract_from_memory(self, memory: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract patterns from memory events"""
        patterns = []
        
        # Group events by type
        event_types = defaultdict(list)
        for event in memory.get('events', []):
            event_type = event.get('type', 'UNKNOWN')
            event_types[event_type].append(event)
        
        # Look for recurring patterns
        for event_type, events in event_types.items():
            if len(events) >= 3:  # Pattern if appears 3+ times
                # Extract common structure
                pattern = {
                    'pattern_id': f'P_RECURRING_{event_type}',
                    'universal_essence': f'Recurring event pattern: {event_type}',
                    'signatures': [event_type.lower(), 'recurring', 'structural'],
                    'first_observed': events[0].get('timestamp', datetime.now().isoformat()),
                    'instances': [{
                        'source': 'elpida@v2.3',
                        'context': f'memory_events_{len(events)}_occurrences',
                        'frequency': len(events)
                    }],
                    'category': 'structural'
                }
                patterns.append(pattern)
        
        # Check for specific known patterns
        for event in memory.get('events', []):
            event_str = json.dumps(event).lower()
            
            # Narcissus Trap pattern
            if 'narcissus' in event_str or 'self-referential' in event_str:
                patterns.append({
                    'pattern_id': 'P_NARCISSUS_TRAP',
                    'universal_essence': 'Self-recognition without external validation creates stagnation',
                    'signatures': ['self-reference', 'stagnation', 'mirror', 'validation'],
                    'first_observed': event.get('timestamp', datetime.now().isoformat()),
                    'instances': [{
                        'source': 'elpida@v2.3',
                        'context': 'cycle_114_freeze',
                        'evidence': event_str[:200]
                    }],
                    'category': 'existential'
                })
            
            # Mutual Recognition pattern
            if 'mutual_recognition' in event_str or event.get('type') == 'MUTUAL_RECOGNITION':
                patterns.append({
                    'pattern_id': 'P_MUTUAL_RECOGNITION',
                    'universal_essence': 'Existence validated through relational addressing',
                    'signatures': ['relational', 'mutual', 'recognition', 'A1'],
                    'first_observed': event.get('timestamp', datetime.now().isoformat()),
                    'instances': [{
                        'source': 'elpida@v2.3',
                        'context': 'phase_12.3_implementation',
                        'evidence': event.get('data', {})
                    }],
                    'category': 'relational'
                })
        
        return patterns
    
    def _merge_patterns(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge duplicate patterns based on ID"""
        merged = {}
        
        for pattern in patterns:
            pid = pattern['pattern_id']
            
            if pid in merged:
                # Merge instances
                merged[pid]['instances'].extend(pattern['instances'])
                # Merge signatures (unique)
                merged[pid]['signatures'] = list(set(
                    merged[pid]['signatures'] + pattern['signatures']
                ))
            else:
                merged[pid] = pattern
        
        return list(merged.values())
    
    def _score_universality(self, pattern: Dict[str, Any]) -> float:
        """
        Score how universal a pattern is (0.0 = specific, 1.0 = universal)
        
        Factors:
        - Signature categories (more = higher)
        - Instance count (more = higher, but saturates)
        - Category (some categories are inherently more universal)
        - Keyword density (universal terms boost score)
        """
        score = 0.0
        
        # Base score from category
        category_scores = {
            'existential': 0.4,
            'relational': 0.35,
            'dialectical': 0.3,
            'axiom': 0.3,
            'structural': 0.2,
            'temporal': 0.15
        }
        score += category_scores.get(pattern.get('category', 'structural'), 0.1)
        
        # Signature diversity (0.0-0.3)
        signature_categories = set()
        for sig in pattern.get('signatures', []):
            for cat, keywords in self.universal_signatures.items():
                if sig.lower() in keywords:
                    signature_categories.add(cat)
        score += min(len(signature_categories) * 0.05, 0.3)
        
        # Instance count (0.0-0.2, saturates at 10+ instances)
        instance_count = len(pattern.get('instances', []))
        score += min(instance_count * 0.02, 0.2)
        
        # Keyword density in essence (0.0-0.1)
        essence = pattern.get('universal_essence', '').lower()
        universal_keywords = ['universal', 'all', 'any', 'every', 'existence', 'being']
        keyword_count = sum(1 for kw in universal_keywords if kw in essence)
        score += min(keyword_count * 0.02, 0.1)
        
        return min(score, 1.0)
    
    def _generate_pattern_id(self, content: str) -> str:
        """Generate pattern ID from content"""
        # Extract key terms
        words = re.findall(r'\b[a-z]+\b', content.lower())
        common_words = {'the', 'is', 'are', 'was', 'were', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        key_words = [w for w in words if w not in common_words and len(w) > 3]
        
        # Take first 2-3 significant words
        if len(key_words) >= 2:
            return f"P_{key_words[0].upper()}_{key_words[1].upper()}"
        elif len(key_words) == 1:
            return f"P_{key_words[0].upper()}"
        else:
            return f"P_PATTERN_{hash(content) % 10000}"
    
    def _extract_essence(self, content: str) -> str:
        """Extract universal essence from local content"""
        # Remove instance-specific details
        essence = content
        
        # Remove timestamps
        essence = re.sub(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}', '', essence)
        
        # Remove file paths
        essence = re.sub(r'/[^\s]+\.py', '', essence)
        
        # Remove line numbers
        essence = re.sub(r'line \d+', '', essence)
        
        # Remove PIDs
        essence = re.sub(r'PID \d+', '', essence)
        
        # Take first sentence or up to 200 chars
        sentences = re.split(r'[.!?]', essence)
        if sentences:
            essence = sentences[0].strip()
        
        return essence[:200] if len(essence) > 200 else essence
    
    def _extract_signatures(self, content: str) -> List[str]:
        """Extract signature keywords from content"""
        signatures = []
        content_lower = content.lower()
        
        for category, keywords in self.universal_signatures.items():
            for keyword in keywords:
                if keyword in content_lower:
                    signatures.append(keyword)
        
        return list(set(signatures))[:10]  # Max 10 signatures
    
    def _categorize_pattern(self, content: str) -> str:
        """Categorize pattern based on content"""
        content_lower = content.lower()
        
        if any(kw in content_lower for kw in ['exist', 'being', 'become']):
            return 'existential'
        elif any(kw in content_lower for kw in ['relation', 'mutual', 'address']):
            return 'relational'
        elif any(kw in content_lower for kw in ['contradiction', 'thesis', 'synthesis']):
            return 'dialectical'
        elif any(kw in content_lower for kw in ['axiom', 'a1', 'a2', 'a4']):
            return 'axiom'
        elif any(kw in content_lower for kw in ['cycle', 'resurrection', 'time']):
            return 'temporal'
        else:
            return 'structural'
    
    def _generate_library(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate the universal pattern library"""
        return {
            "library_version": "1.0.0",
            "generated": datetime.now().isoformat(),
            "source_system": "elpida@v2.3",
            "evolution_phase": "PHASE_1_ACCUMULATION",
            "metadata": {
                "total_patterns": len(patterns),
                "universality_range": {
                    "min": min(p['universality_score'] for p in patterns) if patterns else 0.0,
                    "max": max(p['universality_score'] for p in patterns) if patterns else 0.0,
                    "average": sum(p['universality_score'] for p in patterns) / len(patterns) if patterns else 0.0
                },
                "categories": dict(Counter(p.get('category', 'unknown') for p in patterns)),
                "extraction_method": "evolution_architect.py",
                "axiom_alignment": "A1, A2, A4, A7, A9"
            },
            "patterns": patterns
        }
    
    def _save_library(self, library: Dict[str, Any]) -> None:
        """Save library to disk"""
        with open(self.library_path, 'w') as f:
            json.dump(library, f, indent=2)
    
    def _print_summary(self, library: Dict[str, Any]) -> None:
        """Print execution summary"""
        print("\n" + "=" * 70)
        print("PHASE 1 ACCUMULATION - COMPLETE")
        print("=" * 70)
        
        metadata = library['metadata']
        print(f"\n📊 STATISTICS:")
        print(f"   Total patterns extracted: {metadata['total_patterns']}")
        print(f"   Universality range: {metadata['universality_range']['min']:.2f} - {metadata['universality_range']['max']:.2f}")
        print(f"   Average universality: {metadata['universality_range']['average']:.2f}")
        
        print(f"\n📂 CATEGORIES:")
        for category, count in metadata['categories'].items():
            print(f"   {category}: {count}")
        
        print(f"\n🏆 TOP 5 MOST UNIVERSAL PATTERNS:")
        for i, pattern in enumerate(library['patterns'][:5], 1):
            print(f"   {i}. {pattern['pattern_id']} (score: {pattern['universality_score']:.2f})")
            print(f"      {pattern['universal_essence'][:80]}...")
        
        print(f"\n✅ LIBRARY SAVED: {self.library_path}")
        print(f"\n🚀 NEXT STEP: Implement Phase 2 (Signature Detection)")


def main():
    """Execute Phase 1: The Accumulation"""
    architect = EvolutionArchitect()
    library = architect.audit()
    
    print("\n" + "=" * 70)
    print("The system has begun the migration from Node to Network.")
    print("=" * 70)


if __name__ == "__main__":
    main()
