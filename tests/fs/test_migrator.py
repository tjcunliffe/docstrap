"""Tests for directory migration functionality."""

import logging
from pathlib import Path
from unittest.mock import Mock, call, patch

import pytest

from docstrap.fs.handler import FileSystemError
from docstrap.fs.migrator import DirectoryMigrator


@pytest.fixture
def mock_file_handler():
    """Create a mock file handler."""
    handler = Mock()
    handler.remove_dir = Mock()
    return handler


@pytest.fixture
def migrator(mock_file_handler):
    """Create a migrator instance with mock handler."""
    return DirectoryMigrator(mock_file_handler)


@pytest.fixture
def setup_test_files(tmp_path):
    """Set up test files in a directory."""

    def _setup(dir_path: Path):
        dir_path.mkdir(parents=True, exist_ok=True)
        policies_dir = dir_path / "policies"
        policies_dir.mkdir(parents=True, exist_ok=True)
        (policies_dir / "policy1.md").write_text("Policy 1 content")
        (policies_dir / "policy2.md").write_text("Policy 2 content")

    return _setup


@pytest.fixture
def temp_project(tmp_path, setup_test_files):
    """Create a temporary project structure."""
    # Create a basic project structure
    docs_dir = tmp_path / "docs"
    setup_test_files(docs_dir)

    # Create some numbered directories
    numbered_dir = tmp_path / "numbered_docs"
    numbered_dir.mkdir(exist_ok=True)
    policies_numbered = numbered_dir / "010_policies"
    policies_numbered.mkdir(exist_ok=True)
    (policies_numbered / "010_policy1.md").write_text("Numbered Policy 1")

    return tmp_path


def test_find_isms_directories_basic(migrator, temp_project):
    """Test finding basic documentation directories."""
    new_dir = temp_project / "new_docs"

    dirs = migrator.find_isms_directories(temp_project, new_dir)

    assert len(dirs) == 2
    assert temp_project / "docs" in dirs
    assert temp_project / "numbered_docs" in dirs


def test_find_isms_directories_exclude_new(migrator, temp_project):
    """Test that new directory is excluded from search."""
    new_dir = temp_project / "docs" / "new"
    new_dir.mkdir(parents=True, exist_ok=True)
    (new_dir / "policies").mkdir(parents=True, exist_ok=True)
    (new_dir / "policies" / "test.md").write_text("test")

    dirs = migrator.find_isms_directories(temp_project, new_dir)

    assert new_dir not in dirs


def test_handle_directory_change_no_existing(migrator, temp_project):
    """Test handling directory change with no existing directories."""
    empty_dir = temp_project / "empty"
    empty_dir.mkdir(exist_ok=True)
    new_dir = temp_project / "new_docs"

    with patch("builtins.input", return_value="n"):
        migrator.handle_directory_change(empty_dir, new_dir)

    # Should do nothing
    assert not new_dir.exists()


def test_handle_directory_change_existing_content(migrator, temp_project):
    """Test handling directory change when destination has content."""
    new_dir = temp_project / "new_docs"
    new_dir.mkdir(exist_ok=True)
    (new_dir / "existing.md").write_text("existing content")

    with pytest.raises(FileSystemError) as exc_info:
        migrator.handle_directory_change(temp_project, new_dir)

    assert "already exists and contains files" in str(exc_info.value)


def test_handle_directory_change_single_source(
    migrator, temp_project, setup_test_files
):
    """Test migration from a single source directory."""
    source_dir = temp_project / "docs"
    new_dir = temp_project / "new_docs"
    setup_test_files(source_dir)

    # Mock all user interactions:
    # 1. Directory selection (when multiple found)
    # 2. Migration confirmation
    # 3. Source directory removal confirmation
    with (
        patch("builtins.input", return_value="y"),
        patch.object(migrator, "_confirm_migration", return_value=True),
        patch.object(migrator, "_confirm_removal", return_value=False),
    ):
        migrator.handle_directory_change(temp_project, new_dir)

    # Verify files were migrated
    assert migrator.file_handler.create.call_count > 0
    create_calls = [call[0] for call in migrator.file_handler.create.call_args_list]
    assert any(
        str(new_dir / "policies" / "policy1.md") in str(args[0])
        for args in create_calls
    )


def test_handle_directory_change_multiple_sources(
    migrator, temp_project, setup_test_files
):
    """Test migration with multiple source directories."""
    new_dir = temp_project / "new_docs"
    setup_test_files(temp_project / "docs")

    # Mock directory selection and confirmations
    with (
        patch("builtins.input", return_value="y"),
        patch.object(migrator, "_confirm_migration", return_value=True),
        patch.object(migrator, "_confirm_removal", return_value=False),
    ):
        migrator.handle_directory_change(temp_project, new_dir)

    # Verify files were migrated
    assert migrator.file_handler.create.call_count > 0
    create_calls = [call[0] for call in migrator.file_handler.create.call_args_list]
    assert any(
        str(new_dir / "policies" / "policy1.md") in str(args[0])
        for args in create_calls
    )


def test_handle_directory_change_skip_migration(migrator, temp_project):
    """Test skipping migration when user declines."""
    new_dir = temp_project / "new_docs"

    with patch("builtins.input", return_value="n"):
        migrator.handle_directory_change(temp_project, new_dir)

    # Should not create new directory
    assert not new_dir.exists()


def test_handle_directory_change_keyboard_interrupt(migrator, temp_project):
    """Test handling keyboard interrupt during migration."""
    new_dir = temp_project / "new_docs"

    with patch("builtins.input", side_effect=KeyboardInterrupt):
        migrator.handle_directory_change(temp_project, new_dir)

    # Should not create new directory
    assert not new_dir.exists()


def test_handle_directory_change_eof(migrator, temp_project):
    """Test handling EOF during migration."""
    new_dir = temp_project / "new_docs"

    with patch("builtins.input", side_effect=EOFError):
        migrator.handle_directory_change(temp_project, new_dir)

    # Should not create new directory
    assert not new_dir.exists()


def test_cleanup_empty_dirs(migrator, temp_project):
    """Test cleaning up empty directories."""
    test_dir = temp_project / "test_cleanup"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "empty1").mkdir(exist_ok=True)
    (test_dir / "empty1" / "empty2").mkdir(exist_ok=True)
    (test_dir / "nonempty").mkdir(exist_ok=True)
    (test_dir / "nonempty" / "file.txt").write_text("content")

    migrator._cleanup_empty_dirs(test_dir)

    # Empty directories should be removed
    assert not (test_dir / "empty1").exists()
    assert not (test_dir / "empty1" / "empty2").exists()
    # Non-empty directory should remain
    assert (test_dir / "nonempty").exists()


def test_migrate_directory_with_removal(migrator, temp_project, setup_test_files):
    """Test migration with source directory removal."""
    source_dir = temp_project / "docs"
    dest_dir = temp_project / "new_docs"
    setup_test_files(source_dir)

    # Mock user confirming removal
    with patch("builtins.input", return_value="y"):
        migrator._migrate_directory(source_dir, dest_dir)

    # Verify files were migrated
    assert migrator.file_handler.create.call_count > 0
    create_calls = [call[0] for call in migrator.file_handler.create.call_args_list]
    assert any(
        str(dest_dir / "policies" / "policy1.md") in str(args[0])
        for args in create_calls
    )
    # Verify source was removed
    migrator.file_handler.remove_dir.assert_called_once_with(source_dir)


def test_migrate_directory_keep_source(migrator, temp_project, setup_test_files):
    """Test migration while keeping source directory."""
    source_dir = temp_project / "docs"
    dest_dir = temp_project / "new_docs"
    setup_test_files(source_dir)

    # Mock user declining removal
    with patch("builtins.input", return_value="n"):
        migrator._migrate_directory(source_dir, dest_dir)

    # Verify files were migrated
    assert migrator.file_handler.create.call_count > 0
    create_calls = [call[0] for call in migrator.file_handler.create.call_args_list]
    assert any(
        str(dest_dir / "policies" / "policy1.md") in str(args[0])
        for args in create_calls
    )
    # Verify source was not removed
    migrator.file_handler.remove_dir.assert_not_called()


def test_migrate_directory_error(migrator, temp_project):
    """Test error handling during migration."""
    source_dir = temp_project / "docs"
    dest_dir = temp_project / "new_docs"

    # Simulate permission error
    with (
        patch("pathlib.Path.read_text", side_effect=PermissionError),
        pytest.raises(FileSystemError) as exc_info,
    ):
        migrator._migrate_directory(source_dir, dest_dir)

    assert "Error during migration" in str(exc_info.value)


def test_confirm_migration_yes(migrator):
    """Test migration confirmation when user accepts."""
    with patch("builtins.input", return_value="y"):
        assert migrator._confirm_migration(Path("old"), Path("new")) is True


def test_confirm_migration_no(migrator):
    """Test migration confirmation when user declines."""
    with patch("builtins.input", return_value="n"):
        assert migrator._confirm_migration(Path("old"), Path("new")) is False


def test_confirm_removal_yes(migrator):
    """Test removal confirmation when user accepts."""
    with patch("builtins.input", return_value="y"):
        assert migrator._confirm_removal(Path("test")) is True


def test_confirm_removal_no(migrator):
    """Test removal confirmation when user declines."""
    with patch("builtins.input", return_value="n"):
        assert migrator._confirm_removal(Path("test")) is False
