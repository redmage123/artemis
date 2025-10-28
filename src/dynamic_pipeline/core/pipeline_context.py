#!/usr/bin/env python3
"""
Module: pipeline_context.py

WHY: Manages pipeline execution context including router guidance, AI service
     integration, and stage caching. Separates context management from pipeline
     execution logic.

RESPONSIBILITY: Single source of truth for pipeline context, router integration,
                and result caching.

PATTERNS:
    - Data Structure: Encapsulates context state and router metadata
    - Strategy: Provides methods to access different context aspects
    - Guard Clauses: Validates context access patterns
"""

from typing import Dict, Any, Optional, List
from dynamic_pipeline.stage_result import StageResult


class PipelineContext:
    """
    Pipeline execution context manager.

    WHY: Centralizes context management, router guidance extraction, and
         result caching. Prevents context-related logic from polluting
         pipeline execution code.

    RESPONSIBILITY: Manage execution context, router metadata, and cache.

    PATTERNS: Data encapsulation with controlled access methods.

    Attributes:
        context: Main execution context dictionary
        ai_service: Optional AI service for adaptive calls
        router_intensity: Pre-computed intensity from router (0.0-1.0)
        router_guidance: Router's prompt/guidance text
        suggested_workers: Suggested worker count from router
        priority_stages: Stages to prioritize from router
        optional_stages: Stages that can be skipped from router
        result_cache: Cache of successful stage results
    """

    def __init__(self, initial_context: Dict[str, Any]):
        """
        Initialize pipeline context.

        WHY: Extracts router metadata from context to avoid repeated lookups.

        Args:
            initial_context: Initial context with router metadata
        """
        self.context = initial_context.copy()

        # Extract router metadata (hybrid AI approach)
        self.ai_service = initial_context.get('ai_service')
        self.router_intensity = initial_context.get('intensity', 0.5)
        self.router_guidance = initial_context.get('prompt', '')
        self.suggested_workers = initial_context.get('suggested_max_workers', 4)
        self.priority_stages = initial_context.get('stages_to_prioritize', [])
        self.optional_stages = initial_context.get('stages_optional', [])

        # Result cache
        self.result_cache: Dict[str, StageResult] = {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from context.

        Args:
            key: Context key
            default: Default value if key not found

        Returns:
            Value from context or default
        """
        return self.context.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set value in context.

        Args:
            key: Context key
            value: Value to set
        """
        self.context[key] = value

    def copy(self) -> Dict[str, Any]:
        """
        Get copy of context.

        WHY: Prevents external mutation of internal state.

        Returns:
            Copy of context dictionary
        """
        return self.context.copy()

    def update_from_result(self, stage_name: str, result: StageResult) -> None:
        """
        Update context with stage result data.

        WHY: Allows subsequent stages to access previous stage results.

        Args:
            stage_name: Name of stage that produced result
            result: Stage result to add to context
        """
        self.context[f"{stage_name}_result"] = result.data

    def cache_result(self, stage_name: str, result: StageResult) -> None:
        """
        Cache successful stage result.

        WHY: Enables result reuse if stage is re-executed.

        Args:
            stage_name: Name of stage
            result: Result to cache
        """
        self.result_cache[stage_name] = result

    def get_cached_result(self, stage_name: str) -> Optional[StageResult]:
        """
        Get cached result for stage.

        Args:
            stage_name: Name of stage

        Returns:
            Cached result or None
        """
        return self.result_cache.get(stage_name)

    def clear_cache(self) -> None:
        """Clear result cache."""
        self.result_cache.clear()

    def has_ai_service(self) -> bool:
        """
        Check if AI service is available.

        Returns:
            True if AI service available
        """
        return self.ai_service is not None

    def is_low_intensity(self, threshold: float = 0.5) -> bool:
        """
        Check if router intensity is below threshold.

        WHY: Low intensity means simple execution plan without AI calls.

        Args:
            threshold: Intensity threshold (default 0.5)

        Returns:
            True if intensity below threshold
        """
        return self.router_intensity < threshold

    def get_router_metadata(self) -> Dict[str, Any]:
        """
        Get router metadata as dictionary.

        WHY: Useful for logging and debugging router integration.

        Returns:
            Dictionary with router metadata
        """
        return {
            'intensity': self.router_intensity,
            'guidance': self.router_guidance[:200] if self.router_guidance else '',
            'suggested_workers': self.suggested_workers,
            'priority_stages': self.priority_stages,
            'optional_stages': self.optional_stages
        }
