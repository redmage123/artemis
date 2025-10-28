#!/usr/bin/env python3
"""
Module: kanban/board/board_visualizer.py

WHY: Separates board visualization/printing from business logic
     Provides console output formatting

RESPONSIBILITY:
- Print visual board representation
- Format card display with emojis
- Display metrics summary

PATTERNS:
- Strategy Pattern: Dictionary mapping for emoji display
- Separation of Concerns: UI separated from logic
"""

from typing import Dict


class BoardVisualizer:
    """
    Board visualization and console output.

    WHY: Separates UI concerns from business logic
    RESPONSIBILITY: Format and display board state
    PATTERNS: Strategy pattern for display formatting
    """

    PRIORITY_EMOJIS = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    }

    @staticmethod
    def print_board(board: Dict) -> None:
        """
        Print visual representation of board.

        WHY: Console visualization for debugging and monitoring
        PERFORMANCE: O(n) where n is total cards

        Args:
            board: Board dictionary to display
        """
        BoardVisualizer._print_header(board)
        BoardVisualizer._print_columns(board)
        BoardVisualizer._print_metrics(board)

    @staticmethod
    def _print_header(board: Dict) -> None:
        """
        Print board header with sprint info.

        WHY: Extracted for clarity
        """
        print("\n" + "="*80)
        print(f"  KANBAN BOARD: {board['board_id']}")
        print(f"  Last Updated: {board['last_updated']}")

        if board.get('current_sprint'):
            sprint = board['current_sprint']
            completed = sprint['completed_story_points']
            committed = sprint['committed_story_points']
            print(f"  Sprint: {sprint['sprint_id']} ({completed}/{committed} points)")

        print("="*80)

    @staticmethod
    def _print_columns(board: Dict) -> None:
        """
        Print all columns with cards.

        WHY: Extracted for clarity
        """
        for column in board['columns']:
            BoardVisualizer._print_column(column)

    @staticmethod
    def _print_column(column: Dict) -> None:
        """
        Print a single column with cards.

        WHY: Extracted for clarity and testability
        """
        # Format WIP info
        wip_info = (
            f"(WIP: {len(column['cards'])}/{column['wip_limit']})"
            if column['wip_limit']
            else f"({len(column['cards'])})"
        )

        print(f"\n📋 {column['name']} {wip_info}")
        print("-" * 80)

        # Guard clause: empty column
        if not column['cards']:
            print("  (empty)")
            return

        # Print cards
        for card in column['cards']:
            BoardVisualizer._print_card(card)

    @staticmethod
    def _print_card(card: Dict) -> None:
        """
        Print a single card with formatting.

        WHY: Extracted for clarity and testability
        """
        # Get display elements
        blocked_indicator = "🚫 " if card.get('blocked', False) else ""
        priority_emoji = BoardVisualizer.PRIORITY_EMOJIS.get(
            card['priority'],
            "⚪"
        )

        # Print card header
        print(f"  {blocked_indicator}{priority_emoji} {card['card_id']} - {card['title']}")

        # Print card details
        agents = ', '.join(card['assigned_agents'][:2])
        points = card.get('story_points', 'N/A')
        print(f"     Priority: {card['priority']} | Points: {points} | Agents: {agents}")

        # Print test status if available
        if card.get('test_status'):
            coverage = card['test_status'].get('test_coverage_percent', 0)
            print(f"     Tests: {coverage}% coverage")

    @staticmethod
    def _print_metrics(board: Dict) -> None:
        """
        Print board metrics summary.

        WHY: Extracted for clarity
        """
        print("\n" + "="*80)
        print("METRICS")
        print("="*80)

        metrics = board['metrics']
        print(f"  Cycle Time: {metrics.get('cycle_time_avg_hours', 0):.2f}h avg")
        print(f"  Throughput: {metrics.get('throughput_current_sprint', 0)} cards this sprint")
        print(f"  Velocity: {metrics.get('velocity_current_sprint', 0)} story points")
        print(f"  Blocked: {metrics.get('blocked_items_count', 0)} items")
        print(f"  WIP Violations: {metrics.get('wip_violations_count', 0)}")
        print("="*80 + "\n")
