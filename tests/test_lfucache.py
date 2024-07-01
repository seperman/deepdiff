import random
import pytest
import concurrent.futures
from deepdiff.lfucache import LFUCache


class TestLFUcache:

    @pytest.mark.parametrize("items, size, expected_results, expected_freq", [
        (['a', 'a', 'b', 'a', 'c', 'b', 'd'], 3, [('b', 2), ('c', 1), ('d', 1)], '1.333'),
        (['a', 'a', 'b', 'a', 'c', 'b', 'd', 'e', 'c', 'b'], 3, [('b', 3), ('d', 1), ('e', 1)], '1.666'),
        (['a', 'a', 'b', 'a', 'c', 'b', 'd', 'e', 'c', 'b', 'b', 'c', 'd', 'b'], 3, [('b', 5), ('c', 3), ('d', 2)], '3.333'),
    ])
    def test_lfu(self, items, size, expected_results, expected_freq, benchmark):
        benchmark(self._test_lfu, items, size, expected_results, expected_freq)

    def _test_lfu(self, items, size, expected_results, expected_freq):
        lfucache = LFUCache(size)
        for item in items:
            lfucache.set(item, value='{}_cached'.format(item))
        for item in items:
            lfucache.get(item)
        results = lfucache.get_sorted_cache_keys()
        assert expected_results == results
        freq = lfucache.get_average_frequency()
        assert expected_freq == str(freq)[:5]

    def test_get_multithreading(self):
        keys = 'aaaaaaaaaaaaaaaaaaaaaaaaaaabbc'
        lfucache = LFUCache(2)

        def _do_set(cache, key):
            cache.set(key, value='{}_cached'.format(key))

        def _do_get(cache, key):
            return cache.get(key)

        def _key_gen():
            i = 0
            while i < 30000:
                i += 1
                yield random.choice(keys)

        def _random_func(cache, key):
            return random.choice([_do_get, _do_get, _do_set])(cache, key)

        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            futures = (executor.submit(_random_func, lfucache, key) for key in _key_gen())
            for future in concurrent.futures.as_completed(futures):
                future.result()
