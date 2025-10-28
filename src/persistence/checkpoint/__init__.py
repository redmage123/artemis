#!/usr/bin/env python3
"""
Checkpoint Management Package

WHY: Provides a modular, extensible checkpoint system for pipeline crash
     recovery and state persistence. Enables pipeline resumption after
     interruptions while caching expensive LLM operations.

RESPONSIBILITY:
    - Export public checkpoint API
    - Maintain backward compatibility
    - Provide convenient factory functions
    - Define package interface

PATTERNS:
    - Facade Pattern: Simplified public API
    - Factory Pattern: Convenient object creation
    - Module Pattern: Clear separation of concerns

ARCHITECTURE:
    models.py      - Data structures and enumerations
    storage.py     - Repository pattern for persistence
    creator.py     - Checkpoint creation and updates
    restorer.py    - Checkpoint restoration and caching
    manager_core.py - Main orchestration facade

USAGE:
    from persistence.checkpoint import CheckpointManager, CheckpointStatus

    # Create manager
    manager = CheckpointManager(card_id="CARD-123")

    # Create checkpoint
    checkpoint = manager.create_checkpoint(total_stages=5)

    # Save stage completion
    manager.save_stage_checkpoint(
        stage_name="research",
        status="completed",
        result={"findings": "..."}
    )

    # Resume from checkpoint
    if manager.can_resume():
        checkpoint = manager.resume()
"""

# Core models and enumerations
from .models import (
    CheckpointStatus,
    StageCheckpoint,
    PipelineCheckpoint,
    calculate_progress_percent,
    estimate_remaining_time
)

# Storage layer
from .storage import (
    CheckpointRepository,
    FilesystemCheckpointRepository,
    CheckpointValidator,
    create_checkpoint_repository
)

# Creator components
from .creator import (
    CheckpointCreator,
    CheckpointUpdater,
    ProgressCalculator,
    LLMCacheKeyGenerator
)

# Restorer components
from .restorer import (
    CheckpointRestorer,
    LLMCacheManager,
    CheckpointStateRestorer,
    create_state_restorer
)

# Main manager facade
from .manager_core import (
    CheckpointManager,
    create_checkpoint_manager
)


# ============================================================================
# PUBLIC API
# ============================================================================

__all__ = [
    # Main interface
    "CheckpointManager",
    "create_checkpoint_manager",

    # Models
    "CheckpointStatus",
    "StageCheckpoint",
    "PipelineCheckpoint",

    # Storage
    "CheckpointRepository",
    "FilesystemCheckpointRepository",
    "create_checkpoint_repository",

    # Utilities
    "CheckpointValidator",
    "ProgressCalculator",
    "LLMCacheManager",

    # Helper functions
    "calculate_progress_percent",
    "estimate_remaining_time",
]


# ============================================================================
# PACKAGE METADATA
# ============================================================================

__version__ = "2.0.0"
__author__ = "Artemis Team"
__description__ = "Modular checkpoint management for pipeline crash recovery"


# ============================================================================
# BACKWARD COMPATIBILITY HELPERS
# ============================================================================

def get_checkpoint_manager(*args, **kwargs) -> CheckpointManager:
    """
    Legacy factory function for backward compatibility

    Args:
        *args: Positional arguments for CheckpointManager
        **kwargs: Keyword arguments for CheckpointManager

    Returns:
        CheckpointManager instance
    """
    return CheckpointManager(*args, **kwargs)
