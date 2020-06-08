from deepdiff import DeepDiff


class TestCache:

    def test_cache_deeply_nested(self):
        ignore_order = True
        cache_size = 5000
        max_diffs = 300000
        max_passes = 40000

        t1 = [
            [
                [
                    [["a", "b", "c", "d"], ["a", "e", "c", "d"], ["e", "c", "d", 1, 2, 4, 5]],
                    [[10, "b", 2, "d"], ["a", "e", "c", "d"], ["f", 2, "d", 80]],
                    [['10', "d"], ["a", "d", 89], [10, 2, 2, 80]],
                ],
                [
                    [["a", "b", "f", "d"], ["a", "c", "d"], ["e", "c", "d", 1, 2, 4, 5]],
                    [[10, "b", 2, "d"], ["a", "e", "c", "d", "d"], ["f", 22, "d", 80]],
                    [['10', "dd"], ["a", "d", 89], [10, 2]],
                ],
                [
                    [["a", "b", "c", "d"], ["a", "e", "c", "d"], ["e", "c", "d", 1, 2, 4, 5]],
                    [['10', "d"], ["a", "d", 89], [10, 2, 2, 80]],
                ],
                [
                    [["a", "b", "f", "d"], ["a", "c", "d"], ["e", "c", "d", 1, 2, 4, 5]],
                    [[10, "b", 22, "d"], ["a", "e", "c", "d", "d"], ["f", 22, "d", 80]],
                    [['10', "dd"], ["a", "d", 89], [10, 2]],
                ],
            ],
            [
                [
                    [["a", "b", "f", "d"], ["a", "c", "d"], ["e", "c", "d", 1, 2, 4, 5]],
                    [[10, "dada"], ["a", "e", "c", "d", "d"], ["f", 22, "d", 80]],
                    [['10', "dd"], ["a", "d", 389], [10, 2]],
                ],
                [
                    [["a", "b", "c", "d"], ["a", "e", "c", "d"], ["e", "c", "d", 1, 2, 4, 5]],
                    [[10, "b", 2, "d"], ["a", "e", "c", "d"], ["f", 2, "d", 80]],
                    [['10', "d"], ["a", "d", 89], [10, 2, 2, 80]],
                ],
                [
                    [["a", "b", "c", "d"], ["a", "e", "c", "d"], ["e", "c", "d", 1, 2, 4, 5]],
                    [['10', "d"], ["a", "d", 89], [10, 2, 2, 801]],
                ],
                [
                    [["a", "b", "f", "d"], ["a", "c", "d"], ["e", "c", "d", 1, 2, 4, 5]],
                    [[10, "b", 22, "d"], ["a", "e", "d"], ["f", 22, "d", 80]],
                    [['10', "dd"], ["a", "d", 89], [10, 2, 11]],
                ],
            ],
        ]

        t2 = [
            [
                [
                    [["a", "b", "c", "d"], ["a", "e", "c", "d"], ["e", "c", "d", 1, 2, 4, 5]],
                    [[1, "b", 2, "d"], ["a", "e", "c", "d"], ["f", 2, "d", 80]],
                    [['10', 0, "d"], ["a", "d", 89], [10, 2, 2, 80]],
                ],
                [
                    [["a", "b", "f", "d"], ["a", "c", "d"], ["e", "c", "d", 9, 2, 4, 5]],
                    [[10, "dd3"], ["ab", "d", 89], [10, 2]],
                    [[10, "b", 2, "d"], ["a", "e", "c", "d", "d", "f"], ["f", 80]],
                ],
                [
                    [["a", "b", ], ["a", "e", "c1", "d"], ["e", "c", "d", 1, 2, 4, 5]],
                    [["b", 2, "d"], ["a", "e", "c", "d"], ["f", 2, "d", 80]],
                    [['10', "d"], ["a", "d", 89], [10, 2, 2, 80]],
                ],
                [
                    [["a", "b", "f", "d"], ["a", "c", "d"], ["e", "c", "d", 9, 2, 4, 5]],
                    [[10, "b", 2, "d"], ["f", 9], ["f", 80]],
                    [['10', "dd1"], ["ab", "d", 89], [10, 2]],
                ],
            ],
            [
                [
                    [["a", "b", "c", "d"], ["a", "e", "c", "d"], ["e", "c", "d", 1, 2, 4, 5]],
                    [[1, "b", 2, "d"], ["a", "e", "c", "d"], ["f", 2, "d", 80]],
                    [['10', 0, "d"], ["a", "d", 89], [10, 2, 2, 80]],
                ],
                [
                    [["a12", "b", "f", "d"], ["a", "c", "d"], ["e", "c", "d", 9, 2, 4, 5]],
                    [[10, "dd3"], ["ab", "d", 89], [10, 2]],
                    [[10, "b", 2, "d"], ["a", "e", "c", "d", "d", "f"], ["f", 80]],
                ],
                [
                    [["a", "b", ], ["a", "e", "c1", "d"], ["e", "d", 1, 2, 4, 5]],
                    [["b", 22, "d"], ["a", "e", "c", "d"], ["f", 2, "d", 80]],
                    [['10', "d"], ["a", "d", 89], [10, 2, 2, 80]],
                ],
                [
                    [["a", "b", "f", "d"], [], ["e", "c", "d", 9, 2, 4, 5]],
                    [[10, "b", 2, "d"], ["f", 9], ["f", 80]],
                    [['10', "dd1"], ["ab", "d", 89], [10, 2, "4"]],
                ],
            ],
        ]

        diff = DeepDiff(t1, t2, ignore_order=ignore_order, max_passes=max_passes,
                        max_diffs=max_diffs, cache_size=cache_size, cache_tuning_sample_size=0,
                        cutoff_intersection_for_pairs=1)

        stats = diff.get_stats()
        expected_stats = {
            'PASSES COUNT': 802,
            'DIFF COUNT': 4937,
            'LEVEL CACHE HIT COUNT': 524,
            'DISTANCE CACHE HIT COUNT': 3440,
            'MAX PASS LIMIT REACHED': False,
            'MAX DIFF LIMIT REACHED': False
        }
        assert expected_stats == stats

        expected = {
            'values_changed': {
                'root[1][1][1][0][0]': {
                    'new_value': 1,
                    'old_value': 10
                },
                'root[1][0][0][2][3]': {
                    'new_value': 9,
                    'old_value': 1
                },
                'root[1][3][0][2][3]': {
                    'new_value': 9,
                    'old_value': 1
                },
                'root[1][3][2][0][1]': {
                    'new_value': 'dd1',
                    'old_value': 'dd'
                },
                'root[1][0][2][0]': {
                    'new_value': [10, 'dd3'],
                    'old_value': ['10', 'dd']
                },
                'root[0][1]': {
                    'new_value': [[['a12', 'b', 'f', 'd'], ['a', 'c', 'd'],
                                   ['e', 'c', 'd', 9, 2, 4, 5]],
                                  [[10, 'dd3'], ['ab', 'd', 89], [10, 2]],
                                  [[10, 'b', 2, 'd'], ['a', 'e', 'c', 'd', 'd', 'f'],
                                   ['f', 80]]],
                    'old_value': [[['a', 'b', 'f', 'd'], ['a', 'c', 'd'],
                                   ['e', 'c', 'd', 1, 2, 4, 5]],
                                  [[10, 'b', 2, 'd'], ['a', 'e', 'c', 'd', 'd'],
                                   ['f', 22, 'd', 80]],
                                  [['10', 'dd'], ['a', 'd', 89], [10, 2]]]
                },
                'root[1][0][1][0]': {
                    'new_value': [10, 'b', 2, 'd'],
                    'old_value': [10, 'dada']
                },
                'root[1][3][2][1][0]': {
                    'new_value': 'ab',
                    'old_value': 'a'
                },
                'root[1][3][1][1]': {
                    'new_value': ['f', 9],
                    'old_value': ['a', 'e', 'd']
                }
            },
            'iterable_item_added': {
                'root[1][1][2][0][1]': 0,
                'root[1][2][1]': [['b', 2, 'd'], ['a', 'e', 'c', 'd'],
                                  ['f', 2, 'd', 80]]
            },
            'iterable_item_removed': {
                'root[1][3][2][2][2]': 11
            }
        }
        assert expected == diff

        diff2 = DeepDiff(t1, t2, ignore_order=ignore_order, max_passes=max_passes,
                         max_diffs=max_diffs, cache_size=500, cache_tuning_sample_size=500,
                         cutoff_intersection_for_pairs=1)

        stats2 = diff2.get_stats()
        expected_stats2 = {
            'PASSES COUNT': 3936,
            'DIFF COUNT': 19365,
            'LEVEL CACHE HIT COUNT': 17,
            'DISTANCE CACHE HIT COUNT': 11863,
            'MAX PASS LIMIT REACHED': False,
            'MAX DIFF LIMIT REACHED': False
        }

        assert expected_stats2 == stats2

        expected2 = {
            'values_changed': {
                'root[0][0][1][0][0]': {
                    'new_value': 1,
                    'old_value': 10
                },
                'root[0][1][0][2][3]': {
                    'new_value': 9,
                    'old_value': 1
                },
                'root[0][3][0][2][3]': {
                    'new_value': 9,
                    'old_value': 1
                },
                'root[0][3][1][0][2]': {
                    'new_value': 2,
                    'old_value': 22
                },
                'root[1][1][1][0][0]': {
                    'new_value': 1,
                    'old_value': 10
                },
                'root[1][0][1][2][1]': {
                    'new_value': 2,
                    'old_value': 22
                },
                'root[1][0][2][1][2]': {
                    'new_value': 89,
                    'old_value': 389
                },
                'root[1][3][0][2][3]': {
                    'new_value': 9,
                    'old_value': 1
                },
                'root[1][3][1][0][2]': {
                    'new_value': 2,
                    'old_value': 22
                },
                'root[1][3][2][1][0]': {
                    'new_value': 'ab',
                    'old_value': 'a'
                },
                'root[0][3][2][0][1]': {
                    'new_value': 'dd1',
                    'old_value': 'dd'
                },
                'root[1][0][0][0][2]': {
                    'new_value': 'c1',
                    'old_value': 'f'
                },
                'root[1][2][0][0][0]': {
                    'new_value': 10,
                    'old_value': 'a'
                },
                'root[0][3][1][1]': {
                    'new_value': ['f', 9],
                    'old_value': ['a', 'e', 'c', 'd', 'd']
                },
                'root[1][2][1][1][0]': {
                    'new_value': 'ab',
                    'old_value': 'a'
                },
                'root[1][2][0][2]': {
                    'new_value': ['f', 80],
                    'old_value': ['e', 'c', 'd', 1, 2, 4, 5]
                },
                'root[1][3][1][1]': {
                    'new_value': ['f', 9],
                    'old_value': ['a', 'e', 'd']
                },
                'root[1][2][0][0][2]': {
                    'new_value': 2,
                    'old_value': 'c'
                },
                'root[1][0][0][1][1]': {
                    'new_value': 'b',
                    'old_value': 'c'
                },
                'root[0][1][2][1][0]': {
                    'new_value': 'ab',
                    'old_value': 'a'
                },
                'root[0][3][2][1][0]': {
                    'new_value': 'ab',
                    'old_value': 'a'
                },
                'root[1][2][1][0]': {
                    'new_value': [10, 'dd3'],
                    'old_value': ['10', 'd']
                },
                'root[1][3][2][2][2]': {
                    'new_value': '4',
                    'old_value': 11
                },
                'root[0][1][2][0]': {
                    'new_value': [10, 'dd3'],
                    'old_value': ['10', 'dd']
                },
                'root[1][3][0][1]': {
                    'new_value': [],
                    'old_value': ['a', 'c', 'd']
                },
                'root[1][0][2][0][1]': {
                    'new_value': 'd',
                    'old_value': 'dd'
                },
                'root[1][3][2][0][1]': {
                    'new_value': 'dd1',
                    'old_value': 'dd'
                },
                'root[1][0][1][0]': {
                    'new_value': ['b', 22, 'd'],
                    'old_value': [10, 'dada']
                },
                'root[1][0][0][0][1]': {
                    'new_value': 'e',
                    'old_value': 'b'
                },
                'root[0][2][0][1][2]': {
                    'new_value': 'c1',
                    'old_value': 'c'
                }
            },
            'iterable_item_added': {
                'root[0][0][2][0][1]':
                0,
                'root[0][1][1][1][5]':
                'f',
                'root[0][2][1]': [['b', 2, 'd'], ['a', 'e', 'c', 'd'],
                                  ['f', 2, 'd', 80]],
                'root[1][1][2][0][1]':
                0,
                'root[1][2][0]': [['a12', 'b', 'f', 'd'], ['a', 'c', 'd'],
                                  ['e', 'c', 'd', 9, 2, 4, 5]],
                'root[1][2][0][1][5]':
                'f',
                'root[1][0][2][2][3]':
                80
            },
            'iterable_item_removed': {
                'root[0][1][1][2][1]': 22,
                'root[0][1][1][2][2]': 'd',
                'root[0][2][0][0][2]': 'c',
                'root[0][2][0][0][3]': 'd',
                'root[0][3][1][2][1]': 22,
                'root[0][3][1][2][2]': 'd',
                'root[1][2][1][2][3]': 801,
                'root[1][0][0][1][2]': 'd',
                'root[1][0][0][2][1]': 'c',
                'root[1][3][1][2][1]': 22,
                'root[1][3][1][2][2]': 'd'
            }
        }
        assert expected2 == diff2

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
            'LEVEL CACHE HIT COUNT': 0,
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
            'LEVEL CACHE HIT COUNT': 0,
            'DISTANCE CACHE HIT COUNT': 0,
            'MAX PASS LIMIT REACHED': False,
            'MAX DIFF LIMIT REACHED': False
        }
        assert expected_stats == stats

        expected = {'values_changed': {'root[11]': {'new_value': 30, 'old_value': 12}, 'root[10]': {'new_value': 31, 'old_value': 11}, 'root[9]': {'new_value': 32, 'old_value': 10}}, 'iterable_item_removed': {'root[0]': 1, 'root[1]': 2, 'root[2]': 3, 'root[3]': 4, 'root[4]': 5, 'root[5]': 6, 'root[6]': 7, 'root[7]': 8, 'root[8]': 9}}
        assert expected == diff

    def test_level_cache_does_not_affect_final_results(self):
        t1 = [[['b'], 3]]
        t2 = [[['a'], 2]]

        diff1 = DeepDiff(t1, t2, ignore_order=True, cache_size=0,
                         cache_tuning_sample_size=0, cutoff_intersection_for_pairs=1)
        diff2 = DeepDiff(t1, t2, ignore_order=True, cache_size=5000,
                         cache_tuning_sample_size=0, cutoff_intersection_for_pairs=1)
        assert diff1 == diff2
