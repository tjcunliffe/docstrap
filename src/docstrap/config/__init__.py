"""Configuration module for docstrap."""

from .loader import load_config
from .models import StructureConfig, DocumentationError, NumberingConfig, DocumentStructure

__all__ = ['load_config', 'StructureConfig', 'DocumentationError', 'NumberingConfig', 'DocumentStructure']
