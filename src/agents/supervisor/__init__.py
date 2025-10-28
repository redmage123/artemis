"""
Supervisor subpackage - Modularized supervisor components.

Part of: agents

This package contains the decomposed supervisor agent components:
- models: Immutable data models for supervisor state
- observer: Observer pattern for health monitoring
- health_monitoring: Agent health tracking and recovery
- stage_execution: Recursive stage execution engine
- auto_fix: LLM-powered automatic error fixing
- heartbeat: Agent heartbeat and monitoring management
- circuit_breaker: Circuit breaker pattern for failing stages
"""

# Import supervisor components
from .auto_fix import AutoFixEngine
from .heartbeat import HeartbeatManager, AgentHealthEvent
from .circuit_breaker import CircuitBreakerManager
from .supervisor import Supervisor

__all__ = [
    "Supervisor",
    "AutoFixEngine",
    "HeartbeatManager",
    "AgentHealthEvent",
    "CircuitBreakerManager",
]
