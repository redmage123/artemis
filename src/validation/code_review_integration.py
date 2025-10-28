#!/usr/bin/env python3
"""
Code Review Integration with Anti-Hallucination Validation

WHY: Enhance code reviews with validation-aware prompts
RESPONSIBILITY: Integrate orchestrator with CodeReviewAgent
PATTERNS: Adapter (CodeReviewAgent → ValidationStrategy), Decorator (enhance prompts)

This module integrates the anti-hallucination orchestrator with code review:
1. Get intelligent validation strategy for code review task
2. Generate validation-aware prompts for LLM
3. Include code standards scanner information
4. Enhance review checklist with validation criteria

Example:
    from validation.code_review_integration import get_code_review_validation_strategy

    # Get strategy for code review
    strategy = get_code_review_validation_strategy(
        code_size=500,
        is_critical=True,
        has_tests=True
    )

    # Generate validation-aware review prompt
    from validation import generate_code_review_prompt
    prompt = generate_code_review_prompt(code, validation_strategy=strategy)
"""

from typing import Optional, List, Dict, Any
from pathlib import Path

from artemis_logger import get_logger
from artemis_exceptions import (
    PipelineValidationError,
    wrap_exception,
)
from validation import (
    AntiHallucinationOrchestrator,
    TaskType,
    TaskContext,
    ValidationStrategy,
    generate_validation_aware_prompt,
    generate_code_review_prompt,
)


class CodeReviewValidationIntegration:
    """
    Integrate anti-hallucination validation with code review.

    WHY: Code reviews need intelligent validation strategy selection
    RESPONSIBILITY: Provide validation-aware prompts for code reviews
    PATTERNS: Adapter, Strategy

    This class:
    - Determines appropriate validation strategy for code reviews
    - Enhances review prompts with validation awareness
    - Provides code standards scanner information to reviewers
    - Ensures reviews check for same issues as validation pipeline
    """

    def __init__(self, logger: Optional[Any] = None):
        """
        Initialize code review validation integration.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger("code_review_validation")
        self.orchestrator = AntiHallucinationOrchestrator(logger=self.logger)

    def get_validation_strategy_for_review(
        self,
        code_size: int,
        is_critical: bool = False,
        has_tests: bool = False,
        dependencies_count: int = 0,
        review_depth: str = "standard"
    ) -> ValidationStrategy:
        """
        Get validation strategy appropriate for code review.

        WHY: Code reviews need same validation criteria as generation
        RESPONSIBILITY: Select validation strategy for review task

        Args:
            code_size: Size of code being reviewed (lines)
            is_critical: Whether code is critical (security, payments, etc.)
            has_tests: Whether code has tests
            dependencies_count: Number of external dependencies
            review_depth: Review depth (minimal, standard, thorough, critical)

        Returns:
            ValidationStrategy for code review

        Raises:
            PipelineValidationError: If strategy selection fails

        Example:
            strategy = integration.get_validation_strategy_for_review(
                code_size=500,
                is_critical=True,
                has_tests=True
            )
        """
        try:
            # Map review depth to profile
            profile_map = {
                "minimal": "minimal",
                "standard": "standard",
                "thorough": "thorough",
                "critical": "critical"
            }

            # Create task context
            context = TaskContext(
                task_type=TaskType.CODE_REVIEW,
                code_complexity=code_size,
                is_critical=is_critical,
                has_tests=has_tests,
                dependencies_count=dependencies_count,
                time_budget_ms=None
            )

            # Get strategy from orchestrator
            strategy = self.orchestrator.select_strategy(context)

            self.logger.info(f"Code review validation strategy:")
            self.logger.info(f"  Profile: {strategy.profile.value}")
            self.logger.info(f"  Risk: {strategy.risk_level.value}")
            self.logger.info(f"  Techniques: {', '.join(strategy.techniques)}")
            self.logger.info(f"  Expected reduction: {strategy.expected_reduction:.1%}")

            return strategy

        except PipelineValidationError:
            raise
        except Exception as e:
            raise wrap_exception(
                e,
                PipelineValidationError,
                "Failed to get validation strategy for code review",
                {
                    "code_size": code_size,
                    "is_critical": is_critical,
                    "has_tests": has_tests,
                    "dependencies_count": dependencies_count,
                    "review_depth": review_depth
                }
            )

    def enhance_review_prompt_with_validation(
        self,
        base_prompt: str,
        validation_strategy: ValidationStrategy,
        include_code_standards: bool = True
    ) -> str:
        """
        Enhance code review prompt with validation awareness.

        WHY: Reviewers should know about validation pipeline and code standards
        RESPONSIBILITY: Add validation context to review prompts

        Args:
            base_prompt: Original review prompt
            validation_strategy: Validation strategy from orchestrator
            include_code_standards: Include code standards scanner info

        Returns:
            Enhanced prompt with validation awareness

        Raises:
            PipelineValidationError: If prompt enhancement fails

        Example:
            enhanced = integration.enhance_review_prompt_with_validation(
                base_prompt="Review this code",
                validation_strategy=strategy,
                include_code_standards=True
            )
        """
        try:
            return generate_validation_aware_prompt(
                base_prompt=base_prompt,
                validation_strategy=validation_strategy,
                include_code_standards=include_code_standards,
                include_anti_hallucination_info=True
            )
        except PipelineValidationError:
            raise
        except Exception as e:
            raise wrap_exception(
                e,
                PipelineValidationError,
                "Failed to enhance review prompt with validation",
                {
                    "base_prompt_length": len(base_prompt),
                    "include_code_standards": include_code_standards
                }
            )

    def generate_review_checklist(
        self,
        validation_strategy: ValidationStrategy,
        include_standards: bool = True
    ) -> List[str]:
        """
        Generate code review checklist based on validation strategy.

        WHY: Checklist ensures reviews cover validation criteria
        RESPONSIBILITY: Create comprehensive review checklist

        Args:
            validation_strategy: Validation strategy to base checklist on
            include_standards: Include code standards checks

        Returns:
            List of review checklist items

        Raises:
            PipelineValidationError: If checklist generation fails

        Example:
            checklist = integration.generate_review_checklist(strategy)
        """
        try:
            checklist = []

            # Always include basic checks
            checklist.extend([
                "Code implements all requirements correctly",
                "No hallucinated functions or imports",
                "Proper error handling for edge cases",
                "Type safety and null pointer safety",
            ])

            # Add code standards checks
            if include_standards:
                checklist.extend([
                    "No nested if statements (use guard clauses)",
                    "No elif chains with 3+ branches (use dispatch tables)",
                    "Functions have single responsibility",
                    "Clear variable and function names",
                ])

            # Add technique-specific checks
            if "static_analysis" in validation_strategy.techniques:
                checklist.append("Static analysis checks pass (no linting errors)")

            if "rag_validation" in validation_strategy.techniques:
                checklist.append("Code follows established patterns from codebase")

            if "self_critique" in validation_strategy.techniques:
                checklist.append("Code has been self-reviewed for logical errors")

            if "property_tests" in validation_strategy.techniques:
                checklist.append("Edge cases are properly handled")

            if "formal_specs" in validation_strategy.techniques:
                checklist.append("Code matches formal specifications")

            # Add security checks for critical code
            if validation_strategy.risk_level.value in ["high", "critical"]:
                checklist.extend([
                    "No security vulnerabilities (SQL injection, XSS, etc.)",
                    "Proper authentication and authorization",
                    "Sensitive data is properly protected",
                ])

            return checklist

        except Exception as e:
            raise wrap_exception(
                e,
                PipelineValidationError,
                "Failed to generate review checklist",
                {
                    "profile": validation_strategy.profile.value,
                    "risk_level": validation_strategy.risk_level.value,
                    "include_standards": include_standards
                }
            )

    def create_review_prompt(
        self,
        code_to_review: str,
        task_description: str,
        validation_strategy: ValidationStrategy
    ) -> str:
        """
        Create complete code review prompt with validation awareness.

        WHY: Complete prompt includes all necessary context
        RESPONSIBILITY: Combine code, task, and validation info

        Args:
            code_to_review: Code to be reviewed
            task_description: Description of what code should do
            validation_strategy: Validation strategy to use

        Returns:
            Complete review prompt

        Raises:
            PipelineValidationError: If prompt creation fails

        Example:
            prompt = integration.create_review_prompt(
                code=code,
                task_description="Implement authentication",
                validation_strategy=strategy
            )
        """
        try:
            # Generate checklist
            checklist = self.generate_review_checklist(validation_strategy)

            # Create review prompt with validation awareness
            return generate_code_review_prompt(
                code_to_review=code_to_review,
                review_checklist=checklist,
                validation_strategy=validation_strategy
            )
        except PipelineValidationError:
            raise
        except Exception as e:
            raise wrap_exception(
                e,
                PipelineValidationError,
                "Failed to create review prompt",
                {
                    "code_length": len(code_to_review),
                    "task_description": task_description[:100] if task_description else None
                }
            )


# Convenience singleton instance
_code_review_validation_instance: Optional[CodeReviewValidationIntegration] = None


def get_code_review_validation_integration(
    logger: Optional[Any] = None
) -> CodeReviewValidationIntegration:
    """
    Get singleton code review validation integration instance.

    Args:
        logger: Optional logger

    Returns:
        Shared CodeReviewValidationIntegration instance
    """
    global _code_review_validation_instance

    if _code_review_validation_instance is None:
        _code_review_validation_instance = CodeReviewValidationIntegration(logger=logger)

    return _code_review_validation_instance


def get_code_review_validation_strategy(
    code_size: int,
    is_critical: bool = False,
    has_tests: bool = False,
    dependencies_count: int = 0,
    logger: Optional[Any] = None
) -> ValidationStrategy:
    """
    Convenience function to get validation strategy for code review.

    Args:
        code_size: Size of code being reviewed
        is_critical: Whether code is critical
        has_tests: Whether code has tests
        dependencies_count: Number of dependencies
        logger: Optional logger

    Returns:
        ValidationStrategy for code review

    Raises:
        PipelineValidationError: If strategy retrieval fails

    Example:
        strategy = get_code_review_validation_strategy(
            code_size=500,
            is_critical=True,
            has_tests=True
        )
    """
    try:
        integration = get_code_review_validation_integration(logger=logger)

        return integration.get_validation_strategy_for_review(
            code_size=code_size,
            is_critical=is_critical,
            has_tests=has_tests,
            dependencies_count=dependencies_count
        )
    except PipelineValidationError:
        raise
    except Exception as e:
        raise wrap_exception(
            e,
            PipelineValidationError,
            "Failed to get code review validation strategy",
            {
                "code_size": code_size,
                "is_critical": is_critical,
                "has_tests": has_tests
            }
        )


def enhance_code_review_with_validation(
    review_prompt: str,
    code_size: int,
    is_critical: bool = False,
    has_tests: bool = False,
    logger: Optional[Any] = None
) -> str:
    """
    Convenience function to enhance code review prompt with validation.

    Args:
        review_prompt: Original review prompt
        code_size: Size of code being reviewed
        is_critical: Whether code is critical
        has_tests: Whether code has tests
        logger: Optional logger

    Returns:
        Enhanced review prompt with validation awareness

    Raises:
        PipelineValidationError: If prompt enhancement fails

    Example:
        enhanced_prompt = enhance_code_review_with_validation(
            review_prompt="Review this authentication code",
            code_size=500,
            is_critical=True,
            has_tests=True
        )
    """
    try:
        integration = get_code_review_validation_integration(logger=logger)

        # Get validation strategy
        strategy = integration.get_validation_strategy_for_review(
            code_size=code_size,
            is_critical=is_critical,
            has_tests=has_tests
        )

        # Enhance prompt
        return integration.enhance_review_prompt_with_validation(
            base_prompt=review_prompt,
            validation_strategy=strategy,
            include_code_standards=True
        )
    except PipelineValidationError:
        raise
    except Exception as e:
        raise wrap_exception(
            e,
            PipelineValidationError,
            "Failed to enhance code review with validation",
            {
                "prompt_length": len(review_prompt),
                "code_size": code_size,
                "is_critical": is_critical
            }
        )
