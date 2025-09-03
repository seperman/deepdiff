import os
import pickle
import pytest
from deepdiff import Delta
from deepdiff.helper import Opcode
from deepdiff.serialization import ForbiddenModule


class TestDeltaClassPollution:

    def test_builtins_int(self):

        pollute_int = pickle.dumps(
            {
                "values_changed": {"root['tmp']": {"new_value": Opcode("", 0, 0, 0, 0)}},
                "dictionary_item_added": {
                    (
                        ("root", "GETATTR"),
                        ("tmp", "GET"),
                        ("__repr__", "GETATTR"),
                        ("__globals__", "GETATTR"),
                        ("__builtins__", "GET"),
                        ("int", "GET"),
                    ): "no longer a class"
                },
            }
        )

        assert isinstance(pollute_int, bytes)

        # ------------[ Exploit ]------------
        # This could be some example, vulnerable, application.
        # The inputs above could be sent via HTTP, for example.


        # Existing dictionary; it is assumed that it contains
        # at least one entry, otherwise a different Delta needs to be
        # applied first, adding an entry to the dictionary.
        mydict = {"tmp": "foobar"}

        # Before pollution
        assert 42 == int("41") + 1

        # Apply Delta to mydict
        result = mydict + Delta(pollute_int)

        assert 1337 == int("1337")

    def test_remote_code_execution(self):
        if os.path.exists('/tmp/pwned'):
            os.remove('/tmp/pwned')

        pollute_safe_to_import = pickle.dumps(
            {
                "values_changed": {"root['tmp']": {"new_value": Opcode("", 0, 0, 0, 0)}},
                "set_item_added": {
                    (
                        ("root", "GETATTR"),
                        ("tmp", "GET"),
                        ("__repr__", "GETATTR"),
                        ("__globals__", "GETATTR"),
                        ("sys", "GET"),
                        ("modules", "GETATTR"),
                        ("deepdiff.serialization", "GET"),
                        ("SAFE_TO_IMPORT", "GETATTR"),
                    ): set(["posix.system"])
                },
            }
        )

        # From https://davidhamann.de/2020/04/05/exploiting-python-pickle/
        class RCE:
            def __reduce__(self):
                cmd = "id > /tmp/pwned"
                return os.system, (cmd,)

        # Wrap object with dictionary so that Delta does not crash
        rce_pickle = pickle.dumps({"_": RCE()})

        assert isinstance(pollute_safe_to_import, bytes)
        assert isinstance(rce_pickle, bytes)

        # ------------[ Exploit ]------------
        # This could be some example, vulnerable, application.
        # The inputs above could be sent via HTTP, for example.

        # Existing dictionary; it is assumed that it contains
        # at least one entry, otherwise a different Delta needs to be
        # applied first, adding an entry to the dictionary.
        mydict = {"tmp": "foobar"}

        # Apply Delta to mydict
        with pytest.raises(ValueError) as exc_info:
            mydict + Delta(pollute_safe_to_import)
        assert "traversing dunder attributes is not allowed" == str(exc_info.value)

        with pytest.raises(ForbiddenModule) as exc_info:
            Delta(rce_pickle)  # no need to apply this Delta
        assert "Module 'posix.system' is forbidden. You need to explicitly pass it by passing a safe_to_import parameter" == str(exc_info.value)

        assert not os.path.exists('/tmp/pwned'), "We should not have created this file"

    def test_delta_should_not_access_globals(self):

        pollute_global = pickle.dumps(
            {
                "dictionary_item_added": {
                    (
                        ("root", "GETATTR"),
                        ("myfunc", "GETATTR"),
                        ("__globals__", "GETATTR"),
                        ("PWNED", "GET"),
                    ): 1337
                }
            }
        )


        # demo application
        class Foo:
            def __init__(self):
                pass

            def myfunc(self):
                pass


        PWNED = False
        delta = Delta(pollute_global)
        assert PWNED is False
        b = Foo() + delta

        assert PWNED is False
