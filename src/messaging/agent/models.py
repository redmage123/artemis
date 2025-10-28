#!/usr/bin/env python3
"""
WHY: Define data models and types for agent messaging system.
RESPONSIBILITY: Provide type-safe message models with validation and serialization.
PATTERNS: Data Transfer Object (DTO), Value Object, Type Safety.

This module contains:
- MessageType enumeration for type safety
- Message priority levels
- Message validation utilities
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class MessageType(Enum):
    """
    WHY: Type-safe message categorization.
    Prevents string typos and enables IDE autocomplete.
    """
    DATA_UPDATE = "data_update"
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class MessagePriority(Enum):
    """
    WHY: Standardize priority levels for message routing.
    Enables priority-based queue ordering.
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AgentStatus(Enum):
    """
    WHY: Track agent lifecycle states.
    Enables health monitoring and agent discovery.
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


@dataclass
class MessageMetadata:
    """
    WHY: Encapsulate optional message metadata.
    RESPONSIBILITY: Store message routing and timeout information.
    """
    requires_response: bool = False
    timeout_seconds: int = 300
    custom_data: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize custom_data if None"""
        if self.custom_data is None:
            self.custom_data = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "requires_response": self.requires_response,
            "timeout_seconds": self.timeout_seconds,
            **self.custom_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MessageMetadata':
        """Create from dictionary with guard clause"""
        if not data:
            return cls()

        return cls(
            requires_response=data.get("requires_response", False),
            timeout_seconds=data.get("timeout_seconds", 300),
            custom_data={k: v for k, v in data.items()
                        if k not in ["requires_response", "timeout_seconds"]}
        )


@dataclass
class AgentRegistration:
    """
    WHY: Represent agent registration information.
    RESPONSIBILITY: Store agent capabilities and status for discovery.
    """
    agent_name: str
    capabilities: List[str]
    status: AgentStatus
    message_endpoint: str
    last_heartbeat: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "status": self.status.value,
            "capabilities": self.capabilities,
            "message_endpoint": self.message_endpoint,
            "last_heartbeat": self.last_heartbeat
        }

    @classmethod
    def from_dict(cls, agent_name: str, data: Dict[str, Any]) -> 'AgentRegistration':
        """Create from dictionary"""
        return cls(
            agent_name=agent_name,
            capabilities=data.get("capabilities", []),
            status=AgentStatus(data.get("status", "active")),
            message_endpoint=data.get("message_endpoint", ""),
            last_heartbeat=data.get("last_heartbeat", "")
        )


def validate_message_data(data: Dict[str, Any]) -> bool:
    """
    WHY: Ensure message data is valid before transmission.
    RESPONSIBILITY: Validate message payload structure.

    Args:
        data: Message data to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(data, dict):
        return False

    # Guard clause: empty data is valid
    if not data:
        return True

    # All values must be JSON-serializable
    try:
        import json
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False


def normalize_priority(priority: str) -> str:
    """
    WHY: Convert string priority to standardized format.
    RESPONSIBILITY: Ensure priority values match MessagePriority enum.

    Args:
        priority: Priority string

    Returns:
        Normalized priority string
    """
    # Guard clause: default to medium
    if not priority:
        return MessagePriority.MEDIUM.value

    priority_lower = priority.lower()

    # Dispatch table for priority normalization
    priority_map = {
        "high": MessagePriority.HIGH.value,
        "medium": MessagePriority.MEDIUM.value,
        "low": MessagePriority.LOW.value,
        "urgent": MessagePriority.HIGH.value,
        "normal": MessagePriority.MEDIUM.value,
    }

    return priority_map.get(priority_lower, MessagePriority.MEDIUM.value)


def get_priority_order(priority: str) -> int:
    """
    WHY: Convert priority to numeric ordering for sorting.
    RESPONSIBILITY: Enable priority-based message queue ordering.

    Args:
        priority: Priority string

    Returns:
        Numeric priority (lower is higher priority)
    """
    priority_order = {
        MessagePriority.HIGH.value: 0,
        MessagePriority.MEDIUM.value: 1,
        MessagePriority.LOW.value: 2
    }

    return priority_order.get(normalize_priority(priority), 1)
