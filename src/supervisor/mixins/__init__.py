#!/usr/bin/env python3
"""
Supervisor Mixins Package

WHY: Provide modular, composable supervision functionality for agents
RESPONSIBILITY: Export all supervision-related mixins, managers, and exceptions
PATTERNS: Facade Pattern, Package Organization

This package provides everything needed for agent supervision:
- Base mixin for general agents
- Specialized mixin for pipeline stages
- Progress tracking
- Registration management
- Heartbeat management
- Custom exceptions

Package Structure:
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

# Core mixins (primary exports)
from .base_mixin import SupervisedAgentMixin
from .stage_mixin import SupervisedStageMixin

# Managers (for advanced customization)
from .progress_tracker import ProgressTracker
from .registration_manager import RegistrationManager
from .heartbeat_manager import HeartbeatManager

# Exceptions (for error handling)
from .exceptions import HeartbeatError, RegistrationError

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

__version__ = "1.0.0"
__author__ = "Artemis Development Team"
