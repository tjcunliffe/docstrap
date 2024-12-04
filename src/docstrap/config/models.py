"""
Configuration models for docstrap.

This module contains the dataclasses that represent the configuration structure
for docstrap. These models are used to validate and type-check the
configuration loaded from YAML files.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


class DocumentationError(Exception):
    """Raised when there's an error in the documentation configuration."""


@dataclass
class NumberingConfig:
    """Configuration for file/directory numbering."""

    enabled: bool
    initial_prefix: int
    dir_start_prefix: int
    prefix_step: int
    padding_width: int

    @classmethod
    def from_dict(cls, data: dict) -> "NumberingConfig":
        """Create NumberingConfig from dictionary."""
        try:
            return cls(
                enabled=data["use_numbered_prefix"],
                initial_prefix=data["initial_prefix"],
                dir_start_prefix=data["dir_start_prefix"],
                prefix_step=data["prefix_step"],
                padding_width=data["padding_width"],
            )
        except KeyError as e:
            raise DocumentationError(
                f"Missing required numbering configuration: {e}"
            ) from e
        except (ValueError, TypeError) as e:
            raise DocumentationError(f"Invalid numbering configuration: {e}") from e

    def validate(self) -> None:
        """Validate the numbering configuration."""
        if self.initial_prefix < 1:
            raise DocumentationError("initial_prefix must be positive")
        if self.dir_start_prefix < 1:
            raise DocumentationError("dir_start_prefix must be positive")
        if self.prefix_step < 1:
            raise DocumentationError("prefix_step must be positive")
        if self.padding_width < 1:
            raise DocumentationError("padding_width must be positive")


@dataclass
class DocumentStructure:
    """Configuration for documentation directory structure."""

    directories: Dict[str, List[str]]
    top_level_files: List[str]

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentStructure":
        """Create DocumentStructure from dictionary."""
        try:
            if not isinstance(data.get("directories"), dict):
                raise DocumentationError("directories must be a dictionary")

            directories = {}
            for dir_name, files in data["directories"].items():
                if not isinstance(files, list):
                    raise DocumentationError(
                        f"Directory contents must be a list for {dir_name}"
                    )
                directories[dir_name] = files

            return cls(
                directories=directories, top_level_files=data.get("top_level_files", [])
            )
        except KeyError as e:
            raise DocumentationError(
                f"Missing required directory configuration: {e}"
            ) from e
        except (ValueError, TypeError) as e:
            raise DocumentationError(f"Invalid directory configuration: {e}") from e

    def validate(self) -> None:
        """Validate the directory structure configuration."""
        if not self.directories:
            raise DocumentationError("At least one directory must be configured")

        for dir_name, files in self.directories.items():
            if not isinstance(dir_name, str) or not dir_name:
                raise DocumentationError(f"Invalid directory name: {dir_name}")
            if "/" in dir_name or "\\" in dir_name:
                raise DocumentationError(
                    "Directory names cannot contain path separators"
                )
            if not isinstance(files, list):
                raise DocumentationError(
                    f"Files for directory {dir_name} must be a list"
                )
            for file in files:
                if not isinstance(file, str) or not file:
                    raise DocumentationError(f"Invalid file name in {dir_name}: {file}")
                if "/" in file or "\\" in file:
                    raise DocumentationError(
                        "File names cannot contain path separators"
                    )

        if not isinstance(self.top_level_files, list):
            raise DocumentationError("top_level_files must be a list")
        for file in self.top_level_files:
            if not isinstance(file, str) or not file:
                raise DocumentationError(f"Invalid top-level file name: {file}")
            if "/" in file or "\\" in file:
                raise DocumentationError("File names cannot contain path separators")


@dataclass
class MkDocsConfig:
    """Configuration for MkDocs."""

    site_name: str
    theme: Dict[str, str]
    repo_url: Optional[str] = None
    markdown_extensions: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: dict) -> Optional["MkDocsConfig"]:
        """Create MkDocsConfig from dictionary."""
        mkdocs_data = data.get("mkdocs_config")
        if not mkdocs_data:
            return None

        try:
            return cls(
                site_name=mkdocs_data.get("site_name", "Documentation"),
                theme=mkdocs_data.get("theme", {"name": "material"}),
                repo_url=mkdocs_data.get("repo_url"),
                markdown_extensions=mkdocs_data.get("markdown_extensions"),
            )
        except (ValueError, TypeError) as e:
            raise DocumentationError(f"Invalid MkDocs configuration: {e}") from e


@dataclass
class StructureConfig:
    """Complete documentation structure configuration."""

    docs_dir: str
    numbering: NumberingConfig
    structure: DocumentStructure
    use_markdown_headings: bool
    generate_mkdocs: bool
    mkdocs: Optional[MkDocsConfig]

    @classmethod
    def from_dict(cls, data: dict) -> "StructureConfig":
        """Create StructureConfig from dictionary."""
        try:
            docs_dir = data.get("docs_dir", data.get("base_dir"))
            if docs_dir is None:
                raise DocumentationError("Missing required configuration: docs_dir")

            if not isinstance(docs_dir, str):
                raise DocumentationError("docs_dir must be a string")

            if "/" in docs_dir or "\\" in docs_dir:
                raise DocumentationError(
                    "Documentation directory name cannot contain path separators"
                )

            return cls(
                docs_dir=docs_dir,
                numbering=NumberingConfig.from_dict(data),
                structure=DocumentStructure.from_dict(data),
                use_markdown_headings=data["use_markdown_headings"],
                generate_mkdocs=data.get("generate_mkdocs", False),
                mkdocs=MkDocsConfig.from_dict(data),
            )
        except KeyError as e:
            raise DocumentationError(f"Missing required configuration key: {e}") from e
        except (ValueError, TypeError) as e:
            raise DocumentationError(f"Invalid configuration: {e}") from e

    def validate(self) -> None:
        """Validate the complete configuration."""
        if not isinstance(self.docs_dir, str):
            raise DocumentationError("docs_dir must be a string")
        if not self.docs_dir:
            raise DocumentationError("docs_dir cannot be empty")
        if not isinstance(self.use_markdown_headings, bool):
            raise DocumentationError("use_markdown_headings must be a boolean")
        if not isinstance(self.generate_mkdocs, bool):
            raise DocumentationError("generate_mkdocs must be a boolean")

        # Validate sub-configurations
        self.numbering.validate()
        self.structure.validate()
