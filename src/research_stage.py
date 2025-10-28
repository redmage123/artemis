#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in stages/research/.

All functionality has been refactored into:
- stages/research/query_builder.py - Query formatting
- stages/research/example_searcher.py - Multi-source searching
- stages/research/example_storage.py - RAG storage operations
- stages/research/summary_formatter.py - Result formatting
- stages/research/stage.py - ResearchStage orchestrator
- stages/research/factory.py - Factory functions

To migrate your code:
    OLD: from research_stage import ResearchStage, create_research_stage
    NEW: from stages.research import ResearchStage, create_research_stage

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from stages.research import (
    ResearchStage,
    create_research_stage,
    ResearchStageFactory,
    format_research_query,
    ResearchQueryBuilder,
    ExampleSearcher,
    ExampleStorage,
    SummaryFormatter,
)

__all__ = [
    'ResearchStage',
    'create_research_stage',
    'ResearchStageFactory',
    'format_research_query',
    'ResearchQueryBuilder',
    'ExampleSearcher',
    'ExampleStorage',
    'SummaryFormatter',
]
