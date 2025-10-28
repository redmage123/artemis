#!/usr/bin/env python3
"""
Token Savings Metrics Data Class

WHY: Encapsulates metrics for tracking token savings and costs.

RESPONSIBILITY:
- Store aggregated token usage and savings
- Track cost metrics (actual and saved)
- Calculate savings percentages
- Track KG hit rates

PATTERNS:
- Dataclass for immutability
- Metrics aggregation
"""

from dataclasses import dataclass


@dataclass
class TokenSavingsMetrics:
    """Metrics for tracking token savings"""
    query_type: str
    queries_executed: int
    total_tokens_used: int
    total_tokens_saved: int
    total_cost_usd: float
    total_cost_saved_usd: float
    average_savings_percent: float
    kg_hits: int
    kg_misses: int
    kg_hit_rate: float
