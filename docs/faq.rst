:doc:`/index`

F.A.Q
=====

.. Note::
    |:mega:| **Please fill out our** `fast 5-question survey <https://forms.gle/E6qXexcgjoKnSzjB8>`__ so that we can learn how & why you use DeepDiff, and what improvements we should make. Thank you! |:dancers:|


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


Q: The report of changes in a nested dictionary is too granular
---------------------------------------------------------------

**Answer**

Use :ref:`threshold_to_diff_deeper_label`

    >>> from deepdiff import DeepDiff
    >>> t1 = {"veggie": "carrots"}
    >>> t2 = {"meat": "carrots"}
    >>>
    >>> DeepDiff(t1, t2, threshold_to_diff_deeper=0)
    {'dictionary_item_added': ["root['meat']"], 'dictionary_item_removed': ["root['veggie']"]}
    >>> DeepDiff(t1, t2, threshold_to_diff_deeper=0.33)
    {'values_changed': {'root': {'new_value': {'meat': 'carrots'}, 'old_value': {'veggie': 'carrots'}}}}



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


Q: How do I parse DeepDiff result paths?
----------------------------------------

**Answer**

Use parse_path:

    >>> from deepdiff import parse_path
    >>> parse_path("root[1][2]['age']")
    [1, 2, 'age']
    >>> parse_path("root[1][2]['age']", include_actions=True)
    [{'element': 1, 'action': 'GET'}, {'element': 2, 'action': 'GET'}, {'element': 'age', 'action': 'GET'}]
    >>>
    >>> parse_path("root['joe'].age")
    ['joe', 'age']
    >>> parse_path("root['joe'].age", include_actions=True)
    [{'element': 'joe', 'action': 'GET'}, {'element': 'age', 'action': 'GETATTR'}]

Or use the tree view so you can use path(output_format='list'):

    >>> t1 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2, 3, 4]}}
    >>> t2 = {1:1, 2:2, 3:3, 4:{"a":"hello", "b":[1, 2]}}
    >>> ddiff = DeepDiff(t1, t2, view='tree')
    >>> ddiff
    {'iterable_item_removed': [<root[4]['b'][2] t1:3, t2:not present>, <root[4]['b'][3] t1:4, t2:not present>]}
    >>> # Note that the iterable_item_removed is a set. In this case it has 2 items in it.
    >>> # One way to get one item from the set is to convert it to a list
    >>> # And then get the first item of the list:
    >>> removed = list(ddiff['iterable_item_removed'])[0]
    >>> removed
    <root[4]['b'][2] t1:3, t2:not present>
    >>>
    >>> parent = removed.up
    >>> parent
    <root[4]['b'] t1:[1, 2, 3, 4], t2:[1, 2]>
    >>> parent.path()  # gives you the string representation of the path
    "root[4]['b']"
    >>> parent.path(output_format='list')  # gives you the list of keys and attributes that make up the path
    [4, 'b']


---------

.. admonition:: A message from `Sep <https://github.com/seperman>`__, the creator of DeepDiff

    | 👋 Hi there,
    |
    | Thank you for using DeepDiff!
    | As an engineer, I understand the frustration of wrestling with **unruly data** in pipelines.
    | That's why I developed a new tool - `Qluster <https://qluster.ai/solution>`__ to empower non-engineers to control and resolve data issues at scale autonomously and **stop bugging the engineers**! 🛠️
    |
    | If you are going through this pain now, I would love to give you `early access <https://www.qluster.ai/try-qluster>`__ to Qluster and get your feedback.

Back to :doc:`/index`
