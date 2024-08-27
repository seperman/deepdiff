import pytest
from decimal import Decimal
from deepdiff import DeepDiff
from deepdiff.helper import py_current_version


class TestCache:

    @pytest.mark.slow
    def test_cache_deeply_nested_a1(self, nested_a_t1, nested_a_t2, nested_a_result, nested_a_affected_paths, benchmark):
        benchmark(self._test_cache_deeply_nested_a1, nested_a_t1, nested_a_t2, nested_a_result, nested_a_affected_paths)

    def _test_cache_deeply_nested_a1(self, nested_a_t1, nested_a_t2, nested_a_result, nested_a_affected_paths):
        diff = DeepDiff(nested_a_t1, nested_a_t2, ignore_order=True,
                        cache_size=5000, cache_tuning_sample_size=280,
                        cutoff_intersection_for_pairs=1)

        stats = diff.get_stats()
        expected_stats = {
            "PASSES COUNT": 1671,
            "DIFF COUNT": 8556,
            "DISTANCE CACHE HIT COUNT": 3445,
            "MAX PASS LIMIT REACHED": False,
            "MAX DIFF LIMIT REACHED": False,
        }
        # assert expected_stats == stats
        assert nested_a_result == diff
        diff_of_diff = DeepDiff(nested_a_result, diff.to_dict(), ignore_order=False)
        assert not diff_of_diff
        assert nested_a_affected_paths == diff.affected_paths
        assert [0, 1] == diff.affected_root_keys

    @pytest.mark.slow
    def test_cache_deeply_nested_a2(self, nested_a_t1, nested_a_t2, nested_a_result):

        diff = DeepDiff(nested_a_t1, nested_a_t2, ignore_order=True,
                        cache_size=500, cache_tuning_sample_size=500,
                        cutoff_intersection_for_pairs=1)

        # stats = diff.get_stats()
        # # Somehow just in python 3.5 the cache stats are different. Weird.
        # if py_current_version == Decimal('3.5'):
        #     expected_stats = {
        #         'PASSES COUNT': 3981,
        #         'DIFF COUNT': 19586,
        #         'DISTANCE CACHE HIT COUNT': 11925,
        #         'MAX PASS LIMIT REACHED': False,
        #         'MAX DIFF LIMIT REACHED': False
        #     }
        # else:
        #     expected_stats = {
        #         'PASSES COUNT': 3960,
        #         'DIFF COUNT': 19469,
        #         'DISTANCE CACHE HIT COUNT': 11847,
        #         'MAX PASS LIMIT REACHED': False,
        #         'MAX DIFF LIMIT REACHED': False
        #     }
        # assert expected_stats == stats
        assert nested_a_result == diff
        diff_of_diff = DeepDiff(nested_a_result, diff.to_dict(), ignore_order=False)
        assert not diff_of_diff

    def test_cache_deeply_nested_b(self, nested_b_t1, nested_b_t2, nested_b_result):

        diff = DeepDiff(nested_b_t1, nested_b_t2, ignore_order=True,
                        cache_size=5000, cache_tuning_sample_size=0,
                        cutoff_intersection_for_pairs=1)

        stats = diff.get_stats()
        expected_stats = {
            'PASSES COUNT': 110,
            'DIFF COUNT': 306,
            'DISTANCE CACHE HIT COUNT': 0,
            'MAX PASS LIMIT REACHED': False,
            'MAX DIFF LIMIT REACHED': False
        }
        stats_diff = DeepDiff(expected_stats, stats, use_log_scale=True, log_scale_similarity_threshold=0.15)
        assert not stats_diff
        assert nested_b_result == diff

        diff_of_diff = DeepDiff(nested_b_result, diff.to_dict(), ignore_order=False)
        assert not diff_of_diff

    def test_cache_1D_array_of_numbers_that_do_not_overlap(self):
        ignore_order = True
        cache_size = 5000
        max_diffs = 30000
        max_passes = 40000

        t1 = list(range(1, 30))

        t2 = list(range(100, 120))

        diff = DeepDiff(t1, t2, ignore_order=ignore_order, max_passes=max_passes,
                        max_diffs=max_diffs, cache_size=cache_size, cache_tuning_sample_size=100)

        stats = diff.get_stats()
        # Since there was no overlap between the 2 arrays, even though ignore_order=True,
        # the algorithm switched to comparing by order.
        expected_stats = {
            'PASSES COUNT': 0,
            'DIFF COUNT': 50,
            'DISTANCE CACHE HIT COUNT': 0,
            'MAX PASS LIMIT REACHED': False,
            'MAX DIFF LIMIT REACHED': False
        }
        assert expected_stats == stats

        expected = {'values_changed': {'root[0]': {'new_value': 100, 'old_value': 1}, 'root[1]': {'new_value': 101, 'old_value': 2}, 'root[2]': {'new_value': 102, 'old_value': 3}, 'root[3]': {'new_value': 103, 'old_value': 4}, 'root[4]': {'new_value': 104, 'old_value': 5}, 'root[5]': {'new_value': 105, 'old_value': 6}, 'root[6]': {'new_value': 106, 'old_value': 7}, 'root[7]': {'new_value': 107, 'old_value': 8}, 'root[8]': {'new_value': 108, 'old_value': 9}, 'root[9]': {'new_value': 109, 'old_value': 10}, 'root[10]': {'new_value': 110, 'old_value': 11}, 'root[11]': {'new_value': 111, 'old_value': 12}, 'root[12]': {'new_value': 112, 'old_value': 13}, 'root[13]': {'new_value': 113, 'old_value': 14}, 'root[14]': {'new_value': 114, 'old_value': 15}, 'root[15]': {'new_value': 115, 'old_value': 16}, 'root[16]': {'new_value': 116, 'old_value': 17}, 'root[17]': {'new_value': 117, 'old_value': 18}, 'root[18]': {'new_value': 118, 'old_value': 19}, 'root[19]': {'new_value': 119, 'old_value': 20}}, 'iterable_item_removed': {'root[20]': 21, 'root[21]': 22, 'root[22]': 23, 'root[23]': 24, 'root[24]': 25, 'root[25]': 26, 'root[26]': 27, 'root[27]': 28, 'root[28]': 29}}
        assert expected == diff

    def test_cache_1D_array_of_numbers_that_overlap(self):
        ignore_order = True
        cache_size = 5000
        max_diffs = 30000
        max_passes = 40000

        t1 = list(range(1, 30))

        t2 = list(range(13, 33))

        diff = DeepDiff(t1, t2, ignore_order=ignore_order, max_passes=max_passes,
                        max_diffs=max_diffs, cache_size=cache_size, cache_tuning_sample_size=100)

        stats = diff.get_stats()
        # In this case an optimization happened to compare numbers. Behind the scene we converted the python lists
        # into Numpy arrays and cached the distances between numbers.
        # So the distance cache was heavily used and stayed ON but the level cache was turned off due to low cache hit

        expected_stats = {
            'PASSES COUNT': 1,
            'DIFF COUNT': 16,
            'DISTANCE CACHE HIT COUNT': 0,
            'MAX PASS LIMIT REACHED': False,
            'MAX DIFF LIMIT REACHED': False
        }
        assert expected_stats == stats

        expected = {
            'values_changed': {
                'root[11]': {
                    'new_value': 30,
                    'old_value': 12
                },
                'root[10]': {
                    'new_value': 31,
                    'old_value': 11
                },
                'root[9]': {
                    'new_value': 32,
                    'old_value': 10
                }
            },
            'iterable_item_removed': {
                'root[0]': 1,
                'root[1]': 2,
                'root[2]': 3,
                'root[3]': 4,
                'root[4]': 5,
                'root[5]': 6,
                'root[6]': 7,
                'root[7]': 8,
                'root[8]': 9
            }
        }
        assert expected == diff

    def test_cache_does_not_affect_final_results(self):
        t1 = [[['b'], 8, 1, 2, 3, 4]]
        t2 = [[['a'], 5, 1, 2, 3, 4]]

        diff1 = DeepDiff(t1, t2, ignore_order=True, cache_size=0,
                         cache_tuning_sample_size=0, cutoff_intersection_for_pairs=1)
        diff2 = DeepDiff(t1, t2, ignore_order=True, cache_size=5000,
                         cache_tuning_sample_size=0, cutoff_intersection_for_pairs=1)
        print(diff1.get_stats())
        print(diff1)
        assert diff1 == diff2
