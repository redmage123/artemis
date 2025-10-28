#!/usr/bin/env python3
"""
WHY: Handle message sending operations with type safety and validation.
RESPONSIBILITY: Compose and send messages to other agents.
PATTERNS: Builder Pattern, Factory Pattern, Single Responsibility.

This module provides:
- Message composition and validation
- Message ID generation
- Convenience methods for common message types
- Broadcast message handling
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

from messenger_interface import Message
from messaging.agent.models import MessageType, normalize_priority


class MessageIdGenerator:
    """
    WHY: Generate unique, traceable message IDs.
    RESPONSIBILITY: Create collision-resistant message identifiers.
    """

    def __init__(self, agent_name: str):
        """
        Initialize message ID generator

        Args:
            agent_name: Agent name for ID prefix
        """
        self.agent_name = agent_name
        self.sequence = 0

    def generate(self, data: Dict[str, Any]) -> str:
        """
        WHY: Create unique message ID with timestamp and hash.
        RESPONSIBILITY: Generate ID that's sortable and traceable.

        Args:
            data: Message data for hash generation

        Returns:
            Unique message ID
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        data_hash = hashlib.md5(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()[:8]
        self.sequence += 1

        return f"msg-{timestamp}-{self.agent_name}-{self.sequence}-{data_hash}"


class MessageBuilder:
    """
    WHY: Build messages with validation using builder pattern.
    RESPONSIBILITY: Construct valid Message objects with defaults.
    """

    PROTOCOL_VERSION = "1.0.0"

    def __init__(self, agent_name: str):
        """
        Initialize message builder

        Args:
            agent_name: Sender agent name
        """
        self.agent_name = agent_name
        self.id_generator = MessageIdGenerator(agent_name)

    def build_message(
        self,
        to_agent: str,
        message_type: str,
        card_id: str,
        data: Dict[str, Any],
        priority: str = "medium",
        metadata: Optional[Dict] = None
    ) -> Message:
        """
        WHY: Construct message with validation and defaults.
        RESPONSIBILITY: Build complete Message object.

        Args:
            to_agent: Recipient agent name
            message_type: Type of message
            card_id: Associated card ID
            data: Message payload
            priority: Message priority
            metadata: Optional metadata

        Returns:
            Constructed Message object
        """
        return Message(
            protocol_version=self.PROTOCOL_VERSION,
            message_id=self.id_generator.generate(data),
            timestamp=datetime.utcnow().isoformat() + 'Z',
            from_agent=self.agent_name,
            to_agent=to_agent,
            message_type=message_type,
            card_id=card_id,
            priority=normalize_priority(priority),
            data=data,
            metadata=metadata or {}
        )


class MessageSender:
    """
    WHY: Send messages with routing logic.
    RESPONSIBILITY: Route messages to recipients and handle broadcasts.
    """

    def __init__(self, agent_name: str, save_callback: Callable, log_callback: Callable):
        """
        Initialize message sender

        Args:
            agent_name: Sender agent name
            save_callback: Callback to save message
            log_callback: Callback to log message
        """
        self.agent_name = agent_name
        self.builder = MessageBuilder(agent_name)
        self.save_callback = save_callback
        self.log_callback = log_callback

    def send(
        self,
        to_agent: str,
        message_type: str,
        data: Dict[str, Any],
        card_id: str,
        priority: str = "medium",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        WHY: Send message with routing and logging.
        RESPONSIBILITY: Build message, route to recipient(s), log operation.

        Args:
            to_agent: Recipient agent name or "all" for broadcast
            message_type: Type of message
            data: Message payload
            card_id: Associated card ID
            priority: Message priority
            metadata: Optional metadata

        Returns:
            Message ID
        """
        message = self.builder.build_message(
            to_agent=to_agent,
            message_type=message_type,
            card_id=card_id,
            data=data,
            priority=priority,
            metadata=metadata
        )

        # Route message
        if to_agent == "all":
            self._broadcast(message)
        else:
            self.save_callback(to_agent, message)

        # Log the send
        self.log_callback(message, direction="sent")

        return message.message_id

    def _broadcast(self, message: Message) -> None:
        """
        WHY: Send message to all registered agents.
        RESPONSIBILITY: Delegate to broadcast callback.

        Args:
            message: Message to broadcast
        """
        # Delegate to broadcast callback
        # This will be set by the messenger core
        if hasattr(self, 'broadcast_callback'):
            self.broadcast_callback(message)


class ConvenienceMessageSender:
    """
    WHY: Provide type-safe convenience methods for common messages.
    RESPONSIBILITY: Simplify message sending with semantic method names.
    """

    def __init__(self, sender: MessageSender):
        """
        Initialize convenience sender

        Args:
            sender: MessageSender instance
        """
        self.sender = sender

    def send_data_update(
        self,
        to_agent: str,
        card_id: str,
        update_type: str,
        data: Dict[str, Any],
        priority: str = "medium"
    ) -> str:
        """
        WHY: Send data update with semantic method name.
        RESPONSIBILITY: Compose data update message.

        Args:
            to_agent: Recipient agent name
            card_id: Card ID
            update_type: Type of update
            data: Update data
            priority: Message priority

        Returns:
            Message ID
        """
        return self.sender.send(
            to_agent=to_agent,
            message_type=MessageType.DATA_UPDATE.value,
            card_id=card_id,
            priority=priority,
            data={"update_type": update_type, **data}
        )

    def send_request(
        self,
        to_agent: str,
        card_id: str,
        request_type: str,
        requirements: Dict[str, Any],
        timeout_seconds: int = 300,
        priority: str = "medium"
    ) -> str:
        """
        WHY: Send request with timeout metadata.
        RESPONSIBILITY: Compose request message with metadata.

        Args:
            to_agent: Recipient agent name
            card_id: Card ID
            request_type: Type of request
            requirements: Request requirements
            timeout_seconds: Request timeout
            priority: Message priority

        Returns:
            Message ID
        """
        return self.sender.send(
            to_agent=to_agent,
            message_type=MessageType.REQUEST.value,
            card_id=card_id,
            priority=priority,
            data={
                "request_type": request_type,
                "requirements": requirements
            },
            metadata={
                "requires_response": True,
                "timeout_seconds": timeout_seconds
            }
        )

    def send_response(
        self,
        to_agent: str,
        card_id: str,
        in_response_to: str,
        response_type: str,
        data: Dict[str, Any],
        priority: str = "medium"
    ) -> str:
        """
        WHY: Send response to a request.
        RESPONSIBILITY: Compose response message with reference.

        Args:
            to_agent: Recipient agent name
            card_id: Card ID
            in_response_to: Original message ID
            response_type: Type of response
            data: Response data
            priority: Message priority

        Returns:
            Message ID
        """
        return self.sender.send(
            to_agent=to_agent,
            message_type=MessageType.RESPONSE.value,
            card_id=card_id,
            priority=priority,
            data={
                "response_type": response_type,
                "in_response_to": in_response_to,
                **data
            }
        )

    def send_notification(
        self,
        to_agent: str,
        card_id: str,
        notification_type: str,
        data: Dict[str, Any],
        priority: str = "low"
    ) -> str:
        """
        WHY: Send notification (low priority by default).
        RESPONSIBILITY: Compose notification message.

        Args:
            to_agent: Recipient agent name
            card_id: Card ID
            notification_type: Type of notification
            data: Notification data
            priority: Message priority (default: low)

        Returns:
            Message ID
        """
        return self.sender.send(
            to_agent=to_agent,
            message_type=MessageType.NOTIFICATION.value,
            card_id=card_id,
            priority=priority,
            data={"notification_type": notification_type, **data}
        )

    def send_error(
        self,
        to_agent: str,
        card_id: str,
        error_type: str,
        message: str,
        severity: str = "high",
        blocks_pipeline: bool = True,
        resolution_suggestions: Optional[List[str]] = None
    ) -> str:
        """
        WHY: Send error message (high priority).
        RESPONSIBILITY: Compose error message with severity.

        Args:
            to_agent: Recipient agent name
            card_id: Card ID
            error_type: Type of error
            message: Error message
            severity: Error severity
            blocks_pipeline: Whether error blocks pipeline
            resolution_suggestions: Suggested resolutions

        Returns:
            Message ID
        """
        return self.sender.send(
            to_agent=to_agent,
            message_type=MessageType.ERROR.value,
            card_id=card_id,
            priority="high",
            data={
                "error_type": error_type,
                "severity": severity,
                "message": message,
                "blocks_pipeline": blocks_pipeline,
                "resolution_suggestions": resolution_suggestions or []
            }
        )
