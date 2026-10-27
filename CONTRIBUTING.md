# Contributing

Bug reports and pull requests are welcome. Open an issue first for larger changes.

To work on the template:

```console
uv sync --frozen
make verify     # lint and the fast tests, under 30 seconds
make test-all   # also locks and syncs a baked project against a package index
```

The tests bake real projects, drive the `cookiecutter` CLI, and break `uv` and `git` on purpose
to prove generation never loses a project. Add a test for each behavior you change.

Keep changes small and generated projects minimal: a new file in the skeleton ships to every
user, so it has to earn its place.
