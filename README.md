# Ruffly

### Usage

Cli tool to add common config to pyroject.toml

```commandline
cd /path/to/poetryproject ruffly init
```
or 
```commandline
ruffly init --path /path/to/poetryproject
```

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
