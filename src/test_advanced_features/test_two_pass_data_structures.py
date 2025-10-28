#!/usr/bin/env python3
"""
Module: test_advanced_features/test_two_pass_data_structures.py

WHY: Validates core data structures for two-pass pipeline (PassResult, PassDelta,
     PassMemento) which carry state and learning between passes.

RESPONSIBILITY:
- Test PassResult creation and serialization
- Test PassDelta calculation and change detection
- Test PassMemento state capture and deep copy

PATTERNS:
- Data structure validation
- Immutability testing (deep copy)
- Guard clauses for validation
"""

import unittest
from two_pass_pipeline import PassResult, PassDelta, PassMemento


class TestPassResult(unittest.TestCase):
    """
    Test PassResult data structure.

    WHAT: Validates pass result creation and serialization
    WHY: PassResult carries execution artifacts between passes and to observers
    """

    def test_pass_result_creation(self):
        """
        WHAT: Tests PassResult creation with all fields
        WHY: Pass results must store artifacts, learnings, and quality metrics
        """
        result = PassResult(
            pass_name="FirstPass",
            success=True,
            artifacts={"code": "test.py"},
            quality_score=0.85,
            learnings=["Learning 1", "Learning 2"],
            insights={"complexity": "low"}
        )

        self.assertEqual(result.pass_name, "FirstPass")
        self.assertTrue(result.success)
        self.assertEqual(result.quality_score, 0.85)
        self.assertEqual(len(result.learnings), 2)

    def test_pass_result_to_dict(self):
        """
        WHAT: Tests PassResult serialization to dict
        WHY: Results must be serializable for logging, storage, and event transmission
        """
        result = PassResult(
            pass_name="FirstPass",
            success=True,
            quality_score=0.85
        )

        result_dict = result.to_dict()

        self.assertEqual(result_dict["pass_name"], "FirstPass")
        self.assertEqual(result_dict["success"], True)
        self.assertEqual(result_dict["quality_score"], 0.85)


class TestPassDelta(unittest.TestCase):
    """
    Test PassDelta calculation.

    WHAT: Validates delta detection between passes
    WHY: Delta quantifies improvements/degradations for rollback decisions
    """

    def test_delta_quality_improvement(self):
        """
        WHAT: Tests delta correctly identifies quality improvement
        WHY: Quality delta drives rollback decisions - must be accurate
        """
        first = PassResult(
            pass_name="FirstPass",
            success=True,
            quality_score=0.70,
            artifacts={"file1": "v1"}
        )

        second = PassResult(
            pass_name="SecondPass",
            success=True,
            quality_score=0.85,
            artifacts={"file1": "v2", "file2": "new"}
        )

        delta = PassDelta(first_pass=first, second_pass=second)

        # Quality improved
        self.assertGreater(delta.quality_delta, 0)
        self.assertTrue(delta.quality_improved)
        self.assertEqual(delta.quality_delta, 0.15)

    def test_delta_detects_new_artifacts(self):
        """
        WHAT: Tests delta identifies new artifacts in second pass
        WHY: Artifact changes indicate progress and incremental improvements
        """
        first = PassResult(
            pass_name="FirstPass",
            success=True,
            artifacts={"file1": "v1"}
        )

        second = PassResult(
            pass_name="SecondPass",
            success=True,
            artifacts={"file1": "v1", "file2": "new"}
        )

        delta = PassDelta(first_pass=first, second_pass=second)

        # Should detect new artifact
        self.assertIn("file2", delta.new_artifacts)

    def test_delta_detects_modified_artifacts(self):
        """
        WHAT: Tests delta identifies modified artifacts
        WHY: Modified artifacts show refinements applied in second pass
        """
        first = PassResult(
            pass_name="FirstPass",
            success=True,
            artifacts={"file1": "version1"}
        )

        second = PassResult(
            pass_name="SecondPass",
            success=True,
            artifacts={"file1": "version2"}
        )

        delta = PassDelta(first_pass=first, second_pass=second)

        # Should detect modification
        self.assertIn("file1", delta.modified_artifacts)

    def test_delta_new_learnings(self):
        """
        WHAT: Tests delta extracts new learnings from second pass
        WHY: Learning extraction enables knowledge accumulation across passes
        """
        first = PassResult(
            pass_name="FirstPass",
            success=True,
            learnings=["Learning 1"]
        )

        second = PassResult(
            pass_name="SecondPass",
            success=True,
            learnings=["Learning 1", "Learning 2"]
        )

        delta = PassDelta(first_pass=first, second_pass=second)

        # Should identify new learning
        self.assertIn("Learning 2", delta.new_learnings)


class TestPassMemento(unittest.TestCase):
    """
    Test PassMemento state capture.

    WHAT: Validates memento creation and deep copy
    WHY: Memento enables rollback and learning transfer without state corruption
    """

    def test_memento_creation(self):
        """
        WHAT: Tests memento captures complete pass state
        WHY: Memento must preserve all state for accurate restoration
        """
        memento = PassMemento(
            pass_name="FirstPass",
            state={"key": "value"},
            artifacts={"file": "content"},
            learnings=["learning1"],
            insights={"complexity": "low"},
            quality_score=0.75
        )

        self.assertEqual(memento.pass_name, "FirstPass")
        self.assertEqual(memento.quality_score, 0.75)
        self.assertIn("learning1", memento.learnings)

    def test_memento_deep_copy(self):
        """
        WHAT: Tests memento deep copy prevents mutation
        WHY: Memento copies must be independent to prevent cross-contamination
        """
        original = PassMemento(
            pass_name="FirstPass",
            state={"key": ["value"]},
            artifacts={},
            learnings=[],
            insights={},
            quality_score=0.75
        )

        copy_memento = original.create_copy()

        # Modify copy
        copy_memento.state["key"].append("new_value")

        # Original should be unchanged
        self.assertEqual(len(original.state["key"]), 1)
        self.assertEqual(len(copy_memento.state["key"]), 2)
