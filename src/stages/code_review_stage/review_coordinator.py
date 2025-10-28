#!/usr/bin/env python3
"""
Multi-Developer Review Coordinator

WHY: Coordinate reviews across multiple developer implementations
RESPONSIBILITY: Orchestrate individual developer reviews and progress tracking
PATTERNS: Coordinator Pattern, Single Responsibility, Guard Clauses
"""

import tempfile
from typing import Dict, List, Any, Optional, Callable

from artemis_stage_interface import LoggerInterface
from code_review_agent import CodeReviewAgent
from rag_agent import RAGAgent


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
        debug_component: Any = None
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
        """
        self.logger = logger
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.rag_agent = rag_agent
        self.code_review_dir = code_review_dir
        self.debug_component = debug_component

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

        # Extract review metrics
        review_status = review_result.get('review_status', 'FAIL')
        critical_issues = review_result.get('critical_issues', 0)
        high_issues = review_result.get('high_issues', 0)
        overall_score = review_result.get('overall_score', 0)

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
