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
uv sync --group dev      # Include dev tools (pytest, mypy, ruff, pre-commit)
uv run pytest            # Run tests
uv run pytest -k "test_name"  # Run single test
uv run mypy backend/     # Type check
uv run ruff check backend/ # Lint
uv run ruff format backend/ # Format
uv run pre-commit run --all-files  # Run all checks (ruff + mypy)
```

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

### Sample Graphs for Demos

```bash
# Smoking → Tar → Cancer (mediation)
archy graph -c "Smoking Tar Cancer"

# Confounded treatment effect: Age confounds Treatment→Outcome
archy graph -e Age Treatment -e Age Outcome -e Treatment Outcome

# Collider: Talent→Success←Luck (conditioning on Success opens path)
archy graph -e Talent Success -e Luck Success

# Front-door criterion: Smoking→Tar→Cancer with unmeasured Genotype
archy graph -e Genotype Smoking -e Genotype Cancer -e Smoking Tar -e Tar Cancer

# Instrumental variable: Rain→Sprinkler→Wet, Rain independent of Shoes
archy graph -e Rain Sprinkler -e Sprinkler Wet -e Shoes Wet
```

## Architecture

```
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
    └── main.py        # Click commands: graph, do, info, dsep, paths
```

**Data flow**: `CausalGraph` (DAG) → `IntervenedGraph` (apply do-operator) → `DoCalculus` (check rule applicability) → `StructuralCausalModel` (counterfactual computation)

**Key patterns**:
- `CausalGraph.from_dict()` / `to_dict()` for JSON serialization (enables CLI piping)
- `IntervenedGraph` creates modified graph copy, doesn't mutate original
- `CausalAIService` is the stateful facade for UI integration (holds graph + SCM state)
- All Pydantic models in `api.py` for typed request/response contracts

## Versioning & Distribution

```bash
uv run bump-my-version bump patch    # 0.1.0 → 0.1.1
uv run bump-my-version bump minor    # 0.1.0 → 0.2.0
uv run bump-my-version bump major    # 0.1.0 → 1.0.0
uv build                             # Build wheel to dist/
```

Version is tracked in both `pyproject.toml` and `backend/__init__.py`.

### Install locally built version

```bash
uv tool install . --force            # Install as global CLI tool (use --force to upgrade)
archy --version                      # Verify installation

# Or install wheel directly into another project
uv pip install dist/archy-*.whl
```
