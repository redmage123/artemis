# Supervisor Agent - Skills

## Agent Overview
**File**: `supervisor_agent.py`
**Purpose**: Pipeline health monitoring and graceful recovery orchestration
**Role**: "Traffic cop" for the Artemis pipeline

## Core Skills

### 1. Health Monitoring
- **Process Monitoring**: CPU, memory, and resource tracking
- **Crash Detection**: Identifies agent/stage crashes immediately
- **Hang Detection**: Detects frozen processes using timeout thresholds
- **Stall Detection**: Identifies stages making no progress

### 2. Recovery Orchestration
- **Automatic Retry**: Exponential backoff with configurable attempts
- **Circuit Breaker Pattern**: Prevents cascading failures
- **Graceful Failover**: Switches to backup strategies on failure
- **Graceful Degradation**: Continues with reduced functionality

### 3. Resource Management
- **Process Cleanup**: Terminates zombie processes
- **File Lock Management**: Releases stuck file locks
- **Memory Management**: Detects and handles memory leaks
- **Thread Safety**: Manages concurrent operations

### 4. Learning Engine Integration
- **LLM-Powered Auto-Fix**: Uses LLM to analyze and fix crashes
- **Pattern Recognition**: Learns from repeated failures
- **RAG Storage**: Stores successful recovery patterns
- **Continuous Learning**: Improves recovery strategies over time

### 5. Real-Time Alerting
- **AgentMessenger Integration**: Sends alerts to Slack/Email
- **Severity Levels**: CRITICAL, HIGH, MEDIUM
- **Alert Deduplication**: Prevents alert storms
- **Alert Routing**: Different channels for different severities

### 6. Circuit Breaker Management
- **Per-Stage Circuit Breakers**: Independent failure tracking
- **Auto-Reset**: Circuits auto-close after cooldown period
- **Manual Override**: Allows manual circuit reset
- **State Persistence**: Remembers circuit states across restarts

### 7. Statistics Tracking
- **Recovery Success Rate**: Tracks effectiveness
- **MTTR (Mean Time To Recovery)**: Performance metrics
- **Failure Categorization**: Groups similar failures
- **Trend Analysis**: Identifies deteriorating health

## Key Components

### Delegated Engines
- **HealthMonitor**: Detects crashes, hangs, stalls
- **RecoveryEngine**: Applies recovery strategies
- **CircuitBreakerManager**: Prevents cascading failures
- **LearningEngine**: Learns from unexpected states
- **SupervisorHealthObserver**: Event-driven health monitoring

## Design Philosophy

> **"Orchestrate, don't implement"** - Delegates to specialized engines
> **"Fail gracefully, learn continuously"** - Automated recovery with learning
> **"Observe, don't poll"** - Event-driven health monitoring

## Supervision Flow

1. HealthMonitor detects issue (crash/hang/stall)
2. Notify SupervisorHealthObserver
3. RecoveryEngine attempts recovery
4. If recovery fails, escalate to LearningEngine
5. If learning fails, request manual intervention
6. Track all events and statistics

## SOLID Principles Applied

- **Single Responsibility**: Orchestration only (delegates actual work)
- **Open/Closed**: Extensible via new recovery strategies, learning patterns
- **Liskov Substitution**: Works with any PipelineStage implementation
- **Interface Segregation**: Minimal supervision interface (AgentHealthObserver)
- **Dependency Inversion**: Depends on abstractions (LoggerInterface, PipelineStage)

## Configuration

**Constants**:
- `MAX_RETRY_ATTEMPTS`: Maximum retry attempts (default from artemis_constants)
- `DEFAULT_RETRY_INTERVAL_SECONDS`: Initial retry interval
- `RETRY_BACKOFF_FACTOR`: Exponential backoff multiplier

## Usage Patterns

```python
supervisor = SupervisorAgent(
    logger=logger,
    rag_agent=rag,
    state_machine=state_machine
)

# Monitor pipeline health
supervisor.monitor_pipeline(
    stages=[research, planning, development, testing]
)

# Handle recovery
recovery_result = supervisor.handle_stage_failure(
    stage=failed_stage,
    error=exception
)
```

## Integration Points

- **Cost Tracker**: Budget monitoring and enforcement
- **Config Validator**: Configuration validation
- **Sandbox Executor**: Safe code execution
- **State Machine**: Pipeline state management
- **AgentMessenger**: Alert distribution

## Design Patterns

- **Observer Pattern**: Health monitoring via observers
- **Strategy Pattern**: Recovery policy strategies
- **Facade Pattern**: Unified supervision interface
- **Composite Pattern**: Delegates to specialized engines
- **Template Method**: Standard recovery workflow

## Performance Features

- Event-driven (no polling overhead)
- Async health checks where possible
- Cached recovery patterns
- Efficient resource cleanup
