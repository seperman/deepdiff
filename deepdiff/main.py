from deepdiff import DeepDiff


def main():
    t1 = [{"id": 1}, {"id": 1}, {"id": 1}]
    t2 = [{"id": 1, "name": 1}]
    # t1 = [1, 1, 1]
    # t2 = [2, 2]
    ddiff = DeepDiff(t1, t2, view="tree",
                     ignore_order=True,
                     report_repetition=True,
                     cutoff_intersection_for_pairs=1,
                     cutoff_distance_for_pairs=1, )
    print(ddiff)


if __name__ == '__main__':
    main()