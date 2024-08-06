from deepdiff.anyset import AnySet


class TestAnySet:
    def test_anyset_init1(self):
        items = [1, 2, 4, 4]
        result = AnySet(items)
        expected = ({1, 2, 4}, {})
        assert expected == result
        assert repr(result) == r'< AnySet SetOrdered([1, 2, 4]), {} >'

    def test_anyset_init2(self):
        items = [1, 2, {1}, 4, 4, {1}]
        result = AnySet(items)
        expected = ({1, 2, 4}, {'e298e5a6cfa50a5b9d2cd4392c6c34a867d325e8de2966a8183c4cdf9a93120d': {1}})
        assert expected == result

    def test_anyset_init3_add(self):
        items = [1, 2, {1}, 4, 4, {1}]
        result = AnySet()
        for item in items:
            result.add(item)
        expected = ({1, 2, 4}, {'e298e5a6cfa50a5b9d2cd4392c6c34a867d325e8de2966a8183c4cdf9a93120d': {1}})
        assert expected == result

    def test_anyset_pop1(self):
        items = [1, 2, {1}, 4, 4, {1}]
        result = AnySet(items)
        while result:
            result_len = len(result)
            item = result.pop()
            assert item in items
            assert len(result) == result_len - 1

    def test_iter_anyset(self):
        items = [1, 2, {1}, 4, 4, {1}, {3: 3}]
        obj = AnySet(items)
        result = [i for i in obj]
        assert [1, 2, 4, {1}, {3: 3}] == result
