from artemis_logger import get_logger
logger = get_logger('example_searcher')
'\nWHY: Orchestrate searching across multiple research sources\nRESPONSIBILITY: Search all sources and handle errors gracefully\nPATTERNS: Strategy (multiple sources), Fault Tolerance (continue on errors)\n\nExample searcher coordinates searches across GitHub, HuggingFace, and local\nsources, collecting examples while handling individual source failures.\n'
from typing import List
from research_strategy import ResearchStrategy, ResearchExample
from research_exceptions import ResearchSourceError

class ExampleSearcher:
    """
    Searches multiple sources for code examples.

    WHY: Research should check multiple sources for comprehensive results.
         Individual source failures shouldn't fail the entire search.

    PATTERNS: Fault tolerance (continue on errors), No nested loops.
    """

    def __init__(self, max_examples_per_source: int=5):
        """
        Initialize example searcher.

        Args:
            max_examples_per_source: Max examples to retrieve per source
        """
        self.max_examples_per_source = max_examples_per_source

    def search_all_sources(self, strategies: List[ResearchStrategy], query: str, technologies: List[str]) -> List[ResearchExample]:
        """
        Search all sources for examples.

        WHY: Multiple sources increase likelihood of finding relevant examples.
             Fault tolerance ensures one failing source doesn't break research.

        Args:
            strategies: List of research strategies
            query: Search query
            technologies: Technologies list

        Returns:
            List of all examples found (may contain duplicates)

        Note:
            Errors in individual sources are caught and logged but don't fail
            the entire search operation.
        """
        all_examples = []
        for strategy in strategies:
            examples = self._search_single_source(strategy, query, technologies)
            all_examples.extend(examples)
        return all_examples

    def _search_single_source(self, strategy: ResearchStrategy, query: str, technologies: List[str]) -> List[ResearchExample]:
        """
        Search a single source with error handling.

        WHY: Isolated error handling for each source prevents cascading failures.

        Args:
            strategy: Research strategy to use
            query: Search query
            technologies: Technologies list

        Returns:
            List of examples from this source (empty list on error)
        """
        try:
            examples = strategy.search(query=query, technologies=technologies, max_results=self.max_examples_per_source)
            return examples
        except ResearchSourceError as e:
            
            logger.log(f'Warning: {e}', 'INFO')
            return []
        except Exception as e:
            source_name = self._get_source_name(strategy)
            
            logger.log(f'Warning: Unexpected error in {source_name}: {e}', 'INFO')
            return []

    def _get_source_name(self, strategy: ResearchStrategy) -> str:
        """
        Get source name from strategy.

        WHY: Provides better error messages for debugging.

        Args:
            strategy: Research strategy

        Returns:
            Source name or 'unknown'
        """
        try:
            return strategy.get_source_name()
        except Exception:
            return 'unknown'