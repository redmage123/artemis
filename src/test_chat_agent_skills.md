# Test Chat Agent - Skills

## Overview
**File**: `test_chat_agent.py`
**Purpose**: Automated testing for Artemis Chat Agent
**Single Responsibility**: Validate chat agent functionality

## Core Skills

### 1. Unit Testing
- **Intent Recognition**: Tests command interpretation
- **Response Generation**: Validates response correctness
- **Context Management**: Tests conversation history
- **Error Handling**: Tests error response generation

### 2. Integration Testing
- **Pipeline Integration**: Tests chat → pipeline commands
- **Orchestrator Integration**: Validates task execution
- **State Machine**: Tests state query functionality
- **RAG Integration**: Tests historical data retrieval

### 3. Test Scenarios

#### Status Queries
```python
def test_status_query():
    response = chat.process("What's the status?")
    assert "current status" in response.lower()
    assert response contains pipeline state
```

#### Task Control
```python
def test_start_task():
    response = chat.process("Start task card-123")
    assert "started" in response.lower()
    assert orchestrator.task_started("card-123")
```

#### Error Handling
```python
def test_invalid_command():
    response = chat.process("xyz invalid abc")
    assert "don't understand" in response.lower()
    assert response suggests help
```

#### Context Awareness
```python
def test_context_retention():
    chat.process("Check card-123")
    response = chat.process("What's its status?")
    # Should remember card-123 context
    assert refers to card-123
```

### 4. Mock Testing
- **Mock LLM**: Tests without API calls
- **Mock Orchestrator**: Simulates pipeline
- **Mock RAG**: Simulates database
- **Predictable Responses**: Deterministic test results

### 5. Performance Testing
- **Response Time**: Tests chat latency
- **Concurrent Users**: Multiple simultaneous chats
- **Memory Usage**: Chat history memory footprint
- **LLM Token Usage**: Tracks API costs

## Test Categories

### Functional Tests
- Command interpretation correctness
- Response accuracy
- Context management
- Error handling

### Integration Tests
- Pipeline command execution
- Status query accuracy
- Historical data retrieval
- Multi-agent coordination

### Performance Tests
- Response latency < 2 seconds
- Concurrent chat sessions
- Memory leak detection
- Token usage optimization

### Regression Tests
- Previous bug fixes
- Edge case handling
- Known failure modes

## Test Fixtures

```python
@pytest.fixture
def chat_agent():
    """Create chat agent with mocks"""
    mock_llm = MockLLMClient()
    mock_orchestrator = MockOrchestrator()
    return ArtemisChatAgent(
        llm=mock_llm,
        orchestrator=mock_orchestrator
    )

@pytest.fixture
def sample_conversation():
    """Pre-loaded conversation history"""
    return [
        {"user": "Check card-123", "agent": "Card-123 is in progress"},
        {"user": "Any errors?", "agent": "No errors found"}
    ]
```

## Usage Patterns

```python
# Run all tests
pytest test_chat_agent.py

# Run specific test category
pytest test_chat_agent.py::TestStatusQueries

# Run with coverage
pytest --cov=artemis_chat_agent test_chat_agent.py

# Run performance tests
pytest -m performance test_chat_agent.py
```

## Test Assertions

- **Response Content**: Correct information
- **Response Tone**: Helpful and clear
- **Command Execution**: Pipeline actions triggered
- **State Consistency**: Agent state matches reality
- **Error Messages**: Clear and actionable

## Design Patterns

- **Fixture Pattern**: Reusable test setup
- **Mock Object Pattern**: Isolates dependencies
- **Builder Pattern**: Constructs test scenarios
- **Parameterized Tests**: Multiple test cases

## Coverage Goals

- **Line Coverage**: > 90%
- **Branch Coverage**: > 85%
- **Function Coverage**: 100%
- **Integration Paths**: All critical paths tested

## CI/CD Integration

- **Automated Runs**: On every commit
- **Pre-Commit Hooks**: Run before push
- **Nightly Tests**: Full test suite
- **Performance Benchmarks**: Track over time
