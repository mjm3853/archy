# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.4] - 2024-12-30

### Added
- Ideas folder with Reasoning Engine vision documents
  - Conversational causal AI concepts (mediation analysis, fairness auditing, counterfactual engine)
  - Personal finance domain application example
- CHANGELOG.md for tracking version history
- Improved release process with changelog integration

### Changed
- Enhanced CLAUDE.md with better formatting and Python API examples
- Makefile improvements for release workflow

## [0.1.3] - 2024-12-29

### Added
- Makefile with standardized development commands
- `make dev` for building and installing CLI globally
- `make release-*` commands for version bumping

## [0.1.2] - 2024-12-29

### Changed
- Build configuration updates

## [0.1.1] - 2024-12-29

### Added
- Initial public release
- Core causal graph implementation with d-separation
- Do-calculus (Rules 1-3) for causal inference
- Intervention support via `IntervenedGraph`
- Structural Causal Models for counterfactual reasoning
- CLI with pipeable JSON commands (`graph`, `do`, `info`, `dsep`, `paths`)
- Example causal structures (confounder, mediator, collider, frontdoor, instrumental, m-bias)
- `CausalAIService` API for UI integration
- Pydantic models for typed request/response contracts

[Unreleased]: https://github.com/mjm3853/archy/compare/v0.1.4...HEAD
[0.1.4]: https://github.com/mjm3853/archy/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/mjm3853/archy/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/mjm3853/archy/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/mjm3853/archy/releases/tag/v0.1.1
