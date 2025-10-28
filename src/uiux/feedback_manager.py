#!/usr/bin/env python3
"""
WHY: Handle feedback and notification logic for UI/UX evaluations
RESPONSIBILITY: Send feedback to developers and notify other agents
PATTERNS: Messenger pattern, Guard clauses

This module handles all communication related to UI/UX evaluations:
- Sending feedback to developers for iteration
- Notifying other agents of evaluation results
"""

from typing import List, Dict, Any
from .models import DeveloperEvaluation


class FeedbackManager:
    """
    WHY: Centralized feedback and notification logic
    RESPONSIBILITY: Manage developer feedback and agent notifications
    PATTERNS: Messenger pattern, Dependency injection

    Benefits:
    - Isolates communication logic
    - Best-effort notifications don't fail evaluations
    - Clean error handling
    """

    def __init__(self, messenger: Any, logger: Any):
        """
        WHY: Initialize with dependencies
        RESPONSIBILITY: Set up messenger and logger

        Args:
            messenger: Agent messenger for communication
            logger: Logger interface
        """
        self.messenger = messenger
        self.logger = logger

    def send_evaluation_notification(
        self,
        card_id: str,
        evaluation_result: DeveloperEvaluation
    ):
        """
        WHY: Send UI/UX evaluation notification to other agents
        RESPONSIBILITY: Notify integration agent of evaluation completion
        PATTERNS: Best-effort notification (no exceptions raised)

        Args:
            card_id: Task card ID
            evaluation_result: Full evaluation results
        """
        try:
            self.messenger.send_data_update(
                to_agent="integration-agent",
                card_id=card_id,
                update_type="uiux_evaluation_complete",
                data={
                    "developer": evaluation_result.developer,
                    "evaluation_status": evaluation_result.evaluation_status,
                    "ux_score": evaluation_result.ux_score,
                    "accessibility_issues": evaluation_result.accessibility_issues,
                    "wcag_aa_compliance": evaluation_result.wcag_aa_compliance
                },
                priority="medium"
            )

            self.logger.log(
                f"Sent UI/UX evaluation notification for {evaluation_result.developer}",
                "DEBUG"
            )

        except Exception as e:
            # Best-effort: Don't fail evaluation if notification fails
            self.logger.log(
                f"Error sending UI/UX evaluation notification: {e}",
                "WARNING"
            )

    def send_feedback_to_developer(
        self,
        card_id: str,
        evaluation_result: DeveloperEvaluation
    ):
        """
        WHY: Send detailed feedback to developer for iteration
        RESPONSIBILITY: Enable feedback loop for UI/UX improvements
        PATTERNS: Best-effort notification (no exceptions raised)

        This enables the feedback loop where developers can fix UI/UX issues
        and re-submit their implementation.

        Args:
            card_id: Task card ID
            evaluation_result: Full evaluation results
        """
        try:
            # Compile actionable feedback
            feedback = {
                "evaluation_status": evaluation_result.evaluation_status,
                "ux_score": evaluation_result.ux_score,
                "requires_iteration": True,

                # WCAG accessibility feedback
                "accessibility_feedback": {
                    "total_issues": evaluation_result.accessibility_issues,
                    "wcag_aa_compliant": evaluation_result.wcag_aa_compliance,
                    "issues": evaluation_result.accessibility_issues_list,
                    "details": evaluation_result.accessibility_details
                },

                # GDPR compliance feedback
                "gdpr_feedback": {
                    "total_issues": evaluation_result.gdpr_issues,
                    "gdpr_compliant": evaluation_result.gdpr_issues == 0,
                    "issues": evaluation_result.gdpr_issues_list,
                    "compliance_status": evaluation_result.gdpr_compliance
                },

                # Summary for quick action
                "action_required": self._create_action_summary(evaluation_result)
            }

            # Send feedback to developer via messenger
            self.messenger.send_data_update(
                to_agent=f"{evaluation_result.developer}-agent",
                card_id=card_id,
                update_type="uiux_feedback_for_iteration",
                data=feedback,
                priority="high"  # High priority so developer can iterate quickly
            )

            # Also store in shared state for developer to retrieve
            self.messenger.update_shared_state(
                card_id=card_id,
                updates={
                    f"{evaluation_result.developer}_uiux_feedback": feedback,
                    f"{evaluation_result.developer}_needs_iteration": True
                }
            )

            self.logger.log(
                f"📤 Sent feedback to {evaluation_result.developer} for iteration "
                f"({evaluation_result.ux_issues} issues)",
                "INFO"
            )

        except Exception as e:
            # Best-effort: Don't fail evaluation if feedback fails
            self.logger.log(
                f"Error sending feedback to developer: {e}",
                "WARNING"
            )

    def _create_action_summary(self, evaluation_result: DeveloperEvaluation) -> str:
        """
        WHY: Create a concise action summary for developers
        RESPONSIBILITY: Generate human-readable action items
        PATTERNS: List comprehension for Pythonic collection building

        Args:
            evaluation_result: Full evaluation results

        Returns:
            Human-readable action summary
        """
        actions = []

        # Accessibility actions
        if evaluation_result.accessibility_issues > 0:
            actions.append(
                f"Fix {evaluation_result.accessibility_issues} WCAG accessibility issue(s)"
            )

        # GDPR actions
        if evaluation_result.gdpr_issues > 0:
            actions.append(
                f"Resolve {evaluation_result.gdpr_issues} GDPR compliance issue(s)"
            )

        # Priority guidance (using list comprehension - Pythonic!)
        critical_count = sum(
            1
            for issue in (
                evaluation_result.accessibility_issues_list +
                evaluation_result.gdpr_issues_list
            )
            if issue.get('severity') in ['critical', 'serious', 'high']
        )

        if critical_count > 0:
            actions.append(f"⚠️  {critical_count} critical issue(s) require immediate attention")

        return " | ".join(actions) if actions else "No major issues found"
