#!/usr/bin/env python3
"""
Module: agent_notifier.py

WHY: Communicate sprint plans to other agents via messenger
RESPONSIBILITY: Broadcast sprint plan completion to architecture and orchestrator
PATTERNS: Publisher pattern for inter-agent communication
"""

from typing import List, Any
from sprint_models import Sprint
from artemis_stage_interface import LoggerInterface


class AgentNotifier:
    """
    WHY: Other agents need sprint plan for their work (architecture, orchestrator)
    RESPONSIBILITY: Send sprint plan updates via messenger
    PATTERNS: Publisher pattern, graceful degradation
    """

    def __init__(self, messenger: Any, logger: LoggerInterface):
        """
        WHY: Need messenger interface for agent communication

        Args:
            messenger: AgentMessenger interface
            logger: Logger for error handling
        """
        self.messenger = messenger
        self.logger = logger

    def notify_sprint_plan_complete(
        self,
        card_id: str,
        task_title: str,
        sprints: List[Sprint]
    ) -> None:
        """
        WHY: Coordinate pipeline by notifying dependent agents
        RESPONSIBILITY: Send sprint plan to architecture and orchestrator
        PATTERNS: Guard clause, graceful degradation

        Args:
            card_id: Card identifier
            task_title: Task title
            sprints: List of Sprint objects
        """
        # Guard: No sprints to notify
        if not sprints:
            return

        try:
            sprint_summary = self._build_summary(task_title, sprints)
            self._notify_architecture_agent(card_id, sprint_summary)
            self._notify_orchestrator(card_id, sprint_summary)
            self._update_shared_state(card_id, sprints)
            self.logger.log("Notified agents of sprint plan", "INFO")
        except Exception as e:
            # Log but don't fail - messaging is not critical
            self.logger.log(f"Error notifying agents: {e}", "ERROR")

    def _build_summary(self, task_title: str, sprints: List[Sprint]) -> dict:
        """
        WHY: Consistent sprint summary format for all agents
        RESPONSIBILITY: Build sprint summary dictionary
        """
        return {
            'task_title': task_title,
            'total_sprints': len(sprints),
            'total_story_points': sum(s.total_story_points for s in sprints),
            'sprints': [s.to_dict() for s in sprints]
        }

    def _notify_architecture_agent(
        self,
        card_id: str,
        sprint_summary: dict
    ) -> None:
        """
        WHY: Architecture agent needs sprint plan for design decisions
        RESPONSIBILITY: Send high-priority update to architecture agent
        """
        self.messenger.send_data_update(
            to_agent="architecture-agent",
            card_id=card_id,
            update_type="sprint_plan_complete",
            data=sprint_summary,
            priority="high"
        )

    def _notify_orchestrator(
        self,
        card_id: str,
        sprint_summary: dict
    ) -> None:
        """
        WHY: Orchestrator tracks overall pipeline progress
        RESPONSIBILITY: Send medium-priority update to orchestrator
        """
        self.messenger.send_data_update(
            to_agent="orchestrator",
            card_id=card_id,
            update_type="sprint_planning_complete",
            data=sprint_summary,
            priority="medium"
        )

    def _update_shared_state(self, card_id: str, sprints: List[Sprint]) -> None:
        """
        WHY: Shared state enables any agent to access sprint plan
        RESPONSIBILITY: Update global shared state with sprint data
        """
        self.messenger.update_shared_state(
            card_id=card_id,
            updates={
                'sprint_planning_complete': True,
                'total_sprints': len(sprints),
                'sprints': [s.to_dict() for s in sprints]
            }
        )
