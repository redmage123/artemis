#!/usr/bin/env python3
"""
Module: supervisor_agent.py (BACKWARD COMPATIBILITY WRAPPER)

DEPRECATION NOTICE:
This module is a backward compatibility wrapper. The supervisor has been refactored
into modular components in agents/supervisor/.

Please update your imports to use:
    from agents.supervisor import Supervisor

New Architecture (agents/supervisor/):
    - supervisor.py: Main orchestrator (composition-based)
    - auto_fix.py: LLM-powered automatic error fixing
    - heartbeat.py: Agent monitoring and heartbeat management
    - circuit_breaker.py: Circuit breaker pattern for failing stages
    - health_monitoring.py: Health tracking and recovery
    - stage_execution.py: Recursive stage execution engine
    - observer.py: Observer pattern for health events
    - models.py: Immutable data models

This wrapper provides backward compatibility by:
1. Re-exporting the new Supervisor class as SupervisorAgent
2. Re-exporting all supporting classes and functions
3. Maintaining the exact same public API

Migration Path:
    # Old code (still works via this wrapper)
    from supervisor_agent import SupervisorAgent
    supervisor = SupervisorAgent(...)

    # New code (recommended)
    from agents.supervisor import Supervisor
    supervisor = Supervisor(...)

ORIGINAL FILE: Backed up as supervisor_agent.py.original_3403_lines
"""

# Re-export the new modular supervisor
from agents.supervisor import Supervisor as SupervisorAgent

# Re-export models and enums
from agents.supervisor.models import (
    AgentHealthEvent,
    HealthStatus,
    RecoveryAction,
    ProcessHealth,
    StageHealth,
    RecoveryStrategy
)

# Re-export specialized engines
from agents.supervisor import (
    AutoFixEngine,
    HeartbeatManager,
    CircuitBreakerManager
)

# Factory function for backward compatibility
def create_supervisor(
    logger=None,
    messenger=None,
    card_id=None,
    rag=None,
    verbose=True,
    enable_cost_tracking=True,
    enable_config_validation=True,
    enable_sandboxing=True,
    daily_budget=None,
    monthly_budget=None,
    hydra_config=None
):
    """
    Factory function to create a supervisor instance

    WHY: Backward compatibility with existing code that uses create_supervisor()

    Args:
        logger: Logger for recording events
        messenger: AgentMessenger for alerts
        card_id: Optional card ID for state machine
        rag: Optional RAG agent for learning from history
        verbose: Enable verbose logging
        enable_cost_tracking: Enable LLM cost tracking
        enable_config_validation: Enable startup config validation
        enable_sandboxing: Enable security sandboxing for code execution
        daily_budget: Daily LLM budget (None = unlimited)
        monthly_budget: Monthly LLM budget (None = unlimited)
        hydra_config: Hydra configuration object (for LLM settings)

    Returns:
        SupervisorAgent instance
    """
    return SupervisorAgent(
        logger=logger,
        messenger=messenger,
        card_id=card_id,
        rag=rag,
        verbose=verbose,
        enable_cost_tracking=enable_cost_tracking,
        enable_config_validation=enable_config_validation,
        enable_sandboxing=enable_sandboxing,
        daily_budget=daily_budget,
        monthly_budget=monthly_budget,
        hydra_config=hydra_config
    )


__all__ = [
    "SupervisorAgent",
    "AgentHealthEvent",
    "HealthStatus",
    "RecoveryAction",
    "ProcessHealth",
    "StageHealth",
    "RecoveryStrategy",
    "AutoFixEngine",
    "HeartbeatManager",
    "CircuitBreakerManager",
    "create_supervisor",
]
