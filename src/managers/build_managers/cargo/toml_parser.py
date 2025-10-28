"""
Module: managers/build_managers/cargo/toml_parser.py

WHY: Parse and extract information from Cargo.toml files.
RESPONSIBILITY: Handle all Cargo.toml parsing and project information extraction.
PATTERNS: Parser Pattern, Guard Clauses, Exception Wrapping.

This module contains:
- Cargo.toml parsing logic
- Workspace detection
- Project metadata extraction

EXTRACTED FROM: cargo_manager.py (lines 150-186)
"""

from pathlib import Path
from typing import Any, Dict

import toml

from artemis_exceptions import wrap_exception
from build_system_exceptions import ProjectConfigurationError
from managers.build_managers.cargo.models import CargoProjectInfo


@wrap_exception(ProjectConfigurationError, "Failed to parse Cargo.toml")
def parse_cargo_toml(cargo_toml_path: Path) -> Dict[str, Any]:
    """
    Parse Cargo.toml and extract project information.

    WHY: Centralize Cargo.toml parsing logic.
    RESPONSIBILITY: Parse TOML and create CargoProjectInfo structure.

    Args:
        cargo_toml_path: Path to Cargo.toml file

    Returns:
        Dict with project information

    Raises:
        ProjectConfigurationError: If Cargo.toml malformed

    Example:
        info = parse_cargo_toml(Path("./Cargo.toml"))
    """
    if not cargo_toml_path.exists():
        raise ProjectConfigurationError(
            "Cargo.toml not found",
            {"path": str(cargo_toml_path)}
        )

    with open(cargo_toml_path, 'r') as f:
        data = toml.load(f)

    # Check if workspace
    is_workspace = "workspace" in data
    workspace_members = data.get("workspace", {}).get("members", [])

    # Package info (might be in workspace root or package)
    package = data.get("package", {})

    info = CargoProjectInfo(
        name=package.get("name", ""),
        version=package.get("version", "0.1.0"),
        edition=package.get("edition", "2021"),
        authors=package.get("authors", []),
        description=package.get("description"),
        license=package.get("license"),
        repository=package.get("repository"),
        dependencies=data.get("dependencies", {}),
        dev_dependencies=data.get("dev-dependencies", {}),
        features=data.get("features", {}),
        workspace_members=workspace_members,
        is_workspace=is_workspace
    )

    return info.to_dict()


def extract_workspace_members(cargo_toml_path: Path) -> list:
    """
    Extract workspace members from Cargo.toml.

    WHY: Support workspace-based Rust projects.
    RESPONSIBILITY: Extract workspace member list.

    Args:
        cargo_toml_path: Path to workspace Cargo.toml

    Returns:
        List of workspace member paths

    Example:
        members = extract_workspace_members(Path("./Cargo.toml"))
    """
    if not cargo_toml_path.exists():
        return []

    with open(cargo_toml_path, 'r') as f:
        data = toml.load(f)

    return data.get("workspace", {}).get("members", [])


def is_workspace_project(cargo_toml_path: Path) -> bool:
    """
    Check if Cargo.toml defines a workspace.

    Args:
        cargo_toml_path: Path to Cargo.toml

    Returns:
        True if workspace project

    Example:
        if is_workspace_project(Path("./Cargo.toml")):
            print("This is a workspace")
    """
    if not cargo_toml_path.exists():
        return False

    with open(cargo_toml_path, 'r') as f:
        data = toml.load(f)

    return "workspace" in data


__all__ = [
    "parse_cargo_toml",
    "extract_workspace_members",
    "is_workspace_project",
]
