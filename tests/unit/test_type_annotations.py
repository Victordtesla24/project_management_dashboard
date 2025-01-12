"""Tests for behaviour related to type annotations."""

import unittest
from typing import Dict, List, Optional, Set, Tuple, Union, cast


class TestTypeAnnotations(unittest.TestCase):
    type_options: Dict[str, Union[str, List[str], Set[str], Tuple[str, ...], Optional[str]]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.type_options = {
            "name": "test_type",
            "values": ["value1", "value2"],
            "unique_values": {"unique1", "unique2"},
            "tuple_values": ("tuple1", "tuple2"),
            "optional_value": None,
        }

    def test_type_annotations(self) -> None:
        """Test basic type annotation functionality."""
        assert self.type_options is not None
        assert self.type_options["name"] == "test_type"
        self.assertListEqual(cast(List[str], self.type_options["values"]), ["value1", "value2"])
        self.assertSetEqual(
            cast(Set[str], self.type_options["unique_values"]),
            {"unique1", "unique2"},
        )
        self.assertTupleEqual(
            cast(Tuple[str, ...], self.type_options["tuple_values"]),
            ("tuple1", "tuple2"),
        )
        assert self.type_options["optional_value"] is None
