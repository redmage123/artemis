#!/usr/bin/env python3
"""
Module: sprint_planning_stage_core.py

WHY: Orchestrate sprint planning workflow with extracted components
RESPONSIBILITY: Coordinate feature extraction, estimation, prioritization, and allocation
PATTERNS: Facade pattern, Dependency Injection, Strategy pattern
"""

from typing import Dict, List, Optional, Any
from artemis_stage_interface import PipelineStage, LoggerInterface
from supervised_agent_mixin import SupervisedStageMixin
from debug_mixin import DebugMixin
from llm_client import LLMClient
from pipeline_observer import PipelineObservable
from sprint_models import Clock, SystemClock
from artemis_exceptions import (
    SprintPlanningError,
    PipelineStageError,
    wrap_exception
)
from stage_notifications import StageNotificationHelper
from planning_poker import FeatureEstimate

# Import extracted components
from stages.sprint_planning.feature_extractor import FeatureExtractor
from stages.sprint_planning.poker_integration import PokerIntegration
from stages.sprint_planning.feature_prioritizer import FeaturePrioritizer
from stages.sprint_planning.sprint_creator import SprintCreator
from stages.sprint_planning.kanban_updater import KanbanUpdater
from stages.sprint_planning.rag_storage import SprintPlanRAGStorage
from stages.sprint_planning.agent_notifier import AgentNotifier


class SprintPlanningStage(PipelineStage, SupervisedStageMixin, DebugMixin):
    """
    WHY: Transform product requirements into estimated, prioritized sprint backlogs
    RESPONSIBILITY: Orchestrate sprint planning workflow using modular components
    PATTERNS: Facade pattern coordinates extracted modules, Strategy for allocation

    Pipeline Position: BEFORE Architecture stage
    Input: Product requirements and feature backlog
    Output: Prioritized sprint backlogs with story point estimates
    """

    def __init__(
        self,
        board,
        messenger,
        rag,
        logger: LoggerInterface,
        llm_client: LLMClient,
        config=None,
        observable: Optional[PipelineObservable] = None,
        supervisor=None,
        clock: Optional[Clock] = None,
        ai_service: Optional[Any] = None
    ):
        """
        WHY: Dependency injection enables testing and runtime configuration
        RESPONSIBILITY: Initialize all components with configured dependencies
        """
        PipelineStage.__init__(self)
        SupervisedStageMixin.__init__(
            self,
            supervisor=supervisor,
            stage_name="SprintPlanningStage",
            heartbeat_interval=20
        )
        DebugMixin.__init__(self, component_name="sprint_planning")

        self.board = board
        self.messenger = messenger
        self.rag = rag
        self.logger = logger
        self.llm_client = llm_client
        self.config = config
        self.ai_service = ai_service
        self.observable = observable
        self.clock = clock or SystemClock()

        # Load configuration
        self._load_config()

        # Initialize notification helper
        self.notifier = StageNotificationHelper(observable, "sprint_planning")

        # Initialize modular components
        self._initialize_components()

    def _load_config(self):
        """
        WHY: Centralize configuration loading with sensible defaults
        RESPONSIBILITY: Extract config values or use defaults
        PATTERNS: Guard clause for missing config
        """
        if not self.config:
            # Sensible defaults
            self.team_velocity = 20.0
            self.sprint_duration_days = 14
            self.planning_poker_agents = ['conservative', 'moderate', 'aggressive']
            self.priority_weight = 0.4
            self.value_weight = 0.3
            self.risk_weight = 0.3
            return

        # Load from ConfigurationAgent
        self.team_velocity = self.config.get('ARTEMIS_SPRINT_TEAM_VELOCITY', 20.0)
        self.sprint_duration_days = self.config.get('ARTEMIS_SPRINT_DURATION_DAYS', 14)
        self.planning_poker_agents = self.config.get(
            'ARTEMIS_PLANNING_POKER_AGENTS',
            ['conservative', 'moderate', 'aggressive']
        )
        self.priority_weight = self.config.get('ARTEMIS_SPRINT_PRIORITY_WEIGHT', 0.4)
        self.value_weight = self.config.get('ARTEMIS_SPRINT_VALUE_WEIGHT', 0.3)
        self.risk_weight = self.config.get('ARTEMIS_SPRINT_RISK_WEIGHT', 0.3)

    def _initialize_components(self):
        """
        WHY: Separate initialization from constructor for clarity
        RESPONSIBILITY: Create all modular component instances
        """
        self.feature_extractor = FeatureExtractor(
            self.llm_client,
            self.logger
        )

        self.poker_integration = PokerIntegration(
            self.llm_client,
            self.logger,
            self.planning_poker_agents,
            self.team_velocity,
            self.observable,
            self.ai_service
        )

        self.feature_prioritizer = FeaturePrioritizer(
            self.priority_weight,
            self.value_weight,
            self.risk_weight
        )

        self.sprint_creator = SprintCreator(
            self.team_velocity,
            self.sprint_duration_days,
            self.clock
        )

        self.kanban_updater = KanbanUpdater(
            self.board,
            self.logger,
            self.clock
        )

        self.rag_storage = SprintPlanRAGStorage(
            self.rag,
            self.logger
        )

        self.agent_notifier = AgentNotifier(
            self.messenger,
            self.logger
        )

    @wrap_exception(PipelineStageError, "Sprint planning stage execution failed")
    def execute(self, card: Dict, context: Dict) -> Dict:
        """
        WHY: Main entry point for sprint planning workflow
        RESPONSIBILITY: Coordinate all components and handle supervision
        PATTERNS: Guard clauses, context manager for supervision

        Args:
            card: Kanban card with feature backlog
            context: Shared pipeline context

        Returns:
            Dict with sprint assignments and estimates

        Raises:
            SprintPlanningError: If sprint planning fails
        """
        metadata = {
            "task_id": card.get('card_id'),
            "stage": "sprint_planning"
        }

        try:
            with self.supervised_execution(metadata):
                return self._do_sprint_planning(card, context)
        except SprintPlanningError:
            raise
        except Exception as e:
            raise wrap_exception(
                e,
                SprintPlanningError,
                "Unexpected error during sprint planning",
                {"card_id": card.get('card_id'), "stage": "sprint_planning"}
            )

    def _do_sprint_planning(self, card: Dict, context: Dict) -> Dict:
        """
        WHY: Internal workflow orchestration separate from execute
        RESPONSIBILITY: Execute sprint planning steps in order
        PATTERNS: Pipeline pattern with progress tracking
        """
        card_id = card.get('card_id')
        task_title = card.get('title', 'Unknown Task')

        self.logger.log(f"🏃 Sprint Planning: {task_title}", "INFO")
        self.update_progress({"step": "starting", "progress_percent": 5})

        self.debug_log("Starting sprint planning", card_id=card_id, task_title=task_title)

        with self.notifier.stage_lifecycle(card_id, {'task_title': task_title}):
            # Step 1: Extract features
            features = self._execute_feature_extraction(card, context, card_id)
            if not features:
                return self._build_skip_response()

            # Step 2: Run Planning Poker
            estimates = self._execute_planning_poker(features, card_id)

            # Step 3: Prioritize features
            prioritized_features = self._execute_prioritization(
                features,
                estimates,
                card_id
            )

            # Step 4: Create sprints
            sprints = self._execute_sprint_creation(prioritized_features, card_id)

            # Step 5: Update Kanban board
            self._execute_kanban_update(card_id, sprints)

            # Step 6: Store in RAG
            self._execute_rag_storage(card_id, task_title, sprints, estimates)

            # Step 7: Notify agents
            self._execute_agent_notification(card_id, task_title, sprints)

            self.update_progress({"step": "complete", "progress_percent": 100})
            self.logger.log(f"✅ Created {len(sprints)} sprints", "SUCCESS")

            return self._build_success_response(features, sprints, estimates)

    def _execute_feature_extraction(
        self,
        card: Dict,
        context: Dict,
        card_id: str
    ) -> List:
        """
        WHY: Isolated feature extraction step with progress tracking
        RESPONSIBILITY: Extract features and notify progress
        """
        self.update_progress({"step": "extracting_features", "progress_percent": 15})

        with self.debug_section("Feature Extraction"):
            features = self.feature_extractor.extract_features(card, context)
            self.logger.log(
                f"Extracted {len(features)} features from backlog",
                "INFO"
            )
            self.debug_dump_if_enabled(
                'dump_features',
                "Extracted Features",
                [f.to_dict() for f in features]
            )

        self.notifier.notify_progress(
            card_id,
            step='features_extracted',
            progress_percent=15,
            features_count=len(features)
        )

        return features

    def _execute_planning_poker(self, features: List, card_id: str) -> List[FeatureEstimate]:
        """
        WHY: Isolated Planning Poker step with progress tracking
        RESPONSIBILITY: Run estimation and notify progress
        """
        self.update_progress({"step": "planning_poker", "progress_percent": 30})

        with self.debug_section("Planning Poker Estimation", feature_count=len(features)):
            estimates = self.poker_integration.estimate_features(features)
            self.debug_if_enabled(
                'show_estimates',
                "Estimates completed",
                estimate_count=len(estimates)
            )
            self.debug_dump_if_enabled(
                'show_estimates',
                "Feature Estimates",
                [
                    {
                        "title": e.feature_title,
                        "story_points": e.final_estimate,
                        "confidence": e.confidence,
                        "risk": e.risk_level
                    }
                    for e in estimates
                ]
            )

        return estimates

    def _execute_prioritization(
        self,
        features: List,
        estimates: List[FeatureEstimate],
        card_id: str
    ) -> List:
        """
        WHY: Isolated prioritization step with progress tracking
        RESPONSIBILITY: Prioritize features and notify progress
        """
        self.update_progress({"step": "prioritizing", "progress_percent": 60})

        with self.debug_section("Feature Prioritization"):
            prioritized_features = self.feature_prioritizer.prioritize(
                features,
                estimates
            )
            self.debug_if_enabled(
                'show_estimates',
                "Prioritization completed",
                top_priority=(
                    prioritized_features[0].feature.title
                    if prioritized_features
                    else "None"
                )
            )

        return prioritized_features

    def _execute_sprint_creation(self, prioritized_features: List, card_id: str) -> List:
        """
        WHY: Isolated sprint creation step with progress tracking
        RESPONSIBILITY: Create sprints and notify progress
        """
        self.update_progress({"step": "creating_sprints", "progress_percent": 75})

        with self.debug_section("Sprint Allocation"):
            sprints = self.sprint_creator.create_sprints(prioritized_features)
            self.debug_log(
                "Created sprints",
                sprint_count=len(sprints),
                total_story_points=sum(s.total_story_points for s in sprints)
            )

        return sprints

    def _execute_kanban_update(self, card_id: str, sprints: List) -> None:
        """
        WHY: Isolated Kanban update step with progress tracking
        RESPONSIBILITY: Update board and notify progress
        """
        self.update_progress({"step": "updating_kanban", "progress_percent": 85})
        self.kanban_updater.update_board(card_id, sprints)

    def _execute_rag_storage(
        self,
        card_id: str,
        task_title: str,
        sprints: List,
        estimates: List[FeatureEstimate]
    ) -> None:
        """
        WHY: Isolated RAG storage step with progress tracking
        RESPONSIBILITY: Store plan and notify progress
        """
        self.update_progress({"step": "storing_in_rag", "progress_percent": 95})
        self.rag_storage.store_sprint_plan(card_id, task_title, sprints, estimates)

    def _execute_agent_notification(
        self,
        card_id: str,
        task_title: str,
        sprints: List
    ) -> None:
        """
        WHY: Isolated agent notification step
        RESPONSIBILITY: Notify other agents of completion
        """
        self.agent_notifier.notify_sprint_plan_complete(card_id, task_title, sprints)

    def _build_skip_response(self) -> Dict:
        """
        WHY: Consistent response format for skip case
        RESPONSIBILITY: Build skip response dictionary
        """
        self.logger.log("No features found in backlog", "WARNING")
        return {
            "stage": "sprint_planning",
            "status": "SKIP",
            "message": "No features to plan"
        }

    def _build_success_response(
        self,
        features: List,
        sprints: List,
        estimates: List[FeatureEstimate]
    ) -> Dict:
        """
        WHY: Consistent response format for success case
        RESPONSIBILITY: Build success response dictionary
        """
        total_story_points = sum(s.total_story_points for s in sprints)
        estimates_dict = [self._estimate_to_dict(e) for e in estimates]

        return {
            "stage": "sprint_planning",
            "status": "PASS",
            "total_features": len(features),
            "total_sprints": len(sprints),
            "total_story_points": total_story_points,
            "features": estimates_dict,
            "sprints": [s.to_dict() for s in sprints],
            "estimates": estimates_dict
        }

    def _estimate_to_dict(self, estimate: FeatureEstimate) -> Dict:
        """
        WHY: Convert FeatureEstimate to dict for JSON serialization
        RESPONSIBILITY: Build estimate dictionary with compatibility fields
        """
        return {
            'feature_title': estimate.feature_title,
            'title': estimate.feature_title,
            'final_estimate': estimate.final_estimate,
            'story_points': estimate.final_estimate,
            'confidence': estimate.confidence,
            'risk_level': estimate.risk_level,
            'estimated_hours': estimate.estimated_hours
        }

    def get_stage_name(self) -> str:
        """
        WHY: Pipeline interface requirement
        RESPONSIBILITY: Return stage identifier
        """
        return "sprint_planning"
