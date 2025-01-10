import datetime
import os
import sys
import typing
import unittest
from io import StringIO
from unittest import mock

import pytest
from tornado.options import Error, OptionParser
from tornado.test.util import subTest
from tornado.util import basestring_type

if typing.TYPE_CHECKING:
    from typing import List  # noqa: F401


class Email:
    def __init__(self, value) -> None:
        if isinstance(value, str) and "@" in value:
            self._value = value
        else:
            raise ValueError

    @property
    def value(self):
        return self._value


class OptionsTest(unittest.TestCase):
    def test_parse_command_line(self):
        options = OptionParser()
        options.define("port", default=80)
        options.parse_command_line(["main.py", "--port=443"])
        assert options.port == 443

    def test_parse_config_file(self):
        options = OptionParser()
        options.define("port", default=80)
        options.define("username", default="foo")
        options.define("my_path")
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "options_test.cfg")
        options.parse_config_file(config_path)
        assert options.port == 443
        assert options.username == "李康"
        assert options.my_path == config_path

    def test_parse_callbacks(self):
        options = OptionParser()
        self.called = False

        def callback():
            self.called = True

        options.add_parse_callback(callback)

        # non-final parse doesn't run callbacks
        options.parse_command_line(["main.py"], final=False)
        assert not self.called

        # final parse does
        options.parse_command_line(["main.py"])
        assert self.called

        # callbacks can be run more than once on the same options
        # object if there are multiple final parses
        self.called = False
        options.parse_command_line(["main.py"])
        assert self.called

    def test_help(self):
        options = OptionParser()
        try:
            orig_stderr = sys.stderr
            sys.stderr = StringIO()
            with pytest.raises(SystemExit):
                options.parse_command_line(["main.py", "--help"])
            usage = sys.stderr.getvalue()
        finally:
            sys.stderr = orig_stderr
        assert "Usage:" in usage

    def test_subcommand(self):
        base_options = OptionParser()
        base_options.define("verbose", default=False)
        sub_options = OptionParser()
        sub_options.define("foo", type=str)
        rest = base_options.parse_command_line(["main.py", "--verbose", "subcommand", "--foo=bar"])
        assert rest == ["subcommand", "--foo=bar"]
        assert base_options.verbose
        rest2 = sub_options.parse_command_line(rest)
        assert rest2 == []
        assert sub_options.foo == "bar"

        # the two option sets are distinct
        try:
            orig_stderr = sys.stderr
            sys.stderr = StringIO()
            with pytest.raises(Error):
                sub_options.parse_command_line(["subcommand", "--verbose"])
        finally:
            sys.stderr = orig_stderr

    def test_setattr(self):
        options = OptionParser()
        options.define("foo", default=1, type=int)
        options.foo = 2
        assert options.foo == 2

    def test_setattr_type_check(self):
        # setattr requires that options be the right type and doesn't
        # parse from string formats.
        options = OptionParser()
        options.define("foo", default=1, type=int)
        with pytest.raises(Error):
            options.foo = "2"

    def test_setattr_with_callback(self):
        values = []  # type: List[int]
        options = OptionParser()
        options.define("foo", default=1, type=int, callback=values.append)
        options.foo = 2
        assert values == [2]

    def _sample_options(self):
        options = OptionParser()
        options.define("a", default=1)
        options.define("b", default=2)
        return options

    def test_iter(self):
        options = self._sample_options()
        # OptionParsers always define 'help'.
        assert {"a", "b", "help"} == set(iter(options))

    def test_getitem(self):
        options = self._sample_options()
        assert options["a"] == 1

    def test_setitem(self):
        options = OptionParser()
        options.define("foo", default=1, type=int)
        options["foo"] = 2
        assert options["foo"] == 2

    def test_items(self):
        options = self._sample_options()
        # OptionParsers always define 'help'.
        expected = [("a", 1), ("b", 2), ("help", options.help)]
        actual = sorted(options.items())
        assert expected == actual

    def test_as_dict(self):
        options = self._sample_options()
        expected = {"a": 1, "b": 2, "help": options.help}
        assert expected == options.as_dict()

    def test_group_dict(self):
        options = OptionParser()
        options.define("a", default=1)
        options.define("b", group="b_group", default=2)

        frame = sys._getframe(0)
        this_file = frame.f_code.co_filename
        assert {"b_group", "", this_file} == options.groups()

        b_group_dict = options.group_dict("b_group")
        assert {"b": 2} == b_group_dict

        assert {} == options.group_dict("nonexistent")

    def test_mock_patch(self):
        # ensure that our setattr hooks don't interfere with mock.patch
        options = OptionParser()
        options.define("foo", default=1)
        options.parse_command_line(["main.py", "--foo=2"])
        assert options.foo == 2

        with mock.patch.object(options.mockable(), "foo", 3):
            assert options.foo == 3
        assert options.foo == 2

        # Try nested patches mixed with explicit sets
        with mock.patch.object(options.mockable(), "foo", 4):
            assert options.foo == 4
            options.foo = 5
            assert options.foo == 5
            with mock.patch.object(options.mockable(), "foo", 6):
                assert options.foo == 6
            assert options.foo == 5
        assert options.foo == 2

    def _define_options(self):
        options = OptionParser()
        options.define("str", type=str)
        options.define("basestring", type=basestring_type)
        options.define("int", type=int)
        options.define("float", type=float)
        options.define("datetime", type=datetime.datetime)
        options.define("timedelta", type=datetime.timedelta)
        options.define("email", type=Email)
        options.define("list-of-int", type=int, multiple=True)
        options.define("list-of-str", type=str, multiple=True)
        return options

    def _check_options_values(self, options):
        assert options.str == "asdf"
        assert options.basestring == "qwer"
        assert options.int == 42
        assert options.float == 1.5
        assert options.datetime == datetime.datetime(2013, 4, 28, 5, 16)
        assert options.timedelta == datetime.timedelta(seconds=45)
        assert options.email.value == "tornado@web.com"
        assert isinstance(options.email, Email)
        assert options.list_of_int == [1, 2, 3]
        assert options.list_of_str == ["a", "b", "c"]

    def test_types(self):
        options = self._define_options()
        options.parse_command_line(
            [
                "main.py",
                "--str=asdf",
                "--basestring=qwer",
                "--int=42",
                "--float=1.5",
                "--datetime=2013-04-28 05:16",
                "--timedelta=45s",
                "--email=tornado@web.com",
                "--list-of-int=1,2,3",
                "--list-of-str=a,b,c",
            ],
        )
        self._check_options_values(options)

    def test_types_with_conf_file(self):
        for config_file_name in (
            "options_test_types.cfg",
            "options_test_types_str.cfg",
        ):
            options = self._define_options()
            options.parse_config_file(os.path.join(os.path.dirname(__file__), config_file_name))
            self._check_options_values(options)

    def test_multiple_string(self):
        options = OptionParser()
        options.define("foo", type=str, multiple=True)
        options.parse_command_line(["main.py", "--foo=a,b,c"])
        assert options.foo == ["a", "b", "c"]

    def test_multiple_int(self):
        options = OptionParser()
        options.define("foo", type=int, multiple=True)
        options.parse_command_line(["main.py", "--foo=1,3,5:7"])
        assert options.foo == [1, 3, 5, 6, 7]

    def test_error_redefine(self):
        options = OptionParser()
        options.define("foo")
        with pytest.raises(Error) as cm:
            options.define("foo")
        assert re.search("Option.*foo.*already defined", str(cm.exception))

    def test_error_redefine_underscore(self):
        # Ensure that the dash/underscore normalization doesn't
        # interfere with the redefinition error.
        tests = [
            ("foo-bar", "foo-bar"),
            ("foo_bar", "foo_bar"),
            ("foo-bar", "foo_bar"),
            ("foo_bar", "foo-bar"),
        ]
        for a, b in tests:
            with subTest(self, a=a, b=b):
                options = OptionParser()
                options.define(a)
                with pytest.raises(Error) as cm:
                    options.define(b)
                assert re.search("Option.*foo.bar.*already defined", str(cm.exception))

    def test_dash_underscore_cli(self):
        # Dashes and underscores should be interchangeable.
        for defined_name in ["foo-bar", "foo_bar"]:
            for flag in ["--foo-bar=a", "--foo_bar=a"]:
                options = OptionParser()
                options.define(defined_name)
                options.parse_command_line(["main.py", flag])
                # Attr-style access always uses underscores.
                assert options.foo_bar == "a"
                # Dict-style access allows both.
                assert options["foo-bar"] == "a"
                assert options["foo_bar"] == "a"

    def test_dash_underscore_file(self):
        # No matter how an option was defined, it can be set with underscores
        # in a config file.
        for defined_name in ["foo-bar", "foo_bar"]:
            options = OptionParser()
            options.define(defined_name)
            options.parse_config_file(os.path.join(os.path.dirname(__file__), "options_test.cfg"))
            assert options.foo_bar == "a"

    def test_dash_underscore_introspection(self):
        # Original names are preserved in introspection APIs.
        options = OptionParser()
        options.define("with-dash", group="g")
        options.define("with_underscore", group="g")
        all_options = ["help", "with-dash", "with_underscore"]
        assert sorted(options) == all_options
        assert sorted(k for k, v in options.items()) == all_options
        assert sorted(options.as_dict().keys()) == all_options

        assert sorted(options.group_dict("g")) == ["with-dash", "with_underscore"]

        # --help shows CLI-style names with dashes.
        buf = StringIO()
        options.print_help(buf)
        assert "--with-dash" in buf.getvalue()
        assert "--with-underscore" in buf.getvalue()
