# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Backend toolkit for causal AI implementing Judea Pearl's causal hierarchy:

1. **Association** (Level 1): Observing correlations
2. **Intervention** (Level 2): "What if I do X?" - do-calculus
3. **Counterfactuals** (Level 3): "What would have happened if...?" - SCMs

## Commands

Run `make help` for all available commands. Key ones:

```bash
# Development
make install        # Install dependencies (uv sync --group dev)
make dev            # Build and install CLI globally (run after code changes)
make check          # Lint + format check + type check (ruff + mypy)
make format         # Auto-fix lint and format issues
make test           # Run all tests (pytest)

# Release
make version        # Show current version
make release-patch  # Bump patch, build, install (0.1.0 → 0.1.1)
make release-minor  # Bump minor, build, install (0.1.0 → 0.2.0)
make release-major  # Bump major, build, install (0.1.0 → 1.0.0)
make publish        # Build and publish to PyPI

# Other
make clean          # Remove build artifacts
```

**Testing**:

- All tests: `make test` or `uv run pytest`
- Single test: `uv run pytest -k "test_name"`
- Watch mode: `uv run pytest --watch`

**After code changes**: Run `make dev` to rebuild and reinstall the CLI globally, then test with `archy` command.

## CLI

Unix-style commands, pipeable via JSON:

```bash
uv run archy             # Show welcome and commands

# Basic graph creation
archy graph -e Smoking Cancer                    # Single edge
archy graph -c "Smoking Tar Cancer"              # Chain: Smoking→Tar→Cancer
archy graph -e Age Treatment -e Age Outcome -e Treatment Outcome  # Confounded

# Pipe commands with --json
archy graph -e Treatment Outcome --json | archy info
archy graph -e Treatment Outcome --json | archy do Treatment

# D-separation (conditional independence)
archy graph -e Smoking Tar -e Tar Cancer --json | archy dsep Smoking Cancer -g Tar

# Find backdoor paths (confounding)
archy graph -e Age Treatment -e Age Outcome -e Treatment Outcome --json | archy paths Treatment Outcome
```

### Example Causal Structures

Use `archy examples` for built-in causal structure templates:

```bash
archy examples                    # List all structures
archy examples collider           # Show details for collider
archy examples mediator --run     # Show and render graph
```

Available: `confounder`, `mediator`, `collider`, `frontdoor`, `instrumental`, `m-bias`

## Architecture

```bash
backend/
├── __init__.py        # Public API exports: CausalGraph, DoCalculus, etc.
├── graph.py           # CausalGraph: DAG via networkx, d-separation
├── interventions.py   # Intervention, IntervenedGraph: do-operator
├── do_calculus.py     # DoCalculus: Rules 1-3 for causal expressions
├── counterfactuals.py # StructuralCausalModel, StructuralEquation
├── api.py             # CausalAIService + Pydantic request/response models
├── py.typed           # PEP 561 marker for type checking
└── cli/
    ├── __init__.py    # Re-exports cli from main
    └── main.py        # Click commands: graph, do, info, dsep, paths, examples

examples/
└── basic_usage.py     # Comprehensive examples of all features
```

**Data flow**: `CausalGraph` (DAG) → `IntervenedGraph` (apply do-operator) → `DoCalculus` (check rule applicability) → `StructuralCausalModel` (counterfactual computation)

**Key patterns**:

- `CausalGraph.from_dict()` / `to_dict()` for JSON serialization (enables CLI piping)
- `IntervenedGraph` creates modified graph copy, doesn't mutate original
- `CausalAIService` is the stateful facade for UI integration (holds graph + SCM state)
- All Pydantic models in `api.py` for typed request/response contracts
- Graph operations maintain DAG invariant (adding cycles raises `ValueError`)
- D-separation implemented via networkx's `d_separated()` function

**Python API Usage**:

```python
from backend import CausalGraph, IntervenedGraph, DoCalculus, StructuralCausalModel

# Create graph
graph = CausalGraph(edges=[("X", "Y"), ("Z", "Y")])

# Query structure
graph.get_parents("Y")      # {'X', 'Z'}
graph.get_ancestors("Y")    # All upstream nodes
graph.is_d_separated({"X"}, {"Z"}, {"Y"})  # Conditional independence

# Apply intervention
intervened = IntervenedGraph(graph, {"Y"})  # do(Y) - removes incoming edges

# Do-calculus (check if rules apply)
do_calc = DoCalculus(graph)
do_calc.can_apply_rule_1(outcome, intervention, conditioning)
```

For UI integration, use `CausalAIService` from `backend.api` with Pydantic request/response models.

## Versioning

Version tracked in `pyproject.toml` and `backend/__init__.py`. Use `make release-*` commands to bump, build, and install in one step. Requires clean git working directory.

**Release process**:

1. Update `CHANGELOG.md` with changes under `[Unreleased]`
2. Run `make release-patch` (or minor/major) — prompts for changelog confirmation
3. Push with `git push && git push --tags`

**Version sync**: `bump-my-version` automatically updates both files and creates a git tag (configured in `pyproject.toml`).
