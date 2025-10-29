"""
Data Management Workflow Handlers

WHY:
Handles data validation, state management, and knowledge base operations
including card data validation, state backup/restore, and RAG index rebuilding.

RESPONSIBILITY:
- Validate and sanitize card data
- Restore state from backups
- Rebuild RAG knowledge indexes
- Manage data integrity

PATTERNS:
- Strategy Pattern: Different data validation strategies
- Guard Clauses: Validate data presence before processing
- Template Method: Common validation patterns

INTEGRATION:
- Extends: WorkflowHandler base class
- Used by: WorkflowHandlerFactory for data actions
- Coordinates with: State management and RAG systems
"""
import json
from typing import Dict, Any, List
from pathlib import Path
from workflows.handlers.base_handler import WorkflowHandler
from artemis_logger import get_logger
logger = get_logger('workflow.data_handlers')

class ValidateCardDataHandler(WorkflowHandler):
    """
    Validate and sanitize card data

    WHY: Ensure Kanban card data integrity before storage
    RESPONSIBILITY: Validate required fields in card data
    PATTERNS: Guard clauses for field validation
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        card = context.get('card', {})
        required_fields = ['card_id', 'title', 'description']
        for field in required_fields:
            if field not in card:
                
                logger.log(f'[Workflow] Missing required field: {field}', 'INFO')
                return False
        
        logger.log('[Workflow] Card data validated', 'INFO')
        return True

class RestoreStateFromBackupHandler(WorkflowHandler):
    """
    Restore state from backup

    WHY: Recover from state corruption by restoring from backup
    RESPONSIBILITY: Load and restore state from backup file
    PATTERNS: Guard clause for file existence check
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        backup_file = context.get('backup_file')
        if not backup_file or not Path(backup_file).exists():
            logger.error(f'No backup file found at: {backup_file}')
            return False
        try:
            logger.info(f'Restoring state from {backup_file}')
            backup_path = Path(backup_file)
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            context['restored_state'] = backup_data
            context['restoration_timestamp'] = backup_data.get('timestamp', 'unknown')
            logger.info(f'Successfully restored state from {backup_file}')
            return True
        except json.JSONDecodeError as e:
            logger.error(f'Failed to parse backup file {backup_file}: {e}')
            return False
        except Exception as e:
            logger.error(f'Failed to restore state from {backup_file}: {e}')
            return False

class RebuildRAGIndexHandler(WorkflowHandler):
    """
    Rebuild RAG index

    WHY: Recover from corrupted or stale RAG knowledge base
    RESPONSIBILITY: Trigger RAG index rebuild process
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        logger.info('Rebuilding RAG index...')
        try:
            logger.warning("RAG index rebuild triggered, but requires integration with specific RAG implementation. Current implementation is a placeholder that logs the rebuild request. To fully implement, inject RAG service instance via context['rag_service'] and call its rebuild method.")
            rag_service = context.get('rag_service')
            if rag_service and hasattr(rag_service, 'rebuild_index'):
                logger.info('RAG service found, triggering rebuild...')
                rag_service.rebuild_index()
                logger.info('RAG index rebuild completed')
                return True
            logger.warning('No RAG service provided in context - manual rebuild required')
            return False
        except Exception as e:
            logger.error(f'Failed to rebuild RAG index: {e}')
            return False