**DeepHash**

DeepHash calculates the hash of objects based on their contents in a deterministic way.
This way 2 objects with the same content should have the same hash.

The main usage of DeepHash is to calculate the hash of otherwise unhashable objects.
For example you can use DeepHash to calculate the hash of a set or a dictionary!

The core of DeepHash is a deterministic serialization of your object into a string so it
can be passed to a hash function. By default it uses Murmur 3 128 bit hash function.
but you can pass another hash function to it if you want.

**Parameters**

obj : any object, The object to be hashed based on its content.

hashes: dictionary, default = empty dictionary
    A dictionary of {object id: object hash} to start with.
    Any object that is encountered and its id is already in the hashes dictionary,
    will re-use the hash that is provided by this dictionary instead of re-calculating
    its hash.

exclude_types: list, default = None
    List of object types to exclude from hashing.

exclude_paths: list, default = None
    List of paths to exclude from the report. If only one item, you can path it as a string.

exclude_regex_paths: list, default = None
    List of string regex paths or compiled regex paths objects to exclude from the report. If only one item, you can pass it as a string or regex compiled object.

hasher: function. default = DeepHash.murmur3_128bit
    hasher is the hashing function. The default is DeepHash.murmur3_128bit.
    But you can pass another hash function to it if you want.
    For example a cryptographic hash function or Python's builtin hash function.
    All it needs is a function that takes the input in string format and returns the hash.

    You can use it by passing: hasher=hash for Python's builtin hash.

    SHA1 is already provided as an alternative too:
    You can use it by passing: hasher=DeepHash.sha1hex

ignore_repetition: Boolean, default = True
    If repetitions in an iterable should cause the hash of iterable to be different.
    Note that the deepdiff diffing functionality lets this to be the default at all times.
    But if you are using DeepHash directly, you can set this parameter.

significant_digits : int >= 0, default=None
    If it is a non negative integer, it compares only that many digits AFTER
    the decimal point.

    This only affects floats, decimal.Decimal and complex.

    Takse a look at DeepDiff.diff docs for explanation of how this works.

constant_size: Boolean, default = True
    What DeepHash does is to "prep" the contents of objects into strings.
    If constant_size is set, then it actually goes ahead and hashes the string
    using the hasher function.

    The only time you want the constant_size to be False is if you want to know what
    the string representation of your object is BEFORE it gets hashed.

ignore_string_type_changes: Boolean, default = True
    string type conversions should not affect the hash output when this is set to True.
    For example "Hello" and b"Hello" should produce the same hash.

**Returns**
    A dictionary of {item id: item hash}.
    If your object is nested, it will build hashes of all the objects it contains!


**Examples**

Let's say you have a dictionary object.
    >>> from deepdiff import DeepHash
    >>>
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
    {4355639248: 2468916477072481777512283587789292749, 4355639280: -35787773492556653776377555218122431491, 4358636128: -88390647972316138151822486391929534118, 4358009664: 8833996863197925870419376694314494743, 4357467952: 34150898645750099477987229399128149852}

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

The result hash is 34150898645750099477987229399128149852.
In this case the hash of the obj is 128 bit that is divided into 2 64bit integers.
Using Murmur 3 64bit for hashing is preferred (and is the default behaviour)
since the chance of hash collision will be minimal and hashing will be deterministic
and will not depend on the version of the Python.

If you do a deep copy of obj, it should still give you the same hash:
    >>> from copy import deepcopy
    >>> obj2 = deepcopy(obj)
    >>> DeepHash(obj2)[obj2]
    34150898645750099477987229399128149852

Note that by default DeepHash will ignore string type differences. So if your strings were bytes, you would still get the same hash:
    >>> obj3 = {1: 2, b'a': b'b'}
    >>> DeepHash(obj3)[obj3]
    34150898645750099477987229399128149852

But if you want a different hash if string types are different, set ignore_string_type_changes to True:
    >>> DeepHash(obj3, ignore_string_type_changes=True)[obj3]
    64067525765846024488103933101621212760
