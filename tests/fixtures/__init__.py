import pytest
from sqlalchemy import testing

class TablesTest:
    """Base class for tests that use tables."""
    
    @classmethod
    def setup_class(cls):
        """Set up any test class resources."""
        pass

    @classmethod
    def teardown_class(cls):
        """Clean up any test class resources."""
        pass

class TestBase:
    """Base class for all tests."""
    
    def setup_method(self, method):
        """Set up any test method resources."""
        pass
        
    def teardown_method(self, method):
        """Clean up any test method resources."""
        pass

class ComputedReflectionFixtureTest(TablesTest):
    """Base class for computed column reflection tests."""
    
    def normalize(self, sqltext):
        """Normalize SQL text for comparison."""
        return sqltext.lower().replace(' ', '')

# Export the classes
__all__ = ['TablesTest', 'TestBase', 'ComputedReflectionFixtureTest']
