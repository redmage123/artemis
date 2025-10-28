#!/usr/bin/env python3
"""
Abstract interface for orchestration planners

WHY:
Defines the contract that all orchestration planners must implement, enabling polymorphism
and allowing different planning strategies (AI, rule-based, hybrid) to be used interchangeably.

RESPONSIBILITY:
- Define create_plan() interface
- Enforce Interface Segregation Principle (minimal interface)
- Enable Strategy Pattern implementation

PATTERNS:
- Interface Segregation Principle: Minimal interface with only essential methods
- Strategy Pattern: Enables interchangeable planning algorithms
- Liskov Substitution Principle: All implementations are substitutable
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_orchestration.orchestration_plan import OrchestrationPlan


class OrchestrationPlannerInterface(ABC):
    """
    Abstract interface for orchestration planners

    Interface Segregation Principle: Minimal interface with only essential methods
    """

    @abstractmethod
    def create_plan(
        self,
        card: Dict,
        platform_info: Any,
        resource_allocation: Any
    ) -> OrchestrationPlan:
        """
        Create orchestration plan for given task

        Args:
            card: Kanban card with task details
            platform_info: Platform detection information
            resource_allocation: Resource allocation limits

        Returns:
            Validated orchestration plan
        """
        pass
