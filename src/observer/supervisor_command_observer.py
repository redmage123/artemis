#!/usr/bin/env python3
"""
Module: observer/supervisor_command_observer.py

WHY: Enables supervisor to send commands back to pipeline stages
     for dynamic control (pause, resume, retry, skip, etc.). Implements
     bidirectional communication between supervisor and pipeline.

RESPONSIBILITY:
    - Register command handlers from stages
    - Route SUPERVISOR_COMMAND_* events to appropriate handlers
    - Execute commands and track results
    - Maintain command execution history
    - Handle missing handlers gracefully

PATTERNS:
    - Observer pattern for receiving commands
    - Command pattern for executing stage operations
    - Registry pattern for handler lookup
    - History pattern for audit trail

DESIGN DECISIONS:
    - Handlers registered by (stage_name, command_type) tuple
    - Command history tracks both successes and failures
    - Errors caught and logged to prevent cascade failures
    - Handlers are callables taking PipelineEvent and returning result dict
"""

from typing import Dict, Any, List, Optional, Callable

from artemis_services import PipelineLogger

from .observer_interface import PipelineObserver
from .event_model import PipelineEvent
from .event_types import EventType


class SupervisorCommandObserver(PipelineObserver):
    """
    Observer that receives and executes supervisor commands (bidirectional control).

    Architecture:
    - Supervisor broadcasts SUPERVISOR_COMMAND_* event via PipelineObservable
    - This observer receives event and looks up registered handler
    - Handler is called with event data
    - Result is recorded in command history

    Handler registration: Stages call register_command_handler() during init
    to register callbacks for specific command types.

    Thread-safety: Not thread-safe (assumes single-threaded pipeline)
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)
        # Map of (stage_name, command_type) -> handler function
        self.command_handlers: Dict[tuple, Callable] = {}
        # Command execution history
        self.command_history: List[Dict[str, Any]] = []

    def register_command_handler(
        self,
        stage_name: str,
        command_type: EventType,
        handler: Callable
    ) -> None:
        """
        Register a command handler for a specific stage and command type

        Args:
            stage_name: Name of the stage (e.g., "ValidationStage", "ArbitrationStage")
            command_type: Type of command event to handle
            handler: Callable that takes (event: PipelineEvent) -> Dict
        """
        key = (stage_name, command_type)
        self.command_handlers[key] = handler

        if self.verbose:
            self.logger.log(
                f"Registered command handler: {stage_name} -> {command_type.value}",
                "DEBUG"
            )

    def unregister_command_handler(
        self,
        stage_name: str,
        command_type: EventType
    ) -> None:
        """Unregister a command handler"""
        key = (stage_name, command_type)
        if key in self.command_handlers:
            del self.command_handlers[key]

            if self.verbose:
                self.logger.log(
                    f"Unregistered command handler: {stage_name} -> {command_type.value}",
                    "DEBUG"
                )

    def on_event(self, event: PipelineEvent) -> None:
        """Handle supervisor command events"""
        # Only process supervisor command events
        if not event.event_type.value.startswith("supervisor_command_"):
            return

        stage_name = self._get_target_stage(event)
        if not stage_name:
            self.logger.log(
                f"Command {event.event_type.value} has no target stage",
                "WARNING"
            )
            return

        handler = self._get_handler(stage_name, event.event_type)
        if not handler:
            self.logger.log(
                f"No handler registered for {stage_name} -> {event.event_type.value}",
                "WARNING"
            )
            return

        self._execute_command(handler, event, stage_name)

    def _get_target_stage(self, event: PipelineEvent) -> Optional[str]:
        """Get target stage from event"""
        return event.stage_name or event.data.get("target_stage")

    def _get_handler(self, stage_name: str, command_type: EventType) -> Optional[Callable]:
        """Get handler for stage and command type"""
        key = (stage_name, command_type)
        return self.command_handlers.get(key)

    def _execute_command(self, handler: Callable, event: PipelineEvent, stage_name: str) -> None:
        """Execute command handler and record result"""
        try:
            self.logger.log(
                f"Executing command: {event.event_type.value} -> {stage_name}",
                "INFO"
            )

            result = handler(event)

            self._record_success(event, stage_name, result)

            self.logger.log(
                f"Command executed successfully: {event.event_type.value}",
                "SUCCESS"
            )

        except Exception as e:
            self.logger.log(
                f"Command execution failed: {event.event_type.value} -> {e}",
                "ERROR"
            )
            self._record_failure(event, stage_name, e)

    def _record_success(self, event: PipelineEvent, stage_name: str, result: Any) -> None:
        """Record successful command execution"""
        self.command_history.append({
            "timestamp": event.timestamp.isoformat(),
            "command": event.event_type.value,
            "stage": stage_name,
            "card_id": event.card_id,
            "result": result,
            "success": True
        })

    def _record_failure(self, event: PipelineEvent, stage_name: str, error: Exception) -> None:
        """Record failed command execution"""
        self.command_history.append({
            "timestamp": event.timestamp.isoformat(),
            "command": event.event_type.value,
            "stage": stage_name,
            "card_id": event.card_id,
            "error": str(error),
            "success": False
        })

    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get command execution history"""
        return self.command_history.copy()

    def clear_command_history(self) -> None:
        """Clear command history"""
        self.command_history = []
