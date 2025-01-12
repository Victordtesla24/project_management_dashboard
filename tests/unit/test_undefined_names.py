import unittest
from typing import Dict, List, Optional, Set, Tuple, Union, cast


class TestUndefinedNames(unittest.TestCase):
    name_options: Dict[str, Union[str, List[str], Set[str], Tuple[str, ...], Optional[str]]]

    @classmethod
    def setUpClass(cls) -> None:
        cls.name_options = {
            "name": "test_undefined",
            "values": ["value1", "value2"],
            "unique_values": {"unique1", "unique2"},
            "tuple_values": ("tuple1", "tuple2"),
            "optional_value": None,
        }

    def test_undefined_names(self) -> None:
        """Test basic undefined names functionality."""
        assert self.name_options is not None
        assert self.name_options["name"] == "test_undefined"
        self.assertListEqual(cast(List[str], self.name_options["values"]), ["value1", "value2"])
        self.assertSetEqual(
            cast(Set[str], self.name_options["unique_values"]),
            {"unique1", "unique2"},
        )
        self.assertTupleEqual(
            cast(Tuple[str, ...], self.name_options["tuple_values"]),
            ("tuple1", "tuple2"),
        )
        assert self.name_options["optional_value"] is None
