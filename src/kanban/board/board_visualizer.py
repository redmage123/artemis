from artemis_logger import get_logger
logger = get_logger('board_visualizer')
'\nModule: kanban/board/board_visualizer.py\n\nWHY: Separates board visualization/printing from business logic\n     Provides console output formatting\n\nRESPONSIBILITY:\n- Print visual board representation\n- Format card display with emojis\n- Display metrics summary\n\nPATTERNS:\n- Strategy Pattern: Dictionary mapping for emoji display\n- Separation of Concerns: UI separated from logic\n'
from typing import Dict

class BoardVisualizer:
    """
    Board visualization and console output.

    WHY: Separates UI concerns from business logic
    RESPONSIBILITY: Format and display board state
    PATTERNS: Strategy pattern for display formatting
    """
    PRIORITY_EMOJIS = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}

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
        
        logger.log('\n' + '=' * 80, 'INFO')
        
        logger.log(f"  KANBAN BOARD: {board['board_id']}", 'INFO')
        
        logger.log(f"  Last Updated: {board['last_updated']}", 'INFO')
        if board.get('current_sprint'):
            sprint = board['current_sprint']
            completed = sprint['completed_story_points']
            committed = sprint['committed_story_points']
            
            logger.log(f"  Sprint: {sprint['sprint_id']} ({completed}/{committed} points)", 'INFO')
        
        logger.log('=' * 80, 'INFO')

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
        wip_info = f"(WIP: {len(column['cards'])}/{column['wip_limit']})" if column['wip_limit'] else f"({len(column['cards'])})"
        
        logger.log(f"\n📋 {column['name']} {wip_info}", 'INFO')
        
        logger.log('-' * 80, 'INFO')
        if not column['cards']:
            
            logger.log('  (empty)', 'INFO')
            return
        for card in column['cards']:
            BoardVisualizer._print_card(card)

    @staticmethod
    def _print_card(card: Dict) -> None:
        """
        Print a single card with formatting.

        WHY: Extracted for clarity and testability
        """
        blocked_indicator = '🚫 ' if card.get('blocked', False) else ''
        priority_emoji = BoardVisualizer.PRIORITY_EMOJIS.get(card['priority'], '⚪')
        
        logger.log(f"  {blocked_indicator}{priority_emoji} {card['card_id']} - {card['title']}", 'INFO')
        agents = ', '.join(card['assigned_agents'][:2])
        points = card.get('story_points', 'N/A')
        
        logger.log(f"     Priority: {card['priority']} | Points: {points} | Agents: {agents}", 'INFO')
        if card.get('test_status'):
            coverage = card['test_status'].get('test_coverage_percent', 0)
            
            logger.log(f'     Tests: {coverage}% coverage', 'INFO')

    @staticmethod
    def _print_metrics(board: Dict) -> None:
        """
        Print board metrics summary.

        WHY: Extracted for clarity
        """
        
        logger.log('\n' + '=' * 80, 'INFO')
        
        logger.log('METRICS', 'INFO')
        
        logger.log('=' * 80, 'INFO')
        metrics = board['metrics']
        
        logger.log(f"  Cycle Time: {metrics.get('cycle_time_avg_hours', 0):.2f}h avg", 'INFO')
        
        logger.log(f"  Throughput: {metrics.get('throughput_current_sprint', 0)} cards this sprint", 'INFO')
        
        logger.log(f"  Velocity: {metrics.get('velocity_current_sprint', 0)} story points", 'INFO')
        
        logger.log(f"  Blocked: {metrics.get('blocked_items_count', 0)} items", 'INFO')
        
        logger.log(f"  WIP Violations: {metrics.get('wip_violations_count', 0)}", 'INFO')
        
        logger.log('=' * 80 + '\n', 'INFO')