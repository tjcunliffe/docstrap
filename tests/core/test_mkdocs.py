"""Tests for MkDocs configuration generation."""

from pathlib import Path

import pytest
import yaml

from docstrap.core.mkdocs import _generate_nav_structure, generate_mkdocs_config


def test_generate_nav_structure() -> None:
    """Test navigation structure generation."""
    docs_dir = "docs"
    directories = {
        "guides": ["getting-started.md", "advanced.md"],
        "reference": ["api.md"],
    }
    top_level_files = ["index.md", "README.md"]

    # Test with numbered prefixes
    nav = _generate_nav_structure(
        docs_dir, directories, top_level_files, use_numbered_prefix=True
    )
    assert nav[0] == {"Home": "index.md"}
    assert {
        "Guides": [
            {"Getting Started": "guides/getting-started.md"},
            {"Advanced": "guides/advanced.md"},
        ]
    } in nav
    assert {"Reference": [{"Api": "reference/api.md"}]} in nav

    # Test without numbered prefixes
    nav = _generate_nav_structure(
        docs_dir, directories, top_level_files, use_numbered_prefix=False
    )
    assert nav[0] == {"Home": "index.md"}
    assert {
        "Guides": [
            {"Getting Started": "guides/getting-started.md"},
            {"Advanced": "guides/advanced.md"},
        ]
    } in nav


def test_generate_mkdocs_config(tmp_path: Path) -> None:
    """Test MkDocs configuration file generation."""
    config = {
        "docs_dir": "docs",
        "directories": {
            "guides": ["getting-started.md"],
            "reference": ["api.md"],
        },
        "top_level_files": ["index.md"],
        "use_numbered_prefix": True,
        "mkdocs_config": {
            "site_name": "Test Docs",
            "theme": {"name": "material"},
            "repo_url": "https://github.com/test/repo",
        },
    }

    generate_mkdocs_config(config, tmp_path)
    mkdocs_file = tmp_path / "mkdocs.yaml"
    assert mkdocs_file.exists()

    with mkdocs_file.open() as f:
        mkdocs_config = yaml.safe_load(f)

    assert mkdocs_config["site_name"] == "Test Docs"
    assert mkdocs_config["theme"]["name"] == "material"
    assert mkdocs_config["repo_url"] == "https://github.com/test/repo"
    assert mkdocs_config["docs_dir"] == "docs"
    assert len(mkdocs_config["nav"]) == 3  # Home + 2 sections


def test_generate_mkdocs_config_minimal(tmp_path: Path) -> None:
    """Test MkDocs configuration with minimal settings."""
    config = {
        "docs_dir": "docs",
        "directories": {},
        "top_level_files": ["index.md"],
    }

    generate_mkdocs_config(config, tmp_path)
    mkdocs_file = tmp_path / "mkdocs.yaml"

    with mkdocs_file.open() as f:
        mkdocs_config = yaml.safe_load(f)

    assert mkdocs_config["site_name"] == "Documentation"
    assert mkdocs_config["theme"]["name"] == "material"
    assert mkdocs_config["docs_dir"] == "docs"
    assert len(mkdocs_config["nav"]) == 1  # Just Home


def test_generate_nav_structure_with_numbered_prefixes() -> None:
    """Test nav structure generation with numbered prefixes."""
    docs_dir = "docs"
    directories = {
        "guides": ["010_getting-started.md", "020_advanced.md"],
    }
    top_level_files = ["010_index.md"]

    nav = _generate_nav_structure(
        docs_dir, directories, top_level_files, use_numbered_prefix=True
    )

    assert nav[0] == {"Home": "010_index.md"}
    assert nav[1] == {
        "Guides": [
            {"Getting Started": "guides/010_getting-started.md"},
            {"Advanced": "guides/020_advanced.md"},
        ]
    }


def test_generate_mkdocs_config_with_extra_settings(tmp_path: Path) -> None:
    """Test MkDocs configuration with additional settings."""
    config = {
        "docs_dir": "docs",
        "directories": {},
        "top_level_files": ["index.md"],
        "mkdocs_config": {
            "site_name": "Test Docs",
            "markdown_extensions": [
                "toc",
                "admonition",
            ],
            "plugins": ["search"],
        },
    }

    generate_mkdocs_config(config, tmp_path)
    mkdocs_file = tmp_path / "mkdocs.yaml"

    with mkdocs_file.open() as f:
        mkdocs_config = yaml.safe_load(f)

    assert "markdown_extensions" in mkdocs_config
    assert "plugins" in mkdocs_config
    assert mkdocs_config["markdown_extensions"] == ["toc", "admonition"]
    assert mkdocs_config["plugins"] == ["search"]
