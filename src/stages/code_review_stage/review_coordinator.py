#!/usr/bin/env python3
"""
Multi-Developer Review Coordinator

WHY: Coordinate reviews across multiple developer implementations
RESPONSIBILITY: Orchestrate individual developer reviews and progress tracking
PATTERNS: Coordinator Pattern, Single Responsibility, Guard Clauses
"""

import os
import tempfile
from typing import Dict, List, Any, Optional, Callable

from artemis_stage_interface import LoggerInterface
from code_review_agent import CodeReviewAgent
from rag_agent import RAGAgent
from .code_standards_reviewer import CodeStandardsReviewer
from .advanced_validation_reviewer import AdvancedValidationReviewer


class MultiDeveloperReviewCoordinator:
    """
    Coordinate code reviews across multiple developer implementations.

    WHY: Separate multi-developer orchestration from single review logic
    RESPONSIBILITY: Manage review workflow for multiple developers
    PATTERNS: Coordinator Pattern, Iterator Pattern
    """

    def __init__(
        self,
        logger: LoggerInterface,
        llm_provider: str,
        llm_model: Optional[str],
        rag_agent: RAGAgent,
        code_review_dir: str,
        debug_component: Any = None,
        enable_code_standards: bool = True,
        code_standards_severity: str = "warning",
        enable_advanced_validation: bool = True,
        enable_static_analysis: bool = True,
        enable_property_tests: bool = True,
        max_complexity: int = 10
    ):
        """
        Initialize review coordinator.

        Args:
            logger: Logger interface
            llm_provider: LLM provider (openai/anthropic)
            llm_model: Specific model to use
            rag_agent: RAG agent for review storage
            code_review_dir: Directory for review output
            debug_component: Optional debug mixin component
            enable_code_standards: Whether to run code standards validation
            code_standards_severity: Minimum severity for code standards ("info", "warning", "critical")
            enable_advanced_validation: Whether to run advanced validation (static analysis + property tests)
            enable_static_analysis: Run static analysis (mypy, ruff, radon)
            enable_property_tests: Generate property-based tests
            max_complexity: Maximum cyclomatic complexity allowed
        """
        self.logger = logger
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.rag_agent = rag_agent
        self.code_review_dir = code_review_dir
        self.debug_component = debug_component

        # Initialize code standards reviewer
        # Check environment variable to enable/disable
        enable_from_env = os.getenv("ARTEMIS_CODE_STANDARDS_ENABLED", "true").lower() == "true"
        self.enable_code_standards = enable_code_standards and enable_from_env

        severity_from_env = os.getenv("ARTEMIS_CODE_STANDARDS_SEVERITY", code_standards_severity)

        self.code_standards_reviewer = CodeStandardsReviewer(
            logger=logger,
            severity_threshold=severity_from_env,
            enabled=self.enable_code_standards
        )

        # Initialize advanced validation reviewer
        # Check environment variable to enable/disable
        enable_adv_from_env = os.getenv("ARTEMIS_ADVANCED_VALIDATION_ENABLED", "true").lower() == "true"
        self.enable_advanced_validation = enable_advanced_validation and enable_adv_from_env

        enable_static_from_env = os.getenv("ARTEMIS_STATIC_ANALYSIS_ENABLED", str(enable_static_analysis)).lower() == "true"
        enable_property_from_env = os.getenv("ARTEMIS_PROPERTY_TESTS_ENABLED", str(enable_property_tests)).lower() == "true"
        max_complexity_from_env = int(os.getenv("ARTEMIS_MAX_COMPLEXITY", str(max_complexity)))

        self.advanced_validation_reviewer = AdvancedValidationReviewer(
            logger=logger,
            enable_static_analysis=enable_static_from_env and self.enable_advanced_validation,
            enable_property_tests=enable_property_from_env and self.enable_advanced_validation,
            static_analysis_config={
                'enable_type_checking': True,
                'enable_linting': True,
                'enable_complexity_check': True,
                'max_complexity': max_complexity_from_env
            }
        )

    def review_all_developers(
        self,
        developers: List[Dict],
        card_id: str,
        task_title: str,
        task_description: str,
        progress_callback: Optional[Callable] = None,
        notification_manager: Optional[Any] = None
    ) -> List[Dict]:
        """
        Review all developer implementations.

        WHY: Main coordination method for multi-developer reviews
        RESPONSIBILITY: Iterate through developers and collect results
        PATTERN: Iterator Pattern, Collector Pattern

        Args:
            developers: List of developer results to review
            card_id: Card identifier
            task_title: Task title
            task_description: Task description
            progress_callback: Optional callback for progress updates
            notification_manager: Optional notification manager

        Returns:
            List of review results for all developers
        """
        review_results = []

        for i, dev_result in enumerate(developers):
            result = self._review_single_developer(
                index=i,
                dev_result=dev_result,
                total_developers=len(developers),
                card_id=card_id,
                task_title=task_title,
                task_description=task_description,
                progress_callback=progress_callback,
                notification_manager=notification_manager
            )

            review_results.append(result)

        return review_results

    def _review_single_developer(
        self,
        index: int,
        dev_result: Dict,
        total_developers: int,
        card_id: str,
        task_title: str,
        task_description: str,
        progress_callback: Optional[Callable] = None,
        notification_manager: Optional[Any] = None
    ) -> Dict:
        """
        Review a single developer's implementation.

        WHY: Encapsulate single developer review logic
        RESPONSIBILITY: Execute review for one developer
        PATTERN: Single Responsibility, Guard Clauses

        Args:
            index: Developer index in list
            dev_result: Developer result dictionary
            total_developers: Total number of developers
            card_id: Card identifier
            task_title: Task title
            task_description: Task description
            progress_callback: Optional callback for progress updates
            notification_manager: Optional notification manager

        Returns:
            Review result dictionary
        """
        developer_name = dev_result.get('developer', 'unknown')
        implementation_dir = dev_result.get('output_dir', f'{tempfile.gettempdir()}/{developer_name}/')

        # Update progress if callback provided
        if progress_callback:
            progress = 10 + ((index + 1) / total_developers) * 70
            progress_callback({
                "step": f"reviewing_{developer_name}",
                "progress_percent": int(progress),
                "current_developer": developer_name,
                "total_developers": total_developers
            })

        self.logger.log(f"\n{'='*60}", "INFO")
        self.logger.log(f"🔍 Reviewing {developer_name} implementation", "INFO")
        self.logger.log(f"{'='*60}", "INFO")

        # Notify review started
        if notification_manager:
            notification_manager.notify_review_started(card_id, developer_name, implementation_dir)

        # Create and run code review agent
        review_agent = CodeReviewAgent(
            developer_name=developer_name,
            llm_provider=self.llm_provider,
            llm_model=self.llm_model,
            logger=self.logger,
            rag_agent=self.rag_agent
        )

        review_result = review_agent.review_implementation(
            implementation_dir=implementation_dir,
            task_title=task_title,
            task_description=task_description,
            output_dir=self.code_review_dir
        )

        # Run code standards validation
        code_standards_result = self.code_standards_reviewer.review_developer_code(
            developer_name=developer_name,
            code_directory=implementation_dir
        )

        # Add code standards result to review result
        review_result['code_standards'] = code_standards_result

        # Run advanced validation (static analysis + property-based testing)
        advanced_validation_result = self._run_advanced_validation(
            developer_name=developer_name,
            implementation_dir=implementation_dir
        )

        # Add advanced validation result to review result
        review_result['advanced_validation'] = advanced_validation_result

        # Extract review metrics
        review_status = review_result.get('review_status', 'FAIL')
        critical_issues = review_result.get('critical_issues', 0)
        high_issues = review_result.get('high_issues', 0)
        overall_score = review_result.get('overall_score', 0)

        # Adjust review status if code standards failed
        if code_standards_result['enabled'] and not code_standards_result['passed']:
            self.logger.log(
                f"  ⚠️  Code standards violations detected - review may be affected",
                "WARNING"
            )
            # Optionally downgrade review status
            # review_status = "FAIL"  # Uncomment to make code standards failures block code

        # Log review summary
        self._log_review_summary(review_status, overall_score, critical_issues, high_issues)

        # Handle review outcome notifications
        if notification_manager:
            notification_manager.handle_review_outcome(
                review_status=review_status,
                developer_name=developer_name,
                card_id=card_id,
                overall_score=overall_score,
                critical_issues=critical_issues,
                high_issues=high_issues
            )

        return review_result

    def _log_review_summary(
        self,
        review_status: str,
        overall_score: int,
        critical_issues: int,
        high_issues: int
    ) -> None:
        """
        Log review summary metrics.

        WHY: Separate presentation logic
        PATTERN: Single Responsibility
        """
        self.logger.log(f"Review Status: {review_status}", "INFO")
        self.logger.log(f"Overall Score: {overall_score}/100", "INFO")
        self.logger.log(f"Critical Issues: {critical_issues}", "INFO")
        self.logger.log(f"High Issues: {high_issues}", "INFO")

    def _run_advanced_validation(
        self,
        developer_name: str,
        implementation_dir: str
    ) -> Dict:
        """
        Run advanced validation (static analysis + property-based testing).

        WHY: Separate advanced validation logic
        RESPONSIBILITY: Collect code files, run validation, aggregate results
        PATTERNS: Guard clauses, Single Responsibility

        Args:
            developer_name: Name of developer
            implementation_dir: Directory containing implementation

        Returns:
            Dict with advanced validation results
        """
        # Guard: Advanced validation disabled
        if not self.enable_advanced_validation:
            return {
                'enabled': False,
                'message': 'Advanced validation is disabled'
            }

        from pathlib import Path

        # Guard: Implementation directory doesn't exist
        impl_path = Path(implementation_dir)
        if not impl_path.exists():
            return {
                'enabled': True,
                'error': f'Implementation directory not found: {implementation_dir}',
                'results': []
            }

        # Find all Python files
        python_files = list(impl_path.rglob('*.py'))

        # Guard: No Python files found
        if not python_files:
            return {
                'enabled': True,
                'message': 'No Python files found to validate',
                'results': []
            }

        self.logger.log(f"\n🔬 Running advanced validation on {len(python_files)} file(s)...", "INFO")

        # Validate each file
        all_results = []
        for py_file in python_files:
            # Guard: Skip if file is too large (> 50KB)
            if py_file.stat().st_size > 50000:
                self.logger.log(f"  ⏭️  Skipping large file: {py_file.name}", "INFO")
                continue

            # Read file content
            try:
                code = py_file.read_text()
            except Exception as e:
                self.logger.log(f"  ⚠️  Failed to read {py_file.name}: {e}", "WARNING")
                continue

            # Guard: Skip empty files
            if not code.strip():
                continue

            # Run validation on this file
            file_result = self.advanced_validation_reviewer.review_code(
                code=code,
                developer_name=developer_name,
                language="python"
            )

            # Add file information
            file_result['file_path'] = str(py_file.relative_to(impl_path))
            file_result['file_name'] = py_file.name

            all_results.append(file_result)

        # Aggregate results
        return self._aggregate_advanced_validation_results(all_results)

    def _aggregate_advanced_validation_results(self, results: List[Dict]) -> Dict:
        """
        Aggregate advanced validation results from multiple files.

        WHY: Provide unified view of advanced validation
        RESPONSIBILITY: Summarize results across all files
        PATTERNS: Guard clauses

        Args:
            results: List of per-file validation results

        Returns:
            Aggregated results dictionary
        """
        # Guard: No results
        if not results:
            return {
                'enabled': True,
                'files_validated': 0,
                'overall_passed': True,
                'total_issues': 0,
                'results': []
            }

        # Count overall statistics
        total_files = len(results)
        files_passed = sum(1 for r in results if r.get('overall_passed', True))
        total_issues = sum(len(r.get('issues_found', [])) for r in results)

        # Collect all static analysis issues
        static_analysis_errors = 0
        static_analysis_warnings = 0

        for result in results:
            static = result.get('static_analysis')
            # Guard: Static analysis not present
            if not static:
                continue

            static_analysis_errors += static.get('error_count', 0)
            static_analysis_warnings += static.get('warning_count', 0)

        # Determine overall pass/fail
        overall_passed = files_passed == total_files and static_analysis_errors == 0

        # Create summary
        summary = self._create_advanced_validation_summary(
            total_files,
            files_passed,
            static_analysis_errors,
            static_analysis_warnings,
            total_issues
        )

        self.logger.log(f"\n{summary}", "INFO")

        return {
            'enabled': True,
            'files_validated': total_files,
            'files_passed': files_passed,
            'overall_passed': overall_passed,
            'static_analysis_errors': static_analysis_errors,
            'static_analysis_warnings': static_analysis_warnings,
            'total_issues': total_issues,
            'summary': summary,
            'results': results
        }

    def _create_advanced_validation_summary(
        self,
        total_files: int,
        files_passed: int,
        errors: int,
        warnings: int,
        total_issues: int
    ) -> str:
        """
        Create summary message for advanced validation.

        WHY: Provide human-readable summary
        RESPONSIBILITY: Format summary text
        PATTERNS: Guard clauses
        """
        # Guard: All passed
        if files_passed == total_files and errors == 0 and warnings == 0:
            return f"✅ Advanced validation: All {total_files} file(s) passed"

        # Guard: Has errors
        if errors > 0:
            return (
                f"❌ Advanced validation: {errors} error(s), {warnings} warning(s) "
                f"across {total_files} file(s)"
            )

        # Has warnings but no errors
        return (
            f"⚠️  Advanced validation: {warnings} warning(s) "
            f"across {total_files} file(s) (no errors)"
        )
