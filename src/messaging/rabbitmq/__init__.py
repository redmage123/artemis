#!/usr/bin/env python3
"""
WHY: Provide clean public API for RabbitMQ messaging package
RESPONSIBILITY: Export public interfaces and check dependencies
PATTERNS: Facade, Dependency Injection

This package provides a modular, well-structured RabbitMQ messenger implementation
for distributed inter-agent communication in the Artemis system.

Package Structure:
    - models.py: RabbitMQ domain models and data structures
    - connection_manager.py: Connection and channel lifecycle management
    - publisher.py: Message publishing operations
    - consumer.py: Message consumption operations
    - messenger_core.py: Main messenger implementation

Benefits:
    - Distributed: Agents can run on different machines
    - Guaranteed delivery: Messages persist until acknowledged
    - Real-time: Push-based, no polling required
    - Scalable: Multiple agent instances can share work
    - Load balancing: Round-robin across worker pools
"""

# Check for pika availability
try:
    import pika
    RABBITMQ_AVAILABLE = True
except ImportError:
    RABBITMQ_AVAILABLE = False
    pika = None


# Public API exports
from messaging.rabbitmq.models import (
    ExchangeType,
    DeliveryMode,
    PriorityLevel,
    ExchangeConfig,
    QueueConfig,
    ConnectionConfig,
    MessageProperties,
    PriorityMapper,
    ArtemisNaming
)

from messaging.rabbitmq.connection_manager import (
    ConnectionManager,
    ConnectionError
)

from messaging.rabbitmq.publisher import MessagePublisher

from messaging.rabbitmq.consumer import (
    MessageConsumer,
    MessageFilter
)

from messaging.rabbitmq.messenger_core import RabbitMQMessengerCore


__all__ = [
    # Availability check
    'RABBITMQ_AVAILABLE',

    # Models
    'ExchangeType',
    'DeliveryMode',
    'PriorityLevel',
    'ExchangeConfig',
    'QueueConfig',
    'ConnectionConfig',
    'MessageProperties',
    'PriorityMapper',
    'ArtemisNaming',

    # Connection Management
    'ConnectionManager',
    'ConnectionError',

    # Publishing
    'MessagePublisher',

    # Consuming
    'MessageConsumer',
    'MessageFilter',

    # Core Messenger
    'RabbitMQMessengerCore',
]


def get_version() -> str:
    """Get package version"""
    return "1.0.0"


def is_available() -> bool:
    """Check if RabbitMQ dependencies are available"""
    return RABBITMQ_AVAILABLE
