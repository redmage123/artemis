"""
Architecture Stage Package

WHY: Modularized architecture stage components
RESPONSIBILITY: Export all architecture stage components
PATTERNS: Package initialization, Backward compatibility

This package contains:
- architecture_stage_core: Main ArchitectureStage class
- adr_file_manager: ADR file naming and numbering
- adr_generator: ADR content generation (template/AI)
- user_story_generator: User story generation from ADRs
- kg_storage: Knowledge Graph storage operations
- rag_storage: RAG database storage operations
"""

# Import all components for backward compatibility
from .architecture_stage_core import ArchitectureStage
from .adr_file_manager import ADRFileManager
from .adr_generator import ADRGenerator
from .user_story_generator import UserStoryGenerator
from .kg_storage import KGArchitectureStorage
from .rag_storage import RAGArchitectureStorage

__all__ = [
    'ArchitectureStage',
    'ADRFileManager',
    'ADRGenerator',
    'UserStoryGenerator',
    'KGArchitectureStorage',
    'RAGArchitectureStorage',
]
