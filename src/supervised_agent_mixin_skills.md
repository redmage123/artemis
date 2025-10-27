# Supervised Agent Mixin - Skills

## Overview
**File**: `supervised_agent_mixin.py`
**Purpose**: Add supervision capabilities to any agent
**Pattern**: Mixin class for reusable supervision behavior

## Core Skills

### 1. Health Reporting
- **Heartbeat**: Regular "I'm alive" signals
- **Status Updates**: Progress and current state
- **Error Reporting**: Notify supervisor of failures
- **Metrics**: Performance and resource usage

### 2. Supervised Execution
- **Monitored Operations**: Executes tasks under supervision
- **Timeout Detection**: Detects and reports hanging operations
- **Exception Handling**: Reports exceptions to supervisor
- **Graceful Degradation**: Continues with reduced functionality on failure

### 3. Recovery Participation
- **Restart Capability**: Can be restarted by supervisor
- **State Restoration**: Restores state after restart
- **Checkpoint Support**: Saves progress for recovery
- **Rollback**: Can roll back failed operations

### 4. Communication with Supervisor
- **Health Events**: Sends health status to supervisor
- **Recovery Requests**: Requests supervisor intervention
- **Status Queries**: Responds to supervisor health checks
- **Alert Escalation**: Escalates critical issues

## Usage Patterns

```python
from supervised_agent_mixin import SupervisedAgentMixin
from artemis_stage_interface import LoggerInterface

class MyAgent(SupervisedAgentMixin):
    def __init__(self, logger: LoggerInterface, supervisor):
        # Initialize mixin
        SupervisedAgentMixin.__init__(
            self,
            agent_name="my-agent",
            supervisor=supervisor
        )
        self.logger = logger

    def do_work(self):
        # Send heartbeat
        self.send_heartbeat()

        try:
            # Monitored execution
            result = self.supervised_execute(
                operation=self._risky_operation,
                timeout=30
            )
            return result
        except Exception as e:
            # Report error to supervisor
            self.report_error(e)
            raise

    def _risky_operation(self):
        # Do actual work
        pass
```

## Provided Methods

### Health Monitoring
- `send_heartbeat()` - Periodic health signal
- `report_status(status)` - Send status update
- `report_error(error)` - Report exceptions
- `report_metrics(metrics)` - Send performance data

### Supervised Execution
- `supervised_execute(operation, timeout)` - Execute with monitoring
- `checkpoint(state)` - Save recovery point
- `restore_checkpoint()` - Restore saved state

### Recovery Support
- `restart()` - Handle restart request
- `rollback()` - Undo failed operations
- `get_health()` - Current health status

## Integration with Supervisor

```python
# Supervisor monitors all supervised agents
supervisor = SupervisorAgent(logger=logger)

# Create supervised agents
agent_a = SupervisedAgentMixin(
    agent_name="developer-agent",
    supervisor=supervisor
)

agent_b = SupervisedAgentMixin(
    agent_name="code-review-agent",
    supervisor=supervisor
)

# Supervisor automatically receives health events
supervisor.monitor_agents([agent_a, agent_b])
```

## Design Patterns

- **Mixin Pattern**: Adds supervision to any class
- **Observer Pattern**: Notifies supervisor of events
- **Template Method**: Standard supervision workflow

## Benefits

- **Reusability**: Add to any agent class
- **Consistency**: Standard supervision interface
- **No Duplication**: Shared supervision code
- **Flexible**: Override methods for custom behavior

## Health States

- **HEALTHY**: Operating normally
- **DEGRADED**: Reduced functionality
- **CRITICAL**: Severe issues
- **FAILED**: Not operational
- **RECOVERING**: In recovery process
