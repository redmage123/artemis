#!/usr/bin/env python3
"""
Core Validated Developer Mixin

WHY: Adds Layer 3 (Validation Pipeline), Layer 3.5 (RAG Validation),
     and Layer 5 (Self-Critique) to developer agents to catch hallucinations
     before they propagate through the codebase.

RESPONSIBILITY:
- Initialize validation pipeline with all layers
- Provide _validated_llm_query for validated code generation
- Manage validation statistics and reporting
- Coordinate validation strategies

PATTERNS:
- Mixin Pattern: Add validation to existing agents without inheritance
- Strategy Pattern: Delegate to validation strategies
- Guard Clauses: Early returns to avoid nested conditionals
- Observer Pattern: Notify observers of validation events
"""

from typing import Dict, Optional, Any
from validation_pipeline import (
    ValidationPipeline,
    ValidationStage,
    StageValidationResult
)

from validated_developer.code_extractor import CodeExtractor
from validated_developer.event_notifier import ValidationEventNotifier
from validated_developer.validation_strategies import (
    RAGValidationStrategy,
    SelfCritiqueValidationStrategy,
    ValidationStrategyInitializer
)


class ValidatedDeveloperMixin:
    """
    Mixin that adds validation pipeline to developer agents.

    WHY: Integrates all 5 layers of validation to catch hallucinations early:
         1. Preflight - Already in standalone_developer_agent
         2. Strategy Selection - Already uses requirements_driven_validator
         3. Validation Pipeline - THIS MIXIN
         3.5. RAG-Enhanced Validation - THIS MIXIN
         5. Self-Critique Validation - THIS MIXIN
         4. Quality Gates - Already uses artifact_quality_validator

    RESPONSIBILITY:
    - Initialize validation pipeline and strategies
    - Provide validated LLM query method
    - Manage validation statistics
    - Coordinate validation event notifications
    """

    def __init_validation_pipeline__(
        self,
        strict_mode: bool = True,
        enable_rag_validation: bool = True,
        enable_self_critique: bool = True
    ):
        """
        Initialize validation pipeline (Layers 3, 3.5, and 5).

        WHY: Adds continuous validation during code generation to catch
             hallucinations before they propagate through the entire artifact.

        Args:
            strict_mode: If True, fail on any validation error.
                        If False, only fail on critical errors.
            enable_rag_validation: If True, enable RAG-enhanced validation (Layer 3.5).
            enable_self_critique: If True, enable self-critique validation (Layer 5).
        """
        # Guard: Already initialized
        if hasattr(self, 'validation_pipeline'):
            return

        # Get dependencies from agent
        llm_client = getattr(self, 'llm_client', None)
        logger = getattr(self, 'logger', None)
        rag_agent = getattr(self, 'rag', None)

        # Initialize validation pipeline (Layer 3)
        self.validation_pipeline = ValidationPipeline(
            llm_client=llm_client,
            logger=logger,
            strict_mode=strict_mode
        )

        # Initialize validation state
        self.validation_enabled = True
        self.validation_stats = {
            'total_validations': 0,
            'failed_validations': 0,
            'regenerations': 0,
            'rag_validations': 0,
            'rag_failures': 0,
            'rag_warnings': 0,
            'self_critique_validations': 0,
            'self_critique_failures': 0,
            'self_critique_regenerations': 0
        }

        # Initialize validation strategies (Layer 3.5 and Layer 5)
        framework = self._get_framework_from_context()

        self.rag_strategy = ValidationStrategyInitializer.initialize_rag_strategy(
            enable_rag=enable_rag_validation,
            rag_agent=rag_agent,
            framework=framework,
            logger=logger
        )

        self.critique_strategy = ValidationStrategyInitializer.initialize_self_critique_strategy(
            enable_critique=enable_self_critique,
            strict_mode=strict_mode,
            llm_client=llm_client,
            rag_agent=rag_agent,
            logger=logger
        )

        # Initialize event notifier
        observable = getattr(self, 'observable', None)
        developer_name = getattr(self, 'developer_name', 'unknown')
        self.event_notifier = ValidationEventNotifier(observable, developer_name, logger)

        if logger:
            logger.log("Validation Pipeline initialized (Layers 3, 3.5, 5)", "INFO")

    def _validated_llm_query(
        self,
        prompt: str,
        stage: ValidationStage,
        max_retries: int = 2,
        context: Optional[Dict] = None
    ) -> str:
        """
        Query LLM with validation pipeline.

        WHY: Replaces direct llm_client.query() calls with validated queries
             that check for hallucinations and regenerate if needed.

        Args:
            prompt: The prompt to send to LLM
            stage: Which validation stage this is
            max_retries: Maximum regeneration attempts
            context: Additional validation context

        Returns:
            Validated code from LLM

        Raises:
            Exception if validation fails after max_retries
        """
        # Guard: Validation disabled - fall back to direct query
        if not self.validation_enabled:
            return self.llm_client.query(prompt)

        llm_client = getattr(self, 'llm_client')
        logger = getattr(self, 'logger', None)

        # Mutable prompt wrapper (avoids nested ifs when updating prompt)
        class PromptWrapper:
            def __init__(self, value):
                self.value = value

        prompt_wrapper = PromptWrapper(prompt)

        for attempt in range(max_retries + 1):
            # Notify validation started
            self.event_notifier.notify_validation_event('validation_started', {
                'stage': stage.value,
                'attempt': attempt
            })

            # Generate code
            if logger and attempt > 0:
                logger.log(f"Regeneration attempt {attempt}/{max_retries}", "INFO")

            response = llm_client.query(prompt_wrapper.value)

            # Extract code from response
            code = CodeExtractor.extract_code_from_response(response)

            # Validate with pipeline (Layer 3)
            result = self.validation_pipeline.validate_stage(code, stage, context)
            self.validation_stats['total_validations'] += 1

            # Guard: Validation failed - regenerate or raise
            if not result.passed:
                if not self._handle_validation_failure(result, stage, attempt, max_retries, prompt_wrapper, logger):
                    raise Exception(f"Validation failed after {max_retries} attempts: {result.feedback}")
                continue

            # Validation passed - notify
            self.event_notifier.notify_validation_event('validation_passed', {
                'stage': stage.value,
                'attempt': attempt,
                'score': result.score if hasattr(result, 'score') else 1.0
            })

            # RAG Validation (Layer 3.5) - Only for BODY and FULL_CODE stages
            should_run_rag = (
                self.rag_strategy and
                stage in [ValidationStage.BODY, ValidationStage.FULL_CODE]
            )
            if should_run_rag and self._should_regenerate_after_rag(code, stage, context, prompt_wrapper, attempt, max_retries):
                continue

            # Self-Critique Validation (Layer 5) - Only for FULL_CODE stage
            should_run_critique = (
                self.critique_strategy and
                stage == ValidationStage.FULL_CODE
            )
            if should_run_critique and self._should_regenerate_after_critique(code, context, prompt_wrapper, attempt, max_retries):
                continue

            # All validation passed
            if logger and attempt > 0:
                logger.log(f"Validation passed after {attempt} regenerations", "INFO")

            if attempt > 0:
                self.validation_stats['regenerations'] += 1

            return code

        # Should never reach here
        return code

    def _validate_generated_code(
        self,
        code: str,
        stage: ValidationStage,
        context: Optional[Dict] = None
    ) -> StageValidationResult:
        """
        Validate generated code at a specific stage.

        Args:
            code: Code to validate
            stage: Which stage to validate
            context: Additional context

        Returns:
            Validation result
        """
        if not hasattr(self, 'validation_pipeline'):
            self.__init_validation_pipeline__()

        return self.validation_pipeline.validate_stage(code, stage, context)

    def get_validation_stats(self) -> Dict:
        """Get validation statistics"""
        if not hasattr(self, 'validation_pipeline'):
            return {'validation_pipeline': 'not_initialized'}

        pipeline_stats = self.validation_pipeline.get_validation_summary()

        return {
            **self.validation_stats,
            **pipeline_stats,
            'validation_enabled': self.validation_enabled
        }

    def enable_validation(self, enabled: bool = True):
        """Enable or disable validation pipeline"""
        self.validation_enabled = enabled
        logger = getattr(self, 'logger', None)
        if logger:
            status = "enabled" if enabled else "disabled"
            logger.log(f"Validation pipeline {status}", "INFO")

    def get_validation_report(self) -> str:
        """Get human-readable validation report"""
        stats = self.get_validation_stats()

        if stats.get('validation_pipeline') == 'not_initialized':
            return "Validation pipeline not initialized"

        report = f"""
Validation Pipeline Report
{'='*50}

Overall Statistics:
  Total Validations: {stats['total_validations']}
  Passed: {stats['passed']}
  Failed: {stats['failed']}
  Pass Rate: {stats['pass_rate']:.1%}
  Regenerations: {stats.get('regenerations', 0)}

By Stage:
"""
        for stage, counts in stats.get('by_stage', {}).items():
            report += f"  {stage}: {counts['passed']} passed, {counts['failed']} failed\n"

        return report

    def _handle_validation_failure(
        self,
        result: StageValidationResult,
        stage: ValidationStage,
        attempt: int,
        max_retries: int,
        prompt_wrapper,
        logger
    ) -> bool:
        """
        Handle validation failure (regenerate or fail).

        Returns:
            True if should continue (regenerate), False if should raise exception
        """
        # Notify validation failed
        self.event_notifier.notify_validation_event('validation_failed', {
            'stage': stage.value,
            'attempt': attempt,
            'feedback': result.feedback[:3]
        })

        self.validation_stats['failed_validations'] += 1

        if logger:
            logger.log(f"Validation failed: {', '.join(result.feedback[:2])}", "WARNING")

        # Guard: Max retries exceeded
        if attempt >= max_retries:
            self.event_notifier.notify_validation_event('validation_max_retries', {
                'stage': stage.value,
                'feedback': result.feedback
            })

            if logger:
                logger.log(f"Max retries exceeded for {stage.value}", "ERROR")

            return False  # Raise exception

        # Regenerate with feedback
        feedback_prompt = self.validation_pipeline.get_regeneration_prompt(result)
        prompt_wrapper.value += f"\n\n{feedback_prompt}"

        return True  # Continue regeneration

    def _should_regenerate_after_rag(
        self,
        code: str,
        stage: ValidationStage,
        context: Optional[Dict],
        prompt_wrapper,
        attempt: int,
        max_retries: int
    ) -> bool:
        """
        Check if should regenerate after RAG validation.

        Args:
            code: Generated code
            stage: Validation stage
            context: Validation context
            prompt_wrapper: Mutable wrapper for prompt
            attempt: Current attempt number
            max_retries: Maximum retry attempts

        Returns:
            True if regeneration needed
        """
        # Validate with RAG strategy
        rag_result = self.rag_strategy.validate_code(code, stage, context)

        # Track stats
        self.validation_stats['rag_validations'] += 1

        # Check if regeneration needed
        should_regenerate = self.rag_strategy.should_regenerate(rag_result, attempt, max_retries)

        # Notify event
        self.event_notifier.notify_rag_validation_event(rag_result, not should_regenerate)

        # Update stats
        if not rag_result.passed:
            self.validation_stats['rag_failures'] += 1

        if should_regenerate:
            # Add RAG feedback to prompt
            feedback = self.rag_strategy.generate_feedback_prompt(rag_result)
            prompt_wrapper.value += feedback
        elif not rag_result.passed:
            # Warning but not regenerating
            self.validation_stats['rag_warnings'] += 1

        return should_regenerate

    def _should_regenerate_after_critique(
        self,
        code: str,
        context: Optional[Dict],
        prompt_wrapper,
        attempt: int,
        max_retries: int
    ) -> bool:
        """
        Check if should regenerate after self-critique validation.

        Args:
            code: Generated code
            context: Validation context
            prompt_wrapper: Mutable wrapper for prompt
            attempt: Current attempt number
            max_retries: Maximum retry attempts

        Returns:
            True if regeneration needed
        """
        logger = getattr(self, 'logger', None)

        # Track stats
        self.validation_stats['self_critique_validations'] += 1
        self.event_notifier.notify_self_critique_event('critique_started', {
            'attempt': attempt,
            'code_length': len(code)
        })

        # Validate with critique strategy
        critique_result = self.critique_strategy.validate_code(
            code=code,
            context=context,
            original_prompt=prompt_wrapper.value
        )

        # Check if regeneration needed
        should_regenerate = self.critique_strategy.should_regenerate(
            critique_result, attempt, max_retries
        )

        # Notify appropriate event
        if critique_result.passed:
            self.event_notifier.notify_self_critique_event('critique_passed', {
                'confidence': critique_result.confidence_score,
                'attempt': attempt
            })
        elif should_regenerate:
            self.validation_stats['self_critique_failures'] += 1
            self.validation_stats['self_critique_regenerations'] += 1
            self.event_notifier.notify_self_critique_event('critique_regenerating', {
                'confidence': critique_result.confidence_score,
                'findings': len(critique_result.findings),
                'attempt': attempt,
                'feedback': critique_result.feedback
            })
        else:
            self.validation_stats['self_critique_failures'] += 1
            self.event_notifier.notify_self_critique_event('critique_accepted_with_warnings', {
                'confidence': critique_result.confidence_score,
                'findings': len(critique_result.findings),
                'attempt': attempt
            })

        # Update prompt if regenerating
        if should_regenerate:
            feedback = self.critique_strategy.generate_feedback_prompt(critique_result)
            prompt_wrapper.value += feedback

        return should_regenerate

    def _get_framework_from_context(self) -> Optional[str]:
        """
        Extract framework from context/metadata.

        WHY: Framework detection enables framework-specific RAG validation
             thresholds (Django vs Flask have different patterns).

        Returns:
            Framework name (django, flask, rails, react, etc.) or None
        """
        # Try context first
        context = getattr(self, 'context', None)
        if context and isinstance(context, dict):
            framework = context.get('framework')
            if framework:
                return framework.lower()

        # Try metadata
        metadata = getattr(self, 'metadata', None)
        if metadata and isinstance(metadata, dict):
            framework = metadata.get('framework')
            if framework:
                return framework.lower()

        # Try config
        config = getattr(self, 'config', None)
        if config and hasattr(config, 'framework'):
            return config.framework.lower()

        # No framework found
        return None
