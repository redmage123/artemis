#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

Original file: 2,690 lines (7 monolithic stage classes)
Refactored to: stages/ directory (7 individual modules)
This wrapper: ~60 lines (97.8% reduction!)

DEPRECATION NOTICE:
This module provides backward compatibility for existing code that imports
stages from artemis_stages. New code should use:

    from stages import ProjectAnalysisStage, ArchitectureStage, ...

The stage classes have been extracted to individual modules:
- stages/project_analysis_stage.py
- stages/architecture_stage.py
- stages/dependency_validation_stage.py
- stages/development_stage.py
- stages/validation_stage.py
- stages/integration_stage.py
- stages/testing_stage.py

WHY THIS REFACTORING:
- Original: Monolithic 2,690-line file with 7 stage classes
- Refactored: 7 individual files with single responsibilities
- Benefits: Easier testing, better separation of concerns, maintainable

ARCHITECTURE:
Each stage is now in its own file with focused responsibility:
- ProjectAnalysisStage: Pre-implementation task analysis
- ArchitectureStage: ADR generation and architecture decisions
- DependencyValidationStage: Dependency compatibility validation
- DevelopmentStage: Code generation orchestration
- ValidationStage: Code quality validation
- IntegrationStage: Integration testing
- TestingStage: Regression testing and quality gates
"""

# Re-export base interfaces for backward compatibility
# (research_stage.py incorrectly imports PipelineStage from here instead of artemis_stage_interface)
from artemis_stage_interface import PipelineStage, LoggerInterface

# Re-export all stages from the modularized stages/ directory
from stages import (
    ProjectAnalysisStage,
    ArchitectureStage,
    DependencyValidationStage,
    DevelopmentStage,
    ValidationStage,
    IntegrationStage,
    TestingStage
)

# Re-export ResearchStage from research_stage module
from research_stage import ResearchStage, create_research_stage

# Re-export for backward compatibility
__all__ = [
    # Base interfaces (for backward compatibility with research_stage.py)
    'PipelineStage',
    'LoggerInterface',

    # Core stages (from stages/ directory)
    'ProjectAnalysisStage',
    'ArchitectureStage',
    'DependencyValidationStage',
    'DevelopmentStage',
    'ValidationStage',
    'IntegrationStage',
    'TestingStage',

    # Research stage (from research_stage.py)
    'ResearchStage',
    'create_research_stage',
]
