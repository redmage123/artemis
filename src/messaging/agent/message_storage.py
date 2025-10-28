#!/usr/bin/env python3
"""
WHY: Handle persistent storage of messages and agent state.
RESPONSIBILITY: Manage file-based message storage, retrieval, and cleanup.
PATTERNS: Repository Pattern, Single Responsibility Principle, Guard Clauses.

This module handles:
- Message file persistence
- State file management
- Registry file operations
- File cleanup and maintenance
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from messenger_interface import Message


class MessageStorage:
    """
    WHY: Centralize all file I/O operations for messages.
    RESPONSIBILITY: Abstract file system operations from business logic.
    """

    def __init__(self, message_dir: str):
        """
        Initialize message storage

        Args:
            message_dir: Base directory for message storage
        """
        self.message_dir = Path(message_dir)
        self.message_dir.mkdir(exist_ok=True, parents=True)

    def save_message(self, to_agent: str, from_agent: str, message: Message) -> None:
        """
        WHY: Persist message to recipient's inbox.
        RESPONSIBILITY: Write message to file system atomically.

        Args:
            to_agent: Recipient agent name
            from_agent: Sender agent name
            message: Message object to save
        """
        recipient_inbox = self.message_dir / to_agent
        recipient_inbox.mkdir(exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        filename = f"{timestamp}_{from_agent}_to_{to_agent}_{message.message_type}.json"
        filepath = recipient_inbox / filename

        with open(filepath, 'w') as f:
            json.dump(message.to_dict(), f, indent=2)

    def load_messages(
        self,
        agent_name: str,
        unread_only: bool = True
    ) -> List[Path]:
        """
        WHY: Retrieve message file paths from agent's inbox.
        RESPONSIBILITY: Locate and filter message files.

        Args:
            agent_name: Agent name
            unread_only: Only return unread messages

        Returns:
            List of message file paths
        """
        inbox = self.message_dir / agent_name

        # Guard clause: inbox doesn't exist
        if not inbox.exists():
            return []

        pattern = "*.json" if unread_only else "*.json*"
        message_files = sorted(inbox.glob(pattern))

        # Guard clause: filter out .read files if unread_only
        if unread_only:
            return [f for f in message_files if f.suffix == '.json']

        return message_files

    def mark_message_read(self, filepath: Path) -> None:
        """
        WHY: Mark message as read without deletion.
        RESPONSIBILITY: Rename message file to indicate read status.

        Args:
            filepath: Path to message file
        """
        # Guard clause: already marked as read
        if filepath.name.endswith('.read'):
            return

        new_path = filepath.with_suffix('.json.read')
        filepath.rename(new_path)

    def cleanup_old_messages(self, agent_name: str, days: int = 7) -> int:
        """
        WHY: Prevent disk space exhaustion from old messages.
        RESPONSIBILITY: Delete read messages older than threshold.

        Args:
            agent_name: Agent name
            days: Delete messages older than this many days

        Returns:
            Number of messages deleted
        """
        inbox = self.message_dir / agent_name

        # Guard clause: inbox doesn't exist
        if not inbox.exists():
            return 0

        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted_count = 0

        for filepath in inbox.glob("*.json.read"):
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)

            # Guard clause: file is newer than cutoff
            if mtime >= cutoff:
                continue

            filepath.unlink()
            deleted_count += 1

        return deleted_count


class StateStorage:
    """
    WHY: Manage shared pipeline state persistence.
    RESPONSIBILITY: Handle state file read/write operations.
    """

    def __init__(self, state_file: str = "/tmp/pipeline_state.json"):
        """
        Initialize state storage

        Args:
            state_file: Path to state file
        """
        self.state_file = Path(state_file)

    def load_state(self) -> Dict[str, Any]:
        """
        WHY: Load current pipeline state.
        RESPONSIBILITY: Read state from file with error handling.

        Returns:
            State dictionary or empty dict if file doesn't exist
        """
        # Guard clause: file doesn't exist
        if not self.state_file.exists():
            return {}

        try:
            with open(self.state_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def save_state(self, state: Dict[str, Any]) -> None:
        """
        WHY: Persist pipeline state to disk.
        RESPONSIBILITY: Write state atomically to file.

        Args:
            state: State dictionary to save
        """
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def update_state(self, card_id: str, agent_name: str, updates: Dict[str, Any]) -> None:
        """
        WHY: Update specific state fields atomically.
        RESPONSIBILITY: Load, modify, and save state in one operation.

        Args:
            card_id: Card ID
            agent_name: Agent making the update
            updates: Dictionary of updates to apply
        """
        state = self.load_state()

        # Guard clause: initialize state if empty
        if not state:
            state = {
                "card_id": card_id,
                "agent_statuses": {},
                "shared_data": {}
            }

        # Apply updates using dispatch table
        update_handlers = {
            "agent_status": lambda v: self._update_agent_status(state, agent_name, v),
        }

        for key, value in updates.items():
            handler = update_handlers.get(key)
            if handler:
                handler(value)
            else:
                state["shared_data"][key] = value

        state["last_updated"] = datetime.utcnow().isoformat() + 'Z'
        state["updated_by"] = agent_name

        self.save_state(state)

    def _update_agent_status(self, state: Dict, agent_name: str, status: str) -> None:
        """Update agent status in state"""
        state["agent_statuses"][agent_name] = status


class RegistryStorage:
    """
    WHY: Manage agent registry persistence.
    RESPONSIBILITY: Handle agent registration file operations.
    """

    def __init__(self, registry_file: str = "/tmp/agent_registry.json"):
        """
        Initialize registry storage

        Args:
            registry_file: Path to registry file
        """
        self.registry_file = Path(registry_file)

    def load_registry(self) -> Dict[str, Any]:
        """
        WHY: Load agent registry.
        RESPONSIBILITY: Read registry from file with error handling.

        Returns:
            Registry dictionary
        """
        # Guard clause: file doesn't exist
        if not self.registry_file.exists():
            return {"agents": {}}

        try:
            with open(self.registry_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"agents": {}}

    def save_registry(self, registry: Dict[str, Any]) -> None:
        """
        WHY: Persist agent registry to disk.
        RESPONSIBILITY: Write registry atomically to file.

        Args:
            registry: Registry dictionary to save
        """
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)

    def register_agent(
        self,
        agent_name: str,
        capabilities: List[str],
        status: str,
        message_endpoint: str
    ) -> None:
        """
        WHY: Register or update agent in registry.
        RESPONSIBILITY: Add/update agent entry with timestamp.

        Args:
            agent_name: Agent name
            capabilities: List of agent capabilities
            status: Agent status
            message_endpoint: Agent's message endpoint
        """
        registry = self.load_registry()

        registry["agents"][agent_name] = {
            "status": status,
            "capabilities": capabilities,
            "message_endpoint": message_endpoint,
            "last_heartbeat": datetime.utcnow().isoformat() + 'Z'
        }

        self.save_registry(registry)

    def update_heartbeat(self, agent_name: str) -> None:
        """
        WHY: Update agent's last heartbeat timestamp.
        RESPONSIBILITY: Touch agent's heartbeat without full registration.

        Args:
            agent_name: Agent name
        """
        registry = self.load_registry()

        # Guard clause: agent not registered
        if agent_name not in registry.get("agents", {}):
            return

        registry["agents"][agent_name]["last_heartbeat"] = (
            datetime.utcnow().isoformat() + 'Z'
        )

        self.save_registry(registry)
