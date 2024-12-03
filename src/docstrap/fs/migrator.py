"""
Directory migration functionality for docstrap.

This module provides functionality for migrating between different
documentation directory structures.
"""

import logging
from pathlib import Path
from typing import List, Optional

from .handler import FileHandler, FileSystemError

logger = logging.getLogger(__name__)


class DirectoryMigrator:
    """Handles migration between different directory structures."""

    def __init__(self, file_handler: FileHandler):
        """
        Initialize the Directory Migrator.

        Args:
            file_handler: Handler for file system operations.
        """
        self.file_handler = file_handler

    def handle_directory_change(self, project_root: Path, target_dir: Path) -> None:
        """
        Handle migration when directory structure changes.

        Args:
            project_root: Project root directory.
            target_dir: Target documentation directory.

        Raises:
            FileSystemError: If there's an error during migration.
        """
        # Check if target directory exists and has content
        if target_dir.exists() and any(target_dir.iterdir()):
            raise FileSystemError("Target directory already exists and contains files")

        # Find existing documentation directories
        source_dirs = self.find_isms_directories(project_root, target_dir)
        if not source_dirs:
            return

        # Handle migration based on number of sources
        if len(source_dirs) == 1:
            self._handle_single_source(source_dirs[0], target_dir)
        else:
            self._handle_multiple_sources(source_dirs, target_dir)

    def _handle_single_source(self, source_dir: Path, target_dir: Path) -> None:
        """Handle migration from a single source directory."""
        if self._confirm_migration(source_dir, target_dir):
            self._migrate_directory(source_dir, target_dir)

    def _handle_multiple_sources(
        self, source_dirs: List[Path], target_dir: Path
    ) -> None:
        """Handle migration when multiple source directories exist."""
        logger.info("Found multiple documentation directories:")
        for idx, dir_path in enumerate(source_dirs, 1):
            logger.info("%d. %s", idx, dir_path)

        try:
            response = input("\nSelect directory to migrate (or 'n' to skip): ").strip()
            if response.lower() == "n":
                return

            source_dir = self._get_selected_source(response, source_dirs)
            if source_dir and self._confirm_migration(source_dir, target_dir):
                self._migrate_directory(source_dir, target_dir)
        except (KeyboardInterrupt, EOFError):
            logger.warning("\nOperation cancelled by user.")

    def _get_selected_source(
        self, response: str, source_dirs: List[Path]
    ) -> Optional[Path]:
        """Get the selected source directory based on user input."""
        try:
            idx = int(response) - 1
            if 0 <= idx < len(source_dirs):
                return source_dirs[idx]
            logger.warning("Invalid selection. Skipping migration.")
        except ValueError:
            if response.lower() == "y" and source_dirs:
                return source_dirs[0]
            logger.warning("Invalid input. Skipping migration.")
        return None

    def find_isms_directories(
        self, project_root: Path, exclude_dir: Path
    ) -> List[Path]:
        """
        Find documentation directories in the project.

        Args:
            project_root: Project root directory.
            exclude_dir: Directory to exclude from search.

        Returns:
            List of found documentation directories.
        """
        result: List[Path] = []

        # Look for common documentation directory names
        patterns = ["docs", "documentation", "doc", "numbered_docs"]
        for pattern in patterns:
            for path in project_root.glob(pattern):
                if path.is_dir() and path != exclude_dir:
                    result.append(path)

        return sorted(result)

    def _migrate_directory(self, source_dir: Path, target_dir: Path) -> None:
        """
        Migrate content from source to target directory.

        Args:
            source_dir: Source directory to migrate from.
            target_dir: Target directory to migrate to.

        Raises:
            FileSystemError: If there's an error during migration.
        """
        try:
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)

            # Copy all files
            for source_file in source_dir.rglob("*"):
                if source_file.is_file():
                    rel_path = source_file.relative_to(source_dir)
                    target_file = target_dir / rel_path

                    # Create parent directories
                    target_file.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file content
                    content = source_file.read_text(encoding="utf-8")
                    self.file_handler.create(target_file, content)

            # Ask to remove source directory
            if self._confirm_removal(source_dir):
                self.file_handler.remove_dir(source_dir)

            # Clean up empty directories
            self._cleanup_empty_dirs(target_dir)

        except OSError as e:
            raise FileSystemError(f"Error during migration: {e}") from e

    def _cleanup_empty_dirs(self, directory: Path) -> None:
        """
        Remove empty directories recursively.

        Args:
            directory: Directory to clean up.
        """
        if not directory.exists():
            return

        for path in sorted(directory.rglob("*"), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()

    def _confirm_migration(self, source_dir: Path, target_dir: Path) -> bool:
        """
        Ask user to confirm migration.

        Args:
            source_dir: Source directory.
            target_dir: Target directory.

        Returns:
            True if user confirms, False otherwise.
        """
        logger.info("Migrate from %s to %s?", source_dir, target_dir)
        response = input("Proceed? (y/N): ").strip().lower()
        return response == "y"

    def _confirm_removal(self, directory: Path) -> bool:
        """
        Ask user to confirm directory removal.

        Args:
            directory: Directory to remove.

        Returns:
            True if user confirms, False otherwise.
        """
        logger.info("Remove original directory %s?", directory)
        response = input("Proceed? (y/N): ").strip().lower()
        return response == "y"
