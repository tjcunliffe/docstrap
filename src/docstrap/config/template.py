"""Default configuration template for docstrap."""

STARTER_CONFIG = """\
# Documentation directory
docs_dir: "docs"

# File naming options
use_numbered_prefix: true
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
"""
