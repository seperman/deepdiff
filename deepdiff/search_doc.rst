**Grep**

grep is a new interface for Deep Search. It takes exactly the same arguments.
And it works just like grep in shell!

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
