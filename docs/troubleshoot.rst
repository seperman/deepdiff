:doc:`/index`

.. _troubleshoot_label:

Troubleshoot
============

Murmur3 Installation
~~~~~~~~~~~~~~~~~~~~

NOTE: Murmur3 was removed from DeepDiff 5.2.0

If you are running into this issue, you are using an older version of DeepDiff.

`Failed to build mmh3 when installing DeepDiff`

DeepDiff prefers to use Murmur3 for hashing. However you have to manually install murmur3 by running: `pip install mmh3`

On MacOS Mojave some user experience difficulty when installing Murmur3.

The problem can be solved by running:

    `xcode-select --install`

And then running

    `pip install mmh3`

Back to :doc:`/index`
