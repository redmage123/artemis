#!/usr/bin/env python3
"""
WHY: Manage RabbitMQ connections and channel lifecycle
RESPONSIBILITY: Handle connection establishment, health checks, and graceful cleanup
PATTERNS: Resource Manager, Guard Clauses, Lazy Initialization

This module centralizes connection management, isolating connection logic from
messaging operations and providing robust error handling.
"""

from typing import Optional, Callable, Any
import logging

try:
    import pika
    RABBITMQ_AVAILABLE = True
    PikaChannel = pika.channel.Channel
except ImportError:
    RABBITMQ_AVAILABLE = False
    pika = None  # type: ignore
    PikaChannel = Any  # type: ignore

from messaging.rabbitmq.models import ConnectionConfig, QueueConfig, ExchangeConfig


logger = logging.getLogger(__name__)


class ConnectionError(Exception):
    """RabbitMQ connection error"""
    pass


class ConnectionManager:
    """
    WHY: Centralize RabbitMQ connection and channel management
    RESPONSIBILITY: Connect, configure, and maintain RabbitMQ connections
    PATTERNS: Resource Manager, Context Manager
    """

    def __init__(self, config: ConnectionConfig):
        """
        Initialize connection manager

        Args:
            config: Connection configuration
        """
        if not RABBITMQ_AVAILABLE:
            raise ImportError(
                "RabbitMQ messenger requires 'pika' package. "
                "Install with: pip install pika"
            )

        self.config = config
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None

    def connect(self) -> None:
        """
        Establish connection to RabbitMQ

        Raises:
            ConnectionError: If connection fails
        """
        if self._is_connected():
            return

        try:
            self._establish_connection()
            self._configure_channel()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to RabbitMQ: {e}")

    def _establish_connection(self) -> None:
        """Establish RabbitMQ connection"""
        parameters = pika.URLParameters(self.config.url)
        parameters.connection_attempts = self.config.max_retries
        parameters.retry_delay = self.config.retry_delay
        parameters.socket_timeout = self.config.connection_timeout
        parameters.heartbeat = self.config.heartbeat

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        logger.info(f"Connected to RabbitMQ: {self.config.url}")

    def _configure_channel(self) -> None:
        """Configure channel with QoS settings"""
        if not self.channel:
            return

        self.channel.basic_qos(prefetch_count=self.config.prefetch_count)

    def _is_connected(self) -> bool:
        """Check if connection is active"""
        if not self.connection or not self.channel:
            return False

        if not self.connection.is_open or not self.channel.is_open:
            return False

        return True

    def get_channel(self) -> PikaChannel:
        """
        Get active channel, reconnecting if necessary

        Returns:
            Active channel

        Raises:
            ConnectionError: If cannot establish connection
        """
        if not self._is_connected():
            self.connect()

        if not self.channel:
            raise ConnectionError("Channel not available")

        return self.channel

    def declare_queue(self, queue_config: QueueConfig) -> None:
        """
        Declare queue with guard clauses

        Args:
            queue_config: Queue configuration
        """
        channel = self.get_channel()

        channel.queue_declare(
            queue=queue_config.name,
            durable=queue_config.durable,
            exclusive=queue_config.exclusive,
            auto_delete=queue_config.auto_delete,
            arguments=queue_config.arguments
        )

        logger.debug(f"Declared queue: {queue_config.name}")

    def declare_exchange(self, exchange_config: ExchangeConfig) -> None:
        """
        Declare exchange with guard clauses

        Args:
            exchange_config: Exchange configuration
        """
        channel = self.get_channel()

        channel.exchange_declare(
            exchange=exchange_config.name,
            exchange_type=exchange_config.exchange_type.value,
            durable=exchange_config.durable,
            auto_delete=exchange_config.auto_delete,
            internal=exchange_config.internal,
            arguments=exchange_config.arguments
        )

        logger.debug(f"Declared exchange: {exchange_config.name}")

    def bind_queue_to_exchange(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str = ''
    ) -> None:
        """
        Bind queue to exchange

        Args:
            queue_name: Queue name
            exchange_name: Exchange name
            routing_key: Routing key (optional)
        """
        channel = self.get_channel()

        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=routing_key
        )

        logger.debug(f"Bound queue {queue_name} to exchange {exchange_name}")

    def cleanup(self) -> None:
        """
        Cleanup resources gracefully
        """
        self._close_channel()
        self._close_connection()

    def _close_channel(self) -> None:
        """Close channel if open"""
        if not self.channel:
            return

        if not self.channel.is_open:
            return

        try:
            self.channel.close()
            logger.debug("Channel closed")
        except Exception as e:
            logger.warning(f"Error closing channel: {e}")

    def _close_connection(self) -> None:
        """Close connection if open"""
        if not self.connection:
            return

        if not self.connection.is_open:
            return

        try:
            self.connection.close()
            logger.info("Connection closed")
        except Exception as e:
            logger.warning(f"Error closing connection: {e}")

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
