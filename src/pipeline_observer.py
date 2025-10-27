#!/usr/bin/env python3
"""
Module: pipeline_observer.py

Purpose: Implements Observer Pattern for decoupled event-driven pipeline monitoring
Why: Allows multiple components to react to pipeline events without tight coupling,
     enabling extensible monitoring, metrics, logging, and notifications
Patterns: Observer (core), Strategy (configurable observers), Factory (observer creation)
Integration: Central event hub for all pipeline stages, supervisor, and monitoring systems

Architecture:
    - PipelineObservable: Event producer (Subject in Observer pattern)
    - PipelineObserver: Event consumer interface (Observer interface)
    - Concrete observers: LoggingObserver, MetricsObserver, StateTrackingObserver, etc.
    - PipelineEvent: Immutable event data structure
    - EventType: Enum of all event types in system
    - SupervisorCommandObserver: Bidirectional command routing

Design Decisions:
    - Observer pattern decouples event producers from consumers (Open/Closed)
    - Immutable events prevent observer interference
    - Error isolation prevents observer failures from breaking pipeline
    - Command observer enables supervisor to send commands back to pipeline
    - Set-based active developers for O(1) add/remove operations

Event Flow:
    Pipeline Stage -> notify(event) -> PipelineObservable -> all observers
    Supervisor -> SUPERVISOR_COMMAND_* event -> SupervisorCommandObserver -> stage handler

Why Observer Pattern:
    - Easy to add new observers without modifying pipeline code
    - Observers can be enabled/disabled dynamically
    - Multiple independent monitoring systems can coexist
    - Supports both reactive monitoring and proactive control
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

from artemis_services import PipelineLogger


# ============================================================================
# EVENT TYPES
# ============================================================================

class EventType(Enum):
    """
    Types of pipeline events.

    Why needed: Centralized enum of all event types in the Artemis pipeline,
    ensuring type safety and preventing string typos. Enables IDE autocomplete
    and compile-time checking.

    Categories:
    - Pipeline lifecycle: PIPELINE_STARTED, PIPELINE_COMPLETED, PIPELINE_FAILED
    - Stage lifecycle: STAGE_STARTED, STAGE_COMPLETED, STAGE_FAILED, STAGE_SKIPPED
    - Developer: DEVELOPER_STARTED, DEVELOPER_COMPLETED, DEVELOPER_FAILED
    - Code review: CODE_REVIEW_*
    - Validation: VALIDATION_*
    - Integration: INTEGRATION_*
    - Workflow: WORKFLOW_*
    - Supervisor commands: SUPERVISOR_COMMAND_* (bidirectional control)
    - Agent responses: AGENT_COMMAND_*, AGENT_STATUS_*
    - Git operations: GIT_*

    Design decision: Single enum for all event types provides centralized
    event catalog and prevents event name collisions.
    """

    # Pipeline lifecycle
    PIPELINE_STARTED = "pipeline_started"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    PIPELINE_PAUSED = "pipeline_paused"
    PIPELINE_RESUMED = "pipeline_resumed"

    # Stage lifecycle
    STAGE_STARTED = "stage_started"
    STAGE_COMPLETED = "stage_completed"
    STAGE_FAILED = "stage_failed"
    STAGE_SKIPPED = "stage_skipped"
    STAGE_RETRYING = "stage_retrying"
    STAGE_PROGRESS = "stage_progress"

    # Developer events
    DEVELOPER_STARTED = "developer_started"
    DEVELOPER_COMPLETED = "developer_completed"
    DEVELOPER_FAILED = "developer_failed"

    # Code review events
    CODE_REVIEW_STARTED = "code_review_started"
    CODE_REVIEW_COMPLETED = "code_review_completed"
    CODE_REVIEW_FAILED = "code_review_failed"

    # Validation events
    VALIDATION_STARTED = "validation_started"
    VALIDATION_COMPLETED = "validation_completed"
    VALIDATION_FAILED = "validation_failed"

    # Integration events
    INTEGRATION_STARTED = "integration_started"
    INTEGRATION_COMPLETED = "integration_completed"
    INTEGRATION_CONFLICT = "integration_conflict"

    # Workflow events
    WORKFLOW_TRIGGERED = "workflow_triggered"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"

    # Supervisor command events (bidirectional communication)
    SUPERVISOR_COMMAND_PAUSE = "supervisor_command_pause"
    SUPERVISOR_COMMAND_RESUME = "supervisor_command_resume"
    SUPERVISOR_COMMAND_CANCEL = "supervisor_command_cancel"
    SUPERVISOR_COMMAND_RETRY = "supervisor_command_retry"
    SUPERVISOR_COMMAND_SKIP = "supervisor_command_skip"
    SUPERVISOR_COMMAND_OVERRIDE = "supervisor_command_override"
    SUPERVISOR_COMMAND_FORCE_APPROVAL = "supervisor_command_force_approval"
    SUPERVISOR_COMMAND_FORCE_REJECTION = "supervisor_command_force_rejection"
    SUPERVISOR_COMMAND_SELECT_WINNER = "supervisor_command_select_winner"
    SUPERVISOR_COMMAND_CHANGE_PRIORITY = "supervisor_command_change_priority"
    SUPERVISOR_COMMAND_ADJUST_TIMEOUT = "supervisor_command_adjust_timeout"
    SUPERVISOR_COMMAND_REQUEST_STATUS = "supervisor_command_request_status"
    SUPERVISOR_COMMAND_EMERGENCY_STOP = "supervisor_command_emergency_stop"

    # Agent response events
    AGENT_COMMAND_ACKNOWLEDGED = "agent_command_acknowledged"
    AGENT_COMMAND_COMPLETED = "agent_command_completed"
    AGENT_COMMAND_FAILED = "agent_command_failed"
    AGENT_STATUS_RESPONSE = "agent_status_response"

    # Git Agent events
    GIT_REPOSITORY_CONFIGURED = "git_repository_configured"
    GIT_BRANCH_CREATED = "git_branch_created"
    GIT_BRANCH_SWITCHED = "git_branch_switched"
    GIT_BRANCH_DELETED = "git_branch_deleted"
    GIT_COMMIT_CREATED = "git_commit_created"
    GIT_PUSH_STARTED = "git_push_started"
    GIT_PUSH_COMPLETED = "git_push_completed"
    GIT_PUSH_FAILED = "git_push_failed"
    GIT_PULL_STARTED = "git_pull_started"
    GIT_PULL_COMPLETED = "git_pull_completed"
    GIT_PULL_FAILED = "git_pull_failed"
    GIT_TAG_CREATED = "git_tag_created"
    GIT_MERGE_STARTED = "git_merge_started"
    GIT_MERGE_COMPLETED = "git_merge_completed"
    GIT_MERGE_CONFLICT = "git_merge_conflict"
    GIT_OPERATION_FAILED = "git_operation_failed"


# ============================================================================
# EVENT DATA
# ============================================================================

@dataclass
class PipelineEvent:
    """
    Represents a pipeline event.

    Why it exists: Immutable, structured event data passed to all observers,
    ensuring consistent event information and preventing observers from
    modifying event data.

    Design pattern: Data Transfer Object (DTO)

    Responsibilities:
    - Carry event information between producer and observers
    - Provide structured access to event metadata
    - Support serialization to dict for logging/storage

    Immutability: Fields should not be modified after creation to prevent
    observers from interfering with each other.

    Thread-safety: Thread-safe (immutable after creation)
    """
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    card_id: Optional[str] = None
    stage_name: Optional[str] = None
    developer_name: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Exception] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary for serialization.

        Why needed: Enables event storage in logs, databases, message queues,
        and metrics systems. Provides JSON-compatible representation.

        Returns:
            Dict with all event fields serialized to JSON-compatible types
        """
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "card_id": self.card_id,
            "stage_name": self.stage_name,
            "developer_name": self.developer_name,
            "data": self.data,
            "error": str(self.error) if self.error else None
        }


# ============================================================================
# OBSERVER INTERFACE
# ============================================================================

class PipelineObserver(ABC):
    """
    Abstract base class for pipeline observers.

    Why it exists: Defines the contract for all pipeline observers, ensuring
    consistent event handling interface across the system.

    Design pattern: Observer interface (Gang of Four Observer pattern)

    Responsibilities:
    - Define event handling contract via on_event()
    - Provide observer identification via get_observer_name()

    Implementation notes:
    - Observers must handle errors internally to prevent breaking pipeline
    - Observers should be fast (avoid blocking operations)
    - Observers should not modify pipeline state directly
    - Use commands/callbacks for pipeline interaction

    Thread-safety: Implementations must be thread-safe if used in
    multi-threaded context
    """

    @abstractmethod
    def on_event(self, event: PipelineEvent) -> None:
        """
        Handle pipeline event.

        Why needed: Core event handling method called by PipelineObservable
        when events occur. Subclasses implement this to react to events.

        Args:
            event: Pipeline event to handle (immutable)

        Raises:
            Should not raise exceptions - errors should be logged internally
            to prevent breaking pipeline execution

        Performance: Should return quickly to avoid blocking other observers
        """
        pass

    def get_observer_name(self) -> str:
        """
        Get observer name for logging and identification.

        Why needed: Allows PipelineObservable to log which observers are
        attached and which observer failed if errors occur.

        Returns:
            Observer class name (default implementation)
        """
        return self.__class__.__name__


# ============================================================================
# OBSERVABLE (SUBJECT)
# ============================================================================

class PipelineObservable:
    """
    Observable pipeline subject (Subject in Observer pattern).

    Why it exists: Central event broadcasting hub that manages observer
    registration and notification. Decouples event producers (pipeline stages)
    from event consumers (observers).

    Design pattern: Observable/Subject (Gang of Four Observer pattern)

    Responsibilities:
    - Maintain list of registered observers
    - Broadcast events to all observers
    - Isolate observer errors from pipeline execution
    - Log observer attachment/detachment
    - Provide observer count for debugging

    Error handling: Observer exceptions are caught and logged to prevent
    one failing observer from breaking the entire notification chain.

    Thread-safety: Not thread-safe (assumes single-threaded pipeline)
    """

    def __init__(self, verbose: bool = True):
        self._observers: List[PipelineObserver] = []
        self.verbose = verbose
        self.logger = PipelineLogger(verbose=verbose)

    def attach(self, observer: PipelineObserver) -> None:
        """
        Attach observer to receive events

        Args:
            observer: Observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)
            if self.verbose:
                self.logger.log(f"Attached observer: {observer.get_observer_name()}", "INFO")

    def detach(self, observer: PipelineObserver) -> None:
        """
        Detach observer from receiving events

        Args:
            observer: Observer to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)
            if self.verbose:
                self.logger.log(f"Detached observer: {observer.get_observer_name()}", "INFO")

    def notify(self, event: PipelineEvent) -> None:
        """
        Notify all observers of event.

        Why needed: Core event broadcasting method. Ensures all registered
        observers receive events while isolating errors.

        Args:
            event: Event to broadcast (immutable)

        Error handling: Catches exceptions from observers to prevent cascade
        failures. Failed observers are logged but don't stop notification
        of other observers.

        Performance: O(n) where n is number of observers. Observers should
        return quickly to avoid blocking pipeline.
        """
        if self.verbose:
            self.logger.log(
                f"Broadcasting event: {event.event_type.value} "
                f"(card_id={event.card_id}, stage={event.stage_name})",
                "DEBUG"
            )

        for observer in self._observers:
            try:
                observer.on_event(event)
            except Exception as e:
                # Don't let observer errors break the pipeline
                self.logger.log(
                    f"Observer {observer.get_observer_name()} failed to handle event: {e}",
                    "ERROR"
                )

    def get_observer_count(self) -> int:
        """Get number of attached observers"""
        return len(self._observers)


# ============================================================================
# CONCRETE OBSERVERS
# ============================================================================

class LoggingObserver(PipelineObserver):
    """
    Observer that logs all pipeline events

    Provides detailed logging of pipeline execution
    """

    def __init__(self, verbose: bool = True):
        self.logger = PipelineLogger(verbose=verbose)

    def on_event(self, event: PipelineEvent) -> None:
        """Log pipeline event"""

        # Determine log level
        if event.event_type.value.endswith("_failed"):
            level = "ERROR"
        elif event.event_type.value.endswith("_completed"):
            level = "SUCCESS"
        elif event.event_type.value.endswith("_started"):
            level = "INFO"
        else:
            level = "DEBUG"

        # Format message
        parts = [event.event_type.value.upper()]

        if event.card_id:
            parts.append(f"card_id={event.card_id}")

        if event.stage_name:
            parts.append(f"stage={event.stage_name}")

        if event.developer_name:
            parts.append(f"developer={event.developer_name}")

        if event.error:
            parts.append(f"error={event.error}")

        message = " | ".join(parts)
        self.logger.log(message, level)


class MetricsObserver(PipelineObserver):
    """
    Observer that collects pipeline metrics

    Tracks:
    - Stage durations
    - Success/failure rates
    - Retry counts
    - Developer performance
    """

    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "pipeline_starts": 0,
            "pipeline_completions": 0,
            "pipeline_failures": 0,
            "stage_durations": {},
            "stage_failures": {},
            "stage_retries": {},
            "developer_stats": {},
            "events": []
        }
        self.stage_start_times: Dict[str, datetime] = {}

    def on_event(self, event: PipelineEvent) -> None:
        """Collect metrics from event"""

        # Track event
        self.metrics["events"].append(event.to_dict())

        # Pipeline metrics
        if event.event_type == EventType.PIPELINE_STARTED:
            self.metrics["pipeline_starts"] += 1

        elif event.event_type == EventType.PIPELINE_COMPLETED:
            self.metrics["pipeline_completions"] += 1

        elif event.event_type == EventType.PIPELINE_FAILED:
            self.metrics["pipeline_failures"] += 1

        # Stage metrics
        elif event.event_type == EventType.STAGE_STARTED:
            if event.stage_name:
                self.stage_start_times[event.stage_name] = event.timestamp

        elif event.event_type == EventType.STAGE_COMPLETED:
            if event.stage_name and event.stage_name in self.stage_start_times:
                start = self.stage_start_times[event.stage_name]
                duration = (event.timestamp - start).total_seconds()

                if event.stage_name not in self.metrics["stage_durations"]:
                    self.metrics["stage_durations"][event.stage_name] = []

                self.metrics["stage_durations"][event.stage_name].append(duration)

        elif event.event_type == EventType.STAGE_FAILED:
            if event.stage_name:
                self.metrics["stage_failures"][event.stage_name] = \
                    self.metrics["stage_failures"].get(event.stage_name, 0) + 1

        elif event.event_type == EventType.STAGE_RETRYING:
            if event.stage_name:
                self.metrics["stage_retries"][event.stage_name] = \
                    self.metrics["stage_retries"].get(event.stage_name, 0) + 1

        # Developer metrics
        elif event.event_type in [EventType.DEVELOPER_STARTED, EventType.DEVELOPER_COMPLETED, EventType.DEVELOPER_FAILED]:
            if event.developer_name:
                if event.developer_name not in self.metrics["developer_stats"]:
                    self.metrics["developer_stats"][event.developer_name] = {
                        "started": 0,
                        "completed": 0,
                        "failed": 0
                    }

                if event.event_type == EventType.DEVELOPER_STARTED:
                    self.metrics["developer_stats"][event.developer_name]["started"] += 1
                elif event.event_type == EventType.DEVELOPER_COMPLETED:
                    self.metrics["developer_stats"][event.developer_name]["completed"] += 1
                elif event.event_type == EventType.DEVELOPER_FAILED:
                    self.metrics["developer_stats"][event.developer_name]["failed"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        return self.metrics

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary without full event list"""
        summary = self.metrics.copy()
        summary["event_count"] = len(summary["events"])
        del summary["events"]  # Don't include full event list in summary
        return summary


class StateTrackingObserver(PipelineObserver):
    """
    Observer that tracks current pipeline state.

    Why it exists: Maintains real-time snapshot of pipeline state for
    monitoring dashboards, health checks, and status queries.

    Design pattern: Observer + State pattern

    Responsibilities:
    - Track current card ID and stage
    - Monitor active developers (set for O(1) operations)
    - Update pipeline status (idle/running/completed/failed/paused)
    - Maintain recent error history (bounded queue)

    Performance optimization: Uses set for active_developers instead of list
    for O(1) add/remove operations instead of O(n).

    Thread-safety: Not thread-safe (assumes single-threaded pipeline)
    """

    def __init__(self):
        self.current_card_id: Optional[str] = None
        self.current_stage: Optional[str] = None
        # Performance: Use set for O(1) add/remove instead of O(n) list operations
        self.active_developers: Set[str] = set()
        self.pipeline_status: str = "idle"
        self.recent_errors: List[str] = []
        self.max_errors = 10

    def on_event(self, event: PipelineEvent) -> None:
        """Update state based on event"""

        # Update card ID
        if event.card_id:
            self.current_card_id = event.card_id

        # Pipeline state
        if event.event_type == EventType.PIPELINE_STARTED:
            self.pipeline_status = "running"
            self.recent_errors = []

        elif event.event_type == EventType.PIPELINE_COMPLETED:
            self.pipeline_status = "completed"
            self.current_stage = None

        elif event.event_type == EventType.PIPELINE_FAILED:
            self.pipeline_status = "failed"

        elif event.event_type == EventType.PIPELINE_PAUSED:
            self.pipeline_status = "paused"

        # Stage state
        elif event.event_type == EventType.STAGE_STARTED:
            self.current_stage = event.stage_name

        elif event.event_type in [EventType.STAGE_COMPLETED, EventType.STAGE_FAILED, EventType.STAGE_SKIPPED]:
            if event.stage_name == self.current_stage:
                self.current_stage = None

        # Developer state (Performance: O(1) set operations instead of O(n) list)
        elif event.event_type == EventType.DEVELOPER_STARTED:
            if event.developer_name:
                self.active_developers.add(event.developer_name)

        elif event.event_type in [EventType.DEVELOPER_COMPLETED, EventType.DEVELOPER_FAILED]:
            if event.developer_name:
                self.active_developers.discard(event.developer_name)  # discard doesn't raise if not found

        # Error tracking
        if event.error:
            self.recent_errors.append(str(event.error))
            if len(self.recent_errors) > self.max_errors:
                self.recent_errors.pop(0)

    def get_state(self) -> Dict[str, Any]:
        """Get current pipeline state"""
        return {
            "card_id": self.current_card_id,
            "current_stage": self.current_stage,
            "active_developers": self.active_developers.copy(),
            "pipeline_status": self.pipeline_status,
            "recent_errors": self.recent_errors.copy()
        }


class NotificationObserver(PipelineObserver):
    """
    Observer that sends notifications for important events

    Can be extended to send:
    - Slack notifications
    - Email alerts
    - Webhook calls
    - Discord messages
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.notifications: List[Dict[str, Any]] = []

    def on_event(self, event: PipelineEvent) -> None:
        """Send notifications for important events"""

        # Only notify on important events
        important_events = [
            EventType.PIPELINE_COMPLETED,
            EventType.PIPELINE_FAILED,
            EventType.STAGE_FAILED,
            EventType.INTEGRATION_CONFLICT
        ]

        if event.event_type not in important_events:
            return

        notification = {
            "type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "card_id": event.card_id,
            "stage_name": event.stage_name,
            "message": self._format_notification(event)
        }

        self.notifications.append(notification)

        if self.verbose:
            print(f"[Notification] {notification['message']}")

    def _format_notification(self, event: PipelineEvent) -> str:
        """Format notification message"""

        if event.event_type == EventType.PIPELINE_COMPLETED:
            return f"✅ Pipeline completed successfully for {event.card_id}"

        elif event.event_type == EventType.PIPELINE_FAILED:
            return f"❌ Pipeline failed for {event.card_id}: {event.error}"

        elif event.event_type == EventType.STAGE_FAILED:
            return f"⚠️  Stage {event.stage_name} failed for {event.card_id}: {event.error}"

        elif event.event_type == EventType.INTEGRATION_CONFLICT:
            return f"⚠️  Integration conflict in {event.card_id}"

        return f"Event: {event.event_type.value}"

    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get all notifications"""
        return self.notifications.copy()


# ============================================================================
# SUPERVISOR COMMAND OBSERVER
# ============================================================================

class SupervisorCommandObserver(PipelineObserver):
    """
    Observer that receives and executes supervisor commands (bidirectional control).

    Why it exists: Enables supervisor to send commands back to pipeline stages
    for dynamic control (pause, resume, retry, skip, etc.). Implements the
    command pattern for supervisor-to-pipeline communication.

    Design pattern: Observer + Command + Registry

    Responsibilities:
    - Register command handlers from stages
    - Route SUPERVISOR_COMMAND_* events to appropriate handlers
    - Execute commands and track results
    - Maintain command execution history
    - Handle missing handlers gracefully

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
        self.command_handlers: Dict[tuple, callable] = {}
        # Command execution history
        self.command_history: List[Dict[str, Any]] = []

    def register_command_handler(
        self,
        stage_name: str,
        command_type: EventType,
        handler: callable
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

        stage_name = event.stage_name or event.data.get("target_stage")

        if not stage_name:
            self.logger.log(
                f"⚠️  Command {event.event_type.value} has no target stage",
                "WARNING"
            )
            return

        # Look up handler
        key = (stage_name, event.event_type)
        handler = self.command_handlers.get(key)

        if not handler:
            self.logger.log(
                f"⚠️  No handler registered for {stage_name} -> {event.event_type.value}",
                "WARNING"
            )
            return

        # Execute command
        try:
            self.logger.log(
                f"🎯 Executing command: {event.event_type.value} -> {stage_name}",
                "INFO"
            )

            result = handler(event)

            # Record command execution
            self.command_history.append({
                "timestamp": event.timestamp.isoformat(),
                "command": event.event_type.value,
                "stage": stage_name,
                "card_id": event.card_id,
                "result": result,
                "success": True
            })

            self.logger.log(
                f"✅ Command executed successfully: {event.event_type.value}",
                "SUCCESS"
            )

        except Exception as e:
            self.logger.log(
                f"❌ Command execution failed: {event.event_type.value} -> {e}",
                "ERROR"
            )

            # Record failure
            self.command_history.append({
                "timestamp": event.timestamp.isoformat(),
                "command": event.event_type.value,
                "stage": stage_name,
                "card_id": event.card_id,
                "error": str(e),
                "success": False
            })

    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get command execution history"""
        return self.command_history.copy()

    def clear_command_history(self) -> None:
        """Clear command history"""
        self.command_history = []


# ============================================================================
# FACTORY FOR CREATING OBSERVERS
# ============================================================================

class ObserverFactory:
    """
    Factory for creating standard observers

    Makes it easy to set up common observer configurations
    """

    @staticmethod
    def create_default_observers(verbose: bool = True) -> List[PipelineObserver]:
        """
        Create default set of observers

        Returns:
            List of: LoggingObserver, MetricsObserver, StateTrackingObserver
        """
        return [
            LoggingObserver(verbose=verbose),
            MetricsObserver(),
            StateTrackingObserver()
        ]

    @staticmethod
    def create_minimal_observers() -> List[PipelineObserver]:
        """
        Create minimal set of observers (just logging)

        Returns:
            List with only LoggingObserver
        """
        return [LoggingObserver(verbose=True)]

    @staticmethod
    def create_full_observers(verbose: bool = True) -> List[PipelineObserver]:
        """
        Create full set of observers including notifications

        Returns:
            List of all observer types
        """
        return [
            LoggingObserver(verbose=verbose),
            MetricsObserver(),
            StateTrackingObserver(),
            NotificationObserver(verbose=verbose)
        ]


# ============================================================================
# EVENT BUILDER - Convenience for creating events
# ============================================================================

class EventBuilder:
    """
    Builder for creating pipeline events

    Provides convenient methods for creating common events
    """

    @staticmethod
    def pipeline_started(card_id: str, **data) -> PipelineEvent:
        """Create pipeline started event"""
        return PipelineEvent(
            event_type=EventType.PIPELINE_STARTED,
            card_id=card_id,
            data=data
        )

    @staticmethod
    def pipeline_completed(card_id: str, **data) -> PipelineEvent:
        """Create pipeline completed event"""
        return PipelineEvent(
            event_type=EventType.PIPELINE_COMPLETED,
            card_id=card_id,
            data=data
        )

    @staticmethod
    def pipeline_failed(card_id: str, error: Exception, **data) -> PipelineEvent:
        """Create pipeline failed event"""
        return PipelineEvent(
            event_type=EventType.PIPELINE_FAILED,
            card_id=card_id,
            error=error,
            data=data
        )

    @staticmethod
    def stage_started(card_id: str, stage_name: str, **data) -> PipelineEvent:
        """Create stage started event"""
        return PipelineEvent(
            event_type=EventType.STAGE_STARTED,
            card_id=card_id,
            stage_name=stage_name,
            data=data
        )

    @staticmethod
    def stage_completed(card_id: str, stage_name: str, **data) -> PipelineEvent:
        """Create stage completed event"""
        return PipelineEvent(
            event_type=EventType.STAGE_COMPLETED,
            card_id=card_id,
            stage_name=stage_name,
            data=data
        )

    @staticmethod
    def stage_failed(card_id: str, stage_name: str, error: Exception, **data) -> PipelineEvent:
        """Create stage failed event"""
        return PipelineEvent(
            event_type=EventType.STAGE_FAILED,
            card_id=card_id,
            stage_name=stage_name,
            error=error,
            data=data
        )

    @staticmethod
    def developer_started(card_id: str, developer_name: str, **data) -> PipelineEvent:
        """Create developer started event"""
        return PipelineEvent(
            event_type=EventType.DEVELOPER_STARTED,
            card_id=card_id,
            developer_name=developer_name,
            data=data
        )

    @staticmethod
    def developer_completed(card_id: str, developer_name: str, **data) -> PipelineEvent:
        """Create developer completed event"""
        return PipelineEvent(
            event_type=EventType.DEVELOPER_COMPLETED,
            card_id=card_id,
            developer_name=developer_name,
            data=data
        )

    @staticmethod
    def validation_event(developer_name: str, event_type: str, validation_data: dict) -> dict:
        """
        Create a validation event for Layer 3 (Validation Pipeline).

        Args:
            developer_name: Name of developer performing validation
            event_type: Type of validation event:
                - 'validation_started': Validation check initiated
                - 'validation_passed': Validation check passed
                - 'validation_failed': Validation check failed
                - 'validation_max_retries': Max retries exceeded
            validation_data: Event data including:
                - stage: ValidationStage value
                - attempt: Attempt number
                - feedback: List of validation feedback (if failed)
                - score: Validation score (if passed)

        Returns:
            Event dict for observer pattern

        Why: Validation events enable real-time monitoring of code quality
             during generation, not just at the end. This allows:
             - UI dashboards to show live validation status
             - Supervisor to learn from validation patterns
             - Metrics collection for retrospective analysis
        """
        from datetime import datetime

        return {
            "type": "validation",
            "subtype": event_type,
            "developer": developer_name,
            "timestamp": datetime.now().isoformat(),
            "data": validation_data
        }

    @staticmethod
    def rag_validation_event(developer_name: str, rag_result, passed: bool) -> dict:
        """
        Create a RAG validation event for Layer 3.5 (RAG-Enhanced Validation).

        WHY: RAG validation events enable monitoring of hallucination prevention:
             - Track how often generated code matches proven patterns
             - Identify frameworks/languages with lower confidence scores
             - Collect metrics on RAG validation effectiveness
             - Enable supervisor to learn from RAG feedback patterns

        Args:
            developer_name: Name of developer performing validation
            rag_result: RAGValidationResult from rag_enhanced_validation
            passed: Whether RAG validation passed

        Returns:
            Event dict for observer pattern with RAG-specific data
        """
        from datetime import datetime

        return {
            "type": "rag_validation",
            "subtype": "passed" if passed else "failed",
            "developer": developer_name,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "confidence": rag_result.confidence,
                "similar_examples_count": len(rag_result.similar_examples),
                "similarity_results_count": len(rag_result.similarity_results),
                "warnings": rag_result.warnings,
                "recommendations": rag_result.recommendations,
                "best_match_source": (
                    max(rag_result.similar_examples, key=lambda e: e.relevance_score).source
                    if rag_result.similar_examples else None
                ),
                "best_match_score": (
                    max(rag_result.similar_examples, key=lambda e: e.relevance_score).relevance_score
                    if rag_result.similar_examples else 0.0
                )
            }
        }
