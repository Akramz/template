.PHONY: help clean clean-skeleton bake paper lint format test test-all verify
.DEFAULT_GOAL := help

BAKE_OPTIONS = --no-input
BAKED = python_boilerplate
SKELETON = {{cookiecutter.project_slug}}

help: ## show available commands
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z_-]+:.*## / {printf "%-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: clean-skeleton ## remove the baked project and any caches
	rm -rf $(BAKED) .pytest_cache .ruff_cache

clean-skeleton: ## drop git-ignored build output left inside the skeleton
	@# Cookiecutter renders every file it finds, so a stray main.log from compiling
	@# the skeleton by hand fails generation with a Jinja syntax error.
	git clean -Xfdq -- "$(SKELETON)"

bake: clean-skeleton ## generate a project using defaults
	uv run cookiecutter $(BAKE_OPTIONS) . --overwrite-if-exists

paper: clean-skeleton ## bake a project and build its paper PDF
	uv run cookiecutter $(BAKE_OPTIONS) . --overwrite-if-exists
	$(MAKE) -C $(BAKED)/paper
	@echo "built $(BAKED)/paper/main.pdf"

lint: ## check template support code
	uv run ruff check hooks tests
	uv run ruff format --check hooks tests

format: ## format template support code
	uv run ruff check --fix hooks tests
	uv run ruff format hooks tests

test: ## run generator and generated-project tests, without the slow ones
	uv run pytest

test-all: ## also run the slow tests that lock and sync against a package index
	uv run pytest -m ""

verify: lint test ## run the complete template gate
