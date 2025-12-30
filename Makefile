.PHONY: help install dev check format test build release-patch release-minor release-major publish clean version

# Default target
help:
	@echo "archy development commands"
	@echo ""
	@echo "Development:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Build and install CLI globally"
	@echo "  make check      - Run linting, formatting, and type checks"
	@echo "  make format     - Auto-fix linting and formatting issues"
	@echo "  make test       - Run tests"
	@echo ""
	@echo "Release:"
	@echo "  make version        - Show current version"
	@echo "  make release-patch  - Bump patch version, build, install (0.1.0 → 0.1.1)"
	@echo "  make release-minor  - Bump minor version, build, install (0.1.0 → 0.2.0)"
	@echo "  make release-major  - Bump major version, build, install (0.1.0 → 1.0.0)"
	@echo "  make publish        - Build and publish to PyPI"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean      - Remove build artifacts"

# Development
install:
	uv sync --group dev

dev: clean build
	uv tool install dist/archy-*.whl --force
	@echo ""
	@archy --version
	@echo "Installed successfully. Run 'archy' to verify."

check:
	uv run ruff check backend/
	uv run ruff format --check backend/
	uv run mypy backend/

format:
	uv run ruff check --fix backend/
	uv run ruff format backend/

test:
	uv run pytest

# Build
build:
	rm -rf dist/
	uv build

# Version
version:
	@grep 'version = ' pyproject.toml | head -1 | cut -d'"' -f2

# Release (bump version + build + install)
# Remember to update CHANGELOG.md before releasing!
release-patch: _ensure-clean _check-changelog
	uv run bump-my-version bump patch
	@$(MAKE) dev
	@echo ""
	@echo "Don't forget to: git push && git push --tags"

release-minor: _ensure-clean _check-changelog
	uv run bump-my-version bump minor
	@$(MAKE) dev
	@echo ""
	@echo "Don't forget to: git push && git push --tags"

release-major: _ensure-clean _check-changelog
	uv run bump-my-version bump major
	@$(MAKE) dev
	@echo ""
	@echo "Don't forget to: git push && git push --tags"

# Publish to PyPI
publish: clean build
	uv publish

# Clean build artifacts
clean:
	rm -rf dist/ build/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Internal: ensure git working directory is clean for releases
_ensure-clean:
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "Error: Git working directory is not clean. Commit or stash changes first."; \
		exit 1; \
	fi

# Internal: remind to update changelog
_check-changelog:
	@if ! grep -q "\[Unreleased\]" CHANGELOG.md 2>/dev/null; then \
		echo "Warning: CHANGELOG.md not found or missing [Unreleased] section."; \
	fi
	@echo "Reminder: Update CHANGELOG.md with changes for this release."
	@read -p "Continue with release? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
