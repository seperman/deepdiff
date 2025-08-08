# DeepDiff v 8.6.0

![Downloads](https://img.shields.io/pypi/dm/deepdiff.svg?style=flat)
![Python Versions](https://img.shields.io/pypi/pyversions/deepdiff.svg?style=flat)
![License](https://img.shields.io/pypi/l/deepdiff.svg?version=latest)
[![Build Status](https://github.com/seperman/deepdiff/workflows/Unit%20Tests/badge.svg)](https://github.com/seperman/deepdiff/actions)
[![codecov](https://codecov.io/gh/seperman/deepdiff/branch/master/graph/badge.svg?token=KkHZ3siA3m)](https://codecov.io/gh/seperman/deepdiff)

## Modules

- [DeepDiff](https://zepworks.com/deepdiff/current/diff.html): Deep Difference of dictionaries, iterables, strings, and ANY other object.
- [DeepSearch](https://zepworks.com/deepdiff/current/dsearch.html): Search for objects within other objects.
- [DeepHash](https://zepworks.com/deepdiff/current/deephash.html): Hash any object based on their content.
- [Delta](https://zepworks.com/deepdiff/current/delta.html): Store the difference of objects and apply them to other objects.
- [Extract](https://zepworks.com/deepdiff/current/extract.html): Extract an item from a nested Python object using its path.
- [commandline](https://zepworks.com/deepdiff/current/commandline.html): Use DeepDiff from commandline.

Tested on Python 3.9+ and PyPy3.

- **[Documentation](https://zepworks.com/deepdiff/8.6.0/)**

## What is new?

Please check the [ChangeLog](CHANGELOG.md) file for the detailed information.

DeepDiff 8-6-0

- Added Colored View thanks to @mauvilsa 
- Added support for applying deltas to NamedTuple thanks to @paulsc 
- Fixed test_delta.py with Python 3.14 thanks to @Romain-Geissler-1A
- Added python property serialization to json
- Added ip address serialization
- Switched to UV from pip
- Added Claude.md
- Added uuid hashing thanks to @akshat62
- Added `ignore_uuid_types` flag to DeepDiff to avoid type reports when comparing UUID and string.
- Added comprehensive type hints across the codebase (multiple commits for better type safety)
- Added support for memoryview serialization
- Added support for bytes serialization (non-UTF8 compatible)
- Fixed bug where group_by with numbers would leak type info into group path reports
- Fixed bug in `_get_clean_to_keys_mapping without` explicit significant digits
- Added support for python dict key serialization
- Enhanced support for IP address serialization with safe module imports
- Added development tooling improvements (pyright config, .envrc example)
- Updated documentation and development instructions


DeepDiff 8-5-0

- Updating deprecated pydantic calls
- Switching to pyproject.toml
- Fix for moving nested tables when using iterable_compare_func.  by 
- Fix recursion depth limit when hashing numpy.datetime64
- Moving from legacy setuptools use to pyproject.toml


DeepDiff 8-4-2

- fixes the type hints for the base
- fixes summarize so if json dumps fails, we can still get a repr of the results
- adds ipaddress support


## Installation

### Install from PyPi:

`pip install deepdiff`

If you want to use DeepDiff from commandline:

`pip install "deepdiff[cli]"`

If you want to improve the performance of DeepDiff with certain functionalities such as improved json serialization:

`pip install "deepdiff[optimize]"`

Install optional packages:
- [yaml](https://pypi.org/project/PyYAML/)
- [tomli](https://pypi.org/project/tomli/) (python 3.10 and older) and [tomli-w](https://pypi.org/project/tomli-w/) for writing
- [clevercsv](https://pypi.org/project/clevercsv/) for more rubust CSV parsing
- [orjson](https://pypi.org/project/orjson/) for speed and memory optimized parsing
- [pydantic](https://pypi.org/project/pydantic/)


# Documentation

<https://zepworks.com/deepdiff/current/>

### A message from Sep, the creator of DeepDiff

> 👋 Hi there,
>
> Thank you for using DeepDiff!
> As an engineer, I understand the frustration of wrestling with **unruly data** in pipelines.
> That's why I developed a new tool - [Qluster](https://qluster.ai/solution) to empower non-engineers to control and resolve data issues at scale autonomously and **stop bugging the engineers**! 🛠️
>
> If you are going through this pain now, I would love to give you [early access](https://www.qluster.ai/try-qluster) to Qluster and get your feedback.


# ChangeLog

Please take a look at the [CHANGELOG](CHANGELOG.md) file.

# Survey

:mega: **Please fill out our [fast 5-question survey](https://forms.gle/E6qXexcgjoKnSzjB8)** so that we can learn how & why you use DeepDiff, and what improvements we should make. Thank you! :dancers:

# Local dev

1. Clone the repo
2. Switch to the dev branch
3. Create your own branch
4. Install dependencies

    - Method 1: Use [`uv`](https://github.com/astral-sh/uv) to install the dependencies:  `uv sync --all-extras`.
    - Method 2: Use pip: `pip install -e ".[cli,coverage,dev,docs,static,test]"`
5. Build `flit build`

# Contribute

1. Please make your PR against the dev branch
2. Please make sure that your PR has tests. Since DeepDiff is used in many sensitive data driven projects, we strive to maintain around 100% test coverage on the code.

Please run `pytest --cov=deepdiff --runslow` to see the coverage report. Note that the `--runslow` flag will run some slow tests too. In most cases you only want to run the fast tests which so you wont add the `--runslow` flag.

Or to see a more user friendly version, please run: `pytest --cov=deepdiff --cov-report term-missing --runslow`.

Thank you!

# Authors

Please take a look at the [AUTHORS](AUTHORS.md) file.
