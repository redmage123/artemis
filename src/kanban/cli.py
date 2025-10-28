#!/usr/bin/env python3
"""
Module: kanban/cli.py

WHY: Provides command-line interface for Kanban board operations, enabling manual
     board management and testing without running the full Artemis pipeline.

RESPONSIBILITY:
- Parse command-line arguments for board operations
- Execute board commands (create, move, block, unblock, show, summary)
- Display usage help and error messages
- Provide interactive board management for debugging

PATTERNS:
- Command Pattern: Each CLI command maps to a board operation
- Guard Clauses: Early validation prevents invalid operations

USAGE:
    python -m kanban.cli create TASK-001 "Add feature"
    python -m kanban.cli move card-123 development
    python -m kanban.cli block card-123 "Waiting on API"
    python -m kanban.cli unblock card-123 development
    python -m kanban.cli show
    python -m kanban.cli summary
"""

import json
import sys

from kanban.board import KanbanBoard


def main():
    """CLI interface for Kanban board"""
    if len(sys.argv) < 2:
        print("Usage: kanban_manager.py <command> [args]")
        print("\nCommands:")
        print("  create <task_id> <title> - Create new card")
        print("  move <card_id> <to_column> - Move card")
        print("  block <card_id> <reason> - Block card")
        print("  unblock <card_id> <to_column> - Unblock card")
        print("  show - Display board")
        print("  summary - Show board summary")
        sys.exit(1)

    board = KanbanBoard()
    command = sys.argv[1]

    if command == "create":
        if len(sys.argv) < 4:
            print("Usage: create <task_id> <title>")
            sys.exit(1)
        task_id = sys.argv[2]
        title = ' '.join(sys.argv[3:])
        # Use Builder pattern instead of deprecated create_card
        card = (board.new_card(task_id, title)
                .with_description("Created via CLI")
                .build())
        board.add_card(card)
        return

    if command == "move":
        if len(sys.argv) < 4:
            print("Usage: move <card_id> <to_column>")
            sys.exit(1)
        card_id = sys.argv[2]
        to_column = sys.argv[3]
        board.move_card(card_id, to_column, "cli")
        return

    if command == "block":
        if len(sys.argv) < 4:
            print("Usage: block <card_id> <reason>")
            sys.exit(1)
        card_id = sys.argv[2]
        reason = ' '.join(sys.argv[3:])
        board.block_card(card_id, reason, "cli")
        return

    if command == "unblock":
        if len(sys.argv) < 4:
            print("Usage: unblock <card_id> <to_column>")
            sys.exit(1)
        card_id = sys.argv[2]
        to_column = sys.argv[3]
        board.unblock_card(card_id, to_column, "cli", "Resolved via CLI")
        return

    if command == "show":
        board.print_board()
        return

    if command == "summary":
        summary = board.get_board_summary()
        print(json.dumps(summary, indent=2))
        return

    print(f"Unknown command: {command}")
    sys.exit(1)


if __name__ == "__main__":
    main()
