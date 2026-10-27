"""Layout and behavior of a generated project."""

import re
import shutil
import subprocess
import tomllib
from contextlib import contextmanager

import pytest
from cookiecutter.utils import rmtree
from support import TEMPLATE_ROOT

PACK_SENTINELS = {
    "deep-learning": [
        "configs/0_baselines/00_baseline_default.yaml",
        "examples/deep-learning/sample.csv",
        "scripts/infer.py",
        "tests/test_deep_learning_pipeline.py",
        "python_boilerplate/deep_learning.py",
    ],
}

# Shipped in every project: agent support, the paper and the research notes.
ALWAYS_PRESENT = [
    "AGENTS.md",
    "CLAUDE.md",
    ".codex/config.toml",
    "knowledge_base/notes.md",
    "paper/main.tex",
    "paper/cup-journal.cls",
    "paper/figures/ai4g_light.pdf",
]

# No GitHub plane: no CI, no Copilot adapter, no repository templates. No
# harness-enforced checks and no subagent profiles: the contract in AGENTS.md
# is the only handoff gate. Skills and memory settings are the user's own, so
# projects ship no .claude directory at all.
NEVER_PRESENT = [
    ".github",
    ".agent",
    ".claude",
    ".agents",
    ".codex/skills",
    "deck",
    "paper/writing_example",
]


@contextmanager
def baked(cookies, **extra_context):
    result = cookies.bake(extra_context=extra_context or None)
    try:
        assert result.exit_code == 0, result.exception
        assert result.project_path
        yield result.project_path
    finally:
        if result.project_path:
            rmtree(str(result.project_path))


@pytest.mark.parametrize("selected_pack", PACK_SENTINELS)
def test_pack_matrix_prunes_unselected_assets(cookies, selected_pack):
    context = {pack: "no" for pack in PACK_SENTINELS}
    context[selected_pack] = "yes"
    with baked(cookies, **context) as project:
        for pack, paths in PACK_SENTINELS.items():
            for relative_path in paths:
                assert (project / relative_path).exists() is (pack == selected_pack)

        pyproject = tomllib.loads((project / "pyproject.toml").read_text())
        dependencies = pyproject["project"]["dependencies"]
        has_torch = any(item.startswith("torch") for item in dependencies)
        assert has_torch is (selected_pack == "deep-learning")
        indexes = pyproject["tool"]["uv"]["index"]
        assert indexes == [
            {"name": "pypi", "url": "https://pypi.org/simple", "default": True}
        ]


def test_default_profile_is_minimal(cookies):
    with baked(cookies) as project:
        for paths in PACK_SENTINELS.values():
            for path in paths:
                assert not (project / path).exists()

        assert not (project / ".codex/skills").exists()
        assert not (project / "examples").exists()
        assert len((project / "AGENTS.md").read_text().splitlines()) <= 18


def test_agent_support_is_always_generated(cookies):
    with baked(cookies) as project:
        for path in ALWAYS_PRESENT:
            assert (project / path).exists(), path
        for path in NEVER_PRESENT:
            assert not (project / path).exists(), path

        assert (project / "CLAUDE.md").is_symlink()
        assert (project / "CLAUDE.md").read_text() == (
            project / "AGENTS.md"
        ).read_text()


def test_no_github_plane_is_generated(cookies):
    with baked(cookies, **{pack: "yes" for pack in PACK_SENTINELS}) as project:
        assert not (project / ".github").exists()

        tracked = [
            path
            for path in project.rglob("*")
            if ".git" not in path.parts and not path.is_dir()
        ]
        mentions = [
            str(path.relative_to(project))
            for path in tracked
            if path.suffix not in {".pt", ".csv"}
            and ".github" in path.read_text(errors="ignore")
        ]
        assert mentions == []


def biber_works():
    if not shutil.which("biber"):
        return False
    return subprocess.run(["biber", "--version"], capture_output=True).returncode == 0


def test_paper_escapes_latex_specials_and_compiles(cookies):
    # main.tex is rendered, not copied, so an unescaped name reaches LaTeX verbatim.
    # `field_maps` is the reference project name and its underscore is a subscript.
    context = {
        "project_name": "field_maps",
        "full_name": "A&B 100% #1_Lab",
        "affiliation": "R&D Lab_1",
    }
    with baked(cookies, **context) as project:
        paper = project / "paper"
        body = (paper / "main.tex").read_text()
        assert r"\title{ field\_maps }" in body
        assert r"A\&B 100\% \#1\_Lab" in body
        assert r"\affiliation{ R\&D Lab\_1 }" in body
        # The class file is copied verbatim; rendering it would eat its `{%` groups.
        assert (
            r"\newcommand*\cup@keyval@bool[2]{%"
            in (paper / "cup-journal.cls").read_text()
        )

        if shutil.which("latexmk") and biber_works():
            subprocess.run(
                [
                    "latexmk",
                    "-pdf",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    "main.tex",
                ],
                cwd=paper,
                check=True,
                capture_output=True,
            )
            assert (paper / "main.pdf").is_file()


def test_makefile_targets_match_the_generated_layout(cookies):
    with baked(cookies) as project:
        makefile = (project / "Makefile").read_text()
        assert "bootstrap-github" not in makefile

        output = subprocess.run(
            ["make", "help"],
            cwd=project,
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        assert {"verify", "security", "typecheck", "test"} <= set(
            line.split()[0] for line in output.splitlines() if line.strip()
        )


def test_generated_python_compiles(cookies):
    with baked(cookies, **{pack: "yes" for pack in PACK_SENTINELS}) as project:
        sources = [
            path
            for path in project.rglob("*.py")
            if ".venv" not in path.parts and "paper" not in path.parts
        ]
        assert sources
        for path in sources:
            compile(path.read_text(), str(path.relative_to(project)), "exec")


def repository_map_paths(readme):
    block = readme.split("## Repository map", 1)[1].split("```text")[1].split("```")[0]
    paths = []
    for line in block.splitlines():
        entry = re.sub(r"^[│├└─\s]*", "", line)
        if not entry or entry == ".":
            continue
        paths.append(entry.split()[0])
    return paths


@pytest.mark.parametrize("selected_pack", [None, *PACK_SENTINELS])
def test_repository_map_matches_the_generated_tree(cookies, selected_pack):
    context = {
        pack: "yes" if pack == selected_pack else "no" for pack in PACK_SENTINELS
    }
    with baked(cookies, **context) as project:
        mapped = repository_map_paths((project / "README.md").read_text())
        assert len(mapped) >= 8
        for relative_path in mapped:
            assert (project / relative_path).exists(), relative_path


JUNK_NAMES = {".DS_Store", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv"}
# Build output, never source. LaTeX detritus once shipped in every generated paper.
JUNK_SUFFIXES = {
    ".pyc",
    ".orig",
    ".rej",
    ".pdf",
    ".aux",
    ".bbl",
    ".blg",
    ".fls",
    ".log",
    ".out",
    ".fdb_latexmk",
    ".gz",
}
# The one PDF that is source: the lab logo the paper class puts on the title page.
SOURCE_FILES = {"paper/figures/ai4g_light.pdf"}


def test_no_local_junk_leaks_into_the_generated_project(cookies):
    with baked(cookies, **{pack: "yes" for pack in PACK_SENTINELS}) as project:
        leaked = [
            str(path.relative_to(project))
            for path in project.rglob("*")
            if ".git" not in path.parts
            and (path.name in JUNK_NAMES or path.suffix in JUNK_SUFFIXES)
            and str(path.relative_to(project)) not in SOURCE_FILES
        ]
        assert leaked == []
        assert ".DS_Store" in (project / ".gitignore").read_text()


def test_the_skeleton_carries_no_git_ignored_files(cookies):
    # Cookiecutter copies the working tree, not the index. Anything ignored but present
    # in the skeleton ships to whoever bakes locally and vanishes for whoever bakes from
    # a clone, and plain `git status` never shows the divergence.
    skeleton = TEMPLATE_ROOT / "{{cookiecutter.project_slug}}"
    status = subprocess.run(
        ["git", "status", "--porcelain", "--ignored", "--", str(skeleton)],
        cwd=TEMPLATE_ROOT,
        text=True,
        capture_output=True,
        check=True,
    ).stdout
    ignored = [line[3:] for line in status.splitlines() if line.startswith("!!")]
    assert ignored == []


def test_generation_initializes_a_git_repository_on_main(cookies):
    with baked(cookies) as project:
        inside_work_tree = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=project,
            text=True,
            capture_output=True,
            check=True,
        )
        assert inside_work_tree.stdout.strip() == "true"
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=project,
            text=True,
            capture_output=True,
            check=True,
        )
        assert branch.stdout.strip() == "main"
