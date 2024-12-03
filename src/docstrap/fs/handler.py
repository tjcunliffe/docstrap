"""
File system handlers for docstrap.

This module provides different file handlers for managing file system operations,
including interactive, silent, and dry-run modes.
"""

import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class FileSystemError(Exception):
    """Raised when there's an error during file system operations."""


class FileHandler:
    """Base class for file system operations."""

    def create(self, path: Path, content: str = "") -> None:
        """Create a file with optional content."""
        raise NotImplementedError

    def remove(self, path: Path) -> None:
        """Remove a file."""
        raise NotImplementedError

    def remove_dir(self, path: Path) -> None:
        """Remove a directory and its contents."""
        raise NotImplementedError


class DryRunFileHandler(FileHandler):
    """Handler that only logs operations without making changes."""

    def create(self, path: Path, content: str = "") -> None:
        """Log file creation without actually creating it."""
        logger.info("Would create file: %s", path)
        if content:
            logger.debug("With content:\n%s", content)

    def remove(self, path: Path) -> None:
        """Log file removal without actually removing it."""
        if path.exists():
            logger.info("Would remove file: %s", path)

    def remove_dir(self, path: Path) -> None:
        """Log directory removal without actually removing it."""
        if path.exists():
            logger.info("Would remove directory: %s", path)
            for item in path.rglob("*"):
                logger.debug("Would remove: %s", item)


class SilentFileHandler(FileHandler):
    """Handler that performs operations without prompting."""

    def create(self, path: Path, content: str = "") -> None:
        """Create a file without prompting."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            logger.info("Created file: %s", path)
        except OSError as e:
            raise FileSystemError(f"Error creating file {path}: {e}") from e

    def remove(self, path: Path) -> None:
        """Remove a file without prompting."""
        try:
            if path.exists():
                path.unlink()
                logger.info("Removed file: %s", path)
        except OSError as e:
            raise FileSystemError(f"Error removing file {path}: {e}") from e

    def remove_dir(self, path: Path) -> None:
        """Remove a directory without prompting."""
        try:
            if path.exists():
                shutil.rmtree(path)
                logger.info("Removed directory: %s", path)
        except OSError as e:
            raise FileSystemError(f"Error removing directory {path}: {e}") from e


class InteractiveFileHandler(FileHandler):
    """Handler that prompts before operations."""

    def create(self, path: Path, content: str = "") -> None:
        """Create a file with prompt."""
        try:
            if path.exists():
                logger.info("File exists: %s", path)
                try:
                    response = input("Overwrite? (y/N): ").strip().lower()
                except (KeyboardInterrupt, EOFError):
                    logger.info("\nSkipping file creation")
                    return

                if response != "y":
                    logger.info("Skipping file creation")
                    return

            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            logger.info("Created file: %s", path)
        except OSError as e:
            raise FileSystemError(f"Error creating file {path}: {e}") from e

    def remove(self, path: Path) -> None:
        """Remove a file with prompt."""
        try:
            if path.exists():
                logger.info("Remove file: %s", path)
                try:
                    response = input("Proceed? (y/N): ").strip().lower()
                except (KeyboardInterrupt, EOFError):
                    logger.info("\nSkipping file removal")
                    return

                if response != "y":
                    logger.info("Skipping file removal")
                    return
                path.unlink()
                logger.info("Removed file: %s", path)
        except OSError as e:
            raise FileSystemError(f"Error removing file {path}: {e}") from e

    def remove_dir(self, path: Path) -> None:
        """Remove a directory with prompt."""
        try:
            if path.exists():
                logger.info("Remove directory: %s", path)
                try:
                    response = input("Proceed? (y/N): ").strip().lower()
                except (KeyboardInterrupt, EOFError):
                    logger.info("\nSkipping directory removal")
                    return

                if response != "y":
                    logger.info("Skipping directory removal")
                    return
                shutil.rmtree(path)
                logger.info("Removed directory: %s", path)
        except OSError as e:
            raise FileSystemError(f"Error removing directory {path}: {e}") from e
