#!/usr/bin/env python3
"""
WHY: Execute validation pipeline with Chain of Responsibility pattern.

RESPONSIBILITY: Orchestrate validation stages, handle retries, and manage
LLM-based regeneration for failed validations.

PATTERNS:
- Chain of Responsibility for stage progression
- Template Method for validation flow
- Strategy pattern for retry logic
"""

from typing import List, Tuple, Optional, Dict, Any
from .models import (
    ValidationStage,
    StageValidationResult,
    ValidationContext,
    ValidationSeverity
)
from .validator_registry import ValidatorRegistry, get_default_registry


class PipelineExecutor:
    """
    WHY: Execute validation pipeline with continuous feedback.

    RESPONSIBILITY: Coordinate validation across stages, handle failures,
    and integrate with LLM for code regeneration.

    Usage:
        executor = PipelineExecutor(llm_client=llm, logger=logger)
        result = executor.validate_stage(code, ValidationStage.IMPORTS)

        if not result.passed:
            prompt = executor.get_regeneration_prompt(result)
            # Pass prompt to LLM for regeneration
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        logger: Optional[Any] = None,
        strict_mode: bool = True,
        registry: Optional[ValidatorRegistry] = None
    ):
        """
        WHY: Initialize pipeline with dependencies and configuration.

        Args:
            llm_client: Optional LLM client for code regeneration
            logger: Optional ArtemisLogger instance
            strict_mode: If True, fail on any error; if False, only fail on critical
            registry: Optional custom validator registry
        """
        self.llm_client = llm_client
        self.logger = logger
        self.strict_mode = strict_mode
        self.registry = registry if registry else get_default_registry()
        self.validation_history: List[StageValidationResult] = []

    def validate_stage(
        self,
        code: str,
        stage: ValidationStage,
        context: Optional[Dict] = None
    ) -> StageValidationResult:
        """
        WHY: Validate code at a specific generation stage.

        Args:
            code: Current generated code
            stage: Which stage to validate
            context: Optional context dictionary (converted to ValidationContext)

        Returns:
            StageValidationResult with pass/fail and feedback
        """
        # Convert dict context to ValidationContext
        validation_context = ValidationContext.from_dict(context)

        # Get validator for stage
        validator = self.registry.get_validator(stage)

        # Guard: No validator for stage
        if not validator:
            return self._create_error_result(
                stage,
                f"No validator registered for stage: {stage.value}"
            )

        # Run validation
        checks, feedback, severity = validator.validate(code, validation_context)

        # Determine pass/fail
        passed = self._determine_passed(checks, severity)

        # Create result
        result = StageValidationResult(
            stage=stage,
            passed=passed,
            checks=checks,
            feedback=feedback,
            severity=severity,
            suggestion=self._generate_suggestion(stage, feedback) if not passed else None
        )

        # Track in history
        self.validation_history.append(result)

        # Log result
        self._log_result(result)

        return result

    def _determine_passed(self, checks: Dict[str, bool], severity: str) -> bool:
        """
        WHY: Determine if validation passed based on mode and severity.

        Args:
            checks: Dictionary of check results
            severity: Severity level

        Returns:
            True if validation passed
        """
        # Guard: Strict mode - all checks must pass
        if self.strict_mode:
            return all(checks.values())

        # Non-strict mode - only fail on critical issues
        critical_checks = [
            check_name for check_name, passed in checks.items()
            if not passed and severity == ValidationSeverity.CRITICAL.value
        ]

        return len(critical_checks) == 0

    def _create_error_result(self, stage: ValidationStage, error: str) -> StageValidationResult:
        """
        WHY: Create error result when validation cannot proceed.

        Args:
            stage: Validation stage
            error: Error message

        Returns:
            StageValidationResult with error
        """
        return StageValidationResult(
            stage=stage,
            passed=False,
            checks={'error': False},
            feedback=[error],
            severity=ValidationSeverity.CRITICAL.value,
            suggestion=None
        )

    def _log_result(self, result: StageValidationResult) -> None:
        """
        WHY: Log validation result if logger is available.

        Args:
            result: Validation result to log
        """
        # Guard: No logger
        if not self.logger:
            return

        if result.passed:
            self.logger.log(f"✅ {result.stage.value} validation passed", "INFO")
        else:
            feedback_summary = ', '.join(result.feedback[:3])
            self.logger.log(
                f"❌ {result.stage.value} validation failed: {feedback_summary}",
                "WARNING"
            )

    def _generate_suggestion(self, stage: ValidationStage, feedback: List[str]) -> Optional[str]:
        """
        WHY: Generate actionable suggestions for fixing validation failures.

        Args:
            stage: Validation stage
            feedback: List of feedback messages

        Returns:
            Suggestion string or None
        """
        # Guard: No feedback
        if not feedback:
            return None

        # Dispatch table for stage-specific suggestions
        suggestions = {
            ValidationStage.IMPORTS: "Add missing imports at the top of the file. Import specific names, not '*'.",
            ValidationStage.SIGNATURE: "Add type hints and docstrings to all functions and classes.",
            ValidationStage.DOCSTRING: "Add comprehensive docstrings with Args and Returns sections.",
            ValidationStage.BODY: "Complete the implementation - remove all TODOs and placeholders. Verify method calls are correct for the framework being used.",
            ValidationStage.TESTS: "Write actual test functions with assertions. Import pytest or unittest.",
            ValidationStage.FULL_CODE: "Fix all validation errors before proceeding."
        }

        base_suggestion = suggestions.get(stage, "Fix the validation errors.")
        feedback_summary = "\n".join(f"- {f}" for f in feedback[:3])

        return f"{base_suggestion}\n\nSpecific issues:\n{feedback_summary}"

    def get_regeneration_prompt(self, result: StageValidationResult) -> str:
        """
        WHY: Generate prompt for LLM to regenerate code with fixes.

        Args:
            result: Failed validation result

        Returns:
            Prompt string to send to LLM
        """
        feedback_list = "\n".join(f"- {f}" for f in result.feedback)
        suggestion = result.suggestion if result.suggestion else ""

        prompt = f"""The {result.stage.value} validation failed with the following issues:

{feedback_list}

{suggestion}

Please regenerate the code to fix these issues. Return ONLY the corrected code, no explanations."""

        return prompt

    def generate_with_validation(
        self,
        task: str,
        stages: List[ValidationStage],
        max_retries: int = 2
    ) -> Tuple[str, bool]:
        """
        WHY: Generate code with continuous validation at each stage.

        Args:
            task: Task description for the LLM
            stages: Stages to validate (in order)
            max_retries: Max retries per stage

        Returns:
            Tuple of (generated_code, success)

        Raises:
            ValueError: If LLM client not provided
        """
        # Guard: No LLM client
        if not self.llm_client:
            raise ValueError("LLM client required for generation")

        code = ""

        for stage in stages:
            stage_prompt = self._create_stage_prompt(task, stage, code)

            # Try generation with retries
            stage_code, success = self._generate_stage_with_retries(
                stage,
                stage_prompt,
                code,
                max_retries
            )

            # Guard: Stage failed
            if not success:
                return code, False

            code = stage_code

        return code, True

    def _generate_stage_with_retries(
        self,
        stage: ValidationStage,
        prompt: str,
        existing_code: str,
        max_retries: int
    ) -> Tuple[str, bool]:
        """
        WHY: Generate code for a stage with validation and retries.

        Args:
            stage: Validation stage
            prompt: Initial prompt for LLM
            existing_code: Code generated in previous stages
            max_retries: Maximum retry attempts

        Returns:
            Tuple of (code, success)
        """
        current_prompt = prompt

        for attempt in range(max_retries + 1):
            # Log attempt
            if self.logger:
                self.logger.log(
                    f"🔄 Generating {stage.value} (attempt {attempt + 1})",
                    "INFO"
                )

            # Generate code
            new_code = self.llm_client.query(current_prompt)
            combined_code = f"{existing_code}\n{new_code}" if existing_code else new_code

            # Validate
            result = self.validate_stage(combined_code, stage)

            # Guard: Validation passed
            if result.passed:
                return combined_code, True

            # Guard: Max retries exceeded
            if attempt >= max_retries:
                self._log_max_retries(stage)
                return existing_code, False

            # Prepare for retry
            feedback_prompt = self.get_regeneration_prompt(result)
            current_prompt = f"{current_prompt}\n\n{feedback_prompt}"

            if self.logger:
                self.logger.log("⚠️  Validation failed, retrying with feedback", "WARNING")

        return existing_code, False

    def _log_max_retries(self, stage: ValidationStage) -> None:
        """
        WHY: Log when max retries are exceeded.

        Args:
            stage: Validation stage
        """
        if self.logger:
            self.logger.log(f"❌ Max retries exceeded for {stage.value}", "ERROR")

    def _create_stage_prompt(self, task: str, stage: ValidationStage, existing_code: str) -> str:
        """
        WHY: Create stage-specific prompt for LLM generation.

        Args:
            task: Overall task description
            stage: Current validation stage
            existing_code: Code generated so far

        Returns:
            Prompt string for LLM
        """
        # Dispatch table for stage prompts
        prompts = {
            ValidationStage.IMPORTS: f"Generate import statements for: {task}\n\nImport only what's needed. No star imports.",
            ValidationStage.SIGNATURE: f"Generate function/class signatures for: {task}\n\nInclude type hints and docstrings.\n\n{existing_code}",
            ValidationStage.BODY: f"Generate the implementation for: {task}\n\nComplete implementation, no TODOs or placeholders.\n\n{existing_code}",
            ValidationStage.TESTS: f"Generate pytest tests for: {task}\n\nInclude multiple test cases with assertions.\n\n{existing_code}",
        }

        return prompts.get(stage, f"Generate {stage.value} for: {task}")

    def reset(self) -> None:
        """
        WHY: Clear validation history for new pipeline run.

        Useful when starting a new validation session.
        """
        self.validation_history = []

    def get_last_result(self) -> Optional[StageValidationResult]:
        """
        WHY: Get the most recent validation result.

        Returns:
            Last StageValidationResult or None
        """
        # Guard: No history
        if not self.validation_history:
            return None

        return self.validation_history[-1]

    def get_failed_stages(self) -> List[StageValidationResult]:
        """
        WHY: Get all failed validation results.

        Returns:
            List of failed StageValidationResults
        """
        return [result for result in self.validation_history if not result.passed]
