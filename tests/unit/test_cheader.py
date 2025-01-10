"""Test header inclusion functionality."""
import os
import re
from typing import List

import pytest


def find_c_functions(source_files: List[str]) -> List[str]:
    """Find C function declarations in source files."""
    functions = []
    for file in source_files:
        if os.path.exists(file):
            with open(file) as f:
                content = f.read()
                # Find function declarations like: void func_name(args)
                matches = re.findall(r"\b\w+\s+(\w+)\s*\([^)]*\)", content)
                functions.extend(matches)
    return functions


def find_header_declarations(header_file: str) -> List[str]:
    """Find function declarations in header file."""
    if not os.path.exists(header_file):
        return []

    with open(header_file) as f:
        content = f.read()
        # Find function declarations in header
        return re.findall(r"\b\w+\s+(\w+)\s*\([^)]*\);", content)


def test_header_declarations():
    """Test that C functions are properly declared in headers."""
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    # Define paths relative to project root
    src_dir = os.path.join(project_root, "src")
    include_dir = os.path.join(project_root, "include")

    # Skip test if directories don't exist
    if not os.path.exists(src_dir) or not os.path.exists(include_dir):
        pytest.skip("Source or include directories not found")

    # Find all .c files
    c_files = []
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".c"):
                c_files.append(os.path.join(root, file))

    # Find all .h files
    h_files = []
    for root, _, files in os.walk(include_dir):
        for file in files:
            if file.endswith(".h"):
                h_files.append(os.path.join(root, file))

    # Skip test if no C files found
    if not c_files:
        pytest.skip("No C source files found")

    # Get all function declarations from source files
    source_functions = set()
    for file in c_files:
        source_functions.update(find_c_functions(file))

    # Get all function declarations from header files
    header_functions = set()
    for file in h_files:
        header_functions.update(find_header_declarations(file))

    # Check that all source functions are declared in headers
    missing_declarations = source_functions - header_functions
    assert (
        not missing_declarations
    ), f"Functions missing header declarations: {missing_declarations}"


def test_header_include_guards():
    """Test that header files have include guards."""
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    include_dir = os.path.join(project_root, "include")

    # Skip test if include directory doesn't exist
    if not os.path.exists(include_dir):
        pytest.skip("Include directory not found")

    # Find all .h files
    h_files = []
    for root, _, files in os.walk(include_dir):
        for file in files:
            if file.endswith(".h"):
                h_files.append(os.path.join(root, file))

    # Skip test if no header files found
    if not h_files:
        pytest.skip("No header files found")

    # Check each header file for include guards
    for file in h_files:
        with open(file) as f:
            content = f.read()

            # Check for include guard pattern
            guard_pattern = re.compile(
                r"#ifndef\s+\w+_H"  # Start guard
                r".*?"  # Any content
                r"#define\s+\w+_H"  # Define guard
                r".*?"  # File content
                r"#endif",  # End guard
                re.DOTALL,
            )

            assert guard_pattern.search(content), f"Header file missing include guards: {file}"
