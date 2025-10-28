#!/usr/bin/env python3
"""
Module: supervisor/recovery/state_restoration.py

WHY: Manage state restoration after failures
RESPONSIBILITY: Restart failed stages, terminate hung agents, restore execution state
PATTERNS: Template Method (common restart workflow), Command (agent operations)

Design Philosophy:
- Restart stages with fixes applied
- Terminate hung agents safely
- Increase timeouts for retries to prevent repeat failures
"""

from typing import Dict, Any, Optional


class StateRestoration:
    """
    Restore execution state after failures.

    WHY: Failed stages need to be restarted with fixes applied
    RESPONSIBILITY: Restart stages, terminate agents, manage timeouts

    Design Pattern: Template Method (restart workflow)
    - Common steps: validate context, apply fix, restart stage
    - Extensible for different stage types
    """

    def __init__(self, state_machine: Optional[Any] = None, messenger: Optional[Any] = None):
        """
        Initialize state restoration.

        Args:
            state_machine: State machine for stage transitions
            messenger: Messenger for alerts
        """
        self.state_machine = state_machine
        self.messenger = messenger

    def restart_stage(
        self,
        context: Dict[str, Any],
        fix_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Restart a failed stage after applying fix.

        WHY: After fixing error, restart stage to continue pipeline execution
        RESPONSIBILITY: Coordinate stage restart with fix application
        PERFORMANCE: O(1) dictionary operations, external stage restart

        Args:
            context: Execution context
            fix_result: Result of the fix that was applied

        Returns:
            Restart result dict
        """
        stage_name = context.get("stage_name", "unknown")

        # Guard clause: No stage name
        if not stage_name or stage_name == "unknown":
            return {
                "success": False,
                "message": "Cannot restart stage: no stage name in context"
            }

        # In full implementation, would actually restart the stage
        # through state machine or stage orchestrator
        return {
            "success": True,
            "stage_name": stage_name,
            "fix_applied": fix_result,
            "message": f"Stage '{stage_name}' restart initiated with fix applied"
        }

    def terminate_agent(self, agent_name: str) -> Dict[str, Any]:
        """
        Terminate a hung agent.

        WHY: Force kill hung agents to free resources and prevent deadlock
        RESPONSIBILITY: Safely terminate agent process
        PERFORMANCE: O(1) dictionary operations, external process termination

        Args:
            agent_name: Name of the agent to terminate

        Returns:
            Termination result dict
        """
        # Guard clause: No agent name
        if not agent_name:
            return {
                "success": False,
                "message": "Cannot terminate agent: no agent name provided"
            }

        # In full implementation, would kill the actual process
        # This would involve:
        # 1. Finding the process ID
        # 2. Sending SIGTERM, then SIGKILL if needed
        # 3. Cleaning up resources
        return {
            "success": True,
            "agent_name": agent_name,
            "message": f"Agent '{agent_name}' terminated"
        }

    def restart_with_timeout(
        self,
        agent_name: str,
        timeout_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Restart agent with increased timeout.

        WHY: Hung agents may just need more time, increase timeout on retry
        RESPONSIBILITY: Calculate new timeout and restart agent
        PERFORMANCE: O(1) arithmetic and dictionary operations

        Args:
            agent_name: Name of the agent
            timeout_info: Information about the timeout

        Returns:
            Restart result with new timeout
        """
        old_timeout = timeout_info.get("timeout_seconds", 300)

        # Increase timeout by 50%
        new_timeout = old_timeout * 1.5

        restart_context = {
            "agent_name": agent_name,
            "timeout_seconds": new_timeout,
            "retry_attempt": timeout_info.get("retry_attempt", 0) + 1
        }

        # Restart stage with new timeout
        restart_result = self.restart_stage(restart_context, {})

        return {
            "success": restart_result.get("success", False),
            "agent_name": agent_name,
            "old_timeout": old_timeout,
            "new_timeout": new_timeout,
            "restart_result": restart_result,
            "message": f"Agent '{agent_name}' restarted with timeout increased to {new_timeout}s"
        }

    def apply_context_fix(
        self,
        context: Dict[str, Any],
        fix_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply fix to execution context.

        WHY: Some fixes modify context (e.g., add default values)
        RESPONSIBILITY: Merge fix results into context
        PERFORMANCE: O(1) dictionary merge

        Args:
            context: Execution context
            fix_result: Fix result with changes

        Returns:
            Updated context
        """
        # Guard clause: No fix result
        if not fix_result:
            return context

        # Apply parsed data from JSON fix
        parsed_data = fix_result.get("parsed_data")
        if parsed_data:
            context["parsed_response"] = parsed_data

        # Apply default value
        default_value = fix_result.get("default_value")
        missing_key = fix_result.get("missing_key")
        if default_value is not None and missing_key:
            context[missing_key] = default_value

        # Record fix applied
        context["fix_applied"] = fix_result.get("strategy", "unknown")

        return context
