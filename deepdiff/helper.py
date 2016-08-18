import sys

py_major_version = sys.version[0]
py_minor_version = sys.version[2]

py3 = py_major_version == '3'

if (py_major_version, py_minor_version) == (2.6):  # pragma: no cover
    sys.exit('Python 2.6 is not supported.')
