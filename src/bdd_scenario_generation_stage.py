#!/usr/bin/env python3
"""
Module: bdd_scenario_generation_stage.py

DEPRECATED: This module is now a backward compatibility wrapper.
            Use stages.bdd_scenario package directly for new code.

Purpose: Transform structured requirements into executable Gherkin BDD scenarios
         using LLM-powered generation.

Why: Bridges the gap between business requirements and executable specifications.
     BDD scenarios serve as both documentation and automated test specifications,
     ensuring implementation matches business intent.

Migration: This wrapper delegates to stages.bdd_scenario.BDDScenarioStageCore
           Existing code can continue using BDDScenarioGenerationStage without changes.

           For new code, prefer:
               from stages.bdd_scenario import BDDScenarioStageCore

           Instead of:
               from bdd_scenario_generation_stage import BDDScenarioGenerationStage

Patterns:
- Template Method Pattern: Implements PipelineStage execution contract
- Strategy Pattern: AI Query Service fallback to direct LLM calls
- Supervised Execution Pattern: Health monitoring via SupervisorAgent
- Observer Pattern: Integrates with PipelineObservable for stage events

Integration:
- Runs after SprintPlanningStage (requirements are available)
- Provides Gherkin scenarios to DevelopmentStage for reference
- Feeds into BDD Test Generation Stage (converts scenarios to pytest-bdd)
- Stores scenarios in RAG for developer query
- Stores feature files in developer workspace

SOLID Principles:
- S: Single Responsibility - Only generates BDD scenarios
- O: Open/Closed - Extensible to new Gherkin formats without modification
- L: Liskov Substitution - Implements PipelineStage contract
- I: Interface Segregation - Focused on scenario generation
- D: Dependency Inversion - Depends on abstractions (LLMClient, RAGAgent)

Refactoring:
- Original: 506 lines (monolithic stage)
- Refactored: Modular package with focused components
  - models.py: BDD data structures (219 lines)
  - gherkin_formatter.py: Gherkin formatting (234 lines)
  - scenario_generator.py: LLM-based generation (251 lines)
  - feature_extractor.py: Feature extraction (241 lines)
  - stage_core.py: Stage orchestration (237 lines)
  - __init__.py: Package exports (84 lines)
- Wrapper: 71 lines
- Total reduction: 506 -> 71 lines (86% reduction in main file)
"""

from typing import Dict, Optional

from stages.bdd_scenario import BDDScenarioStageCore


class BDDScenarioGenerationStage(BDDScenarioStageCore):
    """
    Backward compatibility wrapper for BDD scenario generation stage.

    WHY: Maintains backward compatibility for existing code while
         enabling migration to new modular structure.

    DEPRECATED: Use stages.bdd_scenario.BDDScenarioStageCore directly
                for new code.

    This class simply inherits from BDDScenarioStageCore and provides
    the same interface as the original monolithic implementation.

    All functionality is delegated to the modular package structure:
    - stages/bdd_scenario/models.py - BDD data structures
    - stages/bdd_scenario/gherkin_formatter.py - Gherkin formatting
    - stages/bdd_scenario/scenario_generator.py - LLM generation
    - stages/bdd_scenario/feature_extractor.py - Feature extraction
    - stages/bdd_scenario/stage_core.py - Stage orchestration
    """
    pass


# Export for backward compatibility
__all__ = ["BDDScenarioGenerationStage"]
