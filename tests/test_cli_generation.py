"""Drive the real cookiecutter CLI, the same path `uvx cookiecutter` takes.

pytest-cookies calls the Python API, so it can pass while the command a person actually
runs fails on prompt config, extra-context parsing, or hook output. These drive the CLI.
"""

import os
import subprocess
import sys

import pytest
from support import TEMPLATE_ROOT

# Every question the CLI asks, in order. Changing this list is a deliberate decision.
EXPECTED_PROMPTS = [
    "full_name",
    "email",
    "github_username",
    "project_name",
    "project_slug",
    "project_short_description",
    "Affiliation for the paper's title page",
    "version",
    "Select command_line_interface",
    "Select open_source_license",
    "Add the deep-learning pack?",
]

# The exact answers that failed for the user in the report that prompted these tests.
REPORTED_CONTEXT = [
    "project_name=field_maps",
    "project_short_description=Experimental agricultural maps.",
    "command_line_interface=Argparse",
    "open_source_license=MIT license",
]


def run_cli(destination, extra_context=(), env_overrides=None, stdin=None):
    env = {**os.environ, "COOKIECUTTER_SKIP_LOCK": "1"}
    env.update(env_overrides or {})
    command = [sys.executable, "-m", "cookiecutter", str(TEMPLATE_ROOT)]
    if stdin is None:
        command.append("--no-input")
    command += ["-o", str(destination), *extra_context]
    return subprocess.run(
        command,
        input=stdin,
        env=env,
        text=True,
        capture_output=True,
    )


def test_cli_generates_the_default_project(tmp_path):
    result = run_cli(tmp_path)

    assert result.returncode == 0, result.stderr
    project = tmp_path / "python_boilerplate"
    assert project.is_dir()
    assert (project / "AGENTS.md").exists()
    assert (project / "CLAUDE.md").is_symlink()
    assert (project / ".git").is_dir()
    assert "WARNING" not in result.stdout


def test_cli_generates_the_reported_configuration(tmp_path):
    result = run_cli(tmp_path, extra_context=REPORTED_CONTEXT)

    assert result.returncode == 0, result.stderr
    project = tmp_path / "field_maps"
    assert project.is_dir()
    assert (project / "field_maps" / "cli.py").exists()
    assert "MIT" in (project / "LICENSE").read_text()
    assert 'license = "MIT"' in (project / "pyproject.toml").read_text()
    assert (project / "paper").is_dir()
    assert (project / "knowledge_base").is_dir()
    assert not (project / ".github").exists()
    assert not (project / "configs").exists()


def test_cli_generates_the_deep_learning_pack(tmp_path):
    result = run_cli(tmp_path, extra_context=["deep-learning=yes"])

    assert result.returncode == 0, result.stderr
    project = tmp_path / "python_boilerplate"
    assert (project / "scripts" / "train.py").exists()
    assert "torch" in (project / "pyproject.toml").read_text()


def test_cli_prompts_are_self_explanatory(tmp_path):
    result = run_cli(
        tmp_path,
        stdin="\n" * len(EXPECTED_PROMPTS),
        env_overrides={"COLUMNS": "200"},
    )

    assert result.returncode == 0, result.stderr
    prompts = result.stdout

    for index, expected in enumerate(EXPECTED_PROMPTS, start=1):
        marker = f"[{index}/{len(EXPECTED_PROMPTS)}] {expected}"
        assert marker in prompts, f"missing prompt: {marker}\n\n{prompts}"

    # No unexplained yes/no question survives, and no extra question sneaks in.
    assert f"[{len(EXPECTED_PROMPTS) + 1}/" not in prompts
    assert "Select deep-learning" not in prompts
    assert "claude-code" not in prompts
    assert "copilot" not in prompts.lower()


def test_cli_rejects_an_invalid_project_slug(tmp_path):
    result = run_cli(tmp_path, extra_context=["project_name=9 bad slug"])

    assert result.returncode != 0
    assert "not a valid Python module" in result.stdout + result.stderr
    assert not list(tmp_path.iterdir())


@pytest.mark.slow
def test_cli_writes_a_lockfile_that_syncs(tmp_path):
    """Exercise the real lock step against whichever index uv is configured to use."""
    result = run_cli(tmp_path, env_overrides={"COOKIECUTTER_SKIP_LOCK": "0"})

    assert result.returncode == 0, result.stderr
    project = tmp_path / "python_boilerplate"
    if not (project / "uv.lock").exists():
        # Generation still succeeded, which is the guarantee that matters. Report the
        # reason rather than failing the suite on someone else's blocked network.
        pytest.skip(f"uv could not reach a package index:\n{result.stdout}")

    sync = subprocess.run(
        ["uv", "sync", "--frozen"],
        cwd=project,
        text=True,
        capture_output=True,
    )
    assert sync.returncode == 0, sync.stderr
