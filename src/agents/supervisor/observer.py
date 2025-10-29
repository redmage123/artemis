from artemis_logger import get_logger
logger = get_logger('observer')
'\nModule: agents/supervisor/observer.py\n\nPurpose: Observer pattern for event-driven agent health monitoring\nWhy: Enables real-time health event notifications without polling\nPatterns: Observer Pattern, Event-Driven Architecture\nIntegration: Supervisor listens for agent crashes, hangs, and stalls\n\nWHAT: Defines observer interface and supervisor implementation for health events\nWHY: Event-driven monitoring is more efficient than polling\nRESPONSIBILITY: Listen for agent health events and trigger recovery\n'
from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING
from datetime import datetime
from agents.supervisor.models import AgentHealthEvent
if TYPE_CHECKING:
    from agents.supervisor.supervisor import SupervisorAgent

class AgentHealthObserver(ABC):
    """
    Observer interface for agent health monitoring (Observer Pattern)

    WHY: Event-driven notifications instead of polling
    PATTERN: Observer Pattern - publish/subscribe for health events
    USAGE: Agents notify observers when state changes (crash, hang, progress)
    """

    @abstractmethod
    def on_agent_event(self, agent_name: str, event: AgentHealthEvent, data: Dict[str, Any]) -> None:
        """
        Called when an agent health event occurs

        Args:
            agent_name: Name of the agent
            event: Type of health event
            data: Event-specific data
        """
        pass

class SupervisorHealthObserver(AgentHealthObserver):
    """
    Supervisor implementation of health observer

    WHY: Listens for agent crashes and hangs, then triggers recovery
    PATTERN: Concrete Observer
    USAGE: supervisor.register_health_observer(SupervisorHealthObserver(supervisor))
    """

    def __init__(self, supervisor: 'SupervisorAgent'):
        """
        Initialize observer with supervisor reference

        Args:
            supervisor: The supervisor agent to notify on events
        """
        self.supervisor = supervisor
        self.agent_start_times: Dict[str, datetime] = {}
        self.agent_last_activity: Dict[str, datetime] = {}

    def on_agent_event(self, agent_name: str, event: AgentHealthEvent, data: Dict[str, Any]) -> None:
        """
        Handle agent health events (claude.md: early returns, no nested ifs)

        Pattern: Dictionary dispatch would be overkill for 6 events
        Strategy: Use early returns for each event type
        """
        now = datetime.now()
        if event == AgentHealthEvent.STARTED:
            self._handle_started(agent_name, now)
            return
        if event == AgentHealthEvent.CRASHED:
            self._handle_crashed(agent_name, data)
            return
        if event == AgentHealthEvent.HUNG:
            self._handle_hung(agent_name, data)
            return
        if event == AgentHealthEvent.STALLED:
            self._handle_stalled(agent_name, data)
            return
        if event == AgentHealthEvent.RECOVERED:
            self._handle_recovered(agent_name, now)
            return
        if event == AgentHealthEvent.TERMINATED:
            self._handle_terminated(agent_name)
            return

    def _handle_started(self, agent_name: str, now: datetime) -> None:
        """Handle agent started event"""
        self.agent_start_times[agent_name] = now
        self.agent_last_activity[agent_name] = now
        if not self.supervisor.verbose:
            return
        
        logger.log(f"[Supervisor] 👀 Monitoring agent '{agent_name}'", 'INFO')

    def _handle_crashed(self, agent_name: str, data: Dict[str, Any]) -> None:
        """Handle agent crash event (claude.md: early return for verbose)"""
        if self.supervisor.verbose:
            
            logger.log(f"[Supervisor] 💥 Agent '{agent_name}' crashed!", 'INFO')
        crash_info = data.get('crash_info', {})
        context = data.get('context', {})
        self.supervisor.recover_crashed_agent(crash_info, context)

    def _handle_hung(self, agent_name: str, data: Dict[str, Any]) -> None:
        """Handle agent hung event"""
        if self.supervisor.verbose:
            
            logger.log(f"[Supervisor] ⏰ Agent '{agent_name}' appears hung!", 'INFO')
        timeout_info = data.get('timeout_info', {})
        self.supervisor.recover_hung_agent(agent_name, timeout_info)

    def _handle_stalled(self, agent_name: str, data: Dict[str, Any]) -> None:
        """Handle agent stalled event"""
        if not self.supervisor.verbose:
            return
        time_since = data.get('time_since_activity', 0)
        
        logger.log(f"[Supervisor] ⚠️  Agent '{agent_name}' stalled (no activity for {time_since}s)", 'INFO')

    def _handle_recovered(self, agent_name: str, now: datetime) -> None:
        """Handle agent recovered/completed event"""
        self.agent_last_activity[agent_name] = now
        if not self.supervisor.verbose:
            return
        
        logger.log(f"[Supervisor] ✓ Agent '{agent_name}' making progress", 'INFO')

    def _handle_terminated(self, agent_name: str) -> None:
        """Handle agent terminated/completed event"""
        start_time = self.agent_start_times.get(agent_name)
        if self.supervisor.verbose and start_time:
            elapsed = (datetime.now() - start_time).total_seconds()
            
            logger.log(f"[Supervisor] ✅ Agent '{agent_name}' completed (elapsed: {elapsed}s)", 'INFO')
        self.agent_start_times.pop(agent_name, None)
        self.agent_last_activity.pop(agent_name, None)
__all__ = ['AgentHealthObserver', 'SupervisorHealthObserver']