import argparse
import os

import toml
from ruffly.utils import CONFIG_DICT


def find_file(directory: str) -> str | None:
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename == "pyproject.toml":
                return os.path.join(dirpath, filename)
    return None


def add_config(file_path: str) -> None:
    with open(file_path) as f:
        contents = toml.load(f)

    with open(file_path, "w") as f:
        toml.dump(contents | CONFIG_DICT, f)


def main() -> None:
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Set up ruffly project")
    parser.add_argument("command", help="Command to run", choices=["init"])
    parser.add_argument("--path", help="Path to directory", default=os.getcwd())
    args = parser.parse_args()

    # Locate/initialize the pyproject.toml file
    file_path = find_file(args.path)
    if file_path:
        add_config(file_path)
        print(f"Successfully modified {file_path}")
    else:
        print(f"No pyproject.toml file found in {args.path} -- please run 'poetry init' first")
