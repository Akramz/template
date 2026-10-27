# Artifacts

An **artifact** is the smallest tangible output that shows the code does what it claims:
an image, a CSV, a plot, a JSON summary. Something you open and judge by eye.

Artifacts complement the test suite, they do not replace it. Tests assert behavior and
catch regressions; artifacts show a human whether the result is any good. `make verify`
gates on tests.

## Usage

Add one script per artifact and run it directly:

```console
uv run python artifacts/<name>.py
```

## Guidelines

1. Scripts should run in under 30 seconds. Add a `--light` flag when the full run is slower.
2. Write output to `artifacts/output/`, which is git-ignored.
3. Name outputs so it is obvious what claim they support.
