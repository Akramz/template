.PHONY: help install lint format typecheck test security verify
.DEFAULT_GOAL := help
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

PACKAGE = {{ cookiecutter.project_slug }}
CHECK_PATHS = $(PACKAGE) artifacts tests{% if cookiecutter["deep-learning"] == 'yes' %} scripts{% endif %}

help: ## show available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z_-]+:.*## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## install locked project and development dependencies
	uv sync --frozen

lint: ## check style and formatting
	uv run ruff check $(CHECK_PATHS)
	uv run ruff format --check $(CHECK_PATHS)

format: ## apply safe formatting fixes
	uv run ruff check --fix $(CHECK_PATHS)
	uv run ruff format $(CHECK_PATHS)

typecheck: ## type check executable project code
	uv run ty check $(CHECK_PATHS)

test: ## run tests with no feature-wide skips
	uv run pytest

security: ## scan source and installed dependencies for known security defects
	uv run bandit -q -r $(PACKAGE){% if cookiecutter["deep-learning"] == 'yes' %} scripts{% endif %}
	uv export --frozen --no-emit-project --format requirements-txt | uv run pip-audit --strict --require-hashes --disable-pip -r /dev/stdin

verify: lint typecheck test security ## run the complete handoff gate
