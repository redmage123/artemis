#!/usr/bin/env python3
"""
WHY: Handle RabbitMQ message consumption
RESPONSIBILITY: Consume messages from queues with filtering and acknowledgment
PATTERNS: Observer, Filter Chain, Guard Clauses, Dispatch Table

This module isolates message consumption logic, providing clear separation between
message retrieval, filtering, and acknowledgment.
"""

import json
from typing import List, Optional, Callable, Dict, Any
import logging

try:
    import pika
    RABBITMQ_AVAILABLE = True
except ImportError:
    RABBITMQ_AVAILABLE = False
    pika = None  # type: ignore

from messenger_interface import Message
from messaging.rabbitmq.connection_manager import ConnectionManager


logger = logging.getLogger(__name__)


class MessageFilter:
    """
    WHY: Filter messages based on criteria
    RESPONSIBILITY: Apply filter predicates to messages
    PATTERNS: Filter, Predicate
    """

    @staticmethod
    def matches(
        message: Message,
        message_type: Optional[str] = None,
        from_agent: Optional[str] = None,
        priority: Optional[str] = None
    ) -> bool:
        """
        Check if message matches filter criteria

        Args:
            message: Message to check
            message_type: Filter by message type
            from_agent: Filter by sender
            priority: Filter by priority

        Returns:
            True if message matches all filters
        """
        if message_type and message.message_type != message_type:
            return False

        if from_agent and message.from_agent != from_agent:
            return False

        if priority and message.priority != priority:
            return False

        return True


class MessageConsumer:
    """
    WHY: Centralize message consumption operations
    RESPONSIBILITY: Consume and process messages from RabbitMQ queues
    PATTERNS: Observer, Command
    """

    def __init__(
        self,
        connection_manager: ConnectionManager,
        queue_name: str
    ):
        """
        Initialize message consumer

        Args:
            connection_manager: Connection manager instance
            queue_name: Queue to consume from
        """
        self.connection_manager = connection_manager
        self.queue_name = queue_name
        self.active_consumer_tag: Optional[str] = None

    def consume_batch(
        self,
        message_type: Optional[str] = None,
        from_agent: Optional[str] = None,
        priority: Optional[str] = None,
        mark_as_read: bool = True,
        timeout: float = 0.1
    ) -> List[Message]:
        """
        Consume batch of messages (non-blocking)

        Args:
            message_type: Filter by message type
            from_agent: Filter by sender
            priority: Filter by priority
            mark_as_read: Whether to acknowledge messages
            timeout: Inactivity timeout in seconds

        Returns:
            List of filtered messages
        """
        messages = []
        channel = self.connection_manager.get_channel()

        for method_frame, properties, body in channel.consume(
            self.queue_name,
            inactivity_timeout=timeout
        ):
            if method_frame is None:
                break

            message = self._parse_message(body)

            if not message:
                self._reject_message(channel, method_frame, requeue=False)
                continue

            if not MessageFilter.matches(message, message_type, from_agent, priority):
                self._reject_message(channel, method_frame, requeue=True)
                continue

            messages.append(message)

            if mark_as_read:
                self._acknowledge_message(channel, method_frame)
            else:
                self._reject_message(channel, method_frame, requeue=True)

        self._cancel_consumer(channel)

        return messages

    def start_consuming(self, callback: Callable[[Message], None]) -> None:
        """
        Start consuming messages (blocking)

        Args:
            callback: Function to call for each message
        """
        if not callback:
            raise ValueError("Callback cannot be None")

        channel = self.connection_manager.get_channel()

        def on_message(ch, method, properties, body):
            """Message handler with error handling"""
            try:
                message = self._parse_message(body)

                if not message:
                    self._reject_message(ch, method, requeue=False)
                    return

                callback(message)
                self._acknowledge_message(ch, method)

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                self._reject_message(ch, method, requeue=True)

        channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=on_message
        )

        logger.info(f"Waiting for messages on queue: {self.queue_name}")
        channel.start_consuming()

    def stop_consuming(self) -> None:
        """Stop consuming messages"""
        channel = self.connection_manager.get_channel()

        if not channel.is_open:
            return

        try:
            channel.stop_consuming()
            logger.info("Stopped consuming messages")
        except Exception as e:
            logger.warning(f"Error stopping consumer: {e}")

    def _parse_message(self, body: bytes) -> Optional[Message]:
        """
        Parse message from body

        Args:
            body: Message body

        Returns:
            Parsed message or None if invalid
        """
        if not body:
            return None

        try:
            message_data = json.loads(body)
            return Message.from_dict(message_data)
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None

    def _acknowledge_message(self, channel, method_frame) -> None:
        """
        Acknowledge message

        Args:
            channel: Channel instance
            method_frame: Method frame containing delivery tag
        """
        try:
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except Exception as e:
            logger.error(f"Error acknowledging message: {e}")

    def _reject_message(self, channel, method_frame, requeue: bool) -> None:
        """
        Reject message

        Args:
            channel: Channel instance
            method_frame: Method frame containing delivery tag
            requeue: Whether to requeue the message
        """
        try:
            channel.basic_nack(
                delivery_tag=method_frame.delivery_tag,
                requeue=requeue
            )
        except Exception as e:
            logger.error(f"Error rejecting message: {e}")

    def _cancel_consumer(self, channel) -> None:
        """
        Cancel consumer

        Args:
            channel: Channel instance
        """
        try:
            channel.cancel()
        except Exception as e:
            logger.warning(f"Error canceling consumer: {e}")
