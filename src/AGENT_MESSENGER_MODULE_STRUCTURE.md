# Agent Messenger Module Structure

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     agent_messenger.py                           │
│                 (Backward Compatibility Wrapper)                 │
│                          98 lines                                │
└─────────────────────────────┬───────────────────────────────────┘
                              │ imports from
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   messaging/agent/__init__.py                    │
│                       (Public API Facade)                        │
│                          89 lines                                │
└─────────────┬───────────────────────────────────────────────────┘
              │ exports
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 messaging/agent/messenger_core.py                │
│                    (Main Orchestration)                          │
│                         460 lines                                │
│                                                                  │
│  AgentMessengerCore (implements MessengerInterface)              │
│  ├─ Coordinates all subsystems                                  │
│  ├─ Implements all interface methods                            │
│  └─ Provides observer pattern hooks                             │
└───┬───────┬──────┬─────────┬────────┬────────┬─────────────────┘
    │       │      │         │        │        │
    │       │      │         │        │        │
    ▼       ▼      ▼         ▼        ▼        ▼
┌──────┐ ┌────┐ ┌────┐   ┌──────┐ ┌──────┐ ┌──────┐
│Models│ │Send│ │Recv│   │Store │ │Queue │ │Logger│
└──────┘ └────┘ └────┘   └──────┘ └──────┘ └──────┘
 193 ln  381 ln 217 ln    314 ln   247 ln   102 ln
```

## Module Dependency Graph

```
messenger_core.py
├── models.py (enums, dataclasses, validators)
├── sender.py
│   └── models.py (MessageType, normalize_priority)
├── receiver.py
│   └── message_queue.py
│       └── models.py (get_priority_order)
├── message_storage.py
├── message_queue.py
│   └── models.py (get_priority_order)
└── logger.py
```

## Component Interactions

```
┌─────────────────────────────────────────────────────────────────┐
│                     AgentMessengerCore                           │
└─────────────┬───────────────────────────────────────────────────┘
              │
              ├─── send_message() ───────────────┐
              │                                   ▼
              │                          ┌─────────────────┐
              │                          │  MessageSender  │
              │                          │  ┌────────────┐ │
              │                          │  │ Builder    │ │
              │                          │  │ Generator  │ │
              │                          │  │ Convenience│ │
              │                          │  └────────────┘ │
              │                          └────────┬────────┘
              │                                   │
              │                                   ▼
              │                          ┌─────────────────┐
              │                          │ MessageStorage  │
              │                          │  save_message() │
              │                          └─────────────────┘
              │
              ├─── read_messages() ──────────────┐
              │                                   ▼
              │                          ┌─────────────────┐
              │                          │MessageReceiver  │
              │                          │  ┌────────────┐ │
              │                          │  │ Reader     │ │
              │                          │  │ Queue      │ │
              │                          │  │ Observer   │ │
              │                          │  └────────────┘ │
              │                          └────────┬────────┘
              │                                   │
              │                                   ▼
              │                          ┌─────────────────┐
              │                          │ MessageStorage  │
              │                          │ load_messages() │
              │                          └─────────────────┘
              │
              ├─── update_shared_state() ────────┐
              │                                   ▼
              │                          ┌─────────────────┐
              │                          │  StateStorage   │
              │                          │  update_state() │
              │                          └─────────────────┘
              │
              ├─── register_agent() ─────────────┐
              │                                   ▼
              │                          ┌─────────────────┐
              │                          │RegistryStorage  │
              │                          │register_agent() │
              │                          └─────────────────┘
              │
              └─── all operations ───────────────┐
                                                  ▼
                                         ┌─────────────────┐
                                         │  MessageLogger  │
                                         │  log_message()  │
                                         └─────────────────┘
```

## Data Flow: Send Message

```
Client Code
    │
    ├─ messenger.send_message(to_agent, type, data, ...)
    │
    ▼
AgentMessengerCore
    │
    ├─ sender.send(...)
    │
    ▼
MessageSender
    │
    ├─ builder.build_message(...)
    │   │
    │   ├─ id_generator.generate(data)
    │   └─ normalize_priority(priority)
    │
    ├─ if to_agent == "all":
    │   │
    │   ├─ registry_storage.load_registry()
    │   ├─ broadcast_queue.get_recipients()
    │   └─ for each recipient:
    │       └─ storage.save_message(recipient, message)
    │
    └─ else:
        └─ storage.save_message(to_agent, message)
    │
    └─ logger.log_message(message, "sent")
```

## Data Flow: Read Messages

```
Client Code
    │
    ├─ messenger.read_messages(filters...)
    │
    ▼
AgentMessengerCore
    │
    ├─ receiver.receive(filters...)
    │
    ▼
MessageReceiver
    │
    ├─ storage.load_messages(agent_name, unread_only)
    │   └─ returns List[Path]
    │
    ├─ reader.read_messages_from_files(files, filters...)
    │   │
    │   ├─ queue.add_filter(type, value) for each filter
    │   ├─ for each file:
    │   │   └─ load_message_from_file()
    │   │
    │   ├─ queue.apply_filters(messages)
    │   └─ queue.sort_by_priority(filtered)
    │
    ├─ if mark_as_read:
    │   │
    │   ├─ create_message_file_map()
    │   └─ for each message:
    │       ├─ storage.mark_message_read(filepath)
    │       └─ logger.log_message(message, "received")
    │
    ├─ for each message:
    │   └─ observer.notify(message)
    │
    └─ return messages
```

## Class Relationships

### Composition

```
AgentMessengerCore
    HAS-A MessageStorage
    HAS-A StateStorage
    HAS-A RegistryStorage
    HAS-A MessageSender
        HAS-A MessageBuilder
            HAS-A MessageIdGenerator
        HAS-A ConvenienceMessageSender
    HAS-A MessageReceiver
        HAS-A MessageReader
            HAS-A MessageQueue
    HAS-A MessageLogger
    HAS-A MessageObserver
```

### Inheritance

```
MessengerInterface (ABC)
    ↑
    │ implements
    │
AgentMessengerCore
```

## Design Pattern Mapping

| Pattern | Module | Class/Function |
|---------|--------|----------------|
| **Facade** | messenger_core.py | AgentMessengerCore |
| **Repository** | message_storage.py | MessageStorage, StateStorage, RegistryStorage |
| **Builder** | sender.py | MessageBuilder |
| **Factory** | sender.py | MessageIdGenerator |
| **Observer** | receiver.py | MessageObserver |
| **Strategy** | message_queue.py | MessageFilter |
| **Chain of Responsibility** | message_queue.py | MessageQueue.apply_filters() |
| **Dependency Injection** | messenger_core.py | Callback parameters |
| **Value Object** | models.py | Enums (MessageType, etc.) |
| **DTO** | models.py | Dataclasses |

## Type Safety Flow

```
Client Code
    │
    ├─ from messaging.agent import MessageType
    │
    ├─ messenger.send_message(
    │       message_type=MessageType.DATA_UPDATE.value
    │   )
    │
    ▼
MessageSender
    │
    ├─ MessageBuilder.build_message()
    │   └─ normalize_priority(priority)
    │       └─ Returns: MessagePriority enum value
    │
    └─ Message object created with validated types
```

## Guard Clause Pattern

All modules use guard clauses to reduce nesting:

```python
# Example from message_storage.py
def cleanup_old_messages(self, agent_name: str, days: int = 7) -> int:
    inbox = self.message_dir / agent_name

    # Guard clause: inbox doesn't exist
    if not inbox.exists():
        return 0

    cutoff = datetime.utcnow() - timedelta(days=days)
    deleted_count = 0

    for filepath in inbox.glob("*.json.read"):
        mtime = datetime.fromtimestamp(filepath.stat().st_mtime)

        # Guard clause: file is newer than cutoff
        if mtime >= cutoff:
            continue

        filepath.unlink()
        deleted_count += 1

    return deleted_count
```

## Observer Pattern Implementation

```
MessageObserver
    ├─ observers: List[Callable]
    │
    ├─ subscribe(observer: Callable)
    │   └─ observers.append(observer)
    │
    ├─ unsubscribe(observer: Callable)
    │   └─ observers.remove(observer)
    │
    └─ notify(message: Message)
        └─ for observer in observers:
                observer(message)

Usage:
    messenger = AgentMessenger("agent-name")
    messenger.subscribe_to_messages(my_callback)
    messages = messenger.read_messages()  # triggers notify()
```

## Module Size Distribution

```
messenger_core.py  ████████████████████████████████████████████  460 lines
sender.py          ████████████████████████████████████          381 lines
message_storage.py ███████████████████████████████              314 lines
message_queue.py   ████████████████████                          247 lines
receiver.py        █████████████████████                         217 lines
models.py          ███████████████████                           193 lines
logger.py          ██████████                                    102 lines
__init__.py        ████████                                       89 lines
```

All modules stay under 500 lines with most under 250 lines for optimal maintainability.

## Import Paths

### Recommended (New Code)
```python
from messaging.agent import AgentMessenger, MessageType, MessagePriority
```

### Backward Compatible (Existing Code)
```python
from agent_messenger import AgentMessenger
```

### Internal Module Imports
```python
# In messenger_core.py
from messaging.agent.message_storage import MessageStorage, StateStorage
from messaging.agent.sender import MessageSender, ConvenienceMessageSender
from messaging.agent.receiver import MessageReceiver, MessageObserver
from messaging.agent.logger import MessageLogger
from messaging.agent.models import MessageType, normalize_priority
```

## Testing Strategy

Each module can be tested independently:

```python
# Test MessageBuilder
from messaging.agent.sender import MessageBuilder
builder = MessageBuilder("test-agent")
message = builder.build_message(...)
assert message.from_agent == "test-agent"

# Test MessageFilter
from messaging.agent.message_queue import MessageFilter
assert MessageFilter.by_message_type(message, "data_update")

# Test StateStorage
from messaging.agent.message_storage import StateStorage
storage = StateStorage("/tmp/test_state.json")
storage.update_state("card-123", "agent", {"key": "value"})
```

## Extensibility Points

1. **New Message Types**: Add to `MessageType` enum
2. **New Storage Backends**: Implement new storage classes
3. **New Filters**: Add methods to `MessageFilter`
4. **Message Observers**: Subscribe with `subscribe_to_messages()`
5. **Custom Loggers**: Replace `MessageLogger` instance
6. **Priority Schemes**: Modify `get_priority_order()` dispatch table

## Summary

The modular structure provides:
- **Clear separation of concerns** (8 focused modules)
- **Type safety** (enums and type hints throughout)
- **Testability** (isolated components with clear interfaces)
- **Extensibility** (observer pattern and dispatch tables)
- **Maintainability** (guard clauses, documentation, small modules)
- **Backward compatibility** (wrapper preserves existing API)
