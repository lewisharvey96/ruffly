import argparse
import os
from pathlib import Path
from urllib import request

import toml

DEFAULT_TOML_FP = Path(__file__).parent / "default.toml"


def _find_file(directory: str) -> str | None:
    for path in Path(directory).iterdir():
        if path.is_file() and path.name == "pyproject.toml":
            return path.as_posix()
    return None


def _get_tools(src_path: str) -> list[str]:
    with open(src_path) as f:
        src_contents = toml.load(f)
    return list(src_contents["tool"].keys())


def _add_config(src_path: str, dst_path: str, tools: list[str] | None = None, dry_run: bool = False) -> None:
    if "http:" in src_path or "https:" in src_path:
        resp = request.urlopen(src_path)
        src_contents = toml.loads(resp.read().decode())
    else:
        with open(src_path) as f:
            src_contents = toml.load(f)

    extra_config = {"tool": {k: v for k, v in src_contents["tool"].items() if k in tools}} if tools else src_contents

    if dry_run:
        print(f"Would have modified {dst_path} with the following:")
        print(toml.dumps(extra_config))
    else:
        with open(dst_path) as f:
            dst_contents = toml.load(f)

        with open(dst_path, "w") as f:
            toml.dump(dst_contents | extra_config, f)
        print(f"Successfully modified {dst_path}")


def run() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Ruffly add settings to pyproject.toml")
    parser.add_argument("--dst", help="Path to target pyproject.toml")
    parser.add_argument("--src", help="Path to template pyproject.toml")
    parser.add_argument(
        "--only-existing",
        help="Add settings for tools in current pyproject.toml",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument("--tools", help="Add settings for comma separated list of tools", nargs="?", type=str)
    parser.add_argument(
        "--dry-run", help="Print changes without modifying file", action=argparse.BooleanOptionalAction, default=False
    )
    args = parser.parse_args()

    # Locate/initialize the pyproject.toml file
    file_path = args.dst if args.dst else _find_file(os.getcwd())
    if file_path:
        tools = args.tools.split(",") if args.tools else _get_tools(file_path) if args.only_existing else None
        _add_config(args.src or DEFAULT_TOML_FP.as_posix(), file_path, tools, args.dry_run)
    else:
        print(f"No pyproject.toml file found in {args.path}!")
