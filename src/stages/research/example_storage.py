from artemis_logger import get_logger
logger = get_logger('example_storage')
'\nWHY: Store research examples in RAG using Repository Pattern\nRESPONSIBILITY: Handle storage operations with fault tolerance\nPATTERNS: Repository (storage abstraction), Fault Tolerance (non-fatal failures)\n\nExample storage coordinates with the repository to persist code examples,\nhandling storage failures gracefully without failing the entire stage.\n'
from typing import List
from research_strategy import ResearchExample
from research_repository import ExampleRepository

class ExampleStorage:
    """
    Stores code examples in RAG.

    WHY: Research results need to be stored for developer queries.
         Storage failures shouldn't fail the entire research stage.

    PATTERNS: Repository pattern, Fault tolerance.
    """

    def __init__(self, repository: ExampleRepository):
        """
        Initialize example storage.

        Args:
            repository: Example repository for storage
        """
        self.repository = repository

    def store_examples(self, examples: List[ResearchExample], card_id: str, task_title: str) -> List[str]:
        """
        Store examples in RAG.

        WHY: Persists research results for later retrieval by developers.

        Args:
            examples: Examples to store
            card_id: Card ID
            task_title: Task title

        Returns:
            List of artifact IDs

        Note:
            Storage failures are logged but don't fail the operation.
            Returns empty list on failure.
        """
        if not examples:
            return []
        return self._perform_storage(examples, card_id, task_title)

    def _perform_storage(self, examples: List[ResearchExample], card_id: str, task_title: str) -> List[str]:
        """
        Perform the actual storage operation with error handling.

        WHY: Separation allows guard clause to avoid unnecessary try/except.

        Args:
            examples: Examples to store (guaranteed non-empty by caller)
            card_id: Card ID
            task_title: Task title

        Returns:
            List of artifact IDs (empty list on failure)
        """
        try:
            artifact_ids = self.repository.store_examples_batch(examples=examples, card_id=card_id, task_title=task_title)
            return artifact_ids
        except Exception as e:
            
            logger.log(f'Warning: Failed to store some examples: {e}', 'INFO')
            return []