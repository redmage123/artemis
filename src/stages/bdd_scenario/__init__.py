#!/usr/bin/env python3
"""
Package: stages/bdd_scenario

WHY: Provides modular BDD scenario generation capability for Artemis pipeline.
     Transforms structured requirements into executable Gherkin specifications
     using LLM-powered generation with comprehensive validation.

RESPONSIBILITY: Export BDD scenario generation components for pipeline integration.
                Provides backward compatibility via stage_core exports.

PATTERNS:
- Facade Pattern: Simple package interface to complex subsystem
- Single Responsibility: Each module handles one aspect of BDD generation

Architecture:
    models.py           - BDD data structures (Feature, Scenario, Step)
    feature_extractor.py - Extract feature data from requirements
    scenario_generator.py - Generate scenarios via LLM
    gherkin_formatter.py - Format scenarios as Gherkin syntax
    stage_core.py       - Main stage orchestrator

Integration:
- Used by artemis_orchestrator for pipeline execution
- Integrates with RAG for artifact storage
- Integrates with SupervisorAgent for health monitoring
- Writes feature files to developer workspace

Example usage:
    from stages.bdd_scenario import BDDScenarioStageCore

    stage = BDDScenarioStageCore(
        board=kanban_board,
        rag=rag_agent,
        logger=logger,
        llm_client=llm_client
    )

    result = stage.execute(card, context)
"""

# Core stage orchestrator (main export)
from .stage_core import BDDScenarioStageCore

# Data models
from .models import (
    Feature,
    Scenario,
    Step,
    ValidationResult,
    GenerationRequest,
    GenerationResult
)

# Generation components
from .scenario_generator import (
    ScenarioGenerator,
    RequirementsRetriever,
    ScenarioValidator
)

# Feature extraction and storage
from .feature_extractor import (
    FeatureExtractor,
    FeatureFileStorage
)

# Gherkin formatting
from .gherkin_formatter import GherkinFormatter

# Version info
__version__ = "1.0.0"
__author__ = "Artemis Refactoring Team"

# Public API
__all__ = [
    # Main stage
    "BDDScenarioStageCore",

    # Models
    "Feature",
    "Scenario",
    "Step",
    "ValidationResult",
    "GenerationRequest",
    "GenerationResult",

    # Generation
    "ScenarioGenerator",
    "RequirementsRetriever",
    "ScenarioValidator",

    # Extraction and storage
    "FeatureExtractor",
    "FeatureFileStorage",

    # Formatting
    "GherkinFormatter",
]
