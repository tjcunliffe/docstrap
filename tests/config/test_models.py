"""Tests for the configuration models."""

import pytest

from docstrap.config.models import DocumentationError, StructureConfig


def test_valid_config_creation():
    """Test creating a valid configuration object."""
    config_dict = {
        "docs_dir": "docs",
        "use_numbered_prefix": True,
        "use_markdown_headings": True,
        "initial_prefix": 10,
        "dir_start_prefix": 20,
        "prefix_step": 10,
        "padding_width": 3,
        "directories": {
            "guides": ["getting-started.md"],
            "reference": ["api-reference.md"],
        },
        "top_level_files": ["index.md"],
    }

    config = StructureConfig.from_dict(config_dict)
    assert config.docs_dir == "docs"
    assert config.numbering.enabled is True
    assert isinstance(config.structure.directories, dict)
    assert len(config.structure.directories) == 2
    assert isinstance(config.structure.top_level_files, list)


def test_backward_compatibility():
    """Test that old base_dir config still works."""
    config_dict = {
        "base_dir": "docs",  # Old config name
        "use_numbered_prefix": True,
        "use_markdown_headings": True,
        "initial_prefix": 10,
        "dir_start_prefix": 20,
        "prefix_step": 10,
        "padding_width": 3,
        "directories": {"guides": ["getting-started.md"]},
        "top_level_files": ["index.md"],
    }

    config = StructureConfig.from_dict(config_dict)
    assert config.docs_dir == "docs"


def test_dot_docs_dir():
    """Test that '.' is a valid docs_dir value."""
    config_dict = {
        "docs_dir": ".",
        "use_numbered_prefix": True,
        "use_markdown_headings": True,
        "initial_prefix": 10,
        "dir_start_prefix": 20,
        "prefix_step": 10,
        "padding_width": 3,
        "directories": {"guides": []},
        "top_level_files": [],
    }

    config = StructureConfig.from_dict(config_dict)
    assert config.docs_dir == "."
    config.validate()  # Should not raise any exceptions


def test_invalid_prefix_step():
    """Test configuration with invalid prefix step."""
    config_dict = {
        "docs_dir": "docs",
        "use_numbered_prefix": True,
        "use_markdown_headings": True,
        "initial_prefix": 10,
        "dir_start_prefix": 20,
        "prefix_step": 0,  # Invalid: should be positive
        "padding_width": 3,
        "directories": {"guides": []},
        "top_level_files": [],
    }

    with pytest.raises(DocumentationError) as exc_info:
        StructureConfig.from_dict(config_dict).validate()
    assert "prefix_step must be positive" in str(exc_info.value)


def test_invalid_padding_width():
    """Test configuration with invalid padding width."""
    config_dict = {
        "docs_dir": "docs",
        "use_numbered_prefix": True,
        "use_markdown_headings": True,
        "initial_prefix": 10,
        "dir_start_prefix": 20,
        "prefix_step": 10,
        "padding_width": 0,  # Invalid: should be positive
        "directories": {"guides": []},
        "top_level_files": [],
    }

    with pytest.raises(DocumentationError) as exc_info:
        StructureConfig.from_dict(config_dict).validate()
    assert "padding_width must be positive" in str(exc_info.value)


def test_invalid_directory_structure():
    """Test configuration with invalid directory structure."""
    config_dict = {
        "docs_dir": "docs",
        "use_numbered_prefix": True,
        "use_markdown_headings": True,
        "initial_prefix": 10,
        "dir_start_prefix": 20,
        "prefix_step": 10,
        "padding_width": 3,
        "directories": {"guides": 123},  # Invalid: should be a list
        "top_level_files": [],
    }

    with pytest.raises(DocumentationError) as exc_info:
        StructureConfig.from_dict(config_dict)
    assert "Directory contents must be a list" in str(exc_info.value)


def test_invalid_file_names():
    """Test configuration with invalid file names."""
    config_dict = {
        "docs_dir": "docs",
        "use_numbered_prefix": True,
        "use_markdown_headings": True,
        "initial_prefix": 10,
        "dir_start_prefix": 20,
        "prefix_step": 10,
        "padding_width": 3,
        "directories": {
            "guides": ["invalid/file/path.md"]  # Invalid: contains path separators
        },
        "top_level_files": [],
    }

    with pytest.raises(DocumentationError) as exc_info:
        StructureConfig.from_dict(config_dict).validate()
    assert "File names cannot contain path separators" in str(exc_info.value)


def test_empty_config():
    """Test configuration with minimal valid settings."""
    config_dict = {
        "docs_dir": "docs",
        "use_numbered_prefix": False,
        "use_markdown_headings": False,
        "initial_prefix": 10,
        "dir_start_prefix": 20,
        "prefix_step": 10,
        "padding_width": 3,
        "directories": {"guides": []},  # At least one directory required
        "top_level_files": [],
    }

    config = StructureConfig.from_dict(config_dict)
    config.validate()  # Should not raise any exceptions


def test_directory_name_validation():
    """Test validation of directory names."""
    config_dict = {
        "docs_dir": "docs",
        "use_numbered_prefix": True,
        "use_markdown_headings": True,
        "initial_prefix": 10,
        "dir_start_prefix": 20,
        "prefix_step": 10,
        "padding_width": 3,
        "directories": {"invalid/dir/name": []},  # Invalid: contains path separators
        "top_level_files": [],
    }

    with pytest.raises(DocumentationError) as exc_info:
        StructureConfig.from_dict(config_dict).validate()
    assert "Directory names cannot contain path separators" in str(exc_info.value)


def test_missing_docs_dir():
    """Test that missing docs_dir raises appropriate error."""
    config_dict = {
        "use_numbered_prefix": True,
        "use_markdown_headings": True,
        "initial_prefix": 10,
        "dir_start_prefix": 20,
        "prefix_step": 10,
        "padding_width": 3,
        "directories": {"guides": []},
        "top_level_files": [],
    }

    with pytest.raises(DocumentationError) as exc_info:
        StructureConfig.from_dict(config_dict)
    assert "Missing required configuration: docs_dir" in str(exc_info.value)
