#!/usr/bin/env python3
"""
Path Configuration Models

WHY: Encapsulate path configuration data structures to separate data from logic.
RESPONSIBILITY: Define immutable data structures for path configuration.
PATTERNS: Value Object pattern for immutable configuration data.

This module defines the core data structures used by the path configuration service.
All path objects are immutable to prevent accidental mutations and ensure thread safety.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass(frozen=True)
class CoreDirectories:
    """
    Core directory paths for Artemis pipeline.

    WHY: Groups related core directories into immutable value object.
    RESPONSIBILITY: Store core directory paths (temp, checkpoint, state, status).
    PATTERNS: Value Object - immutable data structure.

    Attributes:
        temp_dir: Temporary files directory
        checkpoint_dir: Pipeline checkpoints directory
        state_dir: Pipeline state storage directory
        status_dir: Workflow status tracking directory
    """
    temp_dir: Path
    checkpoint_dir: Path
    state_dir: Path
    status_dir: Path


@dataclass(frozen=True)
class ArtifactDirectories:
    """
    Artifact directory paths for Artemis outputs.

    WHY: Groups related artifact directories into immutable value object.
    RESPONSIBILITY: Store artifact output directory paths.
    PATTERNS: Value Object - immutable data structure.

    Attributes:
        adr_dir: Architecture Decision Records directory
        developer_output_dir: Base directory for developer outputs
    """
    adr_dir: Path
    developer_output_dir: Path


@dataclass(frozen=True)
class PathConfiguration:
    """
    Complete path configuration for Artemis pipeline.

    WHY: Aggregates all path configuration into single immutable object.
    RESPONSIBILITY: Store complete path configuration state.
    PATTERNS:
        - Value Object: Immutable configuration data
        - Composite: Combines CoreDirectories and ArtifactDirectories

    Attributes:
        core: Core directory paths
        artifacts: Artifact directory paths
        script_dir: Script directory used for relative path resolution
    """
    core: CoreDirectories
    artifacts: ArtifactDirectories
    script_dir: Path

    def to_dict(self) -> Dict[str, Path]:
        """
        Convert configuration to dictionary.

        WHY: Enables serialization and easy access to all paths.
        PERFORMANCE: O(1) - simple dictionary construction.

        Returns:
            Dictionary mapping path names to Path objects
        """
        return {
            'temp_dir': self.core.temp_dir,
            'checkpoint_dir': self.core.checkpoint_dir,
            'state_dir': self.core.state_dir,
            'status_dir': self.core.status_dir,
            'adr_dir': self.artifacts.adr_dir,
            'developer_output_dir': self.artifacts.developer_output_dir,
            'script_dir': self.script_dir
        }


@dataclass(frozen=True)
class DeveloperPaths:
    """
    Developer-specific directory paths.

    WHY: Encapsulate developer-specific path computations.
    RESPONSIBILITY: Store computed paths for specific developer.
    PATTERNS: Value Object - immutable derived data.

    Attributes:
        developer_name: Name of the developer
        base_dir: Developer's base output directory
        tests_dir: Developer's tests directory
        impl_dir: Developer's implementation directory
    """
    developer_name: str
    base_dir: Path
    tests_dir: Path
    impl_dir: Path
