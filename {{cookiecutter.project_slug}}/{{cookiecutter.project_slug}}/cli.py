"""Console script for {{ cookiecutter.project_slug }}."""
{% if cookiecutter.command_line_interface|lower == 'click' %}
import sys

import click


@click.command()
def main(args=None):
    """Console script for {{ cookiecutter.project_slug }}."""
    click.echo("{{ cookiecutter.project_slug }} is ready")
    return 0
{% else %}
import argparse
import sys


def main(argv=None):
    """Console script for {{ cookiecutter.project_slug }}."""
    ## Everything here stays on one short line on purpose: cookiecutter renders the
    ## project slug in, and `ruff format --check` runs in the gate — a line that is
    ## under 88 for a short slug and over it for a long one would fail on generation.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    print("{{ cookiecutter.project_slug }} is ready")
    return 0
{% endif %}

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
