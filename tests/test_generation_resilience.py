"""Post-generation steps must never destroy the project.

Cookiecutter deletes the whole output directory when a hook exits non-zero, so a flaky
network or a missing tool used to wipe a freshly generated project. Each test drives a
real bake with a broken tool and asserts the project survives with a usable warning.
"""

from contextlib import contextmanager

import pytest
from cookiecutter.utils import rmtree

# Stubs run with a stripped PATH, so they use shell builtins only.
UV_NETWORK_FAILURE = """
echo "$@" >> "$STUB_CALLS"
echo "error: Failed to fetch: https://files.pythonhosted.org/ty-0.0.66.whl" >&2
echo "  Caused by: Request failed after 3 retries" >&2
echo "  Caused by: Socket is not connected (os error 57)" >&2
exit 2
"""

UV_LOCK_SUCCESS = """
echo "$@" >> "$STUB_CALLS"
echo "version = 1" > uv.lock
"""

GIT_INIT_FAILURE = """
echo "$@" >> "$STUB_CALLS"
echo "fatal: could not create leading directories" >&2
exit 128
"""


@contextmanager
def baked(cookies, **extra_context):
    result = cookies.bake(extra_context=extra_context or None)
    try:
        yield result
    finally:
        if result.project_path:
            rmtree(str(result.project_path))


@pytest.fixture
def stub_calls(tmp_path, monkeypatch):
    log = tmp_path / "stub-calls.txt"
    monkeypatch.setenv("STUB_CALLS", str(log))
    return log


def assert_remedy_runs_from_the_parent_directory(output, command):
    """Cookiecutter leaves you in the parent directory, so the fix must cd in first."""
    assert f"cd python_boilerplate && {command}" in output, output


def assert_project_is_complete(project_path):
    assert project_path.is_dir()
    assert (project_path / "AGENTS.md").exists()
    assert (project_path / "pyproject.toml").exists()
    assert (project_path / "python_boilerplate" / "__init__.py").exists()
    assert (project_path / "CLAUDE.md").is_symlink()


def test_uv_lock_failure_keeps_the_project_and_warns(
    cookies, monkeypatch, stub_path, stub_calls, capfd
):
    monkeypatch.delenv("COOKIECUTTER_SKIP_LOCK")
    stub_path(stubs={"uv": UV_NETWORK_FAILURE})

    with baked(cookies) as result:
        output = capfd.readouterr().out

        assert result.exit_code == 0
        assert result.exception is None
        assert_project_is_complete(result.project_path)
        assert not (result.project_path / "uv.lock").exists()

        assert "uv lock failed" in output
        assert "files.pythonhosted.org" in output
        assert_remedy_runs_from_the_parent_directory(output, "uv lock")
        # A blocked index is the most likely cause, so name the way out of it.
        assert "UV_DEFAULT_INDEX" in output

        # Transient network errors are retried before the step is given up on.
        assert stub_calls.read_text().splitlines() == ["lock --quiet"] * 3


def test_missing_uv_keeps_the_project_and_warns(cookies, monkeypatch, stub_path, capfd):
    monkeypatch.delenv("COOKIECUTTER_SKIP_LOCK")
    stub_path(available=("git",))

    with baked(cookies) as result:
        output = capfd.readouterr().out

        assert result.exit_code == 0
        assert_project_is_complete(result.project_path)
        assert not (result.project_path / "uv.lock").exists()
        assert "uv was not found on PATH" in output
        assert_remedy_runs_from_the_parent_directory(output, "uv lock")


def test_successful_lock_writes_uv_lock_in_the_project(
    cookies, monkeypatch, stub_path, stub_calls
):
    monkeypatch.delenv("COOKIECUTTER_SKIP_LOCK")
    stub_path(stubs={"uv": UV_LOCK_SUCCESS})

    with baked(cookies) as result:
        assert result.exit_code == 0
        assert (result.project_path / "uv.lock").read_text() == "version = 1\n"
        assert stub_calls.read_text().splitlines() == ["lock --quiet"]


def test_git_init_failure_keeps_the_project_and_warns(
    cookies, stub_path, stub_calls, capfd
):
    stub_path(stubs={"git": GIT_INIT_FAILURE})

    with baked(cookies) as result:
        output = capfd.readouterr().out

        assert result.exit_code == 0
        assert_project_is_complete(result.project_path)
        assert not (result.project_path / ".git").exists()
        assert "git init failed" in output
        assert "could not create leading directories" in output
        assert_remedy_runs_from_the_parent_directory(
            output, "git init --initial-branch=main"
        )

        # An unrecoverable local error is not worth retrying.
        expected = ["init --quiet --initial-branch=main"]
        assert stub_calls.read_text().splitlines() == expected


def test_missing_git_keeps_the_project_and_warns(cookies, stub_path, capfd):
    stub_path(available=())

    with baked(cookies) as result:
        output = capfd.readouterr().out

        assert result.exit_code == 0
        assert_project_is_complete(result.project_path)
        assert not (result.project_path / ".git").exists()
        assert "git was not found on PATH" in output
        assert_remedy_runs_from_the_parent_directory(
            output, "git init --initial-branch=main"
        )


def test_invalid_slug_still_aborts_generation(cookies):
    result = cookies.bake(extra_context={"project_name": "9 bad slug"})
    try:
        assert result.exit_code != 0
        assert result.project_path is None or not result.project_path.exists()
    finally:
        if result.project_path and result.project_path.exists():
            rmtree(str(result.project_path))
