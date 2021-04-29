grep is a more user friendly interface for DeepSearch. It takes exactly the same arguments as DeepSearch except that you pipe the object into it instead of passing it as a parameter.

It works just like grep in linux shell!

**Parameters**

item : The item to search for

verbose_level : int >= 0, default = 1.
    Verbose level one shows the paths of found items.
    Verbose level 2 shows the path and value of the found items.

exclude_paths: list, default = None.
    List of paths to exclude from the report.

exclude_types: list, default = None.
    List of object types to exclude from the report.

case_sensitive: Boolean, default = False

match_string: Boolean, default = False
    If True, the value of the object or its children have to exactly match the item.
    If False, the value of the item can be a part of the value of the object or its children

use_regexp: Boolean, default = False

strict_checking: Boolean, default = True
    If True, it will check the type of the object to match, so when searching for '1234',
    it will NOT match the int 1234. Currently this only affects the numeric values searching.


**Examples**

Importing
    >>> from deepdiff import grep
    >>> from pprint import pprint

Search in list for string
    >>> obj = ["long somewhere", "string", 0, "somewhere great!"]
    >>> item = "somewhere"
    >>> ds = obj | grep(item)
    >>> print(ds)
    {'matched_values': {'root[3]', 'root[0]'}

Search in nested data for string
    >>> obj = ["something somewhere", {"long": "somewhere", "string": 2, 0: 0, "somewhere": "around"}]
    >>> item = "somewhere"
    >>> ds = obj | grep(item, verbose_level=2)
    >>> pprint(ds, indent=2)
    { 'matched_paths': {"root[1]['somewhere']": 'around'},
      'matched_values': { 'root[0]': 'something somewhere',
                          "root[1]['long']": 'somewhere'}}

You can also use regular expressions
    >>> obj = ["something here", {"long": "somewhere", "someone": 2, 0: 0, "somewhere": "around"}]
    >>> ds = obj | grep("some.*", use_regexp=True)
    { 'matched_paths': ["root[1]['someone']", "root[1]['somewhere']"],
      'matched_values': ['root[0]', "root[1]['long']"]}


Change strict_checking to False to match numbers in strings and vice versa:
    >>> obj = {"long": "somewhere", "num": 1123456, 0: 0, "somewhere": "around"}
    >>> item = "1234"
    >>> result = {"matched_values": {"root['num']"}}
    >>> ds = obj | grep(item, verbose_level=1, use_regexp=True)
    >>> pprint(ds)
    {}
    >>>
    >>> ds = obj | grep(item, verbose_level=1, use_regexp=True, strict_checking=False)
    >>> pprint(ds)
    {'matched_values': ["root['num']"]}
