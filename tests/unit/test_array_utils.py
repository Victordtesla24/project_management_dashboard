"""Unit tests for array utilities."""


from src.utils.array_utils import add_arrays, create_array, slice_array


def test_array_creation():
    """Test basic array creation."""
    arr = create_array([1, 2, 3])
    assert arr.shape == (3,)
    assert arr.dtype == int


def test_array_operations():
    """Test basic array operations."""
    arr1 = create_array([1, 2, 3])
    arr2 = create_array([4, 5, 6])
    result = add_arrays(arr1, arr2)
    assert all(result == [5, 7, 9])


def test_array_slicing():
    """Test array slicing."""
    arr = create_array([1, 2, 3, 4, 5])
    slice_result = slice_array(arr, 1, 4)
    assert all(slice_result == [2, 3, 4])
