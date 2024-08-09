import shutil
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import toml
from ruffly.cli import _add_config, _find_file, _get_tools, run

TEST_DIR = Path(__file__).parent

DEFAULT_TOML = """
[tool.ruff]
line-length = 120
show-fixes = true

[tool.mypy]
ignore_missing_imports = true

[tool.poe.tasks]
[tool.poe.tasks.lint]
help = "Lint"
sequence = [
    { cmd = "ruff format ." },
    { cmd = "ruff check . --fix" },
    { cmd = "mypy ." },
]
"""


@pytest.fixture
def _create_empty_toml(tmp_path):
    with open(Path(tmp_path) / "empty.toml", "w") as f:
        f.write("")


@pytest.fixture
def _create_default_toml(tmp_path):
    with open(Path(tmp_path) / "testdefault.toml", "wb") as f:
        f.write(DEFAULT_TOML.encode())


class TestFindsFile:
    def test_finds_file(self, tmp_path, mocker):
        mocker.patch("pathlib.Path.is_file").return_value = True
        sample_src_path = tmp_path / "pyproject.toml"
        sample_src_path.mkdir()
        sample_src_path.touch()

        actual = _find_file(sample_src_path.parent.as_posix())
        assert actual == sample_src_path.as_posix()

    def test_does_not_find_file(self, tmp_path):
        sample_src_path = tmp_path / "pyproject.toml"

        actual = _find_file(sample_src_path.parent.as_posix())
        assert actual is None


class TestAddConfig:
    def test_default_add(self, tmp_path, _create_empty_toml, _create_default_toml):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(tmp_path / "empty.toml", sample_dst_path)
        src_path = tmp_path / "testdefault.toml"

        _add_config(src_path.as_posix(), sample_dst_path.as_posix())

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        with open(src_path) as f:
            expected = toml.load(f)

        assert actual == expected

    def test_add_for_tools(self, tmp_path, _create_empty_toml, _create_default_toml):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(tmp_path / "empty.toml", sample_dst_path)
        src_path = tmp_path / "testdefault.toml"
        tools = ["poe"]

        _add_config(src_path.as_posix(), sample_dst_path.as_posix(), tools=tools)

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        with open(src_path) as f:
            expected = {k: v for k, v in toml.load(f)["tool"].items() if k in tools}

        assert actual["tool"] == expected


def test_get_tools(tmp_path, _create_default_toml):
    src_path = tmp_path / "testdefault.toml"
    actual = _get_tools(src_path.as_posix())
    expected = ["ruff", "mypy", "poe"]
    assert actual == expected


class TestCliRun:
    def test_cli_run_with_defaults(self, tmp_path, mocker, _create_empty_toml):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(tmp_path / "empty.toml", sample_dst_path)
        src_path = TEST_DIR.parent / "src" / "ruffly" / "default.toml"
        mocker.patch("os.getcwd").return_value = sample_dst_path.parent.as_posix()

        test_args = ("ruffly").split(" ")
        with patch.object(sys, "argv", test_args):
            run()

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        with open(src_path) as f:
            expected = toml.load(f)

        assert actual["tool"] == expected["tool"]

    def test_cli_dry_run_with_defaults(self, tmp_path, mocker, _create_empty_toml):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(tmp_path / "empty.toml", sample_dst_path)
        mocker.patch("os.getcwd").return_value = sample_dst_path.parent.as_posix()

        test_args = ("ruffly --dry-run").split(" ")
        with patch.object(sys, "argv", test_args):
            run()

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        assert actual == {}

    def test_cli_run_for_ruff(self, tmp_path, _create_empty_toml, _create_default_toml):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(tmp_path / "empty.toml", sample_dst_path)
        src_path = tmp_path / "testdefault.toml"
        tools = ["ruff"]

        test_args = (f"ruffly --src {src_path.as_posix()} --dst {sample_dst_path.as_posix()} " f"--tools ruff").split(
            " "
        )
        with patch.object(sys, "argv", test_args):
            run()

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        with open(src_path) as f:
            expected = {k: v for k, v in toml.load(f)["tool"].items() if k in tools}

        assert actual["tool"] == expected

    def test_cli_run_auto(self, tmp_path, _create_empty_toml, _create_default_toml):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(tmp_path / "empty.toml", sample_dst_path)
        with open(sample_dst_path, "w") as f:
            toml.dump({"tool": {"mypy": {}}}, f)

        src_path = tmp_path / "testdefault.toml"

        test_args = f"ruffly --src {src_path} --dst {sample_dst_path.as_posix()} --only-existing".split(" ")
        with patch.object(sys, "argv", test_args):
            run()

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        with open(src_path) as f:
            expected = {k: v for k, v in toml.load(f)["tool"].items() if k in ["mypy"]}

        assert actual["tool"] == expected

    def test_cli_run_using_url_src(self, tmp_path, mocker, _create_empty_toml, _create_default_toml):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(tmp_path / "empty.toml", sample_dst_path)
        with open(sample_dst_path, "w") as f:
            toml.dump({"tool": {"ruff": {}}}, f)

        resp_b = DEFAULT_TOML.encode()

        mocker.patch("urllib.request.urlopen").return_value.read.return_value = resp_b
        src_path = "https://someurl.com/pyproject.toml"

        test_args = f"ruffly --src {src_path} --dst {sample_dst_path.as_posix()} --tools ruff,mypy,poe".split(" ")
        with patch.object(sys, "argv", test_args):
            run()

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        assert actual["tool"] == toml.loads(resp_b.decode())["tool"]
