import importlib


def test_package_imports_and_declares_version() -> None:
    package = importlib.import_module("{{ cookiecutter.project_slug }}")
    version = getattr(package, "__version__", "")
    assert version.count(".") == 2
{% if 'no' not in cookiecutter.command_line_interface|lower %}

def test_cli_runs() -> None:
    cli = importlib.import_module("{{ cookiecutter.project_slug }}.cli")
{%- if cookiecutter.command_line_interface|lower == 'click' %}
    assert cli.main.main([], standalone_mode=False) == 0
{%- else %}
    assert cli.main([]) == 0
{%- endif %}
{%- endif %}
