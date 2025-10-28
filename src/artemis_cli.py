#!/usr/bin/env python3
"""
WHY: Maintain backward compatibility for artemis_cli.py
RESPONSIBILITY: Delegate to modular cli package while preserving API
PATTERNS:
- Facade pattern for backward compatibility
- Delegation to new implementation
- Minimal wrapper for seamless migration

Artemis CLI - Unified command-line interface for Artemis helper tools

This is a compatibility wrapper that delegates to the modular cli/ package.

Usage:
    artemis init-prompts    # Initialize all prompts with DEPTH framework
    artemis test-config     # Test Hydra configuration and storage
    artemis run [card-id]   # Run Artemis orchestrator on a task
    artemis cleanup         # Clean up temporary files and reset state
    artemis status          # Show Artemis system status
    artemis prompts         # Manage prompt templates

REFACTORED: This file has been refactored into a modular cli/ package:
    - cli/models.py: Data models and types
    - cli/parser.py: Argument parsing
    - cli/commands.py: Command implementations
    - cli/formatters.py: Output formatting
    - cli/cli_core.py: Main CLI orchestration
    - cli/__init__.py: Package exports
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import main


if __name__ == "__main__":
    sys.exit(main())
