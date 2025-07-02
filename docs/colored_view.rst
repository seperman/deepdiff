.. _colored_view_label:

Colored View
============

The `ColoredView` feature in `deepdiff` provides a human-readable, color-coded JSON output of the
differences between two objects. This feature is particularly useful for visualizing changes in a
clear and intuitive manner.

- **Color-Coded Differences:**

  - **Added Elements:** Shown in green.
  - **Removed Elements:** Shown in red.
  - **Changed Elements:** The old value is shown in red, and the new value is shown in green.

Usage
-----

To use the `ColoredView`, simply pass the `COLORED_VIEW` option to the `DeepDiff` function:

.. code-block:: python

    from deepdiff import DeepDiff
    from deepdiff.helper import COLORED_VIEW

    t1 = {"name": "John", "age": 30, "scores": [1, 2, 3], "address": {"city": "New York", "zip": "10001"}}
    t2 = {"name": "John", "age": 31, "scores": [1, 2, 4], "address": {"city": "Boston", "zip": "10001"}, "new": "value"}

    diff = DeepDiff(t1, t2, view=COLORED_VIEW)
    print(diff)

Or from command line:

.. code-block:: bash

    deep diff --view colored t1.json t2.json

The output will look something like this:

.. raw:: html

    <pre style="background-color: #f8f8f8; padding: 1em; border-radius: 4px;">
    {
      "name": "John",
      "age": <span style="color: #ff0000">30</span> -> <span style="color: #00aa00">31</span>,
      "scores": [
        1,
        2,
        <span style="color: #ff0000">3</span> -> <span style="color: #00aa00">4</span>
      ],
      "address": {
        "city": <span style="color: #ff0000">"New York"</span> -> <span style="color: #00aa00">"Boston"</span>,
        "zip": "10001"
      },
      <span style="color: #00aa00">"new": "value"</span>
    }
    </pre>

Colored Compact View
--------------------

For a more concise output, especially with deeply nested objects where many parts are unchanged,
the `ColoredView` with the compact option can be used. This view is similar but collapses
unchanged nested dictionaries to `{...}` and unchanged lists/tuples to `[...]`. To use the compact
option do:

.. code-block:: python

    from deepdiff import DeepDiff
    from deepdiff.helper import COLORED_COMPACT_VIEW

    t1 = {"name": "John", "age": 30, "scores": [1, 2, 3], "address": {"city": "New York", "zip": "10001"}}
    t2 = {"name": "John", "age": 31, "scores": [1, 2, 4], "address": {"city": "New York", "zip": "10001"}, "new": "value"}

    diff = DeepDiff(t1, t2, view=COLORED_COMPACT_VIEW)
    print(diff)

Or from command line:

.. code-block:: bash

    deep diff --view colored_compact t1.json t2.json


The output will look something like this:

.. raw:: html

    <pre style="background-color: #f8f8f8; padding: 1em; border-radius: 4px;">
    {
      "name": "John",
      "age": <span style="color: #ff0000">30</span> -> <span style="color: #00aa00">31</span>,
      "scores": [
        1,
        2,
        <span style="color: #ff0000">3</span> -> <span style="color: #00aa00">4</span>
      ],
      "address": {...},
      <span style="color: #00aa00">"new": "value"</span>
    }
    </pre>
