#!/usr/bin/env python3
"""
Planning Poker Core Orchestration

WHY: Orchestrates Planning Poker estimation process, coordinating voting
sessions, consensus building, and risk assessment.

RESPONSIBILITY:
- Coordinate multi-round estimation process
- Manage voting sessions and consensus checking
- Calculate final estimates with confidence and risk
- Broadcast estimation events to observers
- Provide batch estimation for multiple features

PATTERNS:
- Facade Pattern: Simplified interface for complex estimation process
- Observer Pattern: Event broadcasting for progress tracking
- Strategy Pattern: Pluggable consensus and estimation strategies
- Guard Clauses: Early validation and error handling
"""

from typing import List, Optional, Dict, TYPE_CHECKING

from artemis_stage_interface import LoggerInterface
from llm_client import LLMClient
from pipeline_observer import PipelineEvent, EventType, PipelineObservable

from .models import (
    EstimationVote,
    EstimationRound,
    FeatureEstimate,
    FibonacciScale
)
from .voting_session import VotingSession
from .consensus_builder import ConsensusBuilder
from .estimator import Estimator

# Conditional imports for type checking
if TYPE_CHECKING:
    from ai_query_service import AIQueryService


class PlanningPoker:
    """
    Planning Poker implementation for AI agent teams

    WHY: Simulates Scrum Planning Poker with AI agents voting on story
    complexity, discussing outliers, and converging on consensus estimates.

    Integrations:
    - Observer Pattern: Broadcasts estimation events
    - AI Query Service: Uses KG-First approach for context
    - Parallel Execution: Concurrent agent voting for 3x speedup
    """

    def __init__(
        self,
        agents: List[str],
        llm_client: LLMClient,
        logger: LoggerInterface,
        team_velocity: float = 20.0,
        max_rounds: int = 3,
        observable: Optional[PipelineObservable] = None,
        ai_service: Optional['AIQueryService'] = None
    ):
        """
        Initialize Planning Poker

        Args:
            agents: List of agent names (e.g., ["architect", "developer", "qa"])
            llm_client: LLM client for generating votes
            logger: Logger interface
            team_velocity: Team's average story points per sprint
            max_rounds: Maximum voting rounds before forcing consensus
            observable: Optional PipelineObservable for event broadcasting
            ai_service: Optional AIQueryService for KG-First optimization
        """
        # Guard clause: validate agents
        if not agents:
            raise ValueError("At least one agent required for Planning Poker")

        self.agents = agents
        self.llm_client = llm_client
        self.logger = logger
        self.team_velocity = team_velocity
        self.max_rounds = max_rounds
        self.observable = observable
        self.ai_service = ai_service

        # Initialize components
        self.voting_session = VotingSession(agents, llm_client, logger, observable)
        self.consensus_builder = ConsensusBuilder()
        self.estimator = Estimator(team_velocity)

        # Fibonacci values for voting
        self.fibonacci_values = [v.value for v in FibonacciScale]

        # Notify initialization
        self._notify_event(EventType.STAGE_PROGRESS, {
            "message": "Planning Poker initialized",
            "agents": agents,
            "max_rounds": max_rounds
        })

    def estimate_feature(
        self,
        feature_title: str,
        feature_description: str,
        acceptance_criteria: List[str]
    ) -> FeatureEstimate:
        """
        Run Planning Poker to estimate a feature

        WHY: Provides structured estimation with consensus tracking

        Process:
        1. Conduct voting rounds until consensus or max rounds
        2. Generate discussion for divergent votes
        3. Force consensus if needed
        4. Calculate confidence and risk

        Args:
            feature_title: Feature name
            feature_description: Detailed description
            acceptance_criteria: List of acceptance criteria

        Returns:
            FeatureEstimate with consensus story points
        """
        self.logger.log(f"🎯 Planning Poker: Estimating '{feature_title}'", "INFO")

        # Notify estimation started
        self._notify_event(EventType.STAGE_STARTED, {
            "feature_title": feature_title,
            "feature_description": feature_description,
            "acceptance_criteria_count": len(acceptance_criteria)
        })

        rounds = []
        consensus_reached = False
        final_estimate = None

        # Conduct voting rounds
        for round_num in range(1, self.max_rounds + 1):
            self.logger.log(f"📊 Round {round_num} of {self.max_rounds}", "INFO")

            # Collect votes
            votes = self.voting_session.collect_votes(
                feature_title,
                feature_description,
                acceptance_criteria,
                round_num,
                previous_votes=rounds[-1].votes if rounds else None
            )

            # Check for consensus
            consensus, estimate = self.consensus_builder.check_consensus(votes)

            # Generate discussion if no consensus
            discussion = ""
            if not consensus and round_num < self.max_rounds:
                discussion = self.consensus_builder.generate_discussion(votes)
                self.logger.log(f"💬 Discussion: {discussion}", "INFO")
            elif consensus:
                self.logger.log(
                    f"✅ Consensus reached: {estimate} story points",
                    "SUCCESS"
                )

            # Store round
            round_data = EstimationRound(
                round_number=round_num,
                votes=votes,
                consensus_reached=consensus,
                final_estimate=estimate if consensus else None,
                discussion_summary=discussion
            )
            rounds.append(round_data)

            # Break if consensus reached
            if consensus:
                consensus_reached = True
                final_estimate = estimate
                break

        # Force consensus if max rounds reached
        if not consensus_reached:
            final_estimate = self.consensus_builder.force_consensus(rounds[-1].votes)
            rounds[-1].consensus_reached = True
            rounds[-1].final_estimate = final_estimate
            self.logger.log(
                f"⚡ Forced consensus after {self.max_rounds} rounds: {final_estimate} points",
                "WARNING"
            )

        # Calculate confidence and risk
        confidence = self.estimator.calculate_confidence(rounds)
        risk_level = self.estimator.assess_risk(final_estimate, confidence)
        estimated_hours = self.estimator.calculate_estimated_hours(final_estimate)

        # Notify estimation completed
        self._notify_event(EventType.STAGE_COMPLETED, {
            "feature_title": feature_title,
            "final_estimate": final_estimate,
            "confidence": confidence,
            "risk_level": risk_level,
            "estimated_hours": estimated_hours,
            "rounds_needed": len(rounds)
        })

        return FeatureEstimate(
            feature_title=feature_title,
            feature_description=feature_description,
            rounds=rounds,
            final_estimate=final_estimate,
            confidence=confidence,
            risk_level=risk_level,
            estimated_hours=estimated_hours
        )

    def estimate_features_batch(
        self,
        features: List[Dict]
    ) -> List[FeatureEstimate]:
        """
        Estimate multiple features using Planning Poker

        WHY: Provides convenient batch estimation interface

        Args:
            features: List of feature dicts with title, description, acceptance_criteria

        Returns:
            List of FeatureEstimate objects
        """
        # Guard clause: no features
        if not features:
            self.logger.log("No features to estimate", "WARNING")
            return []

        estimates = []

        for i, feature in enumerate(features, 1):
            self.logger.log(f"\n{'='*60}", "INFO")
            self.logger.log(f"Feature {i}/{len(features)}", "INFO")
            self.logger.log(f"{'='*60}", "INFO")

            estimate = self.estimate_feature(
                feature_title=feature.get("title", "Unknown Feature"),
                feature_description=feature.get("description", ""),
                acceptance_criteria=feature.get("acceptance_criteria", [])
            )

            estimates.append(estimate)

            self.logger.log(
                f"✅ Estimated: {estimate.final_estimate} points "
                f"(confidence: {estimate.confidence:.0%}, risk: {estimate.risk_level})",
                "SUCCESS"
            )

        return estimates

    def _notify_event(self, event_type: EventType, data: Dict) -> None:
        """
        Notify observers of estimation event

        WHY: Enables progress monitoring and integration

        Args:
            event_type: Type of event
            data: Event data
        """
        if not self.observable:
            return

        event = PipelineEvent(
            event_type=event_type,
            stage_name="planning_poker",
            data=data
        )
        self.observable.notify(event)


def estimate_features_batch(
    features: List[Dict],
    poker: PlanningPoker,
    logger: LoggerInterface
) -> List[FeatureEstimate]:
    """
    Estimate multiple features using Planning Poker

    WHY: Provides standalone batch estimation function for backward compatibility

    Args:
        features: List of feature dicts with title, description, acceptance_criteria
        poker: PlanningPoker instance
        logger: Logger

    Returns:
        List of FeatureEstimate objects
    """
    return poker.estimate_features_batch(features)
