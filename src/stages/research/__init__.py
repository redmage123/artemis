#!/usr/bin/env python3
"""
WHY: Provide public API for research stage package
RESPONSIBILITY: Export main classes and functions for external use
PATTERNS: Facade (simplified package interface)

Research stage package provides code example research functionality
before development begins.
"""

from stages.research.stage import ResearchStage
from stages.research.factory import create_research_stage, ResearchStageFactory
from stages.research.query_builder import format_research_query, ResearchQueryBuilder
from stages.research.example_searcher import ExampleSearcher
from stages.research.example_storage import ExampleStorage
from stages.research.summary_formatter import SummaryFormatter

__all__ = [
    # Main stage
    'ResearchStage',

    # Factory
    'create_research_stage',
    'ResearchStageFactory',

    # Components (for advanced usage)
    'format_research_query',
    'ResearchQueryBuilder',
    'ExampleSearcher',
    'ExampleStorage',
    'SummaryFormatter',
]
