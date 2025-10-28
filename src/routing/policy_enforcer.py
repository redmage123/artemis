#!/usr/bin/env python3
"""
WHY: Enforce routing policies on task requirements (e.g., minimum dev group size).

RESPONSIBILITY:
- Enforce minimum developer group size policy
- Validate and adjust resource allocations
- Log policy enforcement decisions
- Ensure orchestrator constraints are met

PATTERNS:
- Strategy Pattern: Pluggable policy enforcement strategies
- Guard Clauses: Early returns for edge cases
- Single Responsibility: Only handles policy enforcement
"""

from typing import Optional, Any

from routing.models import TaskRequirements


class PolicyEnforcer:
    """
    WHY: Centralize policy enforcement logic for routing decisions.

    RESPONSIBILITY:
    - Enforce minimum one complete dev group (dev-a + dev-b + adjudicator)
    - Adjust recommendations to meet orchestrator constraints
    - Log enforcement actions for visibility
    """

    def __init__(
        self,
        logger: Optional[Any] = None,
        config: Optional[Any] = None
    ):
        """
        WHY: Initialize enforcer with configuration and logger.

        Args:
            logger: Logger for enforcement messages
            config: Configuration with policy parameters
        """
        self.logger = logger
        self.config = config

    def enforce_dev_group_policy(
        self,
        requirements: TaskRequirements
    ) -> TaskRequirements:
        """
        WHY: Ensure minimum one complete dev group is allocated.

        RESPONSIBILITY:
        - Extract max parallel developers from config
        - Enforce minimum dev group size (dev-a + dev-b + adjudicator)
        - Log enforcement actions
        - Return updated requirements

        A dev group consists of: dev-a + dev-b + adjudicator
        The orchestrator must have at least one dev group running,
        but may spin up more if resources and requirements allow.

        Args:
            requirements: Task requirements with LLM's recommendation

        Returns:
            TaskRequirements with enforced dev group policy

        PATTERNS: Guard Clauses - early returns for edge cases
        """
        # Guard: No config means use default minimum
        if not self.config:
            self._log_enforcement(
                current=requirements.parallel_developers_recommended,
                enforced=2,
                reason="No config available, using default minimum dev group size"
            )
            requirements.parallel_developers_recommended = 2
            return requirements

        # Extract max parallel developers from config
        max_parallel_devs = self.config.get('parallel_developers', 2)

        # Guard: Already at or above maximum
        if requirements.parallel_developers_recommended >= max_parallel_devs:
            return requirements

        # Enforce minimum dev group size
        self._log_enforcement(
            current=requirements.parallel_developers_recommended,
            enforced=max_parallel_devs,
            reason="Minimum one dev group (dev-a + dev-b + adjudicator) required"
        )
        requirements.parallel_developers_recommended = max_parallel_devs

        return requirements

    def _log_enforcement(
        self,
        current: int,
        enforced: int,
        reason: str
    ) -> None:
        """
        WHY: Log policy enforcement for visibility and debugging.

        RESPONSIBILITY:
        - Log enforcement action with details
        - Show original vs enforced values
        - Provide reasoning

        Args:
            current: Current recommended developers
            enforced: Enforced developer count
            reason: Reason for enforcement

        PATTERNS: Guard Clause - skip if no logger
        """
        # Guard: No logger
        if not self.logger:
            return

        self.logger.log(
            f"Enforcing dev group policy: {enforced} developers "
            f"(LLM recommended {current})",
            "INFO"
        )
        self.logger.log(f"   Reason: {reason}", "INFO")
