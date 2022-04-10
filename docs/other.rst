:doc:`/index`

Other Parameters
================


.. _encodings_label:

Encodings
---------

significant_digits : int >= 0, default=None

Character encodings to iterate through when we convert bytes into strings. You may want to pass an explicit list of encodings in your objects if you start getting UnicodeDecodeError from DeepHash. Also check out :ref:`ignore_encoding_errors_label` if you can get away with ignoring these errors and don't want to bother with an explicit list of encodings but it will come at the price of slightly less accuracy of the final results. Example: encodings=["utf-8", "latin-1"]

The reason the decoding of bytes to string is needed is that when `ignore_order = True` we calculate the hash of the objects in order to facilitate in diffing them. In order to calculate the hash, we serialize all objects into strings. During the serialization we may encounter issues with character encodings.

**Examples:**

Comparing bytes that have non UTF-8 encoding:
    >>> from deepdiff import DeepDiff
    >>> item = b"\xbc cup of flour"
    >>> DeepDiff([b'foo'], [item], ignore_order=True)
    Traceback (most recent call last):
        raise UnicodeDecodeError(
    UnicodeDecodeError: 'utf-8' codec can't decode byte 0xbc in position 0: Can not produce a hash for root: invalid start byte in 'p of flo...'. Please either pass ignore_encoding_errors=True or pass the encoding via encodings=['utf-8', '...'].

Let's try to pass both 'utf-8' and 'latin-1' as encodings to be tries:
    >>> DeepDiff([b'foo'], [item], encodings=['utf-8', 'latin-1'], ignore_order=True)
    {'values_changed': {'root[0]': {'new_value': b'\xbc cup of flour', 'old_value': b'foo'}}}


.. _ignore_encoding_errors_label:

Ignore Encoding Errors
----------------------

ignore_encoding_errors: Boolean, default = False

If you want to get away with UnicodeDecodeError without passing explicit character encodings, set this option to True. If you want to make sure the encoding is done properly, keep this as False and instead pass an explicit list of character encodings to be considered via the encodings parameter.

We can generally get the same results as above example if we just pass `ignore_encoding_errors=True`. However it comes at the cost of less accuracy of the results.
    >>> DeepDiff([b'foo'], [b"\xbc cup of flour"], ignore_encoding_errors=True, ignore_order=True)
    {'values_changed': {'root[0]': {'new_value': b'\xbc cup of flour', 'old_value': b'foo'}}}

For example if we replace `foo` with ` cup of flour`, we have bytes that are only different in the problematic character. Ignoring that character means DeepDiff will consider these 2 strings to be equal since their hash becomes the same. Note that we only hash items when `ignore_order=True`.
    >>> DeepDiff([b" cup of flour"], [b"\xbc cup of flour"], ignore_encoding_errors=True, ignore_order=True)
    {}

But if we had passed the proper encoding, it would have detected that these 2 bytes are different:
    >>> DeepDiff([b" cup of flour"], [b"\xbc cup of flour"], encodings=['latin-1'], ignore_order=True)
    {'values_changed': {'root[0]': {'new_value': b'\xbc cup of flour', 'old_value': b' cup of flour'}}}


Back to :doc:`/index`
