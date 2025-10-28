"""
Module: agents/supervisor/heartbeat.py

WHY: Agent monitoring and heartbeat management for distributed agent coordination.
RESPONSIBILITY: Track agent health, detect failures, and adapt monitoring frequency.
PATTERNS: Observer Pattern (for health events), Strategy Pattern (auto-adjustment).

This module handles:
- Agent registration and lifecycle tracking
- Periodic heartbeat signals from agents
- Dynamic heartbeat interval adjustment
- Automatic optimization based on agent behavior
- Health event notifications

EXTRACTED FROM: supervisor_agent.py (lines 2801-3027)
"""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class AgentHealthEvent(Enum):
    """Agent health event types for Observer Pattern"""
    STARTED = "started"
    PROGRESS = "progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RECOVERED = "recovered"


class HeartbeatManager:
    """
    Manages agent heartbeats and health monitoring

    WHY: Centralize heartbeat logic with clean interfaces
    PATTERNS: Observer Pattern, Strategy Pattern (auto-adjustment heuristics)
    """

    def __init__(
        self,
        verbose: bool = False,
        state_machine=None,
        stage_health: Optional[Dict] = None
    ):
        """
        Initialize heartbeat manager

        Args:
            verbose: Enable verbose logging
            state_machine: Optional state machine for logging
            stage_health: Optional stage health tracking dict
        """
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self.verbose = verbose
        self.state_machine = state_machine
        self.stage_health = stage_health or {}
        self.health_observers = []

    def register_agent(
        self,
        agent_name: str,
        agent_type: str = "stage",
        metadata: Optional[Dict[str, Any]] = None,
        heartbeat_interval: float = 15.0
    ) -> None:
        """
        Register an agent with the heartbeat manager for monitoring

        Agents MUST call this on startup to be monitored.

        Args:
            agent_name: Name of the agent (e.g., "DevelopmentStage")
            agent_type: Type of agent (e.g., "stage", "worker", "analyzer")
            metadata: Optional metadata about the agent
            heartbeat_interval: Initial heartbeat interval in seconds (default 15)
        """
        self.registered_agents[agent_name] = {
            "type": agent_type,
            "registered_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "heartbeat_interval": heartbeat_interval
        }

        if self.verbose:
            print(f"[Heartbeat] ✅ Registered agent '{agent_name}' ({agent_type})")

        # Notify observers that agent started
        self._notify_agent_event(
            agent_name,
            AgentHealthEvent.STARTED,
            {
                "agent_type": agent_type,
                "metadata": metadata
            }
        )

    def unregister_agent(self, agent_name: str) -> None:
        """
        Unregister an agent (called when agent completes)

        Args:
            agent_name: Name of the agent
        """
        # Guard: agent not registered
        if agent_name not in self.registered_agents:
            return

        del self.registered_agents[agent_name]

        if self.verbose:
            print(f"[Heartbeat] ✅ Unregistered agent '{agent_name}'")

        # Notify observers that agent completed
        self._notify_agent_event(
            agent_name,
            AgentHealthEvent.COMPLETED,
            {}
        )

    def agent_heartbeat(
        self,
        agent_name: str,
        progress_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Called by agents to signal they're making progress (heartbeat)

        Agents should call this periodically (e.g., every 10-30 seconds) to
        signal they're alive and making progress.

        Args:
            agent_name: Name of the agent
            progress_data: Optional progress information
        """
        # Guard: unregistered agent
        if agent_name not in self.registered_agents:
            if self.verbose:
                print(f"[Heartbeat] ⚠️  Heartbeat from unregistered agent '{agent_name}'")
            return

        # Update last heartbeat time
        self.registered_agents[agent_name]["last_heartbeat"] = datetime.now().isoformat()

        # Notify observers of progress
        self._notify_agent_event(
            agent_name,
            AgentHealthEvent.PROGRESS,
            progress_data or {}
        )

    def adjust_heartbeat_interval(
        self,
        agent_name: str,
        new_interval: float,
        reason: Optional[str] = None
    ) -> bool:
        """
        Dynamically adjust the heartbeat interval for a registered agent

        Allows the manager to adapt heartbeat frequency based on:
        - Agent workload (increase interval if slow operations detected)
        - System load (decrease interval if system resources constrained)
        - Error rate (decrease interval to catch failures faster)
        - Stage complexity (LLM-heavy vs I/O-heavy vs CPU-heavy)

        Args:
            agent_name: Name of the agent
            new_interval: New heartbeat interval in seconds (5-60 recommended)
            reason: Optional reason for adjustment (for logging/debugging)

        Returns:
            True if adjustment successful, False if agent not found

        Example:
            # Agent is doing expensive LLM calls, reduce monitoring frequency
            manager.adjust_heartbeat_interval("CodeReviewStage", 30, "LLM operations detected")

            # Agent appears to be stalling, increase monitoring frequency
            manager.adjust_heartbeat_interval("DevelopmentStage", 10, "Stall detection")
        """
        # Guard: agent not registered
        if agent_name not in self.registered_agents:
            if self.verbose:
                print(f"[Heartbeat] ⚠️  Cannot adjust heartbeat for unregistered agent '{agent_name}'")
            return False

        # Validate interval bounds (5-60 seconds)
        new_interval = max(5.0, min(60.0, new_interval))

        # Store old interval for logging
        old_interval = self.registered_agents[agent_name].get("heartbeat_interval", 15.0)

        # Update heartbeat interval
        self.registered_agents[agent_name]["heartbeat_interval"] = new_interval
        self.registered_agents[agent_name]["heartbeat_adjusted_at"] = datetime.now().isoformat()
        self.registered_agents[agent_name]["heartbeat_adjustment_reason"] = reason or "manual adjustment"

        if self.verbose:
            direction = "↑" if new_interval > old_interval else "↓"
            print(
                f"[Heartbeat] {direction} Adjusted heartbeat for '{agent_name}': "
                f"{old_interval}s → {new_interval}s ({reason or 'no reason given'})"
            )

        # Log to state machine if available
        if self.state_machine:
            from artemis_state_machine import PipelineState
            self.state_machine.push_state(
                PipelineState.STAGE_RUNNING,
                {
                    "event": "heartbeat_adjusted",
                    "agent": agent_name,
                    "old_interval": old_interval,
                    "new_interval": new_interval,
                    "reason": reason
                }
            )

        return True

    def get_heartbeat_interval(self, agent_name: str) -> Optional[float]:
        """
        Get the current heartbeat interval for an agent

        Args:
            agent_name: Name of the agent

        Returns:
            Heartbeat interval in seconds, or None if agent not registered
        """
        # Guard: agent not registered
        if agent_name not in self.registered_agents:
            return None

        return self.registered_agents[agent_name].get("heartbeat_interval", 15.0)

    def auto_adjust_heartbeat(self, agent_name: str) -> None:
        """
        Automatically adjust heartbeat interval based on agent behavior

        Uses heuristics to determine optimal heartbeat frequency:
        - If agent has many rapid heartbeats → increase interval (reduce overhead)
        - If agent has slow heartbeats → current interval is appropriate
        - If agent shows errors → decrease interval (catch failures faster)
        - If agent uses LLMs → increase interval (LLM calls are inherently slow)

        This is called automatically by the supervisor's learning engine.

        Args:
            agent_name: Name of the agent
        """
        # Guard: agent not registered
        if agent_name not in self.registered_agents:
            return

        agent_metadata = self.registered_agents[agent_name].get("metadata", {})
        current_interval = self.get_heartbeat_interval(agent_name)

        # Strategy 1: LLM usage → increase interval
        if self._should_increase_for_llm_usage(agent_metadata, current_interval):
            self.adjust_heartbeat_interval(
                agent_name,
                20.0,
                "LLM usage detected - reducing monitoring frequency"
            )
            return

        # Strategy 2: Evaluation-heavy → increase interval
        if self._should_increase_for_evaluation(agent_metadata, current_interval):
            self.adjust_heartbeat_interval(
                agent_name,
                25.0,
                "Evaluation-heavy workload detected"
            )
            return

        # Strategy 3: High failure rate → decrease interval
        if self._should_decrease_for_failures(agent_name, agent_metadata, current_interval):
            failure_rate = self._calculate_failure_rate(agent_name, agent_metadata)
            self.adjust_heartbeat_interval(
                agent_name,
                10.0,
                f"High failure rate ({failure_rate:.1%}) - increasing monitoring"
            )
            return

        # Default: no adjustment needed
        if self.verbose:
            print(f"[Heartbeat] ✓ Heartbeat interval for '{agent_name}' is optimal ({current_interval}s)")

    def _should_increase_for_llm_usage(
        self,
        agent_metadata: Dict[str, Any],
        current_interval: float
    ) -> bool:
        """Check if agent uses LLMs and needs increased interval"""
        uses_llm = agent_metadata.get("uses_llm", False)
        return uses_llm and current_interval < 20

    def _should_increase_for_evaluation(
        self,
        agent_metadata: Dict[str, Any],
        current_interval: float
    ) -> bool:
        """Check if agent is evaluation-heavy and needs increased interval"""
        is_evaluation_heavy = agent_metadata.get("evaluation_heavy", False)
        return is_evaluation_heavy and current_interval < 25

    def _should_decrease_for_failures(
        self,
        agent_name: str,
        agent_metadata: Dict[str, Any],
        current_interval: float
    ) -> bool:
        """Check if agent has high failure rate and needs decreased interval"""
        stage_name = agent_metadata.get("stage_name", agent_name)

        # Guard: no health data
        if stage_name not in self.stage_health:
            return False

        failure_rate = self._calculate_failure_rate(agent_name, agent_metadata)

        # High failure rate → more frequent monitoring
        return failure_rate > 0.3 and current_interval > 10

    def _calculate_failure_rate(
        self,
        agent_name: str,
        agent_metadata: Dict[str, Any]
    ) -> float:
        """Calculate failure rate for an agent"""
        stage_name = agent_metadata.get("stage_name", agent_name)

        # Guard: no health data
        if stage_name not in self.stage_health:
            return 0.0

        stage_health = self.stage_health[stage_name]
        execution_count = max(stage_health.execution_count, 1)

        return stage_health.failure_count / execution_count

    def _notify_agent_event(
        self,
        agent_name: str,
        event: AgentHealthEvent,
        data: Dict[str, Any]
    ) -> None:
        """
        Notify all observers of an agent health event

        Args:
            agent_name: Name of the agent
            event: Type of health event
            data: Event data
        """
        for observer in self.health_observers:
            try:
                observer.on_agent_event(agent_name, event, data)
            except Exception as e:
                if self.verbose:
                    print(f"[Heartbeat] ⚠️  Observer notification failed: {e}")

    def add_observer(self, observer) -> None:
        """
        Add a health observer

        Args:
            observer: Observer implementing on_agent_event(agent_name, event, data)
        """
        self.health_observers.append(observer)

    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get current status for an agent

        Args:
            agent_name: Name of the agent

        Returns:
            Agent status dict or None if not registered
        """
        # Guard: agent not registered
        if agent_name not in self.registered_agents:
            return None

        return self.registered_agents[agent_name].copy()

    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status for all registered agents

        Returns:
            Dict mapping agent_name to agent status
        """
        return self.registered_agents.copy()


__all__ = [
    "HeartbeatManager",
    "AgentHealthEvent"
]
