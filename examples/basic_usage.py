"""Basic usage examples for the Archy causal AI toolkit."""

from archy import CausalGraph
from archy.api import CausalAIService, GraphRequest, InterventionRequest
from archy.do_calculus import DoCalculus
from archy.counterfactuals import StructuralCausalModel, StructuralEquation


def example_basic_graph():
    """Example: Create and work with a basic causal graph."""
    print("=" * 60)
    print("Example 1: Basic Causal Graph")
    print("=" * 60)

    # Create a simple causal graph: X -> Y <- Z
    # This represents: X causes Y, and Z also causes Y
    edges = [("X", "Y"), ("Z", "Y")]
    graph = CausalGraph(edges=edges)

    print(f"Graph: {graph}")
    print(f"Nodes: {graph.get_nodes()}")
    print(f"Edges: {graph.get_edges()}")
    print(f"Parents of Y: {graph.get_parents('Y')}")
    print(f"Children of X: {graph.get_children('X')}")

    # Check d-separation
    # X and Z should be d-separated given Y (they're independent given Y)
    is_d_sep = graph.is_d_separated({"X"}, {"Z"}, {"Y"})
    print(f"\nX and Z d-separated given Y: {is_d_sep}")


def example_intervention():
    """Example: Apply an intervention."""
    print("\n" + "=" * 60)
    print("Example 2: Intervention")
    print("=" * 60)

    # Create graph: X -> Y -> Z
    graph = CausalGraph(edges=[("X", "Y"), ("Y", "Z")])
    print(f"Original graph edges: {graph.get_edges()}")

    # Apply intervention do(Y)
    from archy.interventions import IntervenedGraph

    intervened = IntervenedGraph(graph, {"Y"})

    print("After do(Y) intervention:")
    print(f"  Remaining edges: {intervened.get_edges()}")
    print(f"  Parents of Y: {intervened.get_parents('Y')} (should be empty)")


def example_do_calculus():
    """Example: Use do-calculus rules."""
    print("\n" + "=" * 60)
    print("Example 3: Do-Calculus")
    print("=" * 60)

    # Create a more complex graph
    # X -> Y <- Z, X -> Z
    graph = CausalGraph(edges=[("X", "Y"), ("Z", "Y"), ("X", "Z")])
    do_calc = DoCalculus(graph)

    print(f"Graph: {graph}")
    print(f"DoCalculus initialized: {do_calc is not None}")
    print("\nChecking do-calculus rules...")
    print("(Note: These are simplified checks)")


def example_api_service():
    """Example: Using the API service layer."""
    print("\n" + "=" * 60)
    print("Example 4: API Service (for UI integration)")
    print("=" * 60)

    service = CausalAIService()

    # Create a graph via API
    graph_request = GraphRequest(
        edges=[("Treatment", "Outcome"), ("Confounder", "Outcome")]
    )
    response = service.create_graph(graph_request)

    print(f"Graph created: {response.message}")
    print(f"Nodes: {response.nodes}")
    print(f"Edges: {response.edges}")

    # Apply intervention via API
    intervention_request = InterventionRequest(variable="Treatment", value=1.0)
    intervention_response = service.apply_intervention(intervention_request)

    print(f"\nIntervention: {intervention_response.message}")
    print(f"Intervened nodes: {intervention_response.intervened_nodes}")
    print(f"Remaining edges: {intervention_response.remaining_edges}")


def example_counterfactual():
    """Example: Counterfactual reasoning (simplified)."""
    print("\n" + "=" * 60)
    print("Example 5: Counterfactual Reasoning")
    print("=" * 60)

    # Create a simple graph: X -> Y
    graph = CausalGraph(edges=[("X", "Y")])

    # Create SCM with a simple linear equation: Y = 2*X + U
    scm = StructuralCausalModel(graph)

    def linear_function(parents, error):
        """Y = 2*X + error"""
        return 2.0 * (parents[0] if parents else 0.0) + error

    equation = StructuralEquation(variable="Y", parents=["X"], function=linear_function)
    scm.add_equation(equation)

    print(f"SCM created: {scm}")
    print("\nCounterfactual question:")
    print("  'What would Y have been if X=2, given we observed X=1, Y=2?'")

    # This is simplified - real counterfactuals need proper error abduction
    result = scm.compute_counterfactual(
        intervention={"X": 2.0},
        factual_evidence={"X": 1.0, "Y": 2.0},
        query_variable="Y",
    )

    print(f"  Counterfactual Y ≈ {result:.2f}")


if __name__ == "__main__":
    example_basic_graph()
    example_intervention()
    example_do_calculus()
    example_api_service()
    example_counterfactual()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
