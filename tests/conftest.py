import os
import shutil

import pytest


@pytest.fixture(autouse=True)
def skip_lock_by_default(monkeypatch):
    """Keep the suite offline and fast; lock behavior has its own tests."""
    monkeypatch.setenv("COOKIECUTTER_SKIP_LOCK", "1")


@pytest.fixture
def stub_path(tmp_path_factory, monkeypatch):
    """Replace PATH with a directory holding chosen real tools and shell stubs."""
    bin_dir = tmp_path_factory.mktemp("stub-bin")
    original_path = os.environ.get("PATH", "")

    def configure(stubs=None, available=("git",)):
        for name in available:
            resolved = shutil.which(name, path=original_path)
            assert resolved, f"{name} must be installed to run this test"
            link = bin_dir / name
            if not link.exists():
                link.symlink_to(resolved)
        for name, body in (stubs or {}).items():
            stub = bin_dir / name
            if stub.exists() or stub.is_symlink():
                stub.unlink()
            stub.write_text(f"#!/bin/sh\n{body}\n")
            stub.chmod(0o755)
        monkeypatch.setenv("PATH", str(bin_dir))
        return bin_dir

    return configure
