# Tests

`test_smoke.py` checks package imports and the selected CLI.
{%- if cookiecutter["deep-learning"] == 'yes' %}
`test_deep_learning_pipeline.py` executes the real light-mode train/evaluate/infer command
path and asserts its checkpoint, metrics, and predictions.
{%- endif %}

Use `uv run pytest path/to/test.py -k pattern` while iterating and `make verify` before
handoff. Tests must assert observable behavior, reproduce fixed regressions, remain
deterministic, and write only to pytest-provided temporary directories.

Write end-to-end tests on small real inputs, differential tests (old and new code on the same
inputs) for rewrites, and property tests (Hypothesis) for clear invariants. No unit tests.
