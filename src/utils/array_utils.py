"""Array utility functions."""

import numpy as np


def create_array(data):
    """Create a numpy array from input data."""
    return np.array(data)


def add_arrays(arr1, arr2):
    """Add two arrays element-wise."""
    return arr1 + arr2


def slice_array(arr, start, end):
    """Slice an array from start to end index."""
    return arr[start:end]
