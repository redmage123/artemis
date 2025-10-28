#!/usr/bin/env python3
"""
Module: rag_storage.py

WHY: Store sprint plans in RAG for learning and future reference
RESPONSIBILITY: Persist sprint planning artifacts to RAG storage
PATTERNS: Helper pattern for DRY RAG storage operations
"""

from typing import List, Any
from sprint_models import Sprint
from planning_poker import FeatureEstimate
from artemis_stage_interface import LoggerInterface
from rag_storage_helper import RAGStorageHelper


class SprintPlanRAGStorage:
    """
    WHY: RAG storage enables learning from past sprint estimates
    RESPONSIBILITY: Format and store sprint plans in RAG
    PATTERNS: Template Method pattern for summary generation
    """

    def __init__(self, rag: Any, logger: LoggerInterface):
        """
        WHY: Need RAG interface for storage

        Args:
            rag: RAG agent interface
            logger: Logger for error handling
        """
        self.rag = rag
        self.logger = logger

    def store_sprint_plan(
        self,
        card_id: str,
        task_title: str,
        sprints: List[Sprint],
        estimates: List[FeatureEstimate]
    ) -> None:
        """
        WHY: Persist sprint plan for future reference and learning
        RESPONSIBILITY: Generate summary and store in RAG
        PATTERNS: Guard clause, graceful degradation

        Args:
            card_id: Card identifier
            task_title: Task title
            sprints: List of Sprint objects
            estimates: List of FeatureEstimate objects
        """
        # Guard: No sprints to store
        if not sprints:
            return

        try:
            summary = self._generate_summary(
                task_title,
                sprints,
                estimates
            )
            metadata = self._build_metadata(sprints, estimates)

            RAGStorageHelper.store_stage_artifact(
                rag=self.rag,
                stage_name="sprint_plan",
                card_id=card_id,
                task_title=task_title,
                content=summary,
                metadata=metadata
            )
        except Exception as e:
            # Log but don't fail - RAG storage is not critical
            self.logger.log(
                f"Error storing sprint plan in RAG: {e}",
                "ERROR"
            )

    def _generate_summary(
        self,
        task_title: str,
        sprints: List[Sprint],
        estimates: List[FeatureEstimate]
    ) -> str:
        """
        WHY: Human-readable summary for RAG retrieval
        RESPONSIBILITY: Format sprint plan as readable text
        """
        total_points = sum(s.total_story_points for s in sprints)
        avg_confidence = (
            sum(e.confidence for e in estimates) / max(len(estimates), 1)
        )

        summary_parts = [
            f"Sprint Plan: {task_title}",
            "",
            f"Total Features: {len(estimates)}",
            f"Total Story Points: {total_points}",
            f"Total Sprints: {len(sprints)}",
            f"Average Confidence: {avg_confidence:.0%}",
            "",
            "Sprint Breakdown:"
        ]

        for sprint in sprints:
            summary_parts.extend([
                "",
                (
                    f"Sprint {sprint.sprint_number} "
                    f"({sprint.start_date.strftime('%Y-%m-%d')} to "
                    f"{sprint.end_date.strftime('%Y-%m-%d')}):"
                ),
                f"  - {len(sprint.features)} features",
                f"  - {sprint.total_story_points} story points",
                f"  - {sprint.capacity_used:.0%} capacity used"
            ])

        return "\n".join(summary_parts)

    def _build_metadata(
        self,
        sprints: List[Sprint],
        estimates: List[FeatureEstimate]
    ) -> dict:
        """
        WHY: Structured metadata enables analytics on sprint plans
        RESPONSIBILITY: Build metadata dictionary
        """
        total_points = sum(s.total_story_points for s in sprints)
        avg_confidence = (
            sum(e.confidence for e in estimates) / max(len(estimates), 1)
        )

        return {
            'total_sprints': len(sprints),
            'total_story_points': total_points,
            'average_confidence': avg_confidence,
            'sprints': [s.to_dict() for s in sprints]
        }
