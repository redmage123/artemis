from artemis_logger import get_logger
logger = get_logger('message_queue')
'\nWHY: Manage message queuing, filtering, and priority ordering.\nRESPONSIBILITY: Handle message retrieval, filtering, and sorting operations.\nPATTERNS: Queue Pattern, Filter Chain, Strategy Pattern for filtering.\n\nThis module provides:\n- Message queue filtering\n- Priority-based sorting\n- Message retrieval with filters\n'
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path
import json
from messenger_interface import Message
from messaging.agent.models import get_priority_order

class MessageFilter:
    """
    WHY: Apply filtering logic to message collections.
    RESPONSIBILITY: Filter messages by type, sender, priority, etc.
    """

    @staticmethod
    def by_message_type(message: Message, message_type: str) -> bool:
        """Filter by message type"""
        return message.message_type == message_type

    @staticmethod
    def by_from_agent(message: Message, from_agent: str) -> bool:
        """Filter by sender agent"""
        return message.from_agent == from_agent

    @staticmethod
    def by_priority(message: Message, priority: str) -> bool:
        """Filter by priority"""
        return message.priority == priority

    @staticmethod
    def by_card_id(message: Message, card_id: str) -> bool:
        """Filter by card ID"""
        return message.card_id == card_id

class MessageQueue:
    """
    WHY: Manage message queue operations with filtering and sorting.
    RESPONSIBILITY: Retrieve, filter, and order messages from storage.
    """

    def __init__(self):
        """Initialize message queue"""
        self.filters: List[Callable[[Message], bool]] = []

    def add_filter(self, filter_type: str, filter_value: Any) -> None:
        """
        WHY: Add filter to the filter chain.
        RESPONSIBILITY: Build composite filter from individual criteria.

        Args:
            filter_type: Type of filter (message_type, from_agent, priority, card_id)
            filter_value: Value to filter by
        """
        if not filter_value:
            return
        filter_map = {'message_type': lambda m: MessageFilter.by_message_type(m, filter_value), 'from_agent': lambda m: MessageFilter.by_from_agent(m, filter_value), 'priority': lambda m: MessageFilter.by_priority(m, filter_value), 'card_id': lambda m: MessageFilter.by_card_id(m, filter_value)}
        filter_func = filter_map.get(filter_type)
        if filter_func:
            self.filters.append(filter_func)

    def apply_filters(self, messages: List[Message]) -> List[Message]:
        """
        WHY: Apply all filters to message list.
        RESPONSIBILITY: Filter messages through the filter chain.

        Args:
            messages: List of messages to filter

        Returns:
            Filtered list of messages
        """
        if not self.filters:
            return messages
        filtered_messages = messages
        for filter_func in self.filters:
            filtered_messages = [m for m in filtered_messages if filter_func(m)]
        return filtered_messages

    def sort_by_priority(self, messages: List[Message]) -> List[Message]:
        """
        WHY: Order messages by priority (high to low).
        RESPONSIBILITY: Sort messages for processing order.

        Args:
            messages: List of messages to sort

        Returns:
            Sorted list of messages
        """
        if not messages:
            return messages
        return sorted(messages, key=lambda m: get_priority_order(m.priority))

    def clear_filters(self) -> None:
        """
        WHY: Reset filter chain for reuse.
        RESPONSIBILITY: Clear all active filters.
        """
        self.filters.clear()

class MessageReader:
    """
    WHY: Read messages from file system with filtering.
    RESPONSIBILITY: Load messages from files and apply filters.
    """

    def __init__(self):
        """Initialize message reader"""
        self.queue = MessageQueue()

    def read_messages_from_files(self, message_files: List[Path], message_type: Optional[str]=None, from_agent: Optional[str]=None, priority: Optional[str]=None, card_id: Optional[str]=None) -> List[Message]:
        """
        WHY: Load messages from files with filtering.
        RESPONSIBILITY: Read JSON files, parse messages, apply filters.

        Args:
            message_files: List of message file paths
            message_type: Filter by message type
            from_agent: Filter by sender
            priority: Filter by priority
            card_id: Filter by card ID

        Returns:
            List of filtered messages
        """
        if not message_files:
            return []
        self.queue.clear_filters()
        if message_type:
            self.queue.add_filter('message_type', message_type)
        if from_agent:
            self.queue.add_filter('from_agent', from_agent)
        if priority:
            self.queue.add_filter('priority', priority)
        if card_id:
            self.queue.add_filter('card_id', card_id)
        messages = []
        for filepath in message_files:
            message = self._load_message_from_file(filepath)
            if message:
                messages.append(message)
        filtered_messages = self.queue.apply_filters(messages)
        return self.queue.sort_by_priority(filtered_messages)

    def _load_message_from_file(self, filepath: Path) -> Optional[Message]:
        """
        WHY: Load single message from file with error handling.
        RESPONSIBILITY: Parse JSON and construct Message object.

        Args:
            filepath: Path to message file

        Returns:
            Message object or None if error
        """
        try:
            with open(filepath) as f:
                message_data = json.load(f)
            return Message.from_dict(message_data)
        except (json.JSONDecodeError, IOError, KeyError) as e:
            
            logger.log(f'Error reading message {filepath}: {e}', 'INFO')
            return None

class BroadcastQueue:
    """
    WHY: Handle broadcast message distribution.
    RESPONSIBILITY: Send messages to all registered agents.
    """

    def __init__(self, registry_data: Dict[str, Any]):
        """
        Initialize broadcast queue

        Args:
            registry_data: Agent registry data
        """
        self.registry_data = registry_data

    def get_broadcast_recipients(self, sender_agent: str) -> List[str]:
        """
        WHY: Get list of agents to receive broadcast.
        RESPONSIBILITY: Filter out sender from recipient list.

        Args:
            sender_agent: Agent sending the broadcast

        Returns:
            List of recipient agent names
        """
        agents = self.registry_data.get('agents', {})
        if not agents:
            return []
        return [agent_name for agent_name in agents.keys() if agent_name != sender_agent]