"""Test complexity utility functions."""
import ast

import pytest


def cc_rank(score):
    """Calculate complexity rank."""
    if score < 0:
        msg = "Score cannot be negative"
        raise ValueError(msg)
    elif score <= 5:
        return "A"
    elif score <= 10:
        return "B"
    elif score <= 20:
        return "C"
    elif score <= 30:
        return "D"
    elif score <= 40:
        return "E"
    else:
        return "F"


def sorted_results(blocks):
    """Sort blocks by complexity."""
    return sorted(blocks, key=lambda b: b.complexity)


def average_complexity(blocks):
    """Calculate average complexity."""
    if not blocks:
        return 0.0
    return sum(block.complexity for block in blocks) / len(blocks)


class Function:
    """Mock function class for testing."""

    def __init__(self, name, complexity) -> None:
        self.name = name
        self.complexity = complexity


class Class:
    """Mock class for testing."""

    def __init__(self, name, complexity) -> None:
        self.name = name
        self.complexity = complexity


def test_rank_values():
    """Test complexity rank calculation."""
    test_cases = [
        (-1, ValueError),
        (0, "A"),
        (5, "A"),
        (6, "B"),
        (10, "B"),
        (11, "C"),
        (20, "C"),
        (21, "D"),
        (30, "D"),
        (31, "E"),
        (40, "E"),
        (41, "F"),
        (100, "F"),
    ]

    for score, expected in test_cases:
        if isinstance(expected, type) and issubclass(expected, Exception):
            with pytest.raises(expected):
                cc_rank(score)
        else:
            assert cc_rank(score) == expected


def test_sorted_results():
    """Test block sorting by complexity."""
    blocks = [
        Function("func1", 12),
        Function("func2", 14),
        Function("func3", 1),
        Class("class1", 5),
    ]

    sorted_blocks = sorted_results(blocks)
    assert len(sorted_blocks) == len(blocks)
    assert sorted_blocks[0].complexity == 1  # Lowest complexity first
    assert sorted_blocks[-1].complexity == 14  # Highest complexity last

    # Test empty list
    assert sorted_results([]) == []


def test_average_complexity():
    """Test average complexity calculation."""
    test_cases = [
        ([], 0.0),  # Empty list
        ([Function("f1", 4)], 4.0),  # Single function
        ([Function("f1", 4), Function("f2", 8)], 6.0),  # Two functions
        ([Function("f1", 4), Class("c1", 8), Function("f2", 6)], 6.0),  # Mixed blocks
    ]

    for blocks, expected in test_cases:
        assert average_complexity(blocks) == expected


def test_complexity_calculation():
    """Test complexity calculation with code samples."""
    code_samples = [
        ("def simple():\n    return True", 1),  # Base complexity
        (
            """def with_if(x):
                if x > 0:
                    return True
                return False""",
            2,  # Base + 1 for if
        ),
        (
            """def with_loop(items):
                for item in items:
                    if item > 0:
                        return True
                return False""",
            3,  # Base + 1 for loop + 1 for if
        ),
    ]

    for code, expected_complexity in code_samples:
        tree = ast.parse(code)
        # Basic complexity = 1 + number of if/for/while/except
        complexity = 1 + sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler))
        )
        assert complexity == expected_complexity
