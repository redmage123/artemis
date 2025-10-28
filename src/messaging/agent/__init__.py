#!/usr/bin/env python3
"""
WHY: Provide clean public API for agent messaging system.
RESPONSIBILITY: Export public classes and convenience functions.
PATTERNS: Facade Pattern, API Design.

Package: messaging.agent
Purpose: File-based inter-agent communication system

Public API:
- AgentMessenger: Main messenger class (backward compatible)
- MessageType: Message type enumeration
- MessagePriority: Priority enumeration
- send_update: Quick send data update
- send_notification: Quick send broadcast notification
- send_error: Quick send error
"""

from messaging.agent.messenger_core import AgentMessengerCore
from messaging.agent.models import MessageType, MessagePriority, AgentStatus

# Main public class (backward compatible name)
AgentMessenger = AgentMessengerCore


# Convenience functions for quick usage

def send_update(from_agent: str, to_agent: str, card_id: str, **data):
    """
    WHY: Quick send data update without creating messenger instance.
    RESPONSIBILITY: Create messenger and send update in one call.

    Args:
        from_agent: Sender agent name
        to_agent: Recipient agent name
        card_id: Card ID
        **data: Update data

    Returns:
        Message ID
    """
    messenger = AgentMessenger(from_agent)
    return messenger.send_data_update(to_agent, card_id, "update", data)


def send_notification(from_agent: str, card_id: str, **data):
    """
    WHY: Quick send broadcast notification.
    RESPONSIBILITY: Create messenger and send notification to all.

    Args:
        from_agent: Sender agent name
        card_id: Card ID
        **data: Notification data

    Returns:
        Message ID
    """
    messenger = AgentMessenger(from_agent)
    return messenger.send_notification("all", card_id, "notification", data)


def send_error(from_agent: str, to_agent: str, card_id: str, error: str):
    """
    WHY: Quick send error message.
    RESPONSIBILITY: Create messenger and send error.

    Args:
        from_agent: Sender agent name
        to_agent: Recipient agent name
        card_id: Card ID
        error: Error message

    Returns:
        Message ID
    """
    messenger = AgentMessenger(from_agent)
    return messenger.send_error(to_agent, card_id, "error", error)


__all__ = [
    "AgentMessenger",
    "MessageType",
    "MessagePriority",
    "AgentStatus",
    "send_update",
    "send_notification",
    "send_error",
]
