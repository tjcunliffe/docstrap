"""Tests for the CLI module."""

import argparse
import logging
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from docstrap.cli import (
    create_parser,
    create_structure,
    init_config,
    main,
    setup_logging,
)
from docstrap.config.models import (
    DocumentationError,
    DocumentStructure,
    MkDocsConfig,
    NumberingConfig,
    StructureConfig,
)
from docstrap.config.template import STARTER_CONFIG
from docstrap.fs.handler import (
    DryRunFileHandler,
    InteractiveFileHandler,
    SilentFileHandler,
)


def test_create_parser() -> None:
    """Test parser creation and argument handling."""
    parser = create_parser()

    # Test init command
    args = parser.parse_args(["init"])
    assert args.command == "init"
    assert not args.force

    args = parser.parse_args(["init", "-f"])
    assert args.command == "init"
    assert args.force

    # Test create command
    args = parser.parse_args(["create", "-c", "config.yaml"])
    assert args.command == "create"
    assert args.config == "config.yaml"
    assert not args.dry_run
    assert not args.yes
    assert not args.verbose
    assert not args.mkdocs

    args = parser.parse_args(
        [
            "create",
            "-c",
            "config.yaml",
            "-d",
            "project",
            "--dry-run",
            "-y",
            "-v",
            "--mkdocs",
        ]
    )
    assert args.command == "create"
    assert args.config == "config.yaml"
    assert args.directory == "project"
    assert args.dry_run
    assert args.yes
    assert args.verbose
    assert args.mkdocs


def test_init_config(tmp_path: Path) -> None:
    """Test configuration file generation."""
    with patch("pathlib.Path.cwd", return_value=tmp_path):
        # Test normal creation
        with (
            patch("pathlib.Path.exists", return_value=False),
            patch("pathlib.Path.write_text") as mock_write,
        ):
            assert init_config() == 0
            mock_write.assert_called_once_with(STARTER_CONFIG)

        # Test existing file without force
        with patch("pathlib.Path.exists", return_value=True):
            assert init_config() == 1

        # Test existing file with force
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("pathlib.Path.write_text") as mock_write,
        ):
            assert init_config(force=True) == 0
            mock_write.assert_called_once_with(STARTER_CONFIG)


def test_setup_logging() -> None:
    """Test logging configuration."""
    with patch("logging.basicConfig") as mock_basic_config:
        # Test normal logging level
        setup_logging(verbose=False)
        mock_basic_config.assert_called_with(level=logging.INFO, format="%(message)s")

        # Test verbose logging level
        setup_logging(verbose=True)
        mock_basic_config.assert_called_with(level=logging.DEBUG, format="%(message)s")


def test_create_structure_handlers(tmp_path: Path) -> None:
    """Test create_structure with different file handlers."""
    config_path = tmp_path / "docstrap.yaml"
    config_path.write_text(STARTER_CONFIG)

    # Test with dry run
    args = argparse.Namespace(
        config=str(config_path),
        directory=None,
        dry_run=True,
        yes=False,
        verbose=False,
        mkdocs=False,
    )
    with patch("docstrap.cli.DocumentationManager") as mock_manager:
        assert create_structure(args) == 0
        manager_instance = mock_manager.call_args[0][1]
        assert isinstance(manager_instance, DryRunFileHandler)

    # Test with silent mode
    args.dry_run = False
    args.yes = True
    with patch("docstrap.cli.DocumentationManager") as mock_manager:
        assert create_structure(args) == 0
        manager_instance = mock_manager.call_args[0][1]
        assert isinstance(manager_instance, SilentFileHandler)

    # Test with interactive mode
    args.yes = False
    with patch("docstrap.cli.DocumentationManager") as mock_manager:
        assert create_structure(args) == 0
        manager_instance = mock_manager.call_args[0][1]
        assert isinstance(manager_instance, InteractiveFileHandler)


def test_create_structure_with_mkdocs(tmp_path: Path) -> None:
    """Test create_structure with MkDocs configuration."""
    config_path = tmp_path / "docstrap.yaml"
    config_path.write_text(STARTER_CONFIG)

    # Test with mkdocs flag
    args = argparse.Namespace(
        config=str(config_path),
        directory=None,
        dry_run=False,
        yes=True,
        verbose=False,
        mkdocs=True,
    )

    test_config = StructureConfig(
        docs_dir="docs",
        numbering=NumberingConfig(
            enabled=False,
            initial_prefix=10,
            dir_start_prefix=20,
            prefix_step=10,
            padding_width=3,
        ),
        structure=DocumentStructure(
            directories={"guides": ["getting-started.md"]},
            top_level_files=["index.md"],
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

    with (
        patch("docstrap.cli.DocumentationManager") as mock_manager,
        patch("docstrap.cli.generate_mkdocs_config") as mock_mkdocs,
        patch("docstrap.cli.load_config", return_value=test_config),
    ):
        assert create_structure(args) == 0
        mock_mkdocs.assert_called_once()

    # Test with generate_mkdocs in config
    args.mkdocs = False
    with (
        patch("docstrap.cli.load_config", return_value=test_config),
        patch("docstrap.cli.DocumentationManager") as mock_manager,
        patch("docstrap.cli.generate_mkdocs_config") as mock_mkdocs,
    ):
        assert create_structure(args) == 0
        mock_mkdocs.assert_called_once()

    # Test mkdocs generation error
    with (
        patch("docstrap.cli.load_config", return_value=test_config),
        patch("docstrap.cli.DocumentationManager") as mock_manager,
        patch(
            "docstrap.cli.generate_mkdocs_config",
            side_effect=ValueError("test error"),
        ),
    ):
        assert create_structure(args) == 1


def test_create_structure_error_handling(tmp_path: Path) -> None:
    """Test error handling in create_structure."""
    config_path = tmp_path / "docstrap.yaml"
    config_path.write_text(STARTER_CONFIG)
    args = argparse.Namespace(
        config=str(config_path),
        directory=None,
        dry_run=False,
        yes=False,
        verbose=True,
        mkdocs=False,
    )

    # Test DocumentationError
    with patch(
        "docstrap.cli.load_config", side_effect=DocumentationError("test error")
    ):
        assert create_structure(args) == 1

    # Test OSError
    with patch("docstrap.cli.load_config", side_effect=OSError("test error")):
        assert create_structure(args) == 1

    # Test ValueError
    with patch("docstrap.cli.load_config", side_effect=ValueError("test error")):
        assert create_structure(args) == 1

    # Test KeyboardInterrupt
    with patch("docstrap.cli.load_config", side_effect=KeyboardInterrupt()):
        assert create_structure(args) == 130


@pytest.mark.parametrize(
    "command,expected_code",
    [
        ([], 1),  # No command
        (["init"], 0),  # Init command
        (["init", "-f"], 0),  # Init with force
        (["create"], 2),  # Create without config
        (["create", "-c", "missing.yaml"], 1),  # Create with missing config
    ],
)
def test_main_return_codes(
    command: list[str], expected_code: int, tmp_path: Path
) -> None:
    """Test main function return codes for different scenarios."""
    with (
        patch("sys.argv", ["docstrap"] + command),
        patch("pathlib.Path.cwd", return_value=tmp_path),
        patch("docstrap.cli.init_config", return_value=0),
    ):
        if expected_code == 2:
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == expected_code
        elif command and command[0] == "create" and len(command) > 2:
            # Mock load_config to fail for missing.yaml
            with patch("docstrap.cli.load_config", side_effect=FileNotFoundError()):
                assert main() == expected_code
        else:
            assert main() == expected_code


@patch("docstrap.cli.DocumentationManager")
def test_create_structure_integration(mock_manager: Mock, tmp_path: Path) -> None:
    """Test create command with valid config."""
    config_path = tmp_path / "docstrap.yaml"
    config_path.write_text(STARTER_CONFIG)

    with (
        patch("sys.argv", ["docstrap", "create", "-c", str(config_path)]),
        patch("pathlib.Path.cwd", return_value=tmp_path),
    ):
        assert main() == 0
        mock_manager.return_value.create_structure.assert_called_once()


def test_create_structure_custom_directory(tmp_path: Path) -> None:
    """Test create_structure with custom directory path."""
    config_path = tmp_path / "docstrap.yaml"
    config_path.write_text(STARTER_CONFIG)
    custom_dir = tmp_path / "custom"

    args = argparse.Namespace(
        config=str(config_path),
        directory=str(custom_dir),
        dry_run=False,
        yes=False,
        verbose=False,
        mkdocs=False,
    )

    with patch("docstrap.cli.DocumentationManager") as mock_manager:
        assert create_structure(args) == 0
        mock_manager.return_value.create_structure.assert_called_once_with(custom_dir)
