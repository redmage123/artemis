#!/usr/bin/env python3
"""
Code Review Stage - Event Notification Handler

WHY: Separate notification logic from core review logic for better testability and SRP.
RESPONSIBILITY: Handle all event notifications for code review stage.
PATTERNS: Strategy pattern for notification types, Observer pattern for event distribution.

This module manages all code review event notifications including review started,
completed, and failed events.
"""

from typing import Dict, Optional
from pipeline_observer import PipelineObservable, PipelineEvent, EventType


class ReviewNotifier:
    """
    Code review event notification handler.

    WHY: Centralize notification logic to avoid duplication and enable testing.
    RESPONSIBILITY: Send appropriate notifications for review lifecycle events.
    PATTERNS: Strategy pattern for different notification types.

    Attributes:
        observable: PipelineObservable for event broadcasting
        logger: Logger interface for debug logging
    """

    def __init__(
        self,
        observable: Optional[PipelineObservable],
        logger: 'LoggerInterface'
    ):
        """
        Initialize review notifier.

        Args:
            observable: Optional PipelineObservable for event notifications
            logger: Logger interface for debug logging
        """
        self.observable = observable
        self.logger = logger

    def notify_review_started(
        self,
        card_id: str,
        developer_name: str,
        implementation_dir: str
    ) -> None:
        """
        Send notification that code review has started.

        WHY: Enable monitoring and tracking of review lifecycle.

        Args:
            card_id: Task card identifier
            developer_name: Name of developer being reviewed
            implementation_dir: Directory containing implementation
        """
        if not self.observable:
            return

        event = PipelineEvent(
            event_type=EventType.CODE_REVIEW_STARTED,
            card_id=card_id,
            developer_name=developer_name,
            data={"implementation_dir": implementation_dir}
        )
        self.observable.notify(event)

    def notify_review_completed(
        self,
        card_id: str,
        developer_name: str,
        overall_score: int,
        critical_issues: int,
        high_issues: int,
        review_status: str
    ) -> None:
        """
        Send notification that code review completed successfully.

        WHY: Enable monitoring and tracking of successful reviews.

        Args:
            card_id: Task card identifier
            developer_name: Name of developer reviewed
            overall_score: Review score (0-100)
            critical_issues: Count of critical issues
            high_issues: Count of high priority issues
            review_status: Review status (PASS/NEEDS_IMPROVEMENT)
        """
        if not self.observable:
            return

        event = PipelineEvent(
            event_type=EventType.CODE_REVIEW_COMPLETED,
            card_id=card_id,
            developer_name=developer_name,
            data={
                "score": overall_score,
                "critical_issues": critical_issues,
                "high_issues": high_issues,
                "status": review_status
            }
        )
        self.observable.notify(event)

    def notify_review_failed(
        self,
        card_id: str,
        developer_name: str,
        overall_score: int,
        critical_issues: int
    ) -> None:
        """
        Send notification that code review failed.

        WHY: Enable immediate alerting on critical review failures.

        Args:
            card_id: Task card identifier
            developer_name: Name of developer reviewed
            overall_score: Review score (0-100)
            critical_issues: Count of critical issues
        """
        if not self.observable:
            return

        error = Exception(f"Code review failed with {critical_issues} critical issues")
        event = PipelineEvent(
            event_type=EventType.CODE_REVIEW_FAILED,
            card_id=card_id,
            developer_name=developer_name,
            error=error,
            data={"score": overall_score, "critical_issues": critical_issues}
        )
        self.observable.notify(event)

    def log_review_summary(
        self,
        review_status: str,
        overall_score: int,
        critical_issues: int,
        high_issues: int
    ) -> None:
        """
        Log review summary metrics.

        WHY: Provide consistent logging format for review results.

        Args:
            review_status: Review status (PASS/FAIL/NEEDS_IMPROVEMENT)
            overall_score: Score from 0-100
            critical_issues: Count of critical issues
            high_issues: Count of high priority issues
        """
        self.logger.log(f"Review Status: {review_status}", "INFO")
        self.logger.log(f"Overall Score: {overall_score}/100", "INFO")
        self.logger.log(f"Critical Issues: {critical_issues}", "INFO")
        self.logger.log(f"High Issues: {high_issues}", "INFO")

    def log_review_outcome(
        self,
        developer_name: str,
        review_status: str
    ) -> None:
        """
        Log review outcome message.

        WHY: Provide user-friendly outcome messages with appropriate severity.
        PATTERNS: Strategy pattern via dictionary mapping for outcome messages.

        Args:
            developer_name: Name of developer reviewed
            review_status: Review status (PASS/FAIL/NEEDS_IMPROVEMENT)
        """
        # Strategy pattern: Map status to (message, log_level)
        outcome_strategies = {
            "FAIL": (
                f"❌ {developer_name} implementation FAILED code review",
                "ERROR"
            ),
            "NEEDS_IMPROVEMENT": (
                f"⚠️  {developer_name} implementation needs improvement",
                "WARNING"
            ),
            "PASS": (
                f"✅ {developer_name} implementation PASSED code review",
                "SUCCESS"
            )
        }

        message, level = outcome_strategies.get(
            review_status,
            (f"❓ {developer_name} implementation has unknown status", "WARNING")
        )

        self.logger.log(message, level)
