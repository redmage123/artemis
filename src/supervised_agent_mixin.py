#!/usr/bin/env python3
"""
Supervised Agent Mixin - Backward Compatibility Wrapper

WHY: Maintain 100% backward compatibility during modularization
RESPONSIBILITY: Re-export all symbols from new supervisor.mixins package
PATTERNS: Facade Pattern, Deprecation Path

This module provides backward compatibility for code using the old
supervised_agent_mixin.py module. All functionality has been moved to
the supervisor.mixins package with improved modularity.

MIGRATION PATH:
    Old: from supervised_agent_mixin import SupervisedAgentMixin
    New: from supervisor.mixins import SupervisedAgentMixin

This wrapper ensures existing code continues to work unchanged while
allowing gradual migration to the new package structure.

Package Structure:
    supervisor/mixins/
        exceptions.py          - Custom exception definitions
        progress_tracker.py    - Progress data tracking
        registration_manager.py - Supervisor registration/unregistration
        heartbeat_manager.py   - Daemon heartbeat thread management
        base_mixin.py          - Core supervised agent mixin
        stage_mixin.py         - Specialized stage mixin

Design Patterns:
    - Mixin Pattern: Reusable supervision functionality
    - Composition: Managers handle specific responsibilities
    - Template Method: supervised_execution() defines lifecycle
    - Strategy: Heartbeat and progress can be customized
    - Context Manager: Automatic resource management
"""

# Re-export all public symbols from new package
from supervisor.mixins import (
    SupervisedAgentMixin,
    SupervisedStageMixin,
    ProgressTracker,
    RegistrationManager,
    HeartbeatManager,
    HeartbeatError,
    RegistrationError,
)

__all__ = [
    # Primary mixins
    "SupervisedAgentMixin",
    "SupervisedStageMixin",

    # Managers (advanced use)
    "ProgressTracker",
    "RegistrationManager",
    "HeartbeatManager",

    # Exceptions
    "HeartbeatError",
    "RegistrationError",
]

# Deprecation notice (commented to avoid breaking existing code)
# import warnings
# warnings.warn(
#     "supervised_agent_mixin module is deprecated. "
#     "Use 'from supervisor.mixins import SupervisedAgentMixin' instead.",
#     DeprecationWarning,
#     stacklevel=2
# )
