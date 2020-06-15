:doc:`/index`

.. _optimizations_label:

Optimizations
=============

If you are dealing with large nested objects and ignore_order=True, chances are DeepDiff takes a while to calculate the diff. Here are some tips that may help you with optimizations and progress report.


Max Passes
----------

:ref:`max_passes_label` comes with the default of 10000000.
If you don't need to exactly pinpoint the difference and you can get away with getting a less granular report, you can reduce the number of passes. It is recommended to get a diff of your objects with the defaults max_passes and take a look at the stats by running :ref:`get_stats_label` before deciding to reduce this number. In many cases reducing this number does not yield faster results.


Back to :doc:`/index`
