"""
Retrospective Stage Package

WHY: Modularized retrospective agent components
RESPONSIBILITY: Export all retrospective stage components
PATTERNS: Package initialization, Backward compatibility

This package contains:
- retrospective_agent_core: Main RetrospectiveAgent class
- retrospective_models: Data models (RetrospectiveItem, SprintMetrics, etc.)
- metrics_extractor: Sprint metrics extraction
- success_analyzer: What went well analysis
- failure_analyzer: What didn't go well analysis
- action_item_generator: Action item generation
- learning_extractor: Key learnings extraction
- health_assessor: Sprint health assessment
- recommendation_generator: Recommendation generation
- retrospective_storage: RAG storage and communication
"""

# Import all components for backward compatibility
from .retrospective_agent_core import RetrospectiveAgent
from .retrospective_models import (
    RetrospectiveItem,
    SprintMetrics,
    RetrospectiveReport,
    RetrospectiveContext
)
from .metrics_extractor import MetricsExtractor
from .success_analyzer import SuccessAnalyzer
from .failure_analyzer import FailureAnalyzer
from .action_item_generator import ActionItemGenerator
from .learning_extractor import LearningExtractor
from .health_assessor import HealthAssessor
from .recommendation_generator import RecommendationGenerator
from .retrospective_storage import RetrospectiveStorage

__all__ = [
    # Main agent
    'RetrospectiveAgent',

    # Data models
    'RetrospectiveItem',
    'SprintMetrics',
    'RetrospectiveReport',
    'RetrospectiveContext',

    # Components
    'MetricsExtractor',
    'SuccessAnalyzer',
    'FailureAnalyzer',
    'ActionItemGenerator',
    'LearningExtractor',
    'HealthAssessor',
    'RecommendationGenerator',
    'RetrospectiveStorage',
]
