#!/usr/bin/env python3
"""
Code Review Stage - Review Execution Logic

WHY: Separate review execution from coordination and storage for better testability.
RESPONSIBILITY: Execute individual developer code reviews and aggregate results.
PATTERNS: Strategy pattern for review processing, Template method for review workflow.

This module contains the core logic for executing code reviews on developer
implementations, managing the review workflow, and aggregating results.
"""

import tempfile
from typing import Dict, List, Tuple

from code_review_agent import CodeReviewAgent
from .models import DeveloperReviewResult, ReviewMetrics, StageProgress
from .review_notifier import ReviewNotifier
from .storage_manager import ReviewStorageManager


class ReviewExecutor:
    """
    Executor for code review operations.

    WHY: Centralize review execution logic for better testability and maintainability.
    RESPONSIBILITY: Coordinate review of all developer implementations.
    PATTERNS: Template method pattern for review workflow.

    Attributes:
        llm_provider: LLM provider name (openai/anthropic)
        llm_model: Specific model to use
        code_review_dir: Directory for code review output
        logger: Logger interface
        notifier: ReviewNotifier for event notifications
        storage: ReviewStorageManager for persisting results
        progress_callback: Optional callback for progress updates
    """

    def __init__(
        self,
        llm_provider: str,
        llm_model: str,
        code_review_dir: str,
        logger: 'LoggerInterface',
        notifier: ReviewNotifier,
        storage: ReviewStorageManager,
        progress_callback=None
    ):
        """
        Initialize review executor.

        Args:
            llm_provider: LLM provider (openai/anthropic)
            llm_model: Specific model to use
            code_review_dir: Directory for code review output
            logger: Logger interface
            notifier: ReviewNotifier for notifications
            storage: ReviewStorageManager for storage operations
            progress_callback: Optional callback for progress updates
        """
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.code_review_dir = code_review_dir
        self.logger = logger
        self.notifier = notifier
        self.storage = storage
        self.progress_callback = progress_callback

    def review_all_developers(
        self,
        developers: List[Dict],
        card_id: str,
        task_title: str,
        task_description: str
    ) -> Tuple[List[Dict], bool, int, int]:
        """
        Review all developer implementations.

        WHY: Coordinate reviews across multiple developers and aggregate results.
        PATTERNS: Template method - defines review workflow structure.

        Args:
            developers: List of developer results to review
            card_id: Task card identifier
            task_title: Task title
            task_description: Task description

        Returns:
            Tuple of (review_results, all_reviews_pass, total_critical_issues, total_high_issues)
        """
        review_results = []
        all_reviews_pass = True
        total_critical_issues = 0
        total_high_issues = 0

        for i, dev_result in enumerate(developers):
            result = self._review_single_developer(
                index=i,
                dev_result=dev_result,
                total_developers=len(developers),
                card_id=card_id,
                task_title=task_title,
                task_description=task_description
            )

            review_results.append(result.review_result)
            total_critical_issues += result.critical_issues
            total_high_issues += result.high_issues

            if result.review_status == "FAIL":
                all_reviews_pass = False

        return review_results, all_reviews_pass, total_critical_issues, total_high_issues

    def _review_single_developer(
        self,
        index: int,
        dev_result: Dict,
        total_developers: int,
        card_id: str,
        task_title: str,
        task_description: str
    ) -> DeveloperReviewResult:
        """
        Review a single developer's implementation.

        WHY: Template method pattern - encapsulates single developer review workflow.
        PATTERNS: Template method defining review steps.

        Args:
            index: Developer index in list (for progress tracking)
            dev_result: Developer result dictionary
            total_developers: Total number of developers
            card_id: Task card identifier
            task_title: Task title
            task_description: Task description

        Returns:
            DeveloperReviewResult with complete review data
        """
        developer_name = dev_result.get('developer', 'unknown')
        implementation_dir = dev_result.get(
            'output_dir',
            f'{tempfile.gettempdir()}/{developer_name}/'
        )

        # Step 1: Update progress
        self._update_review_progress(index, developer_name, total_developers)

        # Step 2: Log review start
        self._log_review_start(developer_name)

        # Step 3: Notify review started
        self.notifier.notify_review_started(
            card_id,
            developer_name,
            implementation_dir
        )

        # Step 4: Execute review
        review_result = self._execute_review(
            developer_name,
            implementation_dir,
            task_title,
            task_description
        )

        # Step 5: Extract metrics
        metrics = ReviewMetrics.from_dict(review_result)

        # Step 6: Log summary
        self.notifier.log_review_summary(
            metrics.review_status,
            metrics.overall_score,
            metrics.critical_issues,
            metrics.high_issues
        )

        # Step 7: Log outcome
        self.notifier.log_review_outcome(developer_name, metrics.review_status)

        # Step 8: Send appropriate notifications
        self._send_outcome_notifications(
            card_id,
            developer_name,
            metrics
        )

        # Step 9: Store results
        self._store_review_results(
            card_id,
            task_title,
            developer_name,
            review_result,
            implementation_dir
        )

        return DeveloperReviewResult(
            developer_name=developer_name,
            review_result=review_result,
            metrics=metrics
        )

    def _update_review_progress(
        self,
        index: int,
        developer_name: str,
        total_developers: int
    ) -> None:
        """
        Update progress for current review.

        WHY: Provide user feedback on review progress.
        PERFORMANCE: Progress scaled from 10% to 80% across all developers.

        Args:
            index: Developer index (0-based)
            developer_name: Name of developer being reviewed
            total_developers: Total number of developers
        """
        if not self.progress_callback:
            return

        # Scale progress: 10% to 80% for review phase
        progress = 10 + ((index + 1) / total_developers) * 70

        progress_data = StageProgress(
            step=f"reviewing_{developer_name}",
            progress_percent=int(progress),
            current_developer=developer_name,
            total_developers=total_developers
        )

        self.progress_callback(progress_data.to_dict())

    def _log_review_start(self, developer_name: str) -> None:
        """
        Log review start message.

        WHY: Provide clear visual separation between developer reviews.

        Args:
            developer_name: Name of developer being reviewed
        """
        self.logger.log(f"\n{'='*60}", "INFO")
        self.logger.log(f"🔍 Reviewing {developer_name} implementation", "INFO")
        self.logger.log(f"{'='*60}", "INFO")

    def _execute_review(
        self,
        developer_name: str,
        implementation_dir: str,
        task_title: str,
        task_description: str
    ) -> Dict:
        """
        Execute code review using CodeReviewAgent.

        WHY: Delegate actual review to specialized agent.

        Args:
            developer_name: Name of developer
            implementation_dir: Directory containing implementation
            task_title: Task title
            task_description: Task description

        Returns:
            Complete review result dictionary
        """
        review_agent = CodeReviewAgent(
            developer_name=developer_name,
            llm_provider=self.llm_provider,
            llm_model=self.llm_model,
            logger=self.logger,
            rag_agent=None  # Storage manager handles RAG separately
        )

        return review_agent.review_implementation(
            implementation_dir=implementation_dir,
            task_title=task_title,
            task_description=task_description,
            output_dir=self.code_review_dir
        )

    def _send_outcome_notifications(
        self,
        card_id: str,
        developer_name: str,
        metrics: ReviewMetrics
    ) -> None:
        """
        Send appropriate notifications based on review outcome.

        WHY: Alert different stakeholders based on review result severity.
        PATTERNS: Strategy pattern via status mapping.

        Args:
            card_id: Task card identifier
            developer_name: Name of developer reviewed
            metrics: Review metrics
        """
        # Guard clause: Only send notifications for completed reviews
        if metrics.review_status not in ["FAIL", "NEEDS_IMPROVEMENT", "PASS"]:
            return

        if metrics.review_status == "FAIL":
            self.notifier.notify_review_failed(
                card_id,
                developer_name,
                metrics.overall_score,
                metrics.critical_issues
            )
        else:
            # PASS or NEEDS_IMPROVEMENT
            self.notifier.notify_review_completed(
                card_id,
                developer_name,
                metrics.overall_score,
                metrics.critical_issues,
                metrics.high_issues,
                metrics.review_status
            )

    def _store_review_results(
        self,
        card_id: str,
        task_title: str,
        developer_name: str,
        review_result: Dict,
        implementation_dir: str
    ) -> None:
        """
        Store review results in all storage backends.

        WHY: Persist results for learning and traceability.

        Args:
            card_id: Task card identifier
            task_title: Task title
            developer_name: Name of developer
            review_result: Complete review result
            implementation_dir: Directory containing implementation
        """
        self.storage.store_review_in_rag(
            card_id,
            task_title,
            developer_name,
            review_result
        )

        self.storage.store_review_in_knowledge_graph(
            card_id,
            developer_name,
            review_result,
            implementation_dir
        )

        self.storage.send_review_notification(
            card_id,
            developer_name,
            review_result
        )
