:doc:`/index`

F.A.Q
=====


Q: DeepDiff report is not precise when ignore_order=True
--------------------------------------------------------

    >>> from deepdiff import DeepDiff
    >>> from pprint import pprint
    >>> t1 = [
    ...     {
    ...         "key": "some/pathto/customers/foo/",
    ...         "flags": 0,
    ...         "value": ""
    ...     },
    ...     {
    ...         "key": "some/pathto/customers/foo/account_number",
    ...         "flags": 0,
    ...         "value": "somevalue1"
    ...     }
    ... ]
    >>>
    >>> t2 = [
    ...     {
    ...         "key": "some/pathto/customers/foo/account_number",
    ...         "flags": 0,
    ...         "value": "somevalue2"
    ...     },
    ...     {
    ...         "key": "some/pathto/customers/foo/",
    ...         "flags": 0,
    ...         "value": "new"
    ...     }
    ... ]
    >>>
    >>> pprint(DeepDiff(t1, t2))
    {'values_changed': {"root[0]['key']": {'new_value': 'some/pathto/customers/foo/account_number',
                                           'old_value': 'some/pathto/customers/foo/'},
                        "root[0]['value']": {'new_value': 'somevalue2',
                                             'old_value': ''},
                        "root[1]['key']": {'new_value': 'some/pathto/customers/foo/',
                                           'old_value': 'some/pathto/customers/foo/account_number'},
                        "root[1]['value']": {'new_value': 'new',
                                             'old_value': 'somevalue1'}}}

**Answer**

This is explained in :ref:`cutoff_distance_for_pairs_label` and :ref:`cutoff_intersection_for_pairs_label`

Bump up these 2 parameters to 1 and you get what you want:

    >>> pprint(DeepDiff(t1, t2, ignore_order=True, cutoff_distance_for_pairs=1, cutoff_intersection_for_pairs=1))
    {'values_changed': {"root[0]['value']": {'new_value': 'new', 'old_value': ''},
                        "root[1]['value']": {'new_value': 'somevalue2',
                                             'old_value': 'somevalue1'}}}


Q: TypeError: Object of type type is not JSON serializable
----------------------------------------------------------

I'm trying to serialize the DeepDiff results into json and I'm getting the TypeError.

    >>> diff=DeepDiff(1, "a")
    >>> diff
    {'type_changes': {'root': {'old_type': <class 'int'>, 'new_type': <class 'str'>, 'old_value': 1, 'new_value': 'a'}}}
    >>> json.dumps(diff)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File ".../json/__init__.py", line 231, in dumps
        return _default_encoder.encode(obj)
      File ".../json/encoder.py", line 199, in encode
        chunks = self.iterencode(o, _one_shot=True)
      File ".../json/encoder.py", line 257, in iterencode
        return _iterencode(o, 0)
      File ".../json/encoder.py", line 179, in default
        raise TypeError(f'Object of type {o.__class__.__name__} '
    TypeError: Object of type type is not JSON serializable

**Answer**

In order to serialize DeepDiff results into json, use to_json()

    >>> diff.to_json()
    '{"type_changes": {"root": {"old_type": "int", "new_type": "str", "old_value": 1, "new_value": "a"}}}'

Back to :doc:`/index`
