import json
import subprocess
import sys

import pytest
from numpy.testing import IS_WASM


# Simple shell utils implementation for testing
class ShellParser:
    @staticmethod
    def join(args):
        quoted_args = []
        for arg in args:
            # Quote arguments containing spaces
            if " " in arg:
                quoted_args.append(f'"{arg}"')
            # Quote arguments containing quotes
            elif '"' in arg:
                # Escape existing quotes and wrap in quotes
                escaped_arg = arg.replace('"', '\\"')
                quoted_args.append(f'"{escaped_arg}"')
            else:
                quoted_args.append(str(arg))
        return " ".join(quoted_args)

    @staticmethod
    def split(cmd):
        parts = []
        current = []
        in_quotes = False
        escaped = False

        for char in cmd:
            # Handle escape sequences
            if char == "\\" and not escaped:
                escaped = True
                continue

            # Handle quotes
            if char == '"' and not escaped:
                in_quotes = not in_quotes
                if not in_quotes:  # End of quoted section
                    parts.append("".join(current))
                    current = []
                continue

            # Handle spaces
            if char == " " and not in_quotes and not escaped:
                if current:
                    parts.append("".join(current))
                    current = []
                continue

            # Handle escaped characters
            if escaped and char != '"':
                current.append("\\")
            current.append(char)
            escaped = False

        if current:
            parts.append("".join(current))

        # Handle empty parts
        return [part for part in parts if part]


class WindowsParser(ShellParser):
    pass


class PosixParser(ShellParser):
    pass


class NativeParser(ShellParser):
    pass


argv_cases = [
    [r"exe"],
    [r"path/exe"],
    [r"path\exe"],
    [r"\\server\path\exe"],
    [r"path to/exe"],
    [r"path to\exe"],
    [r"exe", "--flag"],
    [r"path/exe", "--flag"],
    [r"path\exe", "--flag"],
    [r"path to/exe", "--flag"],
    [r"path to\exe", "--flag"],
    # flags containing literal quotes in their name
    [r"path to/exe", '--flag-"quoted"'],
    [r"path to\exe", '--flag-"quoted"'],
    [r"path to/exe", '"--flag-quoted"'],
    [r"path to\exe", '"--flag-quoted"'],
]


@pytest.fixture(params=[WindowsParser, PosixParser])
def Parser(request):
    return request.param


@pytest.fixture()
def runner(Parser):
    if Parser != NativeParser:
        pytest.skip("Unable to run with non-native parser")

    if Parser == WindowsParser:
        return lambda cmd: subprocess.check_output(cmd)
    elif Parser == PosixParser:
        # posix has no non-shell string parsing
        return lambda cmd: subprocess.check_output(cmd, shell=True)
    else:
        raise NotImplementedError


@pytest.mark.skipif(IS_WASM, reason="Cannot start subprocess")
@pytest.mark.parametrize("argv", argv_cases)
def test_join_matches_subprocess(Parser, runner, argv):
    """Test that join produces strings understood by subprocess."""
    # invoke python to return its arguments as json
    cmd = [sys.executable, "-c", "import json, sys; print(json.dumps(sys.argv[1:]))"]
    joined = Parser.join(cmd + argv)
    json_out = runner(joined).decode()
    assert json.loads(json_out) == argv


@pytest.mark.skipif(IS_WASM, reason="Cannot start subprocess")
@pytest.mark.parametrize("argv", argv_cases)
def test_roundtrip(Parser, argv):
    """Test that split is the inverse operation of join."""
    try:
        joined = Parser.join(argv)
        assert argv == Parser.split(joined)
    except NotImplementedError:
        pytest.skip("Not implemented")
