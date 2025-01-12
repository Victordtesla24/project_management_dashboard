#!/usr/bin/env python
"""Test suite for autoflake."""
from __future__ import annotations

import contextlib
import functools
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from typing import Any, Iterator, Mapping, Sequence

import autoflake

ROOT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


AUTOFLAKE_COMMAND = [
    sys.executable,
    "-m",
    "autoflake",
]


def normalize_line_endings(text: str) -> str:
    """Normalize line endings to match the system default."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


class UnitTests(unittest.TestCase):
    """Unit tests."""

    def test_imports(self) -> None:
        assert len(autoflake.SAFE_IMPORTS) > 0

    def test_unused_import_line_numbers(self) -> None:
        assert [1] == list(autoflake.unused_import_line_numbers(autoflake.check("import os\n")))

    def test_unused_import_line_numbers_with_from(self) -> None:
        assert [1] == list(
            autoflake.unused_import_line_numbers(autoflake.check("from os import path\n")),
        )

    def test_unused_import_line_numbers_with_dot(self) -> None:
        assert [1] == list(
            autoflake.unused_import_line_numbers(autoflake.check("import os.path\n")),
        )

    def test_extract_package_name(self) -> None:
        assert autoflake.extract_package_name("import os") == "os"
        assert autoflake.extract_package_name("from os import path") == "os"
        assert autoflake.extract_package_name("import os.path") == "os"

    def test_extract_package_name_should_ignore_doctest_for_now(self) -> None:
        assert not autoflake.extract_package_name(">>> import os")

    def test_standard_package_names(self) -> None:
        assert "os" in list(autoflake.standard_package_names())
        assert "subprocess" in list(autoflake.standard_package_names())
        assert "urllib" in list(autoflake.standard_package_names())

        assert "autoflake" not in list(autoflake.standard_package_names())
        assert "pep8" not in list(autoflake.standard_package_names())

    def test_get_line_ending(self) -> None:
        assert autoflake.get_line_ending("\n") == "\n"
        assert autoflake.get_line_ending("abc\n") == "\n"
        assert autoflake.get_line_ending("abc\t  \t\n") == "\t  \t\n"

        assert autoflake.get_line_ending("abc") == ""
        assert autoflake.get_line_ending("") == ""

    def test_get_indentation(self) -> None:
        assert autoflake.get_indentation("") == ""
        assert autoflake.get_indentation("    abc") == "    "
        assert autoflake.get_indentation("    abc  \n\t") == "    "
        assert autoflake.get_indentation("\tabc  \n\t") == "\t"
        assert autoflake.get_indentation(" \t abc  \n\t") == " \t "
        assert autoflake.get_indentation("    ") == ""

    def test_filter_star_import(self) -> None:
        assert autoflake.filter_star_import("from math import *", ["cos"]) == "from math import cos"

        assert (
            autoflake.filter_star_import("from math import *", ["sin", "cos"])
            == "from math import cos, sin"
        )

    def test_filter_unused_variable(self) -> None:
        assert autoflake.filter_unused_variable("x = foo()") == "foo()"

        assert autoflake.filter_unused_variable("    x = foo()") == "    foo()"

    def test_filter_unused_variable_with_literal_or_name(self) -> None:
        assert autoflake.filter_unused_variable("x = 1") == "pass"

        assert autoflake.filter_unused_variable("x = y") == "pass"

        assert autoflake.filter_unused_variable("x = {}") == "pass"

    def test_filter_unused_variable_with_basic_data_structures(self) -> None:
        assert autoflake.filter_unused_variable("x = dict()") == "pass"

        assert autoflake.filter_unused_variable("x = list()") == "pass"

        assert autoflake.filter_unused_variable("x = set()") == "pass"

    def test_filter_unused_variable_should_ignore_multiline(self) -> None:
        assert autoflake.filter_unused_variable("x = foo()\\") == "x = foo()\\"

    def test_filter_unused_variable_should_multiple_assignments(self) -> None:
        assert autoflake.filter_unused_variable("x = y = foo()") == "x = y = foo()"

    def test_filter_unused_variable_with_exception(self) -> None:
        assert (
            autoflake.filter_unused_variable("except Exception as exception:")
            == "except Exception:"
        )

        assert (
            autoflake.filter_unused_variable("except (ImportError, ValueError) as foo:")
            == "except (ImportError, ValueError):"
        )

    def test_filter_unused_variable_drop_rhs(self) -> None:
        assert autoflake.filter_unused_variable("x = foo()", drop_rhs=True) == ""

        assert autoflake.filter_unused_variable("    x = foo()", drop_rhs=True) == ""

    def test_filter_unused_variable_with_literal_or_name_drop_rhs(self) -> None:
        assert autoflake.filter_unused_variable("x = 1", drop_rhs=True) == "pass"

        assert autoflake.filter_unused_variable("x = y", drop_rhs=True) == "pass"

        assert autoflake.filter_unused_variable("x = {}", drop_rhs=True) == "pass"

    def test_filter_unused_variable_with_basic_data_structures_drop_rhs(self) -> None:
        assert autoflake.filter_unused_variable("x = dict()", drop_rhs=True) == "pass"

        assert autoflake.filter_unused_variable("x = list()", drop_rhs=True) == "pass"

        assert autoflake.filter_unused_variable("x = set()", drop_rhs=True) == "pass"

    def test_filter_unused_variable_should_ignore_multiline_drop_rhs(self) -> None:
        assert autoflake.filter_unused_variable("x = foo()\\", drop_rhs=True) == "x = foo()\\"

    def test_filter_unused_variable_should_multiple_assignments_drop_rhs(self) -> None:
        assert autoflake.filter_unused_variable("x = y = foo()", drop_rhs=True) == "x = y = foo()"

    def test_filter_unused_variable_with_exception_drop_rhs(self) -> None:
        assert (
            autoflake.filter_unused_variable("except Exception as exception:", drop_rhs=True)
            == "except Exception:"
        )

        assert (
            autoflake.filter_unused_variable(
                "except (ImportError, ValueError) as foo:",
                drop_rhs=True,
            )
            == "except (ImportError, ValueError):"
        )

    def test_filter_code(self) -> None:
        assert (
            "".join(autoflake.filter_code("import os\nimport re\nos.foo()\n"))
            == "import os\npass\nos.foo()\n"
        )

    def test_filter_code_with_indented_import(self) -> None:
        assert (
            "".join(autoflake.filter_code("import os\nif True:\n    import re\nos.foo()\n"))
            == "import os\nif True:\n    pass\nos.foo()\n"
        )

    def test_filter_code_with_from(self) -> None:
        assert "".join(autoflake.filter_code("from os import path\nx = 1\n")) == "pass\nx = 1\n"

    def test_filter_code_with_not_from(self) -> None:
        assert (
            "".join(
                autoflake.filter_code("import frommer\nx = 1\n", remove_all_unused_imports=True),
            )
            == "pass\nx = 1\n"
        )

    def test_filter_code_with_used_from(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "import frommer\nprint(frommer)\n",
                    remove_all_unused_imports=True,
                ),
            )
            == "import frommer\nprint(frommer)\n"
        )

    def test_filter_code_with_ambiguous_from(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "from frommer import abc, frommer, xyz\n",
                    remove_all_unused_imports=True,
                ),
            )
            == "pass\n"
        )

    def test_filter_code_should_avoid_inline_except(self) -> None:
        line = """\
try: from zap import foo
except: from zap import bar
"""
        assert line == "".join(autoflake.filter_code(line, remove_all_unused_imports=True))

    def test_filter_code_should_avoid_escaped_newlines(self) -> None:
        line = """\
try:\\
from zap import foo
except:\\
from zap import bar
"""
        assert line == "".join(autoflake.filter_code(line, remove_all_unused_imports=True))

    def test_filter_code_with_remove_all_unused_imports(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "import foo\nimport zap\nx = 1\n",
                    remove_all_unused_imports=True,
                ),
            )
            == "pass\npass\nx = 1\n"
        )

    def test_filter_code_with_additional_imports(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "import foo\nimport zap\nx = 1\n",
                    additional_imports=["foo", "bar"],
                ),
            )
            == "pass\nimport zap\nx = 1\n"
        )

    def test_filter_code_should_ignore_imports_with_inline_comment(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "from os import path  # foo\nfrom os import path\nfrom fake_foo import z  # foo, foo, zap\nx = 1\n",
                ),
            )
            == "from os import path  # foo\npass\nfrom fake_foo import z  # foo, foo, zap\nx = 1\n"
        )

    def test_filter_code_should_respect_noqa(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "from os import path\nimport re  # noqa\nfrom subprocess import Popen  # NOQA\nx = 1\n",
                ),
            )
            == "pass\nimport re  # noqa\nfrom subprocess import Popen  # NOQA\nx = 1\n"
        )

    def test_filter_code_expand_star_imports(self) -> None:
        assert (
            "".join(autoflake.filter_code("from math import *\nsin(1)\n", expand_star_imports=True))
            == "from math import sin\nsin(1)\n"
        )

        assert (
            "".join(
                autoflake.filter_code(
                    "from math import *\nsin(1)\ncos(1)\n",
                    expand_star_imports=True,
                ),
            )
            == "from math import cos, sin\nsin(1)\ncos(1)\n"
        )

    def test_filter_code_ignore_multiple_star_import(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "from math import *\nfrom re import *\nsin(1)\ncos(1)\n",
                    expand_star_imports=True,
                ),
            )
            == "from math import *\nfrom re import *\nsin(1)\ncos(1)\n"
        )

    def test_filter_code_with_special_re_symbols_in_key(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "a = {\n  '????': 3,\n  '????': 2,\n}\nprint(a)\n",
                    remove_duplicate_keys=True,
                ),
            )
            == "a = {\n  '????': 2,\n}\nprint(a)\n"
        )

    def test_multiline_import(self) -> None:
        assert autoflake.multiline_import("\\\nimport os, \\\n    math, subprocess\n")

        assert not autoflake.multiline_import("import os, math, subprocess\n")

        assert autoflake.multiline_import("import os, math, subprocess\n", previous_line="if: \\\n")

        assert autoflake.multiline_import("from os import (path, sep)")

    def test_multiline_statement(self) -> None:
        assert not autoflake.multiline_statement("x = foo()")

        assert autoflake.multiline_statement("x = 1;")
        assert autoflake.multiline_statement("import os, \\")
        assert autoflake.multiline_statement("foo(")
        assert autoflake.multiline_statement("1", previous_line="x = \\")

    def test_break_up_import(self) -> None:
        assert (
            autoflake.break_up_import("import abc, subprocess, math\n")
            == "import abc\nimport subprocess\nimport math\n"
        )

    def test_break_up_import_with_indentation(self) -> None:
        assert (
            autoflake.break_up_import("    import abc, subprocess, math\n")
            == "    import abc\n    import subprocess\n    import math\n"
        )

    def test_break_up_import_should_do_nothing_on_no_line_ending(self) -> None:
        assert (
            autoflake.break_up_import("import abc, subprocess, math")
            == "import abc, subprocess, math"
        )

    def test_filter_from_import_no_remove(self) -> None:
        assert (
            autoflake.filter_from_import(
                "    from foo import abc, subprocess, math\n",
                unused_module=[],
            )
            == "    from foo import abc, subprocess, math\n"
        )

    def test_filter_from_import_remove_module(self) -> None:
        assert (
            autoflake.filter_from_import(
                "    from foo import abc, subprocess, math\n",
                unused_module=["foo.abc"],
            )
            == "    from foo import subprocess, math\n"
        )

    def test_filter_from_import_remove_all(self) -> None:
        assert (
            autoflake.filter_from_import(
                "    from foo import abc, subprocess, math\n",
                unused_module=["foo.abc", "foo.subprocess", "foo.math"],
            )
            == "    pass\n"
        )

    def test_filter_code_multiline_imports(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "\\\nimport os\nimport re\nimport os, \\\n    math, subprocess\nos.foo()\n",
                ),
            )
            == "\\\nimport os\npass\nimport os\nos.foo()\n"
        )

    def test_filter_code_multiline_from_imports(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "\\\nimport os\nimport re\nfrom os.path import (\n    exists,\n    join,\n)\njoin('a', 'b')\nfrom os.path import \\\n    abspath, basename, \\\n    commonpath\nos.foo()\nfrom os.path import \\\n    isfile \\\n    , isdir\nisdir('42')\n",
                ),
            )
            == "\\\nimport os\npass\nfrom os.path import (\n    join,\n)\njoin('a', 'b')\npass\nos.foo()\nfrom os.path import \\\n    isdir\nisdir('42')\n"
        )

    def test_filter_code_should_ignore_semicolons(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "\\\nimport os\nimport re\nimport os; import math, subprocess\nos.foo()\n",
                ),
            )
            == "\\\nimport os\npass\nimport os; import math, subprocess\nos.foo()\n"
        )

    def test_filter_code_should_ignore_non_standard_library(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "import os\nimport my_own_module\nimport re\nfrom my_package import another_module\nfrom my_package import subprocess\nfrom my_blah.my_blah_blah import blah\nos.foo()\n",
                ),
            )
            == "import os\nimport my_own_module\npass\nfrom my_package import another_module\nfrom my_package import subprocess\nfrom my_blah.my_blah_blah import blah\nos.foo()\n"
        )

    def test_filter_code_should_ignore_unsafe_imports(self) -> None:
        assert (
            "".join(
                autoflake.filter_code(
                    "import rlcompleter\nimport sys\nimport io\nimport os\nprint(1)\n",
                ),
            )
            == "import rlcompleter\npass\npass\npass\nprint(1)\n"
        )

    def test_filter_code_should_ignore_docstring(self) -> None:
        line = """
def foo() -> None:
    '''
    >>> import math
    '''
"""
        assert line == "".join(autoflake.filter_code(line))

    def test_with_ignore_init_module_imports_flag(self) -> None:
        # Need a temp directory in order to specify file name as __init__.py
        temp_directory = tempfile.mkdtemp(dir=".")
        temp_file = os.path.join(temp_directory, "__init__.py")
        try:
            with open(temp_file, "w") as output:
                output.write("import re\n")

            p = subprocess.Popen(
                [*list(AUTOFLAKE_COMMAND), "--ignore-init-module-imports", temp_file],
                stdout=subprocess.PIPE,
            )
            result = p.communicate()[0].decode("utf-8")

            assert "import re" not in result
        finally:
            shutil.rmtree(temp_directory)

    def test_without_ignore_init_module_imports_flag(self) -> None:
        # Need a temp directory in order to specify file name as __init__.py
        temp_directory = tempfile.mkdtemp(dir=".")
        temp_file = os.path.join(temp_directory, "__init__.py")
        try:
            with open(temp_file, "w") as output:
                output.write("import re\n")

            p = subprocess.Popen(
                [*list(AUTOFLAKE_COMMAND), temp_file],
                stdout=subprocess.PIPE,
            )
            result = p.communicate()[0].decode("utf-8")

            assert "import re" in result
        finally:
            shutil.rmtree(temp_directory)

    def test_fix_code(self) -> None:
        assert (
            autoflake.fix_code(
                "import os\nimport re\nimport abc, math, subprocess\nfrom sys import exit, version\nos.foo()\nmath.pi\nx = version\n",
            )
            == "import os\nimport math\nfrom sys import version\nos.foo()\nmath.pi\nx = version\n"
        )

    def test_fix_code_with_from_and_as(self) -> None:
        assert (
            autoflake.fix_code("from collections import defaultdict, namedtuple as xyz\nxyz\n")
            == "from collections import namedtuple as xyz\nxyz\n"
        )

        assert (
            autoflake.fix_code(
                "from collections import defaultdict as abc, namedtuple as xyz\nxyz\n",
            )
            == "from collections import namedtuple as xyz\nxyz\n"
        )

        assert (
            autoflake.fix_code(
                "from collections import defaultdict as abc, namedtuple\nnamedtuple\n",
            )
            == "from collections import namedtuple\nnamedtuple\n"
        )

        assert (
            autoflake.fix_code("from collections import defaultdict as abc, namedtuple as xyz\n")
            == ""
        )

    def test_fix_code_with_from_with_and_without_remove_all(self) -> None:
        code = """\
from x import a as b, c as d
"""

        assert autoflake.fix_code(code, remove_all_unused_imports=True) == ""

        assert code == autoflake.fix_code(code, remove_all_unused_imports=False)

    def test_fix_code_with_from_and_depth_module(self) -> None:
        assert (
            autoflake.fix_code(
                "from distutils.version import LooseVersion, StrictVersion\nStrictVersion('1.0.0')\n",
                remove_all_unused_imports=True,
            )
            == "from distutils.version import StrictVersion\nStrictVersion('1.0.0')\n"
        )

        assert (
            autoflake.fix_code(
                "from distutils.version import LooseVersion, StrictVersion as version\nversion('1.0.0')\n",
                remove_all_unused_imports=True,
            )
            == "from distutils.version import StrictVersion as version\nversion('1.0.0')\n"
        )

    def test_fix_code_with_indented_from(self) -> None:
        assert (
            autoflake.fix_code(
                "def z() -> None:\n    from ctypes import c_short, c_uint, c_int, c_long, pointer, POINTER, byref\n    POINTER, byref\n    ",
            )
            == "def z() -> None:\n    from ctypes import POINTER, byref\n    POINTER, byref\n    "
        )

        assert (
            autoflake.fix_code(
                "def z() -> None:\n    from ctypes import c_short, c_uint, c_int, c_long, pointer, POINTER, byref\n",
            )
            == "def z() -> None:\n    pass\n"
        )

    def test_fix_code_with_empty_string(self) -> None:
        assert autoflake.fix_code("") == ""

    def test_fix_code_with_from_and_as_and_escaped_newline(self) -> None:
        """Make sure stuff after escaped newline is not lost."""
        result = autoflake.fix_code(
            """\
from collections import defaultdict, namedtuple \\
    as xyz
xyz
""",
        )
        # We currently leave lines with escaped newlines as is. But in the
        # future this we may parse them and remove unused import accordingly.
        # For now, we'll work around it here.
        result = re.sub(r" *\\\n *as ", " as ", result)

        assert autoflake.fix_code(result) == "from collections import namedtuple as xyz\nxyz\n"

    def test_fix_code_with_unused_variables(self) -> None:
        assert (
            autoflake.fix_code(
                "def main() -> None:\n    x = 10\n    y = 11\n    print(y)\n",
                remove_unused_variables=True,
            )
            == "def main() -> None:\n    y = 11\n    print(y)\n"
        )

    def test_fix_code_with_unused_variables_drop_rhs(self) -> None:
        assert (
            autoflake.fix_code(
                "def main() -> None:\n    x = 10\n    y = 11\n    print(y)\n",
                remove_unused_variables=True,
                remove_rhs_for_unused_variables=True,
            )
            == "def main() -> None:\n    y = 11\n    print(y)\n"
        )

    def test_fix_code_with_unused_variables_should_skip_nonlocal(self) -> None:
        """Pyflakes does not handle nonlocal correctly."""
        code = """\
def bar() -> None:
    x = 1

    def foo() -> None:
        nonlocal x
        x = 2
"""
        assert code == autoflake.fix_code(code, remove_unused_variables=True)

    def test_fix_code_with_unused_variables_should_skip_nonlocal_drop_rhs(
        self,
    ):
        """Pyflakes does not handle nonlocal correctly."""
        code = """\
def bar() -> None:
    x = 1

    def foo() -> None:
        nonlocal x
        x = 2
"""
        assert code == autoflake.fix_code(
            code,
            remove_unused_variables=True,
            remove_rhs_for_unused_variables=True,
        )

    def test_detect_encoding_with_bad_encoding(self) -> None:
        with temporary_file("# -*- coding: blah -*-\n") as filename:
            assert autoflake.detect_encoding(filename) == "latin-1"

    def test_fix_code_with_comma_on_right(self) -> None:
        """Pyflakes does not handle nonlocal correctly."""
        assert (
            autoflake.fix_code(
                "def main() -> None:\n    x = (1, 2, 3)\n",
                remove_unused_variables=True,
            )
            == "def main() -> None:\n    pass\n"
        )

    def test_fix_code_with_comma_on_right_drop_rhs(self) -> None:
        """Pyflakes does not handle nonlocal correctly."""
        assert (
            autoflake.fix_code(
                "def main() -> None:\n    x = (1, 2, 3)\n",
                remove_unused_variables=True,
                remove_rhs_for_unused_variables=True,
            )
            == "def main() -> None:\n    pass\n"
        )

    def test_fix_code_with_unused_variables_should_skip_multiple(self) -> None:
        code = """\
def main() -> None:
    (x, y, z) = (1, 2, 3)
    print(z)
"""
        assert code == autoflake.fix_code(code, remove_unused_variables=True)

    def test_fix_code_with_unused_variables_should_skip_multiple_drop_rhs(
        self,
    ):
        code = """\
def main() -> None:
    (x, y, z) = (1, 2, 3)
    print(z)
"""
        assert code == autoflake.fix_code(
            code,
            remove_unused_variables=True,
            remove_rhs_for_unused_variables=True,
        )

    def test_fix_code_should_handle_pyflakes_recursion_error_gracefully(self) -> None:
        code = "x = [{}]".format("+".join(["abc" for _ in range(2000)]))
        assert code == autoflake.fix_code(code)

    def test_fix_code_with_duplicate_key(self) -> None:
        assert (
            "".join(
                autoflake.fix_code(
                    "a = {\n  (0,1): 1,\n  (0, 1): 'two',\n  (0,1): 3,\n}\nprint(a)\n",
                    remove_duplicate_keys=True,
                ),
            )
            == "a = {\n  (0,1): 3,\n}\nprint(a)\n"
        )

    def test_fix_code_with_duplicate_key_longer(self) -> None:
        assert (
            "".join(
                autoflake.fix_code(
                    "{\n    'a': 0,\n    'b': 1,\n    'c': 2,\n    'd': 3,\n    'e': 4,\n    'f': 5,\n    'b': 6,\n}\n",
                    remove_duplicate_keys=True,
                ),
            )
            == "{\n    'a': 0,\n    'c': 2,\n    'd': 3,\n    'e': 4,\n    'f': 5,\n    'b': 6,\n}\n"
        )

    def test_fix_code_with_duplicate_key_with_many_braces(self) -> None:
        assert (
            "".join(
                autoflake.fix_code(
                    "a = None\n\n{None: {None: None},\n }\n\n{\n    None: a.a,\n    None: a.b,\n}\n",
                    remove_duplicate_keys=True,
                ),
            )
            == "a = None\n\n{None: {None: None},\n }\n\n{\n    None: a.b,\n}\n"
        )

    def test_fix_code_should_ignore_complex_case_of_duplicate_key(self) -> None:
        """We only handle simple cases."""
        code = """\
a = {(0,1): 1, (0, 1): 'two',
  (0,1): 3,
}
print(a)
"""

        assert code == "".join(autoflake.fix_code(code, remove_duplicate_keys=True))

    def test_fix_code_should_ignore_complex_case_of_duplicate_key_comma(self) -> None:
        """We only handle simple cases."""
        code = """\
{
    1: {0,
    },
    1: {2,
    },
}
"""

        assert code == "".join(autoflake.fix_code(code, remove_duplicate_keys=True))

    def test_fix_code_should_ignore_complex_case_of_duplicate_key_partially(
        self,
    ):
        """We only handle simple cases."""
        code = """\
a = {(0,1): 1, (0, 1): 'two',
  (0,1): 3,
  (2,3): 4,
  (2,3): 4,
  (2,3): 5,
}
print(a)
"""

        assert (
            "".join(autoflake.fix_code(code, remove_duplicate_keys=True))
            == "a = {(0,1): 1, (0, 1): 'two',\n  (0,1): 3,\n  (2,3): 5,\n}\nprint(a)\n"
        )

    def test_fix_code_should_ignore_more_cases_of_duplicate_key(self) -> None:
        """We only handle simple cases."""
        code = """\
a = {
    (0,1):
    1,
    (0, 1): 'two',
  (0,1): 3,
}
print(a)
"""

        assert code == "".join(autoflake.fix_code(code, remove_duplicate_keys=True))

    def test_fix_code_should_ignore_duplicate_key_with_comments(self) -> None:
        """We only handle simple cases."""
        code = """\
a = {
    (0,1)  # : f
    :
    1,
    (0, 1): 'two',
  (0,1): 3,
}
print(a)
"""

        assert code == "".join(autoflake.fix_code(code, remove_duplicate_keys=True))

        code = """\
{
    1: {0,
    },
    1: #{2,
    #},
    0
}
"""

        assert code == "".join(autoflake.fix_code(code, remove_duplicate_keys=True))

    def test_fix_code_should_ignore_duplicate_key_with_multiline_key(self) -> None:
        """We only handle simple cases."""
        code = """\
a = {
    (0,1
    ): 1,
    (0, 1): 'two',
  (0,1): 3,
}
print(a)
"""

        assert code == "".join(autoflake.fix_code(code, remove_duplicate_keys=True))

    def test_fix_code_should_ignore_duplicate_key_with_no_comma(self) -> None:
        """We don't want to delete the line and leave a lone comma."""
        code = """\
a = {
    (0,1) : 1
    ,
    (0, 1): 'two',
  (0,1): 3,
}
print(a)
"""

        assert code == "".join(autoflake.fix_code(code, remove_duplicate_keys=True))

    def test_fix_code_keeps_pass_statements(self) -> None:
        code = """\
    if True:
        pass
    else:
        def foo() -> None:
            \"\"\" A docstring. \"\"\"
            pass
        def foo2() -> None:
            \"\"\" A docstring. \"\"\"

            pass
        def foo3() -> None:
            \"\"\" A docstring. \"\"\"


            pass
        def bar() -> None:
            # abc
            pass
        def blah() -> None:
            123
            pass
            pass  # Nope.
            pass
    """

        assert code == "".join(autoflake.fix_code(code, ignore_pass_statements=True))

    def test_fix_code_keeps_passes_after_docstrings(self) -> None:
        actual = autoflake.fix_code(
            """\
    if True:
        pass
    else:
        def foo() -> None:
            \"\"\" A docstring. \"\"\"
            pass
        def foo2() -> None:
            \"\"\" A docstring. \"\"\"

            pass
        def foo3() -> None:
            \"\"\" A docstring. \"\"\"


            pass
        def bar() -> None:
            # abc
            pass
        def blah() -> None:
            123
            pass
            pass  # Nope.
            pass
    """,
            ignore_pass_after_docstring=True,
        )

        expected = """\
    if True:
        pass
    else:
        def foo() -> None:
            \"\"\" A docstring. \"\"\"
            pass
        def foo2() -> None:
            \"\"\" A docstring. \"\"\"

            pass
        def foo3() -> None:
            \"\"\" A docstring. \"\"\"


            pass
        def bar() -> None:
            # abc
            pass
        def blah() -> None:
            123
            pass  # Nope.
    """

        assert actual == expected

    def test_useless_pass_line_numbers(self) -> None:
        assert [1] == list(autoflake.useless_pass_line_numbers("pass\n"))

        assert [] == list(autoflake.useless_pass_line_numbers("if True:\n    pass\n"))

    def test_useless_pass_line_numbers_with_escaped_newline(self) -> None:
        assert [] == list(autoflake.useless_pass_line_numbers("if True:\\\n    pass\n"))

    def test_useless_pass_line_numbers_with_more_complex(self) -> None:
        assert [6] == list(
            autoflake.useless_pass_line_numbers(
                "if True:\n    pass\nelse:\n    True\n    x = 1\n    pass\n",
            ),
        )

    def test_useless_pass_line_numbers_after_docstring(self) -> None:
        actual_pass_line_numbers = list(
            autoflake.useless_pass_line_numbers(
                """\
    @abc.abstractmethod
    def some_abstract_method() -> None:
        \"\"\"Some docstring.\"\"\"
        pass
    """,
            ),
        )

        expected_pass_line_numbers = [4]
        assert expected_pass_line_numbers == actual_pass_line_numbers

    def test_useless_pass_line_numbers_keep_pass_after_docstring(self) -> None:
        actual_pass_line_numbers = list(
            autoflake.useless_pass_line_numbers(
                """\
    @abc.abstractmethod
    def some_abstract_method() -> None:
        \"\"\"Some docstring.\"\"\"
        pass
    """,
                ignore_pass_after_docstring=True,
            ),
        )

        expected_pass_line_numbers = []
        assert expected_pass_line_numbers == actual_pass_line_numbers

    def test_filter_useless_pass(self) -> None:
        assert (
            "".join(
                autoflake.filter_useless_pass(
                    "if True:\n    pass\nelse:\n    True\n    x = 1\n    pass\n",
                ),
            )
            == "if True:\n    pass\nelse:\n    True\n    x = 1\n"
        )

    def test_filter_useless_pass_with_syntax_error(self) -> None:
        source = """\
if True:
if True:
            if True:
    if True:

if True:
    pass
else:
    True
    pass
    pass
    x = 1
"""

        assert source == "".join(autoflake.filter_useless_pass(source))

    def test_filter_useless_pass_more_complex(self) -> None:
        assert (
            "".join(
                autoflake.filter_useless_pass(
                    "if True:\n    pass\nelse:\n    def foo() -> None:\n        pass\n        # abc\n    def bar() -> None:\n        # abc\n        pass\n    def blah() -> None:\n        123\n        pass\n        pass  # Nope.\n        pass\n    True\n    x = 1\n    pass\n",
                ),
            )
            == "if True:\n    pass\nelse:\n    def foo() -> None:\n        pass\n        # abc\n    def bar() -> None:\n        # abc\n        pass\n    def blah() -> None:\n        123\n        pass  # Nope.\n    True\n    x = 1\n"
        )

    def test_filter_useless_pass_keep_pass_after_docstring(self) -> None:
        source = """\
    def foo() -> None:
        \"\"\" This is not a useless 'pass'. \"\"\"
        pass

    @abc.abstractmethod
    def bar() -> None:
        \"\"\"
            Also this is not a useless 'pass'.
        \"\"\"
        pass
    """
        assert source == "".join(
            autoflake.filter_useless_pass(source, ignore_pass_after_docstring=True),
        )

    def test_filter_useless_pass_keeps_pass_statements(self) -> None:
        source = """\
    if True:
        pass
        pass
        pass
        pass
    else:
        pass
        True
        x = 1
        pass
    """

        assert source == "".join(autoflake.filter_useless_pass(source, ignore_pass_statements=True))

    def test_filter_useless_paspasss_with_try(self) -> None:
        assert (
            "".join(
                autoflake.filter_useless_pass(
                    "import os\nos.foo()\ntry:\n    pass\n    pass\nexcept ImportError:\n    pass\n",
                ),
            )
            == "import os\nos.foo()\ntry:\n    pass\nexcept ImportError:\n    pass\n"
        )

    def test_filter_useless_pass_leading_pass(self) -> None:
        assert (
            "".join(
                autoflake.filter_useless_pass(
                    "if True:\n    pass\n    pass\n    pass\n    pass\nelse:\n    pass\n    True\n    x = 1\n    pass\n",
                ),
            )
            == "if True:\n    pass\nelse:\n    True\n    x = 1\n"
        )

    def test_filter_useless_pass_leading_pass_with_number(self) -> None:
        assert (
            "".join(
                autoflake.filter_useless_pass(
                    "def func11() -> None:\n    pass\n    0, 11 / 2\n    return 1\n",
                ),
            )
            == "def func11() -> None:\n    0, 11 / 2\n    return 1\n"
        )

    def test_filter_useless_pass_leading_pass_with_string(self) -> None:
        assert (
            "".join(
                autoflake.filter_useless_pass(
                    "def func11() -> None:\n    pass\n    'hello'\n    return 1\n",
                ),
            )
            == "def func11() -> None:\n    'hello'\n    return 1\n"
        )

    def test_check(self) -> None:
        assert autoflake.check("import os")

    def test_check_with_bad_syntax(self) -> None:
        assert not autoflake.check("foo(")

    def test_check_with_unicode(self) -> None:
        assert not autoflake.check('print("∑")')

        assert autoflake.check("import os  # ∑")

    def test_get_diff_text(self) -> None:
        # We ignore the first two lines since it differs on Python 2.6.
        assert (
            "\n".join(autoflake.get_diff_text(["foo\n"], ["bar\n"], "").split("\n")[3:])
            == "-foo\n+bar\n"
        )

    def test_get_diff_text_without_newline(self) -> None:
        # We ignore the first two lines since it differs on Python 2.6.
        assert (
            "\n".join(autoflake.get_diff_text(["foo"], ["foo\n"], "").split("\n")[3:])
            == "-foo\n\\ No newline at end of file\n+foo\n"
        )

    def test_is_literal_or_name(self) -> None:
        assert autoflake.is_literal_or_name("123")
        assert autoflake.is_literal_or_name("[1, 2, 3]")
        assert autoflake.is_literal_or_name("xyz")

        assert not autoflake.is_literal_or_name("xyz.prop")
        assert not autoflake.is_literal_or_name(" ")

    def test_is_python_file(self) -> None:
        assert autoflake.is_python_file(os.path.join(ROOT_DIRECTORY, "autoflake.py"))

        with temporary_file("#!/usr/bin/env python", suffix="") as filename:
            assert autoflake.is_python_file(filename)

        with temporary_file("#!/usr/bin/python", suffix="") as filename:
            assert autoflake.is_python_file(filename)

        with temporary_file("#!/usr/bin/python3", suffix="") as filename:
            assert autoflake.is_python_file(filename)

        with temporary_file("#!/usr/bin/pythonic", suffix="") as filename:
            assert not autoflake.is_python_file(filename)

        with temporary_file("###!/usr/bin/python", suffix="") as filename:
            assert not autoflake.is_python_file(filename)

        assert not autoflake.is_python_file(os.devnull)
        assert not autoflake.is_python_file("/bin/bash")

    def test_is_exclude_file(self) -> None:
        assert autoflake.is_exclude_file("1.py", ["test*", "1*"])

        assert not autoflake.is_exclude_file("2.py", ["test*", "1*"])

        # folder glob
        assert autoflake.is_exclude_file("test/test.py", ["test/**.py"])

        assert autoflake.is_exclude_file("test/auto_test.py", ["test/*_test.py"])

        assert not autoflake.is_exclude_file("test/auto_auto.py", ["test/*_test.py"])

    def test_match_file(self) -> None:
        with temporary_file("", suffix=".py", prefix=".") as filename:
            assert not autoflake.match_file(filename, exclude=[]), filename

        assert not autoflake.match_file(os.devnull, exclude=[])

        with temporary_file("", suffix=".py", prefix="") as filename:
            assert autoflake.match_file(filename, exclude=[]), filename

    def test_find_files(self) -> None:
        temp_directory = tempfile.mkdtemp()
        try:
            target = os.path.join(temp_directory, "dir")
            os.mkdir(target)
            with open(os.path.join(target, "a.py"), "w"):
                pass

            exclude = os.path.join(target, "ex")
            os.mkdir(exclude)
            with open(os.path.join(exclude, "b.py"), "w"):
                pass

            sub = os.path.join(exclude, "sub")
            os.mkdir(sub)
            with open(os.path.join(sub, "c.py"), "w"):
                pass

            # FIXME: Avoid changing directory. This may interfere with parallel
            # test runs.
            cwd = os.getcwd()
            os.chdir(temp_directory)
            try:
                files = list(
                    autoflake.find_files(
                        ["dir"],
                        True,
                        [os.path.join("dir", "ex")],
                    ),
                )
            finally:
                os.chdir(cwd)

            file_names = [os.path.basename(f) for f in files]
            assert "a.py" in file_names
            assert "b.py" not in file_names
            assert "c.py" not in file_names
        finally:
            shutil.rmtree(temp_directory)

    def test_exclude(self) -> None:
        temp_directory = tempfile.mkdtemp(dir=".")
        try:
            with open(os.path.join(temp_directory, "a.py"), "w") as output:
                output.write("import re\n")

            os.mkdir(os.path.join(temp_directory, "d"))
            with open(
                os.path.join(temp_directory, "d", "b.py"),
                "w",
            ) as output:
                output.write("import os\n")

            p = subprocess.Popen(
                [*list(AUTOFLAKE_COMMAND), temp_directory, "--recursive", "--exclude=a*"],
                stdout=subprocess.PIPE,
            )
            result = p.communicate()[0].decode("utf-8")

            assert "import re" not in result
            assert "import os" in result
        finally:
            shutil.rmtree(temp_directory)


class SystemTests(unittest.TestCase):
    """System tests."""

    def test_skip_file(self) -> None:
        skipped_file_file_text = """
# autoflake: skip_file
import re
import os
import my_own_module
x = 1
"""
        with temporary_file(skipped_file_file_text) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=["my_fake_program", filename, "--stdout"],
                standard_out=output_file,
                standard_error=None,
            )
            assert normalize_line_endings(skipped_file_file_text) == normalize_line_endings(
                output_file.getvalue(),
            )

    def test_skip_file_with_shebang_respect(self) -> None:
        skipped_file_file_text = """
#!/usr/bin/env python3

# autoflake: skip_file

import re
import os
import my_own_module
x = 1
"""
        with temporary_file(skipped_file_file_text) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=["my_fake_program", filename, "--stdout"],
                standard_out=output_file,
                standard_error=None,
            )
            assert normalize_line_endings(skipped_file_file_text) == normalize_line_endings(
                output_file.getvalue(),
            )

    def test_diff(self) -> None:
        with temporary_file(
            """\
import re
import os
import my_own_module
x = 1
""",
        ) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=["my_fake_program", filename],
                standard_out=output_file,
                standard_error=None,
            )
            assert (
                "\n".join(output_file.getvalue().split("\n")[3:])
                == "-import re\n-import os\n import my_own_module\n x = 1\n"
            )

    def test_diff_with_nonexistent_file(self) -> None:
        output_file = io.StringIO()
        autoflake._main(
            argv=["my_fake_program", "nonexistent_file"],
            standard_out=output_file,
            standard_error=output_file,
        )
        assert "no such file" in output_file.getvalue().lower()

    def test_diff_with_encoding_declaration(self) -> None:
        with temporary_file(
            """\
# coding: iso-8859-1
import re
import os
import my_own_module
x = 1
""",
        ) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=["my_fake_program", filename],
                standard_out=output_file,
                standard_error=None,
            )
            assert (
                "\n".join(output_file.getvalue().split("\n")[3:])
                == " # coding: iso-8859-1\n-import re\n-import os\n import my_own_module\n x = 1\n"
            )

    def test_in_place(self) -> None:
        with temporary_file(
            """\
import foo
x = foo
import subprocess
x()

try:
    import os
except ImportError:
    import os
""",
        ) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=["my_fake_program", "--in-place", filename],
                standard_out=output_file,
                standard_error=None,
            )
            with open(filename) as f:
                assert (
                    f.read()
                    == "import foo\nx = foo\nx()\n\ntry:\n    pass\nexcept ImportError:\n    pass\n"
                )

    def test_check_with_empty_file(self) -> None:
        line = ""

        with temporary_file(line) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=["my_fake_program", "--check", filename],
                standard_out=output_file,
                standard_error=None,
            )
            assert f"{filename}: No issues detected!{os.linesep}" == output_file.getvalue()

    def test_check_correct_file(self) -> None:
        with temporary_file(
            """\
import foo
x = foo.bar
print(x)
""",
        ) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=["my_fake_program", "--check", filename],
                standard_out=output_file,
                standard_error=None,
            )
            assert f"{filename}: No issues detected!{os.linesep}" == output_file.getvalue()

    def test_check_correct_file_with_quiet(self) -> None:
        with temporary_file(
            """\
import foo
x = foo.bar
print(x)
""",
        ) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=[
                    "my_fake_program",
                    "--check",
                    "--quiet",
                    filename,
                ],
                standard_out=output_file,
                standard_error=None,
            )
            assert output_file.getvalue() == ""

    def test_check_useless_pass(self) -> None:
        with temporary_file(
            """\
import foo
x = foo
import subprocess
x()

try:
    pass
    import os
except ImportError:
    pass
    import os
    import sys
""",
        ) as filename:
            output_file = io.StringIO()
            exit_status = autoflake._main(
                argv=["my_fake_program", "--check", filename],
                standard_out=output_file,
                standard_error=None,
            )
            assert exit_status == 1
            assert (
                f"{filename}: Unused imports/variables detected{os.linesep}"
                == output_file.getvalue()
            )

    def test_check_with_multiple_files(self) -> None:
        with temporary_file("import sys") as file1:
            with temporary_file("import sys") as file2:
                output_file = io.StringIO()
                exit_status = autoflake._main(
                    argv=["my_fake_program", "--check", file1, file2],
                    standard_out=output_file,
                    standard_error=None,
                )
                assert exit_status == 1
                assert {
                    f"{file1}: Unused imports/variables detected",
                    f"{file2}: Unused imports/variables detected",
                } == set(output_file.getvalue().strip().split(os.linesep))

    def test_check_diff_with_empty_file(self) -> None:
        line = ""

        with temporary_file(line) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=["my_fake_program", "--check-diff", filename],
                standard_out=output_file,
                standard_error=None,
            )
            assert f"{filename}: No issues detected!{os.linesep}" == output_file.getvalue()

    def test_check_diff_correct_file(self) -> None:
        with temporary_file(
            """\
import foo
x = foo.bar
print(x)
""",
        ) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=["my_fake_program", "--check-diff", filename],
                standard_out=output_file,
                standard_error=None,
            )
            assert f"{filename}: No issues detected!{os.linesep}" == output_file.getvalue()

    def test_check_diff_correct_file_with_quiet(self) -> None:
        with temporary_file(
            """\
import foo
x = foo.bar
print(x)
""",
        ) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=[
                    "my_fake_program",
                    "--check-diff",
                    "--quiet",
                    filename,
                ],
                standard_out=output_file,
                standard_error=None,
            )
            assert output_file.getvalue() == ""

    def test_check_diff_useless_pass(self) -> None:
        with temporary_file(
            """\
import foo
x = foo
import subprocess
x()
try:
    pass
    import os
except ImportError:
    pass
    import os
    import sys
""",
        ) as filename:
            output_file = io.StringIO()
            exit_status = autoflake._main(
                argv=["my_fake_program", "--check-diff", filename],
                standard_out=output_file,
                standard_error=None,
            )
            assert exit_status == 1
            assert (
                "\n".join(output_file.getvalue().split("\n")[3:])
                == " import foo\n x = foo\n-import subprocess\n x()\n try:\n     pass\n-    import os\n except ImportError:\n     pass\n-    import os\n-    import sys\n"
            )

    def test_in_place_with_empty_file(self) -> None:
        line = ""

        with temporary_file(line) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=["my_fake_program", "--in-place", filename],
                standard_out=output_file,
                standard_error=None,
            )
            with open(filename) as f:
                assert line == f.read()

    def test_in_place_with_with_useless_pass(self) -> None:
        with temporary_file(
            """\
import foo
x = foo
import subprocess
x()

try:
    pass
    import os
except ImportError:
    pass
    import os
    import sys
""",
        ) as filename:
            output_file = io.StringIO()
            autoflake._main(
                argv=["my_fake_program", "--in-place", filename],
                standard_out=output_file,
                standard_error=None,
            )
            with open(filename) as f:
                assert (
                    f.read()
                    == "import foo\nx = foo\nx()\n\ntry:\n    pass\nexcept ImportError:\n    pass\n"
                )

    def test_with_missing_file(self) -> None:
        output_file = io.StringIO()
        ignore = StubFile()
        autoflake._main(
            argv=["my_fake_program", "--in-place", ".fake"],
            standard_out=output_file,
            standard_error=ignore,  # type: ignore
        )
        assert not output_file.getvalue()

    def test_ignore_hidden_directories(self) -> None:
        with temporary_directory() as directory, temporary_directory(
            prefix=".",
            directory=directory,
        ) as inner_directory, temporary_file(
            """\
import re
import os
""",
            directory=inner_directory,
        ):
            output_file = io.StringIO()
            autoflake._main(
                argv=[
                    "my_fake_program",
                    "--recursive",
                    directory,
                ],
                standard_out=output_file,
                standard_error=None,
            )
            assert output_file.getvalue().strip() == ""

    def test_in_place_and_stdout(self) -> None:
        output_file = io.StringIO()
        self.assertRaises(
            SystemExit,
            autoflake._main,
            argv=["my_fake_program", "--in-place", "--stdout", __file__],
            standard_out=output_file,
            standard_error=output_file,
        )

    def test_end_to_end(self) -> None:
        with temporary_file(
            """\
import fake_fake, fake_foo, fake_bar, fake_zoo
import re, os
x = os.sep
print(x)
""",
        ) as filename:
            process = subprocess.Popen(
                [*AUTOFLAKE_COMMAND, "--imports=fake_foo,fake_bar", filename],
                stdout=subprocess.PIPE,
            )
            assert (
                "\n".join(process.communicate()[0].decode().split(os.linesep)[3:])
                == "-import fake_fake, fake_foo, fake_bar, fake_zoo\n-import re, os\n+import fake_fake\n+import fake_zoo\n+import os\n x = os.sep\n print(x)\n"
            )

    def test_end_to_end_multiple_files(self) -> None:
        with temporary_file(
            """\
import fake_fake, fake_foo, fake_bar, fake_zoo
import re, os
x = os.sep
print(x)
""",
        ) as filename1, temporary_file(
            """\
import os
x = os.sep
print(x)
""",
        ) as filename2:
            process = subprocess.Popen(
                [
                    *AUTOFLAKE_COMMAND,
                    "--imports=fake_foo,fake_bar",
                    "--check",
                    "--jobs=2",
                    filename1,
                    filename2,
                ],
                stdout=subprocess.PIPE,
            )

            status_code = process.wait()
            assert status_code == 1

    def test_end_to_end_with_remove_all_unused_imports(self) -> None:
        with temporary_file(
            """\
import fake_fake, fake_foo, fake_bar, fake_zoo
import re, os
x = os.sep
print(x)
""",
        ) as filename:
            process = subprocess.Popen(
                [*AUTOFLAKE_COMMAND, "--remove-all", filename],
                stdout=subprocess.PIPE,
            )
            assert (
                "\n".join(process.communicate()[0].decode().split(os.linesep)[3:])
                == "-import fake_fake, fake_foo, fake_bar, fake_zoo\n-import re, os\n+import os\n x = os.sep\n print(x)\n"
            )

    def test_end_to_end_with_remove_duplicate_keys_multiple_lines(self) -> None:
        with temporary_file(
            """\
a = {
    'b': 456,
    'a': 123,
    'b': 7834,
    'a': 'wow',
    'b': 456,
    'c': 'hello',
    'c': 'hello2',
    'b': 'hiya',
}
print(a)
""",
        ) as filename:
            process = subprocess.Popen(
                [*AUTOFLAKE_COMMAND, "--remove-duplicate-keys", filename],
                stdout=subprocess.PIPE,
            )
            assert (
                "\n".join(process.communicate()[0].decode().split(os.linesep)[3:])
                == " a = {\n-    'b': 456,\n-    'a': 123,\n-    'b': 7834,\n     'a': 'wow',\n-    'b': 456,\n-    'c': 'hello',\n     'c': 'hello2',\n     'b': 'hiya',\n }\n"
            )

    def test_end_to_end_with_remove_duplicate_keys_and_other_errors(self) -> None:
        with temporary_file(
            """\
from math import *
print(sin(4))
a = { # Hello
    'b': 456,
    'a': 123,
    'b': 7834,
    'a': 'wow',
    'b': 456,
    'c': 'hello',
    'c': 'hello2',
    'b': 'hiya',
}
print(a)
""",
        ) as filename:
            process = subprocess.Popen(
                [*AUTOFLAKE_COMMAND, "--remove-duplicate-keys", filename],
                stdout=subprocess.PIPE,
            )
            assert (
                "\n".join(process.communicate()[0].decode().split(os.linesep)[3:])
                == " from math import *\n print(sin(4))\n a = { # Hello\n-    'b': 456,\n-    'a': 123,\n-    'b': 7834,\n     'a': 'wow',\n-    'b': 456,\n-    'c': 'hello',\n     'c': 'hello2',\n     'b': 'hiya',\n }\n"
            )

    def test_end_to_end_with_remove_duplicate_keys_tuple(self) -> None:
        with temporary_file(
            """\
a = {
  (0,1): 1,
  (0, 1): 'two',
  (0,1): 3,
}
print(a)
""",
        ) as filename:
            process = subprocess.Popen(
                [*AUTOFLAKE_COMMAND, "--remove-duplicate-keys", filename],
                stdout=subprocess.PIPE,
            )
            assert (
                "\n".join(process.communicate()[0].decode().split(os.linesep)[3:])
                == " a = {\n-  (0,1): 1,\n-  (0, 1): 'two',\n   (0,1): 3,\n }\n print(a)\n"
            )

    def test_end_to_end_with_error(self) -> None:
        with temporary_file(
            """\
import fake_fake, fake_foo, fake_bar, fake_zoo
import re, os
x = os.sep
print(x)
""",
        ) as filename:
            process = subprocess.Popen(
                [*AUTOFLAKE_COMMAND, "--imports=fake_foo,fake_bar", "--remove-all", filename],
                stderr=subprocess.PIPE,
            )
            assert "not allowed with argument" in process.communicate()[1].decode()

    def test_end_to_end_from_stdin(self) -> None:
        stdin_data = b"""\
import fake_fake, fake_foo, fake_bar, fake_zoo
import re, os
x = os.sep
print(x)
"""
        process = subprocess.Popen(
            [*AUTOFLAKE_COMMAND, "--remove-all", "-"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        stdout, _ = process.communicate(stdin_data)
        assert "\n".join(stdout.decode().split(os.linesep)) == "import os\nx = os.sep\nprint(x)\n"

    def test_end_to_end_from_stdin_with_in_place(self) -> None:
        stdin_data = b"""\
import fake_fake, fake_foo, fake_bar, fake_zoo
import re, os, sys
x = os.sep
print(x)
"""
        process = subprocess.Popen(
            [*AUTOFLAKE_COMMAND, "--remove-all", "--in-place", "-"],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        stdout, _ = process.communicate(stdin_data)
        assert "\n".join(stdout.decode().split(os.linesep)) == "import os\nx = os.sep\nprint(x)\n"

    def test_end_to_end_dont_remove_unused_imports_when_not_using_flag(self) -> None:
        with temporary_file(
            """\
from . import fake_bar
from . import fake_foo
fake_foo.fake_function()
""",
        ) as filename:
            process = subprocess.Popen(
                [*AUTOFLAKE_COMMAND, filename],
                stdout=subprocess.PIPE,
            )
            assert "\n".join(process.communicate()[0].decode().split(os.linesep)[3:]) == ""


class MultilineFromImportTests(unittest.TestCase):
    def test_is_over(self) -> None:
        filt = autoflake.FilterMultilineImport("from . import (\n")
        assert filt.is_over("module)\n")
        assert filt.is_over("  )\n")
        assert filt.is_over("  )  # comment\n")
        assert filt.is_over("from module import (a, b)\n")
        assert not filt.is_over("#  )")
        assert not filt.is_over("module\n")
        assert not filt.is_over("module, \\\n")
        assert not filt.is_over("\n")

        filt = autoflake.FilterMultilineImport("from . import module, \\\n")
        assert filt.is_over("module\n")
        assert filt.is_over("\n")
        assert filt.is_over("m1, m2  # comment with \\\n")
        assert not filt.is_over("m1, m2 \\\n")
        assert not filt.is_over("m1, m2 \\  #\n")
        assert not filt.is_over("m1, m2 \\  # comment with \\\n")
        assert not filt.is_over("\\\n")

        # "Multiline" imports that are not really multiline
        filt = autoflake.FilterMultilineImport(
            "import os; import math, subprocess",
        )
        assert filt.is_over()

    unused = ()

    def assert_fix(
        self,
        lines: Sequence[str],
        result: str,
        remove_all: bool = True,
    ) -> None:
        fixer = autoflake.FilterMultilineImport(
            lines[0],
            remove_all_unused_imports=remove_all,
            unused_module=self.unused,
        )
        fixed = functools.reduce(
            lambda acc, x: acc(x) if isinstance(acc, autoflake.PendingFix) else acc,
            lines[1:],
            fixer(),
        )
        assert fixed == result

    def test_fix(self) -> None:
        self.unused = ["third_party.lib" + str(x) for x in (1, 3, 4)]

        # Example m0 (isort)
        self.assert_fix(
            [
                "from third_party import (lib1, lib2, lib3,\n",
                "                         lib4, lib5, lib6)\n",
            ],
            "from third_party import (lib2, lib5, lib6)\n",
        )

        # Example m1(isort)
        self.assert_fix(
            [
                "from third_party import (lib1,\n",
                "                         lib2,\n",
                "                         lib3,\n",
                "                         lib4,\n",
                "                         lib5,\n",
                "                         lib6)\n",
            ],
            "from third_party import (lib2,\n"
            "                         lib5,\n"
            "                         lib6)\n",
        )

        # Variation m1(isort)
        self.assert_fix(
            [
                "from third_party import (lib1\n",
                "                        ,lib2\n",
                "                        ,lib3\n",
                "                        ,lib4\n",
                "                        ,lib5\n",
                "                        ,lib6)\n",
            ],
            "from third_party import (lib2\n"
            "                        ,lib5\n"
            "                        ,lib6)\n",
        )

        # Example m2 (isort)
        self.assert_fix(
            [
                "from third_party import \\\n",
                "    lib1, lib2, lib3, \\\n",
                "    lib4, lib5, lib6\n",
            ],
            "from third_party import \\\n    lib2, lib5, lib6\n",
        )

        # Example m3 (isort)
        self.assert_fix(
            [
                "from third_party import (\n",
                "    lib1,\n",
                "    lib2,\n",
                "    lib3,\n",
                "    lib4,\n",
                "    lib5\n",
                ")\n",
            ],
            "from third_party import (\n    lib2,\n    lib5\n)\n",
        )

        # Example m4 (isort)
        self.assert_fix(
            [
                "from third_party import (\n",
                "    lib1, lib2, lib3, lib4,\n",
                "    lib5, lib6)\n",
            ],
            "from third_party import (\n    lib2, lib5, lib6)\n",
        )

        # Example m5 (isort)
        self.assert_fix(
            [
                "from third_party import (\n",
                "    lib1, lib2, lib3, lib4,\n",
                "    lib5, lib6\n",
                ")\n",
            ],
            "from third_party import (\n    lib2, lib5, lib6\n)\n",
        )

        # Some Deviations
        self.assert_fix(
            [
                "from third_party import (\n",
                "    lib1\\\n",  # only unused + line continuation
                "    ,lib2, \n",
                "    libA\n",  # used import with no commas
                "    ,lib3, \n",  # leading and trailing commas + unused import
                "    libB, \n",
                "    \\\n",  # empty line with continuation
                "    lib4,\n",  # unused import with comment
                ")\n",
            ],
            "from third_party import (\n    lib2\\\n    ,libA, \n    libB,\n)\n",
        )

        self.assert_fix(
            [
                "from third_party import (\n",
                "    lib1\n",
                ",\n",
                "    lib2\n",
                ",\n",
                "    lib3\n",
                ",\n",
                "    lib4\n",
                ",\n",
                "    lib5\n",
                ")\n",
            ],
            "from third_party import (\n    lib2\n,\n    lib5\n)\n",
        )

        self.assert_fix(
            [
                "from third_party import (\n",
                "    lib1 \\\n",
                ", \\\n",
                "    lib2 \\\n",
                ",\\\n",
                "    lib3\n",
                ",\n",
                "    lib4\n",
                ",\n",
                "    lib5 \\\n",
                ")\n",
            ],
            "from third_party import (\n    lib2 \\\n, \\\n    lib5 \\\n)\n",
        )

    def test_indentation(self) -> None:
        # Some weird indentation examples
        self.unused = ["third_party.lib" + str(x) for x in (1, 3, 4)]
        self.assert_fix(
            [
                "    from third_party import (\n",
                "            lib1, lib2, lib3, lib4,\n",
                "    lib5, lib6\n",
                ")\n",
            ],
            "    from third_party import (\n            lib2, lib5, lib6\n)\n",
        )
        self.assert_fix(
            [
                "\tfrom third_party import \\\n",
                "\t\tlib1, lib2, lib3, \\\n",
                "\t\tlib4, lib5, lib6\n",
            ],
            "\tfrom third_party import \\\n\t\tlib2, lib5, lib6\n",
        )

    def test_fix_relative(self) -> None:
        # Example m0 (isort)
        self.unused = [".lib" + str(x) for x in (1, 3, 4)]
        self.assert_fix(
            [
                "from . import (lib1, lib2, lib3,\n",
                "               lib4, lib5, lib6)\n",
            ],
            "from . import (lib2, lib5, lib6)\n",
        )

        # Example m1(isort)
        self.unused = ["..lib" + str(x) for x in (1, 3, 4)]
        self.assert_fix(
            [
                "from .. import (lib1,\n",
                "                lib2,\n",
                "                lib3,\n",
                "                lib4,\n",
                "                lib5,\n",
                "                lib6)\n",
            ],
            "from .. import (lib2,\n                lib5,\n                lib6)\n",
        )

        # Example m2 (isort)
        self.unused = ["...lib" + str(x) for x in (1, 3, 4)]
        self.assert_fix(
            [
                "from ... import \\\n",
                "    lib1, lib2, lib3, \\\n",
                "    lib4, lib5, lib6\n",
            ],
            "from ... import \\\n    lib2, lib5, lib6\n",
        )

        # Example m3 (isort)
        self.unused = [".parent.lib" + str(x) for x in (1, 3, 4)]
        self.assert_fix(
            [
                "from .parent import (\n",
                "    lib1,\n",
                "    lib2,\n",
                "    lib3,\n",
                "    lib4,\n",
                "    lib5\n",
                ")\n",
            ],
            "from .parent import (\n    lib2,\n    lib5\n)\n",
        )

    def test_fix_without_from(self) -> None:
        self.unused = ["lib" + str(x) for x in (1, 3, 4)]

        # Multiline but not "from"
        self.assert_fix(
            [
                "import \\\n",
                "    lib1, lib2, lib3 \\\n",
                "    ,lib4, lib5, lib6\n",
            ],
            "import \\\n    lib2, lib5, lib6\n",
        )
        self.assert_fix(
            [
                "import lib1, lib2, lib3, \\\n",
                "       lib4, lib5, lib6\n",
            ],
            "import lib2, lib5, lib6\n",
        )

        # Problematic example without "from"
        self.assert_fix(
            [
                "import \\\n",
                "    lib1,\\\n",
                "    lib2, \\\n",
                "    libA\\\n",  # used import with no commas
                "    ,lib3, \\\n",  # leading and trailing commas with unused
                "    libB, \\\n",
                "    \\  \n",  # empty line with continuation
                "    lib4\\\n",  # unused import with comment
                "\n",
            ],
            "import \\\n    lib2,\\\n    libA, \\\n    libB\\\n\n",
        )

        self.unused = [f"lib{x}.x.y.z" for x in (1, 3, 4)]
        self.assert_fix(
            [
                "import \\\n",
                "    lib1.x.y.z \\",
                "    , \\\n",
                "    lib2.x.y.z \\\n",
                "    , \\\n",
                "    lib3.x.y.z \\\n",
                "    , \\\n",
                "    lib4.x.y.z \\\n",
                "    , \\\n",
                "    lib5.x.y.z\n",
            ],
            "import \\\n    lib2.x.y.z \\    , \\\n    lib5.x.y.z\n",
        )

    def test_give_up(self) -> None:
        # Semicolon
        self.unused = ["lib" + str(x) for x in (1, 3, 4)]
        self.assert_fix(
            [
                "import \\\n",
                "    lib1, lib2, lib3, \\\n",
                "    lib4, lib5; import lib6\n",
            ],
            "import \\\n    lib1, lib2, lib3, \\\n    lib4, lib5; import lib6\n",
        )
        # Comments
        self.unused = [".lib" + str(x) for x in (1, 3, 4)]
        self.assert_fix(
            [
                "from . import ( # comment\n",
                "    lib1,\\\n",  # only unused + line continuation
                "    lib2, \n",
                "    libA\n",  # used import with no commas
                "    ,lib3, \n",  # leading and trailing commas + unused import
                "    libB, \n",
                "    \\  \n",  # empty line with continuation
                "    lib4,  # noqa \n",  # unused import with comment
                ") ; import sys\n",
            ],
            "from . import ( # comment\n"
            "    lib1,\\\n"
            "    lib2, \n"
            "    libA\n"
            "    ,lib3, \n"
            "    libB, \n"
            "    \\  \n"
            "    lib4,  # noqa \n"
            ") ; import sys\n",
        )

    def test_just_one_import_used(self) -> None:
        self.unused = ["lib2"]
        self.assert_fix(
            [
                "import \\\n",
                "    lib1\n",
            ],
            "import \\\n    lib1\n",
        )
        self.assert_fix(
            [
                "import \\\n",
                "    lib2\n",
            ],
            "pass\n",
        )
        # Example from issue #8
        self.unused = ["re.subn"]
        self.assert_fix(
            [
                "\tfrom re import (subn)\n",
            ],
            "\tpass\n",
        )

    def test_just_one_import_left(self) -> None:
        # Examples from issue #8
        self.unused = ["math.sqrt"]
        self.assert_fix(
            [
                "from math import (\n",
                "        sqrt,\n",
                "        log\n",
                "    )\n",
            ],
            "from math import (\n        log\n    )\n",
        )
        self.unused = ["module.b"]
        self.assert_fix(
            [
                "from module import (a, b)\n",
            ],
            "from module import a\n",
        )
        self.assert_fix(
            [
                "from module import (a,\n",
                "                    b)\n",
            ],
            "from module import a\n",
        )
        self.unused = []
        self.assert_fix(
            [
                "from re import (subn)\n",
            ],
            "from re import (subn)\n",
        )

    def test_no_empty_imports(self) -> None:
        self.unused = ["lib" + str(x) for x in (1, 3, 4)]
        self.assert_fix(
            [
                "import \\\n",
                "    lib1, lib3, \\\n",
                "    lib4 \n",
            ],
            "pass \n",
        )

        # Indented parenthesized block
        self.unused = [".parent.lib" + str(x) for x in (1, 3, 4)]
        self.assert_fix(
            [
                "\t\tfrom .parent import (\n",
                "    lib1,\n",
                "    lib3,\n",
                "    lib4,\n",
                ")\n",
            ],
            "\t\tpass\n",
        )

    def test_without_remove_all(self) -> None:
        self.unused = ["lib" + str(x) for x in (1, 3, 4)]
        self.assert_fix(
            [
                "import \\\n",
                "    lib1,\\\n",
                "    lib3,\\\n",
                "    lib4\n",
            ],
            "import \\\n    lib1,\\\n    lib3,\\\n    lib4\n",
            remove_all=False,
        )

        self.unused += ["os.path." + x for x in ("dirname", "isdir", "join")]
        self.assert_fix(
            [
                "from os.path import (\n",
                "    dirname,\n",
                "    isdir,\n",
                "    join,\n",
                ")\n",
            ],
            "pass\n",
            remove_all=False,
        )
        self.assert_fix(
            [
                "import \\\n",
                "    os.path.dirname, \\\n",
                "    lib1, \\\n",
                "    lib3\n",
            ],
            "import \\\n    lib1, \\\n    lib3\n",
            remove_all=False,
        )


class ConfigFileTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.mkdtemp(prefix="autoflake.")

    def tearDown(self) -> None:
        if self.tmpdir:
            shutil.rmtree(self.tmpdir)

    def effective_path(self, path: str, is_file: bool = True) -> str:
        path = os.path.normpath(path)
        if os.path.isabs(path):
            msg = "Should not create an absolute test path"
            raise ValueError(msg)
        effective_path = os.path.sep.join([self.tmpdir, path])
        if not effective_path.startswith(
            f"{self.tmpdir}{os.path.sep}",
        ) and (effective_path != self.tmpdir or is_file):
            msg = "Should create a path within the tmp dir only"
            raise ValueError(msg)
        return effective_path

    def create_dir(self, path) -> None:
        effective_path = self.effective_path(path, False)
        os.makedirs(effective_path, exist_ok=True)

    def create_file(self, path, contents="") -> None:
        effective_path = self.effective_path(path)
        self.create_dir(os.path.split(path)[0])
        with open(effective_path, "w") as f:
            f.write(contents)

    def with_defaults(self, **kwargs: Any) -> Mapping[str, Any]:
        return {
            "check": False,
            "check_diff": False,
            "expand_star_imports": False,
            "ignore_init_module_imports": False,
            "ignore_pass_after_docstring": False,
            "ignore_pass_statements": False,
            "in_place": False,
            "quiet": False,
            "recursive": False,
            "remove_all_unused_imports": False,
            "remove_duplicate_keys": False,
            "remove_rhs_for_unused_variables": False,
            "remove_unused_variables": False,
            "write_to_stdout": False,
            **kwargs,
        }

    def test_no_config_file(self) -> None:
        self.create_file("test_me.py")
        original_args = {
            "files": [self.effective_path("test_me.py")],
        }
        args, success = autoflake.merge_configuration_file(original_args)
        assert success is True
        assert args == self.with_defaults(**original_args)

    def test_non_nested_pyproject_toml_empty(self) -> None:
        self.create_file("test_me.py")
        self.create_file("pyproject.toml", '[tool.other]\nprop="value"\n')
        files = [self.effective_path("test_me.py")]
        original_args = {"files": files}
        args, success = autoflake.merge_configuration_file(original_args)
        assert success is True
        assert args == self.with_defaults(**original_args)

    def test_non_nested_pyproject_toml_non_empty(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "pyproject.toml",
            "[tool.autoflake]\nexpand-star-imports=true\n",
        )
        files = [self.effective_path("test_me.py")]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(
            files=files,
            expand_star_imports=True,
        )

    def test_non_nested_setup_cfg_non_empty(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "setup.cfg",
            "[other]\nexpand-star-imports = yes\n",
        )
        files = [self.effective_path("test_me.py")]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(files=files)

    def test_non_nested_setup_cfg_empty(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "setup.cfg",
            "[autoflake]\nexpand-star-imports = yes\n",
        )
        files = [self.effective_path("test_me.py")]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(
            files=files,
            expand_star_imports=True,
        )

    def test_nested_file(self) -> None:
        self.create_file("nested/file/test_me.py")
        self.create_file(
            "pyproject.toml",
            "[tool.autoflake]\nexpand-star-imports=true\n",
        )
        files = [self.effective_path("nested/file/test_me.py")]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(
            files=files,
            expand_star_imports=True,
        )

    def test_common_path_nested_file_do_not_load(self) -> None:
        self.create_file("nested/file/test_me.py")
        self.create_file("nested/other/test_me.py")
        self.create_file(
            "nested/file/pyproject.toml",
            "[tool.autoflake]\nexpand-star-imports=true\n",
        )
        files = [
            self.effective_path("nested/file/test_me.py"),
            self.effective_path("nested/other/test_me.py"),
        ]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(files=files)

    def test_common_path_nested_file_do_load(self) -> None:
        self.create_file("nested/file/test_me.py")
        self.create_file("nested/other/test_me.py")
        self.create_file(
            "nested/pyproject.toml",
            "[tool.autoflake]\nexpand-star-imports=true\n",
        )
        files = [
            self.effective_path("nested/file/test_me.py"),
            self.effective_path("nested/other/test_me.py"),
        ]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(
            files=files,
            expand_star_imports=True,
        )

    def test_common_path_instead_of_common_prefix(self) -> None:
        """Using common prefix would result in a failure."""
        self.create_file("nested/file-foo/test_me.py")
        self.create_file("nested/file-bar/test_me.py")
        self.create_file(
            "nested/file/pyproject.toml",
            "[tool.autoflake]\nexpand-star-imports=true\n",
        )
        files = [
            self.effective_path("nested/file-foo/test_me.py"),
            self.effective_path("nested/file-bar/test_me.py"),
        ]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(files=files)

    def test_continue_search_if_no_config_found(self) -> None:
        self.create_file("nested/test_me.py")
        self.create_file(
            "nested/pyproject.toml",
            '[tool.other]\nprop = "value"\n',
        )
        self.create_file(
            "pyproject.toml",
            "[tool.autoflake]\nexpand-star-imports = true\n",
        )
        files = [self.effective_path("nested/test_me.py")]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(
            files=files,
            expand_star_imports=True,
        )

    def test_stop_search_if_config_found(self) -> None:
        self.create_file("nested/test_me.py")
        self.create_file(
            "nested/pyproject.toml",
            "[tool.autoflake]\n",
        )
        self.create_file(
            "pyproject.toml",
            "[tool.autoflake]\nexpand-star-imports = true\n",
        )
        files = [self.effective_path("nested/test_me.py")]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(files=files)

    def test_config_option(self) -> None:
        with temporary_file(
            suffix=".ini",
            contents=("[autoflake]\ncheck = True\n"),
        ) as temp_config:
            self.create_file("test_me.py")
            files = [self.effective_path("test_me.py")]

            args, success = autoflake.merge_configuration_file(
                {
                    "files": files,
                    "config_file": temp_config,
                },
            )
            assert success is True
            assert args == self.with_defaults(
                files=files,
                config_file=temp_config,
                check=True,
            )

    def test_merge_configuration_file__toml_config_option(self) -> None:
        with temporary_file(
            suffix=".toml",
            contents="""[project]
name = "test"
version = "0.1.0"

[tool.autoflake]
check = true
""",
        ) as temp_config:
            self.create_file("test_me.py")
            files = [self.effective_path("test_me.py")]

            args, success = autoflake.merge_configuration_file(
                {
                    "files": files,
                    "config_file": temp_config,
                    "check": False,  # Command line arguments should take precedence
                },
            )
            assert success is True
            # Command line arguments should override config file settings
            assert args == self.with_defaults(
                files=files,
                config_file=temp_config,
                check=False,  # Should match command line argument
            )

    def test_load_false(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "setup.cfg",
            "[autoflake]\nexpand-star-imports = no\n",
        )
        files = [self.effective_path("test_me.py")]

        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(
            files=files,
            expand_star_imports=False,
        )

    def test_list_value_pyproject_toml(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "pyproject.toml",
            '[tool.autoflake]\nimports=["my_lib", "other_lib"]\n',
        )
        files = [self.effective_path("test_me.py")]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(
            files=files,
            imports="my_lib,other_lib",
        )

    def test_list_value_comma_sep_string_pyproject_toml(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "pyproject.toml",
            '[tool.autoflake]\nimports="my_lib,other_lib"\n',
        )
        files = [self.effective_path("test_me.py")]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(
            files=files,
            imports="my_lib,other_lib",
        )

    def test_list_value_setup_cfg(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "setup.cfg",
            "[autoflake]\nimports=my_lib,other_lib\n",
        )
        files = [self.effective_path("test_me.py")]
        args, success = autoflake.merge_configuration_file({"files": files})
        assert success is True
        assert args == self.with_defaults(
            files=files,
            imports="my_lib,other_lib",
        )

    def test_non_bool_value_for_bool_property(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "pyproject.toml",
            '[tool.autoflake]\nexpand-star-imports="invalid"\n',
        )
        files = [self.effective_path("test_me.py")]
        _, success = autoflake.merge_configuration_file({"files": files})
        assert success is False

    def test_non_bool_value_for_bool_property_in_setup_cfg(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "setup.cfg",
            "[autoflake]\nexpand-star-imports=ok\n",
        )
        files = [self.effective_path("test_me.py")]
        _, success = autoflake.merge_configuration_file({"files": files})
        assert success is False

    def test_non_list_value_for_list_property(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "pyproject.toml",
            "[tool.autoflake]\nexclude=true\n",
        )
        files = [self.effective_path("test_me.py")]
        _, success = autoflake.merge_configuration_file({"files": files})
        assert success is False

    def test_merge_with_cli_set_list_property(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "pyproject.toml",
            '[tool.autoflake]\nimports=["my_lib"]\n',
        )
        files = [self.effective_path("test_me.py")]
        args, success = autoflake.merge_configuration_file(
            {"files": files, "imports": "other_lib"},
        )
        assert success is True
        assert args == self.with_defaults(
            files=files,
            imports="my_lib,other_lib",
        )

    def test_merge_prioritizes_flags(self) -> None:
        self.create_file("test_me.py")
        self.create_file(
            "pyproject.toml",
            "[tool.autoflake]\ncheck = false\n",
        )
        files = [self.effective_path("test_me.py")]
        flag_args = {
            "files": files,
            "imports": "other_lib",
            "check": True,
        }
        args, success = autoflake.merge_configuration_file(flag_args)
        assert success is True
        assert args == self.with_defaults(
            files=files,
            imports="other_lib",
            check=True,
        )


@contextlib.contextmanager
def temporary_file(
    contents: str,
    directory: str = ".",
    suffix: str = ".py",
    prefix: str = "",
) -> Iterator[str]:
    """Write contents to temporary file and yield it."""
    f = tempfile.NamedTemporaryFile(
        suffix=suffix,
        prefix=prefix,
        delete=False,
        dir=directory,
    )
    try:
        f.write(contents.encode())
        f.close()
        yield f.name
    finally:
        os.remove(f.name)


@contextlib.contextmanager
def temporary_directory(directory: str = ".", prefix: str = "tmp.") -> Iterator[str]:
    """Create temporary directory and yield its path."""
    temp_directory = tempfile.mkdtemp(prefix=prefix, dir=directory)
    try:
        yield temp_directory
    finally:
        shutil.rmtree(temp_directory)


class StubFile:
    """Fake file that ignores everything."""

    def write(*_: Any) -> None:
        """Ignore."""


if __name__ == "__main__":
    unittest.main()
