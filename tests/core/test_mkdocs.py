"""Tests for MkDocs configuration generation."""

from pathlib import Path

import pytest

from docstrap.config.models import (
    DocumentStructure,
    MkDocsConfig,
    NumberingConfig,
    StructureConfig,
)
from docstrap.core.mkdocs import _generate_nav_structure, generate_mkdocs_config


def test_generate_nav_structure() -> None:
    """Test navigation structure generation."""
    config = StructureConfig(
        docs_dir="docs",
        numbering=NumberingConfig(
            enabled=True,
            initial_prefix=10,
            dir_start_prefix=20,
            prefix_step=10,
            padding_width=3,
        ),
        structure=DocumentStructure(
            directories={
                "guides": ["getting-started.md", "advanced.md"],
                "reference": ["api.md"],
            },
            top_level_files=["index.md", "README.md"],
        ),
        use_markdown_headings=True,
        generate_mkdocs=True,
        mkdocs=MkDocsConfig(
            site_name="Test Docs",
            theme={"name": "material"},
            repo_url=None,
            markdown_extensions=None,
        ),
    )

    nav = _generate_nav_structure(config)
    assert nav[0] == {"Home": "index.md"}
    assert {
        "Guides": [
            {"Getting Started": "guides/getting-started.md"},
            {"Advanced": "guides/advanced.md"},
        ]
    } in nav
    assert {"Reference": [{"Api": "reference/api.md"}]} in nav


def test_generate_mkdocs_config(tmp_path: Path) -> None:
    """Test MkDocs configuration file generation."""
    config = StructureConfig(
        docs_dir="docs",
        numbering=NumberingConfig(
            enabled=True,
            initial_prefix=10,
            dir_start_prefix=20,
            prefix_step=10,
            padding_width=3,
        ),
        structure=DocumentStructure(
            directories={
                "guides": ["getting-started.md"],
                "reference": ["api.md"],
            },
            top_level_files=["index.md"],
        ),
        use_markdown_headings=True,
        generate_mkdocs=True,
        mkdocs=MkDocsConfig(
            site_name="Test Docs",
            theme={"name": "material"},
            repo_url="https://github.com/test/repo",
            markdown_extensions=None,
        ),
    )

    generate_mkdocs_config(config, tmp_path)
    mkdocs_file = tmp_path / "mkdocs.yaml"
    assert mkdocs_file.exists()

    with mkdocs_file.open() as f:
        import yaml

        mkdocs_config = yaml.safe_load(f)

    assert mkdocs_config["site_name"] == "Test Docs"
    assert mkdocs_config["theme"]["name"] == "material"
    assert mkdocs_config["repo_url"] == "https://github.com/test/repo"
    assert mkdocs_config["docs_dir"] == "docs"
    assert len(mkdocs_config["nav"]) == 3  # Home + 2 sections


def test_generate_mkdocs_config_minimal(tmp_path: Path) -> None:
    """Test MkDocs configuration with minimal settings."""
    config = StructureConfig(
        docs_dir="docs",
        numbering=NumberingConfig(
            enabled=False,
            initial_prefix=10,
            dir_start_prefix=20,
            prefix_step=10,
            padding_width=3,
        ),
        structure=DocumentStructure(
            directories={},
            top_level_files=["index.md"],
        ),
        use_markdown_headings=True,
        generate_mkdocs=True,
        mkdocs=MkDocsConfig(
            site_name="Documentation",
            theme={"name": "material"},
            repo_url=None,
            markdown_extensions=None,
        ),
    )

    generate_mkdocs_config(config, tmp_path)
    mkdocs_file = tmp_path / "mkdocs.yaml"

    with mkdocs_file.open() as f:
        import yaml

        mkdocs_config = yaml.safe_load(f)

    assert mkdocs_config["site_name"] == "Documentation"
    assert mkdocs_config["theme"]["name"] == "material"
    assert mkdocs_config["docs_dir"] == "docs"
    assert len(mkdocs_config["nav"]) == 1  # Just Home


def test_generate_nav_structure_with_numbered_prefixes() -> None:
    """Test nav structure generation with numbered prefixes."""
    config = StructureConfig(
        docs_dir="docs",
        numbering=NumberingConfig(
            enabled=True,
            initial_prefix=10,
            dir_start_prefix=20,
            prefix_step=10,
            padding_width=3,
        ),
        structure=DocumentStructure(
            directories={
                "guides": ["010_getting-started.md", "020_advanced.md"],
            },
            top_level_files=["010_index.md"],
        ),
        use_markdown_headings=True,
        generate_mkdocs=True,
        mkdocs=MkDocsConfig(
            site_name="Documentation",
            theme={"name": "material"},
            repo_url=None,
            markdown_extensions=None,
        ),
    )

    nav = _generate_nav_structure(config)
    assert nav[0] == {"Home": "010_index.md"}
    assert nav[1] == {
        "Guides": [
            {"Getting Started": "guides/010_getting-started.md"},
            {"Advanced": "guides/020_advanced.md"},
        ]
    }


def test_generate_mkdocs_config_with_extra_settings(tmp_path: Path) -> None:
    """Test MkDocs configuration with additional settings."""
    config = StructureConfig(
        docs_dir="docs",
        numbering=NumberingConfig(
            enabled=False,
            initial_prefix=10,
            dir_start_prefix=20,
            prefix_step=10,
            padding_width=3,
        ),
        structure=DocumentStructure(
            directories={},
            top_level_files=["index.md"],
        ),
        use_markdown_headings=True,
        generate_mkdocs=True,
        mkdocs=MkDocsConfig(
            site_name="Test Docs",
            theme={"name": "material"},
            repo_url=None,
            markdown_extensions=["toc", "admonition"],
        ),
    )

    generate_mkdocs_config(config, tmp_path)
    mkdocs_file = tmp_path / "mkdocs.yaml"

    with mkdocs_file.open() as f:
        import yaml

        mkdocs_config = yaml.safe_load(f)

    assert "markdown_extensions" in mkdocs_config
    assert mkdocs_config["markdown_extensions"] == ["toc", "admonition"]
