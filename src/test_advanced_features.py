#!/usr/bin/env python3
"""
Module: test_advanced_features.py (BACKWARD COMPATIBILITY WRAPPER)

WHY: This module maintains backward compatibility by re-exporting all test classes
     from the modularized test_advanced_features package. Existing test runners
     and imports continue to work unchanged.

MIGRATION: Code should migrate to direct imports from test_advanced_features package:
    OLD: from test_advanced_features import TestStageSelectionStrategies
    NEW: from test_advanced_features.test_stage_selection_strategies import TestStageSelectionStrategies

ARCHITECTURE:
    This is now a thin wrapper. The actual implementation is in:
    /test_advanced_features/
        - mock_classes.py
        - test_stage_selection_strategies.py
        - test_retry_policy.py
        - test_stage_executors.py
        - test_dynamic_pipeline_builder.py
        - test_dynamic_pipeline.py
        - test_two_pass_data_structures.py
        - test_two_pass_strategies.py
        - test_two_pass_orchestration.py
        - test_thermodynamic_data_structures.py
        - test_uncertainty_strategies.py
        - test_temperature_scheduling.py
        - test_thermodynamic_computing.py

PATTERNS:
- Re-export pattern for backward compatibility
- Deprecation path for future refactoring
"""

# Re-export everything from the package
from test_advanced_features import *

# Maintain module docstring for documentation
__doc__ = """
Comprehensive unit tests for Dynamic Pipelines, Two-Pass Pipelines, and Thermodynamic Computing

Test Coverage:
1. Dynamic Pipelines:
   - Stage selection strategies (complexity, resource, manual)
   - Parallel execution and dependency resolution
   - Retry logic and error handling
   - Runtime modification (add/remove stages)
   - Resource allocation
   - Observer integration

2. Two-Pass Pipelines:
   - First pass execution
   - Second pass execution with learning transfer
   - Delta detection and comparison
   - Learning transfer between passes
   - Rollback functionality
   - Pass comparison metrics

3. Thermodynamic Computing:
   - Uncertainty quantification (Bayesian, Monte Carlo, Ensemble)
   - Bayesian learning and prior updates
   - Monte Carlo simulation
   - Temperature scheduling and annealing
   - Ensemble methods and voting
   - Confidence tracking and history

Design Principles:
- NO elif chains (use dispatch tables)
- NO nested loops (extract to helper methods)
- NO nested ifs (use guard clauses)
- ALL public methods tested
- Mock external dependencies
- Test error conditions
- Verify observer integration
"""

# For unittest discovery
if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)
