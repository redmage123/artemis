#!/usr/bin/env python3
"""
Artemis Checkpoint Manager - Backward Compatibility Wrapper

WHY: Maintains backward compatibility with existing codebase while delegating
     to the new modular persistence/checkpoint/ package implementation.

RESPONSIBILITY:
    - Re-export all public APIs from new package
    - Maintain identical interface for existing consumers
    - Provide deprecation path for future migration

PATTERNS:
    - Proxy Pattern: Delegates to new implementation
    - Facade Pattern: Maintains simple interface
    - Backward Compatibility: Preserves existing API

MIGRATION NOTE:
    This is a compatibility shim. New code should import directly from:
    from persistence.checkpoint import CheckpointManager

    Old imports still work:
    from checkpoint_manager import CheckpointManager

REFACTORING SUMMARY:
    Original: 637 lines monolithic module
    New: Modular package with 6 focused modules
    - models.py (250 lines) - Data structures
    - storage.py (244 lines) - Repository pattern storage
    - creator.py (244 lines) - Checkpoint creation
    - restorer.py (218 lines) - Restoration and caching
    - manager_core.py (363 lines) - Main orchestration
    - __init__.py (133 lines) - Package exports
    Wrapper: 74 lines
"""

# ============================================================================
# BACKWARD COMPATIBILITY EXPORTS
# ============================================================================

# Import everything from the new modular package
from persistence.checkpoint import (
    # Main interface
    CheckpointManager,
    create_checkpoint_manager,

    # Models and enums
    CheckpointStatus,
    StageCheckpoint,
    PipelineCheckpoint,

    # Storage interfaces
    CheckpointRepository,
    FilesystemCheckpointRepository,

    # Utilities
    CheckpointValidator,
    ProgressCalculator,
    LLMCacheManager,

    # Helper functions
    calculate_progress_percent,
    estimate_remaining_time,
)


# ============================================================================
# PUBLIC API (Maintained for backward compatibility)
# ============================================================================

__all__ = [
    # Main classes
    "CheckpointManager",
    "CheckpointStatus",
    "StageCheckpoint",
    "PipelineCheckpoint",

    # Factory function
    "create_checkpoint_manager",

    # Storage
    "CheckpointRepository",
    "FilesystemCheckpointRepository",
]


# ============================================================================
# MODULE METADATA
# ============================================================================

__version__ = "2.0.0"
__refactored__ = True
__module_location__ = "persistence.checkpoint"
