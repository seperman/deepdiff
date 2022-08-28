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
def nested_a_affected_paths():
    return {
        'root[0][0][2][0][1]', 'root[0][1][1][1][5]', 'root[0][2][1]',
        'root[1][1][2][0][1]', 'root[1][2][0]', 'root[1][2][0][1][5]',
        'root[1][0][2][2][3]', 'root[0][0][1][0][0]', 'root[0][1][0][2][3]',
        'root[0][3][0][2][3]', 'root[0][3][1][0][2]', 'root[1][1][1][0][0]',
        'root[1][0][1][2][1]', 'root[1][0][2][1][2]', 'root[1][3][0][2][3]',
        'root[1][3][1][0][2]', 'root[1][2][0][2]', 'root[1][0][2][0][1]',
        'root[0][3][2][0][1]', 'root[0][3][2][1][0]', 'root[1][3][1][1]',
        'root[1][2][1][1][0]', 'root[1][2][1][0]', 'root[1][0][0][0][2]',
        'root[1][3][2][1][0]', 'root[1][0][0][1][1]', 'root[0][1][2][0]',
        'root[0][1][2][1][0]', 'root[0][2][0][1][2]', 'root[1][3][0][1]',
        'root[0][3][1][1]', 'root[1][2][0][0][2]', 'root[1][3][2][0][1]',
        'root[1][0][1][0]', 'root[1][2][0][0][0]', 'root[1][0][0][0][1]',
        'root[1][3][2][2][2]', 'root[0][1][1][2][1]', 'root[0][1][1][2][2]',
        'root[0][2][0][0][2]', 'root[0][2][0][0][3]', 'root[0][3][1][2][1]',
        'root[0][3][1][2][2]', 'root[1][2][1][2][3]', 'root[1][0][0][1][2]',
        'root[1][0][0][2][1]', 'root[1][3][1][2][1]', 'root[1][3][1][2][2]'
    }


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


@pytest.fixture(scope='class')
def compare_func_t1():
    with open(os.path.join(FIXTURES_DIR, 'compare_func_t1.json')) as the_file:
        return json.load(the_file)


@pytest.fixture(scope='class')
def compare_func_t2():
    with open(os.path.join(FIXTURES_DIR, 'compare_func_t2.json')) as the_file:
        return json.load(the_file)


@pytest.fixture(scope='class')
def compare_func_result1():
    with open(os.path.join(FIXTURES_DIR, 'compare_func_result1.json')) as the_file:
        return json.load(the_file)
