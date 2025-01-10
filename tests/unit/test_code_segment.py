from pyflakes import messages as m
from pyflakes.checker import (
    Argument,
    Assignment,
    ClassScope,
    FunctionDefinition,
    FunctionScope,
    ModuleScope,
)
from pyflakes.test.harness import TestCase


class TestCodeSegments(TestCase):
    """Tests for segments of a module."""

    def test_function_segment(self):
        self.flakes(
            """
        def foo():
            def bar():
                pass
        """,
            is_segment=True,
        )

        self.flakes(
            """
        def foo():
            def bar():
                x = 0
        """,
            m.UnusedVariable,
            is_segment=True,
        )

    def test_class_segment(self):
        self.flakes(
            """
        class Foo:
            class Bar:
                pass
        """,
            is_segment=True,
        )

        self.flakes(
            """
        class Foo:
            def bar():
                x = 0
        """,
            m.UnusedVariable,
            is_segment=True,
        )

    def test_scope_class(self):
        checker = self.flakes(
            """
        class Foo:
            x = 0
            def bar(a, b=1, *d, **e):
                pass
        """,
            is_segment=True,
        )

        scopes = checker.deadScopes
        module_scopes = [scope for scope in scopes if scope.__class__ is ModuleScope]
        class_scopes = [scope for scope in scopes if scope.__class__ is ClassScope]
        function_scopes = [scope for scope in scopes if scope.__class__ is FunctionScope]

        # Ensure module scope is not present because we are analysing
        # the inner contents of Foo
        assert len(module_scopes) == 0
        assert len(class_scopes) == 1
        assert len(function_scopes) == 1

        class_scope = class_scopes[0]
        function_scope = function_scopes[0]

        assert isinstance(class_scope, ClassScope)
        assert isinstance(function_scope, FunctionScope)

        assert "x" in class_scope
        assert "bar" in class_scope

        assert "a" in function_scope
        assert "b" in function_scope
        assert "d" in function_scope
        assert "e" in function_scope

        assert isinstance(class_scope["bar"], FunctionDefinition)
        assert isinstance(class_scope["x"], Assignment)

        assert isinstance(function_scope["a"], Argument)
        assert isinstance(function_scope["b"], Argument)
        assert isinstance(function_scope["d"], Argument)
        assert isinstance(function_scope["e"], Argument)

    def test_scope_function(self):
        checker = self.flakes(
            """
        def foo(a, b=1, *d, **e):
            def bar(f, g=1, *h, **i):
                pass
        """,
            is_segment=True,
        )

        scopes = checker.deadScopes
        module_scopes = [scope for scope in scopes if scope.__class__ is ModuleScope]
        function_scopes = [scope for scope in scopes if scope.__class__ is FunctionScope]

        # Ensure module scope is not present because we are analysing
        # the inner contents of foo
        assert len(module_scopes) == 0
        assert len(function_scopes) == 2

        function_scope_foo = function_scopes[1]
        function_scope_bar = function_scopes[0]

        assert isinstance(function_scope_foo, FunctionScope)
        assert isinstance(function_scope_bar, FunctionScope)

        assert "a" in function_scope_foo
        assert "b" in function_scope_foo
        assert "d" in function_scope_foo
        assert "e" in function_scope_foo
        assert "bar" in function_scope_foo

        assert "f" in function_scope_bar
        assert "g" in function_scope_bar
        assert "h" in function_scope_bar
        assert "i" in function_scope_bar

        assert isinstance(function_scope_foo["bar"], FunctionDefinition)
        assert isinstance(function_scope_foo["a"], Argument)
        assert isinstance(function_scope_foo["b"], Argument)
        assert isinstance(function_scope_foo["d"], Argument)
        assert isinstance(function_scope_foo["e"], Argument)

        assert isinstance(function_scope_bar["f"], Argument)
        assert isinstance(function_scope_bar["g"], Argument)
        assert isinstance(function_scope_bar["h"], Argument)
        assert isinstance(function_scope_bar["i"], Argument)

    def test_scope_async_function(self):
        self.flakes("async def foo(): pass", is_segment=True)
