# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DeepDiff is a Python library for deep comparison, searching, and hashing of Python objects. It provides:
- **DeepDiff**: Deep difference detection between objects
- **DeepSearch**: Search for objects within other objects  
- **DeepHash**: Content-based hashing for any object
- **Delta**: Git-like diff objects that can be applied to other objects
- **CLI**: Command-line interface via `deep` command

## Development Commands

### Setup
```bash
# Install with all development dependencies
uv pip install -e ".[cli,coverage,dev,docs,static,test]"
# OR using uv (recommended)
uv sync --all-extras
```

**Virtual Environment**: Activate with `source ~/.venvs/atlas/bin/activate` before running tests or Python commands


### Testing
```bash
# Run tests with coverage
pytest --cov=deepdiff --cov-report term-missing

# Run tests including slow ones
pytest --cov=deepdiff --runslow

# Run single test file
pytest tests/test_diff_text.py

# Run tests across multiple Python versions
nox -s pytest
```

### Quality Checks
```bash
# Linting (max line length: 120)
nox -s flake8

# Type checking
nox -s mypy

# Run all quality checks
nox
```

## Architecture

### Core Structure
- **deepdiff/diff.py**: Main DeepDiff implementation (most complex component)
- **deepdiff/deephash.py**: DeepHash functionality
- **deepdiff/base.py**: Shared base classes and functionality
- **deepdiff/model.py**: Core data structures and result objects
- **deepdiff/helper.py**: Utility functions and type definitions
- **deepdiff/delta.py**: Delta objects for applying changes

### Key Patterns
- **Inheritance**: `Base` class provides common functionality with mixins
- **Result Objects**: Different result formats (`ResultDict`, `TreeResult`, `TextResult`)
- **Path Navigation**: Consistent path notation for nested object access
- **Performance**: LRU caching and numpy array optimization

### Testing
- Located in `/tests/` directory
- Organized by functionality (e.g., `test_diff_text.py`, `test_hash.py`)
- Aims for ~100% test coverage
- Uses pytest with comprehensive fixtures

## Development Notes

- **Python Support**: 3.9+ and PyPy3
- **Main Branch**: `master` (PRs typically go to `dev` branch)
- **Build System**: Modern `pyproject.toml` with `flit_core`
- **Dependencies**: Core dependency is `orderly-set>=5.4.1,<6`
- **CLI Tool**: Available as `deep` command after installation with `[cli]` extra
