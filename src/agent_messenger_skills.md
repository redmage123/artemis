# Agent Messenger - Skills

## Agent Overview
**File**: `agent_messenger.py`
**Purpose**: File-based inter-agent communication system
**Single Responsibility**: Enable standardized message passing between pipeline agents

## Core Skills

### 1. Message Passing
- **Send Messages**: Post messages to other agents
- **Read Messages**: Retrieve incoming messages from inbox
- **Message Types**: `data_update`, `alert`, `status`, `request`, `response`
- **Routing**: Agent-to-agent message delivery
- **Card-Scoped**: Messages associated with specific cards

### 2. Shared State Management
- **State Updates**: Update shared pipeline state
- **State Retrieval**: Read current shared state
- **Card Context**: Per-card state isolation
- **Atomic Updates**: Thread-safe state modifications

### 3. File-Based Storage
- **JSON Messages**: Human-readable message format
- **Inbox System**: Per-agent message directories
- **Shared State File**: Central state storage
- **Message Archive**: Historical message log

### 4. Protocol Compliance
- **Protocol Version**: 1.0.0
- **Standardized Format**: Consistent message structure
- **Message Interface**: Implements MessengerInterface
- **Backward Compatibility**: Version tracking

## Message Structure

```json
{
  "message_id": "msg-abc123",
  "protocol_version": "1.0.0",
  "timestamp": "2025-10-27T10:30:00",
  "from_agent": "architecture-agent",
  "to_agent": "dependency-validation-agent",
  "message_type": "data_update",
  "card_id": "card-20251027-001",
  "data": {
    "adr_file": "/tmp/adr/ADR-001.md",
    "status": "ready"
  }
}
```

## Shared State Structure

```json
{
  "card-20251027-001": {
    "adr_file": "/tmp/adr/ADR-001.md",
    "status": "in_progress",
    "last_updated": "2025-10-27T10:30:00",
    "updated_by": "architecture-agent"
  }
}
```

## Usage Patterns

```python
# Initialize messenger
messenger = AgentMessenger("supervisor-agent")

# Send message to another agent
messenger.send_message(
    to_agent="developer-agent",
    message_type="request",
    card_id="card-123",
    data={"action": "implement_feature", "priority": "high"}
)

# Read incoming messages
messages = messenger.read_messages()
for msg in messages:
    print(f"From: {msg.from_agent}, Type: {msg.message_type}")
    process_message(msg)

# Update shared state
messenger.update_shared_state(
    card_id="card-123",
    updates={"status": "code_review", "reviewer": "code-review-agent"}
)

# Read shared state
state = messenger.get_shared_state(card_id="card-123")
```

## Design Patterns

- **Mediator Pattern**: Centralizes inter-agent communication
- **Message Queue**: Inbox-based message delivery
- **Shared Memory**: Central state storage

## Integration Points

- **All Pipeline Agents**: Every agent can communicate
- **Supervisor**: Broadcasts alerts and status updates
- **Orchestrator**: Coordinates agent workflows
- **State Machine**: Synchronizes pipeline state

## File Structure

```
.artemis_data/
  agent_messages/
    supervisor-agent/
      inbox/
        msg-abc123.json
    developer-agent/
      inbox/
        msg-def456.json
    shared_state.json
```

## Message Types

- **data_update**: Share data between agents
- **alert**: Critical notifications
- **status**: Status updates and progress
- **request**: Request action from another agent
- **response**: Response to a request

## Thread Safety

- **Atomic Writes**: File write operations are atomic
- **Lock-Free Reads**: Multiple agents can read concurrently
- **Message Deduplication**: Prevents duplicate message processing

## Performance Features

- **No Network Overhead**: File-based (no TCP/HTTP)
- **Fast Local I/O**: Filesystem performance
- **Lazy Loading**: Messages loaded on-demand
- **Clean Up**: Old messages archived or deleted
