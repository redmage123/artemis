#!/usr/bin/env python3
"""
Factory for creating orchestration planners

WHY:
Decouples planner creation from usage, allowing selection of appropriate planner
(AI vs rule-based) based on runtime configuration and LLM availability.

RESPONSIBILITY:
- Create appropriate planner based on configuration
- Handle fallback from AI to rule-based planner
- Provide consistent interface for planner instantiation

PATTERNS:
- Factory Pattern: Creates objects without exposing creation logic
- Strategy Pattern: Returns different strategies based on context
- Dependency Inversion: Returns interface, not concrete implementations
"""

from typing import Optional, Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_orchestration.planner_interface import OrchestrationPlannerInterface
from ai_orchestration.ai_planner import AIOrchestrationPlanner
from ai_orchestration.rule_based_planner import RuleBasedOrchestrationPlanner


class OrchestrationPlannerFactory:
    """
    Factory for creating orchestration planners

    Factory Pattern: Creates appropriate planner based on configuration
    """

    @staticmethod
    def create_planner(
        llm_client: Optional[Any] = None,
        logger: Optional[Any] = None,
        prefer_ai: bool = True
    ) -> OrchestrationPlannerInterface:
        """
        Create appropriate orchestration planner

        Args:
            llm_client: LLM client (required for AI planner)
            logger: Optional logger instance
            prefer_ai: Prefer AI planner if available

        Returns:
            Orchestration planner instance
        """
        if prefer_ai and llm_client is not None:
            return AIOrchestrationPlanner(llm_client, logger)

        if logger and prefer_ai and llm_client is None:
            logger.log("⚠️  LLM client not available, using rule-based planner", "WARNING")
        return RuleBasedOrchestrationPlanner(logger)
