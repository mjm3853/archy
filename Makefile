.PHONY: help install dev check format test build version clean
.PHONY: dev-start dev-bump release-patch release-minor release-major release publish

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
	@echo "Versioning:"
	@echo "  make version    - Show current version"
	@echo "  make dev-start  - Start dev version (0.1.4 → 0.1.5.dev0)"
	@echo "  make dev-bump   - Bump dev version (0.1.5.dev0 → 0.1.5.dev1)"
	@echo "  make release    - Finalize release (0.1.5.dev0 → 0.1.5)"
	@echo ""
	@echo "Release (from stable version):"
	@echo "  make release-patch  - Bump patch (0.1.4 → 0.1.5)"
	@echo "  make release-minor  - Bump minor (0.1.4 → 0.2.0)"
	@echo "  make release-major  - Bump major (0.1.4 → 1.0.0)"
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

# Development versioning (work in progress)
# Start a new dev cycle: 0.1.4 → 0.1.5.dev0
dev-start:
	@if grep -q "\.dev" pyproject.toml; then \
		echo "Already in dev mode. Use 'make dev-bump' or 'make release'."; \
		exit 1; \
	fi
	uv run bump-my-version bump patch  # 0.1.4 → 0.1.5
	uv run bump-my-version bump dev    # 0.1.5 → 0.1.5.dev0
	@$(MAKE) dev
	@echo ""
	@echo "Now in dev mode: $$(make version)"

# Bump dev version: 0.1.5.dev0 → 0.1.5.dev1
dev-bump:
	@if ! grep -q "\.dev" pyproject.toml; then \
		echo "Not in dev mode. Use 'make dev-start' first."; \
		exit 1; \
	fi
	uv run bump-my-version bump dev
	@$(MAKE) dev
	@echo ""
	@echo "Dev version bumped: $$(make version)"

# Finalize release: 0.1.5.dev0 → 0.1.5 (removes dev suffix, tags, and commits)
release: _ensure-clean _check-changelog
	@if ! grep -q "\.dev" pyproject.toml; then \
		echo "Not in dev mode. Use release-patch/minor/major for direct releases."; \
		exit 1; \
	fi
	uv run bump-my-version bump dev --tag --tag-message "Release v{new_version}"
	@$(MAKE) dev
	@echo ""
	@echo "Released: $$(make version)"
	@echo "Don't forget to: git push && git push --tags"

# Direct releases (from stable version, skipping dev cycle)
# Remember to update CHANGELOG.md before releasing!
release-patch: _ensure-clean _check-changelog
	@if grep -q "\.dev" pyproject.toml; then \
		echo "In dev mode. Use 'make release' to finalize, or manually reset version."; \
		exit 1; \
	fi
	uv run bump-my-version bump patch --tag --tag-message "Release v{new_version}"
	@$(MAKE) dev
	@echo ""
	@echo "Don't forget to: git push && git push --tags"

release-minor: _ensure-clean _check-changelog
	@if grep -q "\.dev" pyproject.toml; then \
		echo "In dev mode. Use 'make release' to finalize, or manually reset version."; \
		exit 1; \
	fi
	uv run bump-my-version bump minor --tag --tag-message "Release v{new_version}"
	@$(MAKE) dev
	@echo ""
	@echo "Don't forget to: git push && git push --tags"

release-major: _ensure-clean _check-changelog
	@if grep -q "\.dev" pyproject.toml; then \
		echo "In dev mode. Use 'make release' to finalize, or manually reset version."; \
		exit 1; \
	fi
	uv run bump-my-version bump major --tag --tag-message "Release v{new_version}"
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
