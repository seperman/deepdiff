grep is a more user friendly interface for DeepSearch. It takes exactly the same arguments as DeepSearch.
And it works just like grep in linux shell!

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
