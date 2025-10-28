#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in build_managers/terraform/.

All functionality has been refactored into:
- build_managers/terraform/manager.py - TerraformManager implementation
- build_managers/terraform/__init__.py - Public API

To migrate your code:
    OLD: from terraform_manager import TerraformManager
    NEW: from build_managers.terraform import TerraformManager

No breaking changes - all imports remain identical.
"""

from pathlib import Path
from build_managers.terraform import TerraformManager
from build_manager_factory import register_build_manager, BuildSystem

# Re-register with factory for backward compatibility
register_build_manager(BuildSystem.TERRAFORM)(TerraformManager)

__all__ = [
    'TerraformManager',
]


# CLI entry point - maintain backward compatibility
if __name__ == "__main__":
    import sys
    manager = TerraformManager(Path.cwd())
    sys.exit(0 if manager.detect() else 1)
