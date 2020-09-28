import os
import pytest
from click.testing import CliRunner
from deepdiff.commands import diff
from conftest import FIXTURES_DIR
from deepdiff.helper import pypy3


@pytest.mark.skipif(pypy3, reason='clevercsv is not supported in pypy3')
class TestCommands:

    @pytest.mark.parametrize('t1, t2, kwargs, expected_in_stdout', [
        ('t1.json', 't2.json', {}, "'dictionary_item_added\': [root[0]"),
        ('t1.json', 't2_json.csv', {}, "'old_value\': \'value2\'"),
        ('t1.csv', 't2.csv', {}, "\'new_value\': \'James\'"),
        ('t1.toml', 't2.toml', {}, "10.0.0.2"),
        ('t1.pickle', 't2.pickle', {}, "'new_value': 5, 'old_value': 1"),
        ('t1.yaml', 't2.yaml', {}, "'new_value': 61, 'old_value': 65"),
    ])
    def test_diff_command(self, t1, t2, kwargs, expected_in_stdout):
        t1 = os.path.join(FIXTURES_DIR, t1)
        t2 = os.path.join(FIXTURES_DIR, t2)
        runner = CliRunner()
        result = runner.invoke(diff, [t1, t2], **kwargs)
        assert result.exit_code == 0
        assert expected_in_stdout in result.output
