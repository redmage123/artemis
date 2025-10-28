#!/usr/bin/env python3
"""
WHY: Define RabbitMQ-specific models and data structures
RESPONSIBILITY: Provide type-safe representations for RabbitMQ exchanges, queues, and configurations
PATTERNS: Dataclass, Immutability, Value Objects

This module encapsulates RabbitMQ-specific domain models, separating data representation
from business logic and connection management.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
from enum import Enum


class ExchangeType(Enum):
    """RabbitMQ exchange types"""
    DIRECT = 'direct'
    FANOUT = 'fanout'
    TOPIC = 'topic'
    HEADERS = 'headers'


class DeliveryMode(Enum):
    """Message delivery modes"""
    TRANSIENT = 1  # Non-persistent (in-memory only)
    PERSISTENT = 2  # Persistent (survives broker restarts)


class PriorityLevel(Enum):
    """Message priority levels"""
    LOW = 1
    MEDIUM = 5
    HIGH = 9


@dataclass(frozen=True)
class ExchangeConfig:
    """
    WHY: Encapsulate exchange configuration
    RESPONSIBILITY: Hold exchange parameters in a type-safe structure
    """
    name: str
    exchange_type: ExchangeType
    durable: bool = True
    auto_delete: bool = False
    internal: bool = False
    arguments: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class QueueConfig:
    """
    WHY: Encapsulate queue configuration
    RESPONSIBILITY: Hold queue parameters in a type-safe structure
    """
    name: str
    durable: bool = True
    exclusive: bool = False
    auto_delete: bool = False
    arguments: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class ConnectionConfig:
    """
    WHY: Encapsulate connection configuration
    RESPONSIBILITY: Hold RabbitMQ connection parameters
    """
    url: str = "amqp://localhost"
    prefetch_count: int = 1
    connection_timeout: int = 30
    heartbeat: int = 60
    retry_delay: int = 5
    max_retries: int = 3


@dataclass
class MessageProperties:
    """
    WHY: Encapsulate RabbitMQ message properties
    RESPONSIBILITY: Hold message metadata and delivery options
    """
    delivery_mode: DeliveryMode
    priority: PriorityLevel
    content_type: str = 'application/json'
    message_id: Optional[str] = None
    timestamp: Optional[int] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    expiration: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None


class PriorityMapper:
    """
    WHY: Map priority strings to RabbitMQ priority values
    RESPONSIBILITY: Provide consistent priority translation
    PATTERNS: Strategy, Dispatch Table
    """

    _PRIORITY_MAP: Dict[str, PriorityLevel] = {
        "high": PriorityLevel.HIGH,
        "medium": PriorityLevel.MEDIUM,
        "low": PriorityLevel.LOW
    }

    @classmethod
    def to_priority_level(cls, priority: str) -> PriorityLevel:
        """Convert priority string to PriorityLevel"""
        if not priority:
            return PriorityLevel.MEDIUM

        return cls._PRIORITY_MAP.get(priority.lower(), PriorityLevel.MEDIUM)

    @classmethod
    def to_priority_value(cls, priority: str) -> int:
        """Convert priority string to numeric value"""
        return cls.to_priority_level(priority).value


class ArtemisNaming:
    """
    WHY: Centralize Artemis-specific naming conventions
    RESPONSIBILITY: Generate consistent RabbitMQ resource names
    PATTERNS: Static Factory
    """

    BROADCAST_EXCHANGE = "artemis.broadcast"
    STATE_EXCHANGE = "artemis.state"
    REGISTRY_EXCHANGE = "artemis.registry"

    @staticmethod
    def agent_queue_name(agent_name: str) -> str:
        """Generate agent queue name"""
        if not agent_name:
            raise ValueError("Agent name cannot be empty")

        return f"artemis.agent.{agent_name}"

    @staticmethod
    def state_routing_key(card_id: str) -> str:
        """Generate state update routing key"""
        if not card_id:
            raise ValueError("Card ID cannot be empty")

        return f"state.{card_id}"

    @staticmethod
    def registry_routing_key() -> str:
        """Generate registry routing key"""
        return "agent.registered"
