# Ruffly

### Usage

Cli tool to add common config to pyroject.toml.

Basic usage:
```commandline
cd/project/with/pyrojecttoml ruffly
```
will add default config to pyproject.toml found in working directory.

Additional arguments:

- ```--dst``` The path to the target pytroject.toml to modify
- ```--src``` The path to the source pytroject.toml to copy from (can be url)
- ```--only-existing``` Only copies config for tools that exist int the target pyproject.toml
- ```--tools``` A list of tools to copy config for
- ```--dry-run``` Only prints the changes that would be made

Current tools supported:
- ruff
- mypy
- pytest
- coverage
- poe (poethepoet)

### Installation

```commandline
pip install ruffly
```

### Development
To setup the development environment and run linting and testing:

```commandline
python -m venv .venv
source .venv/Scripts/activate  # or .venv/bin/activate on linux
pip install -e .[dev]
poe all
```

To test the install with pipx ```pipx install . --force```

To build the package: ```python -m build --wheel```
