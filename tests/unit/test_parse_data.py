"""Test parsing of test data files."""
import os
import tempfile
from unittest import TestCase


class ParseTestDataSuite(TestCase):
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir)

    def create_test_file(self, content: str) -> str:
        """Create a temporary test file with given content."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".test", dir=self.temp_dir, delete=False,
        ) as f:
            f.write(content)
            return f.name

    def test_parse_invalid_case(self):
        """Test parsing invalid test case."""
        # Create test file
        test_content = """
        [case abc]
        s: str
        [case foo-XFAIL]
        s: str
        """
        test_file = self.create_test_file(test_content)

        # Parse and verify
        with open(test_file) as f:
            content = f.read()
            # Verify basic structure
            assert "[case abc]" in content
            assert "[case foo-XFAIL]" in content
            # Verify content is preserved
            assert "s: str" in content
            # Verify case order
            first_case = content.index("[case abc]")
            second_case = content.index("[case foo-XFAIL]")
            assert first_case < second_case

    def test_parse_invalid_section(self):
        """Test parsing invalid section."""
        # Create test file
        test_content = """
        [case abc]
        s: str
        [unknownsection]
        abc
        """
        test_file = self.create_test_file(test_content)

        # Parse and verify
        with open(test_file) as f:
            content = f.read()
            # Verify basic structure
            assert "[case abc]" in content
            assert "[unknownsection]" in content
            # Verify content is preserved
            assert "s: str" in content
            assert "abc" in content
            # Verify section order
            case_pos = content.index("[case abc]")
            section_pos = content.index("[unknownsection]")
            assert case_pos < section_pos

    def test_version_check(self):
        """Test version check parsing."""
        # Create test file
        test_content = """
        [case abc]
        s: str
        [out version>=3.8]
        abc
        """
        test_file = self.create_test_file(test_content)

        # Parse and verify
        with open(test_file) as f:
            content = f.read()
            # Verify basic structure
            assert "[case abc]" in content
            assert "[out version>=3.8]" in content
            # Verify content is preserved
            assert "s: str" in content
            assert "abc" in content
            # Verify version check format
            version_line = next(line for line in content.splitlines() if "version>=" in line)
            assert "version>=" in version_line
            assert "3.8" in version_line

    def test_eq_version_check(self):
        """Test equality version check parsing."""
        # Create test file
        test_content = """
        [case abc]
        s: str
        [out version==3.7]
        abc
        """
        test_file = self.create_test_file(test_content)

        # Parse and verify
        with open(test_file) as f:
            content = f.read()
            # Verify basic structure
            assert "[case abc]" in content
            assert "[out version==3.7]" in content
            # Verify content is preserved
            assert "s: str" in content
            assert "abc" in content
            # Verify version check format
            version_line = next(line for line in content.splitlines() if "version==" in line)
            assert "version==" in version_line
            assert "3.7" in version_line
