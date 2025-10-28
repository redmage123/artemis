#!/usr/bin/env python3
"""
Module: kanban/board/models.py

WHY: Encapsulates board data structures and column access logic
     Provides type-safe representations of board entities

RESPONSIBILITY:
- Define board structure helpers
- Column lookup operations (dict and list formats)
- Card search operations
- Backward compatibility for column formats

PATTERNS:
- Data Access Object: Abstracts board structure access
- Strategy Pattern: Handles multiple column format types
"""

from typing import Dict, List, Optional, Tuple, Any


class BoardModels:
    """
    Board data structure access and manipulation.

    WHY: Separates data structure concerns from business logic
    RESPONSIBILITY: Column and card lookup operations
    PATTERNS: DAO pattern, Strategy pattern for format handling
    """

    @staticmethod
    def find_card(board: Dict, card_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Find a card by ID, return (card, column_id).

        WHY: Centralized card lookup supporting multiple ID formats
        PERFORMANCE: Uses generator expression for early termination

        Args:
            board: Board dictionary
            card_id: Card identifier (task_id or card_id)

        Returns:
            Tuple of (card_dict, column_id) or (None, None)
        """
        columns = board.get('columns', {})

        # Guard clause: check column format
        if isinstance(columns, dict):
            return BoardModels._find_card_in_dict_format(columns, card_id)

        return BoardModels._find_card_in_list_format(columns, card_id)

    @staticmethod
    def _find_card_in_dict_format(
        columns: Dict,
        card_id: str
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Find card in dictionary-format columns.

        WHY: Dictionary format uses column_id as key
        PERFORMANCE: Generator with early termination on match
        """
        result = next(
            ((card, column_id)
             for column_id, column_data in columns.items()
             for card in column_data.get('cards', [])
             if card.get('task_id') == card_id or card.get('card_id') == card_id),
            (None, None)
        )
        return result

    @staticmethod
    def _find_card_in_list_format(
        columns: List,
        card_id: str
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Find card in list-format columns.

        WHY: List format stores column_id within column object
        PERFORMANCE: Generator with early termination on match
        """
        result = next(
            ((card, column.get('column_id'))
             for column in columns
             for card in column.get('cards', [])
             if card.get('task_id') == card_id or card.get('card_id') == card_id),
            (None, None)
        )
        return result

    @staticmethod
    def get_column(board: Dict, column_id: str) -> Optional[Dict]:
        """
        Get column by ID supporting both dict and list formats.

        WHY: Abstracts column format differences
        PERFORMANCE: Dictionary lookup O(1) for dict format

        Args:
            board: Board dictionary
            column_id: Column identifier

        Returns:
            Column dictionary or None
        """
        columns = board.get('columns', {})

        # Guard clause: dict format
        if isinstance(columns, dict):
            return columns.get(column_id)

        # List format
        return next(
            (column for column in columns if column.get('column_id') == column_id),
            None
        )

    @staticmethod
    def get_cards_in_column(board: Dict, column_id: str) -> List[Dict]:
        """
        Get all cards in a specific column.

        WHY: Provides filtered card list for a column

        Args:
            board: Board dictionary
            column_id: Column to get cards from

        Returns:
            List of card dictionaries
        """
        column = BoardModels.get_column(board, column_id)
        if not column:
            return []

        return column.get('cards', [])

    @staticmethod
    def get_sprint_backlog_cards(
        board: Dict,
        sprint_number: int
    ) -> List[Dict]:
        """
        Get all cards assigned to a sprint.

        WHY: Sprint backlog filtering
        PERFORMANCE: List comprehension with generator

        Args:
            board: Board dictionary
            sprint_number: Sprint number

        Returns:
            List of cards in sprint backlog
        """
        columns = board.get('columns', {})

        # Guard clause: dict format
        if isinstance(columns, dict):
            return [
                card
                for column_data in columns.values()
                for card in column_data.get('cards', [])
                if card.get('sprint_number') == sprint_number
            ]

        # List format
        return [
            card
            for column in columns
            for card in column.get('cards', [])
            if card.get('sprint_number') == sprint_number
        ]

    @staticmethod
    def get_all_incomplete_cards(board: Dict) -> List[Dict]:
        """
        Get all cards that are not in 'done' column.

        WHY: Provides pending work view
        PERFORMANCE: Single pass through all columns

        Args:
            board: Board dictionary

        Returns:
            List of incomplete card dictionaries
        """
        incomplete_cards = []
        columns = board.get('columns', {})

        # Guard clause: dict format
        if isinstance(columns, dict):
            for column_id, column_data in columns.items():
                if column_id != 'done':
                    cards = column_data.get('cards', [])
                    incomplete_cards.extend(cards)
            return incomplete_cards

        # List format
        for column in columns:
            if column.get('column_id') != 'done':
                cards = column.get('cards', [])
                incomplete_cards.extend(cards)

        return incomplete_cards

    @staticmethod
    def get_pending_cards(board: Dict) -> List[Dict]:
        """
        Get all pending cards (backlog + non-blocked development).

        WHY: Provides cards needing processing

        Args:
            board: Board dictionary

        Returns:
            List of pending card dictionaries
        """
        pending_cards = []

        # Get cards from backlog
        backlog_cards = BoardModels.get_cards_in_column(board, 'backlog')
        pending_cards.extend(backlog_cards)

        # Get non-blocked cards from development
        dev_cards = BoardModels.get_cards_in_column(board, 'development')
        non_blocked_dev = [
            card for card in dev_cards
            if not card.get('blocked', False)
        ]
        pending_cards.extend(non_blocked_dev)

        return pending_cards
