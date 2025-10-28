#!/usr/bin/env python3
"""
Module: pipeline_stage.py

WHY: Defines the contract all pipeline stages must implement, enabling polymorphic
     stage execution and consistent behavior across diverse stage types.

RESPONSIBILITY: Provide abstract base for all pipeline stages with execution contract.

PATTERNS:
    - Template Method: Defines execution algorithm skeleton
    - Strategy: Each stage is a strategy for a specific pipeline operation
    - Dependency Injection: Context injected at execution time
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List

from artemis_services import PipelineLogger
from dynamic_pipeline.stage_result import StageResult


class PipelineStage(ABC):
    """
    Abstract base for all pipeline stages.

    Why it exists: Defines contract for all pipeline stages, enabling
    polymorphic execution and consistent error handling.

    Design pattern: Template Method + Strategy

    Responsibilities:
    - Define execution contract via execute()
    - Declare dependencies for ordering
    - Support conditional execution via should_execute()
    - Provide stage metadata (name, description)
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = PipelineLogger(verbose=True)

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> StageResult:
        """
        Execute stage logic.

        Why needed: Core stage execution method. Context contains all data
        from previous stages. Returns result for next stage.

        Args:
            context: Execution context with previous stage results

        Returns:
            StageResult with execution outcome and data

        Raises:
            PipelineException: On stage execution failure
        """
        pass

    def get_dependencies(self) -> List[str]:
        """
        Get list of stage names this stage depends on.

        Why needed: Enables dependency resolution for parallel execution
        and proper stage ordering.

        Returns:
            List of stage names that must complete before this stage
        """
        return []

    def should_execute(self, context: Dict[str, Any]) -> bool:
        """
        Determine if stage should execute based on context.

        Why needed: Enables conditional stage execution. For example,
        testing stage skips if no tests found, deployment skips in
        development mode.

        Args:
            context: Execution context with previous results

        Returns:
            True if stage should execute, False to skip
        """
        return True

    def get_description(self) -> str:
        """Get human-readable stage description"""
        return f"Stage: {self.name}"
