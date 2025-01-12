# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/pylint-dev/pylint/blob/main/LICENSE
# Copyright (c) https://github.com/pylint-dev/pylint/blob/main/CONTRIBUTORS.txt

from __future__ import annotations

import configparser
import contextlib
import unittest
from os.path import basename, exists, join
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Callable


def parse_python_version(ver_str: str) -> tuple[int, ...]:
    """Convert python version to a tuple of integers for easy comparison."""
    return tuple(int(digit) for digit in ver_str.split("."))


class NoFileError(Exception):
    pass


class FileOptions(TypedDict):
    min_pyver: tuple[int, ...]
    max_pyver: tuple[int, ...]
    min_pyver_end_position: tuple[int, ...]
    requires: list[str]
    except_implementations: list[str]
    exclude_platforms: list[str]
    exclude_from_minimal_messages_config: bool


class TestFileOptions(unittest.TestCase):
    options: dict[str, object]
    file: str | None

    @classmethod
    def setUpClass(cls) -> None:
        cls.options = {
            "min_pyver": (),
            "max_pyver": (),
            "min_pyver_end_position": (),
            "requires": [],
            "except_implementations": [],
            "exclude_platforms": [],
            "exclude_from_minimal_messages_config": False,
        }
        cls.file = None

    def test_file_options(self):
        # Test implementation
        pass


# mypy need something literal, we can't create this dynamically from TestFileOptions
POSSIBLE_TEST_OPTIONS = {
    "min_pyver",
    "max_pyver",
    "min_pyver_end_position",
    "requires",
    "except_implementations",
    "exclude_platforms",
    "exclude_from_minimal_messages_config",
}


class FunctionalTestFile:
    """A single functional test case file with options."""

    _CONVERTERS: dict[str, Callable[[str], tuple[int, ...] | list[str]]] = {
        "min_pyver": parse_python_version,
        "max_pyver": parse_python_version,
        "min_pyver_end_position": parse_python_version,
        "requires": lambda s: [i.strip() for i in s.split(",")],
        "except_implementations": lambda s: [i.strip() for i in s.split(",")],
        "exclude_platforms": lambda s: [i.strip() for i in s.split(",")],
    }

    def __init__(self, directory: str, filename: str) -> None:
        self._directory = directory
        self.base = filename.replace(".py", "")
        self.options: dict[str, object] = {
            "min_pyver": (2, 5),
            "max_pyver": (4, 0),
            "min_pyver_end_position": (3, 8),
            "requires": [],
            "except_implementations": [],
            "exclude_platforms": [],
            "exclude_from_minimal_messages_config": False,
        }
        self._parse_options()

    def __repr__(self) -> str:
        return f"FunctionalTest:{self.base}"

    def _parse_options(self) -> None:
        cp = configparser.ConfigParser()
        cp.add_section("testoptions")
        with contextlib.suppress(NoFileError):
            cp.read(self.option_file)

        for name, value in cp.items("testoptions"):
            conv = self._CONVERTERS.get(name, lambda v: v)
            assert (
                name in POSSIBLE_TEST_OPTIONS
            ), f"[testoptions] can only contain one of {POSSIBLE_TEST_OPTIONS} and had '{name}'"
            self.options[name] = conv(value)

    @property
    def option_file(self) -> str:
        return self._file_type(".rc")

    @property
    def module(self) -> str:
        package = basename(self._directory)
        return f"{package}.{self.base}"

    @property
    def expected_output(self) -> str:
        return self._file_type(".txt", check_exists=False)

    @property
    def source(self) -> str:
        return self._file_type(".py")

    def _file_type(self, ext: str, check_exists: bool = True) -> str:
        name = join(self._directory, self.base + ext)
        if not check_exists or exists(name):
            return name
        msg = f"Cannot find '{name}'."
        raise NoFileError(msg)
