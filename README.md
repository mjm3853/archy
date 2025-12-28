# Archy

A backend toolkit for causal AI concepts: do-calculus, counterfactuals, and interventions.

## Overview

Archy provides a Python backend for working with causal inference concepts, designed to be consumed by UI applications. It implements:

- **Causal Graphs (DAGs)**: Represent causal relationships between variables
- **Do-Calculus**: Rules for manipulating causal expressions
- **Interventions**: Apply do-operations to break causal dependencies
- **Counterfactuals**: Answer "what if" questions using structural causal models

## Installation

```bash
uv sync                  # Install dependencies
uv sync --group dev      # Include dev tools (pytest, mypy, ruff, pre-commit)
```

## Quick Start

### Basic Causal Graph

```python
from archy import CausalGraph

# Create a causal graph: X -> Y <- Z
graph = CausalGraph(edges=[("X", "Y"), ("Z", "Y")])

# Get graph properties
print(graph.get_parents("Y"))  # {'X', 'Z'}
print(graph.get_children("X"))  # {'Y'}

# Check d-separation
is_d_sep = graph.is_d_separated({"X"}, {"Z"}, {"Y"})
```

### Interventions

```python
from archy.interventions import IntervenedGraph

# Apply intervention do(Y)
intervened = IntervenedGraph(graph, {"Y"})

# After intervention, Y has no parents
print(intervened.get_parents("Y"))  # set()
```

### API Service (for UI Integration)

```python
from archy.api import CausalAIService, GraphRequest, InterventionRequest

service = CausalAIService()

# Create graph
graph_request = GraphRequest(edges=[("Treatment", "Outcome")])
response = service.create_graph(graph_request)

# Apply intervention
intervention_request = InterventionRequest(variable="Treatment", value=1.0)
intervention_response = service.apply_intervention(intervention_request)
```

## Examples

See `examples/basic_usage.py` for comprehensive examples of all features.

Run examples:
```bash
uv run python examples/basic_usage.py
```

## Development

```bash
uv run pytest                        # Run tests
uv run pytest -k "test_name"         # Run single test
uv run mypy archy/                   # Type check
uv run ruff check archy/             # Lint
uv run ruff format archy/            # Format
uv run pre-commit run --all-files    # Run all checks (ruff + mypy)
```

## Architecture

- `archy/graph.py`: Causal graph representation and DAG operations
- `archy/interventions.py`: Intervention operations (do-calculus)
- `archy/do_calculus.py`: Do-calculus rules implementation
- `archy/counterfactuals.py`: Structural causal models and counterfactual reasoning
- `archy/api.py`: High-level API service for UI integration

## Theory

This toolkit implements concepts from Judea Pearl's causal hierarchy:

1. **Association** (Level 1): Observing correlations
2. **Intervention** (Level 2): "What if I do X?" - requires do-calculus
3. **Counterfactuals** (Level 3): "What would have happened if...?" - requires SCMs

## Next Steps

- [ ] Add data-driven causal effect estimation
- [ ] Implement full identifiability algorithms
- [ ] Add support for latent variables
- [ ] Create REST API wrapper
- [ ] Add visualization utilities
- [ ] Integrate with existing causal inference libraries (DoWhy, CausalML)

## Dependencies

- `networkx`: Graph operations
- `numpy`, `pandas`: Data handling
- `scipy`: Statistical functions
- `pydantic`: Data validation

## License

MIT
