from decimal import Decimal
from deepdiff import DeepDiff


class TestDiffMath:
    def test_math_diff(self):
        """Testing for the correct setting and usage of epsilon."""
        d1 = {"a": Decimal("3.5")}
        d2 = {"a": Decimal("4")}
        ep = 0.5
        res = DeepDiff(d1, d2, math_epsilon=ep)
        assert res == {}
        d1 = {"a": Decimal("2.5")}
        d2 = {"a": Decimal("3")}
        ep = 0.5
        res = DeepDiff(d1, d2, math_epsilon=ep)
        assert res == {}
        d1 = {"a": Decimal("2.5")}
        d2 = {"a": Decimal("2")}
        ep = 0.5
        res = DeepDiff(d1, d2, math_epsilon=ep)
        assert res == {}
        d1 = {"a": Decimal("7.175")}
        d2 = {"a": Decimal("7.174")}
        ep = 0.1
        res = DeepDiff(d1, d2, math_epsilon=ep)
        assert res == {}
        d1 = {"a": Decimal("7.175")}
        d2 = {"a": Decimal("7.174")}
        ep = 0.01
        res = DeepDiff(d1, d2, math_epsilon=ep)
        assert res == {}
        d1 = {"a": Decimal("7.175")}
        d2 = {"a": Decimal("7.174")}
        ep = 0.001
        res = DeepDiff(d1, d2, math_epsilon=ep)
        assert res == {}
        d1 = {"a": Decimal("7.175")}
        d2 = {"a": Decimal("7.174")}
        ep = 0.0001
        expected = {
            "values_changed": {
                "root['a']": {
                    "new_value": Decimal("7.174"),
                    "old_value": Decimal("7.175"),
                }
            }
        }
        res = DeepDiff(d1, d2, math_epsilon=ep)
        assert res == expected

    def test_math_diff_special_case(self):
        """Testing epsilon on a special Decimal case.
        
        Even though the Decimal looks different, math will evaluate it for us."""
        d1 = {"a": Decimal("9.709999618320632")}
        d2 = {"a": Decimal("9.710000038146973")}
        ep = 0.001
        res = DeepDiff(d1, d2, math_epsilon=ep)
        assert res == {}
        d1 = {"a": Decimal("9.709999618320632")}
        d2 = {"a": Decimal("9.710000038146973")}
        ep = 0.0001
        res = DeepDiff(d1, d2, math_epsilon=ep)
        assert res == {}
        d1 = {"a": Decimal("9.709999618320632")}
        d2 = {"a": Decimal("9.710000038146973")}
        ep = 0.00001
        res = DeepDiff(d1, d2, math_epsilon=ep)
        assert res == {}
        d1 = {"a": Decimal("9.709999618320632")}
        d2 = {"a": Decimal("9.710000038146973")}
        ep = 0.000001
        res = DeepDiff(d1, d2, math_epsilon=ep)
        assert res == {}
        d1 = {"a": Decimal("9.709999618320632")}
        d2 = {"a": Decimal("9.710000038146973")}
        ep = 0.0000001
        res = DeepDiff(d1, d2, math_epsilon=ep)
        expected = {
            "values_changed": {
                "root['a']": {
                    "new_value": Decimal("9.710000038146973"),
                    "old_value": Decimal("9.709999618320632"),
                }
            }
        }
        assert res == expected

    def test_math_diff_ignore_order(self):
        """math_close will not work with ignore_order=true.
        
        Items are hashed if order is ignored, that will not work."""
        d1 = {"a": [Decimal("9.709999618320632"), Decimal("9.709999618320632")]}
        d2 = {"a": [Decimal("9.710000038146973"), Decimal("9.709999618320632")]}
        ep = 0.0001
        res = DeepDiff(d1, d2, ignore_order=False, math_epsilon=ep)
        assert res == {}

    def test_math_diff_ignore_order_warning(self, caplog):
        """math_close will not work with ignore_order=true.
        
        Items are hashed if order is ignored, that will not work."""
        d1 = {"a": [Decimal("9.709999618320632"), Decimal("9.709999618320632")]}
        d2 = {"a": [Decimal("9.710000038146973"), Decimal("9.709999618320632")]}
        ep = 0.0001
        res = DeepDiff(d1, d2, ignore_order=True, math_epsilon=ep)
        expected = {
            "iterable_item_added": {"root['a'][0]": Decimal("9.710000038146973")}
        }
        assert res == expected
        # assert "math_epsilon will be ignored." in caplog.text

    def test_ignore_numeric_type_changes_with_numeric_keys_and_no_significant_digits(self):
        """Test that ignore_numeric_type_changes works with numeric keys when significant_digits is None.
        
        This test covers the bug fix in _get_clean_to_keys_mapping where significant_digits=None
        caused a crash when number_to_string was called without the required parameter.
        """
        # Test case with numeric keys and ignore_numeric_type_changes=True, significant_digits=None
        d1 = {1: "value1", 2.5: "value2"}  
        d2 = {1.0: "value1", 2.5: "value2"}  # int vs float keys
        
        # This should not crash and should treat 1 and 1.0 as the same key
        result = DeepDiff(d1, d2, ignore_numeric_type_changes=True, significant_digits=None)
        assert result == {}
