#!/usr/bin/env python3
"""
Package: stages.sprint_planning

WHY: Modular sprint planning components with backward compatibility
RESPONSIBILITY: Export all components for internal and external use
PATTERNS: Facade pattern for backward compatibility

ARCHITECTURE:
- sprint_planning_stage_core.py: Main orchestrator (Facade)
- feature_extractor.py: Extract features from various sources
- poker_integration.py: Planning Poker estimation integration
- feature_prioritizer.py: Weighted feature prioritization
- sprint_creator.py: Sprint allocation with velocity constraints
- kanban_updater.py: Kanban board persistence
- rag_storage.py: RAG storage for learning
- agent_notifier.py: Inter-agent communication
- input_sanitizer.py: Prompt injection prevention
"""

# Main stage class
from stages.sprint_planning.sprint_planning_stage_core import SprintPlanningStage

# Component classes (for advanced use cases)
from stages.sprint_planning.feature_extractor import FeatureExtractor
from stages.sprint_planning.poker_integration import PokerIntegration
from stages.sprint_planning.feature_prioritizer import FeaturePrioritizer
from stages.sprint_planning.sprint_creator import SprintCreator
from stages.sprint_planning.kanban_updater import KanbanUpdater
from stages.sprint_planning.rag_storage import SprintPlanRAGStorage
from stages.sprint_planning.agent_notifier import AgentNotifier
from stages.sprint_planning.input_sanitizer import InputSanitizer

__all__ = [
    # Main stage
    'SprintPlanningStage',
    # Components
    'FeatureExtractor',
    'PokerIntegration',
    'FeaturePrioritizer',
    'SprintCreator',
    'KanbanUpdater',
    'SprintPlanRAGStorage',
    'AgentNotifier',
    'InputSanitizer',
]
