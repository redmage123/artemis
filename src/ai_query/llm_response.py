#!/usr/bin/env python3
"""
LLM Response Data Class

WHY: Encapsulates LLM response with metadata for cost tracking and analysis.

RESPONSIBILITY:
- Store LLM response content
- Track token usage and savings
- Calculate cost metrics
- Store model configuration

PATTERNS:
- Dataclass for immutability
- Optional error for graceful degradation
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM response with metadata"""
    content: str
    tokens_used: int
    tokens_saved: int  # Estimated savings from KG-First
    cost_usd: float
    model: str
    temperature: float
    error: Optional[str] = None
