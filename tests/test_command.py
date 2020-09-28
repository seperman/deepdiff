import os
import pytest
from click.testing import CliRunner
from deepdiff.commands import diff
from conftest import FIXTURES_DIR


class TestCommands:

    @pytest.mark.parametrize('t1, t2, kwargs, expected_in_stdout', [
        ('t1.json', 't2.json', {}, "'dictionary_item_added\': [root[0]"),
        ('t1.json', 't2_json.csv', {}, "'old_value\': \'value2\'"),
        ('t1.csv', 't2.csv', {}, "\'new_value\': \'James\'"),
    ])
    def test_diff_command(self, t1, t2, kwargs, expected_in_stdout):
        t1 = os.path.join(FIXTURES_DIR, t1)
        t2 = os.path.join(FIXTURES_DIR, t2)
        runner = CliRunner()
        result = runner.invoke(diff, [t1, t2], **kwargs)
        assert result.exit_code == 0
        assert expected_in_stdout in result.output
