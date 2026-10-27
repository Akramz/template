"""Shared fixtures for the {{ cookiecutter.project_slug }} test suite."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Repo root, for tests that need to reach configs/ or artifacts/."""
    return PROJECT_ROOT


@pytest.fixture
def tmp_run_dir(tmp_path: Path) -> Path:
    """Isolated output directory.

    Tests must never write into the repo. Leftover artifacts make the next run
    non-deterministic and pollute the working tree an agent is about to commit.
    """
    d = tmp_path / "run"
    d.mkdir()
    return d
