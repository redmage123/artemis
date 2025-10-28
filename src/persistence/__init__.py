#!/usr/bin/env python3
"""
Persistence Package - Modular Pipeline State Storage

WHY: Provides modular, well-structured persistence layer for pipeline state.
     Separates concerns into focused modules with clear responsibilities.

RESPONSIBILITY: Package initialization and public API export.
                Provides backward compatibility with original interface.

PATTERNS:
- Facade Pattern: Clean public API hiding internal structure
- Single Responsibility: Each module has one clear purpose
- Open/Closed: Easy to extend with new storage backends

Package Structure:
- models: Data models (PipelineState, StageCheckpoint)
- interface: Abstract persistence interface
- serialization: JSON serialization utilities
- sqlite_store: SQLite backend implementation
- json_store: JSON file backend implementation
- factory: Store creation factory
- query_interface: High-level query operations
- checkpoint_manager: Checkpoint creation and validation
- state_restoration: Pipeline recovery operations

Original file: 766 lines
Modularized: 9 focused modules
"""

# Core models
from .models import (
    PipelineState,
    StageCheckpoint
)

# Interface
from .interface import PersistenceStoreInterface

# Storage backends
from .sqlite_store import SQLitePersistenceStore
from .json_store import JSONFilePersistenceStore

# Factory
from .factory import PersistenceStoreFactory

# High-level interfaces
from .query_interface import PersistenceQueryInterface
from .checkpoint_manager import CheckpointManager
from .state_restoration import StateRestorationManager

# Serialization utilities (internal use)
from .serialization import (
    serialize_pipeline_state,
    deserialize_pipeline_state,
    serialize_stage_checkpoint,
    deserialize_stage_checkpoint
)


__all__ = [
    # Models
    'PipelineState',
    'StageCheckpoint',

    # Interface
    'PersistenceStoreInterface',

    # Storage backends
    'SQLitePersistenceStore',
    'JSONFilePersistenceStore',

    # Factory
    'PersistenceStoreFactory',

    # High-level interfaces
    'PersistenceQueryInterface',
    'CheckpointManager',
    'StateRestorationManager',

    # Serialization (for advanced users)
    'serialize_pipeline_state',
    'deserialize_pipeline_state',
    'serialize_stage_checkpoint',
    'deserialize_stage_checkpoint',
]


# Package metadata
__version__ = '2.0.0'
__author__ = 'Artemis Team'
__description__ = 'Modular persistence layer for Artemis pipeline state'
