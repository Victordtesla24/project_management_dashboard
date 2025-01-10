"""Test memory management functionality."""
from copy import copy

from smmap.mman import SlidingWindowMapManager, StaticWindowMapManager, WindowCursor

from .lib import FileCreator, TestBase


class TestMMan(TestBase):
    def test_cursor(self):
        """Test cursor operations."""
        fc = FileCreator()
        try:
            # Create a test file with known content
            test_content = "x" * self.k_window_test_size
            test_path = fc.create_file("cursor_test", test_content)

            man = SlidingWindowMapManager()
            ci = WindowCursor(man)  # invalid cursor
            assert not ci.is_valid()
            assert not ci.is_associated()
            assert ci.size() == 0  # cached, can query in invalid state

            cv = man.make_cursor(test_path)
            assert not cv.is_valid()  # no region mapped yet
            assert cv.is_associated()  # but knows where to map from
            assert cv.file_size() == len(test_content)
            assert cv.path() == test_path

            # Test copy
            cio = copy(cv)
            assert not cio.is_valid()
            assert cio.is_associated()

            # Test assign
            assert not ci.is_associated()
            ci.assign(cv)
            assert not ci.is_valid()
            assert ci.is_associated()

            # Test unuse and destroy
            cv.unuse_region()
            cv.unuse_region()  # multiple unuse is fine
            cv._destroy()
            WindowCursor(man)._destroy()  # multiple destroy is fine
        finally:
            fc.cleanup()

    def test_memory_manager(self):
        """Test memory manager operations."""
        fc = FileCreator()
        try:
            # Create test file
            test_content = "x" * self.k_window_test_size
            test_path = fc.create_file("manager_test", test_content)

            slide_man = SlidingWindowMapManager()
            static_man = StaticWindowMapManager()

            for man in (static_man, slide_man):
                assert man.num_file_handles() == 0
                assert man.num_open_files() == 0

                # Test basic operations
                c = man.make_cursor(test_path)
                assert c.path_or_fd() == test_path
                assert c.use_region(10, 10).is_valid()
                assert c.ofs_begin() == 10
                assert c.size() == 10

                # Verify content
                with open(test_path, "rb") as fp:
                    assert c.buffer()[:] == fp.read(20)[10:]
        finally:
            fc.cleanup()

    def test_memman_operation(self):
        """Test memory manager advanced operations."""
        fc = FileCreator()
        try:
            # Create test file with larger content to force collection
            test_content = "x" * (self.k_window_test_size * 2)
            test_path = fc.create_file("manager_operation_test", test_content)

            # Use small limits to force collection
            max_num_handles = 2
            window_size = 100
            max_memory = 1000

            # Test both manager types
            for mtype in (StaticWindowMapManager, SlidingWindowMapManager):
                man = mtype(
                    window_size=window_size,
                    max_memory_size=max_memory,
                    max_open_handles=max_num_handles,
                )
                c = man.make_cursor(test_path)

                # Test basic state
                assert man.num_open_files() == 0
                assert man.mapped_memory_size() == 0

                # Map multiple regions to exceed limits
                for offset in range(0, len(test_content), window_size):
                    assert c.use_region(offset, window_size).is_valid()

                # Test cleanup - behavior differs between manager types
                handles_before = man.num_file_handles()
                assert handles_before > 0  # Verify we have handles to collect

                if isinstance(man, SlidingWindowMapManager):
                    # Force collection by mapping beyond limits
                    assert c.use_region(len(test_content) - window_size, window_size).is_valid()
                    assert man.num_file_handles() <= max_num_handles
                else:
                    # StaticWindowMapManager maintains its mapping
                    man.collect()
                    assert man.num_file_handles() == handles_before
        finally:
            fc.cleanup()
