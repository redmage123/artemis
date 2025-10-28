#!/usr/bin/env python3
"""
WHY: Provide public API for intent handlers
RESPONSIBILITY: Export all handler classes
PATTERNS: Facade (simplified package interface)

Handler package provides specialized handlers for different intent types.
"""

from chat.handlers.greeting_handler import GreetingHandler
from chat.handlers.task_handler import TaskHandler
from chat.handlers.status_handler import StatusHandler
from chat.handlers.capability_handler import CapabilityHandler
from chat.handlers.general_handler import GeneralHandler

__all__ = [
    'GreetingHandler',
    'TaskHandler',
    'StatusHandler',
    'CapabilityHandler',
    'GeneralHandler',
]
