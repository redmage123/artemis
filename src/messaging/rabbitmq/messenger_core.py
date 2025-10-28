#!/usr/bin/env python3
"""
WHY: Provide RabbitMQ messenger implementation
RESPONSIBILITY: Implement MessengerInterface using RabbitMQ components
PATTERNS: Facade, Adapter, Composition, Dispatch Table

This module composes the connection manager, publisher, and consumer into a
cohesive messenger implementation that satisfies the MessengerInterface contract.
"""

from datetime import datetime
from typing import Dict, List, Optional, Callable

from messenger_interface import MessengerInterface, Message
from messaging.rabbitmq.connection_manager import ConnectionManager
from messaging.rabbitmq.publisher import MessagePublisher
from messaging.rabbitmq.consumer import MessageConsumer
from messaging.rabbitmq.models import (
    ConnectionConfig,
    QueueConfig,
    ExchangeConfig,
    ExchangeType,
    ArtemisNaming
)


class RabbitMQMessengerCore(MessengerInterface):
    """
    WHY: Provide RabbitMQ-based distributed agent communication
    RESPONSIBILITY: Implement MessengerInterface using RabbitMQ
    PATTERNS: Facade, Adapter, Composition
    """

    def __init__(
        self,
        agent_name: str,
        rabbitmq_url: str = "amqp://localhost",
        durable: bool = True,
        prefetch_count: int = 1
    ):
        """
        Initialize RabbitMQ messenger

        Args:
            agent_name: Name of this agent
            rabbitmq_url: RabbitMQ connection URL
            durable: Whether queues/messages persist across restarts
            prefetch_count: How many unacknowledged messages to buffer
        """
        if not agent_name:
            raise ValueError("Agent name cannot be empty")

        self.agent_name = agent_name
        self.durable = durable

        # Initialize connection manager
        config = ConnectionConfig(url=rabbitmq_url, prefetch_count=prefetch_count)
        self.connection_manager = ConnectionManager(config)
        self.connection_manager.connect()

        # Setup infrastructure
        self._setup_infrastructure()

        # Initialize publisher and consumer
        self.publisher = MessagePublisher(
            self.connection_manager,
            self.agent_name,
            self.durable
        )

        queue_name = ArtemisNaming.agent_queue_name(agent_name)
        self.consumer = MessageConsumer(self.connection_manager, queue_name)

    def _setup_infrastructure(self) -> None:
        """Setup RabbitMQ queues and exchanges"""
        # Create agent's queue
        queue_name = ArtemisNaming.agent_queue_name(self.agent_name)
        queue_config = QueueConfig(name=queue_name, durable=self.durable)
        self.connection_manager.declare_queue(queue_config)

        # Create broadcast exchange (fanout)
        broadcast_exchange = ExchangeConfig(
            name=ArtemisNaming.BROADCAST_EXCHANGE,
            exchange_type=ExchangeType.FANOUT,
            durable=self.durable
        )
        self.connection_manager.declare_exchange(broadcast_exchange)

        # Bind agent queue to broadcast exchange
        self.connection_manager.bind_queue_to_exchange(
            queue_name=queue_name,
            exchange_name=ArtemisNaming.BROADCAST_EXCHANGE
        )

        # Create shared state exchange (topic)
        state_exchange = ExchangeConfig(
            name=ArtemisNaming.STATE_EXCHANGE,
            exchange_type=ExchangeType.TOPIC,
            durable=self.durable
        )
        self.connection_manager.declare_exchange(state_exchange)

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
        Send message to another agent via RabbitMQ

        Args:
            to_agent: Recipient agent name (or "all" for broadcast)
            message_type: Type of message
            data: Message payload
            card_id: Associated card ID
            priority: Message priority
            metadata: Optional metadata

        Returns:
            Message ID
        """
        if not to_agent:
            raise ValueError("Recipient agent cannot be empty")

        message = self._create_message(
            to_agent=to_agent,
            message_type=message_type,
            data=data,
            card_id=card_id,
            priority=priority,
            metadata=metadata or {}
        )

        if to_agent == "all":
            return self.publisher.broadcast_message(message)

        return self.publisher.publish_to_agent(message, to_agent)

    def read_messages(
        self,
        message_type: Optional[str] = None,
        from_agent: Optional[str] = None,
        priority: Optional[str] = None,
        unread_only: bool = True,
        mark_as_read: bool = True
    ) -> List[Message]:
        """
        Read messages from queue (non-blocking)

        Args:
            message_type: Filter by message type
            from_agent: Filter by sender
            priority: Filter by priority
            unread_only: Ignored (RabbitMQ always returns unread)
            mark_as_read: Whether to acknowledge messages

        Returns:
            List of Message objects
        """
        return self.consumer.consume_batch(
            message_type=message_type,
            from_agent=from_agent,
            priority=priority,
            mark_as_read=mark_as_read
        )

    def start_consuming(self, callback: Callable[[Message], None]) -> None:
        """
        Start consuming messages (blocking)

        Args:
            callback: Function to call for each message: callback(message: Message)
        """
        self.consumer.start_consuming(callback)

    def send_data_update(
        self,
        to_agent: str,
        card_id: str,
        update_type: str,
        data: Dict,
        priority: str = "medium"
    ) -> str:
        """Send data update"""
        if not to_agent or not card_id:
            raise ValueError("Agent and card_id cannot be empty")

        return self.send_message(
            to_agent=to_agent,
            message_type="data_update",
            card_id=card_id,
            priority=priority,
            data={"update_type": update_type, **data}
        )

    def send_notification(
        self,
        to_agent: str,
        card_id: str,
        notification_type: str,
        data: Dict,
        priority: str = "low"
    ) -> str:
        """Send notification"""
        if not to_agent or not card_id:
            raise ValueError("Agent and card_id cannot be empty")

        return self.send_message(
            to_agent=to_agent,
            message_type="notification",
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
        """Send error"""
        if not to_agent or not card_id:
            raise ValueError("Agent and card_id cannot be empty")

        return self.send_message(
            to_agent=to_agent,
            message_type="error",
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

    def update_shared_state(self, card_id: str, updates: Dict) -> None:
        """
        Update shared pipeline state

        Args:
            card_id: Card ID
            updates: Dictionary of updates to apply
        """
        if not card_id:
            raise ValueError("Card ID cannot be empty")

        self.publisher.publish_state_update(
            card_id=card_id,
            updates=updates,
            agent_name=self.agent_name
        )

    def get_shared_state(self, card_id: Optional[str] = None) -> Dict:
        """
        Get current shared pipeline state

        Note: RabbitMQ is not a state store. This is a placeholder.
        In production, use Redis or a database for shared state.

        Args:
            card_id: Optional card ID to filter

        Returns:
            Shared state dictionary (empty in RabbitMQ implementation)
        """
        # RabbitMQ is a message broker, not a state store
        # For shared state, use Redis or database
        return {}

    def register_agent(self, capabilities: List[str], status: str = "active") -> None:
        """
        Register agent in agent registry

        Args:
            capabilities: List of agent capabilities
            status: Agent status
        """
        if not capabilities:
            raise ValueError("Capabilities cannot be empty")

        self.publisher.publish_agent_registration(
            agent_name=self.agent_name,
            capabilities=capabilities,
            status=status
        )

    def cleanup(self) -> None:
        """
        Cleanup resources

        Closes RabbitMQ connection.
        """
        self.connection_manager.cleanup()

    def get_messenger_type(self) -> str:
        """Get messenger implementation type"""
        return "rabbitmq"

    def _create_message(
        self,
        to_agent: str,
        message_type: str,
        data: Dict,
        card_id: str,
        priority: str,
        metadata: Dict
    ) -> Message:
        """
        Create message object

        Args:
            to_agent: Recipient agent
            message_type: Message type
            data: Message data
            card_id: Card ID
            priority: Priority
            metadata: Metadata

        Returns:
            Message object
        """
        message_id = self.publisher.generate_message_id(data)

        return Message(
            protocol_version="1.0.0",
            message_id=message_id,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            from_agent=self.agent_name,
            to_agent=to_agent,
            message_type=message_type,
            card_id=card_id,
            priority=priority,
            data=data,
            metadata=metadata
        )
