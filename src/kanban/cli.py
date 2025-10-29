from artemis_logger import get_logger
logger = get_logger('cli')
'\nModule: kanban/cli.py\n\nWHY: Provides command-line interface for Kanban board operations, enabling manual\n     board management and testing without running the full Artemis pipeline.\n\nRESPONSIBILITY:\n- Parse command-line arguments for board operations\n- Execute board commands (create, move, block, unblock, show, summary)\n- Display usage help and error messages\n- Provide interactive board management for debugging\n\nPATTERNS:\n- Command Pattern: Each CLI command maps to a board operation\n- Guard Clauses: Early validation prevents invalid operations\n\nUSAGE:\n    python -m kanban.cli create TASK-001 "Add feature"\n    python -m kanban.cli move card-123 development\n    python -m kanban.cli block card-123 "Waiting on API"\n    python -m kanban.cli unblock card-123 development\n    python -m kanban.cli show\n    python -m kanban.cli summary\n'
import json
import sys
from kanban.board import KanbanBoard

def main():
    """CLI interface for Kanban board"""
    if len(sys.argv) < 2:
        
        logger.log('Usage: kanban_manager.py <command> [args]', 'INFO')
        
        logger.log('\nCommands:', 'INFO')
        
        logger.log('  create <task_id> <title> - Create new card', 'INFO')
        
        logger.log('  move <card_id> <to_column> - Move card', 'INFO')
        
        logger.log('  block <card_id> <reason> - Block card', 'INFO')
        
        logger.log('  unblock <card_id> <to_column> - Unblock card', 'INFO')
        
        logger.log('  show - Display board', 'INFO')
        
        logger.log('  summary - Show board summary', 'INFO')
        sys.exit(1)
    board = KanbanBoard()
    command = sys.argv[1]
    if command == 'create':
        if len(sys.argv) < 4:
            
            logger.log('Usage: create <task_id> <title>', 'INFO')
            sys.exit(1)
        task_id = sys.argv[2]
        title = ' '.join(sys.argv[3:])
        card = board.new_card(task_id, title).with_description('Created via CLI').build()
        board.add_card(card)
        return
    if command == 'move':
        if len(sys.argv) < 4:
            
            logger.log('Usage: move <card_id> <to_column>', 'INFO')
            sys.exit(1)
        card_id = sys.argv[2]
        to_column = sys.argv[3]
        board.move_card(card_id, to_column, 'cli')
        return
    if command == 'block':
        if len(sys.argv) < 4:
            
            logger.log('Usage: block <card_id> <reason>', 'INFO')
            sys.exit(1)
        card_id = sys.argv[2]
        reason = ' '.join(sys.argv[3:])
        board.block_card(card_id, reason, 'cli')
        return
    if command == 'unblock':
        if len(sys.argv) < 4:
            
            logger.log('Usage: unblock <card_id> <to_column>', 'INFO')
            sys.exit(1)
        card_id = sys.argv[2]
        to_column = sys.argv[3]
        board.unblock_card(card_id, to_column, 'cli', 'Resolved via CLI')
        return
    if command == 'show':
        board.print_board()
        return
    if command == 'summary':
        summary = board.get_board_summary()
        
        logger.log(json.dumps(summary, indent=2), 'INFO')
        return
    
    logger.log(f'Unknown command: {command}', 'INFO')
    sys.exit(1)
if __name__ == '__main__':
    main()