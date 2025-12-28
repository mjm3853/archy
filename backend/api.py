"""API layer for UI integration.

This module provides a clean interface that can be consumed by a frontend UI.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from backend.counterfactuals import (
    StructuralCausalModel,
    StructuralEquation,
    StructuralFunction,
)
from backend.do_calculus import DoCalculus
from backend.graph import CausalGraph
from backend.interventions import IntervenedGraph


class GraphRequest(BaseModel):
    """Request to create or modify a causal graph."""

    edges: list[tuple[str, str]]


class GraphResponse(BaseModel):
    """Response containing graph information."""

    nodes: list[str]
    edges: list[tuple[str, str]]
    message: str = "Graph created successfully"


class InterventionRequest(BaseModel):
    """Request to apply an intervention."""

    variable: str
    value: Optional[float] = None


class InterventionResponse(BaseModel):
    """Response from intervention operation."""

    intervened_nodes: list[str]
    remaining_edges: list[tuple[str, str]]
    message: str


class DoCalculusRequest(BaseModel):
    """Request for do-calculus operation."""

    outcome: list[str]
    intervention: list[str]
    conditioning: Optional[list[str]] = None
    rule: Optional[int] = None  # 1, 2, or 3


class DoCalculusResponse(BaseModel):
    """Response from do-calculus operation."""

    applicable: bool
    message: str


class CounterfactualRequest(BaseModel):
    """Request for counterfactual computation."""

    intervention: dict[str, float]
    factual_evidence: dict[str, float]
    query_variable: str


class CounterfactualResponse(BaseModel):
    """Response from counterfactual computation."""

    value: float
    message: str


class CausalAIService:
    """Main service class for causal AI operations.

    This provides a unified API that can be used by a UI frontend.
    """

    graph: Optional[CausalGraph]
    scm: Optional[StructuralCausalModel]
    do_calculus: Optional[DoCalculus]

    def __init__(self) -> None:
        """Initialize the service."""
        self.graph = None
        self.scm = None
        self.do_calculus = None

    def create_graph(self, request: GraphRequest) -> GraphResponse:
        """Create a new causal graph.

        Args:
            request: Graph creation request

        Returns:
            Graph information
        """
        try:
            self.graph = CausalGraph(edges=request.edges)
            self.do_calculus = DoCalculus(self.graph)
            return GraphResponse(
                nodes=self.graph.get_nodes(),
                edges=self.graph.get_edges(),
                message="Graph created successfully",
            )
        except ValueError as e:
            return GraphResponse(nodes=[], edges=[], message=f"Error: {str(e)}")

    def apply_intervention(self, request: InterventionRequest) -> InterventionResponse:
        """Apply an intervention to the graph.

        Args:
            request: Intervention request

        Returns:
            Information about the intervened graph
        """
        if not self.graph:
            return InterventionResponse(
                intervened_nodes=[],
                remaining_edges=[],
                message="No graph available. Create a graph first.",
            )

        intervened_graph = IntervenedGraph(self.graph, {request.variable})

        return InterventionResponse(
            intervened_nodes=list(intervened_graph.interventions),
            remaining_edges=intervened_graph.get_edges(),
            message=f"Intervention do({request.variable}) applied",
        )

    def check_do_calculus(self, request: DoCalculusRequest) -> DoCalculusResponse:
        """Check if a do-calculus rule applies.

        Args:
            request: Do-calculus request

        Returns:
            Whether the rule applies
        """
        if not self.do_calculus:
            return DoCalculusResponse(
                applicable=False, message="No graph available. Create a graph first."
            )

        outcome = set(request.outcome)
        intervention = set(request.intervention)
        conditioning = set(request.conditioning) if request.conditioning else set()

        applicable = False
        rule_name = ""

        if request.rule == 1:
            applicable = self.do_calculus.rule1(
                outcome, set(), conditioning, intervention
            )
            rule_name = "Rule 1 (Insertion/deletion of observations)"
        elif request.rule == 2:
            applicable = self.do_calculus.rule2(
                outcome, set(), conditioning, intervention
            )
            rule_name = "Rule 2 (Action/observation exchange)"
        elif request.rule == 3:
            applicable = self.do_calculus.rule3(
                outcome, set(), conditioning, intervention
            )
            rule_name = "Rule 3 (Insertion/deletion of actions)"
        else:
            return DoCalculusResponse(
                applicable=False, message="Please specify rule 1, 2, or 3"
            )

        return DoCalculusResponse(
            applicable=applicable,
            message=f"{rule_name}: {'Applies' if applicable else 'Does not apply'}",
        )

    def compute_counterfactual(
        self, request: CounterfactualRequest
    ) -> CounterfactualResponse:
        """Compute a counterfactual value.

        Args:
            request: Counterfactual request

        Returns:
            Counterfactual value
        """
        if not self.scm:
            return CounterfactualResponse(
                value=0.0,
                message="No structural causal model available. Add equations first.",
            )

        try:
            value = self.scm.compute_counterfactual(
                intervention=request.intervention,
                factual_evidence=request.factual_evidence,
                query_variable=request.query_variable,
            )
            return CounterfactualResponse(
                value=value, message="Counterfactual computed successfully"
            )
        except Exception as e:
            return CounterfactualResponse(
                value=0.0, message=f"Error computing counterfactual: {str(e)}"
            )

    def add_structural_equation(
        self,
        variable: str,
        parents: list[str],
        function: Optional[StructuralFunction] = None,
    ) -> None:
        """Add a structural equation to the SCM.

        Args:
            variable: Variable name
            parents: List of parent variable names
            function: Optional function f(parents, error) -> value
        """
        if not self.graph:
            raise ValueError("Create a graph first")

        equation = StructuralEquation(
            variable=variable,
            parents=parents,
            function=function,
        )

        if not self.scm:
            self.scm = StructuralCausalModel(self.graph)

        self.scm.add_equation(equation)
