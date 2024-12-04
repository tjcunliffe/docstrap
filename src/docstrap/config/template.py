"""Default configuration template for docstrap."""

STARTER_CONFIG = """\
# Documentation directory
docs_dir: "docs"

# File naming options
use_numbered_prefix: false
use_markdown_headings: true

# Numbering settings
initial_prefix: 10
dir_start_prefix: 20
prefix_step: 10
padding_width: 3

# Structure
directories:
  guides:
    - getting-started.md
  reference:
    - api.md

top_level_files:
  - index.md

# MkDocs configuration
generate_mkdocs: false  # Set to true to generate mkdocs.yaml
mkdocs_config:
  site_name: "My Documentation"
  theme:
    name: "material"  # Using mkdocs-material theme
  repo_url: ""  # Optional: Add your repository URL
  markdown_extensions:
    - toc:
        permalink: true
    - admonition
    - pymdownx.highlight
    - pymdownx.superfences
"""
