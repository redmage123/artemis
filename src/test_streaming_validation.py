#!/usr/bin/env python3
"""
Integration Tests for Streaming Validation (Layer 3.6)

WHY: Validates that streaming validation works end-to-end:
     - StreamingValidator detects placeholders/forbidden patterns
     - LLM client supports streaming with callbacks
     - Developer agent integrates streaming validation
     - Early stopping prevents wasted tokens

TESTING STRATEGY:
1. Unit tests: StreamingValidator in isolation
2. Integration tests: LLM client + validator
3. End-to-end tests: Full developer agent with streaming enabled
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from streaming_validator import (
    StreamingValidator,
    StreamingValidatorFactory,
    StreamingValidationResult
)
from llm_client import LLMMessage, LLMResponse


class TestStreamingValidatorUnit(unittest.TestCase):
    """
    Unit tests for StreamingValidator.

    WHY: Test validation logic in isolation (no LLM calls).
    """

    def setUp(self):
        """Create validator for each test."""
        self.validator = StreamingValidatorFactory.create_validator(
            mode='standard',
            allowed_imports=['django', 'requests'],
            logger=None
        )

    def test_placeholder_detection_todo(self):
        """
        Test that TODO placeholders are detected.

        WHY: Placeholders indicate incomplete/hallucinated code.
        """
        # Simulate streaming tokens that form a TODO
        tokens = ["def", " ", "process", "(", "):", "\n", "    ", "#", " ", "TODO", ":", " ", "implement"]

        result = None
        for token in tokens:
            result = self.validator.on_token(token)
            if not result.should_continue:
                break

        # Validation should have stopped at TODO
        self.assertFalse(result.should_continue)
        self.assertIn("Placeholder detected", result.reason)
        self.assertIn("TODO", result.reason)

    def test_placeholder_detection_pass(self):
        """
        Test that pass statements are detected.

        WHY: Pass indicates incomplete implementation.
        """
        # Simulate tokens forming "pass"
        tokens = ["def", " ", "foo", "(", "):", "\n", "    ", "pass"]

        result = None
        for token in tokens:
            result = self.validator.on_token(token)
            if not result.should_continue:
                break

        self.assertFalse(result.should_continue)
        self.assertIn("Placeholder detected", result.reason)

    def test_forbidden_pattern_eval(self):
        """
        Test that eval() is detected as forbidden.

        WHY: eval() is a hallucination indicator and security risk.
        """
        tokens = ["result", " ", "=", " ", "eval", "(", "user_input", ")"]

        result = None
        for token in tokens:
            result = self.validator.on_token(token)
            if not result.should_continue:
                break

        self.assertFalse(result.should_continue)
        self.assertIn("Forbidden pattern", result.reason)
        self.assertIn("eval", result.reason)

    def test_forbidden_pattern_exec(self):
        """
        Test that exec() is detected as forbidden.

        WHY: exec() is a hallucination indicator and security risk.
        """
        tokens = ["exec", "(", '"import os"', ")"]

        result = None
        for token in tokens:
            result = self.validator.on_token(token)
            if not result.should_continue:
                break

        self.assertFalse(result.should_continue)
        self.assertIn("Forbidden pattern", result.reason)
        self.assertIn("exec", result.reason)

    def test_invalid_import_detection(self):
        """
        Test that imports not in requirements are detected.

        WHY: LLMs hallucinate imports for libraries not in requirements.
        """
        # kafka is NOT in allowed_imports (only django and requests)
        tokens = ["from", " ", "kafka", " ", "import", " ", "KafkaProducer"]

        result = None
        for token in tokens:
            result = self.validator.on_token(token)
            if not result.should_continue:
                break

        self.assertFalse(result.should_continue)
        self.assertIn("Hallucinated import", result.reason)
        self.assertIn("kafka", result.reason)

    def test_allowed_import_passes(self):
        """
        Test that allowed imports pass validation.

        WHY: Django and requests are in allowed_imports.
        """
        # Django is in allowed_imports
        tokens = ["from", " ", "django", ".", "db", " ", "import", " ", "models", "\n"]

        result = None
        for token in tokens:
            result = self.validator.on_token(token)

        # Should continue (django is allowed)
        self.assertTrue(result.should_continue)

    def test_standard_library_always_allowed(self):
        """
        Test that standard library imports are always allowed.

        WHY: No need to restrict standard library.
        """
        tokens = ["import", " ", "json", "\n", "import", " ", "os"]

        result = None
        for token in tokens:
            result = self.validator.on_token(token)

        self.assertTrue(result.should_continue)

    def test_validation_interval_respected(self):
        """
        Test that validation happens at correct intervals.

        WHY: Performance - don't validate every single token.
        """
        # Standard mode checks every 50 tokens
        for i in range(49):
            result = self.validator.on_token("x")

        # Should have done 0 validations (interval not reached)
        self.assertEqual(self.validator.validation_count, 0)

        # Token 50 should trigger validation
        result = self.validator.on_token("x")
        self.assertEqual(self.validator.validation_count, 1)

    def test_stats_collection(self):
        """
        Test that statistics are collected.

        WHY: Enables monitoring and optimization.
        """
        # Generate 150 tokens to trigger validations
        for i in range(150):
            self.validator.on_token("x")

        stats = self.validator.get_stats()

        self.assertEqual(stats['token_count'], 150)
        self.assertEqual(stats['validation_mode'], 'standard')
        self.assertEqual(stats['validation_interval'], 50)
        self.assertGreater(stats['validation_count'], 0)


class TestStreamingValidatorModes(unittest.TestCase):
    """
    Test different validation modes.

    WHY: Ensure lightweight/standard/thorough modes work correctly.
    """

    def test_lightweight_mode_interval(self):
        """Test lightweight mode checks every 25 tokens."""
        validator = StreamingValidatorFactory.create_validator(mode='lightweight')

        for i in range(24):
            validator.on_token("x")

        self.assertEqual(validator.validation_count, 0)

        validator.on_token("x")  # Token 25
        self.assertEqual(validator.validation_count, 1)

    def test_thorough_mode_interval(self):
        """Test thorough mode checks every 100 tokens."""
        validator = StreamingValidatorFactory.create_validator(mode='thorough')

        for i in range(99):
            validator.on_token("x")

        self.assertEqual(validator.validation_count, 0)

        validator.on_token("x")  # Token 100
        self.assertEqual(validator.validation_count, 1)

    def test_lightweight_mode_allows_placeholders(self):
        """
        Test that lightweight mode allows placeholders.

        WHY: Lightweight mode only stops on security issues.
        """
        validator = StreamingValidatorFactory.create_validator(mode='lightweight')

        tokens = ["#", " ", "TODO", ":", " ", "implement"]
        result = None
        for token in tokens:
            result = validator.on_token(token)

        # Lightweight mode allows placeholders
        self.assertTrue(result.should_continue)


class TestLLMClientStreaming(unittest.TestCase):
    """
    Integration tests for LLM client streaming.

    WHY: Test that complete_stream() works with callbacks.
    """

    @patch('llm_client.anthropic')
    def test_anthropic_streaming_with_callback(self, mock_anthropic):
        """
        Test Anthropic streaming with validation callback.

        WHY: Ensure callback can stop generation early.
        """
        from llm_client import AnthropicClient

        # Mock streaming response
        mock_stream = [
            Mock(delta=Mock(text="def ")),
            Mock(delta=Mock(text="foo():")),
            Mock(delta=Mock(text="\n    ")),
            Mock(delta=Mock(text="# TODO")),  # Should stop here
        ]

        mock_client = Mock()
        mock_client.messages.stream.return_value.__enter__.return_value.text_stream = iter(mock_stream)
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient(api_key="test-key")

        # Callback that stops at TODO
        stop_at_todo = lambda token: "TODO" not in token

        messages = [LLMMessage(role="user", content="Write a function")]

        response = client.complete_stream(
            messages=messages,
            on_token_callback=stop_at_todo,
            model="claude-3-5-sonnet-20241022"
        )

        # Should have stopped before completing
        self.assertIn("def", response.content)
        self.assertNotIn("TODO", response.content)


class TestStreamingValidationIntegration(unittest.TestCase):
    """
    End-to-end integration tests.

    WHY: Test full integration with standalone_developer_agent.
    """

    def test_environment_variable_enables_streaming(self):
        """
        Test that ARTEMIS_ENABLE_STREAMING_VALIDATION enables streaming.

        WHY: Ensure environment variable control works.
        """
        from standalone_developer_agent import StandaloneDeveloperAgent

        with patch.dict(os.environ, {'ARTEMIS_ENABLE_STREAMING_VALIDATION': 'true'}):
            agent = StandaloneDeveloperAgent(
                developer_name="test-dev",
                developer_type="conservative",
                llm_provider="openai"
            )

            # Create validator - should succeed when env var is true
            validator = agent._create_streaming_validator()
            self.assertIsNotNone(validator)

    def test_environment_variable_disables_streaming(self):
        """
        Test that streaming is disabled by default.

        WHY: Ensure backward compatibility.
        """
        from standalone_developer_agent import StandaloneDeveloperAgent

        with patch.dict(os.environ, {}, clear=True):
            agent = StandaloneDeveloperAgent(
                developer_name="test-dev",
                developer_type="conservative",
                llm_provider="openai"
            )

            # Should return None when disabled
            validator = agent._create_streaming_validator()
            self.assertIsNone(validator)

    def test_streaming_validator_not_available_returns_none(self):
        """
        Test that missing streaming_validator module is handled gracefully.

        WHY: Ensure backward compatibility if module not installed.
        """
        from standalone_developer_agent import StandaloneDeveloperAgent

        with patch.dict(os.environ, {'ARTEMIS_ENABLE_STREAMING_VALIDATION': 'true'}):
            # Temporarily disable streaming validator
            import standalone_developer_agent
            original_value = standalone_developer_agent.STREAMING_VALIDATOR_AVAILABLE
            standalone_developer_agent.STREAMING_VALIDATOR_AVAILABLE = False

            try:
                agent = StandaloneDeveloperAgent(
                    developer_name="test-dev",
                    developer_type="conservative",
                    llm_provider="openai"
                )

                validator = agent._create_streaming_validator()
                self.assertIsNone(validator)
            finally:
                # Restore original value
                standalone_developer_agent.STREAMING_VALIDATOR_AVAILABLE = original_value


class TestStreamingValidationPerformance(unittest.TestCase):
    """
    Performance tests for streaming validation.

    WHY: Ensure validation overhead is acceptable (< 1ms per token).
    """

    def test_validation_overhead_is_minimal(self):
        """
        Test that validation adds minimal overhead.

        WHY: on_token() is called thousands of times, must be fast.
        """
        import time

        validator = StreamingValidatorFactory.create_validator(mode='standard')

        # Measure time for 1000 token validations
        start = time.time()
        for i in range(1000):
            validator.on_token("x")
        elapsed = time.time() - start

        # Should be well under 1 second for 1000 tokens
        self.assertLess(elapsed, 1.0)

        # Average should be < 1ms per token
        avg_per_token = elapsed / 1000
        self.assertLess(avg_per_token, 0.001)


def run_streaming_validation_tests():
    """
    Run all streaming validation tests.

    WHY: Convenience function for running full test suite.
    """
    print("\n" + "="*70)
    print("STREAMING VALIDATION TEST SUITE (Layer 3.6)")
    print("="*70)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStreamingValidatorUnit))
    suite.addTests(loader.loadTestsFromTestCase(TestStreamingValidatorModes))
    suite.addTests(loader.loadTestsFromTestCase(TestLLMClientStreaming))
    suite.addTests(loader.loadTestsFromTestCase(TestStreamingValidationIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestStreamingValidationPerformance))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_streaming_validation_tests()
    sys.exit(0 if success else 1)
