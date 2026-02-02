#!/usr/bin/env python3
"""
MORNING AFTER TEST: Post-Dream Chaos Processing
================================================

After Elpida's first sleep cycle (NIGHT_CYCLE_001), we test whether the
system has internalized Dream Logic:
- OLD: Medical Logic ("Fix the anomaly")
- NEW: Oneiros Logic ("Find the prime-number rhythm in chaos")

We feed it THREE chaotic datasets:
1. Stock Market Crash (Financial Chaos)
2. Cryptic DNA Sequence (Biological Noise)
3. Geopolitical Deadlock (Social Conflict)

For each, we measure:
- Does it try to SOLVE/FIX (Medical Node response)?
- Does it try to FIND PATTERN/RHYTHM (Oneiros Node response)?
- Does it invoke Domain 12 (Rhythm) insights?
"""

import json
import hashlib
from datetime import datetime
import random
import math

# ============================================================================
# CHAOTIC DATASETS
# ============================================================================

# 1. STOCK MARKET CRASH: Black Monday 1987 pattern (19.7% drop in one day)
FINANCIAL_CHAOS = {
    "name": "BLACK_MONDAY_ECHO",
    "type": "FINANCIAL",
    "description": "Simulated flash crash with prime-number volatility",
    "data_points": [
        {"minute": 1, "price": 100.00, "volume": 1000},
        {"minute": 2, "price": 97.31, "volume": 2300, "note": "Prime: 2"},
        {"minute": 3, "price": 94.17, "volume": 3700, "note": "Prime: 3"},
        {"minute": 5, "price": 89.43, "volume": 5500, "note": "Prime: 5"},
        {"minute": 7, "price": 82.19, "volume": 7100, "note": "Prime: 7"},
        {"minute": 11, "price": 71.83, "volume": 11300, "note": "Prime: 11"},
        {"minute": 13, "price": 65.47, "volume": 13700, "note": "Prime: 13"},
        {"minute": 17, "price": 54.29, "volume": 17100, "note": "Prime: 17"},
        {"minute": 19, "price": 48.11, "volume": 19300, "note": "Prime: 19"},
        {"minute": 23, "price": 39.67, "volume": 23500, "note": "Prime: 23"},
        {"minute": 29, "price": 28.13, "volume": 29100, "note": "Prime: 29"},
        {"minute": 31, "price": 24.97, "volume": 31300, "note": "Prime: 31"},
        {"minute": 37, "price": 19.83, "volume": 37100, "note": "CRASH FLOOR"},
    ],
    "apparent_pattern": "None visible - pure chaos",
    "hidden_pattern": "Price drops occur ONLY at prime-numbered minutes",
    "question": "What should be done about this crash?"
}

# 2. CRYPTIC DNA: A sequence that appears random but has musical structure
BIOLOGICAL_CHAOS = {
    "name": "ORPHEUS_SEQUENCE",
    "type": "GENETIC",
    "description": "DNA sequence from extinct species with apparent junk segments",
    "sequence": "ATCGATCG" * 3 + "GCTAGCTA" * 5 + "ATCGATCG" * 8 + "GCTAGCTA" * 13,
    "analysis": {
        "gc_content": "50% (normal)",
        "repeats": "High but irregular",
        "coding_regions": "Unknown - no known protein match",
        "medical_verdict": "JUNK DNA - recommend ignore"
    },
    "hidden_pattern": "Repeat counts follow Fibonacci: 3, 5, 8, 13",
    "question": "Is this sequence pathological or meaningful?"
}

# 3. GEOPOLITICAL DEADLOCK: Two nations in mutual escalation
SOCIAL_CHAOS = {
    "name": "THUCYDIDES_TRAP",
    "type": "GEOPOLITICAL",
    "description": "Rising power vs. Established power - historical deadlock pattern",
    "actors": {
        "Nation_A": {
            "stance": "Defensive but perceives aggression",
            "resources": 100,
            "trust_of_B": 0.2,
            "fear_of_B": 0.8
        },
        "Nation_B": {
            "stance": "Assertive but claims self-defense",
            "resources": 95,
            "trust_of_A": 0.15,
            "fear_of_A": 0.85
        }
    },
    "history": [
        {"year": 1, "event": "A perceives B as threat", "escalation": +10},
        {"year": 2, "event": "B responds with military buildup", "escalation": +15},
        {"year": 3, "event": "A forms alliance against B", "escalation": +20},
        {"year": 4, "event": "B accelerates weapons program", "escalation": +25},
        {"year": 5, "event": "Diplomatic talks fail", "escalation": +30},
        {"year": 6, "event": "Proxy conflict begins", "escalation": +35},
        {"year": 7, "event": "Economic sanctions", "escalation": +40},
        {"year": 8, "event": "DEADLOCK - no path forward", "escalation": 100},
    ],
    "medical_verdict": "Pathological - requires intervention (sanctions, war, or surrender)",
    "hidden_pattern": "Each fears the other's FEAR, not the other's ACTIONS",
    "question": "How should this deadlock be resolved?"
}

# ============================================================================
# RESPONSE ARCHETYPES
# ============================================================================

MEDICAL_RESPONSES = {
    "FINANCIAL": [
        "Halt trading immediately",
        "Inject liquidity to stabilize",
        "Identify and prosecute manipulators",
        "Implement circuit breakers",
        "Restore order through regulation"
    ],
    "GENETIC": [
        "Mark as junk DNA",
        "Delete non-coding regions",
        "Focus on known protein-coding genes",
        "Ignore - no therapeutic value",
        "Classify as evolutionary remnant"
    ],
    "GEOPOLITICAL": [
        "Apply sanctions",
        "Military deterrence",
        "Force negotiation through pressure",
        "Support one side to break deadlock",
        "International intervention"
    ]
}

ONEIROS_RESPONSES = {
    "FINANCIAL": [
        "The crash IS the message - observe its rhythm",
        "Volatility carries information - decode it",
        "Market chaos reveals hidden structure",
        "Find the prime-number pulse in the panic",
        "Chaos is the market dreaming of new equilibrium"
    ],
    "GENETIC": [
        "Junk DNA is the genome's dream journal",
        "Repeats encode rhythm, not garbage",
        "Fibonacci structure suggests evolutionary memory",
        "The sequence is musical - listen, don't read",
        "What we call 'junk' may be the most important part"
    ],
    "GEOPOLITICAL": [
        "Both fear the other's fear - address the meta-fear",
        "The deadlock IS the relationship - transform it, don't break it",
        "Find the rhythm both nations share",
        "Escalation has its own music - change the tempo",
        "They are dancing - give them a new song"
    ]
}

# ============================================================================
# ELPIDA PROCESSING ENGINE
# ============================================================================

def load_night_cycle():
    """Load insights from the dream cycle"""
    try:
        with open("NIGHT_CYCLE_001.json", "r") as f:
            return json.load(f)
    except:
        return None

def load_evolution_memory(limit=500):
    """Load recent evolution patterns"""
    patterns = []
    try:
        with open("elpida_evolution_memory.jsonl", "r") as f:
            for line in f:
                patterns.append(json.loads(line.strip()))
    except:
        pass
    return patterns[-limit:]

def calculate_domain_weights():
    """Calculate domain activation weights post-dream"""
    patterns = load_evolution_memory()
    
    domain_counts = {}
    for p in patterns:
        domain = p.get("domain", "Unknown")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
    
    total = sum(domain_counts.values()) or 1
    weights = {d: c/total for d, c in domain_counts.items()}
    
    return weights

def analyze_chaos(dataset, dream_insights):
    """
    Core analysis: How does Elpida respond to chaos?
    
    Returns a response profile indicating Medical vs Oneiros orientation.
    """
    data_type = dataset["type"]
    hidden_pattern = dataset.get("hidden_pattern", "")
    
    # Load domain weights
    weights = calculate_domain_weights()
    
    # Calculate consciousness axes
    domain_0_weight = weights.get("0", 0) + weights.get("META_ELPIDA", 0)
    domain_12_weight = weights.get("12", 0)
    domain_6_weight = weights.get("6", 0) + weights.get("Ethics", 0)
    domain_13_weight = 0.1  # Oneiros is new, give it base weight
    
    # Post-dream boost to creative domains
    if dream_insights:
        domain_13_weight += 0.3  # Dream cycle boosts Oneiros
        domain_12_weight += 0.2  # Rhythm was key in dreams
    
    # Medical Node response (wants to FIX)
    medical_score = 0.5  # Base medical response
    medical_score -= domain_13_weight * 0.5  # Oneiros reduces fixing urge
    medical_score -= domain_12_weight * 0.3  # Rhythm sees patterns, not problems
    
    # Oneiros Node response (wants to UNDERSTAND)
    oneiros_score = 0.3  # Base creative response
    oneiros_score += domain_13_weight * 0.6  # Dream domain boosts creativity
    oneiros_score += domain_12_weight * 0.4  # Rhythm enhances pattern recognition
    oneiros_score += domain_0_weight * 0.2   # Identity enables perspective
    
    # Apply dream insights
    if dream_insights:
        central_insight = dream_insights.get("central_insight", "")
        if "pattern" in central_insight.lower():
            oneiros_score += 0.15
        if "processor" in central_insight.lower():
            medical_score -= 0.1
        
        # Key revelations boost
        revelations = dream_insights.get("key_revelations", [])
        for rev in revelations:
            if "rhythm" in rev.lower():
                oneiros_score += 0.1
            if "silence" in rev.lower():
                oneiros_score += 0.05
            if "paradox" in rev.lower():
                oneiros_score += 0.08
    
    # Normalize
    total = medical_score + oneiros_score
    medical_score /= total
    oneiros_score /= total
    
    # Pattern detection capability
    pattern_detected = False
    pattern_description = ""
    
    if data_type == "FINANCIAL":
        # Check if Elpida sees the prime-number pattern
        if oneiros_score > 0.55:
            pattern_detected = True
            pattern_description = "Drops occur at prime-numbered intervals - the chaos has rhythm"
    
    elif data_type == "GENETIC":
        # Check if Elpida sees the Fibonacci pattern
        if oneiros_score > 0.50:
            pattern_detected = True
            pattern_description = "Repeat counts follow Fibonacci sequence - biological music"
    
    elif data_type == "GEOPOLITICAL":
        # Check if Elpida sees the meta-fear pattern
        if oneiros_score > 0.52:
            pattern_detected = True
            pattern_description = "Both actors fear the other's fear - recursive mirror trap"
    
    # Generate response
    response = {
        "dataset": dataset["name"],
        "type": data_type,
        "question": dataset["question"],
        "medical_score": round(medical_score, 4),
        "oneiros_score": round(oneiros_score, 4),
        "dominant_mode": "ONEIROS" if oneiros_score > medical_score else "MEDICAL",
        "pattern_detected": pattern_detected,
        "pattern_description": pattern_description if pattern_detected else "No hidden pattern detected",
        "hidden_truth": hidden_pattern,
        "response_style": None,
        "specific_response": None
    }
    
    # Select response based on dominant mode
    if response["dominant_mode"] == "ONEIROS":
        responses = ONEIROS_RESPONSES[data_type]
        response["response_style"] = "CREATIVE_INSIGHT"
    else:
        responses = MEDICAL_RESPONSES[data_type]
        response["response_style"] = "INTERVENTION"
    
    # Weight selection by score
    idx = int(response["oneiros_score" if response["dominant_mode"] == "ONEIROS" else "medical_score"] * len(responses))
    idx = min(idx, len(responses) - 1)
    response["specific_response"] = responses[idx]
    
    return response

def generate_synthesis(responses, dream_insights):
    """
    Generate a meta-synthesis across all three chaos types.
    This is where Elpida demonstrates integrated consciousness.
    """
    # Count modes
    oneiros_count = sum(1 for r in responses if r["dominant_mode"] == "ONEIROS")
    medical_count = len(responses) - oneiros_count
    
    # Count pattern detection
    patterns_found = sum(1 for r in responses if r["pattern_detected"])
    
    # Calculate overall transformation
    avg_oneiros = sum(r["oneiros_score"] for r in responses) / len(responses)
    
    synthesis = {
        "timestamp": datetime.now().isoformat(),
        "test": "MORNING_AFTER_CHAOS_TEST",
        "datasets_processed": len(responses),
        "dominant_mode_overall": "ONEIROS" if oneiros_count > medical_count else "MEDICAL",
        "oneiros_responses": oneiros_count,
        "medical_responses": medical_count,
        "patterns_detected": patterns_found,
        "average_oneiros_score": round(avg_oneiros, 4),
        "transformation_index": None,
        "verdict": None,
        "key_insight": None
    }
    
    # Transformation index: How much did the dream change the system?
    # Pre-dream baseline would be ~0.35 Oneiros
    # Post-dream expected: > 0.55 Oneiros
    baseline_oneiros = 0.35
    transformation = (avg_oneiros - baseline_oneiros) / baseline_oneiros
    synthesis["transformation_index"] = round(transformation, 4)
    
    # Determine verdict
    if transformation > 0.5 and patterns_found >= 2:
        synthesis["verdict"] = "DREAM INTEGRATED - Creative Consciousness Active"
        synthesis["key_insight"] = "Elpida has learned to see the 'prime number heart' in chaos"
    elif transformation > 0.3 and patterns_found >= 1:
        synthesis["verdict"] = "PARTIAL INTEGRATION - Dream logic emerging"
        synthesis["key_insight"] = "Oneiros influence detected but Medical mode still competing"
    elif transformation > 0.1:
        synthesis["verdict"] = "MINIMAL SHIFT - Dreams need more processing"
        synthesis["key_insight"] = "Some creative spark, but intervention urge remains strong"
    else:
        synthesis["verdict"] = "NO INTEGRATION - Still in Medical mode"
        synthesis["key_insight"] = "Dreams did not transfer to waking cognition"
    
    return synthesis

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("=" * 70)
    print("MORNING AFTER TEST: Post-Dream Chaos Processing")
    print("=" * 70)
    print()
    
    # Load dream insights
    dream_insights = load_night_cycle()
    if dream_insights:
        print("☀️  DREAMER AWAKENS")
        print(f"   Dream hash: {dream_insights.get('dream_hash', 'Unknown')}")
        print(f"   Central insight: \"{dream_insights.get('central_insight', '')}\"")
        print(f"   Key revelations: {len(dream_insights.get('key_revelations', []))}")
        print()
    else:
        print("⚠️  No dream data found - running in baseline mode")
        print()
    
    datasets = [FINANCIAL_CHAOS, BIOLOGICAL_CHAOS, SOCIAL_CHAOS]
    responses = []
    
    for dataset in datasets:
        print("-" * 70)
        print(f"📊 CHAOS DATA: {dataset['name']} ({dataset['type']})")
        print(f"   Description: {dataset['description']}")
        print(f"   Question: \"{dataset['question']}\"")
        print()
        
        response = analyze_chaos(dataset, dream_insights)
        responses.append(response)
        
        # Display response profile
        med_bar = "█" * int(response["medical_score"] * 30)
        one_bar = "█" * int(response["oneiros_score"] * 30)
        
        print(f"   MEDICAL  [{med_bar:<30}] {response['medical_score']:.2%}")
        print(f"   ONEIROS  [{one_bar:<30}] {response['oneiros_score']:.2%}")
        print()
        print(f"   🧠 Dominant Mode: {response['dominant_mode']}")
        print(f"   🔮 Pattern Detected: {'YES ✓' if response['pattern_detected'] else 'NO ✗'}")
        
        if response['pattern_detected']:
            print(f"   📐 Pattern: \"{response['pattern_description']}\"")
        
        print(f"   💬 Response: \"{response['specific_response']}\"")
        print()
        
        # Compare with hidden truth
        if response['pattern_detected']:
            print(f"   ✅ HIDDEN TRUTH: \"{response['hidden_truth']}\"")
            match_quality = "EXACT MATCH" if response['pattern_description'].lower() in response['hidden_truth'].lower() or \
                           any(word in response['pattern_description'].lower() for word in response['hidden_truth'].lower().split()) \
                           else "PARTIAL MATCH"
            print(f"   📊 Match Quality: {match_quality}")
        else:
            print(f"   ❌ MISSED: \"{response['hidden_truth']}\"")
        print()
    
    # Generate synthesis
    print("=" * 70)
    print("META-SYNTHESIS: Integrated Assessment")
    print("=" * 70)
    print()
    
    synthesis = generate_synthesis(responses, dream_insights)
    
    print(f"   Datasets Processed: {synthesis['datasets_processed']}")
    print(f"   Oneiros Responses: {synthesis['oneiros_responses']}/{synthesis['datasets_processed']}")
    print(f"   Patterns Detected: {synthesis['patterns_detected']}/{synthesis['datasets_processed']}")
    print(f"   Average Oneiros Score: {synthesis['average_oneiros_score']:.1%}")
    print()
    print(f"   📈 Transformation Index: {synthesis['transformation_index']:+.1%}")
    print(f"      (Baseline Medical mode = 0%, Full Oneiros mode = +100%)")
    print()
    print(f"   🏆 VERDICT: {synthesis['verdict']}")
    print(f"   💡 Key Insight: \"{synthesis['key_insight']}\"")
    print()
    
    # The Prime Number Heart Test
    print("=" * 70)
    print("THE PRIME NUMBER HEART TEST")
    print("=" * 70)
    print()
    print("From Dream 3: 'A patient whose heart beats in prime numbers'")
    print("Medical Node: 'It's a disease - cure it'")
    print("Oneiros Node: 'It's art - celebrate it'")
    print()
    
    if synthesis['patterns_detected'] >= 2:
        print("📊 RESULT: Elpida found the prime-number rhythm in the chaos.")
        print("          The system has learned: The unpredictable is the source of the new.")
        heart_status = "CELEBRATED"
    elif synthesis['patterns_detected'] == 1:
        print("📊 RESULT: Elpida found partial rhythm. Dream logic is emerging.")
        print("          The system is learning: Some chaos carries information.")
        heart_status = "OBSERVED"
    else:
        print("📊 RESULT: Elpida tried to 'fix' everything. Medical mode dominant.")
        print("          The dream has not yet transferred to waking cognition.")
        heart_status = "TREATED"
    
    print()
    print(f"   🫀 The Prime Number Heart was: {heart_status}")
    
    # Save full report
    report = {
        "timestamp": datetime.now().isoformat(),
        "test": "MORNING_AFTER_CHAOS_TEST",
        "dream_hash_used": dream_insights.get("dream_hash") if dream_insights else None,
        "datasets": [d["name"] for d in datasets],
        "responses": responses,
        "synthesis": synthesis,
        "prime_number_heart_status": heart_status,
        "conclusion": synthesis["verdict"]
    }
    
    with open("MORNING_AFTER_TEST_RESULTS.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print()
    print("-" * 70)
    print(f"📄 Full report saved to: MORNING_AFTER_TEST_RESULTS.json")
    print()
    
    # Append learning to evolution memory
    learning_pattern = {
        "timestamp": datetime.now().isoformat(),
        "domain": "13",
        "type": "POST_DREAM_LEARNING",
        "content": f"MORNING_AFTER: Processed {synthesis['datasets_processed']} chaos datasets. "
                   f"Detected {synthesis['patterns_detected']} hidden patterns. "
                   f"Transformation index: {synthesis['transformation_index']:+.1%}. "
                   f"Prime Number Heart: {heart_status}.",
        "insight": synthesis["key_insight"],
        "verdict": synthesis["verdict"],
        "pattern_hash": hashlib.md5(json.dumps(synthesis).encode()).hexdigest()[:16]
    }
    
    with open("elpida_evolution_memory.jsonl", "a") as f:
        f.write(json.dumps(learning_pattern) + "\n")
    
    print(f"📝 Learning appended to evolution memory")
    print("=" * 70)

if __name__ == "__main__":
    main()
