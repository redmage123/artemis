#!/usr/bin/env python3
"""
Orchestration plan data structure

WHY:
Encapsulates all orchestration decisions (stages, resources, duration, reasoning) in an immutable,
validated data structure, ensuring plan integrity and providing serialization capabilities.

RESPONSIBILITY:
- Store orchestration plan configuration
- Validate plan integrity (complexity, stages, resources)
- Provide serialization (to_dict) for persistence
- Ensure immutability (frozen dataclass)

PATTERNS:
- Data Class: Structured data with automatic methods
- Immutability: Frozen dataclass prevents modification
- Validation: Guard clauses with early returns
- Serialization: Dictionary conversion for JSON/storage
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from artemis_exceptions import PipelineConfigurationError
from ai_orchestration.enums import VALID_COMPLEXITIES, VALID_EXECUTION_STRATEGIES
from ai_orchestration.constants import VALID_STAGES


@dataclass
class OrchestrationPlan:
    """
    Orchestration plan data structure

    Immutable once created (frozen=True for safety)
    """
    complexity: str
    task_type: str
    stages: List[str]
    skip_stages: List[str]
    parallel_developers: int
    max_parallel_tests: int
    execution_strategy: str
    estimated_duration_minutes: int
    reasoning: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'complexity': self.complexity,
            'task_type': self.task_type,
            'stages': self.stages,
            'skip_stages': self.skip_stages,
            'parallel_developers': self.parallel_developers,
            'max_parallel_tests': self.max_parallel_tests,
            'execution_strategy': self.execution_strategy,
            'estimated_duration_minutes': self.estimated_duration_minutes,
            'reasoning': self.reasoning
        }

    def validate(self) -> None:
        """
        Validate plan integrity with guard clauses (early return pattern)

        WHY: Guard clauses fail fast on first validation error, improving
        performance and readability. No need to check all conditions if one fails.

        Raises:
            PipelineConfigurationError: If plan is invalid
        """
        # Guard clause 1: Validate complexity (O(1) set membership check)
        if self.complexity not in VALID_COMPLEXITIES:
            raise PipelineConfigurationError(
                f"Invalid complexity: {self.complexity}",
                context={'valid_values': list(VALID_COMPLEXITIES)}
            )

        # Guard clause 2: Validate execution strategy (O(1) set membership check)
        if self.execution_strategy not in VALID_EXECUTION_STRATEGIES:
            raise PipelineConfigurationError(
                f"Invalid execution strategy: {self.execution_strategy}",
                context={'valid_values': list(VALID_EXECUTION_STRATEGIES)}
            )

        # Guard clause 3: Validate stages (O(n) but necessary)
        invalid_stages = [s for s in self.stages if s not in VALID_STAGES]
        if invalid_stages:
            raise PipelineConfigurationError(
                f"Invalid stages: {invalid_stages}",
                context={'valid_stages': list(VALID_STAGES)}
            )

        # Guard clause 4: Validate parallel developers minimum
        if self.parallel_developers < 1:
            raise PipelineConfigurationError(
                f"parallel_developers must be >= 1, got {self.parallel_developers}"
            )

        # Guard clause 5: Validate parallel tests minimum
        if self.max_parallel_tests < 1:
            raise PipelineConfigurationError(
                f"max_parallel_tests must be >= 1, got {self.max_parallel_tests}"
            )
