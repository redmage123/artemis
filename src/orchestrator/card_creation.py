"""
Card Creation Helpers - Extract card creation logic from entry_points.py

WHY: Simplify entry_points.py by extracting card creation logic.
RESPONSIBILITY: Create and configure cards from requirements files.
PATTERNS: Strategy Pattern for different card creation scenarios.
"""

from typing import Dict, Any, Tuple
from pathlib import Path
from datetime import datetime

from artemis_logger import get_logger
from requirements_parser_agent import RequirementsParserAgent
from document_reader import DocumentReader
from kanban_manager import KanbanBoard

logger = get_logger(__name__)


def create_card_from_requirements(
    requirements_file: str,
    board: KanbanBoard,
    rag: Any,
    config: Dict
) -> Tuple[str, Any]:
    """
    Create new card from requirements file (autonomous mode).

    Args:
        requirements_file: Path to requirements file
        board: Kanban board instance
        rag: RAG agent
        config: Configuration dict

    Returns:
        Tuple of (card_id, parsed_requirements)
    """
    logger.log(f'\n🤖 Autonomous Mode: Creating card from requirements file...', 'INFO')
    logger.log(f'📄 Reading: {requirements_file}', 'INFO')

    # Read and parse requirements
    doc_reader = DocumentReader(verbose=False)
    requirements_text = doc_reader.read_document(requirements_file)

    parser = RequirementsParserAgent(
        llm_provider=config.get('ARTEMIS_LLM_PROVIDER', 'openai'),
        llm_model=config.get('ARTEMIS_LLM_MODEL', 'gpt-4'),
        rag=rag
    )
    parsed_reqs = parser.parse_requirements_file(requirements_file)

    # Determine card title
    filename_without_ext = Path(requirements_file).stem
    filename_as_title = filename_without_ext.replace('_', ' ').replace('-', ' ').title()
    title = filename_as_title

    if parsed_reqs.functional_requirements:
        title = parsed_reqs.functional_requirements[0].title

    if parsed_reqs.project_name and parsed_reqs.project_name != filename_as_title:
        title = parsed_reqs.project_name

    # Generate card ID
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    card_id = f'auto-{timestamp}'

    # Determine priority
    priority_map = {
        'critical': 'high',
        'high': 'high',
        'medium': 'medium',
        'low': 'low',
        'nice_to_have': 'low'
    }
    priority = 'medium'

    if parsed_reqs.functional_requirements:
        priority_order = {
            'critical': 0,
            'high': 1,
            'medium': 2,
            'low': 3,
            'nice_to_have': 4
        }
        priorities = [req.priority.value for req in parsed_reqs.functional_requirements]
        highest_priority = min(priorities, key=lambda p: priority_order.get(p, 2))
        priority = priority_map.get(highest_priority, 'medium')

    # Calculate story points
    total_reqs = len(parsed_reqs.functional_requirements) + len(parsed_reqs.non_functional_requirements)
    fibonacci = [1, 2, 3, 5, 8, 13]
    story_points = min(fibonacci, key=lambda x: abs(x - total_reqs))

    # Create card
    card = (board.new_card(card_id, title)
            .with_description(parsed_reqs.executive_summary or requirements_text[:500])
            .with_priority(priority)
            .with_story_points(story_points)
            .build())

    card['requirements_file'] = requirements_file
    card['metadata'] = card.get('metadata', {})
    card['metadata']['auto_created'] = True
    card['metadata']['created_from'] = requirements_file

    board.add_card(card)

    logger.log(f'✅ Created card: {card_id}', 'INFO')
    logger.log(f'   Title: {title}', 'INFO')
    logger.log(f"   Priority: {card['priority']}", 'INFO')
    logger.log(f"   Story Points: {card['story_points']}", 'INFO')

    return card_id, parsed_reqs


def attach_requirements_to_card(
    card_id: str,
    requirements_file: str,
    board: KanbanBoard
) -> str:
    """
    Attach requirements file to existing card.

    Args:
        card_id: Existing card ID
        requirements_file: Path to requirements file
        board: Kanban board instance

    Returns:
        Card ID
    """
    card, _ = board._find_card(card_id)
    if not card:
        logger.log(f'⚠️  Card {card_id} not found - requirements file will be used from context', 'INFO')
        return card_id

    board.update_card(card_id, {'requirements_file': requirements_file})
    logger.log(f'✅ Added requirements file to card: {requirements_file}', 'INFO')
    return card_id
