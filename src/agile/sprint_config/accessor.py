#!/usr/bin/env python3
"""
Sprint Configuration Accessor - Unified Configuration Facade

WHY: Provides a single, simple interface for accessing all sprint configuration,
     hiding the complexity of multiple loaders and validators.
RESPONSIBILITY: Coordinate loading from multiple sources and provide unified access.
PATTERNS: Facade pattern, composition, factory methods

This is the main entry point for sprint configuration access. It composes
the various loaders and models into a cohesive, easy-to-use interface.
"""

from typing import Dict, Any, Optional
from omegaconf import DictConfig

from agile.sprint_config.models import (
    SprintPlanningConfig,
    ProjectReviewConfig,
    UIUXEvaluationConfig,
    RetrospectiveConfig
)
from agile.sprint_config.hydra_loader import (
    extract_sprint_planning,
    extract_project_review,
    extract_uiux_evaluation,
    extract_retrospective
)
from agile.sprint_config.dict_loader import (
    extract_sprint_planning_from_dict,
    extract_project_review_from_dict,
    extract_uiux_evaluation_from_dict,
    extract_retrospective_from_dict
)


class SprintConfigAccessor:
    """
    Facade for accessing all sprint workflow configuration.

    WHY: Provides single point of access for all sprint config with
         support for multiple config sources (Hydra, dict).
    RESPONSIBILITY: Coordinate config loading and provide unified access.
    PATTERNS: Facade pattern - simplifies complex subsystem interaction,
              Composition - composes multiple config models.

    Attributes:
        sprint_planning: Sprint planning configuration
        project_review: Project review configuration
        uiux_evaluation: UI/UX evaluation configuration
        retrospective: Retrospective configuration
    """

    def __init__(
        self,
        sprint_planning: SprintPlanningConfig,
        project_review: ProjectReviewConfig,
        uiux_evaluation: UIUXEvaluationConfig,
        retrospective: RetrospectiveConfig
    ) -> None:
        """
        Initialize accessor with configuration models.

        WHY: Enables dependency injection for testing.
        PATTERNS: Composition - contains multiple config models.

        Args:
            sprint_planning: Sprint planning configuration model
            project_review: Project review configuration model
            uiux_evaluation: UI/UX evaluation configuration model
            retrospective: Retrospective configuration model
        """
        self.sprint_planning = sprint_planning
        self.project_review = project_review
        self.uiux_evaluation = uiux_evaluation
        self.retrospective = retrospective

    @classmethod
    def from_hydra(cls, cfg: DictConfig) -> 'SprintConfigAccessor':
        """
        Create accessor from Hydra configuration.

        WHY: Factory method for creating from Hydra/OmegaConf sources.
        PATTERNS: Factory method - encapsulates creation logic.
        PERFORMANCE: O(n) where n is total config entries.

        Args:
            cfg: Hydra DictConfig object (from @hydra.main decorator)

        Returns:
            SprintConfigAccessor with all configurations loaded and validated

        Raises:
            ConfigurationError: If validation fails
            KeyError: If required config sections missing

        Example:
            @hydra.main(config_path="conf", config_name="config")
            def main(cfg: DictConfig):
                sprint_config = SprintConfigAccessor.from_hydra(cfg)
                velocity = sprint_config.sprint_planning.team_velocity
        """
        return cls(
            sprint_planning=extract_sprint_planning(cfg),
            project_review=extract_project_review(cfg),
            uiux_evaluation=extract_uiux_evaluation(cfg),
            retrospective=extract_retrospective(cfg)
        )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SprintConfigAccessor':
        """
        Create accessor from dictionary (for testing).

        WHY: Factory method enabling testing without Hydra dependency.
        PATTERNS: Factory method - encapsulates creation logic.
        PERFORMANCE: O(n) where n is total config entries.

        Args:
            config_dict: Dictionary with all sprint configuration sections

        Returns:
            SprintConfigAccessor with all configurations loaded and validated

        Raises:
            ConfigurationError: If validation fails
            KeyError: If required config sections missing

        Example:
            config = {
                'sprint_planning': {...},
                'project_review': {...},
                'uiux_evaluation': {...},
                'retrospective': {...}
            }
            accessor = SprintConfigAccessor.from_dict(config)
        """
        return cls(
            sprint_planning=extract_sprint_planning_from_dict(config_dict),
            project_review=extract_project_review_from_dict(config_dict),
            uiux_evaluation=extract_uiux_evaluation_from_dict(config_dict),
            retrospective=extract_retrospective_from_dict(config_dict)
        )

    def get_risk_score(self, risk_level: str) -> int:
        """
        Convenience method to get risk score.

        WHY: Provides direct access to commonly used sprint planning values.
        PERFORMANCE: O(1) dictionary lookup via model method.

        Args:
            risk_level: Risk level identifier (low/medium/high)

        Returns:
            Numeric risk score
        """
        return self.sprint_planning.get_risk_score(risk_level)

    def is_overcommitted(self, planned_points: float, capacity: float) -> bool:
        """
        Check if sprint is overcommitted.

        WHY: Encapsulates overcommitment logic using configured threshold.
        PERFORMANCE: O(1) - simple calculation.

        Args:
            planned_points: Planned story points for sprint
            capacity: Available capacity (velocity)

        Returns:
            True if planned points exceed capacity by threshold percentage
        """
        if capacity == 0:
            return False

        utilization = planned_points / capacity
        return utilization > self.project_review.overcommitted_threshold

    def is_underutilized(self, planned_points: float, capacity: float) -> bool:
        """
        Check if sprint is underutilized.

        WHY: Encapsulates underutilization logic using configured threshold.
        PERFORMANCE: O(1) - simple calculation.

        Args:
            planned_points: Planned story points for sprint
            capacity: Available capacity (velocity)

        Returns:
            True if planned points are below threshold percentage of capacity
        """
        if capacity == 0:
            return True

        utilization = planned_points / capacity
        return utilization < self.project_review.underutilized_threshold

    def __repr__(self) -> str:
        """
        String representation for debugging.

        WHY: Aids debugging by showing key configuration values.
        """
        return (
            f"SprintConfigAccessor("
            f"velocity={self.sprint_planning.team_velocity}, "
            f"sprint_days={self.sprint_planning.sprint_duration_days}, "
            f"approval_threshold={self.project_review.approval_threshold})"
        )
