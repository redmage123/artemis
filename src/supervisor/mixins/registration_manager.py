#!/usr/bin/env python3
"""
WHY: Isolate supervisor registration/unregistration logic
RESPONSIBILITY: Handle agent lifecycle registration with supervisor
PATTERNS: Guard Clauses (max 1 level), Error Recovery, Logging

This module manages the registration and unregistration of agents with
the supervisor, implementing defensive error handling for cleanup scenarios.

Design Decisions:
- Guard clauses prevent unnecessary work when supervisor is None
- Unregister-before-register prevents duplicate registrations
- Silent failure in unregister for cleanup robustness
- Comprehensive error categorization for debugging
"""

import logging
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from supervisor_agent import SupervisorAgent


class RegistrationManager:
    """
    Manages agent registration lifecycle with supervisor

    Handles registration, unregistration, and re-registration scenarios
    with defensive error handling.
    """

    def __init__(
        self,
        supervisor: Optional['SupervisorAgent'],
        agent_name: str,
        agent_type: str
    ) -> None:
        """
        Initialize registration manager

        Args:
            supervisor: SupervisorAgent instance or None
            agent_name: Unique agent identifier
            agent_type: Agent category (e.g., "stage", "worker")
        """
        self.supervisor = supervisor
        self.agent_name = agent_name
        self.agent_type = agent_type
        self._logger = logging.getLogger(f"registration.{agent_name}")

    def register(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Register agent with supervisor

        Args:
            metadata: Optional metadata about the agent

        Process:
            1. Guard: Skip if no supervisor
            2. Unregister first (prevent duplicates)
            3. Register with provided metadata
        """
        # Guard clause: no supervisor means no registration
        if self.supervisor is None:
            return

        # Unregister first to handle re-initialization cases
        self.unregister()

        # Register with supervisor
        self.supervisor.register_agent(
            agent_name=self.agent_name,
            agent_type=self.agent_type,
            metadata=metadata or {}
        )
        self._logger.debug(f"Registered {self.agent_type} agent: {self.agent_name}")

    def unregister(self) -> None:
        """
        Unregister agent from supervisor

        Note: Implements defensive error handling since this is typically
        called during cleanup. Errors are logged but don't propagate.

        Error Categories:
            - Expected: AttributeError, KeyError, ValueError (logged as debug)
            - Unexpected: Other exceptions (logged as warning)
        """
        # Guard clause: no supervisor means nothing to unregister
        if self.supervisor is None:
            return

        try:
            self.supervisor.unregister_agent(self.agent_name)
            self._logger.debug(f"Unregistered {self.agent_type} agent: {self.agent_name}")

        except (AttributeError, KeyError, ValueError) as e:
            # Expected errors - agent may not be registered or supervisor unavailable
            self._logger.debug(f"Unregistration ignored (expected): {e}")

        except Exception as e:
            # Unexpected errors - log warning but don't fail cleanup
            self._logger.warning(
                f"Unexpected error during unregistration: {e}",
                exc_info=True
            )

    def __repr__(self) -> str:
        supervisor_status = "active" if self.supervisor else "none"
        return (
            f"RegistrationManager("
            f"agent={self.agent_name}, "
            f"type={self.agent_type}, "
            f"supervisor={supervisor_status})"
        )
