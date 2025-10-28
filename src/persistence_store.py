#!/usr/bin/env python3
"""
Persistence Store - Backward Compatibility Wrapper

WHY: Provides backward compatibility with original persistence_store.py.
     Allows existing code to work without modification while using modular implementation.

RESPONSIBILITY: Re-exports all components from modularized persistence package.
                Maintains original API surface for seamless migration.

PATTERNS:
- Facade Pattern: Simplified interface to modular implementation
- Proxy Pattern: Delegates to modular components
- Open/Closed Principle: Original API preserved, implementation replaced

MIGRATION PATH:
Old: from persistence_store import PipelineState, SQLitePersistenceStore
New: from persistence import PipelineState, SQLitePersistenceStore
Both work identically - this wrapper ensures compatibility.

Original file: 766 lines (monolithic)
Refactored to: 9 focused modules in persistence/ package
This wrapper: Re-exports for compatibility
"""

# Re-export all public components from modular package
from persistence import (
    # Core models
    PipelineState,
    StageCheckpoint,

    # Interface
    PersistenceStoreInterface,

    # Storage backends
    SQLitePersistenceStore,
    JSONFilePersistenceStore,

    # Factory
    PersistenceStoreFactory,

    # High-level interfaces
    PersistenceQueryInterface,
    CheckpointManager,
    StateRestorationManager,

    # Serialization utilities
    serialize_pipeline_state,
    deserialize_pipeline_state,
    serialize_stage_checkpoint,
    deserialize_stage_checkpoint,
)


# Maintain backward compatibility for common usage patterns
__all__ = [
    'PipelineState',
    'StageCheckpoint',
    'PersistenceStoreInterface',
    'SQLitePersistenceStore',
    'JSONFilePersistenceStore',
    'PersistenceStoreFactory',
    'PersistenceQueryInterface',
    'CheckpointManager',
    'StateRestorationManager',
    'serialize_pipeline_state',
    'deserialize_pipeline_state',
    'serialize_stage_checkpoint',
    'deserialize_stage_checkpoint',
]


# Example usage remains identical to original
if __name__ == "__main__":
    """Example usage - identical to original implementation"""
    from datetime import datetime

    print("Persistence Store - Example Usage (Backward Compatible)")
    print("=" * 70)

    # Create store (same API as before)
    store = PersistenceStoreFactory.create("sqlite", db_path="/tmp/test_persistence.db")

    # Save pipeline state (same API as before)
    state = PipelineState(
        card_id="test-card-001",
        status="running",
        current_stage="development",
        stages_completed=["project_analysis", "architecture"],
        stage_results={"architecture": {"adr": "ADR-001.md"}},
        developer_results=[],
        metrics={"stages_completed": 2},
        created_at=datetime.utcnow().isoformat() + 'Z',
        updated_at=datetime.utcnow().isoformat() + 'Z'
    )

    store.save_pipeline_state(state)
    print(f"Saved pipeline state: {state.card_id}")

    # Save stage checkpoint (same API as before)
    checkpoint = StageCheckpoint(
        card_id="test-card-001",
        stage_name="architecture",
        status="completed",
        started_at=datetime.utcnow().isoformat() + 'Z',
        completed_at=datetime.utcnow().isoformat() + 'Z',
        result={"adr_file": "ADR-001.md"}
    )

    store.save_stage_checkpoint(checkpoint)
    print(f"Saved stage checkpoint: {checkpoint.stage_name}")

    # Load pipeline state (same API as before)
    loaded_state = store.load_pipeline_state("test-card-001")
    print(f"Loaded pipeline state: status={loaded_state.status}")

    # Get resumable pipelines (same API as before)
    resumable = store.get_resumable_pipelines()
    print(f"Resumable pipelines: {resumable}")

    # Get statistics (same API as before)
    stats = store.get_statistics()
    print(f"Database statistics:")
    print(f"   Total pipelines: {stats['total_pipelines']}")
    print(f"   By status: {stats['by_status']}")
    print(f"   Total checkpoints: {stats['total_checkpoints']}")

    print("\n" + "=" * 70)
    print("Persistence store working correctly (modular implementation)!")
