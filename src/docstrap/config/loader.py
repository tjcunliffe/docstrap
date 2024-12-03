"""
Configuration loading functionality for docstrap.

This module provides functionality for loading and validating
configuration from YAML files.
"""

import logging
from pathlib import Path

import yaml

from .models import DocumentationError, StructureConfig

logger = logging.getLogger(__name__)


def load_config(config_path: str) -> StructureConfig:
    """
    Load and validate configuration from a YAML file.

    Args:
        config_path: Path to the configuration file.

    Returns:
        StructureConfig: Validated configuration object.

    Raises:
        DocumentationError: If there's an error loading or validating the config.
    """
    path = Path(config_path)

    # Check if file exists
    if not path.exists():
        raise DocumentationError("Configuration file not found")

    # Load YAML content
    try:
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise DocumentationError(f"Error parsing YAML file: {e}") from e

    # Validate basic structure
    if not isinstance(data, dict):
        raise DocumentationError("Configuration must be a YAML dictionary")

    # Create and validate config object
    try:
        config = StructureConfig.from_dict(data)
        config.validate()
        return config
    except DocumentationError as e:
        raise DocumentationError(f"Error loading configuration: {e}") from e
