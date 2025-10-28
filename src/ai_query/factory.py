#!/usr/bin/env python3
"""
AI Query Service Factory

WHY: Factory function to create AI Query Service with auto-detection of KG.

RESPONSIBILITY:
- Create configured AIQueryService instances
- Auto-detect Knowledge Graph if not provided
- Handle creation failures gracefully

PATTERNS:
- Factory Pattern
- Exception wrapping
"""

from typing import Optional, Any

from artemis_exceptions import ArtemisException, wrap_exception
from ai_query.ai_query_service_impl import AIQueryService


def create_ai_query_service(
    llm_client: Any,
    kg: Optional[Any] = None,
    rag: Optional[Any] = None,
    logger: Optional[Any] = None,
    verbose: bool = False
) -> AIQueryService:
    """
    Factory function to create AI Query Service

    Args:
        llm_client: LLM client instance
        kg: Knowledge Graph instance (optional)
        rag: RAG agent instance (optional)
        logger: Logger (optional)
        verbose: Enable verbose logging

    Returns:
        Configured AIQueryService instance
    """
    try:
        # Auto-detect KG if not provided
        if kg is None:
            try:
                from knowledge_graph_factory import get_knowledge_graph
                kg = get_knowledge_graph()
            except Exception:
                pass  # KG not available

        return AIQueryService(
            llm_client=llm_client,
            kg=kg,
            rag=rag,
            logger=logger,
            enable_kg=(kg is not None),
            enable_rag=(rag is not None),
            verbose=verbose
        )
    except Exception as e:
        raise wrap_exception(e, ArtemisException,
                           f"Failed to create AI Query Service: {str(e)}")
