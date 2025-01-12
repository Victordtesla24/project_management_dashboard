# Copyright (C) 2010, 2011 Sebastian Thiel (byronimo@gmail.com) and contributors
#
# This module is part of GitDB and is released under
# the New BSD License: https://opensource.org/license/bsd-3-clause/
"""Test for object db."""
import os
import tempfile
import unittest
from typing import Dict, List, Optional, Set, Tuple, Union, cast

from gitdb.util import NULL_HEX_SHA, LockedFD, to_hex_sha


class TestUtils(unittest.TestCase):
    util_options: Dict[str, Union[str, List[str], Set[str], Tuple[str, ...], Optional[str]]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.util_options = {
            "name": "test_util",
            "values": ["value1", "value2"],
            "unique_values": {"unique1", "unique2"},
            "tuple_values": ("tuple1", "tuple2"),
            "optional_value": None,
        }

    def test_utils(self) -> None:
        """Test basic utility functionality."""
        assert self.util_options is not None
        assert self.util_options["name"] == "test_util"
        self.assertListEqual(cast(List[str], self.util_options["values"]), ["value1", "value2"])
        self.assertSetEqual(
            cast(Set[str], self.util_options["unique_values"]),
            {"unique1", "unique2"},
        )
        self.assertTupleEqual(
            cast(Tuple[str, ...], self.util_options["tuple_values"]),
            ("tuple1", "tuple2"),
        )
        assert self.util_options["optional_value"] is None

    def test_basics(self):
        assert to_hex_sha(NULL_HEX_SHA) == NULL_HEX_SHA

    def _cmp_contents(self, file_path, data):
        # raise if data from file at file_path
        # does not match data string
        with open(file_path, "rb") as fp:
            assert fp.read() == data.encode("ascii")

    def test_lockedfd(self):
        my_file = tempfile.mktemp()
        orig_data = "hello"
        new_data = "world"
        with open(my_file, "wb") as my_file_fp:
            my_file_fp.write(orig_data.encode("ascii"))

        try:
            lfd = LockedFD(my_file)
            lockfilepath = lfd._lockfilepath()

            # cannot end before it was started
            self.assertRaises(AssertionError, lfd.rollback)
            self.assertRaises(AssertionError, lfd.commit)

            # open for writing
            assert not os.path.isfile(lockfilepath)
            wfd = lfd.open(write=True)
            assert lfd._fd is wfd
            assert os.path.isfile(lockfilepath)

            # write data and fail
            os.write(wfd, new_data.encode("ascii"))
            lfd.rollback()
            assert lfd._fd is None
            self._cmp_contents(my_file, orig_data)
            assert not os.path.isfile(lockfilepath)

            # additional call doesn't fail
            lfd.commit()
            lfd.rollback()

            # test reading
            lfd = LockedFD(my_file)
            rfd = lfd.open(write=False)
            assert os.read(rfd, len(orig_data)) == orig_data.encode("ascii")

            assert os.path.isfile(lockfilepath)
            # deletion rolls back
            del lfd
            assert not os.path.isfile(lockfilepath)

            # write data - concurrently
            lfd = LockedFD(my_file)
            olfd = LockedFD(my_file)
            assert not os.path.isfile(lockfilepath)
            wfdstream = lfd.open(write=True, stream=True)  # this time as stream
            assert os.path.isfile(lockfilepath)
            # another one fails
            self.assertRaises(IOError, olfd.open)

            wfdstream.write(new_data.encode("ascii"))
            lfd.commit()
            assert not os.path.isfile(lockfilepath)
            self._cmp_contents(my_file, new_data)

            # could test automatic _end_writing on destruction
        finally:
            os.remove(my_file)
        # END final cleanup

        # try non-existing file for reading
        lfd = LockedFD(tempfile.mktemp())
        try:
            lfd.open(write=False)
        except OSError:
            assert not os.path.exists(lfd._lockfilepath())
        else:
            self.fail("expected OSError")
        # END handle exceptions
