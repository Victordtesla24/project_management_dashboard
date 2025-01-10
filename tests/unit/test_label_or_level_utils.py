"""Test label and level utility functions."""
from typing import Dict, List

import numpy as np
import pandas as pd
import pytest


@pytest.fixture()
def sample_data() -> Dict[str, List]:
    """Create sample data for testing."""
    return {"L1": [1, 2, 3], "L2": [11, 12, 13], "L3": ["A", "B", "C"]}


@pytest.fixture()
def df(sample_data: Dict[str, List]) -> pd.DataFrame:
    """Create test DataFrame."""
    return pd.DataFrame(sample_data)


@pytest.fixture()
def df_indexed(df: pd.DataFrame) -> pd.DataFrame:
    """Create indexed DataFrame."""
    return df.set_index(["L1", "L2"])


@pytest.fixture()
def df_with_duplicates(sample_data: Dict[str, List]) -> pd.DataFrame:
    """Create DataFrame with duplicate columns."""
    data = {
        "L1": sample_data["L1"],
        "L2_1": sample_data["L2"],
        "L2_2": sample_data["L2"],
        "L3": sample_data["L3"],
    }
    df = pd.DataFrame(data)
    df.columns = ["L1", "L2", "L2", "L3"]  # Rename to create duplicates
    return df


def test_basic_dataframe_structure(df: pd.DataFrame) -> None:
    """Test basic DataFrame structure."""
    assert isinstance(df, pd.DataFrame)
    assert all(col in df.columns for col in ["L1", "L2", "L3"])
    assert df.shape == (3, 3)
    assert df.index.nlevels == 1


def test_index_levels(df_indexed: pd.DataFrame) -> None:
    """Test index level structure."""
    assert df_indexed.index.names == ["L1", "L2"]
    assert df_indexed.index.nlevels == 2
    assert "L3" in df_indexed.columns
    assert len(df_indexed.columns) == 1


def test_level_values(df_indexed: pd.DataFrame) -> None:
    """Test getting level values."""
    l1_values = df_indexed.index.get_level_values("L1")
    l2_values = df_indexed.index.get_level_values("L2")

    np.testing.assert_array_equal(l1_values, [1, 2, 3])
    np.testing.assert_array_equal(l2_values, [11, 12, 13])


def test_drop_levels(df_indexed: pd.DataFrame) -> None:
    """Test dropping index levels."""
    # Drop first level
    df_l2 = df_indexed.droplevel("L1")
    assert df_l2.index.names == ["L2"]
    assert df_l2.index.nlevels == 1

    # Drop second level
    df_l1 = df_indexed.droplevel("L2")
    assert df_l1.index.names == ["L1"]
    assert df_l1.index.nlevels == 1


def test_duplicate_labels(df_with_duplicates: pd.DataFrame) -> None:
    """Test handling of duplicate column labels."""
    # Check duplicate detection
    assert df_with_duplicates.columns.tolist().count("L2") == 2
    assert len(df_with_duplicates.columns) == 4

    # Test duplicate column access
    with pytest.raises(pd.errors.InvalidIndexError):
        _ = df_with_duplicates.columns.get_indexer(["L2"])


def test_series_operations(df: pd.DataFrame) -> None:
    """Test operations on Series."""
    series = df.set_index("L1")["L2"]

    assert isinstance(series, pd.Series)
    assert series.index.name == "L1"
    np.testing.assert_array_equal(series.index, [1, 2, 3])
    np.testing.assert_array_equal(series.values, [11, 12, 13])


def test_invalid_operations(df: pd.DataFrame) -> None:
    """Test invalid operations raise appropriate errors."""
    # Test invalid column access
    with pytest.raises(KeyError, match="NonExistent"):
        df.set_index("NonExistent")

    # Test invalid level access
    df_indexed = df.set_index("L1")
    with pytest.raises(KeyError, match="NonExistent"):
        df_indexed.index.get_level_values("NonExistent")


def test_ambiguous_references(df: pd.DataFrame) -> None:
    """Test handling of ambiguous references."""
    # Create ambiguous situation
    df_ambig = df.set_index("L1")
    df_ambig["L1"] = range(len(df))

    # Verify ambiguous state
    assert "L1" in df_ambig.index.names
    assert "L1" in df_ambig.columns

    # Test access behavior - should return column not index
    result = df_ambig["L1"]
    assert isinstance(result, pd.Series)
    np.testing.assert_array_equal(result.values, [0, 1, 2])


def test_index_manipulation(df: pd.DataFrame) -> None:
    """Test index manipulation operations."""
    # Test setting multiple indices
    df_multi = df.set_index(["L1", "L2"])
    assert df_multi.index.nlevels == 2

    # Test resetting index
    df_reset = df_multi.reset_index()
    assert df_reset.index.nlevels == 1
    assert all(col in df_reset.columns for col in ["L1", "L2"])
