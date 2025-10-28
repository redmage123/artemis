#!/usr/bin/env python3
"""
Module: kanban/board/metrics_calculator.py

WHY: Separates metrics calculation logic from board operations
     Provides performance analytics for retrospectives

RESPONSIBILITY:
- Cycle time calculations (avg, min, max)
- Throughput tracking
- Velocity calculations
- WIP and blocked item counts

PATTERNS:
- Strategy Pattern: Dictionary mapping for metric calculators
- Pure Functions: No side effects, testable calculations
"""

from typing import Dict, List

from kanban.board.models import BoardModels


class MetricsCalculator:
    """
    Board metrics calculation and analytics.

    WHY: Separates metrics logic for testability
    RESPONSIBILITY: Calculate board performance metrics
    PATTERNS: Pure functions for calculations
    """

    @staticmethod
    def update_metrics(board: Dict) -> None:
        """
        Recalculate all board metrics.

        WHY: Updates metrics after card completion
        PERFORMANCE: O(n) where n is number of done cards

        Args:
            board: Board dictionary to update
        """
        done_column = BoardModels.get_column(board, "done")

        # Guard clause: no done column
        if not done_column:
            return

        done_cards = done_column['cards']

        # Guard clause: no done cards
        if not done_cards:
            return

        # Calculate cycle time metrics
        MetricsCalculator._update_cycle_time_metrics(board, done_cards)

        # Calculate throughput and velocity
        MetricsCalculator._update_throughput_velocity(board, done_cards)

    @staticmethod
    def _update_cycle_time_metrics(board: Dict, done_cards: List[Dict]) -> None:
        """
        Update cycle time metrics (avg, min, max).

        WHY: Extracted for clarity and testability
        PERFORMANCE: O(n) list comprehension
        """
        cycle_times = [
            c.get('cycle_time_hours', 0)
            for c in done_cards
            if 'cycle_time_hours' in c
        ]

        # Guard clause: no cycle times
        if not cycle_times:
            return

        board['metrics']['cycle_time_avg_hours'] = round(
            sum(cycle_times) / len(cycle_times), 2
        )
        board['metrics']['cycle_time_min_hours'] = round(min(cycle_times), 2)
        board['metrics']['cycle_time_max_hours'] = round(max(cycle_times), 2)

    @staticmethod
    def _update_throughput_velocity(board: Dict, done_cards: List[Dict]) -> None:
        """
        Update throughput and velocity metrics.

        WHY: Extracted for clarity and testability
        PERFORMANCE: O(n) for story points sum
        """
        board['metrics']['cards_completed'] = len(done_cards)
        board['metrics']['throughput_current_sprint'] = len(done_cards)

        # Calculate velocity (sum of story points)
        velocity = sum(c.get('story_points', 0) for c in done_cards)
        board['metrics']['velocity_current_sprint'] = velocity

        # Update current sprint if exists
        if board.get('current_sprint'):
            board['current_sprint']['completed_story_points'] = velocity

    @staticmethod
    def get_board_summary(board: Dict) -> Dict:
        """
        Get summary of board status.

        WHY: Provides high-level board overview
        PERFORMANCE: O(n) where n is total cards

        Args:
            board: Board dictionary

        Returns:
            Summary dictionary with columns and metrics
        """
        summary = {
            "board_id": board['board_id'],
            "last_updated": board['last_updated'],
            "columns": []
        }

        for column in board['columns']:
            summary['columns'].append({
                "name": column['name'],
                "column_id": column['column_id'],
                "card_count": len(column['cards']),
                "wip_limit": column['wip_limit'],
                "cards": [
                    {
                        "card_id": c['card_id'],
                        "title": c['title'],
                        "priority": c['priority'],
                        "blocked": c.get('blocked', False)
                    }
                    for c in column['cards']
                ]
            })

        summary['metrics'] = board['metrics']
        summary['current_sprint'] = board.get('current_sprint')

        return summary
