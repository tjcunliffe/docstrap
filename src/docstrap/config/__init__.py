"""Configuration module for docstrap."""

from .loader import load_config
from .models import (
    DocumentationError,
    DocumentStructure,
    NumberingConfig,
    StructureConfig,
)

__all__ = [
    "load_config",
    "StructureConfig",
    "DocumentationError",
    "NumberingConfig",
    "DocumentStructure",
]
