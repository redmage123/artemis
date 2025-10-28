#!/usr/bin/env python3
"""
Module: sprint_planning_stage_refactored.py

BACKWARD COMPATIBILITY WRAPPER

WHY: Maintain import compatibility while using modular architecture
RESPONSIBILITY: Re-export SprintPlanningStage from new location
PATTERNS: Facade pattern, Deprecation pattern

MIGRATION PATH:
Old: from sprint_planning_stage import SprintPlanningStage
New: from stages.sprint_planning import SprintPlanningStage

This wrapper allows existing code to continue working while transitioning
to the modular architecture.

MODULARIZATION:
Original file: 751 lines
Refactored into 10 modules:
- sprint_planning_stage_core.py: Main orchestrator (~330 lines)
- feature_extractor.py: Feature extraction (~160 lines)
- poker_integration.py: Planning Poker integration (~85 lines)
- feature_prioritizer.py: Prioritization logic (~130 lines)
- sprint_creator.py: Sprint creation (~65 lines)
- kanban_updater.py: Kanban updates (~100 lines)
- rag_storage.py: RAG storage (~110 lines)
- agent_notifier.py: Agent notifications (~105 lines)
- input_sanitizer.py: Input sanitization (~70 lines)
- __init__.py: Package exports (~45 lines)

Total: ~1200 lines (with documentation)
Net increase: ~450 lines (60% more due to comprehensive documentation)
Complexity reduction: 751 lines → 330 lines in main class (56% reduction)
"""

# Re-export main class for backward compatibility
from stages.sprint_planning import SprintPlanningStage

# Re-export components for advanced users
from stages.sprint_planning import (
    FeatureExtractor,
    PokerIntegration,
    FeaturePrioritizer,
    SprintCreator,
    KanbanUpdater,
    SprintPlanRAGStorage,
    AgentNotifier,
    InputSanitizer,
)

__all__ = [
    'SprintPlanningStage',
    'FeatureExtractor',
    'PokerIntegration',
    'FeaturePrioritizer',
    'SprintCreator',
    'KanbanUpdater',
    'SprintPlanRAGStorage',
    'AgentNotifier',
    'InputSanitizer',
]
