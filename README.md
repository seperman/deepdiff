# DeepDiff v 6.4.0

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

Tested on Python 3.7+ and PyPy3.

- **[Documentation](https://zepworks.com/deepdiff/6.4.0/)**

## What is new?

Please check the [ChangeLog](CHANGELOG.md) file for the detailed information.

DeepDiff 6-3-1

This release includes many bug fixes.

- Bugfix deephash for paths by [maggelus](https://github.com/maggelus)
- Bugfix deephash compiled regex [maggelus](https://github.com/maggelus)
- Fix tests dependent on toml by [martin-kokos](https://github.com/martin-kokos)
- Bugfix for `include_paths` for nested dictionaries by [kor4ik](https://github.com/kor4ik)
- Use tomli and tomli-w for dealing with tomli files by [martin-kokos](https://github.com/martin-kokos)
- Bugfix for `datetime.date` by [Alex Sauer-Budge](https://github.com/amsb)


DeepDiff 6-3-0

- [`PrefixOrSuffixOperator`](https://zepworks.com/deepdiff/current/custom.html#prefix-or-suffix-operator-label): This operator will skip strings that are suffix or prefix of each other.
- [`include_obj_callback`](https://zepworks.com/deepdiff/current/ignore_types_or_values.html#include-obj-callback-label) and `include_obj_callback_strict` are added by [Håvard Thom](https://github.com/havardthom).
- Fixed a corner case where numpy's `np.float32` nans are not ignored when using `ignore_nan_equality` by [Noam Gottlieb](https://github.com/noamgot)
- `orjson` becomes optional again.
- Fix for `ignore_type_in_groups` with numeric values so it does not report number changes when the number types are different.

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

# ChangeLog

Please take a look at the [CHANGELOG](CHANGELOG.md) file.

# Survey

:mega: **Please fill out our [fast 5-question survey](https://forms.gle/E6qXexcgjoKnSzjB8)** so that we can learn how & why you use DeepDiff, and what improvements we should make. Thank you! :dancers:


# Contribute

1. Please make your PR against the dev branch
2. Please make sure that your PR has tests. Since DeepDiff is used in many sensitive data driven projects, we strive to maintain around 100% test coverage on the code.

Please run `pytest --cov=deepdiff --runslow` to see the coverage report. Note that the `--runslow` flag will run some slow tests too. In most cases you only want to run the fast tests which so you wont add the `--runslow` flag.

Or to see a more user friendly version, please run: `pytest --cov=deepdiff --cov-report term-missing --runslow`.

Thank you!

# Citing

How to cite this library (APA style):

    Dehpour, S. (2023). DeepDiff (Version 6.4.0) [Software]. Available from https://github.com/seperman/deepdiff.

How to cite this library (Chicago style):

    Dehpour, Sep. 2023. DeepDiff (version 6.4.0).

# Authors

Please take a look at the [AUTHORS](AUTHORS.md) file.
