# Circuit Breaker Architecture

## Package Structure

```
core/resilience/
├── __init__.py              # Public API exports
├── models.py                # States, config, exceptions (56 lines)
├── state_machine.py         # State transitions (239 lines)
├── failure_detector.py      # Request validation (84 lines)
├── recovery_handler.py      # Success/failure handling (106 lines)
├── circuit_breaker_core.py  # Main facade (228 lines)
├── registry.py              # Global registry (192 lines)
├── cli_demo.py              # CLI interface (148 lines)
└── ARCHITECTURE.md          # This file
```

## Component Relationships

```
┌──────────────────────────────────────────────────────────────┐
│                    CircuitBreaker (Facade)                   │
│                   circuit_breaker_core.py                    │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐│
│  │ StateMachine   │  │FailureDetector │  │RecoveryHandler ││
│  │                │  │                │  │                ││
│  │ - State logic  │  │ - Pre-checks   │  │ - Success/Fail ││
│  │ - Transitions  │  │ - Rejection    │  │ - Callbacks    ││
│  └────────────────┘  └────────────────┘  └────────────────┘│
│          │                    │                    │         │
│          └────────────────────┼────────────────────┘         │
│                               │                              │
│                      ┌────────▼────────┐                     │
│                      │   models.py     │                     │
│                      │                 │                     │
│                      │ - CircuitState  │                     │
│                      │ - Config        │                     │
│                      │ - Exceptions    │                     │
│                      └─────────────────┘                     │
└──────────────────────────────────────────────────────────────┘
                               │
                               │
                      ┌────────▼────────┐
                      │  registry.py    │
                      │                 │
                      │ - Factory       │
                      │ - Lifecycle     │
                      │ - Monitoring    │
                      └─────────────────┘
```

## State Machine

```
                    failure_threshold
         ┌──────────────────────────────────┐
         │                                  │
         │                                  ▼
    ┌────┴─────┐                      ┌─────────┐
    │  CLOSED  │                      │  OPEN   │
    │          │◄─────────────────────┤         │
    │ Normal   │  success_threshold   │ Failing │
    └────┬─────┘                      └────┬────┘
         │                                  │
         │                                  │ timeout_seconds
         │                                  │
         │                            ┌─────▼──────┐
         └────────────────────────────┤ HALF_OPEN  │
              success_threshold       │            │
                                      │  Testing   │
                                      └────────────┘
```

## Design Patterns

### 1. State Pattern
- **Where**: `state_machine.py`
- **Why**: Clean state transitions without complex conditionals
- **States**: CLOSED, OPEN, HALF_OPEN

### 2. Facade Pattern
- **Where**: `circuit_breaker_core.py`
- **Why**: Simple interface hiding complex subsystems
- **Coordinates**: StateMachine, FailureDetector, RecoveryHandler

### 3. Registry Pattern
- **Where**: `registry.py`
- **Why**: Centralized circuit breaker management
- **Features**: Factory, lifecycle, monitoring

### 4. Decorator Pattern
- **Where**: `circuit_breaker_core.py` (@protect)
- **Why**: Non-invasive function protection
- **Usage**: `@breaker.protect`

### 5. Context Manager Pattern
- **Where**: `circuit_breaker_core.py` (__enter__/__exit__)
- **Why**: Block-level protection with automatic cleanup
- **Usage**: `with breaker: ...`

## Guard Clauses Example

**Before** (nested):
```python
if self.state == CircuitState.OPEN:
    if self._should_attempt_reset():
        self._transition_to_half_open()
    else:
        raise CircuitBreakerOpenError(...)
```

**After** (guard clauses):
```python
# Guard: not open, allow
if self.state != CircuitState.OPEN:
    return

# Guard: can reset, transition
if self._should_attempt_reset():
    self._transition_to_half_open()
    return

# Circuit open - reject
raise CircuitBreakerOpenError(...)
```

## Usage Examples

### Basic Decorator
```python
from core.resilience import CircuitBreaker

breaker = CircuitBreaker("api_service")

@breaker.protect
def call_api():
    return external_api.get()
```

### Context Manager
```python
from core.resilience import get_circuit_breaker

breaker = get_circuit_breaker("database")

with breaker:
    result = db.query()
```

### Custom Config
```python
from core.resilience import CircuitBreaker, CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=3,
    timeout_seconds=30,
    success_threshold=2
)

breaker = CircuitBreaker("service", config)
```

## Testing

### Unit Tests
```python
from core.resilience import CircuitBreaker, CircuitBreakerOpenError

breaker = CircuitBreaker("test")

# Test failure detection
for _ in range(breaker.config.failure_threshold):
    try:
        breaker.call(lambda: 1/0)
    except ZeroDivisionError:
        pass

# Verify circuit opened
assert breaker.state == "open"
```

### Integration Tests
```python
from core.resilience import get_circuit_breaker, reset_all_circuit_breakers

# Test registry
breaker1 = get_circuit_breaker("service1")
breaker2 = get_circuit_breaker("service2")

# Test bulk operations
reset_all_circuit_breakers()
```

## Migration Path

### Phase 1: Backward Compatible (Current)
```python
# Old imports still work
from circuit_breaker import CircuitBreaker
```

### Phase 2: Update Imports (Recommended)
```python
# New modular imports
from core.resilience import CircuitBreaker
from core.resilience.registry import get_circuit_breaker
```

### Phase 3: Direct Module Access (Advanced)
```python
# Access internal components
from core.resilience.state_machine import StateMachine
from core.resilience.failure_detector import FailureDetector
```

## Benefits

1. **Modularity**: 8 focused modules vs 1 monolithic file
2. **Testability**: Each component testable in isolation
3. **Maintainability**: Clear responsibilities, easy to modify
4. **Extensibility**: Easy to add new states, strategies
5. **Type Safety**: Complete type hints throughout
6. **Documentation**: WHY/RESPONSIBILITY/PATTERNS on every module

## Performance

- **No overhead**: Thin wrapper pattern
- **Thread-safe**: Lock-based synchronization
- **Efficient**: Early returns, guard clauses
- **Scalable**: O(1) registry lookups

## Future Enhancements

1. **Metrics**: Prometheus integration
2. **Recovery Strategies**: Exponential backoff, jitter
3. **Custom States**: Add DEGRADED state
4. **Callbacks**: Event hooks for state changes
5. **Persistence**: Save/restore circuit state
