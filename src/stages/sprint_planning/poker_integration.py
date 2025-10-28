#!/usr/bin/env python3
"""
Module: poker_integration.py

WHY: Integrate Planning Poker estimation with sprint planning workflow
RESPONSIBILITY: Coordinate multi-agent estimation for feature story points
PATTERNS: Adapter pattern to bridge Planning Poker and Sprint Planning
"""

from typing import List, Optional, Any
from artemis_stage_interface import LoggerInterface
from llm_client import LLMClient
from sprint_models import Feature
from planning_poker import PlanningPoker, estimate_features_batch, FeatureEstimate
from pipeline_observer import PipelineObservable
from artemis_exceptions import PlanningPokerError, wrap_exception


class PokerIntegration:
    """
    WHY: Planning Poker is complex; isolate it from main stage logic
    RESPONSIBILITY: Run Planning Poker estimation and return results
    PATTERNS: Adapter pattern, Facade pattern for simplified interface
    """

    def __init__(
        self,
        llm_client: LLMClient,
        logger: LoggerInterface,
        poker_agents: List[str],
        team_velocity: float,
        observable: Optional[PipelineObservable] = None,
        ai_service: Optional[Any] = None
    ):
        """
        WHY: Need LLM client and config to run Planning Poker

        Args:
            llm_client: LLM client for agent voting
            logger: Logger for progress tracking
            poker_agents: List of agent perspectives (conservative, moderate, aggressive)
            team_velocity: Team velocity for capacity calculation
            observable: Observer for real-time progress events
            ai_service: AI Query Service for intelligent estimation
        """
        self.llm_client = llm_client
        self.logger = logger
        self.poker_agents = poker_agents
        self.team_velocity = team_velocity
        self.observable = observable
        self.ai_service = ai_service

    def estimate_features(self, features: List[Feature]) -> List[FeatureEstimate]:
        """
        WHY: Centralized estimation logic with error handling
        RESPONSIBILITY: Run Planning Poker and return estimates
        PATTERNS: Guard clause for empty input

        Args:
            features: List of Feature objects to estimate

        Returns:
            List of FeatureEstimate objects with story points

        Raises:
            PlanningPokerError: If estimation fails
        """
        # Guard: No features to estimate
        if not features:
            return []

        try:
            poker = PlanningPoker(
                agents=self.poker_agents,
                llm_client=self.llm_client,
                logger=self.logger,
                team_velocity=self.team_velocity,
                observable=self.observable,
                ai_service=self.ai_service
            )

            # Convert features to dicts (Planning Poker expects dicts)
            feature_dicts = [f.to_dict() for f in features]
            estimates = estimate_features_batch(
                feature_dicts,
                poker,
                self.logger
            )

            return estimates

        except Exception as e:
            raise wrap_exception(
                e,
                PlanningPokerError,
                "Planning Poker estimation failed",
                {"feature_count": len(features)}
            )
