#!/usr/bin/env python3
"""
Retry Coordinator with Circuit Breaker (Layer 4: Retry with Refinement)

WHY: Orchestrates intelligent retry with prompt refinement and circuit breaker.
     Prevents infinite retry loops with configurable limits.
     Learns from retry patterns for supervisor.

RESPONSIBILITY: ONLY retry coordination - delegates validation and generation.
PATTERNS: Strategy pattern, Circuit Breaker pattern.

Example:
    coordinator = RetryCoordinator(max_retries=3)
    result = coordinator.execute_with_retry(generate_func, validate_func, prompt)
"""

from typing import Dict, Callable, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import os

from artemis_stage_interface import LoggerInterface
from artemis_exceptions import ValidationError, ConfigurationError, create_wrapped_exception
from validation_failure_analyzer import ValidationFailureAnalyzer, FailureAnalysis
from prompt_refinement_engine import PromptRefinementEngine, RefinedPrompt
from confidence_scorer import ConfidenceScorer, ConfidenceScore


@dataclass
class RetryAttempt:
    """
    Record of a single retry attempt.

    Attributes:
        attempt_number: Which attempt this was (1, 2, 3...)
        timestamp: When the attempt occurred
        prompt: Prompt used for this attempt
        validation_results: Validation results
        confidence_score: Confidence score
        failure_analysis: Analysis of why it failed (if it did)
        succeeded: Whether this attempt succeeded
    """
    attempt_number: int
    timestamp: str
    prompt: str
    validation_results: Dict
    confidence_score: float
    failure_analysis: Optional[FailureAnalysis] = None
    succeeded: bool = False


@dataclass
class RetryResult:
    """
    Final result after all retry attempts.

    Attributes:
        succeeded: Whether retry loop succeeded
        final_code: Final generated code (if successful)
        attempts: List of all retry attempts
        total_attempts: Total number of attempts made
        circuit_breaker_tripped: Whether circuit breaker stopped retries
    """
    succeeded: bool
    final_code: Optional[str] = None
    attempts: List[RetryAttempt] = field(default_factory=list)
    total_attempts: int = 0
    circuit_breaker_tripped: bool = False


class RetryCoordinator:
    """
    Coordinates intelligent retry with prompt refinement and circuit breaker.

    WHY: Simple retries waste tokens on same mistakes.
         Intelligent retry refines prompts based on failures.
         Circuit breaker prevents infinite loops.

    RESPONSIBILITY: ONLY coordinate retries - delegate validation/generation.
    PATTERNS: Circuit Breaker, Strategy, Observer.
    PERFORMANCE: Early termination, configurable retry limits.

    Example:
        coordinator = RetryCoordinator(max_retries=3)
        result = coordinator.execute_with_retry(
            generate_func=lambda p: generate_code(p),
            validate_func=lambda c: validate(c),
            original_prompt="Write a function"
        )
    """

    def __init__(
        self,
        logger: Optional[LoggerInterface] = None,
        max_retries: Optional[int] = None,
        acceptance_threshold: float = 0.85
    ):
        """
        Initialize retry coordinator.

        Args:
            logger: Optional logger
            max_retries: Maximum retry attempts (from env or default 3)
            acceptance_threshold: Minimum confidence to accept (0.0-1.0)
        """
        self.logger = logger

        # Get max retries from env or use provided value or default
        self.max_retries = max_retries or int(
            os.getenv("ARTEMIS_MAX_VALIDATION_RETRIES", "3")
        )

        self.acceptance_threshold = acceptance_threshold

        # Create components (dependency injection)
        self.failure_analyzer = ValidationFailureAnalyzer(logger=logger)
        self.refinement_engine = PromptRefinementEngine(logger=logger)
        self.confidence_scorer = ConfidenceScorer(
            logger=logger,
            acceptance_threshold=acceptance_threshold
        )

        # Circuit breaker state
        self.circuit_open = False
        self.consecutive_failures = 0

        if self.logger:
            self.logger.log(
                f"🔄 Retry coordinator initialized (max_retries={self.max_retries}, "
                f"threshold={acceptance_threshold:.2f})",
                "DEBUG"
            )

    def execute_with_retry(
        self,
        generate_func: Callable[[str], str],
        validate_func: Callable[[str], Dict],
        original_prompt: str
    ) -> RetryResult:
        """
        Execute generation with intelligent retry.

        WHY: Automatically refines prompts and retries on validation failure.
             Stops early if circuit breaker trips or confidence sufficient.

        PERFORMANCE: Early termination on success, circuit breaker on repeated failures.

        Args:
            generate_func: Function that generates code from prompt
            validate_func: Function that validates generated code
            original_prompt: Original prompt to generate from

        Returns:
            RetryResult with success status and attempt history

        Example:
            result = coordinator.execute_with_retry(
                generate_func=lambda p: llm.generate(p),
                validate_func=lambda c: validator.validate(c),
                original_prompt="Write a function that adds two numbers"
            )
        """
        attempts = []
        current_prompt = original_prompt

        # Retry loop with circuit breaker
        for attempt_num in range(1, self.max_retries + 1):
            # Check circuit breaker (early termination)
            if self._is_circuit_open():
                if self.logger:
                    self.logger.log("🚫 Circuit breaker OPEN - stopping retries", "WARNING")

                return RetryResult(
                    succeeded=False,
                    attempts=attempts,
                    total_attempts=len(attempts),
                    circuit_breaker_tripped=True
                )

            if self.logger:
                self.logger.log(
                    f"🔄 Retry attempt {attempt_num}/{self.max_retries}",
                    "INFO"
                )

            # Execute attempt (avoid nested ifs - extract to helper)
            attempt = self._execute_attempt(
                attempt_num=attempt_num,
                prompt=current_prompt,
                generate_func=generate_func,
                validate_func=validate_func
            )

            attempts.append(attempt)

            # Check if attempt succeeded (early return on success)
            if attempt.succeeded:
                if self.logger:
                    self.logger.log(
                        f"✅ Retry succeeded on attempt {attempt_num}",
                        "INFO"
                    )

                self._reset_circuit_breaker()

                return RetryResult(
                    succeeded=True,
                    final_code=attempt.validation_results.get('code'),
                    attempts=attempts,
                    total_attempts=len(attempts),
                    circuit_breaker_tripped=False
                )

            # Attempt failed - refine prompt for next attempt
            current_prompt = self._refine_prompt_for_next_attempt(
                original_prompt=original_prompt,
                attempt=attempt,
                attempt_num=attempt_num
            )

            # Update circuit breaker state
            self._update_circuit_breaker(attempt)

        # All retries exhausted
        if self.logger:
            self.logger.log(
                f"❌ All {self.max_retries} retry attempts exhausted",
                "WARNING"
            )

        return RetryResult(
            succeeded=False,
            attempts=attempts,
            total_attempts=len(attempts),
            circuit_breaker_tripped=False
        )

    def _execute_attempt(
        self,
        attempt_num: int,
        prompt: str,
        generate_func: Callable[[str], str],
        validate_func: Callable[[str], Dict]
    ) -> RetryAttempt:
        """
        Execute single retry attempt.

        WHY: Encapsulates attempt logic to avoid nested code.
        PERFORMANCE: Early returns on success.

        Args:
            attempt_num: Attempt number
            prompt: Prompt to use
            generate_func: Code generation function
            validate_func: Validation function

        Returns:
            RetryAttempt with results
        """
        timestamp = datetime.now().isoformat()

        try:
            # Generate code
            code = generate_func(prompt)

            # Validate code
            validation_results = validate_func(code)
            validation_results['code'] = code  # Include code in results

            # Calculate confidence score
            confidence_score_obj = self.confidence_scorer.score_confidence(validation_results)

            # Analyze failures if validation didn't pass
            failure_analysis = None
            if not confidence_score_obj.passed_threshold:
                failure_analysis = self.failure_analyzer.analyze_failures(
                    validation_results,
                    code
                )

            # Determine if attempt succeeded
            succeeded = confidence_score_obj.passed_threshold

            return RetryAttempt(
                attempt_number=attempt_num,
                timestamp=timestamp,
                prompt=prompt,
                validation_results=validation_results,
                confidence_score=confidence_score_obj.confidence,
                failure_analysis=failure_analysis,
                succeeded=succeeded
            )

        except Exception as e:
            # Handle generation/validation errors
            if self.logger:
                self.logger.log(
                    f"❌ Attempt {attempt_num} failed with error: {e}",
                    "ERROR"
                )

            return RetryAttempt(
                attempt_number=attempt_num,
                timestamp=timestamp,
                prompt=prompt,
                validation_results={'error': str(e), 'passed': False},
                confidence_score=0.0,
                failure_analysis=None,
                succeeded=False
            )

    def _refine_prompt_for_next_attempt(
        self,
        original_prompt: str,
        attempt: RetryAttempt,
        attempt_num: int
    ) -> str:
        """
        Refine prompt based on failure analysis.

        WHY: Each retry should be more specific based on what failed.
        PERFORMANCE: Early return if no failure analysis.

        Args:
            original_prompt: Original prompt
            attempt: Failed attempt
            attempt_num: Attempt number

        Returns:
            Refined prompt for next attempt
        """
        # Early return if no failure analysis available
        if not attempt.failure_analysis:
            return original_prompt

        # Generate refined prompt
        refined_prompt_obj = self.refinement_engine.refine_prompt(
            original_prompt=original_prompt,
            failure_analysis=attempt.failure_analysis,
            attempt=attempt_num + 1  # Next attempt number
        )

        if self.logger:
            self.logger.log(
                f"✨ Refined prompt for attempt {attempt_num + 1} "
                f"({len(refined_prompt_obj.constraints_added)} constraints added)",
                "DEBUG"
            )

        return refined_prompt_obj.prompt

    def _is_circuit_open(self) -> bool:
        """
        Check if circuit breaker is open.

        WHY: Prevents wasting tokens on hopeless retry loops.
        PERFORMANCE: O(1) check.

        Returns:
            True if circuit is open (should stop retries)
        """
        return self.circuit_open

    def _update_circuit_breaker(self, attempt: RetryAttempt):
        """
        Update circuit breaker state after attempt.

        WHY: Opens circuit after too many consecutive failures.
        PATTERNS: Circuit Breaker pattern.

        Args:
            attempt: Retry attempt that just completed
        """
        # Strategy pattern: Success/failure handling
        if attempt.succeeded:
            self.consecutive_failures = 0
        else:
            self.consecutive_failures += 1

        # Open circuit if too many consecutive failures
        circuit_breaker_threshold = 3
        if self.consecutive_failures >= circuit_breaker_threshold:
            self.circuit_open = True

            if self.logger:
                self.logger.log(
                    f"🚫 Circuit breaker OPENED after {circuit_breaker_threshold} "
                    "consecutive failures",
                    "WARNING"
                )

    def _reset_circuit_breaker(self):
        """
        Reset circuit breaker after success.

        WHY: Allows future retries after successful attempt.
        """
        self.circuit_open = False
        self.consecutive_failures = 0

    def get_retry_stats(self, result: RetryResult) -> Dict:
        """
        Get statistics from retry result.

        WHY: Enables supervisor learning from retry patterns.

        Args:
            result: Retry result

        Returns:
            Statistics dictionary
        """
        return {
            'total_attempts': result.total_attempts,
            'succeeded': result.succeeded,
            'circuit_breaker_tripped': result.circuit_breaker_tripped,
            'avg_confidence': sum(a.confidence_score for a in result.attempts) / len(result.attempts) if result.attempts else 0.0,
            'failure_categories': [
                a.failure_analysis.category.value
                for a in result.attempts
                if a.failure_analysis
            ]
        }
