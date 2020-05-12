:doc:`/index`

.. _optimizations_label:

Optimizations
=============

If you are dealing with large nested objects and ignore_order=True, chances are DeepDiff takes a while to calculate the diff. Here are some tips that may help you with optimizations and progress report.


Max Passes
----------

Reduce the :ref:max_passes_label from the default which is 10000000.
If you don't need to exactly pinpoint the difference and you can get away with getting a report of the parents of the actual difference.

.. _log_frequency_in_sec_label:

Log Frequency In Sec
--------------------

log_frequency_in_sec: Integer, default = 0
    How often to log the progress. The default of 0 means logging progress is disabled.
    If you set it to 20, it will log every 20 seconds. This is useful only when running DeepDiff
    on massive objects that will take a while to run. If you are only dealing with small objects, keep it at 0 to disable progress logging.


Back to :doc:`/index`
