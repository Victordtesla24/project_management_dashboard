"""Test cases for complexity visitor."""
import textwrap
from typing import List, Tuple


def dedent(text: str) -> str:
    """Remove common leading whitespace from every line in text."""
    return textwrap.dedent(text).strip()


# Test cases for general complexity analysis
GENERAL_CASES: List[Tuple[str, int]] = [
    # Simple function, complexity = 1
    (
        dedent(
            """
    def simple():
        return True
    """,
        ),
        1,
    ),
    # Function with if statement, complexity = 2
    (
        dedent(
            """
    def with_if(x):
        if x > 0:
            return True
        return False
    """,
        ),
        2,
    ),
    # Function with if/else, complexity = 2
    (
        dedent(
            """
    def with_if_else(x):
        if x > 0:
            return True
        else:
            return False
    """,
        ),
        2,
    ),
    # Function with nested if, complexity = 3
    (
        dedent(
            """
    def nested_if(x, y):
        if x > 0:
            if y > 0:
                return True
        return False
    """,
        ),
        3,
    ),
    # Function with for loop, complexity = 2
    (
        dedent(
            """
    def with_for(items):
        for item in items:
            print(item)
    """,
        ),
        2,
    ),
    # Function with while loop, complexity = 2
    (
        dedent(
            """
    def with_while(x):
        while x > 0:
            x -= 1
    """,
        ),
        2,
    ),
    # Function with try/except, complexity = 2
    (
        dedent(
            """
    def with_try():
        try:
            return True
        except:
            return False
    """,
        ),
        2,
    ),
    # Complex function with multiple branches, complexity = 6
    (
        dedent(
            """
    def complex(x, y, items):
        if x > 0:
            if y > 0:
                for item in items:
                    if item > 0:
                        return True
        return False
    """,
        ),
        6,
    ),
]

# Test cases for specific Python constructs
SPECIFIC_CASES: List[Tuple[str, int]] = [
    # List comprehension, complexity = 2
    (
        dedent(
            """
    def list_comp(items):
        return [x for x in items if x > 0]
    """,
        ),
        2,
    ),
    # Generator expression, complexity = 2
    (
        dedent(
            """
    def gen_exp(items):
        return (x for x in items if x > 0)
    """,
        ),
        2,
    ),
    # Lambda function, complexity = 1
    (
        dedent(
            """
    lambda x: x + 1
    """,
        ),
        1,
    ),
    # Ternary operator, complexity = 2
    (
        dedent(
            """
    def ternary(x):
        return True if x > 0 else False
    """,
        ),
        2,
    ),
]

# Test cases for error handling
ERROR_CASES: List[Tuple[str, int]] = [
    # Multiple except blocks, complexity = 3
    (
        dedent(
            """
    def multiple_except():
        try:
            return True
        except ValueError:
            return False
        except TypeError:
            return None
    """,
        ),
        3,
    ),
    # Try/except/else/finally, complexity = 4
    (
        dedent(
            """
    def full_try():
        try:
            return True
        except:
            return False
        else:
            print("Success")
        finally:
            print("Done")
    """,
        ),
        4,
    ),
]
