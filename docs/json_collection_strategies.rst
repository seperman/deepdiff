JSON Collection Strategies
==========================

``DeepJSONDiff`` is an opt-in facade for comparing JSON-like values whose nested
arrays require path-specific semantics. It builds canonical caller-isolated
views and delegates the final recursive comparison to ``DeepDiff``. Existing
``DeepDiff`` behaviour is unchanged.

Basic identity matching
-----------------------

Use ``match_by`` when list records have a stable business identity::

    from deepdiff import CollectionStrategy, DeepJSONDiff

    diff = DeepJSONDiff(
        expected,
        actual,
        collection_strategies=[
            CollectionStrategy(
                path="$.users",
                match_by=("id",),
            )
        ],
    )

Reordering does not create differences. Additions, removals, and field changes
remain visible against canonical identity-keyed paths.

Selectors
---------

Selectors use a deliberately small JSONPath-like grammar:

- ``$.users`` selects an object key.
- ``$.groups[0].users`` selects one array index.
- ``$.groups[*].users`` matches exactly one array index.
- ``$.*.users`` matches exactly one object key.
- ``$['a-b']`` selects a quoted key that cannot be written safely in dot form.

Wildcards never cross additional levels. Diagnostic paths use the same quoted
key syntax and can be reused as selectors. JSON object keys are expected to be
strings.

Relative identity and sort fields use dotted extraction and may include numeric
list indexes, such as ``product.id`` or ``versions.0.number``.

Identity values
---------------

Identity fields must resolve, after normalization, to finite JSON scalar values:
``None``, booleans, integers, finite floats, or strings. Structured and
non-finite values are rejected.

Composite identities are encoded using a canonical type-preserving format, so
values such as integer ``1``, float ``1.0``, and string ``"1"`` remain distinct
and delimiter characters cannot cause collisions.

Filtering, normalization, and exclusion
---------------------------------------

``filter_func`` and normalizers receive defensive copies and may mutate them
without modifying caller-owned inputs. Copies are created only when callbacks
are configured; otherwise canonicalization rebuilds the structure directly.

Processing order is:

1. Copy when callbacks require isolation.
2. Apply ``filter_func``.
3. Apply normalizers.
4. Extract identity and sort fields.
5. Remove ``exclude_fields``.
6. Canonicalize nested content.

Identity and sort fields may therefore also appear in ``exclude_fields``. They
can control matching or ordering without remaining in the compared record.

Sorting
-------

``sort_by`` creates a total, type-stable order for JSON-compatible values.
Integers and floats are intentionally distinguished. Finite values, infinities,
and NaN values have deterministic positions and do not produce mixed-type sort
errors.

Structured sort keys are supported only for JSON lists and mappings with string
keys. Tuples, sets, mappings with non-string keys, and arbitrary objects are
rejected rather than ordered through unstable ``repr`` output.

Order-insensitive scalar arrays
-------------------------------

``compare_as_set=True`` performs multiset (bag) comparison:

- order is ignored;
- duplicate counts remain significant;
- integer and float values remain type-distinct;
- only finite JSON scalar values are accepted.

It cannot be combined with ``match_by`` or ``sort_by``.

Missing identities
------------------

The default ``MissingIdentityPolicy.FALLBACK`` retains records missing one or
more identity fields and compares them in relative order. ``EXCLUDE`` omits
them, and ``ERROR`` raises ``IdentityExtractionError``. Enum members and their
string values are accepted.

Duplicate identities
--------------------

Duplicate identities raise ``DuplicateIdentityError`` by default.
``DuplicateIdentityPolicy.GROUP`` retains every record under the identity.
Provide ``sort_by`` when duplicate-group order is not meaningful.

Rule precedence
---------------

Higher ``priority`` wins when multiple strategies match. At equal priority, the
pattern with more exact tokens wins. Equally specific matches are rejected as
ambiguous.

Diagnostics
-----------

``get_stats()`` separates diagnostics by input side::

    stats = diff.get_stats()
    left_users = stats["left"]["$.users"]
    right_users = stats["right"]["$.users"]

Each entry includes the selected strategy, input item count, filtered count,
missing-identity count, and duplicate-group count. Keeping sides separate
prevents statistics for different logical parents from being merged when a
parent identity-matched collection is reordered.

DeepDiff keyword compatibility
------------------------------

Identity matching changes selected arrays into canonical mappings. DeepDiff
options that interpret caller-visible paths, object paths, or iterable positions
would therefore operate on a different structure. ``DeepJSONDiff`` rejects
these path-sensitive options instead of silently changing their meaning:

- ``include_paths``
- ``exclude_paths``
- ``exclude_regex_paths``
- ``ignore_order_func``
- ``iterable_compare_func``
- ``custom_operators``
- ``exclude_obj_callback``
- ``exclude_obj_callback_strict``

Other keyword arguments are forwarded to the underlying ``DeepDiff`` instance.

Result interface
----------------

``DeepJSONDiff`` is a composition-based facade, not a complete ``DeepDiff``
subclass. It implements the read-only mapping interface and exposes ``diff`` for
direct access to the underlying result. ``to_dict()`` and ``to_json()`` are
delegated explicitly.
