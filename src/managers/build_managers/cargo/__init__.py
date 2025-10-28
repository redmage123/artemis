"""
Cargo subpackage - Modularized Cargo build manager components.

Part of: managers/build_managers

WHY: Organize Cargo build system management into cohesive, maintainable modules.
RESPONSIBILITY: Export all Cargo-related components with clear public API.
PATTERNS: Package Organization, Explicit Exports, Facade Pattern.

This package contains the decomposed CargoManager components:
- models: Data models (BuildProfile, CargoFeature, CargoProjectInfo)
- toml_parser: Cargo.toml parsing logic
- dependency_manager: Crate dependency management
- build_operations: Build/test/check/clippy/fmt/clean operations
- version_detector: Rust/Cargo version detection
- cli_handlers: CLI command handlers
- cargo_manager: Main orchestrator class (composition-based)

EXTRACTED FROM: cargo_manager.py (601 lines -> modular structure)
"""

# Export main CargoManager class
from managers.build_managers.cargo.cargo_manager import CargoManager

# Export key models
from managers.build_managers.cargo.models import (
    BuildProfile,
    CargoFeature,
    CargoProjectInfo,
)

# Export parser functions
from managers.build_managers.cargo.toml_parser import (
    parse_cargo_toml,
    extract_workspace_members,
    is_workspace_project,
)

# Export specialized components (for advanced usage)
from managers.build_managers.cargo.build_operations import BuildOperations
from managers.build_managers.cargo.dependency_manager import DependencyManager
from managers.build_managers.cargo.version_detector import VersionDetector

# Export CLI handler
from managers.build_managers.cargo.cli_handlers import run_cli

__all__ = [
    # Main class
    "CargoManager",

    # Models
    "BuildProfile",
    "CargoFeature",
    "CargoProjectInfo",

    # Parser functions
    "parse_cargo_toml",
    "extract_workspace_members",
    "is_workspace_project",

    # Components (for advanced usage)
    "BuildOperations",
    "DependencyManager",
    "VersionDetector",

    # CLI
    "run_cli",
]
