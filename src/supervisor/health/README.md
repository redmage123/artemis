# Supervisor Health Monitor Package

**WHY**: Modular health monitoring system for Artemis supervisor agents and processes
**RESPONSIBILITY**: Track agent liveness, detect crashes/hangs/stalls, notify observers
**PATTERNS**: Facade, Observer, Registry, Strategy, Watchdog

## Overview

The health monitoring package provides comprehensive monitoring of Artemis agents and processes. It detects crashes, hangs, stalls, and resource issues, then notifies observers for appropriate recovery actions.

## Architecture

```
supervisor/health/
├── event_types.py           # Event definitions and data structures
├── agent_registry.py        # Agent registration and heartbeat tracking
├── process_monitor.py       # Process resource monitoring
├── crash_detector.py        # Crash detection via state machine
├── progress_tracker.py      # Progress tracking via state transitions
├── health_calculator.py     # Overall health status calculation
├── event_observer.py        # Observer pattern implementation
├── watchdog.py              # Autonomous background monitoring
├── health_monitor.py        # Main facade coordinating all components
└── __init__.py              # Package exports
```

## Quick Start

### Basic Usage

```python
from supervisor.health import HealthMonitor, AgentHealthEvent, HealthStatus

# Create monitor
monitor = HealthMonitor(verbose=True, state_machine=my_state_machine)

# Register agents
monitor.register_agent("DevelopmentStage", "stage", heartbeat_interval=15.0)

# Send heartbeats
monitor.agent_heartbeat("DevelopmentStage", {"progress": 50})

# Check health
status = monitor.get_health_status()
print(f"Health: {status.value}")  # healthy, degraded, failing, critical

# Get statistics
stats = monitor.get_statistics()
print(f"Crashes: {stats['crashes_detected']}")
```

### Autonomous Monitoring (Watchdog)

```python
# Start watchdog for continuous monitoring
monitor.start_watchdog(check_interval=5, timeout_seconds=300)

# Watchdog automatically detects:
# - CRASHED: State machine in FAILED state
# - HUNG: No state transition for > timeout_seconds
# - STALLED: No progress for > timeout_seconds/2

# Stop watchdog
monitor.stop_watchdog()
```

### Observer Pattern

```python
class MyObserver:
    def on_agent_event(self, agent_name, event, data):
        if event == AgentHealthEvent.CRASHED:
            print(f"{agent_name} crashed: {data['crash_info']}")
        elif event == AgentHealthEvent.HUNG:
            print(f"{agent_name} hung: {data['timeout_info']}")

observer = MyObserver()
monitor.register_health_observer(observer)
```

## Components

### 1. HealthMonitor (Facade)

Main interface coordinating all components.

```python
from supervisor.health import HealthMonitor

monitor = HealthMonitor(
    logger=my_logger,           # Optional LoggerInterface
    verbose=True,               # Print to console
    state_machine=my_sm         # Optional state machine integration
)
```

**Key Methods**:
- `register_agent()` - Add agent to monitoring
- `agent_heartbeat()` - Record agent liveness
- `detect_agent_crash()` - Check for crash
- `monitor_agent_health()` - Blocking monitoring loop
- `start_watchdog()` - Autonomous background monitoring
- `get_health_status()` - Overall system health

### 2. AgentRegistry

Tracks registered agents and heartbeats.

```python
from supervisor.health import AgentRegistry

registry = AgentRegistry()
registry.register("agent1", "stage", heartbeat_interval=15.0)
registry.record_heartbeat("agent1", {"progress": 50})
stalled_count = registry.count_stalled_agents()
```

### 3. ProcessMonitor

Monitors process resources (CPU, memory, hanging).

```python
from supervisor.health import ProcessMonitor

monitor = ProcessMonitor()
monitor.register_process(pid=1234, stage_name="DevelopmentStage")
hanging = monitor.detect_hanging_processes()  # CPU > 90%, time > 5min
monitor.kill_process(pid=1234, force=False)   # SIGTERM
monitor.cleanup_zombie_processes()
```

### 4. CrashDetector

Detects crashes via state machine monitoring.

```python
from supervisor.health import CrashDetector

detector = CrashDetector(state_machine=my_sm)
crash_info = detector.detect_crash("agent1")
if crash_info:
    print(f"Error: {crash_info['error']}")
```

### 5. ProgressTracker

Tracks state transitions and detects stalls/hangs.

```python
from supervisor.health import ProgressTracker

tracker = ProgressTracker(state_machine=my_sm)
progress = tracker.check_progress("agent1")
hang_stall = tracker.check_hang_or_stall(timeout_seconds=300)
```

### 6. HealthCalculator

Calculates overall health status from metrics.

```python
from supervisor.health import HealthCalculator, HealthStatus

calculator = HealthCalculator()
status = calculator.calculate_status(stalled_count=2, total_count=10)
# Returns: HEALTHY, DEGRADED, FAILING, or CRITICAL
```

### 7. EventObserver

Manages observer pattern for health events.

```python
from supervisor.health import EventObserver, AgentHealthEvent

observer = EventObserver()
observer.register_observer(my_observer)
observer.notify_event("agent1", AgentHealthEvent.CRASHED, crash_data)
```

### 8. Watchdog

Autonomous background monitoring in daemon thread.

```python
from supervisor.health import Watchdog

watchdog = Watchdog(crash_detector, progress_tracker, event_observer)
thread = watchdog.start(check_interval=5, timeout_seconds=300)
watchdog.stop()
```

## Event Types

### AgentHealthEvent

- `STARTED` - Agent registered
- `PROGRESS` - Heartbeat received
- `STALLED` - No progress for > timeout/2
- `CRASHED` - State machine in FAILED state
- `HUNG` - No transition for > timeout
- `COMPLETED` - Agent unregistered

### HealthStatus

- `HEALTHY` - All agents responsive (0% stalled)
- `DEGRADED` - Some agents stalled (<50%)
- `FAILING` - Many agents stalled (50-75%)
- `CRITICAL` - Most agents stalled (75%+)

## Thread Safety

All components are thread-safe:
- **AgentRegistry**: Uses `_agents_lock`
- **ProcessMonitor**: Uses `_process_lock`
- **EventObserver**: Uses `_observers_lock`
- **Watchdog**: Daemon thread, safe concurrent access

## Design Patterns

### Facade Pattern
`HealthMonitor` provides unified interface to all components.

### Observer Pattern
`EventObserver` decouples monitoring from event handling.

### Registry Pattern
`AgentRegistry` and `ProcessMonitor` track entities.

### Strategy Pattern
`CrashDetector`, `ProgressTracker`, `HealthCalculator` are pluggable strategies.

### Watchdog Pattern
`Watchdog` provides autonomous background monitoring.

### Dispatch Table
Replaces elif chains with dict/list mappings:
```python
# HealthCalculator thresholds
threshold_dispatch = [
    (0.75, HealthStatus.CRITICAL),
    (0.5, HealthStatus.FAILING),
    (0.0, HealthStatus.DEGRADED)
]

# Watchdog event mapping
event_dispatch = {
    "hung": AgentHealthEvent.HUNG,
    "stalled": AgentHealthEvent.STALLED
}
```

## Guard Clauses

All methods use guard clauses (max 1 level nesting):

```python
def check_progress(self, agent_name):
    # Guard: no state machine
    if not self.state_machine:
        return None

    # Guard: no context
    if not hasattr(self.state_machine, 'context'):
        return None

    # Main logic
    return self._get_progress(agent_name)
```

## Type Hints

Full type hints for all parameters and returns:

```python
from typing import Dict, List, Optional, Any, Callable

def register_agent(
    self,
    agent_name: str,
    agent_type: str = "stage",
    metadata: Optional[Dict[str, Any]] = None,
    heartbeat_interval: float = 15.0
) -> None:
    ...
```

## Testing

### Unit Tests

Each component can be tested independently:

```python
from supervisor.health import AgentRegistry

def test_agent_registration():
    registry = AgentRegistry()
    registry.register("agent1", "stage")
    assert registry.is_registered("agent1")
    assert registry.get_agent_count() == 1
```

### Integration Tests

Test full workflow:

```python
from supervisor.health import HealthMonitor

def test_health_workflow():
    monitor = HealthMonitor()
    monitor.register_agent("agent1", "stage")
    monitor.agent_heartbeat("agent1", {"progress": 50})
    status = monitor.get_health_status()
    assert status == HealthStatus.HEALTHY
```

## Backward Compatibility

The original monolithic module still works:

```python
# Old import (still works)
from supervisor_health_monitor import HealthMonitor

# New import (recommended)
from supervisor.health import HealthMonitor
```

All public APIs are preserved. The old module is now a wrapper that re-exports from the new package.

## Migration Guide

### For Existing Code

No changes required! The backward compatibility wrapper ensures all imports work.

### For New Code

Use the new import path:

```python
# Recommended
from supervisor.health import (
    HealthMonitor,
    AgentHealthEvent,
    HealthStatus,
    ProcessHealth
)
```

### For Advanced Usage

Import individual components:

```python
from supervisor.health import (
    HealthMonitor,
    AgentRegistry,
    ProcessMonitor,
    CrashDetector,
    ProgressTracker,
    HealthCalculator,
    EventObserver,
    Watchdog
)

# Create custom health monitor
class MyHealthMonitor(HealthMonitor):
    def __init__(self):
        super().__init__()
        # Add custom components
        self.network_monitor = NetworkMonitor()
```

## Performance

### Memory Complexity
- O(n) for n registered agents
- O(m) for m monitored processes
- O(k) for k observers

### CPU Complexity
- Heartbeat: O(1) - dict update
- Stalled count: O(n) - iterate agents
- Health status: O(n) + O(1) - count + threshold lookup
- Watchdog: Configurable interval (default 5s)

### Lock Contention
- Fine-grained locks per component
- Locks held briefly during updates
- No inter-component lock contention

## Extension Points

### Add New Health Check

```python
class NetworkMonitor:
    def check_network_health(self):
        # Custom network checks
        pass

# Inject into HealthMonitor
monitor = HealthMonitor()
monitor.network_monitor = NetworkMonitor()
```

### Add New Observer

```python
class SlackObserver:
    def on_agent_event(self, agent_name, event, data):
        if event == AgentHealthEvent.CRASHED:
            send_slack_alert(f"{agent_name} crashed!")

monitor.register_health_observer(SlackObserver())
```

### Add New Health Status Level

```python
# Add to HealthStatus enum
class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    CRITICAL = "critical"
    EMERGENCY = "emergency"  # New level

# Update HealthCalculator thresholds
calculator.set_threshold(HealthStatus.EMERGENCY, 0.9)
```

## Benefits

1. **Maintainability**: Each module is focused and easy to understand
2. **Testability**: Components can be tested in isolation
3. **Extensibility**: Easy to add new strategies/monitors
4. **Readability**: Clear separation of concerns
5. **Documentation**: Comprehensive WHY/RESPONSIBILITY/PATTERNS
6. **Type Safety**: Full type hints for IDE support
7. **Thread Safety**: Fine-grained locking per component
8. **Zero Breaking Changes**: Backward compatible wrapper

## CLI Interface

The package preserves the CLI interface:

```bash
# Run demo
python supervisor_health_monitor.py --demo

# Show statistics
python supervisor_health_monitor.py --stats
```

## Contributing

When adding new features:
1. Follow WHY/RESPONSIBILITY/PATTERNS documentation style
2. Use guard clauses (max 1 level nesting)
3. Add full type hints
4. Use dispatch tables instead of elif chains
5. Ensure thread safety
6. Write unit tests
7. Update this README

## License

Part of the Artemis Autonomous Development Pipeline.
