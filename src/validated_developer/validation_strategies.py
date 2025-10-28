#!/usr/bin/env python3
"""
Validation Strategies

WHY: Different validation approaches (RAG, self-critique) need to be encapsulated
     in separate strategies to maintain single responsibility and enable testing.

RESPONSIBILITY:
- RAG-enhanced validation strategy (Layer 3.5)
- Self-critique validation strategy (Layer 5)
- Regeneration decision logic
- Feedback prompt generation

PATTERNS:
- Strategy Pattern: Encapsulate validation algorithms
- Guard Clauses: Early returns to avoid nested conditionals
- Dependency Injection: Validators injected via constructors
"""

from typing import Dict, Optional, Any, Callable
from validation_pipeline import ValidationStage


class RAGValidationStrategy:
    """
    RAG-enhanced validation strategy (Layer 3.5).

    WHY: Checks generated code against proven patterns from RAG database
         to catch hallucinations that pass standard validation but don't
         match real-world code patterns.

    RESPONSIBILITY:
    - Validate code against RAG database
    - Determine if regeneration needed based on confidence
    - Generate feedback prompts from RAG recommendations
    """

    def __init__(self, rag_validator: Any, logger: Optional[Any] = None):
        """
        Initialize RAG validation strategy.

        Args:
            rag_validator: RAG validator instance
            logger: Logger for debugging
        """
        self.rag_validator = rag_validator
        self.logger = logger

    def validate_code(
        self,
        code: str,
        stage: ValidationStage,
        context: Optional[Dict]
    ) -> 'RAGValidationResult':
        """
        Validate code using RAG-enhanced validation.

        Args:
            code: Generated code to validate
            stage: Validation stage (BODY or FULL_CODE)
            context: Additional context (language, framework, requirements)

        Returns:
            RAGValidationResult with pass/fail and recommendations
        """
        try:
            # Build RAG context from validation context
            rag_context = self._build_rag_context(context)

            # Validate using RAG validator
            result = self.rag_validator.validate_code(
                generated_code=code,
                context=rag_context,
                top_k=5  # Query top 5 similar examples
            )

            return result

        except Exception as e:
            # RAG validation failure shouldn't block code generation
            return self._create_error_result(e)

    def should_regenerate(
        self,
        rag_result: 'RAGValidationResult',
        attempt: int,
        max_retries: int
    ) -> bool:
        """
        Determine if regeneration needed based on RAG validation result.

        WHY: Low confidence RAG results indicate potential hallucinations
             that should trigger regeneration.

        Args:
            rag_result: RAG validation result
            attempt: Current attempt number
            max_retries: Maximum retry attempts

        Returns:
            True if regeneration needed
        """
        # Guard: Validation passed
        if rag_result.passed:
            # Log low confidence warning but don't regenerate
            if rag_result.confidence < 0.7 and self.logger:
                self.logger.log(
                    f"Code validated but with low RAG confidence: {rag_result.confidence:.2f}",
                    "WARNING"
                )
            return False

        # Guard: High confidence or max retries reached
        should_regenerate = rag_result.confidence < 0.3 and attempt < max_retries
        if not should_regenerate:
            return False

        # Regenerate with RAG feedback
        if self.logger:
            self.logger.log("Regenerating with RAG feedback", "INFO")

        return True

    def generate_feedback_prompt(self, rag_result: 'RAGValidationResult') -> str:
        """
        Generate feedback prompt from RAG recommendations.

        Args:
            rag_result: RAG validation result

        Returns:
            Feedback prompt for regeneration
        """
        # Take top 3 recommendations
        recommendations = rag_result.recommendations[:3]
        feedback = "\\n".join(recommendations)

        return f"\\n\\nRAG Validation Feedback:\\n{feedback}"

    def _build_rag_context(self, context: Optional[Dict]) -> Dict:
        """
        Build RAG context from validation context.

        Args:
            context: Validation context

        Returns:
            RAG context dictionary
        """
        if not context:
            return {'language': 'python'}

        return {
            'language': context.get('language', 'python'),
            'framework': context.get('framework'),
            'requirements': context.get('task_description')
        }

    def _create_error_result(self, error: Exception) -> 'RAGValidationResult':
        """
        Create error result for RAG validation failures.

        Args:
            error: Exception that occurred

        Returns:
            RAGValidationResult with passed=True (don't block on errors)
        """
        if self.logger:
            self.logger.log(f"RAG validation error: {error}", "DEBUG")

        # Import here to avoid circular dependency
        from rag_enhanced_validation import RAGValidationResult

        return RAGValidationResult(
            passed=True,  # Don't block on RAG errors
            confidence=0.5,  # Medium confidence
            similar_examples=[],
            similarity_results=[],
            warnings=[f"RAG validation encountered error: {str(error)}"],
            recommendations=[]
        )


class SelfCritiqueValidationStrategy:
    """
    Self-critique validation strategy (Layer 5).

    WHY: AI reviews its own code to catch subtle bugs, edge cases,
         and hallucinations that automated checks miss.

    RESPONSIBILITY:
    - Run self-critique validation
    - Determine if regeneration needed based on confidence
    - Generate feedback prompts from critique findings
    """

    def __init__(self, self_critique_validator: Any, logger: Optional[Any] = None):
        """
        Initialize self-critique validation strategy.

        Args:
            self_critique_validator: Self-critique validator instance
            logger: Logger for debugging
        """
        self.self_critique_validator = self_critique_validator
        self.logger = logger

    def validate_code(
        self,
        code: str,
        context: Optional[Dict],
        original_prompt: str
    ) -> 'CritiqueResult':
        """
        Validate code using self-critique.

        Args:
            code: Generated code to critique
            context: Validation context
            original_prompt: Original prompt for context

        Returns:
            CritiqueResult with pass/fail and findings
        """
        return self.self_critique_validator.validate_code(
            code=code,
            context=context,
            original_prompt=original_prompt
        )

    def should_regenerate(
        self,
        critique_result: 'CritiqueResult',
        attempt: int,
        max_retries: int
    ) -> bool:
        """
        Determine if regeneration needed based on critique result.

        Args:
            critique_result: Critique validation result
            attempt: Current attempt number
            max_retries: Maximum retry attempts

        Returns:
            True if regeneration needed
        """
        # Guard: Critique passed
        if critique_result.passed:
            if self.logger:
                self.logger.log(
                    f"Self-critique passed (confidence: {critique_result.confidence_score:.2f})",
                    "INFO"
                )
            return False

        # Critique failed - log warning
        if self.logger:
            self.logger.log(
                f"Self-critique concerns (confidence: {critique_result.confidence_score:.2f})",
                "WARNING"
            )

        # Guard: Cannot regenerate (max retries or not needed)
        can_regenerate = critique_result.regeneration_needed and attempt < max_retries
        if not can_regenerate:
            if self.logger:
                self.logger.log(
                    "Proceeding despite low confidence (max retries or no regeneration needed)",
                    "WARNING"
                )
            return False

        # Regenerate with feedback
        if self.logger:
            self.logger.log(
                f"Regenerating with self-critique feedback (attempt {attempt + 1}/{max_retries})",
                "INFO"
            )

        return True

    def generate_feedback_prompt(self, critique_result: 'CritiqueResult') -> str:
        """
        Generate feedback prompt from critique findings.

        Args:
            critique_result: Critique validation result

        Returns:
            Feedback prompt for regeneration
        """
        return f"\\n\\nSelf-Critique Feedback:\\n{critique_result.feedback}"


class ValidationStrategyInitializer:
    """
    Initializes validation strategies with proper dependency injection.

    WHY: Strategy initialization requires checking for available dependencies
         and configuring validators. This centralizes initialization logic.
    """

    @staticmethod
    def initialize_rag_strategy(
        enable_rag: bool,
        rag_agent: Optional[Any],
        framework: Optional[str],
        logger: Optional[Any]
    ) -> Optional[RAGValidationStrategy]:
        """
        Initialize RAG validation strategy.

        Args:
            enable_rag: Whether to enable RAG validation
            rag_agent: RAG agent instance
            framework: Framework for framework-specific validation
            logger: Logger instance

        Returns:
            RAGValidationStrategy or None if disabled/unavailable
        """
        # Guard: RAG validation disabled
        if not enable_rag:
            return None

        # Guard: No RAG agent available
        if not rag_agent:
            if logger:
                logger.log("RAG Validation disabled (no RAG agent)", "WARNING")
            return None

        # Create RAG validator
        from rag_enhanced_validation import RAGValidationFactory

        rag_validator = RAGValidationFactory.create_validator(
            rag_agent=rag_agent,
            framework=framework
        )

        if logger:
            logger.log(f"RAG Validation enabled (framework: {framework or 'generic'})", "INFO")

        return RAGValidationStrategy(rag_validator, logger)

    @staticmethod
    def initialize_self_critique_strategy(
        enable_critique: bool,
        strict_mode: bool,
        llm_client: Optional[Any],
        rag_agent: Optional[Any],
        logger: Optional[Any]
    ) -> Optional[SelfCritiqueValidationStrategy]:
        """
        Initialize self-critique validation strategy.

        Args:
            enable_critique: Whether to enable self-critique
            strict_mode: Whether to use strict mode
            llm_client: LLM client instance
            rag_agent: RAG agent instance
            logger: Logger instance

        Returns:
            SelfCritiqueValidationStrategy or None if disabled
        """
        # Guard: Self-critique disabled
        if not enable_critique:
            return None

        # Determine environment based on settings
        environment = 'production' if strict_mode else 'development'

        # Create self-critique validator
        from self_critique_validator import SelfCritiqueFactory

        self_critique_validator = SelfCritiqueFactory.create_validator(
            llm_client=llm_client,
            environment=environment,
            strict_mode=strict_mode,
            rag_agent=rag_agent,
            logger=logger
        )

        if logger:
            logger.log(
                f"Self-Critique Validation enabled (Layer 5, level: {self_critique_validator.level.value})",
                "INFO"
            )

        return SelfCritiqueValidationStrategy(self_critique_validator, logger)
