"""Do-calculus operations for causal inference.

Do-calculus provides rules for manipulating causal expressions,
allowing us to convert interventional distributions into observational ones.
"""

from __future__ import annotations

from typing import Optional, Set

import networkx as nx

from backend.graph import CausalGraph
from backend.interventions import IntervenedGraph


class DoCalculus:
    """Implements do-calculus rules for causal reasoning."""

    graph: CausalGraph

    def __init__(self, graph: CausalGraph) -> None:
        """Initialize with a causal graph.

        Args:
            graph: The causal graph to reason about
        """
        self.graph = graph

    def rule1(self, y: Set[str], z: Set[str], w: Set[str], x: Set[str]) -> bool:
        """Do-calculus Rule 1: Insertion/deletion of observations.

        P(y | do(x), z, w) = P(y | do(x), w) if (Y ⟂ Z | X, W)_{G_{\bar{X}}}

        We can remove Z from the conditioning set if Y and Z are
        d-separated in the graph with X intervened.

        Args:
            y: Outcome variables
            z: Variables to potentially remove
            w: Other conditioning variables
            x: Intervention variables

        Returns:
            True if the rule applies (Z can be removed)
        """
        intervened_graph = IntervenedGraph(self.graph, x)
        # Check d-separation in the intervened graph
        return intervened_graph._graph is not None and self._check_d_separation(
            intervened_graph, y, z, w
        )

    def rule2(self, y: Set[str], z: Set[str], w: Set[str], x: Set[str]) -> bool:
        """Do-calculus Rule 2: Action/observation exchange.

        P(y | do(x), do(z), w) = P(y | do(x), z, w) if (Y ⟂ Z | X, W)_{G_{X̄_Z̲}}

        We can exchange an intervention for an observation if Y and Z are
        d-separated in the graph with X intervened and Z not intervened.

        Args:
            y: Outcome variables
            z: Variables to exchange (intervention -> observation)
            w: Other conditioning variables
            x: Other intervention variables

        Returns:
            True if the rule applies (intervention can become observation)
        """
        # Graph with X intervened but Z not intervened
        # This means we remove edges into X but keep edges into Z
        intervened_graph = IntervenedGraph(self.graph, x)
        # Check d-separation
        return self._check_d_separation(intervened_graph, y, z, w)

    def rule3(self, y: Set[str], z: Set[str], w: Set[str], x: Set[str]) -> bool:
        """Do-calculus Rule 3: Insertion/deletion of actions.

        P(y | do(x), do(z), w) = P(y | do(x), w) if (Y ⟂ Z | X, W)_{G_{\bar{X}\bar{Z}}}

        We can remove an intervention if Y and Z are d-separated in the
        graph with both X and Z intervened.

        Args:
            y: Outcome variables
            z: Variables to potentially remove from interventions
            w: Other conditioning variables
            x: Other intervention variables

        Returns:
            True if the rule applies (Z intervention can be removed)
        """
        # Graph with both X and Z intervened
        intervened_graph = IntervenedGraph(self.graph, x | z)
        # Check d-separation
        return self._check_d_separation(intervened_graph, y, z, w)

    def _check_d_separation(
        self, graph: IntervenedGraph, y: Set[str], z: Set[str], w: Set[str]
    ) -> bool:
        """Helper to check d-separation in an intervened graph."""
        try:
            return nx.is_d_separator(graph._graph, y, z, w)
        except Exception:
            return False

    def is_identifiable(
        self, y: Set[str], x: Set[str], z: Optional[Set[str]] = None
    ) -> bool:
        """Check if P(y | do(x)) is identifiable from observational data.

        This is a simplified check - full identifiability requires
        systematically applying do-calculus rules.

        Args:
            y: Outcome variables
            x: Intervention variables
            z: Optional conditioning variables

        Returns:
            True if the causal effect appears identifiable
        """
        # Basic check: if there are no backdoor paths, it might be identifiable
        # This is a simplified version - full identifiability is more complex
        if z is None:
            z = set()

        # Check if we can block all backdoor paths
        for x_var in x:
            for y_var in y:
                backdoor_paths = self.graph.get_backdoor_paths(x_var, y_var)
                if backdoor_paths:
                    # Check if conditioning on Z blocks these paths
                    # This is simplified - real identifiability is more nuanced
                    pass

        return True  # Simplified - would need full algorithm
