"""
docstrap - A tool for bootstrapping and managing documentation directory structures.

This package provides tools and utilities for creating and managing standardized
documentation structures with support for numbered prefixes, markdown headings,
and configurable directory layouts.
"""

from .config import StructureConfig, DocumentationError
from .core import DocumentationManager
from .fs import FileHandler, InteractiveFileHandler, SilentFileHandler, DryRunFileHandler

__version__ = "0.1.0"

__all__ = [
    'StructureConfig',
    'DocumentationError',
    'DocumentationManager',
    'FileHandler',
    'InteractiveFileHandler',
    'SilentFileHandler',
    'DryRunFileHandler'
]
