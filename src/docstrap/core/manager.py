"""
Core management functionality for docstrap.

This module provides the main interface for creating and managing
documentation directory structures.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Set

from ..config.models import DocumentationError, StructureConfig
from ..fs.handler import FileHandler
from ..fs.migrator import DirectoryMigrator
from .formatter import FilenameFormatter

logger = logging.getLogger(__name__)


class DocumentationManager:
    """Manages the creation and maintenance of documentation directory structures."""

    def __init__(self, config: StructureConfig, file_handler: FileHandler):
        """
        Initialize the Documentation Manager.

        Args:
            config: Configuration object.
            file_handler: Handler for file system operations.
        """
        self.config = config
        self.file_handler = file_handler
        self.formatter = FilenameFormatter()
        self.migrator = DirectoryMigrator(file_handler)

    def create_structure(self, project_root: Optional[Path] = None) -> None:
        """
        Create the complete documentation directory structure.

        Args:
            project_root: Optional root directory. If not provided,
                        uses the current working directory.

        Raises:
            DocumentationError: If there's an error creating the structure.
        """
        if project_root is None:
            project_root = Path.cwd()

        docs_dir = project_root / self.config.docs_dir

        try:
            # Handle directory migration if needed
            self.migrator.handle_directory_change(project_root, docs_dir)

            # Create docs directory
            docs_dir.mkdir(exist_ok=True)

            # Clean up any existing content that doesn't match the current format
            self._cleanup_mismatched_content(docs_dir)

            # Create top-level files
            self._create_top_level_files(docs_dir)

            # Create directory structure
            self._create_directories(docs_dir)

            logger.info("Documentation structure created successfully in %s", docs_dir)

        except Exception as e:
            raise DocumentationError(f"Error creating directory structure: {e}") from e

    def _handle_multiple_versions(self, dirs: List[Path]) -> None:
        """
        Handle multiple versions of the same directory.

        Args:
            dirs: List of directory paths to handle.
        """
        base_name = self.formatter.get_base_name(dirs[0])
        logger.info("\nFound multiple versions of '%s' directory:", base_name)
        for idx, dir_path in enumerate(dirs, 1):
            logger.info("%d. %s", idx, dir_path)

        try:
            response = input(
                "\nSelect which version to keep (or 'n' to skip): "
            ).strip()
            if response.lower() == "n":
                return

            try:
                idx = int(response) - 1
                if 0 <= idx < len(dirs):
                    # Remove all other versions
                    for i, dir_path in enumerate(dirs):
                        if i != idx and dir_path.exists():
                            self.file_handler.remove_dir(dir_path)
            except ValueError:
                logger.warning("Invalid input. Skipping.")
        except (KeyboardInterrupt, EOFError):
            logger.warning("\nOperation cancelled by user.")

    def _cleanup_mismatched_content(self, directory: Path) -> None:
        """
        Clean up content that doesn't match the current numbering format.

        Args:
            directory: Directory to clean up.
        """
        if not directory.exists():
            return

        # Get all directories (both numbered and unnumbered)
        all_dirs: Set[Path] = set()
        for pattern in ["[0-9][0-9][0-9]_*", "*"]:
            all_dirs.update(
                d for d in directory.glob(pattern) if d.is_dir() and d.name != ".git"
            )

        # Group directories by their base name
        dir_groups: Dict[str, Set[Path]] = {}
        for dir_path in all_dirs:
            base_name = self.formatter.get_base_name(dir_path)
            if base_name not in dir_groups:
                dir_groups[base_name] = set()
            dir_groups[base_name].add(dir_path)

        # Handle each group
        for dirs in dir_groups.values():
            dirs_list = sorted(dirs)
            if len(dirs_list) > 1:
                self._handle_multiple_versions(dirs_list)
            else:
                # Single directory - check if format matches current configuration
                dir_path = next(iter(dirs))
                has_number = bool(re.match(r"^\d+_", dir_path.name))
                if (self.config.numbering.enabled and not has_number) or (
                    not self.config.numbering.enabled and has_number
                ):
                    self.file_handler.remove_dir(dir_path)

    def _create_top_level_files(self, docs_dir: Path) -> None:
        """
        Create top-level files.

        Args:
            docs_dir: Documentation directory for the structure.
        """
        logger.info("Creating top-level files...")

        # Create configured top-level files
        for idx, file in enumerate(self.config.structure.top_level_files, start=1):
            self._create_file(docs_dir, file, idx)

    def _create_directories(self, docs_dir: Path) -> None:
        """
        Create directory structure with files.

        Args:
            docs_dir: Documentation directory for the structure.
        """
        for idx, (dir_name, files) in enumerate(
            self.config.structure.directories.items(), start=1
        ):
            dir_path = self._get_directory_path(docs_dir, dir_name, idx)
            dir_path.mkdir(exist_ok=True)
            logger.info("Creating directory: %s", dir_path)

            for file_idx, file in enumerate(files, start=1):
                self._create_file(dir_path, file, file_idx)

    def _create_file(self, parent_dir: Path, filename: str, index: int) -> None:
        """
        Create a file with optional numbering and markdown heading.

        Args:
            parent_dir: Directory to create the file in.
            filename: Name of the file to create.
            index: Index for numbered prefix.
        """
        sanitized_name = self.formatter.sanitize(filename)
        final_name = (
            self._get_numbered_name(sanitized_name, index)
            if self.config.numbering.enabled
            else sanitized_name
        )

        content = ""
        if self.config.use_markdown_headings and filename.endswith(".md"):
            title = self.formatter.to_title(sanitized_name)
            content = f"# {title}\n"

        self.file_handler.create(parent_dir / final_name, content)

    def _get_numbered_name(self, filename: str, index: int) -> str:
        """
        Generate numbered filename.

        Args:
            filename: Base filename.
            index: Index for the number prefix.

        Returns:
            str: Filename with number prefix.
        """
        prefix = index * self.config.numbering.prefix_step
        padded_prefix = f"{prefix:0{self.config.numbering.padding_width}d}"
        return f"{padded_prefix}_{filename}"

    def _get_directory_path(self, docs_dir: Path, dir_name: str, index: int) -> Path:
        """
        Get directory path with optional numbering.

        Args:
            docs_dir: Documentation directory.
            dir_name: Name of the directory.
            index: Index for numbered prefix.

        Returns:
            Path: Complete path for the directory.
        """
        if self.config.numbering.enabled:
            prefix = index * self.config.numbering.dir_start_prefix
            padded_prefix = f"{prefix:0{self.config.numbering.padding_width}d}"
            return docs_dir / f"{padded_prefix}_{dir_name}"
        return docs_dir / dir_name
