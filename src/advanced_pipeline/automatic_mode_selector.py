#!/usr/bin/env python3
"""
Module: automatic_mode_selector.py

WHY this module exists:
    Provides automatic mode selection based on task characteristics including
    complexity, priority, story points, and keywords.

RESPONSIBILITY:
    - Analyze task characteristics (story points, priority, keywords)
    - Calculate complexity score
    - Map complexity to appropriate execution mode
    - Override mode based on special keywords
    - Log selection rationale

PATTERNS:
    - Strategy Pattern: Concrete strategy implementation
    - Dispatch Table Pattern: Threshold-based mode mapping
"""

from typing import Dict, Any, Optional

from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from advanced_pipeline.mode_selection_strategy import ModeSelectionStrategy
from advanced_pipeline.pipeline_mode import PipelineMode
from advanced_pipeline.pipeline_config import AdvancedPipelineConfig


class AutomaticModeSelector(ModeSelectionStrategy):
    """
    Automatic mode selection based on task characteristics.

    WHY: Selects optimal mode automatically using task complexity, priority,
    story points, and keywords. Implements heuristics refined from experience.

    Selection algorithm:
        1. Extract task characteristics (story points, priority, keywords)
        2. Calculate complexity score
        3. Map complexity to mode using thresholds
        4. Override based on special keywords (e.g., "experimental" -> TWO_PASS)

    Complexity scoring:
        - Story points: Direct contribution to score
        - Priority: high=2, medium=1, low=0
        - Keywords: complex keywords +1, simple keywords -1
        - Final score: sum of contributions

    Mode mapping:
        - score <= 3: STANDARD (simple tasks)
        - 3 < score <= 5: DYNAMIC (moderate tasks)
        - 5 < score <= 8: ADAPTIVE (complex tasks)
        - score > 8: FULL (very complex tasks)
    """

    def __init__(
        self,
        config: AdvancedPipelineConfig,
        logger: Optional[PipelineLogger] = None
    ):
        """
        Initialize automatic selector.

        Args:
            config: Configuration with thresholds
            logger: Logger for selection rationale
        """
        self.config = config
        self.logger = logger or PipelineLogger(verbose=True)

    @wrap_exception(PipelineException, "Automatic mode selection failed")
    def select_mode(self, context: Dict[str, Any]) -> PipelineMode:
        """
        Select mode automatically based on task characteristics.

        WHAT: Analyzes task complexity, priority, and requirements to select
        optimal execution mode. Uses scoring algorithm with configurable thresholds.

        Args:
            context: Task context containing:
                - card: Kanban card with task details
                - story_points: Task size estimate
                - priority: Task priority (high/medium/low)
                - description: Task description for keyword analysis

        Returns:
            Selected PipelineMode with rationale logged
        """
        card = context.get("card", {})

        # Extract task characteristics
        story_points = card.get("story_points", card.get("points", 5))
        priority = card.get("priority", "medium")
        description = card.get("description", "").lower()
        title = card.get("title", "").lower()
        combined_text = f"{title} {description}"

        # Calculate complexity score using helper method
        complexity_score = self._calculate_complexity_score(
            story_points, priority, combined_text
        )

        # Select mode based on score using dispatch table
        # WHY dispatch table: No elif chain, easy to configure, declarative
        mode_thresholds = [
            (self.config.complex_task_min_story_points, PipelineMode.FULL),
            (self.config.simple_task_max_story_points + 2, PipelineMode.ADAPTIVE),
            (self.config.simple_task_max_story_points, PipelineMode.DYNAMIC),
            (0, PipelineMode.STANDARD)
        ]

        selected_mode = next(
            mode for threshold, mode in mode_thresholds
            if complexity_score > threshold
        )

        # Override based on keywords (special cases)
        mode_overrides = self._check_mode_overrides(combined_text)
        if mode_overrides:
            selected_mode = mode_overrides

        # Log selection rationale
        self.logger.log(
            f"Mode selected: {selected_mode.value} "
            f"(complexity_score={complexity_score}, story_points={story_points})",
            "INFO"
        )

        return selected_mode

    def _calculate_complexity_score(
        self,
        story_points: int,
        priority: str,
        text: str
    ) -> float:
        """
        Calculate task complexity score.

        WHY extracted: Separates scoring logic from mode selection logic.
        Enables testing and refinement of scoring algorithm independently.

        Args:
            story_points: Task size estimate
            priority: Task priority
            text: Combined title + description

        Returns:
            Complexity score (higher = more complex)
        """
        score = 0.0

        # Story points contribution (direct mapping)
        score += story_points

        # Priority contribution using dispatch table
        priority_scores = {"high": 2, "medium": 1, "low": 0}
        score += priority_scores.get(priority, 1)

        # Keyword analysis contribution
        complex_keywords = [
            "architecture", "refactor", "migrate", "integrate",
            "performance", "scalability", "distributed", "microservice",
            "complex", "advanced", "experimental"
        ]
        simple_keywords = [
            "fix", "update", "small", "minor", "simple", "quick", "trivial"
        ]

        # Count keyword occurrences
        complex_count = sum(1 for kw in complex_keywords if kw in text)
        simple_count = sum(1 for kw in simple_keywords if kw in text)

        # Add keyword contribution (complex +1 each, simple -1 each)
        score += complex_count - simple_count

        return max(0, score)  # Ensure non-negative

    def _check_mode_overrides(self, text: str) -> Optional[PipelineMode]:
        """
        Check for keyword-based mode overrides.

        WHY: Some keywords indicate specific mode requirements regardless
        of complexity score. For example, "prototype" suggests two-pass
        for fast feedback.

        Args:
            text: Combined title + description

        Returns:
            Override mode or None
        """
        # Dispatch table for keyword -> mode overrides
        # WHY dispatch table: Declarative, easy to extend
        override_keywords = {
            "prototype": PipelineMode.TWO_PASS,
            "experiment": PipelineMode.TWO_PASS,
            "poc": PipelineMode.TWO_PASS,  # Proof of concept
            "spike": PipelineMode.DYNAMIC,  # Investigation task
            "research": PipelineMode.ADAPTIVE,  # High uncertainty
            "critical": PipelineMode.FULL  # Critical tasks get full features
        }

        # Check for override keywords
        for keyword, mode in override_keywords.items():
            if keyword in text:
                return mode

        return None
