#!/usr/bin/env python3
"""
Base Workflow Handler Interface

WHY:
Provides abstract base class for all workflow action handlers, enforcing
consistent interface and enabling polymorphic handler execution.

RESPONSIBILITY:
- Define handler contract (single handle method)
- Ensure type safety for all handlers
- Enable polymorphic handler composition

PATTERNS:
- Template Method: Subclasses implement handle() logic
- Strategy Pattern: Different handlers are different recovery strategies
- Command Pattern: Each handler encapsulates an action
- Interface Segregation: Minimal interface (just handle method)

INTEGRATION:
- Extended by: All handler classes in infrastructure, code, dependency, etc.
- Used by: WorkflowHandlerFactory for handler instantiation
- Used by: Workflow execution engine for action orchestration
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class WorkflowHandler(ABC):
    """
    Abstract base class for workflow handlers

    WHAT:
    Base interface for all workflow action handlers. Defines contract that every
    recovery action must implement: a single handle() method that executes the
    action and returns success/failure.

    WHY:
    Interface Segregation Principle: All handlers need only one method (handle).
    This minimal interface makes handlers:
    - Easy to implement (just one method)
    - Easy to test (mock the handle method)
    - Easy to compose (chain handlers in workflows)
    - Polymorphic (any handler can be used in any workflow)

    PATTERNS:
    - Template Method: Subclasses implement handle() logic
    - Strategy Pattern: Different handlers are different recovery strategies
    - Command Pattern: Each handler encapsulates an action

    INTEGRATION:
    - Implemented by: 30+ handler classes (KillHangingProcessHandler, etc.)
    - Used by: Workflow.execute() to run action sequences
    - Created by: WorkflowHandlerFactory.create()
    """

    @abstractmethod
    def handle(self, context: Dict[str, Any]) -> bool:
        """
        Handle the workflow action

        WHAT:
        Executes recovery action (e.g., kill process, free memory, retry LLM request).

        WHY:
        Uniform interface enables workflow execution engine to run any action
        without knowing implementation details. Handlers can be added, removed,
        or swapped without changing workflow execution logic.

        Args:
            context: Context dictionary with action parameters (e.g., pid, file_path, timeout)

        RETURNS:
            bool: True if action succeeded, False if action failed

        EXAMPLE:
            handler = KillHangingProcessHandler()
            success = handler.handle({'pid': 12345})
            if success:
                print("Process killed successfully")
        """
        pass
