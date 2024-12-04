"""Shared test fixtures and utilities."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from docstrap.config.models import DocumentStructure, NumberingConfig, StructureConfig
from docstrap.fs.handler import FileHandler


@pytest.fixture
def mock_file_handler():
    """Create a mock file handler."""
    handler = Mock(spec=FileHandler)
    handler.create = Mock()
    handler.remove = Mock()
    handler.remove_dir = Mock()
    return handler


@pytest.fixture
def temp_docs(tmp_path):
    """Create a temporary documentation structure."""
    # Create a basic project structure
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()

    # Create some documentation files
    policies_dir = docs_dir / "policies"
    policies_dir.mkdir()
    (policies_dir / "policy1.md").write_text("Policy 1 content")
    (policies_dir / "policy2.md").write_text("Policy 2 content")

    # Create some numbered directories
    numbered_dir = tmp_path / "numbered_docs"
    numbered_dir.mkdir()
    policies_numbered = numbered_dir / "010_policies"
    policies_numbered.mkdir()
    (policies_numbered / "010_policy1.md").write_text("Numbered Policy 1")

    return tmp_path


@pytest.fixture
def basic_config():
    """Create a basic configuration without numbering."""
    return StructureConfig(
        docs_dir="docs",
        numbering=NumberingConfig(
            enabled=False,
            initial_prefix=10,
            dir_start_prefix=20,
            prefix_step=10,
            padding_width=3,
        ),
        structure=DocumentStructure(
            directories={"guides": ["getting-started.md"], "reference": ["api.md"]},
            top_level_files=["index.md"],
        ),
        use_markdown_headings=True,
        generate_mkdocs=False,
        mkdocs=None,
    )


@pytest.fixture
def numbered_config():
    """Create a configuration with numbering enabled."""
    return StructureConfig(
        docs_dir="docs",
        numbering=NumberingConfig(
            enabled=True,
            initial_prefix=10,
            dir_start_prefix=20,
            prefix_step=10,
            padding_width=3,
        ),
        structure=DocumentStructure(
            directories={"guides": ["getting-started.md"], "reference": ["api.md"]},
            top_level_files=["index.md"],
        ),
        use_markdown_headings=True,
        generate_mkdocs=False,
        mkdocs=None,
    )


@pytest.fixture
def dot_config():
    """Create a configuration that uses '.' as docs_dir."""
    return StructureConfig(
        docs_dir=".",
        numbering=NumberingConfig(
            enabled=False,
            initial_prefix=10,
            dir_start_prefix=20,
            prefix_step=10,
            padding_width=3,
        ),
        structure=DocumentStructure(
            directories={"guides": ["getting-started.md"], "reference": ["api.md"]},
            top_level_files=["index.md"],
        ),
        use_markdown_headings=True,
        generate_mkdocs=False,
        mkdocs=None,
    )


@pytest.fixture
def test_project(tmp_path):
    """Create a test project with documentation directories."""
    # Create docs directory with files
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    policies_dir = docs_dir / "policies"
    policies_dir.mkdir()
    (policies_dir / "policy1.md").write_text("Policy 1 content")
    (policies_dir / "policy2.md").write_text("Policy 2 content")

    # Create numbered_docs directory with files
    numbered_dir = tmp_path / "numbered_docs"
    numbered_dir.mkdir()
    policies_numbered = numbered_dir / "010_policies"
    policies_numbered.mkdir()
    (policies_numbered / "010_policy1.md").write_text("Numbered Policy 1")

    return tmp_path


def assert_file_content(path: Path, expected_content: str):
    """Assert that a file exists and has the expected content."""
    assert path.exists(), f"File {path} does not exist"
    assert path.read_text() == expected_content, f"File {path} has unexpected content"


def assert_directory_structure(base_dir: Path, expected_structure: dict):
    """Assert that a directory has the expected structure.

    Args:
        base_dir: Base directory to check
        expected_structure: Dictionary mapping paths to content or None (for directories)

    Example:
        assert_directory_structure(docs_dir, {
            "policies/policy1.md": "Policy 1 content",
            "policies/policy2.md": "Policy 2 content",
            "empty_dir": None
        })
    """
    for path, content in expected_structure.items():
        full_path = base_dir / path
        if content is None:
            assert full_path.is_dir(), f"Expected directory at {path}"
        else:
            assert_file_content(full_path, content)
