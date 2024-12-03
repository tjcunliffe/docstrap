"""
Configuration loader for docstrap.

This module handles loading and validating configuration from YAML files.
"""

from pathlib import Path
from typing import Union
import yaml
from yaml.error import YAMLError

from .models import StructureConfig, DocumentationError

def load_config(config_path: Union[str, Path]) -> StructureConfig:
    """
    Load and validate configuration from a YAML file.
    
    Args:
        config_path: Path to the YAML configuration file.
        
    Returns:
        StructureConfig: Validated configuration object.
        
    Raises:
        DocumentationError: If the configuration file is invalid or missing.
    """
    try:
        config_path = Path(config_path)
        
        # If path is not absolute, make it relative to current working directory
        if not config_path.is_absolute():
            config_path = Path.cwd() / config_path
            
        if not config_path.exists():
            raise DocumentationError(f"Configuration file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            try:
                data = yaml.safe_load(f)
            except YAMLError as e:
                raise DocumentationError(f"Error parsing YAML file: {e}")
                
        if not isinstance(data, dict):
            raise DocumentationError("Configuration must be a YAML dictionary")
            
        config = StructureConfig.from_dict(data)
        config.validate()
        return config
        
    except Exception as e:
        if not isinstance(e, DocumentationError):
            raise DocumentationError(f"Error loading configuration: {e}")
        raise
