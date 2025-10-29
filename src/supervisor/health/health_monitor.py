"""
WHY: Main health monitor orchestrator
RESPONSIBILITY: Coordinate all health monitoring components
PATTERNS: Facade (unified interface), Dependency injection (components)
"""
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from artemis_stage_interface import LoggerInterface
from .agent_registry import AgentRegistry
from .crash_detector import CrashDetector
from .event_observer import EventObserver
from .event_types import AgentHealthEvent, HealthStatus, ProcessHealth
from .health_calculator import HealthCalculator
from .process_monitor import ProcessMonitor
from .progress_tracker import ProgressTracker
from .watchdog import Watchdog

class HealthMonitor:
    """
    WHY: Provide unified interface for health monitoring
    RESPONSIBILITY: Coordinate agent registry, process monitoring, crash detection, and watchdog
    PATTERNS: Facade, Dependency injection

    Architecture:
    - AgentRegistry: Track agent registration and heartbeats
    - ProcessMonitor: Monitor process resources and hanging
    - CrashDetector: Detect agent crashes via state machine
    - ProgressTracker: Track state transitions and progress
    - HealthCalculator: Calculate overall health status
    - EventObserver: Manage observer notifications
    - Watchdog: Autonomous background monitoring

    Thread-safety: Thread-safe (components use locks)
    """

    def __init__(self, logger: Optional[LoggerInterface]=None, verbose: bool=True, state_machine: Optional[Any]=None):
        """
        WHY: Initialize health monitor with all components
        RESPONSIBILITY: Create and wire together monitoring components
        PATTERNS: Dependency injection, Facade

        Args:
            logger: Logger for recording events (LoggerInterface)
            verbose: Enable verbose logging
            state_machine: Optional ArtemisStateMachine for crash/progress detection
        """
        self.logger = logger
        self.verbose = verbose
        self.state_machine = state_machine
        self.agent_registry = AgentRegistry()
        self.process_monitor = ProcessMonitor()
        self.crash_detector = CrashDetector(state_machine)
        self.progress_tracker = ProgressTracker(state_machine)
        self.health_calculator = HealthCalculator()
        self.event_observer = EventObserver(self._log)
        self.watchdog = Watchdog(self.crash_detector, self.progress_tracker, self.event_observer, self._log)

    def register_agent(self, agent_name: str, agent_type: str='stage', metadata: Optional[Dict[str, Any]]=None, heartbeat_interval: float=15.0) -> None:
        """
        WHY: Register agent for health monitoring
        RESPONSIBILITY: Delegate to agent registry and notify observers
        PATTERNS: Facade (delegate to registry)

        Args:
            agent_name: Name of the agent
            agent_type: Type of agent
            metadata: Optional metadata
            heartbeat_interval: Expected heartbeat interval in seconds
        """
        agent_info = self.agent_registry.register(agent_name, agent_type, metadata, heartbeat_interval)
        self._log(f"✅ Registered agent '{agent_name}' ({agent_type})")
        self.event_observer.notify_event(agent_name, AgentHealthEvent.STARTED, agent_info)

    def unregister_agent(self, agent_name: str) -> None:
        """
        WHY: Unregister completed agent
        RESPONSIBILITY: Delegate to registry and notify observers
        PATTERNS: Facade, Guard clause

        Args:
            agent_name: Name of the agent
        """
        if not self.agent_registry.unregister(agent_name):
            return
        self._log(f"✅ Unregistered agent '{agent_name}'")
        self.event_observer.notify_event(agent_name, AgentHealthEvent.COMPLETED, {})

    def agent_heartbeat(self, agent_name: str, progress_data: Optional[Dict[str, Any]]=None) -> None:
        """
        WHY: Record agent heartbeat
        RESPONSIBILITY: Delegate to registry and notify observers
        PATTERNS: Facade, Guard clause

        Args:
            agent_name: Name of the agent
            progress_data: Optional progress information
        """
        result = self.agent_registry.record_heartbeat(agent_name, progress_data)
        if result is None:
            self._log(f"⚠️  Heartbeat from unregistered agent '{agent_name}'", 'WARNING')
            return
        self.event_observer.notify_event(agent_name, AgentHealthEvent.PROGRESS, result)

    def detect_hanging_processes(self) -> List[ProcessHealth]:
        """
        WHY: Find hanging processes
        RESPONSIBILITY: Delegate to process monitor
        PATTERNS: Facade

        Returns:
            List of hanging processes
        """
        return self.process_monitor.detect_hanging_processes()

    def detect_agent_crash(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        WHY: Check if agent crashed
        RESPONSIBILITY: Delegate to crash detector
        PATTERNS: Facade

        Args:
            agent_name: Name of the agent

        Returns:
            Crash info dict if crashed, None otherwise
        """
        try:
            return self.crash_detector.detect_crash(agent_name)
        except Exception as e:
            self._log(f'⚠️  Error detecting crash: {e}', 'WARNING')
            return None

    def check_agent_progress(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        WHY: Check agent progress
        RESPONSIBILITY: Delegate to progress tracker
        PATTERNS: Facade

        Args:
            agent_name: Name of the agent

        Returns:
            Progress info dict if available, None otherwise
        """
        try:
            return self.progress_tracker.check_progress(agent_name)
        except Exception as e:
            self._log(f'⚠️  Error checking progress: {e}', 'WARNING')
            return None

    def monitor_agent_health(self, agent_name: str, timeout_seconds: int=300, check_interval: int=5) -> Dict[str, Any]:
        """
        WHY: Monitor agent health (blocking call)
        RESPONSIBILITY: Continuous monitoring loop with crash/hang detection
        PATTERNS: Guard clause (early return on crash/timeout)

        Args:
            agent_name: Name of the agent
            timeout_seconds: Maximum time before considering hung
            check_interval: Check frequency in seconds

        Returns:
            Health status dict
        """
        self._log(f"👀 Monitoring agent '{agent_name}' (timeout: {timeout_seconds}s)")
        start_time = datetime.now()
        last_activity = start_time
        health_status = {'agent_name': agent_name, 'status': 'healthy', 'start_time': start_time.isoformat(), 'checks_performed': 0}
        while True:
            elapsed = (datetime.now() - start_time).total_seconds()
            health_status['checks_performed'] += 1
            crash_detected = self.detect_agent_crash(agent_name)
            if crash_detected:
                return self._build_crash_status(health_status, crash_detected, elapsed, agent_name)
            if elapsed > timeout_seconds:
                return self._build_hung_status(health_status, timeout_seconds, elapsed, agent_name)
            progress = self.check_agent_progress(agent_name)
            if progress:
                last_activity = datetime.now()
                health_status['last_activity'] = last_activity.isoformat()
            time_since_activity = (datetime.now() - last_activity).total_seconds()
            if time_since_activity > timeout_seconds / 2:
                health_status['status'] = 'stalled'
                health_status['time_since_activity'] = time_since_activity
                self._log(f"⚠️  Agent '{agent_name}' may be stalled (no activity for {time_since_activity}s)")
            time.sleep(check_interval)

    def _build_crash_status(self, health_status: Dict[str, Any], crash_info: Dict[str, Any], elapsed: float, agent_name: str) -> Dict[str, Any]:
        """
        WHY: Build crash status response
        RESPONSIBILITY: Format crash information
        """
        health_status['status'] = 'crashed'
        health_status['crash_info'] = crash_info
        health_status['elapsed_time'] = elapsed
        self._log(f"💥 Agent '{agent_name}' crashed!")
        self._log(f"   Error: {crash_info.get('error')}")
        return health_status

    def _build_hung_status(self, health_status: Dict[str, Any], timeout_seconds: int, elapsed: float, agent_name: str) -> Dict[str, Any]:
        """
        WHY: Build hung status response
        RESPONSIBILITY: Format hung information
        """
        health_status['status'] = 'hung'
        health_status['timeout_seconds'] = timeout_seconds
        health_status['elapsed_time'] = elapsed
        self._log(f"⏰ Agent '{agent_name}' appears hung (timeout: {timeout_seconds}s)")
        return health_status

    def start_watchdog(self, check_interval: int=5, timeout_seconds: int=300) -> Any:
        """
        WHY: Start autonomous monitoring
        RESPONSIBILITY: Delegate to watchdog
        PATTERNS: Facade

        Args:
            check_interval: Seconds between checks
            timeout_seconds: Timeout threshold

        Returns:
            Watchdog thread
        """
        return self.watchdog.start(check_interval, timeout_seconds)

    def stop_watchdog(self) -> None:
        """
        WHY: Stop autonomous monitoring
        RESPONSIBILITY: Delegate to watchdog
        PATTERNS: Facade
        """
        self.watchdog.stop()

    def kill_hanging_process(self, pid: int, force: bool=False) -> bool:
        """
        WHY: Kill hanging process
        RESPONSIBILITY: Delegate to process monitor
        PATTERNS: Facade

        Args:
            pid: Process ID
            force: Use SIGKILL instead of SIGTERM

        Returns:
            True if killed successfully
        """
        result = self.process_monitor.kill_process(pid, force)
        if result:
            signal_name = 'SIGKILL' if force else 'SIGTERM'
            self._log(f'💀 Killed hanging process {pid} ({signal_name})')
        else:
            self._log(f'⚠️  Failed to kill process {pid}', 'WARNING')
        return result

    def cleanup_zombie_processes(self) -> int:
        """
        WHY: Clean up zombie processes
        RESPONSIBILITY: Delegate to process monitor
        PATTERNS: Facade

        Returns:
            Number of zombies cleaned
        """
        cleaned = self.process_monitor.cleanup_zombie_processes()
        if cleaned > 0:
            self._log(f'🧟 Cleaned {cleaned} zombie process(es)')
        return cleaned

    def get_health_status(self) -> HealthStatus:
        """
        WHY: Get overall health status
        RESPONSIBILITY: Delegate to health calculator
        PATTERNS: Facade

        Returns:
            HealthStatus enum value
        """
        stalled_count = self.agent_registry.count_stalled_agents()
        total_count = self.agent_registry.get_agent_count()
        return self.health_calculator.calculate_status(stalled_count, total_count)

    def register_health_observer(self, observer: Any) -> None:
        """
        WHY: Register health observer
        RESPONSIBILITY: Delegate to event observer
        PATTERNS: Facade

        Args:
            observer: Observer object with on_agent_event() method
        """
        self.event_observer.register_observer(observer)

    def unregister_health_observer(self, observer: Any) -> None:
        """
        WHY: Unregister health observer
        RESPONSIBILITY: Delegate to event observer
        PATTERNS: Facade

        Args:
            observer: Observer to remove
        """
        self.event_observer.unregister_observer(observer)

    def notify_health_event(self, agent_name: str, event: AgentHealthEvent, data: Dict[str, Any]) -> None:
        """
        WHY: Notify observers of health event
        RESPONSIBILITY: Delegate to event observer
        PATTERNS: Facade

        Args:
            agent_name: Name of the agent
            event: Health event type
            data: Event data
        """
        self.event_observer.notify_event(agent_name, event, data)

    def get_statistics(self) -> Dict[str, Any]:
        """
        WHY: Get monitoring statistics
        RESPONSIBILITY: Aggregate statistics from all components
        PATTERNS: Facade

        Returns:
            Dict with statistics
        """
        return {**self.agent_registry.stats, **self.process_monitor.stats, **self.crash_detector.stats, 'registered_agents_count': self.agent_registry.get_agent_count(), 'monitored_processes_count': self.process_monitor.get_process_count(), 'watchdog_running': self.watchdog.is_running(), 'health_status': self.get_health_status().value}

    def _log(self, message: str, level: str='INFO') -> None:
        """
        WHY: Log messages
        RESPONSIBILITY: Delegate to logger or print
        PATTERNS: Guard clause

        Args:
            message: Message to log
            level: Log level
        """
        if self.logger:
            self.logger.log(message, level)
        elif self.verbose:
            prefix = '[HealthMonitor]'
            
            logger.log(f'{prefix} {message}', 'INFO')

def _setup_backward_compatibility(monitor: HealthMonitor) -> None:
    """
    WHY: Maintain backward compatibility with old code
    RESPONSIBILITY: Expose internal components as properties
    DEPRECATED: For migration only, use method interface
    """
    monitor.registered_agents = monitor.agent_registry.registered_agents
    monitor.process_registry = monitor.process_monitor.process_registry
    monitor.health_observers = monitor.event_observer.health_observers
    monitor.watchdog_thread = monitor.watchdog.watchdog_thread
    monitor._watchdog_running = False
    monitor.stats = monitor.get_statistics()