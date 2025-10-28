#!/usr/bin/env python3
"""
WHY: Centralized exception definitions for supervised agent mixins
RESPONSIBILITY: Define domain-specific exceptions for supervision failures
PATTERNS: Custom Exception Hierarchy

This module provides specialized exceptions for supervised agent operations,
enabling precise error handling and clear failure diagnosis.
"""

from artemis_exceptions import ArtemisException


class HeartbeatError(ArtemisException):
    """
    Raised when heartbeat thread encounters an error

    Used for:
    - Heartbeat thread initialization failures
    - Communication errors with supervisor
    - Thread lifecycle issues
    """
    pass


class RegistrationError(ArtemisException):
    """
    Raised when agent registration fails

    Used for:
    - Failed agent registration with supervisor
    - Invalid registration metadata
    - Supervisor communication failures during registration
    """
    pass
