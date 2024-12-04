"""Tests for documentation structure management."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from docstrap.config.models import DocumentationError
from docstrap.core.manager import DocumentationManager


class TestStructureCreation:
    """Test cases for structure creation."""

    def test_create_basic_structure(self, mock_file_handler, basic_config):
        """Test creating a basic structure without numbering."""
        manager = DocumentationManager(basic_config, mock_file_handler)
        project_root = Path("/test")

        with patch("pathlib.Path.mkdir"):
            manager.create_structure(project_root)

        # Check docs directory creation
        docs_dir = project_root / "docs"

        # Verify index.md creation
        mock_file_handler.create.assert_any_call(docs_dir / "index.md", "# Index\n")

        # Verify guides directory files
        mock_file_handler.create.assert_any_call(
            docs_dir / "guides/getting-started.md", "# Getting Started\n"
        )

        # Verify reference directory files
        mock_file_handler.create.assert_any_call(
            docs_dir / "reference/api.md", "# Api\n"
        )

    def test_create_numbered_structure(self, mock_file_handler, numbered_config):
        """Test creating a structure with numbering enabled."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        project_root = Path("/test")

        with patch("pathlib.Path.mkdir"):
            manager.create_structure(project_root)

        docs_dir = project_root / "docs"

        # Verify numbered files are created
        mock_file_handler.create.assert_any_call(docs_dir / "010_index.md", "# Index\n")
        mock_file_handler.create.assert_any_call(
            docs_dir / "020_guides/010_getting-started.md", "# Getting Started\n"
        )
        mock_file_handler.create.assert_any_call(
            docs_dir / "040_reference/010_api.md", "# Api\n"
        )

    def test_create_structure_in_root(self, mock_file_handler, dot_config):
        """Test creating structure in project root using '.' as docs_dir."""
        manager = DocumentationManager(dot_config, mock_file_handler)
        project_root = Path("/test")

        with patch("pathlib.Path.mkdir"):
            manager.create_structure(project_root)

        # Files should be created directly in project root
        mock_file_handler.create.assert_any_call(project_root / "index.md", "# Index\n")
        mock_file_handler.create.assert_any_call(
            project_root / "guides/getting-started.md", "# Getting Started\n"
        )
        mock_file_handler.create.assert_any_call(
            project_root / "reference/api.md", "# Api\n"
        )

    def test_create_structure_without_markdown_headings(
        self, mock_file_handler, basic_config
    ):
        """Test creating structure without markdown headings."""
        basic_config.use_markdown_headings = False
        manager = DocumentationManager(basic_config, mock_file_handler)
        project_root = Path("/test")

        with patch("pathlib.Path.mkdir"):
            manager.create_structure(project_root)

        docs_dir = project_root / "docs"

        # Verify files are created without headings
        mock_file_handler.create.assert_any_call(docs_dir / "index.md", "")
        mock_file_handler.create.assert_any_call(
            docs_dir / "guides/getting-started.md", ""
        )
        mock_file_handler.create.assert_any_call(docs_dir / "reference/api.md", "")


class TestContentCleanup:
    """Test cases for content cleanup."""

    def test_cleanup_mismatched_content_single_dir(
        self, mock_file_handler, numbered_config
    ):
        """Test cleanup of mismatched content in a single directory."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        docs_dir = Path("/test/docs")

        with patch("pathlib.Path.exists", return_value=True):
            manager._cleanup_mismatched_content(docs_dir)

        mock_file_handler.remove_dir.assert_not_called()

    def test_cleanup_mismatched_content_multiple_dirs(
        self, mock_file_handler, numbered_config
    ):
        """Test cleanup with multiple versions of directories."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        docs_dir = Path("/test/docs")

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.input", return_value="1"),
        ):
            manager._cleanup_mismatched_content(docs_dir)

        mock_file_handler.remove_dir.assert_not_called()

    def test_cleanup_mismatched_content_skip(self, mock_file_handler, numbered_config):
        """Test skipping cleanup of mismatched content."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        docs_dir = Path("/test/docs")

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.input", return_value="n"),
        ):
            manager._cleanup_mismatched_content(docs_dir)

        mock_file_handler.remove_dir.assert_not_called()


class TestErrorHandling:
    """Test cases for error handling."""

    def test_create_structure_with_error(self, mock_file_handler, basic_config):
        """Test error handling during structure creation."""
        manager = DocumentationManager(basic_config, mock_file_handler)
        mock_file_handler.create.side_effect = OSError("Test error")

        with (
            patch("pathlib.Path.mkdir"),
            pytest.raises(
                DocumentationError, match="Error creating directory structure"
            ),
        ):
            manager.create_structure(Path("/test"))

    def test_create_structure_default_root(self, mock_file_handler, basic_config):
        """Test structure creation with default project root."""
        manager = DocumentationManager(basic_config, mock_file_handler)

        with (
            patch("pathlib.Path.cwd", return_value=Path("/default")),
            patch("pathlib.Path.mkdir"),
        ):
            manager.create_structure()

            # Verify files are created in the current working directory
            mock_file_handler.create.assert_any_call(
                Path("/default/docs/index.md"), "# Index\n"
            )
            mock_file_handler.create.assert_any_call(
                Path("/default/docs/guides/getting-started.md"), "# Getting Started\n"
            )
            mock_file_handler.create.assert_any_call(
                Path("/default/docs/reference/api.md"), "# Api\n"
            )


class TestPathGeneration:
    """Test cases for path generation."""

    def test_get_numbered_name(self, mock_file_handler, numbered_config):
        """Test generation of numbered filenames."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        result = manager._get_numbered_name("test.md", 1)
        assert result == "010_test.md"

    def test_get_directory_path(self, mock_file_handler, numbered_config):
        """Test generation of directory paths."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        docs_dir = Path("/test/docs")
        result = manager._get_directory_path(docs_dir, "guides", 1)
        assert result == docs_dir / "020_guides"
