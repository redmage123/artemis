#!/usr/bin/env python3
"""
Package: test_advanced_features

WHY: Comprehensive unit tests for Dynamic Pipelines, Two-Pass Pipelines, and
     Thermodynamic Computing organized into focused, maintainable modules.

RESPONSIBILITY:
- Export all test classes for backward compatibility
- Provide clear module organization by feature area
- Maintain test discoverability for unittest runners

ARCHITECTURE:
    mock_classes.py                        - Reusable test mocks

    Dynamic Pipeline Tests:
    test_stage_selection_strategies.py     - Stage selection logic
    test_retry_policy.py                   - Retry and backoff
    test_stage_executors.py                - Execution engine
    test_dynamic_pipeline_builder.py       - Builder validation
    test_dynamic_pipeline.py               - Pipeline orchestration

    Two-Pass Pipeline Tests:
    test_two_pass_data_structures.py       - PassResult, Delta, Memento
    test_two_pass_strategies.py            - First/second pass strategies
    test_two_pass_orchestration.py         - Comparison, rollback, integration

    Thermodynamic Computing Tests:
    test_thermodynamic_data_structures.py  - ConfidenceScore
    test_uncertainty_strategies.py         - Bayesian, Monte Carlo, Ensemble
    test_temperature_scheduling.py         - Annealing and sampling
    test_thermodynamic_computing.py        - Facade and helpers

PATTERNS:
- Test organization by feature domain
- Mock classes for controlled testing
- Each module exports its test classes
"""

# Mock classes
from test_advanced_features.mock_classes import (
    MockStage,
    MockObserver
)

# Dynamic Pipeline Tests
from test_advanced_features.test_stage_selection_strategies import (
    TestStageSelectionStrategies
)

from test_advanced_features.test_retry_policy import (
    TestRetryPolicy
)

from test_advanced_features.test_stage_executors import (
    TestStageExecutor,
    TestParallelStageExecutor
)

from test_advanced_features.test_dynamic_pipeline_builder import (
    TestDynamicPipelineBuilder
)

from test_advanced_features.test_dynamic_pipeline import (
    TestDynamicPipeline,
    TestDynamicPipelineFactory
)

# Two-Pass Pipeline Tests
from test_advanced_features.test_two_pass_data_structures import (
    TestPassResult,
    TestPassDelta,
    TestPassMemento
)

from test_advanced_features.test_two_pass_strategies import (
    TestFirstPassStrategy,
    TestSecondPassStrategy
)

from test_advanced_features.test_two_pass_orchestration import (
    TestPassComparator,
    TestRollbackManager,
    TestTwoPassPipeline,
    TestTwoPassPipelineFactory
)

# Thermodynamic Computing Tests
from test_advanced_features.test_thermodynamic_data_structures import (
    TestConfidenceScore
)

from test_advanced_features.test_uncertainty_strategies import (
    TestBayesianUncertaintyStrategy,
    TestMonteCarloUncertaintyStrategy,
    TestEnsembleUncertaintyStrategy
)

from test_advanced_features.test_temperature_scheduling import (
    TestTemperatureScheduler
)

from test_advanced_features.test_thermodynamic_computing import (
    TestThermodynamicComputing,
    TestThermodynamicHelperFunctions
)


__all__ = [
    # Mock classes
    'MockStage',
    'MockObserver',

    # Dynamic Pipeline Tests
    'TestStageSelectionStrategies',
    'TestRetryPolicy',
    'TestStageExecutor',
    'TestParallelStageExecutor',
    'TestDynamicPipelineBuilder',
    'TestDynamicPipeline',
    'TestDynamicPipelineFactory',

    # Two-Pass Pipeline Tests
    'TestPassResult',
    'TestPassDelta',
    'TestPassMemento',
    'TestFirstPassStrategy',
    'TestSecondPassStrategy',
    'TestPassComparator',
    'TestRollbackManager',
    'TestTwoPassPipeline',
    'TestTwoPassPipelineFactory',

    # Thermodynamic Computing Tests
    'TestConfidenceScore',
    'TestBayesianUncertaintyStrategy',
    'TestMonteCarloUncertaintyStrategy',
    'TestEnsembleUncertaintyStrategy',
    'TestTemperatureScheduler',
    'TestThermodynamicComputing',
    'TestThermodynamicHelperFunctions',
]
