#!/usr/bin/env python3
"""
Pipeline Execution Context Management.

WHY: Centralize execution context handling and stage result validation.
RESPONSIBILITY: Manage execution context, validate results, checkpoint integration.
PATTERNS: Context Object Pattern, Guard Clause Pattern.

Dependencies: datetime, timedelta
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class ExecutionContextManager:
    """
    Manages pipeline execution context and result validation.

    WHY: Centralize context and result handling logic.
    RESPONSIBILITY: Validate results, update context, manage checkpoints.
    PATTERNS: Manager Pattern, Validation Pattern.
    """

    @staticmethod
    def is_stage_successful(stage_result: Dict[str, Any]) -> bool:
        """
        Check if stage execution was successful.

        WHY: Centralized success validation with multiple check strategies.
        RESPONSIBILITY: Determine stage success from various result formats.

        Args:
            stage_result: Stage execution result dict

        Returns:
            True if stage succeeded, False otherwise
        """
        if not stage_result:
            return False

        # Check explicit success flag
        if stage_result.get("success", False):
            return True

        # Check status field
        status = stage_result.get("status", "")
        if status in ["COMPLETE", "PASS"]:
            return True

        return False

    @staticmethod
    def update_context_from_result(context: Dict[str, Any], stage_result: Dict[str, Any]):
        """
        Update execution context with stage results.

        WHY: Propagate stage outputs to downstream stages.
        RESPONSIBILITY: Merge stage results into context safely.

        Args:
            context: Pipeline execution context to update
            stage_result: Stage execution result to merge
        """
        if not stage_result:
            return

        context.update(stage_result)

    @staticmethod
    def save_checkpoint(
        context: Dict[str, Any],
        stage_name: str,
        stage_result: Dict[str, Any],
        start_time: datetime
    ):
        """
        Save checkpoint after successful stage completion.

        WHY: Enable pipeline resume capability.
        RESPONSIBILITY: Persist stage completion state.

        Args:
            context: Pipeline execution context
            stage_name: Name of completed stage
            stage_result: Stage execution result
            start_time: Stage start time (approximated if not tracked)
        """
        # Guard: Check orchestrator exists
        orchestrator = context.get('orchestrator')
        if not orchestrator or not hasattr(orchestrator, 'checkpoint_manager'):
            return

        checkpoint_manager = orchestrator.checkpoint_manager

        # Save checkpoint
        checkpoint_manager.save_stage_checkpoint(
            stage_name=stage_name.lower(),
            status="completed",
            result=stage_result,
            start_time=start_time,
            end_time=datetime.now()
        )

    @staticmethod
    def get_card_id(context: Dict[str, Any]) -> str:
        """
        Extract card ID from context.

        WHY: Consistent card ID retrieval with fallback.
        RESPONSIBILITY: Get card ID safely.

        Args:
            context: Pipeline execution context

        Returns:
            Card ID or 'unknown'
        """
        return context.get('card_id', 'unknown')

    @staticmethod
    def get_card(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract card from context.

        WHY: Consistent card retrieval.
        RESPONSIBILITY: Get card safely.

        Args:
            context: Pipeline execution context

        Returns:
            Card dict or None
        """
        return context.get('card')

    @staticmethod
    def build_success_result(
        stages_completed: int,
        results: Dict[str, Any],
        duration: float,
        strategy: str,
        **extra_fields
    ) -> Dict[str, Any]:
        """
        Build standardized success result dict.

        WHY: Consistent result structure across strategies.
        RESPONSIBILITY: Create success result with required fields.

        Args:
            stages_completed: Number of stages completed
            results: Stage execution results
            duration: Total duration in seconds
            strategy: Strategy name
            **extra_fields: Additional strategy-specific fields

        Returns:
            Standardized success result dict
        """
        result = {
            "status": "success",
            "stages_completed": stages_completed,
            "results": results,
            "duration_seconds": duration,
            "strategy": strategy
        }
        result.update(extra_fields)
        return result

    @staticmethod
    def build_failure_result(
        stages_completed: int,
        failed_stage: str,
        error: str,
        results: Dict[str, Any],
        duration: float,
        strategy: str,
        **extra_fields
    ) -> Dict[str, Any]:
        """
        Build standardized failure result dict.

        WHY: Consistent result structure across strategies.
        RESPONSIBILITY: Create failure result with required fields.

        Args:
            stages_completed: Number of stages completed before failure
            failed_stage: Name of stage that failed
            error: Error message
            results: Stage execution results
            duration: Total duration in seconds
            strategy: Strategy name
            **extra_fields: Additional strategy-specific fields

        Returns:
            Standardized failure result dict
        """
        result = {
            "status": "failed",
            "stages_completed": stages_completed,
            "failed_stage": failed_stage,
            "error": error,
            "results": results,
            "duration_seconds": duration,
            "strategy": strategy
        }
        result.update(extra_fields)
        return result
