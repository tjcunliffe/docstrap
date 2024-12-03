"""
Filename formatting utilities for ISMS Manager.

This module provides utilities for formatting and transforming filenames,
including sanitization, base name extraction, and title case conversion.
"""

import re
from pathlib import Path


class FilenameFormatter:
    """Handles filename formatting and transformation."""

    @staticmethod
    def sanitize(filename: str) -> str:
        """
        Sanitize and standardize filename.

        Converts filename to lowercase, replaces spaces with dashes,
        removes special characters, and handles multiple dashes.

        Args:
            filename: The filename to sanitize.

        Returns:
            str: The sanitized filename.

        Raises:
            ValueError: If filename is empty.

        Examples:
            >>> FilenameFormatter.sanitize("My File Name.md")
            'my-file-name.md'
            >>> FilenameFormatter.sanitize("multiple---dashes.txt")
            'multiple-dashes.txt'
        """
        if not filename:
            raise ValueError("Filename cannot be empty")

        # Split filename and extension
        parts = filename.rsplit(".", 1)
        name = parts[0]
        ext = f".{parts[1]}" if len(parts) > 1 else ""

        # Convert to lowercase and replace spaces with dashes
        sanitized = name.lower().replace(" ", "-")
        # Remove any special characters except dashes and dots
        sanitized = re.sub(r"[^a-z0-9\-]", "", sanitized)
        # Replace multiple dashes with single dash
        sanitized = re.sub(r"-+", "-", sanitized)
        # Remove leading/trailing dashes
        sanitized = sanitized.strip("-")

        return f"{sanitized}{ext}"

    @staticmethod
    def get_base_name(filepath: Path) -> str:
        """
        Extract base filename without numeric prefix.

        Args:
            filepath: Path object containing the filename.

        Returns:
            str: The filename without any numeric prefix.

        Examples:
            >>> FilenameFormatter.get_base_name(Path("010_file-name.md"))
            'file-name.md'
            >>> FilenameFormatter.get_base_name(Path("file-name.md"))
            'file-name.md'
        """
        return re.sub(r"^\d+_", "", filepath.name)

    @staticmethod
    def to_title(filename: str) -> str:
        """
        Convert filename to title case heading.

        Args:
            filename: The filename to convert.

        Returns:
            str: The filename converted to title case, without extension.

        Raises:
            ValueError: If filename is empty.

        Examples:
            >>> FilenameFormatter.to_title("information-security-policy.md")
            'Information Security Policy'
            >>> FilenameFormatter.to_title("simple-file.txt")
            'Simple File'
        """
        if not filename:
            raise ValueError("Filename cannot be empty")

        # Remove file extension and convert dashes to spaces
        title = filename.rsplit(".", 1)[0].replace("-", " ")
        # Title case the string
        return " ".join(word.capitalize() for word in title.split())
