# DocStrap

A tool for creating structured documentation hierarchies.

## Installation

```bash
# Using pipx (recommended for CLI usage)
pipx install docstrap

# Using pip
pip install docstrap

# Using poetry
poetry add docstrap
```

## Usage

### CLI

```bash
# Create structure using config
docstrap -c config.yaml

# Create in specific directory
docstrap -c config.yaml -d /path/to/project

# Preview changes without making them
docstrap -c config.yaml --dry-run

# Skip confirmation prompts
docstrap -c config.yaml -y

# Enable verbose output
docstrap -c config.yaml -v
```

### Library

```python
from pathlib import Path
from docstrap import DocumentationManager, StructureConfig, SilentFileHandler

# Load config from YAML
config = StructureConfig.from_yaml("config.yaml")

# Or create programmatically
config = StructureConfig(
    docs_dir="docs",  # Use "." for project root
    use_numbered_prefix=True,
    use_markdown_headings=True,
    initial_prefix=10,
    dir_start_prefix=20,
    prefix_step=10,
    padding_width=3,
    directories={
        "guides": ["getting-started.md"],
        "reference": ["api.md"]
    },
    top_level_files=["index.md"]
)

# Choose handler:
# - SilentFileHandler: No prompts
# - InteractiveFileHandler: Prompt before changes
# - DryRunFileHandler: Preview only
handler = SilentFileHandler()

# Create structure
manager = DocumentationManager(config, handler)
manager.create_structure(Path("/path/to/project"))  # Optional path
```

### Configuration

```yaml
# Documentation directory (use "." for project root)
docs_dir: "docs"

# Enable/disable numbered prefixes (010_, 020_, etc.)
use_numbered_prefix: true

# Enable/disable markdown h1 headings in .md files
use_markdown_headings: true

# Numbering configuration
initial_prefix: 10  # Start with 010
dir_start_prefix: 20  # Start with 020
prefix_step: 10  # Increment by 10
padding_width: 3  # For 010, 020, etc.

# Directory structure
directories:
  - guides:
      - getting-started.md
      - configuration.md
  - reference:
      - api.md
  - examples:
      - basic.md
      - advanced.md

# Top-level files
top_level_files:
  - index.md
```

### Output Example

With `use_numbered_prefix: true`:
```
docs/
├── README.md
├── 010_index.md
├── 020_guides/
│   ├── 010_getting-started.md
│   └── 020_configuration.md
├── 040_reference/
│   └── 010_api.md
└── 060_examples/
    ├── 010_basic.md
    └── 020_advanced.md
```

With `use_numbered_prefix: false`:
```
docs/
├── README.md
├── index.md
├── guides/
│   ├── getting-started.md
│   └── configuration.md
├── reference/
│   └── api.md
└── examples/
    ├── basic.md
    └── advanced.md
```

## Development

```bash
# Setup
git clone https://github.com/yourusername/docstrap.git
cd docstrap
poetry install

# Setup pre-commit hooks
poetry run pre-commit install

# Test
poetry run pytest

# Lint (also run automatically on commit)
poetry run black .
poetry run isort .
poetry run mypy src/docstrap
poetry run pylint src/docstrap
```

## License

MIT - see [LICENSE.md](LICENSE.md)
