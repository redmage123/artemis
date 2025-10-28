#!/usr/bin/env python3
"""
Cargo Build Manager (Rust) - Backward Compatibility Wrapper

REFACTORED: This module has been refactored into managers/build_managers/cargo/
This file maintains backward compatibility by re-exporting all components.

NEW LOCATION: managers/build_managers/cargo/
- cargo_manager.py: Main orchestrator
- models.py: Data models and enums
- toml_parser.py: Cargo.toml parsing
- dependency_manager.py: Crate dependency management
- build_operations.py: Build/test/check/clippy/fmt/clean operations
- version_detector.py: Rust/Cargo version detection
- cli_handlers.py: CLI command handlers

For new code, import directly from managers.build_managers.cargo:
    from managers.build_managers.cargo import CargoManager, BuildProfile, CargoProjectInfo

Design Patterns:
- Template Method: Inherits from BuildManagerBase
- Exception Wrapper: All errors properly wrapped
- Strategy Pattern: Different build modes (debug, release)
- Facade Pattern: Single entry point for Cargo operations
"""

# Re-export all components for backward compatibility
from managers.build_managers.cargo import (
    CargoManager,
    BuildProfile,
    CargoFeature,
    CargoProjectInfo,
    BuildOperations,
    DependencyManager,
    VersionDetector,
    parse_cargo_toml,
    extract_workspace_members,
    is_workspace_project,
    run_cli,
)

# Preserve CLI entry point
_run_cli = run_cli

__all__ = [
    "CargoManager",
    "BuildProfile",
    "CargoFeature",
    "CargoProjectInfo",
    "BuildOperations",
    "DependencyManager",
    "VersionDetector",
    "parse_cargo_toml",
    "extract_workspace_members",
    "is_workspace_project",
]


# CLI interface
if __name__ == "__main__":
    _run_cli()
