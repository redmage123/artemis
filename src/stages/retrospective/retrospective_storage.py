#!/usr/bin/env python3
"""
Retrospective Storage

WHY: Store and communicate retrospective findings
RESPONSIBILITY: Persist retrospectives to RAG and notify stakeholders
PATTERNS: Single Responsibility, Guard Clauses
"""

from typing import List, Any

from artemis_stage_interface import LoggerInterface

from .retrospective_models import RetrospectiveReport, RetrospectiveItem


class RetrospectiveStorage:
    """
    Store and communicate retrospective findings

    WHY: Separate storage/communication from analysis logic
    RESPONSIBILITY: Persist and distribute retrospective data
    PATTERNS: Single Responsibility, Dependency Injection
    """

    def __init__(self, rag: Any, messenger: Any, logger: LoggerInterface):
        """
        Initialize Retrospective Storage

        Args:
            rag: RAG agent for persistence
            messenger: AgentMessenger for notifications
            logger: Logger interface

        WHY: Dependency injection for testability
        """
        self.rag = rag
        self.messenger = messenger
        self.logger = logger

    def store_retrospective(self, card_id: str, report: RetrospectiveReport) -> None:
        """
        Store retrospective in RAG for learning

        Args:
            card_id: Card ID for retrospective
            report: Complete retrospective report

        WHY: Persist learnings for future reference
        RESPONSIBILITY: Format and store retrospective
        PATTERNS: Guard clauses for formatting
        """
        content = self._format_retrospective_content(report)

        self.rag.store_artifact(
            artifact_type="sprint_retrospective",
            card_id=card_id,
            task_title=f"Sprint {report.sprint_number} Retrospective",
            content=content,
            metadata={
                'sprint_number': report.sprint_number,
                'overall_health': report.overall_health,
                'velocity': report.metrics.velocity,
                'velocity_trend': report.velocity_trend
            }
        )

    def communicate_retrospective(
        self,
        card_id: str,
        report: RetrospectiveReport
    ) -> None:
        """
        Communicate retrospective to orchestrator and team

        Args:
            card_id: Card ID for retrospective
            report: Complete retrospective report

        WHY: Notify stakeholders of retrospective completion
        RESPONSIBILITY: Send structured updates
        PATTERNS: Single Responsibility
        """
        self.messenger.send_data_update(
            to_agent="orchestrator",
            card_id=card_id,
            update_type="sprint_retrospective_complete",
            data={
                'sprint_number': report.sprint_number,
                'overall_health': report.overall_health,
                'velocity': report.metrics.velocity,
                'velocity_trend': report.velocity_trend,
                'action_items_count': len(report.action_items),
                'recommendations': report.recommendations,
                'key_learnings': report.key_learnings
            },
            priority="medium"
        )

        self.logger.log(
            f"📊 Retrospective communicated to orchestrator: {report.overall_health} health",
            "INFO"
        )

    def _format_retrospective_content(self, report: RetrospectiveReport) -> str:
        """
        Format retrospective report for storage

        Args:
            report: Retrospective report

        Returns:
            Formatted content string

        WHY: Separate formatting logic
        RESPONSIBILITY: Create human-readable retrospective text
        PATTERNS: Helper method, String formatting
        """
        content = f"""Sprint {report.sprint_number} Retrospective

Duration: {report.sprint_start_date} to {report.sprint_end_date}
Health: {report.overall_health}
Velocity: {report.metrics.velocity:.0f}%
Velocity Trend: {report.velocity_trend}

What Went Well ({len(report.what_went_well)} items):
{self._format_items(report.what_went_well)}

What Didn't Go Well ({len(report.what_didnt_go_well)} items):
{self._format_items(report.what_didnt_go_well)}

Action Items ({len(report.action_items)} items):
{self._format_items(report.action_items)}

Key Learnings:
{chr(10).join(['- ' + l for l in report.key_learnings])}

Recommendations:
{chr(10).join(['- ' + r for r in report.recommendations])}
"""
        return content

    def _format_items(self, items: List[RetrospectiveItem]) -> str:
        """
        Format retrospective items for display

        Args:
            items: List of retrospective items

        Returns:
            Formatted items string

        WHY: Separate item formatting logic
        RESPONSIBILITY: Format item list for readability
        PATTERNS: Guard clause, List comprehension
        """
        # Guard: Handle empty list
        if not items:
            return "  (none)"

        # List comprehension for formatting
        return "\n".join([
            f"  - [{item.impact.upper()}] {item.description}"
            for item in items
        ])
