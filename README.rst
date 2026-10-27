=======================
Python project template
=======================

Cookiecutter template for small Python repositories with a minimal frontier-agent contract
and one executable quality gate.

Every generated project supports Codex and Claude Code out of the box. It ships no CI
workflows, bundled skills, generic reasoning skills, or specialist-agent profiles.

What you get
------------

Every project includes:

* ``AGENTS.md`` with the agent contract; ``CLAUDE.md`` links to it
* ``.codex/config.toml``, which configures a workspace-write sandbox
* ``paper/``: a LaTeX manuscript with a writing contract and an arXiv packager. It uses a
  modified ``cup-journal`` class with the Microsoft AI for Good Research Lab title page; swap
  the logo in ``paper/figures/`` and the class's title block for your own
* ``knowledge_base/``: running research notes

One pack is optional and off by default:

* ``deep-learning``: a generic PyTorch train/evaluate/infer path

Generate a project
------------------

Install `uv`_, then run::

    uvx cookiecutter https://github.com/Akramz/template.git
    cd <project_slug>
    uv sync --frozen
    make verify

Generation initializes a local Git repository on the ``main`` branch and writes ``uv.lock``.
``make verify`` is the shared local and agent handoff contract. It runs formatting and lint
checks, type checking, behavior tests, source scanning, and a hash-pinned dependency audit.

Generation never fails because of a network problem or a missing tool. If ``uv lock`` or
``git init`` cannot run, the project is still written and the hook prints the command to run by
hand.

Generated projects pin PyPI, so ``uv.lock`` holds canonical URLs on any machine. If your
network blocks public PyPI, set ``UV_DEFAULT_INDEX`` to an index it allows when you generate
and sync::

    export UV_DEFAULT_INDEX=https://example.internal/pypi/simple

Develop this template
---------------------

::

    uv sync --frozen
    make verify
    make test-all   # also locks and syncs a baked project against a package index

The suite bakes each pack choice, checks the generated project layout, drives the real
``cookiecutter`` CLI, and injects tool failures to prove generation never destroys a project.
``make verify`` runs offline in under 30 seconds.

To see the paper as a PDF (needs ``latexmk`` and ``biber``), run::

    make paper

which bakes a project and builds ``python_boilerplate/paper/main.pdf``. The skeleton under
``{{cookiecutter.project_slug}}/`` is Cookiecutter source, not a working project: its
``main.tex`` opens with a Jinja macro, so ``latexmk`` on that file fails with
``Loading a class or package in a group``. Bake first, then build.

.. _uv: https://docs.astral.sh/uv/
