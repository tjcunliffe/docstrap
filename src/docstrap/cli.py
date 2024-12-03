"""
Command-line interface for docstrap.

This module provides the command-line interface for creating and managing
documentation directory structures.
"""

import argparse
import logging
import sys
import traceback
from pathlib import Path

from .config import load_config
from .config.models import DocumentationError
from .config.template import STARTER_CONFIG
from .core.manager import DocumentationManager
from .fs.handler import (
    DryRunFileHandler,
    FileHandler,
    InteractiveFileHandler,
    SilentFileHandler,
)


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging based on verbosity level.

    Args:
        verbose: Whether to enable debug logging.
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO, format="%(message)s"
    )


def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.

    Returns:
        ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="docstrap - Bootstrap and manage documentation directory structures"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Init command
    init_parser = subparsers.add_parser(
        "init", help="Generate a starter configuration file"
    )
    init_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing configuration file",
    )

    # Create command
    structure_parser = subparsers.add_parser(
        "create", help="Create documentation structure"
    )
    structure_parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=True,
        help="Path to configuration file (e.g., docstrap.yaml)",
    )
    structure_parser.add_argument(
        "-d",
        "--directory",
        type=str,
        help="Project root directory (default: current directory)",
    )
    structure_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    structure_parser.add_argument(
        "-y", "--yes", action="store_true", help="Answer yes to all prompts"
    )
    structure_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    return parser


def init_config(force: bool = False) -> int:
    """
    Generate a starter configuration file.

    Args:
        force: Whether to overwrite existing configuration.

    Returns:
        int: Exit code (0 for success, non-zero for error).
    """
    config_path = Path("docstrap.yaml")
    if config_path.exists() and not force:
        logging.error("Configuration file already exists. Use -f to overwrite.")
        return 1

    try:
        config_path.write_text(STARTER_CONFIG)
        logging.info("Created configuration file: %s", config_path)
        return 0
    except OSError as e:
        logging.error("Error creating configuration file: %s", e)
        return 1


def create_structure(args: argparse.Namespace) -> int:
    """
    Create documentation structure based on configuration.

    Args:
        args: Command line arguments.

    Returns:
        int: Exit code (0 for success, non-zero for error).
    """
    try:
        # Load configuration
        config = load_config(args.config)

        # Determine project root
        if args.directory:
            project_root = Path(args.directory)
        else:
            project_root = Path.cwd()

        # Select appropriate file handler
        handler: FileHandler
        if args.dry_run:
            handler = DryRunFileHandler()
        elif args.yes:
            handler = SilentFileHandler()
        else:
            handler = InteractiveFileHandler()

        # Create and run the manager
        manager = DocumentationManager(config, handler)
        manager.create_structure(project_root)

        return 0

    except DocumentationError as e:
        logging.error("Configuration error: %s", e)
        return 1
    except KeyboardInterrupt:
        logging.error("\nOperation cancelled by user")
        return 130
    except OSError as e:
        logging.error("File system error: %s", e)
        if args.verbose:
            traceback.print_exc()
        return 1
    except ValueError as e:
        logging.error("Invalid value: %s", e)
        if args.verbose:
            traceback.print_exc()
        return 1


def main() -> int:
    """
    Main entry point for the CLI.

    Returns:
        int: Exit code (0 for success, non-zero for error).
    """
    parser = create_parser()
    args = parser.parse_args()

    # Configure logging
    setup_logging(getattr(args, "verbose", False))

    # Handle commands
    if args.command == "init":
        return init_config(args.force)
    if args.command == "create":
        return create_structure(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
