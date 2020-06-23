import sys
import os
import json
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'tests')))

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'tests/fixtures/')


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


@pytest.fixture(scope='class')
def nested_a_t1():
    with open(os.path.join(FIXTURES_DIR, 'nested_a_t1.json')) as the_file:
        return json.load(the_file)


@pytest.fixture(scope='class')
def nested_a_t2():
    with open(os.path.join(FIXTURES_DIR, 'nested_a_t2.json')) as the_file:
        return json.load(the_file)


@pytest.fixture(scope='class')
def nested_a_result():
    with open(os.path.join(FIXTURES_DIR, 'nested_a_result.json')) as the_file:
        return json.load(the_file)


@pytest.fixture(scope='class')
def nested_b_t1():
    with open(os.path.join(FIXTURES_DIR, 'nested_b_t1.json')) as the_file:
        return json.load(the_file)


@pytest.fixture(scope='class')
def nested_b_t2():
    with open(os.path.join(FIXTURES_DIR, 'nested_b_t2.json')) as the_file:
        return json.load(the_file)


@pytest.fixture(scope='class')
def nested_b_result():
    with open(os.path.join(FIXTURES_DIR, 'nested_b_result.json')) as the_file:
        return json.load(the_file)
