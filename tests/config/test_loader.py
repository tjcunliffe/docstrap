"""Tests for the configuration loader module."""

from pathlib import Path

import pytest
import yaml

from docstrap.config.loader import load_config
from docstrap.config.models import DocumentationError, StructureConfig


@pytest.fixture
def valid_config_file(tmp_path):
    """Create a temporary valid configuration file."""
    config_data = {
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

    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    return config_file


@pytest.fixture
def invalid_yaml_file(tmp_path):
    """Create a temporary file with invalid YAML."""
    config_file = tmp_path / "invalid.yaml"
    with open(config_file, "w") as f:
        f.write("invalid: yaml: content:")
    return config_file


def test_load_valid_config(valid_config_file):
    """Test loading a valid configuration file."""
    config = load_config(valid_config_file)
    assert isinstance(config, StructureConfig)
    assert config.docs_dir == "docs"
    assert config.numbering.enabled is True
    assert config.use_markdown_headings is True
    assert config.numbering.initial_prefix == 10
    assert config.numbering.dir_start_prefix == 20
    assert config.numbering.prefix_step == 10
    assert config.numbering.padding_width == 3
    assert "guides" in config.structure.directories
    assert "reference" in config.structure.directories
    assert "index.md" in config.structure.top_level_files


def test_load_nonexistent_config():
    """Test loading a configuration file that doesn't exist."""
    with pytest.raises(DocumentationError) as exc_info:
        load_config("nonexistent.yaml")
    assert "Configuration file not found" in str(exc_info.value)


def test_load_invalid_yaml(invalid_yaml_file):
    """Test loading an invalid YAML file."""
    with pytest.raises(DocumentationError) as exc_info:
        load_config(invalid_yaml_file)
    assert "Error parsing YAML file" in str(exc_info.value)


def test_load_non_dict_config(tmp_path):
    """Test loading a YAML file that doesn't contain a dictionary."""
    config_file = tmp_path / "non_dict.yaml"
    with open(config_file, "w") as f:
        yaml.dump(["list", "instead", "of", "dict"], f)

    with pytest.raises(DocumentationError) as exc_info:
        load_config(config_file)
    assert "Configuration must be a YAML dictionary" in str(exc_info.value)


def test_missing_required_fields(tmp_path):
    """Test configuration with missing required fields."""
    config_file = tmp_path / "missing_fields.yaml"
    with open(config_file, "w") as f:
        yaml.dump({"docs_dir": "docs"}, f)  # Missing most required fields

    with pytest.raises(DocumentationError) as exc_info:
        load_config(config_file)
    assert "Missing required numbering configuration" in str(exc_info.value)


def test_relative_path_handling(tmp_path, monkeypatch):
    """Test handling of relative paths."""
    # Create config file in a known location
    config_data = {
        "docs_dir": "docs",
        "use_numbered_prefix": True,
        "use_markdown_headings": True,
        "initial_prefix": 10,
        "dir_start_prefix": 20,
        "prefix_step": 10,
        "padding_width": 3,
        "directories": {"guides": []},
        "top_level_files": [],
    }

    # Create the config file in the temporary directory
    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_data, f)

    # Temporarily change the current working directory
    monkeypatch.chdir(tmp_path)

    # Test with relative path
    config = load_config("test_config.yaml")
    assert isinstance(config, StructureConfig)
    assert config.docs_dir == "docs"
