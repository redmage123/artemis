#!/usr/bin/env python3
"""
Module: stage_result.py

WHY: Encapsulates all stage execution outcomes in an immutable value object,
     enabling clean data passing between stages and result caching.

RESPONSIBILITY: Store and provide access to stage execution metadata and results.

PATTERNS:
    - Value Object: Immutable result holder for functional composition
    - Data Transfer Object: Carries execution data between pipeline components
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class StageResult:
    """
    Result of stage execution.

    Why it exists: Encapsulates all stage execution data in single immutable
    object for passing between pipeline components and caching.

    Design pattern: Value Object (immutable result holder)

    Responsibilities:
    - Store stage execution success/failure status
    - Preserve stage output data for next stage
    - Track execution duration for metrics
    - Indicate if stage was skipped/retried
    - Provide optional error information
    """
    stage_name: str
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    duration: float = 0.0
    skipped: bool = False
    retry_count: int = 0
    error: Optional[Exception] = None

    def is_success(self) -> bool:
        """Check if stage succeeded (not failed, not skipped)"""
        return self.success and not self.skipped
