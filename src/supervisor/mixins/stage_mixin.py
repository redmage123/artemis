#!/usr/bin/env python3
"""
WHY: Provide specialized mixin for pipeline stages
RESPONSIBILITY: Stage-specific supervision defaults and helpers
PATTERNS: Specialization, Template Method, Callable Strategy

This module extends SupervisedAgentMixin with stage-specific functionality,
providing convenient defaults and a simplified execution interface for
pipeline stages.

Design Decisions:
- Defaults agent_type to "stage" for clarity
- Provides execute_with_supervision() helper for common pattern
- Uses callable strategy for flexible execution
- Automatically extracts stage metadata from context
"""

from typing import Dict, Any, Callable, Optional

from .base_mixin import SupervisedAgentMixin


class SupervisedStageMixin(SupervisedAgentMixin):
    """
    Specialized mixin for pipeline stages

    Provides stage-specific defaults and execution helpers,
    simplifying supervision integration for pipeline stages.

    Design Pattern: Specialization of Mixin
    """

    def __init__(
        self,
        supervisor: Optional[Any],
        stage_name: str,
        heartbeat_interval: int = 15
    ) -> None:
        """
        Initialize supervised stage

        Args:
            supervisor: SupervisorAgent instance (None = no supervision)
            stage_name: Name of the pipeline stage
            heartbeat_interval: Seconds between heartbeats (default 15)

        Note: Automatically sets agent_type to "stage"
        """
        super().__init__(
            supervisor=supervisor,
            agent_name=stage_name,
            agent_type="stage",
            heartbeat_interval=heartbeat_interval
        )

    def execute_with_supervision(
        self,
        context: Dict[str, Any],
        execute_fn: Callable[[], Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Execute stage with automatic supervision

        Combines context extraction and supervised execution into a
        single convenient method. Automatically extracts stage metadata
        from context and wraps execution with supervision.

        Args:
            context: Execution context (must contain execution metadata)
            execute_fn: Callable that performs the actual stage work

        Returns:
            Result from execute_fn

        Usage:
            def execute(self, context):
                return self.execute_with_supervision(
                    context,
                    lambda: self._do_actual_work(context)
                )

        Metadata Extraction:
            - task_id: Extracted from context["card_id"]
            - stage: Set to self.agent_name

        Design Pattern: Template Method + Strategy
            - Template method: Defines execution structure
            - Strategy: execute_fn provides the actual implementation
        """
        # Extract metadata from context
        metadata = {
            "task_id": context.get("card_id"),
            "stage": self.agent_name
        }

        # Execute with supervision using context manager
        with self.supervised_execution(metadata):
            return execute_fn()

    def __repr__(self) -> str:
        supervisor_status = "supervised" if self.supervisor else "unsupervised"
        heartbeat_status = "enabled" if self.enable_heartbeat else "disabled"
        return (
            f"SupervisedStageMixin("
            f"stage={self.agent_name}, "
            f"{supervisor_status}, "
            f"heartbeat={heartbeat_status})"
        )
