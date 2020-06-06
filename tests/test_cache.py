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
                        max_diffs=max_diffs, cache_size=cache_size, cache_tuning_sample_size=0)

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

    def test_cache_1D_array_of_numbers(self):
        ignore_order = True
        cache_size = 5000
        max_diffs = 30000
        max_passes = 40000

        t1 = list(range(1, 200))

        t2 = list(range(300, 400))

        # Since this is not a big array, just for the test, we are reducing the sampling frequency for cache usage
        diff = DeepDiff(t1, t2, ignore_order=ignore_order, max_passes=max_passes,
                        max_diffs=max_diffs, cache_size=cache_size, cache_tuning_sample_size=100)

        stats = diff.get_stats()
        # In this case an optimization happened to compare numbers. Behind the scene we converted the python lists
        # into Numpy arrays and cached the distances between numbers.
        # So the distance cache was heavily used and stayed ON but the level cache was turned off due to low cache hit

        expected_stats = {
            'PASSES COUNT': 1,
            'DIFF COUNT': 300,
            'LEVEL CACHE HIT COUNT': 0,
            'DISTANCE CACHE HIT COUNT': 0,
            'MAX PASS LIMIT REACHED': False,
            'MAX DIFF LIMIT REACHED': False
        }

        assert expected_stats == stats

        expected = {
            'values_changed': {
                'root[198]': {
                    'new_value': 300,
                    'old_value': 199
                },
                'root[197]': {
                    'new_value': 301,
                    'old_value': 198
                },
                'root[196]': {
                    'new_value': 302,
                    'old_value': 197
                },
                'root[195]': {
                    'new_value': 303,
                    'old_value': 196
                },
                'root[194]': {
                    'new_value': 304,
                    'old_value': 195
                },
                'root[193]': {
                    'new_value': 305,
                    'old_value': 194
                },
                'root[192]': {
                    'new_value': 306,
                    'old_value': 193
                },
                'root[191]': {
                    'new_value': 307,
                    'old_value': 192
                },
                'root[190]': {
                    'new_value': 308,
                    'old_value': 191
                },
                'root[189]': {
                    'new_value': 309,
                    'old_value': 190
                },
                'root[188]': {
                    'new_value': 310,
                    'old_value': 189
                },
                'root[187]': {
                    'new_value': 311,
                    'old_value': 188
                },
                'root[186]': {
                    'new_value': 312,
                    'old_value': 187
                },
                'root[185]': {
                    'new_value': 313,
                    'old_value': 186
                },
                'root[184]': {
                    'new_value': 314,
                    'old_value': 185
                },
                'root[183]': {
                    'new_value': 315,
                    'old_value': 184
                },
                'root[182]': {
                    'new_value': 316,
                    'old_value': 183
                },
                'root[181]': {
                    'new_value': 317,
                    'old_value': 182
                },
                'root[180]': {
                    'new_value': 318,
                    'old_value': 181
                },
                'root[179]': {
                    'new_value': 319,
                    'old_value': 180
                },
                'root[178]': {
                    'new_value': 320,
                    'old_value': 179
                },
                'root[177]': {
                    'new_value': 321,
                    'old_value': 178
                },
                'root[176]': {
                    'new_value': 322,
                    'old_value': 177
                },
                'root[175]': {
                    'new_value': 323,
                    'old_value': 176
                },
                'root[174]': {
                    'new_value': 324,
                    'old_value': 175
                },
                'root[173]': {
                    'new_value': 325,
                    'old_value': 174
                },
                'root[172]': {
                    'new_value': 326,
                    'old_value': 173
                },
                'root[171]': {
                    'new_value': 327,
                    'old_value': 172
                },
                'root[170]': {
                    'new_value': 328,
                    'old_value': 171
                },
                'root[169]': {
                    'new_value': 329,
                    'old_value': 170
                },
                'root[168]': {
                    'new_value': 330,
                    'old_value': 169
                },
                'root[167]': {
                    'new_value': 331,
                    'old_value': 168
                },
                'root[166]': {
                    'new_value': 332,
                    'old_value': 167
                },
                'root[165]': {
                    'new_value': 333,
                    'old_value': 166
                },
                'root[164]': {
                    'new_value': 334,
                    'old_value': 165
                },
                'root[163]': {
                    'new_value': 335,
                    'old_value': 164
                },
                'root[162]': {
                    'new_value': 336,
                    'old_value': 163
                },
                'root[161]': {
                    'new_value': 337,
                    'old_value': 162
                },
                'root[160]': {
                    'new_value': 338,
                    'old_value': 161
                },
                'root[159]': {
                    'new_value': 339,
                    'old_value': 160
                },
                'root[158]': {
                    'new_value': 340,
                    'old_value': 159
                },
                'root[157]': {
                    'new_value': 341,
                    'old_value': 158
                },
                'root[156]': {
                    'new_value': 342,
                    'old_value': 157
                },
                'root[155]': {
                    'new_value': 343,
                    'old_value': 156
                },
                'root[154]': {
                    'new_value': 344,
                    'old_value': 155
                },
                'root[153]': {
                    'new_value': 345,
                    'old_value': 154
                },
                'root[152]': {
                    'new_value': 346,
                    'old_value': 153
                },
                'root[151]': {
                    'new_value': 347,
                    'old_value': 152
                },
                'root[150]': {
                    'new_value': 348,
                    'old_value': 151
                },
                'root[149]': {
                    'new_value': 349,
                    'old_value': 150
                },
                'root[148]': {
                    'new_value': 350,
                    'old_value': 149
                },
                'root[147]': {
                    'new_value': 351,
                    'old_value': 148
                },
                'root[146]': {
                    'new_value': 352,
                    'old_value': 147
                },
                'root[145]': {
                    'new_value': 353,
                    'old_value': 146
                },
                'root[144]': {
                    'new_value': 354,
                    'old_value': 145
                },
                'root[143]': {
                    'new_value': 355,
                    'old_value': 144
                },
                'root[142]': {
                    'new_value': 356,
                    'old_value': 143
                },
                'root[141]': {
                    'new_value': 357,
                    'old_value': 142
                },
                'root[140]': {
                    'new_value': 358,
                    'old_value': 141
                },
                'root[139]': {
                    'new_value': 359,
                    'old_value': 140
                },
                'root[138]': {
                    'new_value': 360,
                    'old_value': 139
                },
                'root[137]': {
                    'new_value': 361,
                    'old_value': 138
                },
                'root[136]': {
                    'new_value': 362,
                    'old_value': 137
                },
                'root[135]': {
                    'new_value': 363,
                    'old_value': 136
                },
                'root[134]': {
                    'new_value': 364,
                    'old_value': 135
                },
                'root[133]': {
                    'new_value': 365,
                    'old_value': 134
                },
                'root[132]': {
                    'new_value': 366,
                    'old_value': 133
                },
                'root[131]': {
                    'new_value': 367,
                    'old_value': 132
                },
                'root[130]': {
                    'new_value': 368,
                    'old_value': 131
                },
                'root[129]': {
                    'new_value': 369,
                    'old_value': 130
                },
                'root[128]': {
                    'new_value': 370,
                    'old_value': 129
                },
                'root[127]': {
                    'new_value': 371,
                    'old_value': 128
                },
                'root[126]': {
                    'new_value': 372,
                    'old_value': 127
                },
                'root[125]': {
                    'new_value': 373,
                    'old_value': 126
                },
                'root[124]': {
                    'new_value': 374,
                    'old_value': 125
                },
                'root[123]': {
                    'new_value': 375,
                    'old_value': 124
                },
                'root[122]': {
                    'new_value': 376,
                    'old_value': 123
                },
                'root[121]': {
                    'new_value': 377,
                    'old_value': 122
                },
                'root[120]': {
                    'new_value': 378,
                    'old_value': 121
                },
                'root[119]': {
                    'new_value': 379,
                    'old_value': 120
                },
                'root[118]': {
                    'new_value': 380,
                    'old_value': 119
                },
                'root[117]': {
                    'new_value': 381,
                    'old_value': 118
                },
                'root[116]': {
                    'new_value': 382,
                    'old_value': 117
                },
                'root[115]': {
                    'new_value': 383,
                    'old_value': 116
                },
                'root[114]': {
                    'new_value': 384,
                    'old_value': 115
                },
                'root[113]': {
                    'new_value': 385,
                    'old_value': 114
                },
                'root[112]': {
                    'new_value': 386,
                    'old_value': 113
                },
                'root[111]': {
                    'new_value': 387,
                    'old_value': 112
                },
                'root[110]': {
                    'new_value': 388,
                    'old_value': 111
                },
                'root[109]': {
                    'new_value': 389,
                    'old_value': 110
                },
                'root[108]': {
                    'new_value': 390,
                    'old_value': 109
                },
                'root[107]': {
                    'new_value': 391,
                    'old_value': 108
                },
                'root[106]': {
                    'new_value': 392,
                    'old_value': 107
                },
                'root[105]': {
                    'new_value': 393,
                    'old_value': 106
                },
                'root[104]': {
                    'new_value': 394,
                    'old_value': 105
                },
                'root[103]': {
                    'new_value': 395,
                    'old_value': 104
                },
                'root[102]': {
                    'new_value': 396,
                    'old_value': 103
                },
                'root[101]': {
                    'new_value': 397,
                    'old_value': 102
                },
                'root[100]': {
                    'new_value': 398,
                    'old_value': 101
                },
                'root[99]': {
                    'new_value': 399,
                    'old_value': 100
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
                'root[8]': 9,
                'root[9]': 10,
                'root[10]': 11,
                'root[11]': 12,
                'root[12]': 13,
                'root[13]': 14,
                'root[14]': 15,
                'root[15]': 16,
                'root[16]': 17,
                'root[17]': 18,
                'root[18]': 19,
                'root[19]': 20,
                'root[20]': 21,
                'root[21]': 22,
                'root[22]': 23,
                'root[23]': 24,
                'root[24]': 25,
                'root[25]': 26,
                'root[26]': 27,
                'root[27]': 28,
                'root[28]': 29,
                'root[29]': 30,
                'root[30]': 31,
                'root[31]': 32,
                'root[32]': 33,
                'root[33]': 34,
                'root[34]': 35,
                'root[35]': 36,
                'root[36]': 37,
                'root[37]': 38,
                'root[38]': 39,
                'root[39]': 40,
                'root[40]': 41,
                'root[41]': 42,
                'root[42]': 43,
                'root[43]': 44,
                'root[44]': 45,
                'root[45]': 46,
                'root[46]': 47,
                'root[47]': 48,
                'root[48]': 49,
                'root[49]': 50,
                'root[50]': 51,
                'root[51]': 52,
                'root[52]': 53,
                'root[53]': 54,
                'root[54]': 55,
                'root[55]': 56,
                'root[56]': 57,
                'root[57]': 58,
                'root[58]': 59,
                'root[59]': 60,
                'root[60]': 61,
                'root[61]': 62,
                'root[62]': 63,
                'root[63]': 64,
                'root[64]': 65,
                'root[65]': 66,
                'root[66]': 67,
                'root[67]': 68,
                'root[68]': 69,
                'root[69]': 70,
                'root[70]': 71,
                'root[71]': 72,
                'root[72]': 73,
                'root[73]': 74,
                'root[74]': 75,
                'root[75]': 76,
                'root[76]': 77,
                'root[77]': 78,
                'root[78]': 79,
                'root[79]': 80,
                'root[80]': 81,
                'root[81]': 82,
                'root[82]': 83,
                'root[83]': 84,
                'root[84]': 85,
                'root[85]': 86,
                'root[86]': 87,
                'root[87]': 88,
                'root[88]': 89,
                'root[89]': 90,
                'root[90]': 91,
                'root[91]': 92,
                'root[92]': 93,
                'root[93]': 94,
                'root[94]': 95,
                'root[95]': 96,
                'root[96]': 97,
                'root[97]': 98,
                'root[98]': 99
            }
        }
        assert expected == diff
