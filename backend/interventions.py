"""Intervention operations for causal reasoning."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Set, List, Tuple

import networkx as nx
from pydantic import BaseModel

if TYPE_CHECKING:
    from backend.graph import CausalGraph


class Intervention(BaseModel):
    """Represents a do-intervention on a causal graph.

    An intervention sets a variable to a specific value, breaking
    its causal dependencies (removing incoming edges).
    """

    variable: str
    value: Optional[float] = None

    def __repr__(self) -> str:
        val_str = f"={self.value}" if self.value is not None else ""
        return f"do({self.variable}{val_str})"


class IntervenedGraph:
    """A causal graph with interventions applied.

    When we intervene on a variable, we remove all incoming edges
    to that variable, effectively setting it to a fixed value.
    """

    original_graph: CausalGraph
    interventions: Set[str]
    _graph: nx.DiGraph

    def __init__(self, graph: CausalGraph, interventions: Set[str]) -> None:
        """Create an intervened graph.

        Args:
            graph: The original CausalGraph
            interventions: Set of variable names to intervene on
        """
        self.original_graph = graph
        self.interventions = interventions
        self._build_intervened_graph()

    def _build_intervened_graph(self) -> None:
        """Build the graph structure after interventions."""

        # Start with a copy of the original graph
        self._graph = self.original_graph._graph.copy()

        # Remove all incoming edges to intervened variables
        for var in self.interventions:
            # Get all incoming edges
            incoming = list(self._graph.predecessors(var))
            for parent in incoming:
                self._graph.remove_edge(parent, var)

    def get_parents(self, node: str) -> Set[str]:
        """Get parents after intervention."""
        return set(self._graph.predecessors(node))

    def get_children(self, node: str) -> Set[str]:
        """Get children after intervention."""
        return set(self._graph.successors(node))

    def get_nodes(self) -> List[str]:
        """Get all nodes."""
        return list(self._graph.nodes())

    def get_edges(self) -> List[Tuple[str, str]]:
        """Get all edges after intervention."""
        return list(self._graph.edges())

    def __repr__(self) -> str:
        interventions_str = ", ".join(sorted(self.interventions))
        return f"IntervenedGraph(interventions=[{interventions_str}])"
