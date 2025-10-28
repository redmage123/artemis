#!/usr/bin/env python3
"""
WHY: Provide factory for creating research stages
RESPONSIBILITY: Create configured research stage instances
PATTERNS: Factory (creation abstraction), Open/Closed Principle

Factory enables different research stage configurations without code changes.
"""

from typing import Optional, List
from rag_agent import RAGAgent
from stages.research.stage import ResearchStage


def create_research_stage(
    rag_agent: RAGAgent,
    sources: Optional[List[str]] = None,
    max_examples: int = 5
) -> ResearchStage:
    """
    Create research stage with default configuration.

    WHY: Provides convenient factory function for common use case.
         Encapsulates default configuration values.

    Args:
        rag_agent: RAG agent
        sources: Research sources (default: all)
        max_examples: Max examples per source

    Returns:
        Configured ResearchStage instance

    Example:
        >>> from rag_agent import RAGAgent
        >>> rag = RAGAgent()
        >>> stage = create_research_stage(rag, sources=["local"])
    """
    return ResearchStage(
        rag_agent=rag_agent,
        sources=sources,
        max_examples_per_source=max_examples,
        timeout_seconds=30
    )


class ResearchStageFactory:
    """
    Factory for creating research stages.

    WHY: Enables different research stage configurations without code changes.
    PATTERNS: Factory pattern (Open/Closed principle).
    """

    @staticmethod
    def create_default(rag_agent: RAGAgent) -> ResearchStage:
        """
        Create research stage with default configuration.

        Args:
            rag_agent: RAG agent

        Returns:
            ResearchStage with default settings
        """
        return create_research_stage(rag_agent)

    @staticmethod
    def create_fast(rag_agent: RAGAgent) -> ResearchStage:
        """
        Create fast research stage (fewer examples, shorter timeout).

        WHY: For quick iterations where comprehensive research isn't needed.

        Args:
            rag_agent: RAG agent

        Returns:
            ResearchStage configured for speed
        """
        return ResearchStage(
            rag_agent=rag_agent,
            max_examples_per_source=2,
            timeout_seconds=10
        )

    @staticmethod
    def create_thorough(rag_agent: RAGAgent) -> ResearchStage:
        """
        Create thorough research stage (more examples, longer timeout).

        WHY: For complex tasks requiring comprehensive research.

        Args:
            rag_agent: RAG agent

        Returns:
            ResearchStage configured for thoroughness
        """
        return ResearchStage(
            rag_agent=rag_agent,
            max_examples_per_source=10,
            timeout_seconds=60
        )

    @staticmethod
    def create_local_only(rag_agent: RAGAgent) -> ResearchStage:
        """
        Create research stage using only local sources.

        WHY: For offline development or when external sources aren't available.

        Args:
            rag_agent: RAG agent

        Returns:
            ResearchStage configured for local-only research
        """
        return ResearchStage(
            rag_agent=rag_agent,
            sources=["local"],
            max_examples_per_source=5,
            timeout_seconds=30
        )
