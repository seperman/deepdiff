import sys
import os
import json
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'tests')))

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'tests/fixtures/')


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
