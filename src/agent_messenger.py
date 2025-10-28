#!/usr/bin/env python3
"""
Agent Messenger - File-Based Inter-Agent Communication System

BACKWARD COMPATIBILITY WRAPPER

This file maintains backward compatibility with existing code that imports
from agent_messenger.py. All functionality has been refactored into the
messaging.agent package for better modularity and maintainability.

WHY: Ensure existing code continues to work without modification.
RESPONSIBILITY: Re-export classes and functions from new package structure.
PATTERNS: Facade Pattern, Deprecation Wrapper.

New code should import from:
    from messaging.agent import AgentMessenger, send_update, send_notification, send_error

This wrapper will be maintained until all imports are migrated.
"""

# Import from new modular package
from messaging.agent import (
    AgentMessenger,
    MessageType,
    MessagePriority,
    AgentStatus,
    send_update,
    send_notification,
    send_error
)

# Maintain backward compatibility for direct imports
__all__ = [
    "AgentMessenger",
    "MessageType",
    "MessagePriority",
    "AgentStatus",
    "send_update",
    "send_notification",
    "send_error",
]


# Example usage (preserved from original)
if __name__ == "__main__":
    # Example usage
    print("Agent Messenger - Example Usage")
    print("=" * 60)

    # Create messenger for architecture agent
    arch = AgentMessenger("architecture-agent")

    # Register agent
    arch.register_agent(capabilities=[
        "create_adr",
        "evaluate_options",
        "document_decisions"
    ])

    # Send data update
    msg_id = arch.send_data_update(
        to_agent="dependency-validation-agent",
        card_id="card-123",
        update_type="adr_created",
        data={
            "adr_file": "/tmp/adr/ADR-001.md",
            "dependencies": ["chromadb>=0.4.0"]
        }
    )
    print(f"✅ Sent message: {msg_id}")

    # Update shared state
    arch.update_shared_state(
        card_id="card-123",
        updates={
            "agent_status": "COMPLETE",
            "adr_file": "/tmp/adr/ADR-001.md"
        }
    )
    print("✅ Updated shared state")

    # Read messages (as dependency validation agent)
    dep_val = AgentMessenger("dependency-validation-agent")
    messages = dep_val.read_messages()
    print(f"✅ Read {len(messages)} messages")

    for msg in messages:
        print(f"\n  From: {msg.from_agent}")
        print(f"  Type: {msg.message_type}")
        print(f"  Data: {msg.data}")

    # Get shared state
    state = dep_val.get_shared_state(card_id="card-123")
    print(f"\n✅ Shared state:")
    print(f"  ADR File: {state.get('shared_data', {}).get('adr_file')}")

    print("\n" + "=" * 60)
    print("Example complete!")
