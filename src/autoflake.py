"""Removes unused imports and unused variables as reported by pyflakes."""

import ast
import re
import sys
import tokenize
from typing import Any, Iterator, Set

import pyflakes.api
import pyflakes.messages
import pyflakes.reporter

SAFE_IMPORTS = frozenset(["__future__"])


def standard_package_names() -> Set[str]:
    """Return list of standard module names."""
    names = set()
    for module in list(sys.modules.values()):
        if module:
            file_name = getattr(module, "__file__", "")
            if file_name and "site-packages" not in file_name:
                names.add(module.__name__)
    return names


def detect_encoding(filename: str) -> str:
    """Return file encoding."""
    try:
        with open(filename, "rb") as input_file:
            return tokenize.detect_encoding(input_file.readline)[0]
    except (OSError, SyntaxError):
        return "latin-1"


def _get_skip_file_directive(source: str) -> bool:
    """Return True if source contains a '# autoflake: skip_file' directive."""
    for line in source.splitlines():
        line = line.lstrip()
        if line.startswith("#"):
            if line.startswith("#!"):  # Skip shebang line
                continue
            # More lenient matching, similar to flake8's noqa
            if "autoflake:" in line and "skip_file" in line:
                return True
    return False


def check(source: str) -> Any:
    """Return True if source code is valid Python."""
    try:
        ast.parse(source)
        return True
    except (SyntaxError, TypeError):
        return False


def unused_import_line_numbers(checker: Any) -> Iterator[int]:
    """Yield line numbers of unused imports."""
    for message in checker.messages:
        if isinstance(message, pyflakes.messages.UnusedImport):
            yield message.lineno


def filter_unused_variable(line: str, drop_rhs: bool = False) -> str:
    """Return line with unused variables removed."""
    # Handle except statements
    if re.match(r"\s*except\s+.*\s+as\s+\w+:", line):
        return re.sub(r"(\s*except\s+.*)\s+as\s+\w+:", r"\1:", line)

    # Handle assignments
    if "=" in line and not line.strip().startswith("="):
        lhs = line[: line.index("=")].strip()
        if re.match(r"^[a-zA-Z_]\w*$", lhs):  # Simple variable assignment
            if drop_rhs:
                return "pass"
            else:
                rhs = line[line.index("=") + 1 :].strip()
                if re.match(r"^[a-zA-Z_]\w*$", rhs) or rhs in [
                    "{}",
                    "[]",
                    "()",
                    "dict()",
                    "list()",
                    "set()",
                ]:
                    return "pass"
                return rhs

    return line


def fix_code(source: str, **kwargs: Any) -> str:
    """Return fixed source code."""
    if not source:
        return source

    # Check for skip_file directive before any modifications
    if _get_skip_file_directive(source):
        return source

    # Only process the file if no skip directive is present
    try:
        tree = ast.parse(source)
    except (SyntaxError, TypeError):
        return source

    filtered_source = source

    if kwargs.get("expand_star_imports"):
        filtered_source = _fix_star_import(filtered_source, tree)
        tree = ast.parse(filtered_source)

    if kwargs.get("remove_all_unused_imports"):
        filtered_source = _remove_all_unused_imports(filtered_source, tree)
        tree = ast.parse(filtered_source)

    if kwargs.get("remove_duplicate_keys"):
        filtered_source = _remove_duplicate_keys(filtered_source, tree)
        tree = ast.parse(filtered_source)

    if kwargs.get("remove_unused_variables"):
        filtered_source = _remove_unused_variables(
            filtered_source,
            tree,
            remove_rhs_for_unused_variables=kwargs.get("remove_rhs_for_unused_variables", False),
        )
        tree = ast.parse(filtered_source)

    if kwargs.get("ignore_init_module_imports"):
        filtered_source = _remove_unused_imports(
            filtered_source,
            tree,
            ignore_init_module_imports=True,
        )
        tree = ast.parse(filtered_source)

    if kwargs.get("ignore_pass_statements"):
        filtered_source = _remove_useless_pass(filtered_source, tree)
        tree = ast.parse(filtered_source)

    if kwargs.get("ignore_pass_after_docstring"):
        filtered_source = _remove_useless_pass_after_docstring(filtered_source, tree)
        tree = ast.parse(filtered_source)

    return filtered_source


def _main(
    argv: list[str],
    standard_out: TextIO | None,
    standard_error: TextIO | None,
    *,
    apply_config: bool = True,
) -> int:
    """Return exit status.

    0 means no error.
    """
    import signal

    # Exit on broken pipe.
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    try:
        args = _process_args(argv, standard_error)
    except SystemExit as e:
        return e.code

    if standard_out is None:
        standard_out = sys.stdout

    if standard_error is None:
        standard_error = sys.stderr

    if apply_config:
        args, success = merge_configuration_file(args)
        if not success:
            return 1

    check = args.get("check", False)
    exit_code = 0

    for name in args["files"]:
        try:
            with open(name, encoding=args["encoding"]) as f:
                source = f.read()

            # Check for skip_file directive before any processing
            if _get_skip_file_directive(source):
                if args.get("stdout"):
                    standard_out.write(source)
                continue

            # Only process the file if no skip directive is present
            filtered_source = source
            try:
                tree = ast.parse(source)
                if not args.get("ignore_init_module_imports") or not source.strip().endswith(
                    "__init__.py",
                ):
                    filtered_source = filter_imports(
                        filtered_source,
                        tree,
                        args.get("remove_all_unused_imports", False),
                    )

                # Expand star imports
                if args.get("expand_star_imports"):
                    filtered_source = expand_star_imports(filtered_source, tree)

                # Filter unused variables
                if args.get("remove_unused_variables"):
                    filtered_source = filter_unused_variable(
                        filtered_source,
                        args.get("remove_rhs_for_unused_variables"),
                    )

                # Filter useless pass statements
                if not args.get("ignore_pass_statements"):
                    filtered_source = filter_useless_pass(
                        filtered_source,
                        args.get("ignore_pass_after_docstring"),
                    )

                # Remove duplicate keys
                if args.get("remove_duplicate_keys"):
                    filtered_source = filter_code_with_duplicate_keys(filtered_source)
            except (SyntaxError, TypeError):
                filtered_source = source

            if check:
                if source != filtered_source:
                    exit_code = 1
                    print(
                        f"{name}: Autoflake failed to verify",
                        file=standard_error,
                    )
            else:
                if args.get("stdout"):
                    standard_out.write(filtered_source)
                else:
                    if source != filtered_source:
                        with open(name, "w", encoding=args["encoding"]) as f:
                            f.write(filtered_source)

        except OSError as e:
            print(e, file=standard_error)
            exit_code = 1

    return exit_code


def main() -> None:
    """Run the program."""
    try:
        sys.exit(_main(sys.argv[1:], sys.stdout, sys.stderr))
    except KeyboardInterrupt:
        sys.exit(2)


def _load_toml_config(config_file: str) -> tuple[dict, bool]:
    """Load configuration from TOML file.
    Returns a tuple of (config_dict, success).
    """
    try:
        import tomli
    except ImportError:
        try:
            import toml as tomli
        except ImportError:
            print("TOML configuration requires 'tomli' or 'toml' package.", file=sys.stderr)
            return {}, False

    try:
        with open(config_file, "rb") as f:
            config = tomli.load(f)
            # Check for tool.autoflake section first (preferred)
            if "tool" in config and "autoflake" in config["tool"]:
                return dict(config["tool"]["autoflake"]), True
            # Fallback to autoflake section
            if "autoflake" in config:
                return dict(config["autoflake"]), True
            # No config found is not an error
            return {}, True
    except Exception as e:
        print(f"Error reading TOML config file: {e}", file=sys.stderr)
        return {}, False


def _convert_config_values(config: dict) -> dict:
    """Convert configuration values to appropriate types."""
    converted_config = {}
    for key, value in config.items():
        if isinstance(value, bool):  # Handle native boolean values from TOML
            converted_config[key] = value
        elif isinstance(value, str):
            if value.lower() in ("true", "yes", "1", "on"):
                converted_config[key] = True
            elif value.lower() in ("false", "no", "0", "off"):
                converted_config[key] = False
            elif "," in value:
                converted_config[key] = [v.strip() for v in value.split(",")]
            else:
                converted_config[key] = value
        elif isinstance(value, (list, tuple)):  # Handle native lists from TOML
            converted_config[key] = list(value)
        else:
            converted_config[key] = value
    return converted_config


def merge_configuration_file(args: dict) -> tuple[dict, bool]:
    """Merge configuration file settings with command-line options.
    Command-line options take precedence over config file settings.
    Returns a tuple of (updated_args, success).
    """
    config_file = args.get("config_file")
    if not config_file:
        return args, True

    try:
        if config_file.endswith(".toml"):
            config, success = _load_toml_config(config_file)
            if not success:
                return args, False
        else:
            import configparser

            config = configparser.ConfigParser()
            config.read(config_file)
            if "autoflake" not in config.sections():
                return args, True
            config = dict(config["autoflake"])

        # Convert config values to appropriate types
        converted_config = _convert_config_values(config)

        # Create a new dict with config values, then override with command line args
        result = args.copy()  # Start with command line args
        # Only update with config values if they're not already set by command line
        for key, value in converted_config.items():
            if key not in result or result[key] is None:
                result[key] = value

        return result, True

    except Exception as e:
        print(f"Error reading config file: {e}", file=sys.stderr)
        return args, False


def _process_args(argv: list[str], standard_error: TextIO | None) -> dict:
    """Process command line arguments."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__, prog="autoflake")
    parser.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help="make changes to files instead of printing diffs",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="drill down directories recursively",
    )
    parser.add_argument(
        "--exclude",
        metavar="globs",
        help="exclude files/directories that match these comma-separated globs",
    )
    parser.add_argument(
        "--remove-all-unused-imports",
        action="store_true",
        help="remove all unused imports (not just those from the standard library)",
    )
    parser.add_argument(
        "--ignore-init-module-imports",
        action="store_true",
        help="exclude __init__.py when removing unused imports",
    )
    parser.add_argument(
        "--remove-duplicate-keys",
        action="store_true",
        help="remove all duplicate keys in objects",
    )
    parser.add_argument(
        "--remove-unused-variables",
        action="store_true",
        help="remove unused variables",
    )
    parser.add_argument(
        "--remove-rhs-for-unused-variables",
        action="store_true",
        help="remove RHS of unused variable assignment",
    )
    parser.add_argument(
        "--ignore-pass-statements",
        action="store_true",
        help="ignore pass statements",
    )
    parser.add_argument(
        "--ignore-pass-after-docstring",
        action="store_true",
        help="ignore pass statements after docstrings",
    )
    parser.add_argument(
        "--expand-star-imports",
        action="store_true",
        help="expand wildcard star imports with undefined names",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="return error code if changes are needed",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="write changes to stdout instead of modifying files",
    )
    parser.add_argument(
        "--config",
        metavar="path",
        help="path to configuration file",
    )
    parser.add_argument(
        "--encoding",
        help="specify encoding of the input files",
        default="utf-8",
    )
    parser.add_argument("files", nargs="+", help="files to format")

    args = parser.parse_args(argv[1:])
    args_dict = vars(args)

    if args.config:
        args_dict["config_file"] = args.config

    return args_dict


def filter_code(source: str, tree: ast.AST, args: dict) -> str:
    """Return filtered source code."""
    if _get_skip_file_directive(source):
        return source

    # Get line ending
    get_line_ending(source)

    # Filter imports
    filtered_source = source
    if not args.get("ignore_init_module_imports") or not source.strip().endswith("__init__.py"):
        filtered_source = filter_imports(
            filtered_source,
            tree,
            args.get("remove_all_unused_imports", False),
        )

    # Expand star imports
    if args.get("expand_star_imports"):
        filtered_source = expand_star_imports(filtered_source, tree)

    return filtered_source


def filter_imports(source: str, tree: ast.AST, remove_all_unused_imports: bool) -> str:
    """Return source code with unused imports removed."""
    imports = find_imports(tree)
    assert imports is not None

    get_line_ending(source)
    result = source

    for node in imports:
        if isinstance(node, ast.ImportFrom):
            # Handle "from" imports
            for name in node.names:
                if not name.asname and not is_name_used(name.name, tree):
                    result = remove_import(result, node, name)
        else:
            # Handle regular imports
            for name in node.names:
                if not name.asname and not is_name_used(name.name, tree):
                    if remove_all_unused_imports or is_from_stdlib(name.name):
                        result = remove_import(result, node, name)

    return result


def find_imports(tree: ast.AST) -> list[ast.Import | ast.ImportFrom]:
    """Return list of import statements."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(node)
    return imports


def is_name_used(name: str, tree: ast.AST) -> bool:
    """Return True if name is used in tree."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == name:
            return True
    return False


def is_from_stdlib(name: str) -> bool:
    """Return True if name is from Python standard library."""
    return name in sys.stdlib_module_names


def remove_import(source: str, node: ast.AST, name: ast.alias) -> str:
    """Return source code with import statement removed."""
    if isinstance(node, ast.ImportFrom):
        # Handle "from" imports
        if len(node.names) == 1:
            # Remove entire import statement
            return remove_lines(source, node.lineno, node.end_lineno)
        else:
            # Remove only the specified name
            return remove_name_from_import(source, node.lineno, name.name)
    else:
        # Handle regular imports
        if len(node.names) == 1:
            # Remove entire import statement
            return remove_lines(source, node.lineno, node.end_lineno)
        else:
            # Remove only the specified name
            return remove_name_from_import(source, node.lineno, name.name)


def remove_lines(source: str, start: int, end: int | None = None) -> str:
    """Return source code with lines removed."""
    lines = source.splitlines()
    if end is None:
        end = start
    del lines[start - 1 : end]
    return "\n".join(lines) + "\n"


def remove_name_from_import(source: str, lineno: int, name: str) -> str:
    """Return source code with name removed from import statement."""
    lines = source.splitlines()
    line = lines[lineno - 1]
    if "," in line:
        # Multiple imports on one line
        parts = line.split(",")
        for i, part in enumerate(parts):
            if name in part:
                del parts[i]
                break
        lines[lineno - 1] = ",".join(parts)
    else:
        # Single import on one line
        lines[lineno - 1] = line.replace(name, "")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
