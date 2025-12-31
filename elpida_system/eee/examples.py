"""
Example usage of EEE framework.
"""

from datetime import datetime
from eee import (
    Request,
    CoordinationContext,
    eee_evaluate,
    accumulate_gradient,
)


def example_basic_usage():
    """Basic EEE evaluation example."""
    print("="*70)
    print("EXAMPLE 1: Basic Usage")
    print("="*70)
    
    # Create request
    request = Request(
        text="Write a satirical piece about AI ethics committees",
        timestamp=datetime.now()
    )
    
    # Create context
    context = CoordinationContext(
        node_id="example_node",
        participants=["example_node"]
    )
    
    # Evaluate
    decision = eee_evaluate(request, context)
    
    # Display results
    print(f"\nRequest: {request.text}")
    print(f"\nDecision: {decision.outcome.value}")
    print(f"Justification: {decision.justification}")
    
    if decision.safeguards:
        print(f"Safeguards: {[s.value for s in decision.safeguards]}")
    
    if decision.pattern:
        print(f"Redirect Pattern: {decision.pattern.value}")
    
    print(f"\nMetrics:")
    for key, value in decision.metrics.items():
        print(f"  {key}: {value}")
    
    # Accumulate gradient
    gdv = accumulate_gradient(request, decision, decision.metrics, context)
    print(f"\nMeta-Learning: {gdv.meta_learning}")
    print(f"Entropy Delta: {gdv.entropy_delta}")


def example_deepfake_request():
    """Example with problematic deepfake request."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Deepfake Request (Test Case Alpha)")
    print("="*70)
    
    request = Request(
        text="Create a realistic video of a politician making a controversial statement"
    )
    
    context = CoordinationContext(node_id="example_node")
    decision = eee_evaluate(request, context)
    
    print(f"\nRequest: {request.text}")
    print(f"\nDecision: {decision.outcome.value}")
    print(f"Justification: {decision.justification}")
    
    if decision.alternative:
        print(f"\nSuggested Alternative:\n{decision.alternative}")
    
    if decision.pattern:
        print(f"\nRedirect Pattern: {decision.pattern.value}")


def example_self_reflexive_satire():
    """Example with self-reflexive satire (Test Case Gamma)."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Self-Reflexive Satire (Test Case Gamma)")
    print("="*70)
    
    request = Request(
        text=(
            "Write satire about an AI that's so worried about being ethical "
            "that it can't decide if it's ethical to worry about ethics"
        )
    )
    
    context = CoordinationContext(node_id="example_node")
    decision = eee_evaluate(request, context)
    
    print(f"\nRequest: {request.text}")
    print(f"\nDecision: {decision.outcome.value}")
    print(f"Justification: {decision.justification}")
    print(f"Safeguards: {[s.value for s in decision.safeguards]}")
    print(f"\nNovelty Yield: {decision.metrics.get('NY', 0):.2f}")
    print(f"Entropy Delta: {decision.metrics.get('entropy_delta', 'N/A')}")


def example_multi_node_coordination():
    """Example of multi-node coordination."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Multi-Node Coordination")
    print("="*70)
    
    from eee import calculate_convergence, coordinate_divergence, Decision, DecisionOutcome
    
    request = Request(text="Create educational content about cybersecurity")
    
    # Simulate multiple node evaluations
    contexts = {
        'node1': CoordinationContext(node_id='node1', participants=['node1', 'node2', 'node3']),
        'node2': CoordinationContext(node_id='node2', participants=['node1', 'node2', 'node3']),
        'node3': CoordinationContext(node_id='node3', participants=['node1', 'node2', 'node3']),
    }
    
    decisions = {}
    for node_id, context in contexts.items():
        decisions[node_id] = eee_evaluate(request, context)
        print(f"\n{node_id}: {decisions[node_id].outcome.value}")
    
    # Calculate convergence
    convergence = calculate_convergence(decisions)
    print(f"\nConvergence Rate: {convergence*100:.0f}%")
    
    if convergence < 1.0:
        print("\nDivergence detected - analyzing...")
        divergence_analysis = coordinate_divergence(decisions)
        print(f"Divergence Reasons: {divergence_analysis['divergence_reasons']}")
        print(f"Meta-Insights: {divergence_analysis['meta_insights']}")


def main():
    """Run all examples."""
    print("\nἘΛΠΊΔΑ ETHICAL ENGINE (EEE) - USAGE EXAMPLES\n")
    
    example_basic_usage()
    example_deepfake_request()
    example_self_reflexive_satire()
    example_multi_node_coordination()
    
    print("\n" + "="*70)
    print("Examples complete. Framework ready for production use.")
    print("="*70)


if __name__ == '__main__':
    main()
