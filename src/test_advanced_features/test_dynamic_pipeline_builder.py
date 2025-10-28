#!/usr/bin/env python3
"""
Module: test_advanced_features/test_dynamic_pipeline_builder.py

WHY: Validates builder pattern configuration and validation to ensure pipelines
     are properly configured before execution starts.

RESPONSIBILITY:
- Test builder validation (stages required, no duplicates)
- Test dependency validation
- Test successful pipeline construction

PATTERNS:
- Builder pattern testing
- Validation testing with expected exceptions
- Guard clauses for early validation
"""

import unittest
from dynamic_pipeline import (
    DynamicPipelineBuilder,
    ComplexityBasedSelector,
    PipelineState
)
from artemis_exceptions import PipelineException
from test_advanced_features.mock_classes import MockStage


class TestDynamicPipelineBuilder(unittest.TestCase):
    """
    Test dynamic pipeline builder validation.

    WHAT: Validates builder configuration, validation, and pipeline construction
    WHY: Builder ensures valid pipeline configuration before execution
    """

    def test_builder_requires_stages(self):
        """
        WHAT: Tests builder fails when no stages provided
        WHY: Pipeline needs at least one stage to be useful - fail early with clear error
        """
        builder = DynamicPipelineBuilder()

        with self.assertRaises(PipelineException) as cm:
            builder.build()

        self.assertIn("at least one stage", str(cm.exception).lower())

    def test_builder_detects_duplicate_stage_names(self):
        """
        WHAT: Tests builder detects duplicate stage names
        WHY: Duplicate names cause result lookup ambiguity - must enforce uniqueness
        """
        builder = DynamicPipelineBuilder()
        builder.add_stage(MockStage("duplicate"))
        builder.add_stage(MockStage("duplicate"))

        with self.assertRaises(PipelineException) as cm:
            builder.build()

        self.assertIn("duplicate", str(cm.exception).lower())

    def test_builder_validates_dependencies(self):
        """
        WHAT: Tests builder detects invalid stage dependencies
        WHY: Referencing non-existent dependencies causes runtime errors - validate early
        """
        builder = DynamicPipelineBuilder()
        builder.add_stage(MockStage("stage1", dependencies=["nonexistent"]))

        with self.assertRaises(PipelineException) as cm:
            builder.build()

        self.assertIn("invalid dependencies", str(cm.exception).lower())

    def test_builder_creates_valid_pipeline(self):
        """
        WHAT: Tests builder creates valid pipeline with all components
        WHY: Builder should wire together all components (executor, observable, strategies)
        """
        builder = DynamicPipelineBuilder()
        builder.with_name("test-pipeline")
        builder.add_stage(MockStage("stage1"))
        builder.with_strategy(ComplexityBasedSelector())
        builder.with_parallelism(enabled=True, max_workers=2)

        pipeline = builder.build()

        self.assertIsNotNone(pipeline)
        self.assertEqual(pipeline.name, "test-pipeline")
        self.assertEqual(pipeline.state, PipelineState.READY)
