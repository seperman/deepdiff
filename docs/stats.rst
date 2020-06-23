:doc:`/index`

.. _stats_n_logging_label:

Stats and Logging
=================

.. _log_frequency_in_sec_label:

Log Frequency In Sec
--------------------

log_frequency_in_sec: Integer, default = 0
    How often to log the progress. The default of 0 means logging progress is disabled.
    If you set it to 20, it will log every 20 seconds. This is useful only when running DeepDiff
    on massive objects that will take a while to run. If you are only dealing with small objects, keep it at 0 to disable progress logging.

For example we have run a diff on 2 nested objects that took 2 seconds to get the results. By passing the log_frequency_in_sec=1, we get the following in the logs:

    >>> DeepDiff(t1, t2, log_frequency_in_sec=1)
    INFO:deepdiff.diff:DeepDiff 1 seconds in progress. Pass #1634, Diff #8005
    INFO:deepdiff.diff:DeepDiff 2 seconds in progress. Pass #3319, Diff #16148
    INFO:deepdiff.diff:stats {'PASSES COUNT': 3960, 'DIFF COUNT': 19469, 'DISTANCE CACHE HIT COUNT': 11847, 'MAX PASS LIMIT REACHED': False, 'MAX DIFF LIMIT REACHED': False, 'DURATION SEC': 2}

.. note::
    The default python logger will omit the info logs. You can either set the logging filter to include info logs or pass a different logger via :ref:`progress_logger_label`

        >>> import logging
        >>> logging.basicConfig(level=logging.INFO)


.. _progress_logger_label:

Progress Logger
---------------

progress_logger: log function, default = logger.info
    What logging function to use specifically for progress reporting. This function is only used when progress logging is enabled
    by setting log_frequency_in_sec to anything above zero. The function that is passed as the progress_logger needs to be thread safe.


For example you can pass progress_logger=logger.warning to the example above and everything is logged as warning level:

    >>> DeepDiff(t1, t2, log_frequency_in_sec=1, progress_logger=logger.warning)
    WARNING:deepdiff.diff:DeepDiff 1 seconds in progress. Pass #1634, Diff #8005
    WARNING:deepdiff.diff:DeepDiff 2 seconds in progress. Pass #3319, Diff #16148
    WARNING:deepdiff.diff:stats {'PASSES COUNT': 3960, 'DIFF COUNT': 19469, 'DISTANCE CACHE HIT COUNT': 11847, 'MAX PASS LIMIT REACHED': False, 'MAX DIFF LIMIT REACHED': False, 'DURATION SEC': 2}


.. _get_stats_label:

Get Stats
---------

You can run the get_stats() method on a diff object to get some stats on the object.
For example:

    >>> from pprint import pprint
    >>> from deepdiff import DeepDiff
    >>>
    >>> t1 = [
    ...     [1, 2, 3, 9], [9, 8, 5, 9]
    ... ]
    >>>
    >>> t2 = [
    ...     [1, 2, 4, 10], [4, 2, 5]
    ... ]
    >>>
    >>> diff = DeepDiff(t1, t2, ignore_order=True, cache_size=5000, cutoff_intersection_for_pairs=1)
    >>> pprint(diff.get_stats())
    {'DIFF COUNT': 37,
     'DISTANCE CACHE HIT COUNT': 0,
     'MAX DIFF LIMIT REACHED': False,
     'MAX PASS LIMIT REACHED': False,
     'PASSES COUNT': 7}


Back to :doc:`/index`
