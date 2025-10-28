#!/usr/bin/env python3
"""
Approval Handler - Approval and Rejection Workflow

WHY: Handle approval and rejection workflows with proper notifications
RESPONSIBILITY: Update board, send notifications, handle iteration limits
PATTERNS: Single Responsibility, Guard Clauses, Event-Driven Notifications

This module:
- Handles project approvals
- Handles project rejections with feedback
- Manages iteration count and limits
- Sends notifications to orchestrator and observers
- Updates Kanban board
"""

from typing import Dict, Any, Optional
from datetime import datetime
from pipeline_observer import PipelineEvent, EventType


class ApprovalHandler:
    """
    Handles approval and rejection workflows

    WHY: Centralize approval/rejection logic with proper state management
    RESPONSIBILITY: Coordinate board updates, notifications, and feedback routing
    """

    def __init__(
        self,
        board: Any,
        messenger: Any,
        logger: Any,
        observable: Optional[Any] = None,
        max_review_iterations: int = 3
    ):
        """
        Initialize Approval Handler

        Args:
            board: KanbanBoard instance
            messenger: AgentMessenger for notifications
            logger: Logger interface
            observable: Optional PipelineObservable for events
            max_review_iterations: Maximum allowed review iterations
        """
        if not board:
            raise ValueError("Board is required for approval handler")
        if not messenger:
            raise ValueError("Messenger is required for approval handler")
        if not logger:
            raise ValueError("Logger is required for approval handler")

        self.board = board
        self.messenger = messenger
        self.logger = logger
        self.observable = observable
        self.max_review_iterations = max_review_iterations

    def handle_approval(
        self,
        card_id: str,
        task_title: str,
        score: float,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle project approval workflow

        WHY: Coordinate approval state updates and notifications

        Args:
            card_id: Kanban card identifier
            task_title: Task title for logging
            score: Review score
            context: Pipeline context

        Returns:
            Result dictionary with approval status
        """
        self.logger.log(f"Project APPROVED (score: {score:.1f}/10)", "SUCCESS")

        self._update_board_for_approval(card_id, score)
        self._notify_orchestrator_approval(card_id, score)
        self._notify_observers_approval(card_id, score)

        return {
            "stage": "project_review",
            "status": "APPROVED",
            "success": True,
            "score": score,
            "message": "Project approved for development",
            "ready_for_development": True
        }

    def handle_rejection(
        self,
        card_id: str,
        task_title: str,
        score: float,
        feedback: Dict[str, Any],
        context: Dict[str, Any],
        iteration_count: int
    ) -> Dict[str, Any]:
        """
        Handle project rejection workflow with feedback

        WHY: Route feedback to architecture stage for revision

        Args:
            card_id: Kanban card identifier
            task_title: Task title for logging
            score: Review score
            feedback: Compiled feedback dictionary
            context: Pipeline context
            iteration_count: Current iteration number

        Returns:
            Result dictionary with rejection status and feedback
        """
        self.logger.log(f"Project REJECTED (score: {score:.1f}/10)", "WARNING")

        self._update_board_for_rejection(card_id, score, feedback, iteration_count)
        self._send_feedback_to_architecture(card_id, score, feedback, iteration_count)
        self._notify_observers_rejection(card_id, score, iteration_count)
        self._update_context_for_next_iteration(context, feedback, iteration_count)

        return {
            "stage": "project_review",
            "status": "REJECTED",
            "success": True,
            "score": score,
            "message": "Project requires revision",
            "feedback": feedback,
            "iteration": iteration_count + 1,
            "requires_architecture_revision": True
        }

    def force_approval(
        self,
        card_id: str,
        task_title: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Force approval after max iterations reached

        WHY: Prevent infinite review loops

        Args:
            card_id: Kanban card identifier
            task_title: Task title for logging
            context: Pipeline context

        Returns:
            Result dictionary with forced approval
        """
        self.logger.log(
            f"Forcing approval after max review iterations ({self.max_review_iterations})",
            "WARNING"
        )

        self.board.update_card(
            card_id,
            {
                'project_review_status': 'APPROVED_WITH_WARNINGS',
                'review_score': 6.0,
                'forced_approval': True,
                'approved_at': datetime.now().isoformat()
            }
        )

        return {
            "stage": "project_review",
            "status": "APPROVED",
            "score": 6.0,
            "message": "Forced approval after max iterations",
            "ready_for_development": True,
            "forced": True
        }

    def _update_board_for_approval(self, card_id: str, score: float) -> None:
        """Update Kanban board for approval"""
        self.board.update_card(
            card_id,
            {
                'project_review_status': 'APPROVED',
                'review_score': score,
                'approved_at': datetime.now().isoformat()
            }
        )

    def _update_board_for_rejection(
        self,
        card_id: str,
        score: float,
        feedback: Dict[str, Any],
        iteration_count: int
    ) -> None:
        """Update Kanban board for rejection"""
        self.board.update_card(
            card_id,
            {
                'project_review_status': 'REJECTED',
                'review_score': score,
                'review_iteration': iteration_count + 1,
                'feedback': feedback,
                'rejected_at': datetime.now().isoformat()
            }
        )

    def _notify_orchestrator_approval(self, card_id: str, score: float) -> None:
        """Notify orchestrator of approval"""
        self.messenger.send_data_update(
            to_agent="orchestrator",
            card_id=card_id,
            update_type="project_approved",
            data={
                'status': 'APPROVED',
                'score': score,
                'ready_for_development': True
            },
            priority="high"
        )

    def _send_feedback_to_architecture(
        self,
        card_id: str,
        score: float,
        feedback: Dict[str, Any],
        iteration_count: int
    ) -> None:
        """Send feedback to Architecture agent for revision"""
        self.messenger.send_data_update(
            to_agent="architecture-agent",
            card_id=card_id,
            update_type="review_feedback_for_revision",
            data={
                'status': 'REJECTED',
                'score': score,
                'feedback': feedback,
                'iteration': iteration_count + 1,
                'max_iterations': self.max_review_iterations,
                'requires_revision': True
            },
            priority="high"
        )

    def _notify_observers_approval(self, card_id: str, score: float) -> None:
        """Notify observers of approval"""
        if not self.observable:
            return

        event = PipelineEvent(
            event_type=EventType.STAGE_COMPLETED,
            card_id=card_id,
            stage_name="project_review",
            data={
                'status': 'APPROVED',
                'score': score,
                'ready_for_development': True
            }
        )
        self.observable.notify(event)

    def _notify_observers_rejection(
        self,
        card_id: str,
        score: float,
        iteration_count: int
    ) -> None:
        """Notify observers of rejection"""
        if not self.observable:
            return

        event = PipelineEvent(
            event_type=EventType.STAGE_COMPLETED,
            card_id=card_id,
            stage_name="project_review",
            data={
                'status': 'REJECTED',
                'score': score,
                'iteration': iteration_count + 1,
                'requires_revision': True
            }
        )
        self.observable.notify(event)

    def _update_context_for_next_iteration(
        self,
        context: Dict[str, Any],
        feedback: Dict[str, Any],
        iteration_count: int
    ) -> None:
        """Update context for next review iteration"""
        context['review_iteration_count'] = iteration_count + 1
        context['review_feedback'] = feedback
