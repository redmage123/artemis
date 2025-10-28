#!/usr/bin/env python3
"""
Retrospective Agent Core - Sprint Learning and Continuous Improvement

WHY: Orchestrate sprint retrospective analysis
RESPONSIBILITY: Coordinate retrospective workflow components
PATTERNS: Facade Pattern, Single Responsibility, Guard Clauses

Main Responsibilities:
1. Analyze completed sprints for successes and failures
2. Extract learnings and patterns
3. Generate actionable improvements for next sprint
4. Store learnings in RAG for team knowledge
5. Communicate retrospective findings to orchestrator and team
"""

from typing import Dict, List, Any

from artemis_stage_interface import LoggerInterface
from llm_client import LLMClient
from debug_mixin import DebugMixin

from .retrospective_models import (
    RetrospectiveReport,
    RetrospectiveContext,
    SprintMetrics,
    RetrospectiveItem
)
from .metrics_extractor import MetricsExtractor
from .success_analyzer import SuccessAnalyzer
from .failure_analyzer import FailureAnalyzer
from .action_item_generator import ActionItemGenerator
from .learning_extractor import LearningExtractor
from .health_assessor import HealthAssessor
from .recommendation_generator import RecommendationGenerator
from .retrospective_storage import RetrospectiveStorage


class RetrospectiveAgent(DebugMixin):
    """
    Retrospective Agent - Learn from sprints and improve process

    WHY: Facilitate continuous improvement through retrospectives
    RESPONSIBILITY: Orchestrate retrospective analysis workflow
    PATTERNS: Facade Pattern, Dependency Injection, Guard Clauses

    Analyzes sprint outcomes, extracts patterns, generates improvements
    """

    def __init__(
        self,
        llm_client: LLMClient,
        rag: Any,
        logger: LoggerInterface,
        messenger: Any,
        historical_sprints_to_analyze: int = 3
    ):
        """
        Initialize Retrospective Agent

        Args:
            llm_client: LLM client for analysis
            rag: RAG agent for storing and retrieving learnings
            logger: Logger interface
            messenger: AgentMessenger for communicating results
            historical_sprints_to_analyze: Number of past sprints to compare

        WHY: Dependency injection for all components
        PATTERNS: Constructor injection with defaults
        """
        DebugMixin.__init__(self, component_name="retrospective")

        self.llm_client = llm_client
        self.rag = rag
        self.logger = logger
        self.messenger = messenger
        self.historical_sprints_to_analyze = historical_sprints_to_analyze

        # Initialize component modules
        self.metrics_extractor = MetricsExtractor()
        self.success_analyzer = SuccessAnalyzer(llm_client, logger)
        self.failure_analyzer = FailureAnalyzer(llm_client, logger)
        self.action_item_generator = ActionItemGenerator()
        self.learning_extractor = LearningExtractor()
        self.health_assessor = HealthAssessor()
        self.recommendation_generator = RecommendationGenerator()
        self.storage = RetrospectiveStorage(rag, messenger, logger)

        self.debug_log("RetrospectiveAgent initialized", historical_sprints=historical_sprints_to_analyze)

    def conduct_retrospective(
        self,
        sprint_number: int,
        sprint_data: Dict[str, Any],
        card_id: str
    ) -> RetrospectiveReport:
        """
        Conduct sprint retrospective

        Args:
            sprint_number: Sprint number
            sprint_data: Sprint execution data (metrics, events, outcomes)
            card_id: Card ID for storing retrospective

        Returns:
            RetrospectiveReport with findings and recommendations

        WHY: Orchestrate complete retrospective workflow
        RESPONSIBILITY: Coordinate all retrospective components
        PATTERNS: Facade Pattern, Guard Clauses
        """
        self.debug_trace("conduct_retrospective", sprint_number=sprint_number, card_id=card_id)
        self.logger.log(f"🔄 Sprint {sprint_number} Retrospective", "INFO")

        # Step 1: Extract metrics from sprint data
        metrics = self.metrics_extractor.extract_metrics(sprint_data)

        # Step 2: Retrieve historical sprint data for comparison
        historical_data = self._retrieve_historical_sprints(card_id)

        # Step 3: Analyze what went well
        what_went_well = self.success_analyzer.analyze_successes(sprint_data, metrics)

        # Step 4: Analyze what didn't go well
        what_didnt_go_well = self.failure_analyzer.analyze_failures(sprint_data, metrics)

        # Step 5: Generate action items
        action_items = self.action_item_generator.generate_action_items(
            what_went_well,
            what_didnt_go_well,
            metrics
        )

        # Step 6: Extract key learnings
        key_learnings = self.learning_extractor.extract_learnings(
            sprint_data,
            what_went_well,
            what_didnt_go_well,
            historical_data
        )

        # Step 7: Analyze velocity trend
        velocity_trend = self.health_assessor.analyze_velocity_trend(metrics, historical_data)

        # Step 8: Assess overall sprint health
        overall_health = self.health_assessor.assess_sprint_health(metrics)

        # Step 9: Build retrospective context (Parameter Object pattern)
        retro_context = RetrospectiveContext(
            metrics=metrics,
            action_items=action_items,
            velocity_trend=velocity_trend,
            overall_health=overall_health,
            what_went_well=what_went_well,
            what_didnt_go_well=what_didnt_go_well
        )

        # Step 10: Generate recommendations using Parameter Object
        recommendations = self.recommendation_generator.generate_recommendations(retro_context)

        # Create retrospective report
        report = RetrospectiveReport(
            sprint_number=sprint_number,
            sprint_start_date=sprint_data.get('start_date', 'Unknown'),
            sprint_end_date=sprint_data.get('end_date', 'Unknown'),
            metrics=metrics,
            what_went_well=what_went_well,
            what_didnt_go_well=what_didnt_go_well,
            action_items=action_items,
            key_learnings=key_learnings,
            velocity_trend=velocity_trend,
            overall_health=overall_health,
            recommendations=recommendations
        )

        # Store retrospective in RAG for learning
        self.storage.store_retrospective(card_id, report)

        # Communicate to orchestrator
        self.storage.communicate_retrospective(card_id, report)

        self.logger.log(f"✅ Retrospective complete: {overall_health} health", "SUCCESS")
        self.debug_if_enabled("retrospective_summary", "Retrospective completed",
                             sprint=sprint_number, health=overall_health,
                             action_items=len(action_items))

        return report

    def _retrieve_historical_sprints(self, card_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve historical sprint data from RAG

        Args:
            card_id: Card ID for filtering

        Returns:
            List of historical sprint data

        WHY: Compare current sprint to historical trends
        RESPONSIBILITY: Query RAG for past sprints
        PATTERNS: Guard clause for error handling
        """
        try:
            # Query RAG for past sprint retrospectives
            results = self.rag.query(
                query=f"Sprint retrospectives for {card_id}",
                limit=self.historical_sprints_to_analyze
            )
            return results
        except Exception as e:
            self.logger.log(f"Could not retrieve historical sprints: {e}", "WARNING")
            return []
