#!/usr/bin/env python3
"""
WHY: Define data models and enumerations for self-critique validation.

RESPONSIBILITY:
- CritiqueLevel, CritiqueSeverity enumerations for classification
- CritiqueFinding for individual validation findings
- UncertaintyMetrics for code uncertainty analysis
- CodeCitation for tracking code pattern sources
- CritiqueResult as the complete validation result container

PATTERNS:
- Dataclass Pattern: Immutable data structures with type safety
- Enumeration Pattern: Type-safe constants for critique levels and severities
- Value Object Pattern: Self-contained data objects with no business logic
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class CritiqueLevel(Enum):
    """
    WHY: Define depth of self-critique analysis for performance tuning.

    Depth levels allow trade-off between speed and thoroughness.
    """
    QUICK = "quick"           # Basic checks only (~2s)
    BALANCED = "balanced"     # Standard checks (~5s)
    THOROUGH = "thorough"     # Comprehensive checks (~10s)


class CritiqueSeverity(Enum):
    """
    WHY: Classify severity of critique findings for prioritization.

    Severity levels enable filtering and prioritization of issues.
    """
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class CritiqueFinding:
    """
    WHY: Represent a single finding from self-critique analysis.

    RESPONSIBILITY:
    - Store severity level, category, and descriptive message
    - Track optional line number for precise location
    - Provide actionable suggestion for resolution
    """
    severity: CritiqueSeverity
    category: str  # 'logic', 'edge_case', 'performance', 'security', 'hallucination'
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class UncertaintyMetrics:
    """
    WHY: Quantify code uncertainty to detect hallucination signals.

    RESPONSIBILITY:
    - Calculate uncertainty score (0-10 scale)
    - Track hedging language in comments/docstrings
    - Identify placeholder comments (TODO, FIXME)
    - Detect conditional assumptions
    - Flag missing error handling
    """
    uncertainty_score: float  # 0-10 scale
    hedging_words: List[str] = field(default_factory=list)
    placeholder_comments: List[str] = field(default_factory=list)
    conditional_assumptions: List[str] = field(default_factory=list)
    missing_error_handling: List[str] = field(default_factory=list)


@dataclass
class CodeCitation:
    """
    WHY: Track source of code patterns for verifiability.

    RESPONSIBILITY:
    - Store code pattern and its claimed source
    - Maintain confidence level in citation accuracy
    - Enable future RAG-based verification
    """
    pattern: str  # The code pattern
    source: str   # Where it came from
    confidence: float  # 0-1 confidence in citation


@dataclass
class CritiqueResult:
    """
    WHY: Aggregate all validation results into single response object.

    RESPONSIBILITY:
    - Indicate pass/fail status
    - Provide LLM confidence score
    - Collect all findings, metrics, and citations
    - Determine regeneration necessity
    - Supply feedback for code improvement
    """
    passed: bool
    confidence_score: float  # 0-10 from LLM
    findings: List[CritiqueFinding]
    uncertainty_metrics: UncertaintyMetrics
    citations: List[CodeCitation]
    raw_critique: str
    regeneration_needed: bool
    feedback: str  # Feedback to use for regeneration
