"""
Command-line interface for docstrap.

This module provides the command-line interface for creating and managing
documentation directory structures.
"""

import argparse
import logging
import sys
from pathlib import Path

from .config import load_config
from .config.models import DocumentationError
from .core.manager import DocumentationManager
from .fs.handler import FileHandler, InteractiveFileHandler, SilentFileHandler, DryRunFileHandler

def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging based on verbosity level.
    
    Args:
        verbose: Whether to enable debug logging.
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(message)s'
    )

def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.
    
    Returns:
        ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        description="docstrap - Bootstrap and manage documentation directory structures"
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        required=True,
        help='Path to configuration file (e.g., config/docstrap.yaml)'
    )
    
    parser.add_argument(
        '-d', '--directory',
        type=str,
        help='Project root directory (default: current directory)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    
    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Answer yes to all prompts'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser

def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        int: Exit code (0 for success, non-zero for error).
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Configure logging
    setup_logging(args.verbose)
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Determine project root
        if args.directory:
            project_root = Path(args.directory)
        else:
            project_root = Path.cwd()
        
        # Select appropriate file handler
        if args.dry_run:
            file_handler = DryRunFileHandler()
        elif args.yes:
            file_handler = SilentFileHandler()
        else:
            file_handler = InteractiveFileHandler()
        
        # Create and run the manager
        manager = DocumentationManager(config, file_handler)
        manager.create_structure(project_root)
        
        return 0
        
    except DocumentationError as e:
        logging.error(f"Configuration error: {e}")
        return 1
    except KeyboardInterrupt:
        logging.error("\nOperation cancelled by user")
        return 130
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
