#!/usr/bin/env python3
"""
Review Notification Manager

WHY: Handle all code review event notifications and messaging
RESPONSIBILITY: Send notifications to observers and update shared state
PATTERNS: Observer Pattern, Event Handler, Single Responsibility
"""

from typing import Optional, Dict

from artemis_stage_interface import LoggerInterface
from agent_messenger import AgentMessenger
from pipeline_observer import PipelineObservable, PipelineEvent, EventType


class ReviewNotificationManager:
    """
    Manage notifications for code review events.

    WHY: Separate notification logic from review execution
    RESPONSIBILITY: Send events and notifications for review lifecycle
    PATTERNS: Observer Pattern, Event Handler
    """

    def __init__(
        self,
        observable: Optional[PipelineObservable],
        messenger: AgentMessenger,
        logger: LoggerInterface
    ):
        """
        Initialize notification manager.

        Args:
            observable: Optional PipelineObservable for event broadcasting
            messenger: Agent messenger for inter-agent communication
            logger: Logger interface
        """
        self.observable = observable
        self.messenger = messenger
        self.logger = logger

    def notify_review_started(
        self,
        card_id: str,
        developer_name: str,
        implementation_dir: str
    ) -> None:
        """
        Send notification that code review has started.

        WHY: Inform observers when review begins
        PATTERN: Event notification
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

        WHY: Inform observers of successful review completion
        PATTERN: Event notification with success data
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

        WHY: Inform observers of review failure with error details
        PATTERN: Event notification with error data
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

    def handle_review_outcome(
        self,
        review_status: str,
        developer_name: str,
        card_id: str,
        overall_score: int,
        critical_issues: int,
        high_issues: int
    ) -> None:
        """
        Handle review outcome with appropriate notifications and logging.

        WHY: Centralize outcome handling logic
        RESPONSIBILITY: Route to appropriate handler based on status
        PATTERN: Strategy Pattern using dispatch table

        Args:
            review_status: Review status (PASS/FAIL/NEEDS_IMPROVEMENT)
            developer_name: Developer name
            card_id: Card identifier
            overall_score: Overall review score
            critical_issues: Number of critical issues
            high_issues: Number of high issues
        """
        # Dispatch table for status handling
        handlers = {
            "FAIL": self._handle_failed_review,
            "NEEDS_IMPROVEMENT": self._handle_needs_improvement,
            "PASS": self._handle_passed_review
        }

        # Get handler or default
        handler = handlers.get(review_status, self._handle_unknown_status)

        # Execute handler
        handler(developer_name, card_id, overall_score, critical_issues, high_issues, review_status)

    def _handle_failed_review(
        self,
        developer_name: str,
        card_id: str,
        overall_score: int,
        critical_issues: int,
        high_issues: int,
        review_status: str
    ) -> None:
        """Handle failed review outcome."""
        self.logger.log(f"❌ {developer_name} implementation FAILED code review", "ERROR")
        self.notify_review_failed(card_id, developer_name, overall_score, critical_issues)

    def _handle_needs_improvement(
        self,
        developer_name: str,
        card_id: str,
        overall_score: int,
        critical_issues: int,
        high_issues: int,
        review_status: str
    ) -> None:
        """Handle needs improvement outcome."""
        self.logger.log(f"⚠️  {developer_name} implementation needs improvement", "WARNING")

    def _handle_passed_review(
        self,
        developer_name: str,
        card_id: str,
        overall_score: int,
        critical_issues: int,
        high_issues: int,
        review_status: str
    ) -> None:
        """Handle passed review outcome."""
        self.logger.log(f"✅ {developer_name} implementation PASSED code review", "SUCCESS")
        self.notify_review_completed(card_id, developer_name, overall_score, critical_issues, high_issues, review_status)

    def _handle_unknown_status(
        self,
        developer_name: str,
        card_id: str,
        overall_score: int,
        critical_issues: int,
        high_issues: int,
        review_status: str
    ) -> None:
        """Handle unknown review status."""
        self.logger.log(f"⚠️  {developer_name} implementation has unknown status: {review_status}", "WARNING")

    def send_review_notification(
        self,
        card_id: str,
        developer_name: str,
        review_result: Dict
    ) -> None:
        """
        Send code review notification to other agents.

        WHY: Inform other agents of review completion
        RESPONSIBILITY: Send notification and update shared state
        PATTERN: Message passing
        """
        try:
            self.messenger.send_notification(
                to_agent="all",
                card_id=card_id,
                notification_type="code_review_completed",
                data={
                    "developer": developer_name,
                    "review_status": review_result.get('review_status', 'UNKNOWN'),
                    "overall_score": review_result.get('overall_score', 0),
                    "critical_issues": review_result.get('critical_issues', 0),
                    "high_issues": review_result.get('high_issues', 0),
                    "report_file": review_result.get('report_file', '')
                }
            )

            # Update shared state
            self.messenger.update_shared_state(
                card_id=card_id,
                updates={
                    f"code_review_{developer_name}_status": review_result.get('review_status', 'UNKNOWN'),
                    f"code_review_{developer_name}_score": review_result.get('overall_score', 0),
                    "current_stage": "code_review_complete"
                }
            )

        except Exception as e:
            self.logger.log(f"Warning: Could not send review notification: {e}", "WARNING")
