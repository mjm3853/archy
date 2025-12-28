"""Counterfactual reasoning operations.

Counterfactuals answer "what if" questions - what would have happened
if things had been different. This requires structural causal models (SCMs)
with explicit functional relationships.
"""

from __future__ import annotations

from typing import Callable, Optional

from pydantic import BaseModel

from archy.graph import CausalGraph

# Type alias for structural equation functions: f(parent_values, error) -> value
StructuralFunction = Callable[[list[float], float], float]


class StructuralEquation(BaseModel):
    """Represents a structural equation in a causal model.

    Each variable has a structural equation: Y = f(PA_Y, U_Y)
    where PA_Y are parents and U_Y is an error term.
    """

    variable: str
    function: Optional[StructuralFunction] = None
    parents: list[str] = []
    error_distribution: Optional[str] = None  # e.g., "normal", "uniform"

    def evaluate(self, parent_values: dict[str, float], error: float = 0.0) -> float:
        """Evaluate the structural equation.

        Args:
            parent_values: Dictionary of parent variable values
            error: Error term value

        Returns:
            Computed value for this variable
        """
        if self.function:
            parent_list = [parent_values.get(p, 0.0) for p in self.parents]
            return self.function(parent_list, error)
        return error  # Default: just return error if no function


class StructuralCausalModel:
    """A structural causal model (SCM) for counterfactual reasoning.

    An SCM consists of:
    1. A causal graph (DAG)
    2. Structural equations for each variable
    3. Error term distributions
    """

    graph: CausalGraph
    equations: dict[str, StructuralEquation]

    def __init__(self, graph: CausalGraph) -> None:
        """Initialize an SCM.

        Args:
            graph: The causal graph
        """
        self.graph = graph
        self.equations = {}

    def add_equation(self, equation: StructuralEquation) -> None:
        """Add a structural equation.

        Args:
            equation: The structural equation to add
        """
        # Verify parents match graph structure
        graph_parents = self.graph.get_parents(equation.variable)
        if set(equation.parents) != graph_parents:
            raise ValueError(
                f"Equation parents {set(equation.parents)} don't match "
                f"graph parents {graph_parents} for variable {equation.variable}"
            )
        self.equations[equation.variable] = equation

    def compute_counterfactual(
        self,
        intervention: dict[str, float],
        factual_evidence: dict[str, float],
        query_variable: str,
    ) -> float:
        """Compute a counterfactual value.

        "What would Y have been if X had been x', given that we observed X=x, Y=y?"

        This requires:
        1. Abduction: Infer error terms from factual evidence
        2. Action: Apply intervention (set X to x')
        3. Prediction: Compute Y under the intervention

        Args:
            intervention: Dictionary of {variable: value} to intervene on
            factual_evidence: Observed values in the factual world
            query_variable: Variable to query in the counterfactual world

        Returns:
            Counterfactual value of query_variable
        """
        # Step 1: Abduction - infer error terms from factual evidence
        # This is simplified - real abduction requires solving the system
        errors = self._abduce_errors(factual_evidence)

        # Step 2: Action - apply intervention
        intervened_values = factual_evidence.copy()
        intervened_values.update(intervention)

        # Step 3: Prediction - compute counterfactual
        return self._compute_variable(query_variable, intervened_values, errors)

    def _abduce_errors(self, evidence: dict[str, float]) -> dict[str, float]:
        """Infer error terms from observed evidence.

        This is a simplified version. In practice, this requires
        solving the system of equations backwards.

        Args:
            evidence: Observed variable values

        Returns:
            Dictionary of inferred error terms
        """
        errors: dict[str, float] = {}
        # Simplified: assume errors are zero for now
        # Real implementation would solve: U = Y - f(PA_Y)
        for var in self.graph.get_nodes():
            errors[var] = 0.0
        return errors

    def _compute_variable(
        self,
        variable: str,
        values: dict[str, float],
        errors: dict[str, float],
    ) -> float:
        """Compute a variable value given parent values and errors.

        Args:
            variable: Variable to compute
            values: Current values of all variables
            errors: Error terms

        Returns:
            Computed value
        """
        if variable not in self.equations:
            # If no equation, return current value or error
            return values.get(variable, errors.get(variable, 0.0))

        equation = self.equations[variable]
        parent_values = {p: values.get(p, 0.0) for p in equation.parents}
        error = errors.get(variable, 0.0)

        return equation.evaluate(parent_values, error)

    def __repr__(self) -> str:
        return f"StructuralCausalModel(graph={self.graph}, equations={len(self.equations)})"
