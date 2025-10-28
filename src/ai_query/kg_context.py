#!/usr/bin/env python3
"""
Knowledge Graph Context Data Class

WHY: Encapsulates the results from Knowledge Graph queries before LLM calls.

RESPONSIBILITY:
- Store KG query results
- Track performance metrics (query time)
- Calculate estimated token savings

PATTERNS:
- Dataclass for immutability and clarity
- Optional error field for graceful degradation
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from ai_query.query_type import QueryType


@dataclass
class KGContext:
    """Knowledge Graph context retrieved before LLM call"""
    query_type: QueryType
    patterns_found: List[Dict[str, Any]]
    pattern_count: int
    estimated_token_savings: int
    kg_query_time_ms: float
    kg_available: bool
    error: Optional[str] = None
