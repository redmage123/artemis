#!/usr/bin/env python3
"""
WHY: Orchestrate agent messaging system with all components.
RESPONSIBILITY: Main messenger implementation integrating all subsystems.
PATTERNS: Facade Pattern, Dependency Injection, Single Responsibility.

This module provides:
- Complete messenger implementation
- Component coordination
- Interface implementation
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from messenger_interface import MessengerInterface, Message
from messaging.agent.message_storage import MessageStorage, StateStorage, RegistryStorage
from messaging.agent.sender import MessageSender, ConvenienceMessageSender
from messaging.agent.receiver import MessageReceiver, MessageObserver
from messaging.agent.logger import MessageLogger
from messaging.agent.message_queue import BroadcastQueue


class AgentMessengerCore(MessengerInterface):
    """
    WHY: Provide file-based agent messaging implementation.
    RESPONSIBILITY: Coordinate all messaging subsystems via facade pattern.

    This class integrates:
    - Message storage (persistence)
    - Message sending (composition and routing)
    - Message receiving (filtering and retrieval)
    - Message logging (audit trail)
    - State management (shared pipeline state)
    - Agent registry (discovery)
    """

    PROTOCOL_VERSION = "1.0.0"

    def __init__(self, agent_name: str, message_dir: str = "../../.artemis_data/agent_messages"):
        """
        Initialize agent messenger

        Args:
            agent_name: Name of this agent
            message_dir: Base directory for message storage
        """
        self.agent_name = agent_name

        # Convert relative path to absolute
        if not os.path.isabs(message_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            message_dir = os.path.join(script_dir, message_dir)

        self.message_dir = Path(message_dir)

        # Initialize subsystems
        self._init_storage()
        self._init_messaging()
        self._init_observers()

    def _init_storage(self) -> None:
        """
        WHY: Initialize storage subsystems.
        RESPONSIBILITY: Create storage components.
        """
        self.storage = MessageStorage(str(self.message_dir))
        self.state_storage = StateStorage()
        self.registry_storage = RegistryStorage()
        self.logger = MessageLogger(self.message_dir, self.agent_name)

    def _init_messaging(self) -> None:
        """
        WHY: Initialize messaging subsystems.
        RESPONSIBILITY: Create sender and receiver components.
        """
        # Create sender with callbacks
        self.sender = MessageSender(
            agent_name=self.agent_name,
            save_callback=self._save_message,
            log_callback=self.logger.log_message
        )

        # Set broadcast callback
        self.sender.broadcast_callback = self._broadcast_message

        # Create convenience sender
        self.convenience_sender = ConvenienceMessageSender(self.sender)

        # Create receiver with callbacks
        self.receiver = MessageReceiver(
            agent_name=self.agent_name,
            load_callback=self.storage.load_messages,
            mark_read_callback=self.storage.mark_message_read,
            log_callback=self.logger.log_message
        )

    def _init_observers(self) -> None:
        """
        WHY: Initialize observer pattern for notifications.
        RESPONSIBILITY: Create observer system.
        """
        self.observer = MessageObserver()

    def _save_message(self, to_agent: str, message: Message) -> None:
        """
        WHY: Save message to recipient's inbox.
        RESPONSIBILITY: Delegate to storage subsystem.

        Args:
            to_agent: Recipient agent name
            message: Message to save
        """
        self.storage.save_message(to_agent, self.agent_name, message)

    def _broadcast_message(self, message: Message) -> None:
        """
        WHY: Broadcast message to all registered agents.
        RESPONSIBILITY: Get recipients and save to each inbox.

        Args:
            message: Message to broadcast
        """
        registry = self.registry_storage.load_registry()
        broadcast_queue = BroadcastQueue(registry)
        recipients = broadcast_queue.get_broadcast_recipients(self.agent_name)

        for recipient in recipients:
            self.storage.save_message(recipient, self.agent_name, message)

    # MessengerInterface implementation

    def send_message(
        self,
        to_agent: str,
        message_type: str,
        data: Dict,
        card_id: str,
        priority: str = "medium",
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Send message to another agent (MessengerInterface implementation)

        Args:
            to_agent: Recipient agent name
            message_type: Type of message
            data: Message payload
            card_id: Associated card ID
            priority: Message priority
            metadata: Optional metadata

        Returns:
            Message ID
        """
        return self.sender.send(
            to_agent=to_agent,
            message_type=message_type,
            data=data,
            card_id=card_id,
            priority=priority,
            metadata=metadata
        )

    def read_messages(
        self,
        message_type: Optional[str] = None,
        from_agent: Optional[str] = None,
        priority: Optional[str] = None,
        unread_only: bool = True,
        mark_as_read: bool = True
    ) -> List[Message]:
        """
        Read messages from inbox (MessengerInterface implementation)

        Args:
            message_type: Filter by message type
            from_agent: Filter by sender
            priority: Filter by priority
            unread_only: Only unread messages
            mark_as_read: Mark messages as read after retrieval

        Returns:
            List of Message objects
        """
        messages = self.receiver.receive(
            message_type=message_type,
            from_agent=from_agent,
            priority=priority,
            unread_only=unread_only,
            mark_as_read=mark_as_read
        )

        # Notify observers
        for message in messages:
            self.observer.notify(message)

        return messages

    def send_data_update(
        self,
        to_agent: str,
        card_id: str,
        update_type: str,
        data: Dict,
        priority: str = "medium"
    ) -> str:
        """
        Send data update (MessengerInterface implementation)

        Args:
            to_agent: Recipient agent name
            card_id: Card ID
            update_type: Type of update
            data: Update data
            priority: Message priority

        Returns:
            Message ID
        """
        return self.convenience_sender.send_data_update(
            to_agent=to_agent,
            card_id=card_id,
            update_type=update_type,
            data=data,
            priority=priority
        )

    def send_request(
        self,
        to_agent: str,
        card_id: str,
        request_type: str,
        requirements: Dict,
        timeout_seconds: int = 300,
        priority: str = "medium"
    ) -> str:
        """
        Send request (MessengerInterface implementation)

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
        return self.convenience_sender.send_request(
            to_agent=to_agent,
            card_id=card_id,
            request_type=request_type,
            requirements=requirements,
            timeout_seconds=timeout_seconds,
            priority=priority
        )

    def send_response(
        self,
        to_agent: str,
        card_id: str,
        in_response_to: str,
        response_type: str,
        data: Dict,
        priority: str = "medium"
    ) -> str:
        """
        Send response (MessengerInterface implementation)

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
        return self.convenience_sender.send_response(
            to_agent=to_agent,
            card_id=card_id,
            in_response_to=in_response_to,
            response_type=response_type,
            data=data,
            priority=priority
        )

    def send_notification(
        self,
        to_agent: str,
        card_id: str,
        notification_type: str,
        data: Dict,
        priority: str = "low"
    ) -> str:
        """
        Send notification (MessengerInterface implementation)

        Args:
            to_agent: Recipient agent name
            card_id: Card ID
            notification_type: Type of notification
            data: Notification data
            priority: Message priority

        Returns:
            Message ID
        """
        return self.convenience_sender.send_notification(
            to_agent=to_agent,
            card_id=card_id,
            notification_type=notification_type,
            data=data,
            priority=priority
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
        Send error (MessengerInterface implementation)

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
        return self.convenience_sender.send_error(
            to_agent=to_agent,
            card_id=card_id,
            error_type=error_type,
            message=message,
            severity=severity,
            blocks_pipeline=blocks_pipeline,
            resolution_suggestions=resolution_suggestions
        )

    def update_shared_state(self, card_id: str, updates: Dict):
        """
        Update shared pipeline state (MessengerInterface implementation)

        Args:
            card_id: Card ID
            updates: Dictionary of updates to apply
        """
        self.state_storage.update_state(card_id, self.agent_name, updates)

    def get_shared_state(self, card_id: str = None) -> Dict:
        """
        Get current shared pipeline state (MessengerInterface implementation)

        Args:
            card_id: Optional card ID to filter

        Returns:
            Shared state dictionary
        """
        state = self.state_storage.load_state()

        # Guard clause: filter by card_id if provided
        if card_id and state.get("card_id") != card_id:
            return {}

        return state

    def register_agent(self, capabilities: List[str], status: str = "active"):
        """
        Register agent in agent registry (MessengerInterface implementation)

        Args:
            capabilities: List of agent capabilities
            status: Agent status
        """
        inbox_path = str(self.message_dir / self.agent_name)

        self.registry_storage.register_agent(
            agent_name=self.agent_name,
            capabilities=capabilities,
            status=status,
            message_endpoint=inbox_path
        )

    def send_heartbeat(self):
        """
        WHY: Update agent's last heartbeat timestamp.
        RESPONSIBILITY: Signal agent is still active.
        """
        self.registry_storage.update_heartbeat(self.agent_name)

    def cleanup_old_messages(self, days: int = 7) -> int:
        """
        WHY: Clean up old read messages.
        RESPONSIBILITY: Delegate to storage subsystem.

        Args:
            days: Delete messages older than this many days

        Returns:
            Number of messages deleted
        """
        return self.storage.cleanup_old_messages(self.agent_name, days)

    def cleanup(self):
        """
        Cleanup resources (MessengerInterface implementation)

        For file-based messenger, this cleans up old messages.
        """
        self.cleanup_old_messages(days=7)

    def get_messenger_type(self) -> str:
        """
        Get messenger implementation type (MessengerInterface implementation)

        Returns:
            "file" - indicating file-based messenger
        """
        return "file"

    # Observer pattern methods

    def subscribe_to_messages(self, observer_callback: callable) -> None:
        """
        WHY: Allow components to observe message receipt.
        RESPONSIBILITY: Register observer for notifications.

        Args:
            observer_callback: Callback function for message notifications
        """
        self.observer.subscribe(observer_callback)

    def unsubscribe_from_messages(self, observer_callback: callable) -> None:
        """
        WHY: Remove component from message notifications.
        RESPONSIBILITY: Unregister observer.

        Args:
            observer_callback: Callback function to remove
        """
        self.observer.unsubscribe(observer_callback)
