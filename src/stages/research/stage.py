#!/usr/bin/env python3
"""
WHY: Orchestrate code example research before development begins
RESPONSIBILITY: Execute research pipeline and integrate with stage framework
PATTERNS: Facade (simplified API), Composition (searcher, storage, formatter)

Research stage coordinates searching multiple sources for code examples,
storing results in RAG, and reporting findings. Integrates with Observer
Pattern via stage notifications.
"""

from typing import Dict, Any, List, Optional

from artemis_stages import PipelineStage
from rag_agent import RAGAgent
from research_strategy import ResearchStrategyFactory, ResearchStrategy, ResearchExample
from research_repository import ExampleRepository
from research_exceptions import ResearchStageError, ResearchSourceError

from stages.research.query_builder import format_research_query
from stages.research.example_searcher import ExampleSearcher
from stages.research.example_storage import ExampleStorage
from stages.research.summary_formatter import SummaryFormatter


class ResearchStage(PipelineStage):
    """
    Research Stage - Retrieves code examples before development begins.

    WHY: Developers benefit from seeing existing implementations before coding.
         Reduces hallucination by providing concrete examples.

    RESPONSIBILITY: Orchestrate research pipeline - search, store, report.
    PATTERNS: Facade (simplified API), Composition (specialized components).

    Searches multiple sources (GitHub, HuggingFace, local) for relevant
    code examples and stores them in RAG for developers to query.
    """

    def __init__(
        self,
        rag_agent: RAGAgent,
        sources: Optional[List[str]] = None,
        max_examples_per_source: int = 5,
        timeout_seconds: int = 30
    ):
        """
        Initialize Research Stage.

        Args:
            rag_agent: RAG agent for storage
            sources: List of research sources to use (default: all)
            max_examples_per_source: Max examples per source
            timeout_seconds: Timeout for research operations
        """
        self.rag = rag_agent
        self.sources = sources or ResearchStrategyFactory.get_available_sources()
        self.timeout_seconds = timeout_seconds

        # Initialize components (Composition pattern)
        self.repository = ExampleRepository(rag_agent)
        self.searcher = ExampleSearcher(max_examples_per_source)
        self.storage = ExampleStorage(self.repository)
        self.formatter = SummaryFormatter()

    def execute(self, card: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research stage.

        WHY: Orchestrates the complete research pipeline before development.

        Args:
            card: Kanban card containing task details
            context: Pipeline context with:
                - card_id: Card ID
                - task_title: Task title
                - task_description: Description
                - technologies: List of technologies
                - project_type: Project type (optional)

        Returns:
            Result dict with:
                - success: Boolean
                - status: Status string
                - examples_found: Number of examples found
                - examples_stored: Number of examples stored
                - sources_searched: List of sources searched
                - artifact_ids: List of stored artifact IDs
                - research_summary: Summary of research

        Raises:
            ResearchStageError: If stage fails
        """
        # Extract context
        card_id = context.get('card_id', 'unknown')
        task_title = context.get('task_title', 'Unknown Task')
        task_description = context.get('task_description', '')
        technologies = context.get('technologies', [])

        try:
            # Build research query
            query = format_research_query(task_title, task_description, technologies)

            # Create research strategies (Factory Pattern)
            strategies = self._create_strategies()

            # Search all sources
            all_examples = self.searcher.search_all_sources(
                strategies,
                query,
                technologies
            )

            # Deduplicate and rank
            unique_examples = self.repository.deduplicate_examples(all_examples)
            ranked_examples = self.repository.rank_examples_by_relevance(
                unique_examples,
                query,
                technologies
            )

            # Store top examples
            top_examples = ranked_examples[:self.searcher.max_examples_per_source * len(strategies)]
            artifact_ids = self.storage.store_examples(
                top_examples,
                card_id,
                task_title
            )

            # Build summary
            summary = self.formatter.format_summary(top_examples, strategies)

            # Return result
            return {
                "success": True,
                "status": "COMPLETE",
                "examples_found": len(all_examples),
                "examples_stored": len(artifact_ids),
                "sources_searched": self.sources,
                "artifact_ids": artifact_ids,
                "research_summary": summary
            }

        except ResearchSourceError as e:
            # Wrap and re-raise research errors
            error_msg = f"Research stage failed: {e}"
            raise ResearchStageError(error_msg, cause=e)

        except Exception as e:
            # Wrap unexpected errors
            error_msg = f"Unexpected error in research stage: {str(e)}"
            raise ResearchStageError(error_msg, cause=e)

    def _create_strategies(self) -> List[ResearchStrategy]:
        """
        Create research strategies using Factory Pattern.

        WHY: Encapsulates strategy creation and handles errors.

        Returns:
            List of research strategies

        Raises:
            ResearchStageError: If strategy creation fails
        """
        try:
            # Use comprehension instead of loop
            strategies = [
                ResearchStrategyFactory.create_strategy(
                    source,
                    timeout_seconds=self.timeout_seconds
                )
                for source in self.sources
            ]

            return strategies

        except ValueError as e:
            raise ResearchStageError(
                f"Failed to create research strategies: {e}",
                cause=e
            )

    def validate_prerequisites(self, context: Dict[str, Any]) -> bool:
        """
        Validate that context has required fields.

        WHY: Fail fast if required context is missing.

        Args:
            context: Pipeline context

        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ['card_id', 'task_title']

        # Use all() with generator expression instead of loop
        return all(field in context for field in required_fields)

    def get_required_context_keys(self) -> List[str]:
        """Get list of required context keys"""
        return ['card_id', 'task_title']

    def get_optional_context_keys(self) -> List[str]:
        """Get list of optional context keys"""
        return ['task_description', 'technologies', 'project_type']

    def get_stage_name(self) -> str:
        """Get stage name"""
        return "research"

    def get_stage_description(self) -> str:
        """Get stage description"""
        return (
            "Research Stage: Searches multiple sources (GitHub, HuggingFace, local) "
            "for relevant code examples and stores them in RAG for developer reference."
        )

    def supports_async(self) -> bool:
        """This stage supports async execution"""
        return True
