"""
File system operations for ISMS Manager.

This module provides classes for handling file system operations,
with support for interactive confirmation of destructive operations.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

class FileSystemError(Exception):
    """Raised when there's an error performing file system operations."""
    pass

class FileHandler(ABC):
    """Abstract base class for file operations."""
    
    @abstractmethod
    def create(self, path: Path, content: str = "") -> None:
        """
        Create a file with optional content.
        
        Args:
            path: Path where the file should be created.
            content: Optional content to write to the file.
            
        Raises:
            FileSystemError: If there's an error creating the file.
        """
        pass

    @abstractmethod
    def remove(self, path: Path) -> None:
        """
        Remove a file.
        
        Args:
            path: Path of the file to remove.
            
        Raises:
            FileSystemError: If there's an error removing the file.
        """
        pass

    @abstractmethod
    def remove_dir(self, path: Path) -> None:
        """
        Remove a directory and all its contents.
        
        Args:
            path: Path of the directory to remove.
            
        Raises:
            FileSystemError: If there's an error removing the directory.
        """
        pass

class InteractiveFileHandler(FileHandler):
    """File handler that asks for confirmation before destructive operations."""
    
    def create(self, path: Path, content: str = "") -> None:
        """Create a file with optional content."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            logger.info(f"Created file: {path}")
        except Exception as e:
            raise FileSystemError(f"Error creating file {path}: {e}")

    def remove(self, path: Path) -> None:
        """Remove a file with user confirmation."""
        try:
            if not path.exists():
                return
                
            if self._confirm_removal(path):
                path.unlink()
                logger.info(f"Removed file: {path}")
            else:
                logger.info(f"Skipped removal of: {path}")
        except Exception as e:
            raise FileSystemError(f"Error removing file {path}: {e}")

    def remove_dir(self, path: Path) -> None:
        """Remove a directory and all its contents with user confirmation."""
        try:
            if not path.exists():
                return
                
            if self._confirm_removal(path, is_dir=True):
                shutil.rmtree(path)
                logger.info(f"Removed directory: {path}")
            else:
                logger.info(f"Skipped removal of directory: {path}")
        except Exception as e:
            raise FileSystemError(f"Error removing directory {path}: {e}")

    def _confirm_removal(self, path: Path, is_dir: bool = False) -> bool:
        """
        Ask for user confirmation before removing a file or directory.
        
        Args:
            path: Path to the file or directory.
            is_dir: Whether the path is a directory.
            
        Returns:
            bool: True if the user confirmed, False otherwise.
        """
        try:
            item_type = "directory" if is_dir else "file"
            response = input(
                f"Remove {item_type} '{path}'? [y/N] "
            ).lower().strip()
            return response == 'y'
        except (KeyboardInterrupt, EOFError):
            logger.warning("\nOperation cancelled by user.")
            return False

class SilentFileHandler(FileHandler):
    """File handler that performs operations without confirmation."""
    
    def create(self, path: Path, content: str = "") -> None:
        """Create a file with optional content."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            logger.debug(f"Created file: {path}")
        except Exception as e:
            raise FileSystemError(f"Error creating file {path}: {e}")

    def remove(self, path: Path) -> None:
        """Remove a file without confirmation."""
        try:
            if path.exists():
                path.unlink()
                logger.debug(f"Removed file: {path}")
        except Exception as e:
            raise FileSystemError(f"Error removing file {path}: {e}")

    def remove_dir(self, path: Path) -> None:
        """Remove a directory and all its contents without confirmation."""
        try:
            if path.exists():
                shutil.rmtree(path)
                logger.debug(f"Removed directory: {path}")
        except Exception as e:
            raise FileSystemError(f"Error removing directory {path}: {e}")

class DryRunFileHandler(FileHandler):
    """File handler that logs operations without performing them."""
    
    def create(self, path: Path, content: str = "") -> None:
        """Log file creation without performing it."""
        logger.info(f"Would create file: {path}")
        if content:
            logger.debug(f"With content:\n{content}")

    def remove(self, path: Path) -> None:
        """Log file removal without performing it."""
        if path.exists():
            logger.info(f"Would remove file: {path}")

    def remove_dir(self, path: Path) -> None:
        """Log directory removal without performing it."""
        if path.exists():
            logger.info(f"Would remove directory: {path}")
            for item in path.rglob('*'):
                logger.debug(f"Would remove: {item}")
