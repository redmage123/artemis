#!/usr/bin/env python3
"""
WHY: Define individual recovery actions with retry and rollback capabilities
RESPONSIBILITY: Encapsulate single workflow action with execution parameters
PATTERNS: Command pattern, retry logic, rollback support
"""

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class WorkflowAction:
    """Single action in a workflow"""
    action_name: str
    handler: Callable
    timeout_seconds: float = 60.0
    retry_on_failure: bool = True
    max_retries: int = 3
    rollback_handler: Optional[Callable] = None
