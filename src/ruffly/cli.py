import argparse
import os
from pathlib import Path

import toml


def _find_file(directory: str) -> str | None:
    for path in Path(directory).iterdir():
        if path.is_file() and path.name == "pyproject.toml":
            return path.as_posix()
    return None


def _get_tools(src_path: str) -> list[str]:
    with open(src_path) as f:
        src_contents = toml.load(f)
    return list(src_contents["tool"].keys())


def _add_config(src_path: str, dst_path: str, tools: list[str] | None = None) -> None:
    with open(src_path) as f:
        src_contents = toml.load(f)

    with open(dst_path) as f:
        dst_contents = toml.load(f)

    extra_config = {"tool": {k: v for k, v in src_contents["tool"].items() if k in tools}} if tools else src_contents

    with open(dst_path, "w") as f:
        toml.dump(dst_contents | extra_config, f)


def run() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Ruffly add settings to pyproject.toml")
    parser.add_argument("command", help="Command to run", choices=["init"])
    parser.add_argument("--dst-dir", help="Path to directory of target pyproject.toml", default=os.getcwd())
    parser.add_argument("--src-path", help="Path to template pyproject.toml")
    parser.add_argument(
        "--auto",
        help="Add settings for tools in current pyproject.toml",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument("--tools", help="Add settings for comma seperated list of tools", nargs="?", type=str)
    args = parser.parse_args()

    # Locate/initialize the pyproject.toml file
    file_path = _find_file(args.dst_dir)
    if file_path:
        _add_config(
            args.src_path or "default.toml", file_path, args.tools.split(",") if args.tools else _get_tools(file_path)
        )
        print(f"Successfully modified {file_path}")
    else:
        print(f"No pyproject.toml file found in {args.path}!")
