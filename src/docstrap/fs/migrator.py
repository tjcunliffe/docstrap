"""
Directory migration functionality for ISMS Manager.

This module handles the migration of content between different directory structures,
including handling transitions between numbered and unnumbered formats.
"""

import logging
import re
from pathlib import Path
from typing import List, Set

from ..core.formatter import FilenameFormatter
from .handler import FileHandler, FileSystemError

logger = logging.getLogger(__name__)

class DirectoryMigrator:
    """Handles migration between different directory structures."""

    def __init__(self, file_handler: FileHandler):
        """
        Initialize the migrator.
        
        Args:
            file_handler: Handler for file system operations.
        """
        self.file_handler = file_handler
        self.formatter = FilenameFormatter()

    def find_isms_directories(self, project_root: Path, new_dir: Path) -> List[Path]:
        """
        Find all directories that appear to be ISMS directories.
        
        Args:
            project_root: Root directory to search in.
            new_dir: New directory path to exclude from results.
            
        Returns:
            List of paths to potential ISMS directories.
        """
        isms_dirs = set()  # Use set to avoid duplicates
        
        # Common paths to check
        check_paths = [
            project_root,  # Check root for directories like ISMS, ISMS-NEW, etc.
            project_root / 'docs',  # Check docs directory
        ]
        
        # Common patterns that indicate an ISMS directory
        # Include both numbered and unnumbered patterns
        patterns = [
            '**/[0-9][0-9][0-9]_policies/*.md',  # Numbered format
            '**/policies/*.md',                   # Unnumbered format
            '**/[0-9][0-9][0-9]_procedures/*.md',
            '**/procedures/*.md',
            '**/[0-9][0-9][0-9]_records/*.md',
            '**/records/*.md',
        ]
        
        for base_path in check_paths:
            if not base_path.exists():
                continue
                
            # Check immediate subdirectories
            for dir_path in base_path.iterdir():
                if not dir_path.is_dir() or dir_path == new_dir:
                    continue
                    
                # Check if directory contains ISMS-like structure
                for pattern in patterns:
                    if any(dir_path.glob(pattern)):
                        isms_dirs.add(dir_path)
                        break
        
        # Convert to sorted list for consistent ordering
        return sorted(isms_dirs)

    def handle_directory_change(self, project_root: Path, new_dir: Path) -> None:
        """
        Handle change in base directory name.
        
        Args:
            project_root: Root directory containing the ISMS directories.
            new_dir: Path to the new directory location.
            
        Raises:
            FileSystemError: If there's an error during migration.
        """
        # Find all potential ISMS directories
        existing_dirs = self.find_isms_directories(project_root, new_dir)
        
        if not existing_dirs:
            return

        if new_dir.exists():
            # Check if the directory has any content that isn't just empty subdirectories
            has_content = False
            for path in new_dir.rglob('*'):
                if path.is_file():
                    has_content = True
                    break
            if has_content:
                raise FileSystemError(f"New directory {new_dir} already exists and contains files")

        # If multiple directories found, ask user which one to migrate from
        if len(existing_dirs) > 1:
            logger.info("\nFound multiple potential ISMS directories:")
            for idx, dir_path in enumerate(existing_dirs, 1):
                logger.info(f"{idx}. {dir_path}")
            
            try:
                choice = input("\nEnter the number of the directory to migrate from (or 'n' to skip): ").strip()
                if choice.lower() == 'n':
                    return
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(existing_dirs):
                        old_dir = existing_dirs[idx]
                    else:
                        logger.warning("Invalid choice. Skipping migration.")
                        return
                except ValueError:
                    logger.warning("Invalid input. Skipping migration.")
                    return
            except (KeyboardInterrupt, EOFError):
                logger.warning("\nOperation cancelled by user.")
                return
        else:
            old_dir = existing_dirs[0]
            logger.info(f"\nFound existing ISMS directory: {old_dir}")
            if not self._confirm_migration(old_dir, new_dir):
                return

        # Clean up any empty directories at the new location
        if new_dir.exists():
            self._cleanup_empty_dirs(new_dir)

        # Proceed with migration
        self._migrate_directory(old_dir, new_dir)

    def _cleanup_empty_dirs(self, directory: Path) -> None:
        """
        Remove empty directories recursively.
        
        Args:
            directory: Directory to clean up.
        """
        if not directory.exists():
            return

        for path in sorted(directory.rglob('*'), reverse=True):
            if path.is_dir() and not any(path.iterdir()):
                path.rmdir()

    def _confirm_migration(self, old_dir: Path, new_dir: Path) -> bool:
        """
        Ask user if they want to migrate content to new directory.
        
        Args:
            old_dir: Source directory.
            new_dir: Destination directory.
            
        Returns:
            bool: True if user confirms, False otherwise.
        """
        try:
            response = input(
                f"\nWould you like to migrate content from '{old_dir}' to '{new_dir}'? [y/N] "
            ).lower().strip()
            return response == 'y'
        except (KeyboardInterrupt, EOFError):
            return False

    def _migrate_directory(self, source: Path, destination: Path) -> None:
        """
        Migrate content from old directory to new directory.
        
        Args:
            source: Source directory.
            destination: Destination directory.
            
        Raises:
            FileSystemError: If there's an error during migration.
        """
        try:
            # Create destination if it doesn't exist
            destination.mkdir(parents=True, exist_ok=True)
            
            # Copy all files, preserving directory structure
            for source_path in source.rglob('*'):
                if source_path.is_file():
                    # Calculate relative path from source root
                    rel_path = source_path.relative_to(source)
                    dest_path = destination / rel_path
                    
                    # Create parent directories if needed
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy the file
                    dest_path.write_bytes(source_path.read_bytes())
                    logger.info(f"Migrated: {rel_path}")
            
            logger.info(f"Migration from '{source}' to '{destination}' completed")
            
            # Ask if user wants to remove the old directory
            if self._confirm_removal(source):
                self.file_handler.remove_dir(source)
                
        except Exception as e:
            raise FileSystemError(f"Error during migration: {e}")

    def _confirm_removal(self, directory: Path) -> bool:
        """
        Ask user if they want to remove the old directory.
        
        Args:
            directory: Directory to potentially remove.
            
        Returns:
            bool: True if user confirms, False otherwise.
        """
        try:
            response = input(
                f"\nWould you like to remove '{directory}'? [y/N] "
            ).lower().strip()
            return response == 'y'
        except (KeyboardInterrupt, EOFError):
            return False
