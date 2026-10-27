{% set is_open_source = cookiecutter.open_source_license != 'Not open source' -%}
# {{ cookiecutter.project_name }}

{{ cookiecutter.project_short_description }}

{% if is_open_source -%}
License: {{ cookiecutter.open_source_license }}.
{% endif %}

## Start

```console
uv sync --frozen
make verify
```

`make verify` is the single local and agent definition of a reviewable change.
Generation initializes this directory as a Git repository on the `main` branch.

## Agent contract

- `AGENTS.md` contains the small cross-agent project contract.
- `.codex/config.toml` configures a workspace-write sandbox.
- `CLAUDE.md` adapts the contract for Claude Code.

Agents must run verification and security checks. High-risk changes should receive independent
review.

## Repository map

```text
.
├── AGENTS.md                         project contract
├── CLAUDE.md                         link to AGENTS.md
├── .codex/                           Codex sandbox config
├── artifacts/                        fast, inspectable verification outputs
├── Makefile                          verification entry points
├── pyproject.toml                    dependencies and tool configuration
{%- if cookiecutter["deep-learning"] == 'yes' %}
├── configs/                          experiment configurations
├── examples/deep-learning/           deterministic example dataset
├── scripts/                          train, evaluate, and infer entry points
{%- endif %}
├── knowledge_base/                   running research notes
├── paper/                            LaTeX manuscript and the writing contract
├── tests/                            executable behavior checks
└── {{ "%-34s"|format(cookiecutter.project_slug ~ "/") }}reusable package code
```

## Generated options

| Option | Included |
|---|---|
| deep-learning | {{ cookiecutter["deep-learning"] }} |

{% if cookiecutter["deep-learning"] == 'yes' -%}
## Deep-learning quickstart

```console
uv run python scripts/train.py --config configs/0_baselines/00_baseline_default.yaml --light
uv run python scripts/evaluate.py --model outputs/00_baseline_default/model.pt
uv run python scripts/infer.py --model outputs/00_baseline_default/model.pt \
  --input examples/deep-learning/sample.csv
```

The commands train, evaluate, and run inference with a generic PyTorch MLP, write inspectable JSON
outputs, and are exercised end to end by `make verify`.
{% endif %}
