#!/usr/bin/env python3
"""
AI Query Package - KG → RAG → LLM Pipeline

WHY: Centralized AI query service for all agents to eliminate code duplication.

RESPONSIBILITY:
- Export all public classes and functions
- Provide clean package interface
- Enable easy imports throughout the codebase

PATTERNS:
- Package initialization with explicit exports
- __all__ for controlled public API
"""

from ai_query.query_type import QueryType
from ai_query.kg_context import KGContext
from ai_query.rag_context import RAGContext
from ai_query.llm_response import LLMResponse
from ai_query.ai_query_result import AIQueryResult
from ai_query.kg_query_strategy import KGQueryStrategy
from ai_query.requirements_kg_strategy import RequirementsKGStrategy
from ai_query.architecture_kg_strategy import ArchitectureKGStrategy
from ai_query.code_review_kg_strategy import CodeReviewKGStrategy
from ai_query.code_generation_kg_strategy import CodeGenerationKGStrategy
from ai_query.project_analysis_kg_strategy import ProjectAnalysisKGStrategy
from ai_query.error_recovery_kg_strategy import ErrorRecoveryKGStrategy
from ai_query.sprint_planning_kg_strategy import SprintPlanningKGStrategy
from ai_query.retrospective_kg_strategy import RetrospectiveKGStrategy
from ai_query.token_savings_metrics import TokenSavingsMetrics
from ai_query.token_savings_tracker import TokenSavingsTracker
from ai_query.ai_query_service_impl import AIQueryService
from ai_query.factory import create_ai_query_service

__all__ = [
    # Enums
    'QueryType',

    # Data Classes
    'KGContext',
    'RAGContext',
    'LLMResponse',
    'AIQueryResult',
    'TokenSavingsMetrics',

    # Strategies
    'KGQueryStrategy',
    'RequirementsKGStrategy',
    'ArchitectureKGStrategy',
    'CodeReviewKGStrategy',
    'CodeGenerationKGStrategy',
    'ProjectAnalysisKGStrategy',
    'ErrorRecoveryKGStrategy',
    'SprintPlanningKGStrategy',
    'RetrospectiveKGStrategy',

    # Service & Tracker
    'TokenSavingsTracker',
    'AIQueryService',

    # Factory
    'create_ai_query_service',
]
