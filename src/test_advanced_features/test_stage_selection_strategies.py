#!/usr/bin/env python3
"""
Module: test_advanced_features/test_stage_selection_strategies.py

WHY: Validates stage filtering logic for different selection strategies to ensure
     pipelines adapt correctly to project complexity and resource constraints.

RESPONSIBILITY:
- Test complexity-based stage selection (simple, medium, enterprise)
- Test resource-based stage selection (CPU, memory, time constraints)
- Test manual stage selection with specific stage names

PATTERNS:
- Arrange-Act-Assert test structure
- Guard clauses for test setup validation
"""

import unittest
from typing import List
from dynamic_pipeline import (
    ComplexityBasedSelector,
    ResourceBasedSelector,
    ManualSelector,
    ProjectComplexity
)
from test_advanced_features.mock_classes import MockStage


class TestStageSelectionStrategies(unittest.TestCase):
    """
    Test stage selection strategies.

    WHAT: Validates stage filtering logic for complexity, resource, and manual selection
    WHY: Ensures pipeline adapts correctly to different project complexities and resource constraints
    """

    def setUp(self):
        """Create test stages"""
        self.stages = [
            MockStage("requirements"),
            MockStage("architecture"),
            MockStage("development"),
            MockStage("code_review"),
            MockStage("unit_tests"),
            MockStage("integration"),
            MockStage("security"),
            MockStage("performance"),
            MockStage("validation")
        ]

    def test_complexity_based_selector_simple(self):
        """
        WHAT: Tests complexity selector filters stages for simple projects
        WHY: Simple projects should only include basic stages (requirements, dev, basic tests)
        """
        selector = ComplexityBasedSelector()
        context = {"complexity": ProjectComplexity.SIMPLE}

        selected = selector.select_stages(self.stages, context)
        selected_names = {s.name for s in selected}

        # Should include basic stages only
        self.assertIn("requirements", selected_names)
        self.assertIn("development", selected_names)
        self.assertIn("unit_tests", selected_names)

        # Should not include complex stages
        self.assertNotIn("security", selected_names)
        self.assertNotIn("performance", selected_names)

    def test_complexity_based_selector_enterprise(self):
        """
        WHAT: Tests complexity selector includes all stages for enterprise projects
        WHY: Enterprise projects need comprehensive quality gates including security and performance
        """
        selector = ComplexityBasedSelector()
        context = {"complexity": ProjectComplexity.ENTERPRISE}

        selected = selector.select_stages(self.stages, context)

        # Should include all stages for enterprise
        self.assertEqual(len(selected), len(self.stages))

    def test_resource_based_selector_low_resources(self):
        """
        WHAT: Tests resource selector filters to critical stages when resources are low
        WHY: Resource-constrained environments must prioritize essential stages over expensive ones
        """
        selector = ResourceBasedSelector()
        context = {
            "cpu_cores": 2,
            "memory_gb": 4,
            "time_budget_minutes": 30
        }

        selected = selector.select_stages(self.stages, context)
        selected_names = {s.name for s in selected}

        # Should include critical stages
        self.assertIn("requirements", selected_names)
        self.assertIn("development", selected_names)
        self.assertIn("unit_tests", selected_names)

        # Should exclude expensive stages
        self.assertNotIn("performance", selected_names)
        self.assertNotIn("security", selected_names)

    def test_resource_based_selector_high_resources(self):
        """
        WHAT: Tests resource selector includes all stages when resources are abundant
        WHY: High resource environments can run comprehensive validation including expensive stages
        """
        selector = ResourceBasedSelector()
        context = {
            "cpu_cores": 8,
            "memory_gb": 16,
            "time_budget_minutes": 120
        }

        selected = selector.select_stages(self.stages, context)

        # Should include all stages with high resources
        self.assertEqual(len(selected), len(self.stages))

    def test_manual_selector_specific_stages(self):
        """
        WHAT: Tests manual selector includes only explicitly specified stages
        WHY: Users need ability to run custom stage combinations for debugging or specific workflows
        """
        stage_names = ["requirements", "development", "validation"]
        selector = ManualSelector(stage_names)

        selected = selector.select_stages(self.stages, {})
        selected_names = {s.name for s in selected}

        # Should only include specified stages
        self.assertEqual(selected_names, set(stage_names))

    def test_manual_selector_missing_stage_warning(self):
        """
        WHAT: Tests manual selector handles non-existent stage names gracefully
        WHY: User may specify invalid stage names - should warn but not crash
        """
        stage_names = ["requirements", "nonexistent_stage", "development"]
        selector = ManualSelector(stage_names)

        selected = selector.select_stages(self.stages, {})
        selected_names = {s.name for s in selected}

        # Should only include stages that exist
        self.assertEqual(len(selected), 2)
        self.assertIn("requirements", selected_names)
        self.assertIn("development", selected_names)
