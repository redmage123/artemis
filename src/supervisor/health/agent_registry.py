#!/usr/bin/env python3
"""
WHY: Manage agent registration and heartbeat tracking
RESPONSIBILITY: Track registered agents, heartbeats, and metadata
PATTERNS: Registry (agent tracking), Thread-safe (with locks)
"""

import threading
from datetime import datetime
from typing import Any, Dict, List, Optional

from .event_types import AgentHealthEvent


class AgentRegistry:
    """
    WHY: Centralize agent registration and heartbeat tracking
    RESPONSIBILITY: Register/unregister agents, track heartbeats, determine stalled agents
    PATTERNS: Registry, Thread-safe
    """

    def __init__(self):
        """
        WHY: Initialize thread-safe agent registry
        RESPONSIBILITY: Setup storage and synchronization primitives
        """
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        self._agents_lock = threading.Lock()
        self.stats = {
            "agents_registered": 0,
            "heartbeats_received": 0
        }

    def register(
        self,
        agent_name: str,
        agent_type: str = "stage",
        metadata: Optional[Dict[str, Any]] = None,
        heartbeat_interval: float = 15.0
    ) -> Dict[str, Any]:
        """
        WHY: Register agent for monitoring
        RESPONSIBILITY: Add agent to registry with configuration
        PATTERNS: Guard clause (thread-safe)

        Returns:
            Agent info dict for event notification
        """
        with self._agents_lock:
            self.registered_agents[agent_name] = {
                "type": agent_type,
                "registered_at": datetime.now().isoformat(),
                "metadata": metadata or {},
                "heartbeat_interval": heartbeat_interval,
                "last_heartbeat": None
            }

        self.stats["agents_registered"] += 1

        return {
            "agent_type": agent_type,
            "metadata": metadata
        }

    def unregister(self, agent_name: str) -> bool:
        """
        WHY: Remove agent when completed or terminated
        RESPONSIBILITY: Clean up agent from registry

        Returns:
            True if agent was found and removed
        """
        with self._agents_lock:
            if agent_name not in self.registered_agents:
                return False

            del self.registered_agents[agent_name]
            return True

    def record_heartbeat(
        self,
        agent_name: str,
        progress_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        WHY: Track agent liveness
        RESPONSIBILITY: Update heartbeat timestamp

        Returns:
            Progress data if agent registered, None if unregistered
        """
        with self._agents_lock:
            if agent_name not in self.registered_agents:
                return None

            self.registered_agents[agent_name]["last_heartbeat"] = datetime.now().isoformat()

        self.stats["heartbeats_received"] += 1
        return progress_data or {}

    def is_registered(self, agent_name: str) -> bool:
        """
        WHY: Check agent registration status
        RESPONSIBILITY: Thread-safe registration check
        """
        with self._agents_lock:
            return agent_name in self.registered_agents

    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        WHY: Retrieve agent metadata
        RESPONSIBILITY: Thread-safe agent info retrieval
        """
        with self._agents_lock:
            return self.registered_agents.get(agent_name)

    def count_stalled_agents(self) -> int:
        """
        WHY: Determine system health
        RESPONSIBILITY: Count agents with stale heartbeats
        PATTERNS: Guard clause (early return)

        Returns:
            Number of stalled agents
        """
        if not self.registered_agents:
            return 0

        now = datetime.now()
        stalled_count = 0

        for agent_name, agent_info in self.registered_agents.items():
            last_heartbeat = agent_info.get("last_heartbeat")
            if not last_heartbeat:
                continue

            last_heartbeat_time = datetime.fromisoformat(last_heartbeat)
            elapsed = (now - last_heartbeat_time).total_seconds()
            expected_interval = agent_info.get("heartbeat_interval", 15.0)

            # Agent is stalled if no heartbeat for 3x expected interval
            if elapsed > (expected_interval * 3):
                stalled_count += 1

        return stalled_count

    def get_agent_count(self) -> int:
        """
        WHY: Report registered agent count
        RESPONSIBILITY: Thread-safe count
        """
        with self._agents_lock:
            return len(self.registered_agents)

    def get_all_agents(self) -> List[str]:
        """
        WHY: Retrieve all registered agent names
        RESPONSIBILITY: Thread-safe agent list
        """
        with self._agents_lock:
            return list(self.registered_agents.keys())
