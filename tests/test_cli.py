import shutil
import sys
from pathlib import Path
from unittest.mock import patch

import toml
from ruffly.cli import _add_config, _find_file, _get_tools, run

TEST_DIR = Path(__file__).parent


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
    def test_default_add(self, tmp_path):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(TEST_DIR / "empty.toml", sample_dst_path)
        src_path = TEST_DIR / "testdefault.toml"

        _add_config(src_path.as_posix(), sample_dst_path.as_posix())

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        with open(src_path) as f:
            expected = toml.load(f)

        assert actual == expected

    def test_add_for_tools(self, tmp_path):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(TEST_DIR / "empty.toml", sample_dst_path)
        src_path = TEST_DIR / "testdefault.toml"
        tools = ["ruff"]

        _add_config(src_path.as_posix(), sample_dst_path.as_posix(), tools=tools)

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        with open(src_path) as f:
            expected = {k: v for k, v in toml.load(f)["tool"].items() if k in tools}

        assert actual["tool"] == expected


def test_get_tools():
    src_path = TEST_DIR / "testdefault.toml"
    actual = _get_tools(src_path.as_posix())
    expected = ["ruff", "mypy"]
    assert actual == expected


class TestCliRun:
    def test_cli_run_for_ruff(self, tmp_path):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(TEST_DIR / "empty.toml", sample_dst_path)
        src_path = TEST_DIR / "testdefault.toml"
        tools = ["ruff"]

        test_args = (
            f"ruffly init --src-path {src_path.as_posix()} --dst-dir {sample_dst_path.parent.as_posix()} "
            f"--tools ruff"
        ).split(" ")
        with patch.object(sys, "argv", test_args):
            run()

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        with open(src_path) as f:
            expected = {k: v for k, v in toml.load(f)["tool"].items() if k in tools}

        assert actual["tool"] == expected

    def test_cli_run_auto(self, tmp_path):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(TEST_DIR / "empty.toml", sample_dst_path)
        with open(sample_dst_path, "w") as f:
            toml.dump({"tool": {"mypy": {}}}, f)

        src_path = TEST_DIR / "testdefault.toml"

        test_args = (
            f"ruffly init --src-path {src_path} --dst-dir {sample_dst_path.parent.as_posix()} --auto".split(
                " "
            )
        )
        with patch.object(sys, "argv", test_args):
            run()

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        with open(src_path) as f:
            expected = {k: v for k, v in toml.load(f)["tool"].items() if k in ["mypy"]}

        assert actual["tool"] == expected

    def test_cli_run_using_url_src(self, tmp_path):
        sample_dst_path = tmp_path / "pyproject.toml"
        shutil.copyfile(TEST_DIR / "empty.toml", sample_dst_path)
        with open(sample_dst_path, "w") as f:
            toml.dump({"tool": {"mypy": {}}}, f)

        src_path = "https://github.com/lewisharvey96/ruffly/blob/main/tests/testdefault.toml"

        test_args = (
            f"ruffly init --src-path {src_path.as_posix()} --dst-dir {sample_dst_path.parent.as_posix()} --auto".split(
                " "
            )
        )
        with patch.object(sys, "argv", test_args):
            run()

        with open(sample_dst_path) as f:
            actual = toml.load(f)

        with open(src_path) as f:
            expected = {k: v for k, v in toml.load(f)["tool"].items() if k in ["mypy"]}

        assert actual["tool"] == expected