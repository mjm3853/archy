# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Backend toolkit for causal AI implementing Judea Pearl's causal hierarchy:
1. **Association** (Level 1): Observing correlations
2. **Intervention** (Level 2): "What if I do X?" - do-calculus
3. **Counterfactuals** (Level 3): "What would have happened if...?" - SCMs

## Commands

```bash
uv sync                  # Install dependencies
uv sync --group dev      # Include dev tools
uv run pytest            # Run tests
uv run pytest -k "test_name"  # Run single test
uv run mypy archy/       # Type check
uv run ruff check archy/ # Lint
uv run ruff format archy/ # Format
uv run python examples/basic_usage.py  # Run example

# Pre-commit hooks (run all checks)
uv run pre-commit run --all-files
```

## Architecture

```
archy/
├── graph.py          # CausalGraph: DAG representation using networkx, d-separation
├── interventions.py  # Intervention, IntervenedGraph: do-operator implementation
├── do_calculus.py    # DoCalculus: Rules 1-3 for manipulating causal expressions
├── counterfactuals.py # StructuralCausalModel, StructuralEquation: SCM-based counterfactuals
└── api.py            # CausalAIService: Pydantic request/response models for UI integration
```

**Core flow**: `CausalGraph` → apply `Intervention` → use `DoCalculus` rules → compute counterfactuals via `StructuralCausalModel`

**Key classes**:
- `CausalGraph`: Wraps networkx DiGraph, enforces DAG constraint, provides d-separation
- `CausalAIService`: Stateful service holding graph/SCM, exposes Pydantic-typed methods for frontend consumption

## Maintenance

After significant changes, update README.md to keep documentation in sync. Run `/init` periodically to refresh this file.
