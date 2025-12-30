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
archy graph -e Smoking Cancer                    # Single edge
archy graph -c "Smoking Tar Cancer"              # Chain: Smoking→Tar→Cancer
archy graph -e Age Treatment -e Age Outcome -e Treatment Outcome  # Confounded

# Pipe commands together with --json
archy graph -e Treatment Outcome --json | archy info
archy graph -e Treatment Outcome --json | archy do Treatment
archy graph -e Smoking Tar -e Tar Cancer --json | archy dsep Smoking Cancer -g Tar
archy graph -e Age Treatment -e Age Outcome -e Treatment Outcome --json | archy paths Treatment Outcome
```

Available commands:

- `graph` - Create a causal graph from edges or chains
- `do` - Apply do-intervention (remove incoming edges)
- `info` - Display graph information
- `dsep` - Check d-separation between variables
- `paths` - Find backdoor paths
- `examples` - Show example causal structures (confounder, mediator, collider, etc.)

### Example Causal Structures

```bash
archy examples                    # List all structures
archy examples collider           # Show details
archy examples mediator --run     # Show and render graph
```

Available: `confounder`, `mediator`, `collider`, `frontdoor`, `instrumental`, `m-bias`

## Examples

See `examples/basic_usage.py` for comprehensive examples of all features.

```bash
uv run python examples/basic_usage.py
```

## Development

```bash
make install        # Install dependencies
make dev            # Build and install CLI globally
make check          # Lint + format check + type check
make format         # Auto-fix lint and format issues
make test           # Run tests

# Single test
uv run pytest -k "test_name"
```

## Versioning & Release

Uses [SemVer](https://semver.org/). See [CHANGELOG.md](CHANGELOG.md) for version history.

```bash
make version        # Show current version
make release-patch  # 0.1.0 → 0.1.1
make release-minor  # 0.1.0 → 0.2.0
make release-major  # 0.1.0 → 1.0.0
make publish        # Build and publish to PyPI
```

**Release process**: Update `CHANGELOG.md` → run `make release-*` → push with tags.

## Architecture

- `backend/graph.py`: CausalGraph - DAG representation, d-separation
- `backend/interventions.py`: Intervention, IntervenedGraph - do-operator
- `backend/do_calculus.py`: DoCalculus - Rules 1-3 for causal expressions
- `backend/counterfactuals.py`: StructuralCausalModel - SCM-based counterfactuals
- `backend/api.py`: CausalAIService + Pydantic models for UI integration
- `backend/cli/`: Click-based CLI (graph, do, info, dsep, paths, examples)

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
