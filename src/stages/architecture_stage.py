#!/usr/bin/env python3
"""
Architecture Stage - Backward Compatibility Wrapper

WHY: Maintain backward compatibility after modularization
RESPONSIBILITY: Re-export ArchitectureStage from refactored package
PATTERNS: Facade Pattern, Backward Compatibility

This file ensures all existing imports continue to work:
    from architecture_stage import ArchitectureStage

The actual implementation is now in stages/architecture/ package:
    - architecture_stage_core.py: Main ArchitectureStage class (facade)
    - adr_file_manager.py: ADR file operations
    - adr_generator.py: ADR content generation (template/AI)
    - user_story_generator.py: User story generation from ADRs
    - kg_storage.py: Knowledge Graph storage
    - rag_storage.py: RAG database storage
    - __init__.py: Package initialization

MIGRATION PATH:
Old import: from architecture_stage import ArchitectureStage
New import: from stages.architecture import ArchitectureStage
Both work identically - this wrapper ensures zero breaking changes.
"""

# Re-export all public classes from the refactored package
from stages.architecture import (
    ArchitectureStage,
    ADRFileManager,
    ADRGenerator,
    UserStoryGenerator,
    KGArchitectureStorage,
    RAGArchitectureStorage,
)

__all__ = [
    'ArchitectureStage',
    'ADRFileManager',
    'ADRGenerator',
    'UserStoryGenerator',
    'KGArchitectureStorage',
    'RAGArchitectureStorage',
]
