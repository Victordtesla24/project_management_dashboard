import datetime
import re
import sys
import typing
import unittest
from io import StringIO
from typing import cast

import pytest
import tornado
from tornado.escape import utf8
from tornado.util import (
    ArgReplacer,
    Configurable,
    exec_in,
    import_object,
    is_finalizing,
    raise_exc_info,
    re_unescape,
    timedelta_to_seconds,
)

if typing.TYPE_CHECKING:
    from typing import Any, Dict  # noqa: F401


class RaiseExcInfoTest(unittest.TestCase):
    def test_two_arg_exception(self):
        # This test would fail on python 3 if raise_exc_info were simply
        # a three-argument raise statement, because TwoArgException
        # doesn't have a "copy constructor"
        class TwoArgException(Exception):
            def __init__(self, a, b) -> None:
                super().__init__()
                self.a, self.b = a, b

        try:
            raise TwoArgException(1, 2)
        except TwoArgException:
            exc_info = sys.exc_info()
        try:
            raise_exc_info(exc_info)
            self.fail("didn't get expected exception")
        except TwoArgException as e:
            assert e is exc_info[1]


class TestConfigurable(Configurable):
    @classmethod
    def configurable_base(cls):
        return TestConfigurable

    @classmethod
    def configurable_default(cls):
        return TestConfig1


class TestConfig1(TestConfigurable):
    def initialize(self, pos_arg=None, a=None):
        self.a = a
        self.pos_arg = pos_arg


class TestConfig2(TestConfigurable):
    def initialize(self, pos_arg=None, b=None):
        self.b = b
        self.pos_arg = pos_arg


class TestConfig3(TestConfigurable):
    # TestConfig3 is a configuration option that is itself configurable.
    @classmethod
    def configurable_base(cls):
        return TestConfig3

    @classmethod
    def configurable_default(cls):
        return TestConfig3A


class TestConfig3A(TestConfig3):
    def initialize(self, a=None):
        self.a = a


class TestConfig3B(TestConfig3):
    def initialize(self, b=None):
        self.b = b


class ConfigurableTest(unittest.TestCase):
    def setUp(self):
        self.saved = TestConfigurable._save_configuration()
        self.saved3 = TestConfig3._save_configuration()

    def tearDown(self):
        TestConfigurable._restore_configuration(self.saved)
        TestConfig3._restore_configuration(self.saved3)

    def checkSubclasses(self):
        # no matter how the class is configured, it should always be
        # possible to instantiate the subclasses directly
        assert isinstance(TestConfig1(), TestConfig1)
        assert isinstance(TestConfig2(), TestConfig2)

        obj = TestConfig1(a=1)
        assert obj.a == 1
        obj2 = TestConfig2(b=2)
        assert obj2.b == 2

    def test_default(self):
        # In these tests we combine a typing.cast to satisfy mypy with
        # a runtime type-assertion. Without the cast, mypy would only
        # let us access attributes of the base class.
        obj = cast(TestConfig1, TestConfigurable())
        assert isinstance(obj, TestConfig1)
        assert obj.a is None

        obj = cast(TestConfig1, TestConfigurable(a=1))
        assert isinstance(obj, TestConfig1)
        assert obj.a == 1

        self.checkSubclasses()

    def test_config_class(self):
        TestConfigurable.configure(TestConfig2)
        obj = cast(TestConfig2, TestConfigurable())
        assert isinstance(obj, TestConfig2)
        assert obj.b is None

        obj = cast(TestConfig2, TestConfigurable(b=2))
        assert isinstance(obj, TestConfig2)
        assert obj.b == 2

        self.checkSubclasses()

    def test_config_str(self):
        TestConfigurable.configure("tornado.test.util_test.TestConfig2")
        obj = cast(TestConfig2, TestConfigurable())
        assert isinstance(obj, TestConfig2)
        assert obj.b is None

        obj = cast(TestConfig2, TestConfigurable(b=2))
        assert isinstance(obj, TestConfig2)
        assert obj.b == 2

        self.checkSubclasses()

    def test_config_args(self):
        TestConfigurable.configure(None, a=3)
        obj = cast(TestConfig1, TestConfigurable())
        assert isinstance(obj, TestConfig1)
        assert obj.a == 3

        obj = cast(TestConfig1, TestConfigurable(42, a=4))
        assert isinstance(obj, TestConfig1)
        assert obj.a == 4
        assert obj.pos_arg == 42

        self.checkSubclasses()
        # args bound in configure don't apply when using the subclass directly
        obj = TestConfig1()
        assert obj.a is None

    def test_config_class_args(self):
        TestConfigurable.configure(TestConfig2, b=5)
        obj = cast(TestConfig2, TestConfigurable())
        assert isinstance(obj, TestConfig2)
        assert obj.b == 5

        obj = cast(TestConfig2, TestConfigurable(42, b=6))
        assert isinstance(obj, TestConfig2)
        assert obj.b == 6
        assert obj.pos_arg == 42

        self.checkSubclasses()
        # args bound in configure don't apply when using the subclass directly
        obj = TestConfig2()
        assert obj.b is None

    def test_config_multi_level(self):
        TestConfigurable.configure(TestConfig3, a=1)
        obj = cast(TestConfig3A, TestConfigurable())
        assert isinstance(obj, TestConfig3A)
        assert obj.a == 1

        TestConfigurable.configure(TestConfig3)
        TestConfig3.configure(TestConfig3B, b=2)
        obj2 = cast(TestConfig3B, TestConfigurable())
        assert isinstance(obj2, TestConfig3B)
        assert obj2.b == 2

    def test_config_inner_level(self):
        # The inner level can be used even when the outer level
        # doesn't point to it.
        obj = TestConfig3()
        assert isinstance(obj, TestConfig3A)

        TestConfig3.configure(TestConfig3B)
        obj = TestConfig3()
        assert isinstance(obj, TestConfig3B)

        # Configuring the base doesn't configure the inner.
        obj2 = TestConfigurable()
        assert isinstance(obj2, TestConfig1)
        TestConfigurable.configure(TestConfig2)

        obj3 = TestConfigurable()
        assert isinstance(obj3, TestConfig2)

        obj = TestConfig3()
        assert isinstance(obj, TestConfig3B)


class UnicodeLiteralTest(unittest.TestCase):
    def test_unicode_escapes(self):
        assert utf8("é") == b"\xc3\xa9"


class ExecInTest(unittest.TestCase):
    # TODO(bdarnell): make a version of this test for one of the new
    # future imports available in python 3.
    @unittest.skip("no testable future imports")
    def test_no_inherit_future(self):
        # This file has from __future__ import print_function...
        f = StringIO()
        print("hello", file=f)
        # ...but the template doesn't
        exec_in('print >> f, "world"', {"f": f})
        assert f.getvalue() == "hello\nworld\n"


class ArgReplacerTest(unittest.TestCase):
    def setUp(self):
        def function(x, y, callback=None, z=None):
            pass

        self.replacer = ArgReplacer(function, "callback")

    def test_omitted(self):
        args = (1, 2)
        kwargs = {}  # type: Dict[str, Any]
        assert self.replacer.get_old_value(args, kwargs) is None
        assert self.replacer.replace("new", args, kwargs) == (None, (1, 2), {"callback": "new"})

    def test_position(self):
        args = (1, 2, "old", 3)
        kwargs = {}  # type: Dict[str, Any]
        assert self.replacer.get_old_value(args, kwargs) == "old"
        assert self.replacer.replace("new", args, kwargs) == ("old", [1, 2, "new", 3], {})

    def test_keyword(self):
        args = (1,)
        kwargs = {"y": 2, "callback": "old", "z": 3}
        assert self.replacer.get_old_value(args, kwargs) == "old"
        assert self.replacer.replace("new", args, kwargs) == (
            "old",
            (1,),
            {"y": 2, "callback": "new", "z": 3},
        )


class TimedeltaToSecondsTest(unittest.TestCase):
    def test_timedelta_to_seconds(self):
        time_delta = datetime.timedelta(hours=1)
        assert timedelta_to_seconds(time_delta) == 3600.0


class ImportObjectTest(unittest.TestCase):
    def test_import_member(self):
        assert import_object("tornado.escape.utf8") is utf8

    def test_import_member_unicode(self):
        assert import_object("tornado.escape.utf8") is utf8

    def test_import_module(self):
        assert import_object("tornado.escape") is tornado.escape

    def test_import_module_unicode(self):
        # The internal implementation of __import__ differs depending on
        # whether the thing being imported is a module or not.
        # This variant requires a byte string in python 2.
        assert import_object("tornado.escape") is tornado.escape


class ReUnescapeTest(unittest.TestCase):
    def test_re_unescape(self):
        test_strings = ("/favicon.ico", "index.html", "Hello, World!", "!$@#%;")
        for string in test_strings:
            assert string == re_unescape(re.escape(string))

    def test_re_unescape_raises_error_on_invalid_input(self):
        with pytest.raises(ValueError):
            re_unescape("\\d")
        with pytest.raises(ValueError):
            re_unescape("\\b")
        with pytest.raises(ValueError):
            re_unescape("\\Z")


class IsFinalizingTest(unittest.TestCase):
    def test_basic(self):
        assert not is_finalizing()
