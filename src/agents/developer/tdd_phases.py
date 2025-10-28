"""
Module: agents/developer/tdd_phases.py

WHY: Implement Red-Green-Refactor TDD workflow phases.
RESPONSIBILITY: Orchestrate TDD phases with retry logic and phase-specific validation.
PATTERNS: Template Method (phase structure), Strategy Pattern (retry vs standard), Guard Clauses.

This module handles:
- RED phase: Generate failing tests
- GREEN phase: Implement code to pass tests (with retry coordination)
- REFACTOR phase: Improve code quality while keeping tests green
- Phase-specific logging and validation

EXTRACTED FROM: standalone_developer_agent.py (lines 635-2600, simplified)
"""

from pathlib import Path
from typing import Dict, List, Optional
from artemis_stage_interface import LoggerInterface
from agents.developer.models import PhaseResult


class TDDPhases:
    """
    Orchestrates Red-Green-Refactor TDD workflow

    WHY: Centralize TDD phase execution with consistent structure
    PATTERNS: Template Method, Strategy Pattern, Guard Clauses
    """

    def __init__(
        self,
        file_manager,
        test_runner,
        llm_wrapper,
        logger: Optional[LoggerInterface] = None,
        retry_coordinator=None
    ):
        """
        Initialize TDD phases orchestrator

        Args:
            file_manager: FileManager instance for file I/O
            test_runner: DeveloperTestRunner instance for test execution
            llm_wrapper: LLMClientWrapper instance for LLM calls
            logger: Optional logger
            retry_coordinator: Optional RetryCoordinator for intelligent retry
        """
        self.file_manager = file_manager
        self.test_runner = test_runner
        self.llm_wrapper = llm_wrapper
        self.logger = logger
        self.retry_coordinator = retry_coordinator

    def execute_red_phase(
        self,
        task_title: str,
        task_description: str,
        adr_content: str,
        output_dir: Path,
        context: Dict
    ) -> PhaseResult:
        """
        Execute RED phase: Generate failing tests

        Args:
            task_title: Task title
            task_description: Task description
            adr_content: ADR content
            output_dir: Output directory
            context: Execution context with developer_prompt, kg_context, etc.

        Returns:
            PhaseResult with test files and test results
        """
        self._log_info("🔴 RED Phase: Generating failing tests...")

        # Generate test files using LLM
        test_files = self._red_phase_generate_tests(
            developer_prompt=context['developer_prompt'],
            task_title=task_title,
            task_description=task_description,
            adr_content=adr_content,
            kg_context=context.get('kg_context'),
            code_review_feedback=context.get('code_review_feedback')
        )

        # Write test files
        self.file_manager.write_test_files(test_files, output_dir)

        # Run tests - they should FAIL (red phase)
        test_results = self.test_runner.run_tests(output_dir)

        self._log_red_phase_results(test_results)

        return PhaseResult(
            files=test_files,
            test_results=test_results,
            status="completed",
            phase_name="red"
        )

    def execute_green_phase(
        self,
        task_title: str,
        task_description: str,
        adr_content: str,
        output_dir: Path,
        context: Dict,
        red_results: PhaseResult
    ) -> PhaseResult:
        """
        Execute GREEN phase: Implement code to pass tests.

        WHY: Uses retry coordinator for intelligent retry with prompt refinement.
             Falls back to standard generation if retry coordinator unavailable.

        Args:
            task_title: Task title
            task_description: Task description
            adr_content: ADR content
            output_dir: Output directory
            context: Execution context
            red_results: Results from RED phase

        Returns:
            PhaseResult with implementation files and test results
        """
        self._log_info("🟢 GREEN Phase: Implementing code to pass tests...")

        # Strategy pattern: Use retry coordinator if available
        if self.retry_coordinator:
            return self._green_phase_with_retry(
                task_title, task_description, adr_content, output_dir, context, red_results
            )

        # Fallback: Standard generation without retry
        return self._execute_green_phase_fallback(
            task_title, task_description, adr_content, output_dir, context, red_results
        )

    def execute_refactor_phase(
        self,
        task_title: str,
        output_dir: Path,
        context: Dict,
        green_results: PhaseResult
    ) -> PhaseResult:
        """
        Execute REFACTOR phase: Improve code quality while keeping tests green

        Args:
            task_title: Task title
            output_dir: Output directory
            context: Execution context
            green_results: Results from GREEN phase

        Returns:
            PhaseResult with refactored files and test results
        """
        self._log_info("🔵 REFACTOR Phase: Improving code quality...")

        # Generate refactored files using LLM
        refactored_files = self._refactor_phase_improve(
            developer_prompt=context['developer_prompt'],
            task_title=task_title,
            implementation_files=green_results.files,
            test_results=green_results.test_results,
            refactoring_instructions=context.get('refactoring_instructions')
        )

        # Write refactored files
        self.file_manager.write_implementation_only(refactored_files, output_dir)

        # Run tests again - they should STILL PASS
        test_results = self.test_runner.run_tests(output_dir)

        self._log_refactor_phase_results(test_results)

        return PhaseResult(
            files=refactored_files,
            test_results=test_results,
            status="completed",
            phase_name="refactor"
        )

    # ========== Private Phase Implementation Methods ==========

    def _execute_green_phase_fallback(
        self,
        task_title: str,
        task_description: str,
        adr_content: str,
        output_dir: Path,
        context: Dict,
        red_results: PhaseResult
    ) -> PhaseResult:
        """Execute green phase without retry coordinator"""
        implementation_files = self._green_phase_implement(
            developer_prompt=context['developer_prompt'],
            task_title=task_title,
            task_description=task_description,
            adr_content=adr_content,
            test_files=red_results.files,
            red_test_results=red_results.test_results,
            kg_context=context.get('kg_context'),
            example_slides=context.get('example_slides'),
            code_review_feedback=context.get('code_review_feedback')
        )

        # Write implementation files
        self.file_manager.write_implementation_only(implementation_files, output_dir)

        # Run tests - they should PASS now
        test_results = self.test_runner.run_tests(output_dir)

        self._log_green_phase_results(test_results)

        return PhaseResult(
            files=implementation_files,
            test_results=test_results,
            status="completed",
            phase_name="green"
        )

    def _green_phase_with_retry(
        self,
        task_title: str,
        task_description: str,
        adr_content: str,
        output_dir: Path,
        context: Dict,
        red_results: PhaseResult
    ) -> PhaseResult:
        """
        Execute green phase with intelligent retry coordination

        Uses RetryCoordinator for prompt refinement on test failures
        """
        self._log_info("🔁 Using intelligent retry coordination...")

        # Use retry coordinator to generate implementation with retries
        retry_result = self.retry_coordinator.execute_with_retry(
            generate_fn=lambda: self._green_phase_implement(
                developer_prompt=context['developer_prompt'],
                task_title=task_title,
                task_description=task_description,
                adr_content=adr_content,
                test_files=red_results.files,
                red_test_results=red_results.test_results,
                kg_context=context.get('kg_context'),
                example_slides=context.get('example_slides'),
                code_review_feedback=context.get('code_review_feedback')
            ),
            validate_fn=lambda impl_files: self._validate_implementation(impl_files, output_dir),
            max_retries=3
        )

        # Write final implementation
        self.file_manager.write_implementation_only(retry_result.final_files, output_dir)

        # Run final tests
        test_results = self.test_runner.run_tests(output_dir)

        self._log_green_phase_results(test_results)
        self._log_retry_statistics(retry_result)

        return PhaseResult(
            files=retry_result.final_files,
            test_results=test_results,
            status="completed" if test_results.get('failed', 0) == 0 else "partial",
            phase_name="green"
        )

    def _red_phase_generate_tests(
        self,
        developer_prompt: str,
        task_title: str,
        task_description: str,
        adr_content: str,
        kg_context: Optional[Dict],
        code_review_feedback: Optional[str]
    ) -> List[Dict]:
        """
        RED Phase: Generate failing tests using LLM

        Args:
            developer_prompt: Developer prompt template
            task_title: Task title
            task_description: Task description
            adr_content: ADR content
            kg_context: Knowledge graph context
            code_review_feedback: Code review feedback

        Returns:
            List of test file dicts
        """
        prompt = self._build_red_phase_prompt(
            developer_prompt, task_title, task_description, adr_content,
            kg_context, code_review_feedback
        )

        response = self.llm_wrapper.call_llm(prompt)
        implementation = self.llm_wrapper.parse_implementation(response.content)

        return implementation.get("test_files", [])

    def _green_phase_implement(
        self,
        developer_prompt: str,
        task_title: str,
        task_description: str,
        adr_content: str,
        test_files: List[Dict],
        red_test_results: Dict,
        kg_context: Optional[Dict],
        example_slides: Optional[str],
        code_review_feedback: Optional[str]
    ) -> List[Dict]:
        """
        GREEN Phase: Implement code to pass tests

        Args:
            developer_prompt: Developer prompt template
            task_title: Task title
            task_description: Task description
            adr_content: ADR content
            test_files: Test files from RED phase
            red_test_results: RED phase test results
            kg_context: Knowledge graph context
            example_slides: Example slides content
            code_review_feedback: Code review feedback

        Returns:
            List of implementation file dicts
        """
        prompt = self._build_green_phase_prompt(
            developer_prompt, task_title, task_description, adr_content,
            test_files, red_test_results, kg_context, example_slides, code_review_feedback
        )

        response = self.llm_wrapper.call_llm(prompt)
        implementation = self.llm_wrapper.parse_implementation(response.content)

        return implementation.get("implementation_files", [])

    def _refactor_phase_improve(
        self,
        developer_prompt: str,
        task_title: str,
        implementation_files: List[Dict],
        test_results: Dict,
        refactoring_instructions: Optional[str]
    ) -> List[Dict]:
        """
        REFACTOR Phase: Improve code quality

        Args:
            developer_prompt: Developer prompt template
            task_title: Task title
            implementation_files: Implementation files from GREEN phase
            test_results: GREEN phase test results
            refactoring_instructions: Refactoring instructions from RAG

        Returns:
            List of refactored file dicts
        """
        prompt = self._build_refactor_phase_prompt(
            developer_prompt, task_title, implementation_files,
            test_results, refactoring_instructions
        )

        response = self.llm_wrapper.call_llm(prompt)
        implementation = self.llm_wrapper.parse_implementation(response.content)

        return implementation.get("implementation_files", [])

    # ========== Prompt Building Methods (Placeholders) ==========

    def _build_red_phase_prompt(self, *args, **kwargs) -> str:
        """Build prompt for RED phase (placeholder - implement full prompt)"""
        return "Generate failing tests..."

    def _build_green_phase_prompt(self, *args, **kwargs) -> str:
        """Build prompt for GREEN phase (placeholder - implement full prompt)"""
        return "Implement code to pass tests..."

    def _build_refactor_phase_prompt(self, *args, **kwargs) -> str:
        """Build prompt for REFACTOR phase (placeholder - implement full prompt)"""
        return "Refactor code to improve quality..."

    # ========== Validation and Logging Methods ==========

    def _validate_implementation(self, impl_files: List[Dict], output_dir: Path) -> bool:
        """Validate implementation by running tests"""
        self.file_manager.write_implementation_only(impl_files, output_dir)
        test_results = self.test_runner.run_tests(output_dir)
        return test_results.get('failed', 0) == 0

    def _log_red_phase_results(self, test_results: Dict):
        """Log RED phase results"""
        # Guard: no logger
        if not self.logger:
            return

        failed_count = test_results.get('failed', 0)

        if failed_count > 0:
            self.logger.log(f"✅ RED Phase complete: {failed_count} tests failing (expected)", "INFO")
        else:
            self.logger.log("⚠️  Warning: No tests failed in RED phase (unusual)", "WARNING")

    def _log_green_phase_results(self, test_results: Dict):
        """Log GREEN phase results"""
        # Guard: no logger
        if not self.logger:
            return

        passed_count = test_results.get('passed', 0)
        failed_count = test_results.get('failed', 0)

        if failed_count == 0:
            self.logger.log(f"✅ GREEN Phase complete: All {passed_count} tests passing", "SUCCESS")
        else:
            self.logger.log(f"⚠️  GREEN Phase incomplete: {failed_count} tests still failing", "WARNING")

    def _log_refactor_phase_results(self, test_results: Dict):
        """Log REFACTOR phase results"""
        # Guard: no logger
        if not self.logger:
            return

        passed_count = test_results.get('passed', 0)
        failed_count = test_results.get('failed', 0)

        if failed_count == 0:
            self.logger.log(f"✅ REFACTOR Phase complete: All {passed_count} tests still passing", "SUCCESS")
        else:
            self.logger.log(f"❌ REFACTOR Phase failed: {failed_count} tests broken during refactor", "ERROR")

    def _log_retry_statistics(self, retry_result):
        """Log retry coordination statistics"""
        if self.logger and hasattr(retry_result, 'retry_count'):
            self.logger.log(
                f"🔁 Retry statistics: {retry_result.retry_count} attempts, "
                f"final success: {retry_result.success}",
                "INFO"
            )

    def _log_info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.log(message, "INFO")


__all__ = [
    "TDDPhases"
]
