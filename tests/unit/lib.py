"""Test library utilities."""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from sqlalchemy import (
    CheckConstraint,
    Column,
    Double,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    text
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from ..assertions import eq_, expect_warnings, is_false, is_true

class TestBase:
    """Base class for test cases."""
    
    k_window_test_size = 1000  # Default window size for tests
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.engine = create_engine('sqlite:///:memory:')
        self.metadata = MetaData()
        self.session = Session(self.engine)
    
    def teardown_method(self):
        """Clean up test environment."""
        if hasattr(self, 'session'):
            self.session.close()
        if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

class FileCreator:
    """Utility for creating test files."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize with optional base directory."""
        self.base_dir = base_dir or tempfile.mkdtemp()
        self.files: Dict[str, str] = {}
    
    def create_file(self, path: str, content: str = '') -> str:
        """Create a file with given path and content."""
        full_path = Path(self.base_dir) / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        self.files[path] = content
        return str(full_path)
    
    def cleanup(self) -> None:
        """Clean up created files."""
        if os.path.exists(self.base_dir):
            import shutil
            shutil.rmtree(self.base_dir)

def combinations(*args: List[Any]) -> List[Tuple[Any, ...]]:
    """Generate combinations of test parameters."""
    if not args:
        return [()]
    result = []
    for item in args[0]:
        for rest in combinations(*args[1:]):
            result.append((item,) + rest)
    return result
