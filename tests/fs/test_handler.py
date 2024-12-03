"""Tests for file system handlers."""

import logging
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from docstrap.fs.handler import (
    DryRunFileHandler,
    FileHandler,
    FileSystemError,
    InteractiveFileHandler,
    SilentFileHandler,
)


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for file operations."""
    return tmp_path


@pytest.fixture
def test_file(temp_dir):
    """Create a test file path."""
    return temp_dir / "test.txt"


@pytest.fixture
def test_dir(temp_dir):
    """Create a test directory path."""
    return temp_dir / "test_dir"


@pytest.fixture
def existing_file(test_file):
    """Create an existing test file."""
    test_file.write_text("test content")
    return test_file


@pytest.fixture
def existing_dir(test_dir):
    """Create an existing test directory with some files."""
    test_dir.mkdir()
    (test_dir / "file1.txt").write_text("content 1")
    (test_dir / "file2.txt").write_text("content 2")
    return test_dir


class TestInteractiveFileHandler:
    """Tests for InteractiveFileHandler."""

    def test_create_file(self, test_file):
        """Test creating a new file."""
        handler = InteractiveFileHandler()
        content = "test content"

        handler.create(test_file, content)

        assert test_file.exists()
        assert test_file.read_text() == content

    def test_create_file_with_dirs(self, temp_dir):
        """Test creating a file in nested directories."""
        handler = InteractiveFileHandler()
        path = temp_dir / "nested" / "dirs" / "test.txt"
        content = "test content"

        handler.create(path, content)

        assert path.exists()
        assert path.read_text() == content

    def test_create_file_error(self, temp_dir):
        """Test error handling when creating a file."""
        handler = InteractiveFileHandler()
        path = temp_dir / "test.txt"

        with (
            patch("pathlib.Path.write_text", side_effect=PermissionError),
            pytest.raises(FileSystemError) as exc_info,
        ):
            handler.create(path, "content")

        assert "Error creating file" in str(exc_info.value)

    def test_remove_file_confirmed(self, existing_file):
        """Test removing a file with user confirmation."""
        handler = InteractiveFileHandler()

        with patch("builtins.input", return_value="y"):
            handler.remove(existing_file)

        assert not existing_file.exists()

    def test_remove_file_cancelled(self, existing_file):
        """Test cancelling file removal."""
        handler = InteractiveFileHandler()

        with patch("builtins.input", return_value="n"):
            handler.remove(existing_file)

        assert existing_file.exists()

    def test_remove_file_keyboard_interrupt(self, existing_file):
        """Test handling keyboard interrupt during file removal."""
        handler = InteractiveFileHandler()

        with patch("builtins.input", side_effect=KeyboardInterrupt):
            handler.remove(existing_file)

        assert existing_file.exists()

    def test_remove_file_eof(self, existing_file):
        """Test EOF handling when removing a file."""
        handler = InteractiveFileHandler()

        with patch("builtins.input", side_effect=EOFError):
            handler.remove(existing_file)

        assert existing_file.exists()

    def test_remove_file_error(self, existing_file):
        """Test error handling when removing a file."""
        handler = InteractiveFileHandler()

        with (
            patch("builtins.input", return_value="y"),
            patch("pathlib.Path.unlink", side_effect=PermissionError),
            pytest.raises(FileSystemError) as exc_info,
        ):
            handler.remove(existing_file)

        assert "Error removing file" in str(exc_info.value)
        assert existing_file.exists()

    def test_remove_dir_confirmed(self, existing_dir):
        """Test removing a directory with user confirmation."""
        handler = InteractiveFileHandler()

        with patch("builtins.input", return_value="y"):
            handler.remove_dir(existing_dir)

        assert not existing_dir.exists()

    def test_remove_dir_cancelled(self, existing_dir):
        """Test cancelling directory removal."""
        handler = InteractiveFileHandler()

        with patch("builtins.input", return_value="n"):
            handler.remove_dir(existing_dir)

        assert existing_dir.exists()

    def test_remove_dir_error(self, existing_dir):
        """Test error handling when removing a directory."""
        handler = InteractiveFileHandler()

        with (
            patch("builtins.input", return_value="y"),
            patch("shutil.rmtree", side_effect=PermissionError),
            pytest.raises(FileSystemError) as exc_info,
        ):
            handler.remove_dir(existing_dir)

        assert "Error removing directory" in str(exc_info.value)
        assert existing_dir.exists()

    def test_remove_dir_eof(self, existing_dir):
        """Test EOF handling when removing a directory."""
        handler = InteractiveFileHandler()

        with patch("builtins.input", side_effect=EOFError):
            handler.remove_dir(existing_dir)

        assert existing_dir.exists()

    def test_remove_nonexistent(self, temp_dir):
        """Test removing a nonexistent file/directory."""
        handler = InteractiveFileHandler()
        path = temp_dir / "nonexistent"

        # Should not raise any errors
        handler.remove(path)
        handler.remove_dir(path)


class TestSilentFileHandler:
    """Tests for SilentFileHandler."""

    def test_create_file(self, test_file):
        """Test creating a new file."""
        handler = SilentFileHandler()
        content = "test content"

        handler.create(test_file, content)

        assert test_file.exists()
        assert test_file.read_text() == content

    def test_remove_file(self, existing_file):
        """Test removing a file."""
        handler = SilentFileHandler()

        handler.remove(existing_file)

        assert not existing_file.exists()

    def test_remove_file_error_silent(self, existing_file):
        """Test error handling when removing a file in silent mode."""
        handler = SilentFileHandler()

        with (
            patch("pathlib.Path.unlink", side_effect=PermissionError),
            pytest.raises(FileSystemError) as exc_info,
        ):
            handler.remove(existing_file)

        assert "Error removing file" in str(exc_info.value)
        assert existing_file.exists()

    def test_remove_dir(self, existing_dir):
        """Test removing a directory."""
        handler = SilentFileHandler()

        handler.remove_dir(existing_dir)

        assert not existing_dir.exists()

    def test_remove_dir_error_silent(self, existing_dir):
        """Test error handling when removing a directory in silent mode."""
        handler = SilentFileHandler()

        with (
            patch("shutil.rmtree", side_effect=PermissionError),
            pytest.raises(FileSystemError) as exc_info,
        ):
            handler.remove_dir(existing_dir)

        assert "Error removing directory" in str(exc_info.value)
        assert existing_dir.exists()

    def test_error_handling(self, temp_dir):
        """Test error handling in silent mode."""
        handler = SilentFileHandler()
        path = temp_dir / "test.txt"

        with (
            patch("pathlib.Path.write_text", side_effect=PermissionError),
            pytest.raises(FileSystemError) as exc_info,
        ):
            handler.create(path, "content")

        assert "Error creating file" in str(exc_info.value)


class TestDryRunFileHandler:
    """Tests for DryRunFileHandler."""

    def test_create_file(self, test_file, caplog):
        """Test simulated file creation."""
        handler = DryRunFileHandler()
        content = "test content"

        with caplog.at_level(logging.INFO):
            handler.create(test_file, content)

        assert f"Would create file: {test_file}" in caplog.text
        assert not test_file.exists()

    def test_create_file_with_content_logging(self, test_file, caplog):
        """Test content logging in dry run mode."""
        handler = DryRunFileHandler()
        content = "test content"

        with caplog.at_level(logging.DEBUG):
            handler.create(test_file, content)

        assert "With content:" in caplog.text
        assert content in caplog.text

    def test_remove_file(self, existing_file, caplog):
        """Test simulated file removal."""
        handler = DryRunFileHandler()

        with caplog.at_level(logging.INFO):
            handler.remove(existing_file)

        assert f"Would remove file: {existing_file}" in caplog.text
        assert existing_file.exists()

    def test_remove_dir(self, existing_dir, caplog):
        """Test simulated directory removal."""
        handler = DryRunFileHandler()

        with caplog.at_level(logging.INFO):
            handler.remove_dir(existing_dir)

        assert f"Would remove directory: {existing_dir}" in caplog.text
        assert existing_dir.exists()

    def test_remove_dir_content_logging(self, existing_dir, caplog):
        """Test logging of directory contents in dry run mode."""
        handler = DryRunFileHandler()

        with caplog.at_level(logging.DEBUG):
            handler.remove_dir(existing_dir)

        # Should log about removing each file
        for item in existing_dir.rglob("*"):
            assert f"Would remove: {item}" in caplog.text

    def test_nonexistent_paths(self, temp_dir, caplog):
        """Test handling of nonexistent paths in dry run mode."""
        handler = DryRunFileHandler()
        path = temp_dir / "nonexistent"

        with caplog.at_level(logging.INFO):
            handler.remove(path)
            handler.remove_dir(path)

        # Should not log anything for nonexistent paths
        assert "Would remove" not in caplog.text
