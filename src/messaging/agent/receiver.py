from artemis_logger import get_logger
logger = get_logger('receiver')
'\nWHY: Handle message receiving operations with filtering and marking.\nRESPONSIBILITY: Read messages from inbox with filtering and state management.\nPATTERNS: Observer Pattern (notification), Repository Pattern, Guard Clauses.\n\nThis module provides:\n- Message retrieval with filtering\n- Read/unread state management\n- Message acknowledgment\n'
from typing import List, Optional, Callable
from pathlib import Path
from messenger_interface import Message
from messaging.agent.message_queue import MessageReader

class MessageReceiver:
    """
    WHY: Receive messages with filtering and state management.
    RESPONSIBILITY: Coordinate message loading, filtering, and acknowledgment.
    """

    def __init__(self, agent_name: str, load_callback: Callable, mark_read_callback: Callable, log_callback: Callable):
        """
        Initialize message receiver

        Args:
            agent_name: Receiver agent name
            load_callback: Callback to load message files
            mark_read_callback: Callback to mark message as read
            log_callback: Callback to log message
        """
        self.agent_name = agent_name
        self.load_callback = load_callback
        self.mark_read_callback = mark_read_callback
        self.log_callback = log_callback
        self.reader = MessageReader()

    def receive(self, message_type: Optional[str]=None, from_agent: Optional[str]=None, priority: Optional[str]=None, unread_only: bool=True, mark_as_read: bool=True) -> List[Message]:
        """
        WHY: Receive messages with filtering options.
        RESPONSIBILITY: Load, filter, and optionally mark messages as read.

        Args:
            message_type: Filter by message type
            from_agent: Filter by sender
            priority: Filter by priority
            unread_only: Only unread messages
            mark_as_read: Mark messages as read after retrieval

        Returns:
            List of Message objects
        """
        message_files = self.load_callback(self.agent_name, unread_only)
        if not message_files:
            return []
        messages = self.reader.read_messages_from_files(message_files=message_files, message_type=message_type, from_agent=from_agent, priority=priority)
        if mark_as_read:
            self._process_messages(messages, message_files)
        return messages

    def _process_messages(self, messages: List[Message], message_files: List[Path]) -> None:
        """
        WHY: Mark messages as read and log receipt.
        RESPONSIBILITY: Update message state and audit trail.

        Args:
            messages: List of messages to process
            message_files: List of message file paths
        """
        if not messages:
            return
        message_file_map = self._create_message_file_map(messages, message_files)
        for message in messages:
            filepath = message_file_map.get(message.message_id)
            if not filepath:
                continue
            self.mark_read_callback(filepath)
            self.log_callback(message, direction='received')

    def _create_message_file_map(self, messages: List[Message], message_files: List[Path]) -> dict:
        """
        WHY: Map message IDs to file paths for acknowledgment.
        RESPONSIBILITY: Create lookup table for message files.

        Args:
            messages: List of messages
            message_files: List of message file paths

        Returns:
            Dictionary mapping message IDs to file paths
        """
        if not messages or not message_files:
            return {}
        message_ids = {msg.message_id for msg in messages}
        message_map = {}
        for filepath in message_files:
            try:
                import json
                with open(filepath) as f:
                    data = json.load(f)
                    msg_id = data.get('message_id')
                    if msg_id in message_ids:
                        message_map[msg_id] = filepath
            except (json.JSONDecodeError, IOError):
                continue
        return message_map

class MessageObserver:
    """
    WHY: Implement observer pattern for message notifications.
    RESPONSIBILITY: Notify subscribers when messages are received.
    """

    def __init__(self):
        """Initialize message observer"""
        self.observers: List[Callable[[Message], None]] = []

    def subscribe(self, observer: Callable[[Message], None]) -> None:
        """
        WHY: Register observer for message notifications.
        RESPONSIBILITY: Add observer to notification list.

        Args:
            observer: Callback function to notify
        """
        if observer in self.observers:
            return
        self.observers.append(observer)

    def unsubscribe(self, observer: Callable[[Message], None]) -> None:
        """
        WHY: Remove observer from notifications.
        RESPONSIBILITY: Remove observer from notification list.

        Args:
            observer: Callback function to remove
        """
        if observer not in self.observers:
            return
        self.observers.remove(observer)

    def notify(self, message: Message) -> None:
        """
        WHY: Notify all observers of new message.
        RESPONSIBILITY: Call all registered observers.

        Args:
            message: Message to notify about
        """
        if not self.observers:
            return
        for observer in self.observers:
            try:
                observer(message)
            except Exception as e:
                
                logger.log(f'Error notifying observer: {e}', 'INFO')