"""Tests for documentation structure management."""

import pytest
from pathlib import Path
from unittest.mock import patch

from docstrap.core.manager import DocumentationManager
from docstrap.config.models import DocumentationError
from tests.utils import MockPath

class TestStructureCreation:
    """Tests for basic structure creation functionality."""
    
    def test_create_basic_structure(self, mock_file_handler, basic_config):
        """Test creating a basic structure without numbering."""
        manager = DocumentationManager(basic_config, mock_file_handler)
        project_root = Path("/test")
        
        with patch('pathlib.Path.mkdir'):
            manager.create_structure(project_root)
        
        # Check docs directory creation
        docs_dir = project_root / "docs"
        
        # Verify README.md creation
        mock_file_handler.create.assert_any_call(
            docs_dir / "README.md"
        )
        
        # Verify top-level files
        mock_file_handler.create.assert_any_call(
            docs_dir / "index.md",
            "# Index\n"
        )
        
        # Verify directory structure
        mock_file_handler.create.assert_any_call(
            docs_dir / "guides" / "getting-started.md",
            "# Getting Started\n"
        )
        mock_file_handler.create.assert_any_call(
            docs_dir / "reference" / "api.md",
            "# Api\n"
        )

    def test_create_numbered_structure(self, mock_file_handler, numbered_config):
        """Test creating a structure with numbering enabled."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        project_root = Path("/test")
        
        with patch('pathlib.Path.mkdir'):
            manager.create_structure(project_root)
        
        docs_dir = project_root / "docs"
        
        # Verify README.md (should not be numbered)
        mock_file_handler.create.assert_any_call(
            docs_dir / "README.md"
        )
        
        # Verify numbered top-level files
        mock_file_handler.create.assert_any_call(
            docs_dir / "010_index.md",
            "# Index\n"
        )
        
        # Verify numbered directories and files
        mock_file_handler.create.assert_any_call(
            docs_dir / "020_guides" / "010_getting-started.md",
            "# Getting Started\n"
        )
        mock_file_handler.create.assert_any_call(
            docs_dir / "040_reference" / "010_api.md",
            "# Api\n"
        )

    def test_create_structure_in_root(self, mock_file_handler, dot_config):
        """Test creating structure in project root using '.' as docs_dir."""
        manager = DocumentationManager(dot_config, mock_file_handler)
        project_root = Path("/test")
        
        with patch('pathlib.Path.mkdir'):
            manager.create_structure(project_root)
        
        # Files should be created directly in project root
        mock_file_handler.create.assert_any_call(
            project_root / "README.md"
        )
        
        mock_file_handler.create.assert_any_call(
            project_root / "index.md",
            "# Index\n"
        )
        
        mock_file_handler.create.assert_any_call(
            project_root / "guides" / "getting-started.md",
            "# Getting Started\n"
        )
        
        mock_file_handler.create.assert_any_call(
            project_root / "reference" / "api.md",
            "# Api\n"
        )

    def test_create_structure_without_markdown_headings(self, mock_file_handler, basic_config):
        """Test creating files without markdown headings."""
        basic_config.use_markdown_headings = False
        manager = DocumentationManager(basic_config, mock_file_handler)
        project_root = Path("/test")
        
        with patch('pathlib.Path.mkdir'):
            manager.create_structure(project_root)
        
        docs_dir = project_root / "docs"
        
        # Verify files are created without headings
        mock_file_handler.create.assert_any_call(
            docs_dir / "guides" / "getting-started.md",
            ""
        )

class TestContentCleanup:
    """Tests for content cleanup functionality."""
    
    def test_cleanup_mismatched_content_single_dir(self, mock_file_handler, numbered_config):
        """Test cleanup of single mismatched directory."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        docs_dir = Path("/test/docs")
        guide_dir = MockPath("/test/docs/guides")
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.glob', side_effect=[[guide_dir], []]):
            
            manager._cleanup_mismatched_content(docs_dir)
            
            # Should remove unnumbered directory when numbering is enabled
            mock_file_handler.remove_dir.assert_called_once_with(guide_dir)

    def test_cleanup_mismatched_content_multiple_dirs(self, mock_file_handler, numbered_config):
        """Test cleanup with multiple versions of the same directory."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        docs_dir = Path("/test/docs")
        
        # Create both versions of the directory
        unnumbered = MockPath("/test/docs/guides")
        numbered = MockPath("/test/docs/010_guides")
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.glob', side_effect=[[numbered], [unnumbered]]), \
             patch('builtins.input', return_value="1"):  # Keep the first directory (numbered)
            
            manager._cleanup_mismatched_content(docs_dir)
            
            # Should remove the unnumbered version when numbered is chosen
            mock_file_handler.remove_dir.assert_called_once_with(unnumbered)

    def test_cleanup_mismatched_content_skip(self, mock_file_handler, numbered_config):
        """Test skipping cleanup when user chooses to."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        docs_dir = Path("/test/docs")
        
        unnumbered = MockPath("/test/docs/guides")
        numbered = MockPath("/test/docs/010_guides")
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.glob', side_effect=[[unnumbered], [numbered]]), \
             patch('builtins.input', return_value="n"):
            
            manager._cleanup_mismatched_content(docs_dir)
            
            # Should not remove any directories
            mock_file_handler.remove_dir.assert_not_called()

class TestErrorHandling:
    """Tests for error handling."""
    
    def test_create_structure_with_error(self, mock_file_handler, basic_config):
        """Test error handling during structure creation."""
        manager = DocumentationManager(basic_config, mock_file_handler)
        mock_file_handler.create.side_effect = Exception("Test error")
        
        with pytest.raises(DocumentationError) as exc_info:
            manager.create_structure(Path("/test"))
        
        assert "Error creating directory structure" in str(exc_info.value)

    def test_create_structure_default_root(self, mock_file_handler, basic_config):
        """Test structure creation with default project root."""
        manager = DocumentationManager(basic_config, mock_file_handler)
        
        with patch('pathlib.Path.cwd', return_value=Path("/default")), \
             patch('pathlib.Path.mkdir'):
            manager.create_structure()
            
            # Verify files are created in the current working directory
            mock_file_handler.create.assert_any_call(
                Path("/default/docs/README.md")
            )

class TestPathGeneration:
    """Tests for path generation utilities."""
    
    def test_get_numbered_name(self, mock_file_handler, numbered_config):
        """Test generation of numbered filenames."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        
        result = manager._get_numbered_name("test.md", 2)
        assert result == "020_test.md"

    def test_get_directory_path(self, mock_file_handler, numbered_config):
        """Test generation of directory paths."""
        manager = DocumentationManager(numbered_config, mock_file_handler)
        docs_dir = Path("/test/docs")
        
        # Test with numbering enabled
        result = manager._get_directory_path(docs_dir, "guides", 1)
        assert result == docs_dir / "020_guides"
        
        # Test with numbering disabled
        numbered_config.numbering.enabled = False
        result = manager._get_directory_path(docs_dir, "guides", 1)
        assert result == docs_dir / "guides"
