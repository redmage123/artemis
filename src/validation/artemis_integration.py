#!/usr/bin/env python3
"""
Artemis Integration for Anti-Hallucination Orchestrator

WHY: Bridge between Artemis workflow and intelligent validation strategy selection
RESPONSIBILITY: Convert Artemis task context to validation context, apply strategies
PATTERNS: Adapter (convert Artemis context), Facade (simplify orchestrator usage)

This module integrates the intelligent anti-hallucination orchestrator with Artemis
code generation and review workflows. It automatically selects optimal validation
strategies based on task characteristics.

Integration Points:
- ValidatedDeveloperMixin: Intelligent validation during code generation
- CodeReviewStage: Intelligent validation during code review
- Other stages: Future integration for refactoring, bug fixes, etc.

Example:
    from validation.artemis_integration import get_validation_strategy_for_task

    # During code generation
    strategy = get_validation_strategy_for_task(
        task_type="code_generation",
        code_size=150,
        is_critical=False,
        has_tests=True,
        dependencies=5
    )

    # Apply strategy
    print(f"Using {strategy.profile.value} validation")
    print(f"Techniques: {', '.join(strategy.techniques)}")
    print(f"Expected reduction: {strategy.expected_reduction:.1%}")
"""

from typing import Optional, Dict, Any
from pathlib import Path

from artemis_logger import get_logger
from validation import (
    AntiHallucinationOrchestrator,
    ValidationProfile,
    RiskLevel,
    TaskType,
    TaskContext,
    ValidationStrategy,
)


class ArtemisValidationIntegration:
    """
    Integrates intelligent validation orchestration with Artemis workflows.

    WHY: Artemis tasks need context-aware validation strategy selection
    RESPONSIBILITY: Convert Artemis task info to validation context, select strategy
    PATTERNS: Adapter, Facade, Singleton
    """

    def __init__(self, logger: Optional[Any] = None):
        """
        Initialize Artemis validation integration.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or get_logger("validation_integration")
        self.orchestrator = AntiHallucinationOrchestrator(logger=self.logger)
        self.logger.info("Artemis Validation Integration initialized")

    def get_strategy_for_code_generation(
        self,
        code_size: int,
        is_critical: bool = False,
        has_tests: bool = False,
        dependencies_count: int = 0,
        time_budget_ms: Optional[float] = None
    ) -> ValidationStrategy:
        """
        Get validation strategy for code generation task.

        WHY: Code generation is the most common hallucination source
        RESPONSIBILITY: Create TaskContext, select strategy

        Args:
            code_size: Estimated lines of code to generate
            is_critical: Whether this is critical infrastructure
            has_tests: Whether tests exist/will be generated
            dependencies_count: Number of dependencies
            time_budget_ms: Optional time constraint

        Returns:
            ValidationStrategy with selected techniques

        Example:
            strategy = integration.get_strategy_for_code_generation(
                code_size=200,
                is_critical=False,
                has_tests=True,
                dependencies_count=5
            )
        """
        context = TaskContext(
            task_type=TaskType.CODE_GENERATION,
            code_complexity=code_size,
            is_critical=is_critical,
            has_tests=has_tests,
            dependencies_count=dependencies_count,
            time_budget_ms=time_budget_ms
        )

        strategy = self.orchestrator.select_strategy(context)
        self._log_strategy_selection(strategy, "code_generation")
        return strategy

    def get_strategy_for_code_review(
        self,
        code_size: int,
        is_critical: bool = False,
        has_tests: bool = False,
        dependencies_count: int = 0,
        time_budget_ms: Optional[float] = None
    ) -> ValidationStrategy:
        """
        Get validation strategy for code review task.

        WHY: Code review needs different validation than generation
        RESPONSIBILITY: Create TaskContext for review, select strategy

        Args:
            code_size: Lines of code under review
            is_critical: Whether this is critical infrastructure
            has_tests: Whether tests exist
            dependencies_count: Number of dependencies
            time_budget_ms: Optional time constraint

        Returns:
            ValidationStrategy with selected techniques
        """
        context = TaskContext(
            task_type=TaskType.CODE_REVIEW,
            code_complexity=code_size,
            is_critical=is_critical,
            has_tests=has_tests,
            dependencies_count=dependencies_count,
            time_budget_ms=time_budget_ms
        )

        strategy = self.orchestrator.select_strategy(context)
        self._log_strategy_selection(strategy, "code_review")
        return strategy

    def get_strategy_for_bug_fix(
        self,
        code_size: int,
        is_critical: bool = False,
        has_tests: bool = False,
        dependencies_count: int = 0,
        time_budget_ms: Optional[float] = None
    ) -> ValidationStrategy:
        """
        Get validation strategy for bug fix task.

        WHY: Bug fixes are high-risk due to potential regression
        RESPONSIBILITY: Create TaskContext for bug fix, select strategy

        Args:
            code_size: Lines of code being fixed
            is_critical: Whether this is critical infrastructure
            has_tests: Whether tests exist
            dependencies_count: Number of dependencies
            time_budget_ms: Optional time constraint

        Returns:
            ValidationStrategy with selected techniques
        """
        context = TaskContext(
            task_type=TaskType.BUG_FIX,
            code_complexity=code_size,
            is_critical=is_critical,
            has_tests=has_tests,
            dependencies_count=dependencies_count,
            time_budget_ms=time_budget_ms
        )

        strategy = self.orchestrator.select_strategy(context)
        self._log_strategy_selection(strategy, "bug_fix")
        return strategy

    def get_strategy_for_refactoring(
        self,
        code_size: int,
        is_critical: bool = False,
        has_tests: bool = False,
        dependencies_count: int = 0,
        time_budget_ms: Optional[float] = None
    ) -> ValidationStrategy:
        """
        Get validation strategy for refactoring task.

        WHY: Refactoring can introduce subtle bugs
        RESPONSIBILITY: Create TaskContext for refactoring, select strategy

        Args:
            code_size: Lines of code being refactored
            is_critical: Whether this is critical infrastructure
            has_tests: Whether tests exist
            dependencies_count: Number of dependencies
            time_budget_ms: Optional time constraint

        Returns:
            ValidationStrategy with selected techniques
        """
        context = TaskContext(
            task_type=TaskType.REFACTORING,
            code_complexity=code_size,
            is_critical=is_critical,
            has_tests=has_tests,
            dependencies_count=dependencies_count,
            time_budget_ms=time_budget_ms
        )

        strategy = self.orchestrator.select_strategy(context)
        self._log_strategy_selection(strategy, "refactoring")
        return strategy

    def get_strategy_from_file_analysis(
        self,
        file_path: Path,
        task_type_str: str = "code_generation",
        is_critical: bool = False,
        time_budget_ms: Optional[float] = None
    ) -> ValidationStrategy:
        """
        Analyze file and get appropriate validation strategy.

        WHY: Auto-detect complexity and dependencies from existing code
        RESPONSIBILITY: Analyze file, extract metrics, select strategy

        Args:
            file_path: Path to file to analyze
            task_type_str: Type of task ("code_generation", "code_review", etc.)
            is_critical: Whether this is critical infrastructure
            time_budget_ms: Optional time constraint

        Returns:
            ValidationStrategy based on file analysis
        """
        # Guard: File doesn't exist
        if not file_path.exists():
            self.logger.warning(f"File not found: {file_path}, using default context")
            code_size = 100
            dependencies_count = 0
            has_tests = False
        else:
            # Analyze file
            code_size = self._count_lines(file_path)
            dependencies_count = self._count_dependencies(file_path)
            has_tests = self._check_has_tests(file_path)

        # Map string to TaskType
        task_type_map = {
            "code_generation": TaskType.CODE_GENERATION,
            "code_review": TaskType.CODE_REVIEW,
            "bug_fix": TaskType.BUG_FIX,
            "refactoring": TaskType.REFACTORING,
            "feature_addition": TaskType.FEATURE_ADDITION,
            "documentation": TaskType.DOCUMENTATION,
            "testing": TaskType.TESTING,
        }

        task_type = task_type_map.get(task_type_str, TaskType.CODE_GENERATION)

        context = TaskContext(
            task_type=task_type,
            code_complexity=code_size,
            is_critical=is_critical,
            has_tests=has_tests,
            dependencies_count=dependencies_count,
            time_budget_ms=time_budget_ms
        )

        strategy = self.orchestrator.select_strategy(context)
        self._log_strategy_selection(strategy, task_type_str, file_path)
        return strategy

    def record_validation_failure(
        self,
        task_type_str: str,
        failed_technique: str,
        error_pattern: str
    ) -> None:
        """
        Record validation failure for historical learning.

        WHY: Learn from failures to improve future strategy selection
        RESPONSIBILITY: Delegate to orchestrator for historical tracking

        Args:
            task_type_str: Type of task that failed
            failed_technique: Which technique failed to catch the issue
            error_pattern: Pattern of error (e.g., "null_pointer", "type_mismatch")

        Example:
            integration.record_validation_failure(
                task_type_str="code_generation",
                failed_technique="static_analysis",
                error_pattern="null_pointer"
            )
        """
        task_type_map = {
            "code_generation": TaskType.CODE_GENERATION,
            "code_review": TaskType.CODE_REVIEW,
            "bug_fix": TaskType.BUG_FIX,
            "refactoring": TaskType.REFACTORING,
            "feature_addition": TaskType.FEATURE_ADDITION,
        }

        task_type = task_type_map.get(task_type_str, TaskType.CODE_GENERATION)
        self.orchestrator.record_failure(task_type, failed_technique, error_pattern)

    def _count_lines(self, file_path: Path) -> int:
        """Count lines of code (excluding blanks and comments)."""
        try:
            content = file_path.read_text()
            lines = [
                line for line in content.splitlines()
                if line.strip() and not line.strip().startswith('#')
            ]
            return len(lines)
        except Exception as e:
            self.logger.warning(f"Error counting lines in {file_path}: {e}")
            return 100  # Default estimate

    def _count_dependencies(self, file_path: Path) -> int:
        """Count import statements as proxy for dependencies."""
        try:
            content = file_path.read_text()
            imports = [
                line for line in content.splitlines()
                if line.strip().startswith(('import ', 'from '))
            ]
            return len(imports)
        except Exception as e:
            self.logger.warning(f"Error counting dependencies in {file_path}: {e}")
            return 0

    def _check_has_tests(self, file_path: Path) -> bool:
        """Check if test file exists for this file."""
        # Check for test file in same directory
        test_patterns = [
            f"test_{file_path.stem}.py",
            f"{file_path.stem}_test.py",
            f"tests/test_{file_path.stem}.py",
        ]

        for pattern in test_patterns:
            test_path = file_path.parent / pattern
            if test_path.exists():
                return True

        return False

    def _log_strategy_selection(
        self,
        strategy: ValidationStrategy,
        task_type_str: str,
        file_path: Optional[Path] = None
    ) -> None:
        """Log strategy selection details."""
        file_info = f" for {file_path.name}" if file_path else ""
        self.logger.info(f"Validation strategy selected for {task_type_str}{file_info}:")
        self.logger.info(f"  Risk: {strategy.risk_level.value}")
        self.logger.info(f"  Profile: {strategy.profile.value}")
        self.logger.info(f"  Techniques: {', '.join(strategy.techniques)}")
        self.logger.info(f"  Expected reduction: {strategy.expected_reduction:.1%}")
        self.logger.info(f"  Estimated time: {strategy.estimated_time_ms:.0f}ms")


# Convenience singleton instance
_integration_instance: Optional[ArtemisValidationIntegration] = None


def get_validation_integration(logger: Optional[Any] = None) -> ArtemisValidationIntegration:
    """
    Get singleton validation integration instance.

    WHY: Avoid creating multiple orchestrator instances
    RESPONSIBILITY: Lazy initialization of singleton

    Args:
        logger: Optional logger instance

    Returns:
        Shared ArtemisValidationIntegration instance
    """
    global _integration_instance

    if _integration_instance is None:
        _integration_instance = ArtemisValidationIntegration(logger=logger)

    return _integration_instance


# Convenience functions for quick usage
def get_validation_strategy_for_task(
    task_type: str,
    code_size: int,
    is_critical: bool = False,
    has_tests: bool = False,
    dependencies: int = 0,
    time_budget_ms: Optional[float] = None,
    logger: Optional[Any] = None
) -> ValidationStrategy:
    """
    Quick function to get validation strategy for any task type.

    WHY: Simplified API for common use case
    RESPONSIBILITY: Delegate to appropriate integration method

    Args:
        task_type: "code_generation", "code_review", "bug_fix", etc.
        code_size: Lines of code
        is_critical: Whether critical infrastructure
        has_tests: Whether tests exist
        dependencies: Number of dependencies
        time_budget_ms: Optional time constraint
        logger: Optional logger

    Returns:
        ValidationStrategy

    Example:
        strategy = get_validation_strategy_for_task(
            task_type="code_generation",
            code_size=150,
            is_critical=False,
            has_tests=True,
            dependencies=5
        )
    """
    integration = get_validation_integration(logger)

    # Map task type to appropriate method
    if task_type == "code_generation":
        return integration.get_strategy_for_code_generation(
            code_size=code_size,
            is_critical=is_critical,
            has_tests=has_tests,
            dependencies_count=dependencies,
            time_budget_ms=time_budget_ms
        )

    if task_type == "code_review":
        return integration.get_strategy_for_code_review(
            code_size=code_size,
            is_critical=is_critical,
            has_tests=has_tests,
            dependencies_count=dependencies,
            time_budget_ms=time_budget_ms
        )

    if task_type == "bug_fix":
        return integration.get_strategy_for_bug_fix(
            code_size=code_size,
            is_critical=is_critical,
            has_tests=has_tests,
            dependencies_count=dependencies,
            time_budget_ms=time_budget_ms
        )

    if task_type == "refactoring":
        return integration.get_strategy_for_refactoring(
            code_size=code_size,
            is_critical=is_critical,
            has_tests=has_tests,
            dependencies_count=dependencies,
            time_budget_ms=time_budget_ms
        )

    # Default to code generation
    return integration.get_strategy_for_code_generation(
        code_size=code_size,
        is_critical=is_critical,
        has_tests=has_tests,
        dependencies_count=dependencies,
        time_budget_ms=time_budget_ms
    )
