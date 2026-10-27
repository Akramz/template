import datetime
import importlib
import os
import shlex
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path

from click.testing import CliRunner
from cookiecutter.utils import rmtree


@contextmanager
def inside_dir(dirpath):
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def bake_in_temp_dir(cookies, *args, **kwargs):
    result = cookies.bake(*args, **kwargs)
    try:
        yield result
    finally:
        if result.project_path:
            rmtree(str(result.project_path))


def run_inside_dir(command, dirpath):
    with inside_dir(dirpath):
        return subprocess.check_call(shlex.split(command))


def check_output_inside_dir(command, dirpath):
    with inside_dir(dirpath):
        return subprocess.check_output(shlex.split(command))


def test_year_compute_in_license_file(cookies):
    with bake_in_temp_dir(cookies) as result:
        license_file_path = result.project_path / "LICENSE"
        now = datetime.datetime.now()
        assert str(now.year) in license_file_path.read_text()


def project_info(result):
    project_path = Path(result.project_path)
    project_slug = project_path.name
    project_dir = project_path / project_slug
    return project_path, project_slug, project_dir


def test_bake_with_defaults(cookies):
    with bake_in_temp_dir(cookies) as result:
        assert result.project_path.is_dir()
        assert result.exit_code == 0
        assert result.exception is None

        found_toplevel_files = {path.name for path in result.project_path.iterdir()}
        assert "pyproject.toml" in found_toplevel_files
        assert "python_boilerplate" in found_toplevel_files
        assert "artifacts" in found_toplevel_files


def test_bake_withspecialchars(cookies):
    with bake_in_temp_dir(
        cookies,
        extra_context={"full_name": 'name "quote" name'},
    ) as result:
        assert result.project_path.is_dir()


def test_bake_with_apostrophe(cookies):
    with bake_in_temp_dir(cookies, extra_context={"full_name": "O'connor"}) as result:
        assert result.project_path.is_dir()


def test_make_help(cookies):
    with bake_in_temp_dir(cookies) as result:
        if sys.platform != "win32":
            output = check_output_inside_dir(
                "make help",
                str(result.project_path),
            )
            assert b"verify" in output


def test_bake_selecting_license(cookies):
    license_strings = {
        "MIT license": ("MIT ", 'license = "MIT"'),
        "BSD license": (
            "Redistributions of source code must retain the "
            "above copyright notice, this",
            'license = "BSD-3-Clause"',
        ),
        "ISC license": ("ISC License", 'license = "ISC"'),
        "Apache Software License 2.0": (
            "Licensed under the Apache License, Version 2.0",
            'license = "Apache-2.0"',
        ),
        "GNU General Public License v3": (
            "GNU GENERAL PUBLIC LICENSE",
            'license = "GPL-3.0-only"',
        ),
    }
    for license_name, (license_text, metadata) in license_strings.items():
        with bake_in_temp_dir(
            cookies, extra_context={"open_source_license": license_name}
        ) as result:
            assert license_text in (result.project_path / "LICENSE").read_text()
            assert metadata in (result.project_path / "pyproject.toml").read_text()


def test_bake_not_open_source(cookies):
    with bake_in_temp_dir(
        cookies, extra_context={"open_source_license": "Not open source"}
    ) as result:
        found_toplevel_files = {path.name for path in result.project_path.iterdir()}
        assert "pyproject.toml" in found_toplevel_files
        assert "LICENSE" not in found_toplevel_files
        assert "License" not in (result.project_path / "README.md").read_text()


def test_bake_with_no_console_script(cookies):
    context = {"command_line_interface": "No command-line interface"}
    with bake_in_temp_dir(cookies, extra_context=context) as result:
        project_path, _, project_dir = project_info(result)
        assert "cli.py" not in os.listdir(project_dir)
        assert "[project.scripts]" not in (project_path / "pyproject.toml").read_text()


def test_bake_with_console_script_files(cookies):
    context = {"command_line_interface": "Click"}
    with bake_in_temp_dir(cookies, extra_context=context) as result:
        project_path, _, project_dir = project_info(result)
        assert "cli.py" in os.listdir(project_dir)
        assert "[project.scripts]" in (project_path / "pyproject.toml").read_text()


def test_bake_with_argparse_console_script_files(cookies):
    context = {"command_line_interface": "Argparse"}
    with bake_in_temp_dir(cookies, extra_context=context) as result:
        project_path, _, project_dir = project_info(result)
        assert "cli.py" in os.listdir(project_dir)
        assert "[project.scripts]" in (project_path / "pyproject.toml").read_text()


def test_bake_with_console_script_cli(cookies):
    context = {"command_line_interface": "Click"}
    with bake_in_temp_dir(cookies, extra_context=context) as result:
        _, project_slug, project_dir = project_info(result)
        module_path = project_dir / "cli.py"
        spec = importlib.util.spec_from_file_location(
            f"{project_slug}.cli", module_path
        )
        assert spec and spec.loader
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        runner = CliRunner()
        noarg_result = runner.invoke(cli.main)
        assert noarg_result.exit_code == 0
        assert f"{project_slug} is ready" in noarg_result.output
        help_result = runner.invoke(cli.main, ["--help"])
        assert help_result.exit_code == 0
        assert "Show this message" in help_result.output


def test_bake_with_argparse_console_script_cli(cookies):
    context = {"command_line_interface": "Argparse"}
    with bake_in_temp_dir(cookies, extra_context=context) as result:
        _, project_slug, project_dir = project_info(result)
        module_path = project_dir / "cli.py"
        spec = importlib.util.spec_from_file_location(
            f"{project_slug}.cli", module_path
        )
        assert spec and spec.loader
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        noarg_result = cli.main([])
        assert noarg_result == 0


def test_artifacts_directory_exists(cookies):
    with bake_in_temp_dir(cookies) as result:
        assert result.project_path.is_dir()
        artifacts_dir = result.project_path / "artifacts"
        assert artifacts_dir.is_dir()
        assert (artifacts_dir / "README.md").exists()
