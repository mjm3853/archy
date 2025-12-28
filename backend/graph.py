"""Causal graph representation and operations."""

from __future__ import annotations

from typing import Any, List, Optional, Set, Tuple

import networkx as nx


class CausalGraph:
    """Represents a causal directed acyclic graph (DAG).

    This class provides the foundation for causal reasoning operations
    including do-calculus, interventions, and counterfactuals.
    """

    _graph: nx.DiGraph

    def __init__(self, edges: Optional[List[Tuple[str, str]]] = None) -> None:
        """Initialize a causal graph.

        Args:
            edges: List of (parent, child) tuples representing causal edges.
                  If None, creates an empty graph.
        """
        self._graph = nx.DiGraph()
        if edges:
            self._graph.add_edges_from(edges)

        # Validate it's a DAG
        if not nx.is_directed_acyclic_graph(self._graph):
            raise ValueError("Graph must be a directed acyclic graph (DAG)")

    def add_edge(self, parent: str, child: str) -> None:
        """Add a causal edge from parent to child.

        Args:
            parent: Parent variable name
            child: Child variable name

        Raises:
            ValueError: If adding the edge would create a cycle
        """
        self._graph.add_edge(parent, child)
        if not nx.is_directed_acyclic_graph(self._graph):
            self._graph.remove_edge(parent, child)
            raise ValueError(f"Adding edge ({parent}, {child}) would create a cycle")

    def remove_edge(self, parent: str, child: str) -> None:
        """Remove a causal edge."""
        self._graph.remove_edge(parent, child)

    def get_parents(self, node: str) -> Set[str]:
        """Get all parent nodes of a given node."""
        return set(self._graph.predecessors(node))

    def get_children(self, node: str) -> Set[str]:
        """Get all child nodes of a given node."""
        return set(self._graph.successors(node))

    def get_ancestors(self, node: str) -> Set[str]:
        """Get all ancestor nodes (parents, grandparents, etc.) of a given node."""
        return set(nx.ancestors(self._graph, node))

    def get_descendants(self, node: str) -> Set[str]:
        """Get all descendant nodes (children, grandchildren, etc.) of a given node."""
        return set(nx.descendants(self._graph, node))

    def get_nodes(self) -> List[str]:
        """Get all nodes in the graph."""
        return list(self._graph.nodes())

    def get_edges(self) -> List[Tuple[str, str]]:
        """Get all edges in the graph."""
        return list(self._graph.edges())

    def is_d_separated(self, x: Set[str], y: Set[str], z: Set[str]) -> bool:
        """Check if sets X and Y are d-separated given Z.

        This is fundamental for causal reasoning - d-separation determines
        conditional independence in causal graphs.

        Args:
            x: Set of nodes X
            y: Set of nodes Y
            z: Set of conditioning nodes Z

        Returns:
            True if X and Y are d-separated given Z
        """
        # Use networkx's d-separation check
        return nx.is_d_separator(self._graph, x, y, z)

    def get_backdoor_paths(self, treatment: str, outcome: str) -> List[List[str]]:
        """Find all backdoor paths from treatment to outcome.

        Backdoor paths are paths that start with an arrow pointing into treatment.
        These need to be blocked for proper causal effect estimation.

        Args:
            treatment: Treatment variable
            outcome: Outcome variable

        Returns:
            List of paths, where each path is a list of node names
        """
        paths = []
        # Find all simple paths from treatment to outcome
        for path in nx.all_simple_paths(self._graph, treatment, outcome):
            # Check if it's a backdoor path (starts with incoming edge)
            # In a DAG, we need to check if there's a path that goes backwards
            # from treatment first
            parents = self.get_parents(treatment)
            if parents:
                # Check paths through parents
                for parent in parents:
                    if parent in path:
                        paths.append(path)
        return paths

    def to_dict(self) -> dict[str, Any]:
        """Serialize graph to dictionary format."""
        return {"nodes": self.get_nodes(), "edges": self.get_edges()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CausalGraph:
        """Create graph from dictionary format."""
        return cls(edges=data.get("edges", []))

    def __repr__(self) -> str:
        return (
            f"CausalGraph(nodes={len(self.get_nodes())}, edges={len(self.get_edges())})"
        )
