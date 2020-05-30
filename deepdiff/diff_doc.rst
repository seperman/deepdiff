**DeepDiff**

Deep Difference of dictionaries, iterables, strings and almost any other object.
It will recursively look for all the changes.

**Parameters**

t1 : A dictionary, list, string or any python object that has __dict__ or __slots__
    This is the first item to be compared to the second item

t2 : dictionary, list, string or almost any python object that has __dict__ or __slots__
    The second item is to be compared to the first one

ignore_order : Boolean, default=False
    :ref:`ignore_order_label` ignores order of elements when comparing iterables (lists)
    Normally ignore_order does not report duplicates and repetition changes.
    In order to report repetitions, set report_repetition=True in addition to ignore_order=True

report_repetition : Boolean, default=False
    :ref:`report_repetition_label` reports repetitions when set True
    It only works when ignore_order is set to True too.

significant_digits : int >= 0, default=None
    :ref:`significant_digits_label` defines the number of digits AFTER the decimal point to be used in the comparison. However you can override that by setting the number_format_notation="e" which will make it mean the digits in scientific notation.

truncate_datetime: string, default = None
    Can take value one of 'second', 'minute', 'hour', 'day' and truncate with this value datetime objects before hashing it

number_format_notation : string, default="f"
    :ref:`number_format_notation_label` is what defines the meaning of significant digits. The default value of "f" means the digits AFTER the decimal point. "f" stands for fixed point. The other option is "e" which stands for exponent notation or scientific notation.

number_to_string_func : function, default=None
    :ref:`number_to_string_func_label` is an advanced feature to give the user the full control into overriding how numbers are converted to strings for comparison. The default function is defined in https://github.com/seperman/deepdiff/blob/master/deepdiff/helper.py and is called number_to_string. You can define your own function to do that.

verbose_level: int >= 0, default = 1
    Higher verbose level shows you more details.
    For example verbose level 1 shows what dictionary item are added or removed.
    And verbose level 2 shows the value of the items that are added or removed too.
    Note that the verbose_level is ignore for the delta view.

exclude_paths: list, default = None
    :ref:`exclude_paths_label`
    List of paths to exclude from the report. If only one item, you can path it as a string.

exclude_regex_paths: list, default = None
    :ref:`exclude_regex_paths_label`
    List of string regex paths or compiled regex paths objects to exclude from the report. If only one item, you can pass it as a string or regex compiled object.

hasher: default = DeepHash.murmur3_128bit
    Hash function to be used. If you don't want Murmur3, you can use Python's built-in hash function
    by passing hasher=hash. This is for advanced usage and normally you don't need to modify it.

view: string, default = text
    :ref:`view_label`
    Views are different "formats" of results. Each view comes with its own features.
    The choices are text (the default) and tree.
    The text view is the original format of the results.
    The tree view allows you to traverse through the tree of results. So you can traverse through the tree and see what items were compared to what.

exclude_types: list, default = None
    :ref:`exclude_types_label`
    List of object types to exclude from the report.

exclude_obj_callback: function, default = None
    :ref:`exclude_obj_callback_label`
    A function that takes the object and its path and returns a Boolean. If True is returned, the object is excluded from the results, otherwise it is included.
    This is to give the user a higher level of control than one can achieve via exclude_paths, exclude_regex_paths or other means.

ignore_string_type_changes: Boolean, default = False
    :ref:`ignore_string_type_changes_label`
    Whether to ignore string type changes or not. For example b"Hello" vs. "Hello" are considered the same if ignore_string_type_changes is set to True.

ignore_numeric_type_changes: Boolean, default = False
    :ref:`ignore_numeric_type_changes_label`
    Whether to ignore numeric type changes or not. For example 10 vs. 10.0 are considered the same if ignore_numeric_type_changes is set to True.

ignore_type_in_groups: Tuple or List of Tuples, default = None
    :ref:`ignore_type_in_groups_label`
    ignores types when t1 and t2 are both within the same type group.

ignore_type_subclasses: Boolean, default = False
    :ref:`ignore_type_subclasses_label`
    ignore type (class) changes when dealing with the subclasses of classes that were marked to be ignored.

ignore_string_case: Boolean, default = False
    :ref:`ignore_string_case_label`
    Whether to be case-sensitive or not when comparing strings. By settings ignore_string_case=False, strings will be compared case-insensitively.

ignore_nan_inequality: Boolean, default = False
    :ref:`ignore_nan_inequality_label`
    Whether to ignore float('nan') inequality in Python.

ignore_private_variables: Boolean, default = True
    :ref:`ignore_private_variables_label`
    Whether to exclude the private variables in the calculations or not. It only affects variables that start with double underscores (__).

max_passes: Integer, default = 10000000
    :ref:`max_passes_label` defined the maximum number of passes to run on objects to pin point what exactly is different. This is only used when ignore_order=True

log_frequency_in_sec: Integer, default = 0
    :ref:`log_frequency_in_sec_label`
    How often to log the progress. The default of 0 means logging progress is disabled.
    If you set it to 20, it will log every 20 seconds. This is useful only when running DeepDiff
    on massive objects that will take a while to run. If you are only dealing with small objects, keep it at 0 to disable progress logging.

progress_logger: log function, default = logger.warning
    What logging function to use specifically for progress reporting. This function is only used when progress logging is enabled
    by setting log_frequency_in_sec to anything above zero. The function that is passed needs to be thread safe.
    The reason that the default is logger.warning and not logger.info is that the logging is done via a separate thread and
    somehow the info logs get muted by default.


**Returns**

    A DeepDiff object that has already calculated the difference of the 2 items. The format of the object is chosen by the view parameter.

**Supported data types**

int, string, unicode, dictionary, list, tuple, set, frozenset, OrderedDict, NamedTuple, Numpy, custom objects and more!
