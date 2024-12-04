"""MkDocs configuration generator for docstrap."""

from pathlib import Path
from typing import Dict, List, Union

import yaml

from ..config.models import StructureConfig

# Type aliases for nav structure
NavSection = Dict[str, str]
NavSectionList = List[Dict[str, str]]
NavItem = Dict[str, Union[str, NavSectionList]]


def _generate_nav_structure(config: StructureConfig) -> List[NavItem]:
    """Generate the nav structure for mkdocs.yaml.

    Args:
        config: The docstrap configuration

    Returns:
        List of nav items for mkdocs.yaml
    """
    nav: List[NavItem] = []

    # Add top-level files first
    for file in config.structure.top_level_files:
        name = Path(file).stem
        # Remove numbered prefix if used
        if config.numbering.enabled and name[0].isdigit():
            name = name[name.find("_") + 1 :]
        if name.lower() == "index":
            nav.append({"Home": f"{file}"})
        else:
            nav.append({name.replace("-", " ").title(): f"{file}"})

    # Add directory sections
    for dir_name, files in config.structure.directories.items():
        section_files: NavSectionList = []
        for file in files:
            name = Path(file).stem
            # Remove numbered prefix if used
            if config.numbering.enabled and name[0].isdigit():
                name = name[name.find("_") + 1 :]
            section_files.append({name.replace("-", " ").title(): f"{dir_name}/{file}"})
        nav.append({dir_name.replace("-", " ").title(): section_files})

    return nav


def generate_mkdocs_config(config: StructureConfig, output_dir: Path) -> None:
    """Generate mkdocs.yaml file based on docstrap configuration.

    Args:
        config: The docstrap configuration
        output_dir: Directory where mkdocs.yaml should be created
    """
    if not config.mkdocs:
        raise ValueError("MkDocs configuration is not present in config")

    mkdocs_config = {
        "site_name": config.mkdocs.site_name,
        "docs_dir": config.docs_dir,
        "theme": config.mkdocs.theme,
        "nav": _generate_nav_structure(config),
    }

    # Add optional configurations
    if config.mkdocs.repo_url:
        mkdocs_config["repo_url"] = config.mkdocs.repo_url
    if config.mkdocs.markdown_extensions:
        mkdocs_config["markdown_extensions"] = config.mkdocs.markdown_extensions

    # Write the mkdocs.yaml file
    mkdocs_path = output_dir / "mkdocs.yaml"
    with mkdocs_path.open("w", encoding="utf-8") as f:
        yaml.dump(mkdocs_config, f, default_flow_style=False, sort_keys=False)
