# DocStrap

A tool for creating structured documentation hierarchies with optional MkDocs integration.

## Features

- Create consistent documentation structures
- Optional numbered prefixes for ordering (010_, 020_, etc.)
- Automatic markdown headings
- MkDocs integration with navigation structure
- Interactive, silent, or dry-run modes

## Installation

```bash
pipx install docstrap  # Recommended
# or: pip install docstrap
```

## Quick Start

1. Generate config:
```bash
docstrap init
```

2. Create structure:
```bash
docstrap create -c docstrap.yaml
```

Additional options:
```bash
docstrap create -c docstrap.yaml [options]
  -d DIR        # Target directory
  --dry-run     # Preview changes
  -y            # Skip prompts
  --mkdocs      # Generate mkdocs.yaml
```

## Configuration

Example `docstrap.yaml`:
```yaml
# Base settings
docs_dir: "docs"
use_numbered_prefix: false  # Optional file/dir prefixes (010_, 020_, etc.)
use_markdown_headings: true

# Documentation structure
directories:
  guides:
    - getting-started.md
    - configuration.md
  reference:
    - api.md

top_level_files:
  - index.md

# MkDocs integration (optional)
generate_mkdocs: true
mkdocs_config:
  site_name: "My Documentation"
  theme:
    name: "material"
  markdown_extensions:
    - toc
    - admonition
    - pymdownx.highlight
```

## Python API

```python
from docstrap import DocumentationManager, StructureConfig, SilentFileHandler

config = StructureConfig.from_yaml("docstrap.yaml")
# or: config = StructureConfig(docs_dir="docs", ...)

manager = DocumentationManager(config, SilentFileHandler())
manager.create_structure()
```

## Development

```bash
git clone https://github.com/yourusername/docstrap.git
cd docstrap
poetry install
poetry run pre-commit install
poetry run pytest
```

## License

MIT - see [LICENSE.md](LICENSE.md)
