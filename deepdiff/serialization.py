import pickle
import sys
import io
import builtins  # NOQA
import datetime  # NOQA
import decimal  # NOQA
import ordered_set  # NOQA
import collections  # NOQA
from struct import unpack

MAX_HEADER_LENGTH = 256

MODULE_NOT_FOUND_MSG = 'DeepDiff Delta did not find {} in your modules. Please make sure it is already imported.'
FORBIDDEN_MODULE_MSG = "Module '{}' is forbidden. You need to explicitly pass it by passing a safe_to_import parameter"
BASIC_HEADER = b"DeepDiff Delta Payload v0-0-1"

SAFE_TO_IMPORT = {
    'builtins.range',
    'builtins.complex',
    'builtins.set',
    'builtins.frozenset',
    'builtins.slice',
    'builtins.str',
    'builtins.bytes',
    'builtins.list',
    'builtins.tuple',
    'builtins.int',
    'builtins.float',
    'builtins.dict',
    'builtins.bool',
    'builtins.bin',
    'builtins.None',
    'datetime.datetime',
    'datetime.time',
    'datetime.timedelta',
    'decimal.Decimal',
    'ordered_set.OrderedSet',
    'collections.namedtuple',
}


class ModuleNotFoundError(ImportError):
    """
    Raised when the module is not found in sys.modules
    """
    pass


class ForbiddenModule(ImportError):
    """
    Raised when a module is not explicitly allowed to be imported
    """
    pass


class _RestrictedUnpickler(pickle.Unpickler):

    def __init__(self, *args, **kwargs):
        self.safe_to_import = kwargs.pop('safe_to_import', None)
        if self.safe_to_import:
            self.safe_to_import = set(self.safe_to_import) | SAFE_TO_IMPORT
        else:
            self.safe_to_import = SAFE_TO_IMPORT
        super().__init__(*args, **kwargs)

    def find_class(self, module, name):
        # Only allow safe classes from self.safe_to_import.
        module_dot_class = '{}.{}'.format(module, name)
        if module_dot_class in self.safe_to_import:
            try:
                module_obj = sys.modules[module]
            except KeyError:
                raise ModuleNotFoundError(MODULE_NOT_FOUND_MSG.format(module)) from None
            return getattr(module_obj, name)
        # Forbid everything else.
        raise ForbiddenModule(FORBIDDEN_MODULE_MSG.format(module, name)) from None


def pickle_dump(obj, header=BASIC_HEADER):
    if isinstance(header, str):
        header = header.encode('utf-8')
    # We expect at least python 3.5 so protocol 4 is good.
    return header + b'\n' + pickle.dumps(obj, protocol=4, fix_imports=False)


def basic_header_checker(header, content):
    """
    This is a basic header checker.
    In future it will have more sophisticated header checkers.
    Perhaps something to check the signature of the delta.
    """
    assert header == BASIC_HEADER, "Delta payload header can not be verified. Aborting."


def pickle_load(content, header_checher=basic_header_checker):
    max_header_to_unpack = '{}c'.format(min(MAX_HEADER_LENGTH, len(content)))
    top_of_content = unpack(max_header_to_unpack, content)
    break_index = top_of_content.index(b'\n')
    header = content[: break_index]
    content = content[break_index + 1:]
    if header_checher:
        header_checher(header, content)
    return _RestrictedUnpickler(io.BytesIO(content)).load()
