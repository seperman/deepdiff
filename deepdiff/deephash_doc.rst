**DeepHash**

DeepHash calculates the hash of objects based on their contents in a deterministic way.
This way 2 objects with the same content should have the same hash.

The main usage of DeepHash is to calculate the hash of otherwise unhashable objects.
For example you can use DeepHash to calculate the hash of a set or a dictionary!

At the core of it, DeepHash is a deterministic serialization of your object into a string so it
can be passed to a hash function. By default it uses Murmur 3 128 bit hash function which is a
fast, non-cryptographic hashing function. You have the option to pass any another hashing function to be used instead.

**Parameters**

obj : any object, The object to be hashed based on its content.

hashes: dictionary, default = empty dictionary
    A dictionary of {object or object id: object hash} to start with.
    Any object that is encountered and it is already in the hashes dictionary or its id is in the hashes dictionary,
    will re-use the hash that is provided by this dictionary instead of re-calculating
    its hash. This is typically used when you have a series of objects to be hashed and there might be repeats of the same object.

exclude_types: list, default = None
    List of object types to exclude from hashing.

exclude_paths: list, default = None
    List of paths to exclude from the report. If only one item, you can path it as a string instead of a list containing only one path.

exclude_regex_paths: list, default = None
    List of string regex paths or compiled regex paths objects to exclude from the report. If only one item, you can path it as a string instead of a list containing only one regex path.

hasher: function. default = DeepHash.murmur3_128bit
    hasher is the hashing function. The default is DeepHash.murmur3_128bit.
    But you can pass another hash function to it if you want.
    For example a cryptographic hash function or Python's builtin hash function.
    All it needs is a function that takes the input in string format and returns the hash.

    You can use it by passing: hasher=hash for Python's builtin hash.

    The following alternatives are already provided:

    - hasher=DeepHash.murmur3_128bit
    - hasher=DeepHash.murmur3_64bit
    - hasher=DeepHash.sha1hex

ignore_repetition: Boolean, default = True
    If repetitions in an iterable should cause the hash of iterable to be different.
    Note that the deepdiff diffing functionality lets this to be the default at all times.
    But if you are using DeepHash directly, you can set this parameter.

significant_digits : int >= 0, default=None
    If it is a non negative integer, it compares only that many digits AFTER
    the decimal point.

    This only affects floats, decimal.Decimal and complex numbers.

    Take a look at DeepDiff.diff docs for explanation of how this works.

apply_hash: Boolean, default = True
    DeepHash at its core is doing deterministic serialization of objects into strings.
    Then it hashes the string.
    The only time you want the apply_hash to be False is if you want to know what
    the string representation of your object is BEFORE it gets hashed.

ignore_string_type_changes: Boolean, default = True
    string type conversions should not affect the hash output when this is set to True.
    For example "Hello" and b"Hello" should produce the same hash.

ignore_numeric_type_changes: Boolean, default = True
    numeric type conversions should not affect the hash output when this is set to True.
    For example 10, 10.0 and Decimal(10) should produce the same hash.
    However when ignore_numeric_type_changes is set to True, all numbers are converted
    to decimals with the precision of significant_digits parameter.
    If no significant_digits is passed by the user, a default value of 55 is used.

    For example if significant_digits=5, 1.1, Decimal(1.1) are both converted to 1.10000

    That way they both produce the same hash.

**Returns**
    A dictionary of {item: item hash}.
    If your object is nested, it will build hashes of all the objects it contains too.


**Examples**

Let's say you have a dictionary object.
    >>> from deepdiff import DeepHash
    >>> obj = {1: 2, 'a': 'b'}

If you try to hash it:
    >>> hash(obj)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: unhashable type: 'dict'

But with DeepHash:
    >>> from deepdiff import DeepHash
    >>> obj = {1: 2, 'a': 'b'}
    >>> DeepHash(obj)
    {1: 234041559348429806012597903916437026784, 2: 148655924348182454950690728321917595655, 'a': 119173504597196970070553896747624927922, 'b': 4994827227437929991738076607196210252, '!>*id4488569408': 32452838416412500686422093274247968754}

So what is exactly the hash of obj in this case?
DeepHash is calculating the hash of the obj and any other object that obj contains.
The output of DeepHash is a dictionary of object IDs to their hashes.
In order to get the hash of obj itself, you need to use the object (or the id of object) to get its hash:
    >>> hashes = DeepHash(obj)
    >>> hashes[obj]
    34150898645750099477987229399128149852

Which you can write as:
    >>> hashes = DeepHash(obj)[obj]

At first it might seem weird why DeepHash(obj)[obj] but remember that DeepHash(obj) is a dictionary of hashes of all other objects that obj contains too.

The result hash is 34150898645750099477987229399128149852 which is generated by
Murmur 3 128bit hashing algorithm. If you prefer to use another hashing algorithm, you can pass it using the hasher parameter. Read more about Murmur3 here: https://en.wikipedia.org/wiki/MurmurHash

If you do a deep copy of obj, it should still give you the same hash:
    >>> from copy import deepcopy
    >>> obj2 = deepcopy(obj)
    >>> DeepHash(obj2)[obj2]
    34150898645750099477987229399128149852

Note that by default DeepHash will ignore string type differences. So if your strings were bytes, you would still get the same hash:
    >>> obj3 = {1: 2, b'a': b'b'}
    >>> DeepHash(obj3)[obj3]
    34150898645750099477987229399128149852

But if you want a different hash if string types are different, set ignore_string_type_changes to False:
    >>> DeepHash(obj3, ignore_string_type_changes=False)[obj3]
    64067525765846024488103933101621212760

On the other hand, ignore_numeric_type_changes is by default False.
    >>> obj1 = {4:10}
    >>> obj2 = {4.0: Decimal(10.0)}
    >>> DeepHash(obj1)[4] == DeepHash(obj2)[4.0]
    False
    >>> DeepHash(obj1, ignore_numeric_type_changes=True)[4] == DeepHash(obj2, ignore_numeric_type_changes=True)[4.0]
    True
