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
uv sync                  # Install dependencies and CLI
uv sync --group dev      # Include dev tools (pytest, mypy, ruff, pre-commit)

# Run CLI
uv run archy             # Recommended
. .venv/bin/activate && archy  # Or activate venv first
```

## Quick Start

### Basic Causal Graph

```python
from backend import CausalGraph

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
from backend.interventions import IntervenedGraph

# Apply intervention do(Y)
intervened = IntervenedGraph(graph, {"Y"})

# After intervention, Y has no parents
print(intervened.get_parents("Y"))  # set()
```

### API Service (for UI Integration)

```python
from backend.api import CausalAIService, GraphRequest, InterventionRequest

service = CausalAIService()

# Create graph
graph_request = GraphRequest(edges=[("Treatment", "Outcome")])
response = service.create_graph(graph_request)

# Apply intervention
intervention_request = InterventionRequest(variable="Treatment", value=1.0)
intervention_response = service.apply_intervention(intervention_request)
```

## CLI

Unix-style commands that can be piped together:

```bash
# Create and display a graph
archy graph -e X Y -e Y Z

# Pipe commands together with --json
archy graph -e X Y -e Z Y --json | archy info
archy graph -e X Y -e Z Y --json | archy do Y
archy graph -e X Y -e Z Y --json | archy dsep X Z -g Y
archy graph -e Z X -e Z Y -e X Y --json | archy paths X Y
```

Available commands:
- `graph` - Create a causal graph
- `do` - Apply do-intervention (remove incoming edges)
- `info` - Display graph information
- `dsep` - Check d-separation between variables
- `paths` - Find backdoor paths

## Examples

See `examples/basic_usage.py` for comprehensive examples of all features.

```bash
uv run python examples/basic_usage.py
```

## Development

```bash
uv run pytest                        # Run tests
uv run pytest -k "test_name"         # Run single test
uv run mypy backend/                 # Type check
uv run ruff check backend/           # Lint
uv run ruff format backend/          # Format
uv run pre-commit run --all-files    # Run all checks
```

## Versioning & Release

Uses [SemVer](https://semver.org/) with `bump-my-version`:

```bash
uv run bump-my-version bump patch    # 0.1.0 → 0.1.1
uv run bump-my-version bump minor    # 0.1.0 → 0.2.0
uv run bump-my-version bump major    # 0.1.0 → 1.0.0
```

This updates `pyproject.toml` and `backend/__init__.py`, commits, and creates a git tag.

## Distribution

```bash
# Build package
uv build

# Install globally as a tool
uv tool install .

# Install from git
uv pip install git+https://github.com/USER/archy.git

# Publish to PyPI (when ready)
uv publish
```

## Architecture

- `backend/graph.py`: Causal graph representation and DAG operations
- `backend/interventions.py`: Intervention operations (do-calculus)
- `backend/do_calculus.py`: Do-calculus rules implementation
- `backend/counterfactuals.py`: Structural causal models and counterfactual reasoning
- `backend/api.py`: High-level API service for UI integration
- `backend/cli/`: Click-based CLI with rich terminal output

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
- `click`, `rich`: CLI and terminal output

## License

MIT
