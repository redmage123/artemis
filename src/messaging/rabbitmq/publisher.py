#!/usr/bin/env python3
"""
WHY: Handle RabbitMQ message publishing
RESPONSIBILITY: Publish messages to exchanges and queues with proper routing
PATTERNS: Command, Strategy, Dispatch Table, Guard Clauses

This module isolates message publishing logic, providing clear separation between
message creation and message delivery.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, Optional, Callable, Any

try:
    import pika
    RABBITMQ_AVAILABLE = True
    PikaBasicProperties = pika.BasicProperties
except ImportError:
    RABBITMQ_AVAILABLE = False
    pika = None  # type: ignore
    PikaBasicProperties = Any  # type: ignore

from messenger_interface import Message
from messaging.rabbitmq.connection_manager import ConnectionManager
from messaging.rabbitmq.models import (
    MessageProperties,
    DeliveryMode,
    PriorityMapper,
    ArtemisNaming
)


class MessagePublisher:
    """
    WHY: Centralize message publishing operations
    RESPONSIBILITY: Publish messages to RabbitMQ with proper routing and properties
    PATTERNS: Command, Strategy
    """

    def __init__(
        self,
        connection_manager: ConnectionManager,
        agent_name: str,
        durable: bool = True
    ):
        """
        Initialize message publisher

        Args:
            connection_manager: Connection manager instance
            agent_name: Name of publishing agent
            durable: Whether messages should be persistent
        """
        self.connection_manager = connection_manager
        self.agent_name = agent_name
        self.durable = durable
        self.message_sequence = 0

    def publish_message(
        self,
        message: Message,
        target_queue: Optional[str] = None,
        exchange: str = '',
        routing_key: str = ''
    ) -> str:
        """
        Publish message with guard clauses

        Args:
            message: Message to publish
            target_queue: Target queue name (if direct routing)
            exchange: Exchange name
            routing_key: Routing key

        Returns:
            Message ID
        """
        if not message:
            raise ValueError("Message cannot be None")

        channel = self.connection_manager.get_channel()
        body = self._serialize_message(message)
        properties = self._build_properties(message)

        if target_queue:
            routing_key = target_queue

        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=properties
        )

        return message.message_id

    def publish_to_agent(self, message: Message, to_agent: str) -> str:
        """
        Publish message to specific agent queue

        Args:
            message: Message to publish
            to_agent: Target agent name

        Returns:
            Message ID
        """
        if not to_agent:
            raise ValueError("Target agent cannot be empty")

        target_queue = ArtemisNaming.agent_queue_name(to_agent)

        return self.publish_message(
            message=message,
            target_queue=target_queue,
            exchange='',
            routing_key=target_queue
        )

    def broadcast_message(self, message: Message) -> str:
        """
        Broadcast message to all agents

        Args:
            message: Message to broadcast

        Returns:
            Message ID
        """
        return self.publish_message(
            message=message,
            exchange=ArtemisNaming.BROADCAST_EXCHANGE,
            routing_key=''
        )

    def publish_state_update(self, card_id: str, updates: Dict, agent_name: str) -> None:
        """
        Publish state update to topic exchange

        Args:
            card_id: Card ID
            updates: State updates
            agent_name: Agent making the update
        """
        if not card_id:
            raise ValueError("Card ID cannot be empty")

        state_message = {
            "card_id": card_id,
            "updates": updates,
            "updated_by": agent_name,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }

        body = json.dumps(state_message)
        routing_key = ArtemisNaming.state_routing_key(card_id)

        delivery_mode = DeliveryMode.PERSISTENT if self.durable else DeliveryMode.TRANSIENT

        properties = pika.BasicProperties(
            delivery_mode=delivery_mode.value,
            content_type='application/json'
        )

        channel = self.connection_manager.get_channel()
        channel.basic_publish(
            exchange=ArtemisNaming.STATE_EXCHANGE,
            routing_key=routing_key,
            body=body,
            properties=properties
        )

    def publish_agent_registration(
        self,
        agent_name: str,
        capabilities: list,
        status: str
    ) -> None:
        """
        Publish agent registration

        Args:
            agent_name: Agent name
            capabilities: Agent capabilities
            status: Agent status
        """
        if not agent_name:
            raise ValueError("Agent name cannot be empty")

        registration = {
            "agent_name": agent_name,
            "capabilities": capabilities,
            "status": status,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }

        body = json.dumps(registration)
        routing_key = ArtemisNaming.registry_routing_key()

        channel = self.connection_manager.get_channel()
        channel.basic_publish(
            exchange=ArtemisNaming.REGISTRY_EXCHANGE,
            routing_key=routing_key,
            body=body
        )

    def generate_message_id(self, data: Dict) -> str:
        """
        Generate unique message ID

        Args:
            data: Message data

        Returns:
            Unique message ID
        """
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        data_hash = hashlib.md5(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()[:8]

        self.message_sequence += 1

        return f"msg-{timestamp}-{self.agent_name}-{self.message_sequence}-{data_hash}"

    def _serialize_message(self, message: Message) -> str:
        """Serialize message to JSON"""
        return json.dumps(message.to_dict())

    def _build_properties(self, message: Message) -> PikaBasicProperties:
        """
        Build message properties from message

        Args:
            message: Message object

        Returns:
            Pika BasicProperties
        """
        delivery_mode = DeliveryMode.PERSISTENT if self.durable else DeliveryMode.TRANSIENT
        priority_value = PriorityMapper.to_priority_value(message.priority)

        return pika.BasicProperties(
            delivery_mode=delivery_mode.value,
            priority=priority_value,
            content_type='application/json',
            message_id=message.message_id,
            timestamp=int(datetime.utcnow().timestamp())
        )
