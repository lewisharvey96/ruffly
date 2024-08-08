CONFIG_DICT = {
    "tool": {
        "poetry": {
            "group": {
                "dev": {
                    "dependencies": {
                        "ruff": ">=0.0.286",
                        "mypy": ">=0.991",
                        "poethepoet": ">=0.18.1",
                        "pytest": ">=7.2.1",
                        "coverage": ">=7.3.2",
                        "pytest-random-order": ">=1.1.0",
                        "python-dotenv": ">=1.0.1",
                        "tenvplate": ">=0.0.2"
                    }
                }
            }
        },
        "ruff": {
            "line-length": 120,
            "target-version": "py311",
            "show-fixes": True,
            "exclude": [".venv", "__ignore__", "notebooks", "scripts"],
            "lint": {
                "select": ["A", "E", "F", "UP", "I", "W", "SIM", "RUF", "C901"],
                "ignore": ["A002", "A003", "RUF012"]
            }
        },
        "mypy": {
            "plugins": ["pydantic.mypy"],
            "python_version": "3.11",
            "ignore_missing_imports": True,
            "disallow_untyped_defs": True,
            "exclude": "tests|notebooks|__ignore__|.ipynb_checkpoints|scripts"
        },
        "pytest": {
            "ini_options": {
                "addopts": "--random-order-seed=424242",
                "filterwarnings": ["error", "ignore:Passing unrecognized arguments:DeprecationWarning"]
            }
        },
        "coverage": {
            "run": {
                "include": ["src/*"]
            },
            "report": {
                "exclude_also": ["raise AssertionError", "raise NotImplementedError", "@(abc\\.)?abstractmethod"]
            }
        },
        "poe": {
            "tasks": {
                "lint": {
                    "help": "Lint",
                    "sequence": [
                        {"cmd": "poetry run ruff format ."},
                        {"cmd": "poetry run ruff check . --fix"},
                        {"cmd": "poetry run python -m mypy ."}
                    ]
                },
                "tests": {
                    "help": "Runs all tests",
                    "sequence": [
                        {"cmd": "poetry run coverage run -m pytest ./tests"},
                        {"cmd": "poetry run coverage report -m"}
                    ]
                },
                "all": {
                    "help": "Run all required pre-push commands",
                    "sequence": [
                        {"ref": "lint"},
                        {"ref": "tests"},
                        {"shell": "echo \"\nAll Good! :)\""}
                    ]
                }
            }
        }
    }
}