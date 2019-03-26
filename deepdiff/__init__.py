"""This module offers the DeepDiff, DeepSearch, grep and DeepHash classes."""
# flake8: noqa
import logging
import pkg_resources

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)8s %(message)s')

__version__ = pkg_resources.get_distribution("deepdiff").version

from .diff import DeepDiff
from .search import DeepSearch, grep
from .deephash import DeepHash
