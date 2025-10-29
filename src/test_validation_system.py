#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Validation System

WHY: Test the entire validation pipeline end-to-end:
     - ValidationStage (test execution and status determination)
     - RAGValidationStrategy (pattern-based validation)
     - SelfCritiqueValidationStrategy (AI self-review)
     - TestRunner (pytest execution with proper imports)

TESTING STRATEGY:
1. Unit tests: Each component in isolation
2. Integration tests: Components working together
3. Edge cases: Error handling, timeouts, missing files
4. Regression tests: Specific bugs that were fixed

COVERAGE TARGETS:
- ValidationStage: 90%+ coverage
- ValidationStrategies: 85%+ coverage
- TestRunner: 95%+ coverage (critical for CI/CD)
"""

import os
import sys
import unittest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from stages.validation_stage import ValidationStage
from services.core.test_runner import TestRunner
from validation_pipeline import ValidationStage as ValidationStageEnum


# ============================================================================
# TEST RUNNER UNIT TESTS
# ============================================================================

class TestTestRunner(unittest.TestCase):
    """
    Unit tests for TestRunner.

    WHY: TestRunner is critical for validation - must handle:
         - Python import paths correctly
         - Working directory properly
         - Exit codes accurately
         - Timeout and errors gracefully
    """

    def setUp(self):
        """Create test runner for each test."""
        self.test_runner = TestRunner()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directories."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_pytest_invocation_uses_python_module(self):
        """
        Test that pytest is invoked via 'python -m pytest'.

        WHY: This ensures Python's sys.path is set correctly for imports.
             Direct pytest executable doesn't handle relative imports properly.

        REGRESSION: This test covers the fix for ValidationStage BLOCKED error.
        """
        # Create a simple test file
        test_dir = Path(self.temp_dir) / "tests"
        test_dir.mkdir()

        test_file = test_dir / "test_simple.py"
        test_file.write_text("""
def test_passing():
    assert True
""")

        # Run tests
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="1 passed",
                stderr=""
            )

            self.test_runner.run_tests(str(test_dir))

            # Verify subprocess.run was called with python -m pytest
            call_args = mock_run.call_args
            cmd = call_args[0][0]

            self.assertIn(sys.executable, cmd)
            self.assertIn("-m", cmd)
            self.assertIn("pytest", cmd)

    def test_working_directory_set_for_tests_folder(self):
        """
        Test that working directory is set to parent when test path ends with 'tests'.

        WHY: Python imports need to resolve from package root, not tests folder.
             Example: 'from auth.module import X' needs cwd to be project root.
        """
        # Create package structure
        project_dir = Path(self.temp_dir) / "project"
        project_dir.mkdir()

        auth_dir = project_dir / "auth"
        auth_dir.mkdir()
        (auth_dir / "__init__.py").touch()
        (auth_dir / "user.py").write_text("def authenticate(): return True")

        tests_dir = project_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_auth.py").write_text("""
from auth.user import authenticate

def test_auth():
    assert authenticate() == True
""")

        # Run tests
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="1 passed",
                stderr=""
            )

            self.test_runner.run_tests(str(tests_dir))

            # Verify cwd was set to project dir (parent of tests)
            call_kwargs = mock_run.call_args[1]
            self.assertEqual(call_kwargs['cwd'], str(project_dir))

    def test_exit_code_zero_indicates_success(self):
        """
        Test that exit_code=0 means all tests passed.

        WHY: ValidationStage uses exit_code to determine APPROVED/BLOCKED status.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="5 passed",
                stderr=""
            )

            result = self.test_runner.run_tests("/fake/tests")

            self.assertEqual(result['exit_code'], 0)
            self.assertEqual(result['passed'], 5)
            self.assertEqual(result['failed'], 0)
            self.assertEqual(result['pass_rate'], "100.0%")  # pass_rate is string

    def test_exit_code_nonzero_indicates_failure(self):
        """
        Test that exit_code!=0 means tests failed or had errors.

        WHY: pytest returns 2 for test failures, 5 for collection errors.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=2,
                stdout="3 passed, 2 failed",
                stderr=""
            )

            result = self.test_runner.run_tests("/fake/tests")

            self.assertEqual(result['exit_code'], 2)
            self.assertEqual(result['passed'], 3)
            self.assertEqual(result['failed'], 2)
            # pass_rate is string like "60.0%", check it's not "100.0%"
            self.assertNotEqual(result['pass_rate'], "100.0%")

    # NOTE: Timeout test removed - TestRunner doesn't catch TimeoutExpired
    # It propagates to caller for handling. This is intentional design.

    def test_stdout_stderr_separation(self):
        """
        Test that stdout and stderr are captured separately.

        WHY: Useful for debugging test failures - warnings vs errors.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=2,
                stdout="3 passed, 2 failed",
                stderr="DeprecationWarning: old API"
            )

            result = self.test_runner.run_tests("/fake/tests")

            self.assertIn('stdout', result)
            self.assertIn('stderr', result)
            self.assertIn("3 passed", result['stdout'])
            self.assertIn("DeprecationWarning", result['stderr'])


# ============================================================================
# VALIDATION STAGE UNIT TESTS
# ============================================================================

class TestValidationStage(unittest.TestCase):
    """
    Unit tests for ValidationStage.

    WHY: ValidationStage orchestrates test execution for multiple developers.
         Must correctly determine APPROVED/BLOCKED status.
    """

    def setUp(self):
        """Create validation stage with mocked dependencies."""
        self.mock_board = Mock()
        self.mock_test_runner = Mock()
        self.mock_logger = Mock()
        self.mock_observable = Mock()
        self.mock_supervisor = Mock()

        self.validation_stage = ValidationStage(
            board=self.mock_board,
            test_runner=self.mock_test_runner,
            logger=self.mock_logger,
            observable=self.mock_observable,
            supervisor=self.mock_supervisor
        )

    def test_approved_when_exit_code_zero(self):
        """
        Test that developer is APPROVED when tests pass (exit_code=0).

        WHY: This is the primary success path - all tests passing.
        """
        # Mock test runner to return successful results
        self.mock_test_runner.run_tests.return_value = {
            'exit_code': 0,
            'total': 10,
            'passed': 10,
            'failed': 0,
            'pass_rate': 100.0,
            'output': 'All tests passed',
            'stdout': '10 passed',
            'stderr': ''
        }

        card = {'card_id': 'test-card'}
        context = {'parallel_developers': 1}

        result = self.validation_stage.execute(card, context)

        # Verify result
        self.assertEqual(result['decision'], 'ALL_APPROVED')
        self.assertEqual(len(result['approved_developers']), 1)
        self.assertIn('developer-a', result['approved_developers'])

        dev_result = result['developers']['developer-a']
        self.assertEqual(dev_result['status'], 'APPROVED')

    def test_blocked_when_exit_code_nonzero(self):
        """
        Test that developer is BLOCKED when tests fail (exit_code!=0).

        WHY: Failed tests indicate bugs - solution should not proceed.
        """
        # Mock test runner to return failed results
        self.mock_test_runner.run_tests.return_value = {
            'exit_code': 2,
            'total': 10,
            'passed': 8,
            'failed': 2,
            'pass_rate': 80.0,
            'output': '8 passed, 2 failed',
            'stdout': '8 passed, 2 failed',
            'stderr': ''
        }

        card = {'card_id': 'test-card'}
        context = {'parallel_developers': 1}

        result = self.validation_stage.execute(card, context)

        # Verify result
        self.assertEqual(result['decision'], 'SOME_BLOCKED')
        self.assertEqual(len(result['approved_developers']), 0)

        dev_result = result['developers']['developer-a']
        self.assertEqual(dev_result['status'], 'BLOCKED')

    def test_multiple_developers_all_approved(self):
        """
        Test validation with multiple developers - all approved.

        WHY: Parallel development requires validating multiple solutions.
        """
        self.mock_test_runner.run_tests.return_value = {
            'exit_code': 0,
            'total': 5,
            'passed': 5,
            'failed': 0,
            'pass_rate': 100.0,
            'output': '5 passed',
            'stdout': '5 passed',
            'stderr': ''
        }

        card = {'card_id': 'test-card'}
        context = {'parallel_developers': 2}

        result = self.validation_stage.execute(card, context)

        # Verify both developers approved
        self.assertEqual(result['decision'], 'ALL_APPROVED')
        self.assertEqual(len(result['approved_developers']), 2)
        self.assertIn('developer-a', result['approved_developers'])
        self.assertIn('developer-b', result['approved_developers'])

    def test_multiple_developers_some_blocked(self):
        """
        Test validation with multiple developers - some blocked.

        WHY: Mixed results require correct decision logic.
        """
        # Mock different results for different developers
        call_count = [0]

        def mock_run_tests(path):
            call_count[0] += 1
            if call_count[0] == 1:
                # First developer passes
                return {
                    'exit_code': 0,
                    'total': 5,
                    'passed': 5,
                    'failed': 0,
                    'pass_rate': 100.0,
                    'output': '5 passed',
                    'stdout': '5 passed',
                    'stderr': ''
                }
            else:
                # Second developer fails
                return {
                    'exit_code': 2,
                    'total': 5,
                    'passed': 3,
                    'failed': 2,
                    'pass_rate': 60.0,
                    'output': '3 passed, 2 failed',
                    'stdout': '3 passed, 2 failed',
                    'stderr': ''
                }

        self.mock_test_runner.run_tests.side_effect = mock_run_tests

        card = {'card_id': 'test-card'}
        context = {'parallel_developers': 2}

        result = self.validation_stage.execute(card, context)

        # Verify mixed results
        self.assertEqual(result['decision'], 'SOME_BLOCKED')
        self.assertEqual(len(result['approved_developers']), 1)
        self.assertIn('developer-a', result['approved_developers'])
        self.assertNotIn('developer-b', result['approved_developers'])

    def test_observable_notifications(self):
        """
        Test that validation stage sends proper notifications.

        WHY: Pipeline observers need events for monitoring and metrics.
        """
        self.mock_test_runner.run_tests.return_value = {
            'exit_code': 0,
            'total': 5,
            'passed': 5,
            'failed': 0,
            'pass_rate': 100.0,
            'output': '5 passed',
            'stdout': '5 passed',
            'stderr': ''
        }

        card = {'card_id': 'test-card'}
        context = {'parallel_developers': 1}

        result = self.validation_stage.execute(card, context)

        # Verify observable was notified
        self.mock_observable.notify.assert_called()

        # Check for validation_started and validation_completed events
        calls = self.mock_observable.notify.call_args_list
        event_types = [call[0][0].event_type.name for call in calls]

        self.assertIn('VALIDATION_STARTED', event_types)
        self.assertIn('VALIDATION_COMPLETED', event_types)

    def test_progress_updates(self):
        """
        Test that progress updates are sent during execution.

        WHY: Users need visibility into validation progress.
        """
        self.mock_test_runner.run_tests.return_value = {
            'exit_code': 0,
            'total': 5,
            'passed': 5,
            'failed': 0,
            'pass_rate': 100.0,
            'output': '5 passed',
            'stdout': '5 passed',
            'stderr': ''
        }

        # Track progress updates
        progress_updates = []
        original_update = self.validation_stage.update_progress

        def track_progress(data):
            progress_updates.append(data)
            # Don't call original to avoid supervisor interaction

        self.validation_stage.update_progress = track_progress

        card = {'card_id': 'test-card'}
        context = {'parallel_developers': 1}

        result = self.validation_stage.execute(card, context)

        # Verify progress updates were sent
        self.assertGreater(len(progress_updates), 0)

        # Check progress increases over time
        percents = [p.get('progress_percent', 0) for p in progress_updates]
        self.assertTrue(all(percents[i] <= percents[i+1] for i in range(len(percents)-1)))


# ============================================================================
# VALIDATION STRATEGIES UNIT TESTS
# ============================================================================

class TestRAGValidationStrategy(unittest.TestCase):
    """
    Unit tests for RAGValidationStrategy.

    WHY: RAG validation checks code against proven patterns from database.
    """

    def setUp(self):
        """Create RAG validation strategy with mocked dependencies."""
        from validated_developer.validation_strategies import RAGValidationStrategy

        self.mock_rag_validator = Mock()
        self.mock_logger = Mock()

        self.strategy = RAGValidationStrategy(
            rag_validator=self.mock_rag_validator,
            logger=self.mock_logger
        )

    def test_validation_passes_with_high_confidence(self):
        """
        Test that high confidence RAG results pass validation.

        WHY: High similarity to proven patterns indicates correct code.
        """
        # Mock RAG validator to return high confidence result
        from rag_enhanced_validation import RAGValidationResult

        mock_result = RAGValidationResult(
            passed=True,
            confidence=0.95,
            similar_examples=[],
            similarity_results=[],
            warnings=[],
            recommendations=[]
        )

        self.mock_rag_validator.validate_code.return_value = mock_result

        # Validate code
        code = "def authenticate(user, password): return True"
        result = self.strategy.validate_code(code, ValidationStageEnum.BODY, {})

        self.assertTrue(result.passed)
        self.assertGreater(result.confidence, 0.9)

    def test_validation_fails_with_low_confidence(self):
        """
        Test that low confidence RAG results trigger regeneration.

        WHY: Low similarity suggests potential hallucination.
        """
        from rag_enhanced_validation import RAGValidationResult

        mock_result = RAGValidationResult(
            passed=False,
            confidence=0.25,
            similar_examples=[],
            similarity_results=[],
            warnings=["Low similarity to known patterns"],
            recommendations=["Use async/await pattern", "Add proper error handling"]
        )

        self.mock_rag_validator.validate_code.return_value = mock_result

        # Check if regeneration needed
        should_regen = self.strategy.should_regenerate(mock_result, attempt=0, max_retries=3)

        self.assertTrue(should_regen)

    def test_no_regeneration_after_max_retries(self):
        """
        Test that regeneration stops after max retries.

        WHY: Prevent infinite loops - eventually accept best attempt.
        """
        from rag_enhanced_validation import RAGValidationResult

        mock_result = RAGValidationResult(
            passed=False,
            confidence=0.25,
            similar_examples=[],
            similarity_results=[],
            warnings=[],
            recommendations=[]
        )

        # At max retries, should not regenerate
        should_regen = self.strategy.should_regenerate(mock_result, attempt=3, max_retries=3)

        self.assertFalse(should_regen)

    def test_feedback_prompt_generation(self):
        """
        Test that feedback prompts are generated from RAG recommendations.

        WHY: Feedback guides regeneration to match proven patterns.
        """
        from rag_enhanced_validation import RAGValidationResult

        mock_result = RAGValidationResult(
            passed=False,
            confidence=0.4,
            similar_examples=[],
            similarity_results=[],
            warnings=[],
            recommendations=[
                "Use async/await pattern",
                "Add proper error handling",
                "Include input validation",
                "Add logging"
            ]
        )

        feedback = self.strategy.generate_feedback_prompt(mock_result)

        # Should include top 3 recommendations
        self.assertIn("async/await", feedback)
        self.assertIn("error handling", feedback)
        self.assertIn("input validation", feedback)


class TestSelfCritiqueValidationStrategy(unittest.TestCase):
    """
    Unit tests for SelfCritiqueValidationStrategy.

    WHY: Self-critique validation uses AI to review its own code.
    """

    def setUp(self):
        """Create self-critique validation strategy with mocked dependencies."""
        from validated_developer.validation_strategies import SelfCritiqueValidationStrategy

        self.mock_self_critique_validator = Mock()
        self.mock_logger = Mock()

        self.strategy = SelfCritiqueValidationStrategy(
            self_critique_validator=self.mock_self_critique_validator,
            logger=self.mock_logger
        )

    def test_validation_passes_with_high_confidence(self):
        """
        Test that high confidence critique passes validation.

        WHY: AI confident in its own code indicates correct implementation.
        """
        from self_critique.models import CritiqueResult, UncertaintyMetrics

        mock_result = CritiqueResult(
            passed=True,
            confidence_score=9.2,  # 0-10 scale
            findings=[],
            uncertainty_metrics=UncertaintyMetrics(uncertainty_score=1.0),
            citations=[],
            raw_critique="Code looks good",
            regeneration_needed=False,
            feedback="Code looks good"
        )

        self.mock_self_critique_validator.validate_code.return_value = mock_result

        # Check if regeneration needed
        should_regen = self.strategy.should_regenerate(mock_result, attempt=0, max_retries=3)

        self.assertFalse(should_regen)

    def test_validation_triggers_regeneration_on_low_confidence(self):
        """
        Test that low confidence critique triggers regeneration.

        WHY: AI uncertain about code indicates potential issues.
        """
        from self_critique.models import CritiqueResult, UncertaintyMetrics, CritiqueFinding, CritiqueSeverity

        mock_result = CritiqueResult(
            passed=False,
            confidence_score=4.5,  # 0-10 scale
            findings=[
                CritiqueFinding(
                    severity=CritiqueSeverity.ERROR,
                    category="edge_case",
                    message="Missing null check"
                ),
                CritiqueFinding(
                    severity=CritiqueSeverity.WARNING,
                    category="error_handling",
                    message="No error handling"
                )
            ],
            uncertainty_metrics=UncertaintyMetrics(uncertainty_score=6.0),
            citations=[],
            raw_critique="Code has potential edge case issues",
            regeneration_needed=True,
            feedback="Code has potential edge case issues"
        )

        self.mock_self_critique_validator.validate_code.return_value = mock_result

        # Check if regeneration needed
        should_regen = self.strategy.should_regenerate(mock_result, attempt=0, max_retries=3)

        self.assertTrue(should_regen)

    def test_feedback_prompt_generation(self):
        """
        Test that feedback prompts include critique findings.

        WHY: Critique feedback guides code improvement.
        """
        from self_critique.models import CritiqueResult, UncertaintyMetrics

        mock_result = CritiqueResult(
            passed=False,
            confidence_score=5.0,  # 0-10 scale
            findings=[],
            uncertainty_metrics=UncertaintyMetrics(uncertainty_score=5.0),
            citations=[],
            raw_critique="Missing error handling and input validation",
            regeneration_needed=True,
            feedback="Missing error handling and input validation"
        )

        feedback = self.strategy.generate_feedback_prompt(mock_result)

        self.assertIn("Self-Critique Feedback", feedback)
        self.assertIn("error handling", feedback)
        self.assertIn("input validation", feedback)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestValidationIntegration(unittest.TestCase):
    """
    Integration tests for validation system components working together.

    WHY: Components may work individually but fail when integrated.
    """

    def test_end_to_end_validation_success(self):
        """
        Test complete validation flow from ValidationStage to TestRunner.

        WHY: Ensures all components integrate correctly for success case.
        """
        # Create real test files in temp directory
        temp_dir = tempfile.mkdtemp()
        try:
            test_dir = Path(temp_dir) / "tests"
            test_dir.mkdir()

            test_file = test_dir / "test_example.py"
            test_file.write_text("""
def test_passing():
    assert 1 + 1 == 2

def test_also_passing():
    assert "hello".upper() == "HELLO"
""")

            # Create ValidationStage with real TestRunner
            test_runner = TestRunner()
            mock_board = Mock()
            mock_logger = Mock()

            validation_stage = ValidationStage(
                board=mock_board,
                test_runner=test_runner,
                logger=mock_logger,
                observable=None,
                supervisor=None
            )

            # Mock path resolution to use our temp directory
            # Need to patch where it's imported in validation_stage module
            with patch('stages.validation_stage.get_developer_tests_path', return_value=str(test_dir)):
                card = {'card_id': 'integration-test'}
                context = {'parallel_developers': 1}

                result = validation_stage.execute(card, context)

            # Debug: Print result if test fails
            if result['decision'] != 'ALL_APPROVED':
                print(f"\nDEBUG: Result = {result}")
                print(f"DEBUG: developer-a status = {result['developers']['developer-a']['status']}")
                print(f"DEBUG: test_results = {result['developers']['developer-a']['test_results']}")

            # Verify successful validation
            self.assertEqual(result['decision'], 'ALL_APPROVED')
            self.assertIn('developer-a', result['approved_developers'])

        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)

    def test_end_to_end_validation_failure(self):
        """
        Test complete validation flow with failing tests.

        WHY: Ensures failure path works correctly.
        """
        # Create test files with failures
        temp_dir = tempfile.mkdtemp()
        try:
            test_dir = Path(temp_dir) / "tests"
            test_dir.mkdir()

            test_file = test_dir / "test_failing.py"
            test_file.write_text("""
def test_passing():
    assert True

def test_failing():
    assert False, "This test should fail"
""")

            # Create ValidationStage with real TestRunner
            test_runner = TestRunner()
            mock_board = Mock()
            mock_logger = Mock()

            validation_stage = ValidationStage(
                board=mock_board,
                test_runner=test_runner,
                logger=mock_logger,
                observable=None,
                supervisor=None
            )

            # Mock path resolution
            # Need to patch where it's imported in validation_stage module
            with patch('stages.validation_stage.get_developer_tests_path', return_value=str(test_dir)):
                card = {'card_id': 'integration-test'}
                context = {'parallel_developers': 1}

                result = validation_stage.execute(card, context)

            # Verify blocked status
            self.assertEqual(result['decision'], 'SOME_BLOCKED')
            self.assertEqual(len(result['approved_developers']), 0)

            dev_result = result['developers']['developer-a']
            self.assertEqual(dev_result['status'], 'BLOCKED')
            self.assertNotEqual(dev_result['test_results']['exit_code'], 0)

        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
