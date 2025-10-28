# Checkpoint Manager Architecture

## Module Dependency Graph

```
                    checkpoint_manager.py (93 lines)
                    [Backward Compatibility Wrapper]
                              |
                              | re-exports
                              v
                    persistence/checkpoint/
                           __init__.py
                          [Package API]
                              |
            +--------+--------+--------+--------+
            |        |        |        |        |
            v        v        v        v        v
      models.py storage.py creator.py restorer.py manager_core.py
     (265 lines) (328 lines) (408 lines) (349 lines) (414 lines)
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    CheckpointManager                        │
│                   [manager_core.py]                         │
│                  - Main Facade -                            │
│                                                             │
│  Coordinates all checkpoint operations                      │
└────────────┬──────────────┬─────────────┬─────────────┬────┘
             │              │             │             │
             │              │             │             │
             v              v             v             v
    ┌────────────┐  ┌──────────────┐ ┌─────────┐ ┌──────────────┐
    │ Creator    │  │  Restorer    │ │ Storage │ │   Models     │
    │            │  │              │ │         │ │              │
    │ - Create   │  │ - Resume     │ │ - Save  │ │ - Checkpoint │
    │ - Update   │  │ - Validate   │ │ - Load  │ │ - Stage      │
    │ - Progress │  │ - LLM Cache  │ │ - Delete│ │ - Status     │
    └────────────┘  └──────────────┘ └─────────┘ └──────────────┘
```

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
│                                                             │
│  checkpoint_manager.py (Backward Compatibility Wrapper)     │
│  - Re-exports new API                                       │
│  - Maintains existing imports                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────────┐
│                      FACADE LAYER                           │
│                                                             │
│  __init__.py (Package Interface)                            │
│  - Public API definition                                    │
│  - Factory functions                                        │
│                                                             │
│  manager_core.py (Main Facade)                              │
│  - Orchestrates components                                  │
│  - Unified API surface                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                     │
│                                                             │
│  creator.py (Construction)      restorer.py (Recovery)      │
│  - CheckpointCreator            - CheckpointRestorer        │
│  - CheckpointUpdater            - LLMCacheManager          │
│  - ProgressCalculator           - StateRestorer            │
│  - LLMCacheKeyGenerator                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────────┐
│                   PERSISTENCE LAYER                         │
│                                                             │
│  storage.py (Repository Pattern)                            │
│  - CheckpointRepository (Interface)                         │
│  - FilesystemCheckpointRepository                           │
│  - CheckpointValidator                                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            v
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                             │
│                                                             │
│  models.py (Data Structures)                                │
│  - CheckpointStatus (Enum)                                  │
│  - StageCheckpoint (Dataclass)                              │
│  - PipelineCheckpoint (Dataclass)                           │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Checkpoint Creation Flow
```
Client
  │
  └─> CheckpointManager.create_checkpoint()
        │
        ├─> CheckpointCreator.create_new_checkpoint()
        │     │
        │     └─> PipelineCheckpoint (models.py)
        │
        └─> CheckpointRepository.save()
              │
              └─> FilesystemCheckpointRepository (storage.py)
                    │
                    └─> JSON file on disk
```

### Checkpoint Restoration Flow
```
Client
  │
  └─> CheckpointManager.resume()
        │
        ├─> CheckpointRestorer.can_resume()
        │     │
        │     └─> CheckpointValidator.can_resume_checkpoint()
        │
        ├─> CheckpointRepository.load()
        │     │
        │     └─> PipelineCheckpoint (from JSON)
        │
        └─> LLMCacheManager.restore_cache_from_checkpoint()
              │
              └─> In-memory cache populated
```

### Stage Save Flow
```
Client
  │
  └─> CheckpointManager.save_stage_checkpoint()
        │
        ├─> CheckpointCreator.create_stage_checkpoint()
        │     │
        │     └─> StageCheckpoint (models.py)
        │
        ├─> CheckpointUpdater.update_with_stage()
        │     │
        │     └─> PipelineCheckpoint updated
        │
        ├─> LLMCacheManager.store_response()
        │     │
        │     └─> Cache entry added
        │
        └─> CheckpointRepository.save()
              │
              └─> JSON file updated on disk
```

## Design Patterns Applied

### 1. Repository Pattern (storage.py)
```
┌──────────────────────────┐
│ CheckpointRepository     │  Abstract Interface
│ (Abstract Base Class)    │
└──────────┬───────────────┘
           │
           │ implements
           v
┌──────────────────────────┐
│ FilesystemRepository     │  Concrete Implementation
└──────────────────────────┘
           │
           │ future implementations
           v
┌──────────────────────────┐
│ DatabaseRepository       │  Future: PostgreSQL, SQLite
│ CloudRepository          │  Future: S3, Azure Blob
└──────────────────────────┘
```

### 2. Facade Pattern (manager_core.py)
```
┌──────────────────────────────────────────┐
│         CheckpointManager                │
│         (Simplified Interface)           │
│                                          │
│  create_checkpoint()                     │
│  save_stage_checkpoint()                 │
│  resume()                                │
│  get_progress()                          │
└────────┬─────────┬─────────┬─────────┬──┘
         │         │         │         │
         v         v         v         v
    Creator   Restorer  Storage   Cache
   (Complex Subsystems Hidden)
```

### 3. Builder Pattern (creator.py)
```
CheckpointCreator
    │
    ├─> create_new_checkpoint()
    │     └─> Basic checkpoint structure
    │
    └─> create_stage_checkpoint()
          └─> Stage data structure

CheckpointUpdater
    │
    └─> update_with_stage()
          └─> Incrementally builds checkpoint
```

### 4. Memento Pattern (restorer.py)
```
┌──────────────────────────┐
│   Checkpoint (Memento)   │  Saved state
│   - Stage history        │
│   - Execution context    │
│   - LLM cache            │
└──────────┬───────────────┘
           │
           │ restore
           v
┌──────────────────────────┐
│   Pipeline (Originator)  │  Restored state
└──────────────────────────┘
```

## Module Interaction Example

```python
# Client code
manager = CheckpointManager(card_id="CARD-123")

# manager_core.py orchestrates:
checkpoint = manager.create_checkpoint(total_stages=5)
    # ↓ calls creator.py
    CheckpointCreator.create_new_checkpoint()
    # ↓ creates models.py
    PipelineCheckpoint(...)
    # ↓ calls storage.py
    repository.save(checkpoint)
    # ↓ persists to disk
    FilesystemCheckpointRepository.save()

# Save stage completion
manager.save_stage_checkpoint(stage_name="research", status="completed")
    # ↓ calls creator.py
    CheckpointCreator.create_stage_checkpoint()
    # ↓ calls creator.py
    CheckpointUpdater.update_with_stage()
    # ↓ calls restorer.py
    LLMCacheManager.store_response()
    # ↓ calls storage.py
    repository.save(checkpoint)

# Resume from checkpoint
if manager.can_resume():
    # ↓ calls restorer.py
    checkpoint = manager.resume()
        # ↓ calls restorer.py
        CheckpointRestorer.resume()
        # ↓ calls storage.py
        repository.load(card_id)
        # ↓ calls restorer.py
        LLMCacheManager.restore_cache_from_checkpoint()
```

## File Size Comparison

```
Original Monolithic:
checkpoint_manager.py ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 637 lines

New Wrapper:
checkpoint_manager.py ▓▓ 93 lines (85.4% reduction)

New Package:
models.py             ▓▓▓▓▓▓▓▓ 265 lines
storage.py            ▓▓▓▓▓▓▓▓▓▓▓ 328 lines
creator.py            ▓▓▓▓▓▓▓▓▓▓▓▓▓ 408 lines
restorer.py           ▓▓▓▓▓▓▓▓▓▓▓ 349 lines
manager_core.py       ▓▓▓▓▓▓▓▓▓▓▓▓▓ 414 lines
__init__.py           ▓▓▓▓ 142 lines
                      ──────────────────────
Total Package:        1,906 lines (avg 318/module)
```

## Testing Strategy

```
Unit Tests:
├── test_models.py
│   ├── test_checkpoint_status_enum
│   ├── test_stage_checkpoint_serialization
│   └── test_pipeline_checkpoint_serialization
│
├── test_storage.py
│   ├── test_filesystem_repository_save
│   ├── test_filesystem_repository_load
│   ├── test_checkpoint_validator
│   └── test_repository_factory
│
├── test_creator.py
│   ├── test_checkpoint_creator
│   ├── test_checkpoint_updater
│   ├── test_progress_calculator
│   └── test_llm_cache_key_generator
│
├── test_restorer.py
│   ├── test_checkpoint_restorer
│   ├── test_llm_cache_manager
│   └── test_checkpoint_state_restorer
│
└── test_manager_core.py
    ├── test_checkpoint_lifecycle
    ├── test_stage_save
    ├── test_resume
    └── test_progress_tracking

Integration Tests:
└── test_integration.py
    ├── test_full_checkpoint_lifecycle
    ├── test_crash_recovery
    ├── test_llm_cache_effectiveness
    └── test_backward_compatibility
```

## Summary

The refactored architecture provides:
- **Clear separation of concerns** across 6 focused modules
- **Strong encapsulation** with well-defined interfaces
- **High cohesion** within modules
- **Low coupling** between modules
- **Extensibility** through Repository and Strategy patterns
- **Testability** through dependency injection
- **Maintainability** through clear documentation and type hints
- **Backward compatibility** through wrapper pattern

Total reduction: **85.4%** in main file size while adding comprehensive features.
