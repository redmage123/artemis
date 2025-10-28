#!/usr/bin/env python3
"""
WHY: Provide audit trail and debugging support for message operations.
RESPONSIBILITY: Log message send/receive events with timestamps.
PATTERNS: Single Responsibility, Guard Clauses.

This module provides:
- Message event logging
- Audit trail management
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from messenger_interface import Message


class MessageLogger:
    """
    WHY: Create audit trail of all message operations.
    RESPONSIBILITY: Log message events to file with structured format.
    """

    def __init__(self, message_dir: Path, agent_name: str):
        """
        Initialize message logger

        Args:
            message_dir: Base message directory
            agent_name: Agent name for log file
        """
        self.log_dir = message_dir / "logs"
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"{agent_name}.log"
        self.agent_name = agent_name

    def log_message(self, message: Message, direction: str) -> None:
        """
        WHY: Record message event for audit and debugging.
        RESPONSIBILITY: Append log entry to agent's log file.

        Args:
            message: Message to log
            direction: "sent" or "received"
        """
        log_entry = self._create_log_entry(message, direction)

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

    def _create_log_entry(self, message: Message, direction: str) -> Dict[str, Any]:
        """
        WHY: Structure log data consistently.
        RESPONSIBILITY: Create standardized log entry.

        Args:
            message: Message to log
            direction: "sent" or "received"

        Returns:
            Log entry dictionary
        """
        return {
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "direction": direction,
            "message_id": message.message_id,
            "message_type": message.message_type,
            "from_agent": message.from_agent,
            "to_agent": message.to_agent,
            "card_id": message.card_id,
            "priority": message.priority
        }

    def get_recent_logs(self, count: int = 100) -> list:
        """
        WHY: Retrieve recent message events for debugging.
        RESPONSIBILITY: Read and parse recent log entries.

        Args:
            count: Number of recent entries to retrieve

        Returns:
            List of log entries
        """
        # Guard clause: log file doesn't exist
        if not self.log_file.exists():
            return []

        try:
            with open(self.log_file) as f:
                lines = f.readlines()

            # Get last N lines
            recent_lines = lines[-count:] if len(lines) > count else lines

            # Parse JSON entries
            return [json.loads(line) for line in recent_lines if line.strip()]

        except (json.JSONDecodeError, IOError):
            return []
