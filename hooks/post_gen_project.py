#!/usr/bin/env python
import os
import shutil
import subprocess
import time
from pathlib import Path

PROJECT_DIRECTORY = Path.cwd()
LOCK_ATTEMPTS = 3

PACK_PATHS = {
    "deep-learning": [
        "configs",
        "examples",
        "scripts",
        "tests/test_deep_learning_pipeline.py",
        "{{ cookiecutter.project_slug }}/config.py",
        "{{ cookiecutter.project_slug }}/deep_learning.py",
    ],
}

SELECTED_PACKS = {
    "deep-learning": "{{ cookiecutter['deep-learning'] }}" == "yes",
}


def remove_path(relative_path):
    path = PROJECT_DIRECTORY / relative_path
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def replace_with_link(relative_path, target):
    path = PROJECT_DIRECTORY / relative_path
    source = (path.parent / target).resolve()
    remove_path(relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.symlink_to(target, target_is_directory=source.is_dir())
    except OSError:
        if source.is_dir():
            shutil.copytree(source, path)
        else:
            shutil.copy2(source, path)


def remove_unselected_packs():
    for pack, paths in PACK_PATHS.items():
        if not SELECTED_PACKS[pack]:
            for path in paths:
                remove_path(path)


def apply_project_choices():
    if "no" in "{{ cookiecutter.command_line_interface|lower }}":
        remove_path("{{ cookiecutter.project_slug }}/cli.py")

    if "{{ cookiecutter.open_source_license }}" == "Not open source":
        remove_path("LICENSE")


def configure_agent_adapters():
    replace_with_link("CLAUDE.md", "AGENTS.md")


def indent(text):
    return "\n".join(f"         | {line}" for line in text.splitlines())


def warn(message, remedy, hint=None):
    # Cookiecutter deletes the whole output directory when a hook exits non-zero, so the
    # convenience steps below warn instead of failing. Losing the project to a flaky
    # network or a missing tool costs far more than a missing lockfile.
    # The hook runs from the parent directory, so the remedy has to cd in first.
    print(f"\nWARNING: {message}")
    print("         The project was still generated. To finish it, run:")
    print(f"             cd {PROJECT_DIRECTORY.name} && {remedy}")
    if hint:
        print(f"         {hint}")
    print()


def run_optional(command, attempts=1):
    """Run a command, returning its error output instead of raising."""
    result = None
    for attempt in range(attempts):
        result = subprocess.run(
            command,
            cwd=PROJECT_DIRECTORY,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return ""
        if attempt < attempts - 1:
            time.sleep(2**attempt)
    output = f"{result.stderr}\n{result.stdout}".strip()
    return output or f"exit status {result.returncode}"


def create_lockfile():
    if os.environ.get("COOKIECUTTER_SKIP_LOCK") == "1":
        return
    remedy = "uv lock"
    if not shutil.which("uv"):
        warn("uv was not found on PATH, so uv.lock was not generated.", remedy)
        return
    error = run_optional(["uv", "lock", "--quiet"], attempts=LOCK_ATTEMPTS)
    if error:
        warn(
            f"uv lock failed, so uv.lock was not generated:\n{indent(error)}",
            remedy,
            hint=(
                "If your network blocks PyPI, set UV_DEFAULT_INDEX to an index it "
                "allows. The project pins PyPI, so ~/.config/uv/uv.toml is not enough."
            ),
        )


def initialize_git_repository():
    if (PROJECT_DIRECTORY / ".git").exists():
        return
    remedy = "git init --initial-branch=main"
    if not shutil.which("git"):
        warn("git was not found on PATH, so no repository was initialized.", remedy)
        return
    error = run_optional(["git", "init", "--quiet", "--initial-branch=main"])
    if error:
        warn(f"git init failed:\n{indent(error)}", remedy)


if __name__ == "__main__":
    apply_project_choices()
    remove_unselected_packs()
    configure_agent_adapters()
    create_lockfile()
    initialize_git_repository()
