# Package modules

- `__init__.py` exposes the package version.
{%- if 'no' not in cookiecutter.command_line_interface|lower %}
- `cli.py` provides the selected command-line interface.
{%- endif %}
{%- if cookiecutter["deep-learning"] == 'yes' %}
- `config.py` validates the baseline experiment configuration.
- `deep_learning.py` implements deterministic PyTorch training, evaluation, and inference.

Extend the model behind these functions, keep configuration validation explicit, and add
behavior tests through the real scripts.
{%- endif %}
