#!/usr/bin/env python3
"""
Project Review Stage - Architecture & Sprint Plan Validation

WHY: Quality gate for project planning phases
RESPONSIBILITY: Orchestrate review process using specialized components
PATTERNS: Single Responsibility, Dependency Injection, Composition over Inheritance

Responsibilities:
1. Review architecture design decisions
2. Validate sprint planning and capacity
3. Check for technical debt and anti-patterns
4. Provide actionable feedback to Architecture and Sprint Planning stages
5. Approve or reject project plans with detailed reasoning

Pipeline Position: AFTER Sprint Planning and Architecture, BEFORE Development
Input: Architecture design + Sprint plans
Output: Approval/Rejection with feedback
"""

from typing import Dict, List, Optional, Any
from artemis_stage_interface import PipelineStage, LoggerInterface
from supervised_agent_mixin import SupervisedStageMixin
from llm_client import LLMClient
from pipeline_observer import PipelineObservable, PipelineEvent, EventType
from rag_storage_helper import RAGStorageHelper

# Import modular components
from stages.project_review.architecture_reviewer import ArchitectureReviewer
from stages.project_review.sprint_validator import SprintValidator
from stages.project_review.quality_analyzer import QualityAnalyzer
from stages.project_review.review_scorer import ReviewScorer
from stages.project_review.approval_handler import ApprovalHandler
from stages.project_review.feedback_compiler import FeedbackCompiler


class ProjectReviewStage(PipelineStage, SupervisedStageMixin):
    """
    Project Review Stage - Validate architecture and sprint plans

    WHY: Quality gate preventing problematic designs from reaching development
    RESPONSIBILITY: Coordinate review components and manage review lifecycle
    PATTERNS: Facade, Composition, Dependency Injection
    """

    def __init__(
        self,
        board,
        messenger,
        rag,
        logger: LoggerInterface,
        llm_client: LLMClient,
        config=None,
        observable=None,
        supervisor=None,
        max_review_iterations: int = 3
    ):
        """
        Initialize Project Review Stage

        Args:
            board: KanbanBoard instance
            messenger: AgentMessenger for feedback communication
            rag: RAG agent for learning from reviews
            logger: Logger interface
            llm_client: LLM client for review analysis
            config: ConfigurationAgent for review criteria weights
            observable: Observable for event broadcasting
            supervisor: SupervisorAgent for health monitoring
            max_review_iterations: Max times architecture can be revised
        """
        PipelineStage.__init__(self)
        SupervisedStageMixin.__init__(
            self,
            supervisor=supervisor,
            stage_name="ProjectReviewStage",
            heartbeat_interval=20
        )

        self.board = board
        self.messenger = messenger
        self.rag = rag
        self.logger = logger
        self.llm_client = llm_client
        self.config = config
        self.observable = observable

        # Load configuration
        self.max_review_iterations = self._get_max_iterations(config, max_review_iterations)
        review_weights = self._load_review_weights(config)
        capacity_thresholds = self._load_capacity_thresholds(config)
        tech_debt_penalty = self._load_tech_debt_penalty(config)

        # Initialize specialized components using dependency injection
        self.architecture_reviewer = ArchitectureReviewer(llm_client, logger)
        self.sprint_validator = SprintValidator(
            logger,
            capacity_thresholds['high'],
            capacity_thresholds['low']
        )
        self.quality_analyzer = QualityAnalyzer(logger, tech_debt_penalty)
        self.review_scorer = ReviewScorer(review_weights, logger)
        self.approval_handler = ApprovalHandler(
            board,
            messenger,
            logger,
            observable,
            self.max_review_iterations
        )
        self.feedback_compiler = FeedbackCompiler(logger)

    def execute(self, card: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute Project Review with supervisor monitoring

        WHY: Supervised execution with progress tracking

        Args:
            card: Kanban card with project plan
            context: Shared pipeline context with architecture and sprints

        Returns:
            Dict with review decision and feedback
        """
        metadata = {
            "task_id": card.get('card_id'),
            "stage": "project_review"
        }

        with self.supervised_execution(metadata):
            result = self._do_project_review(card, context)

        return result

    def get_stage_name(self) -> str:
        """Get the name of this pipeline stage"""
        return "project_review"

    def _do_project_review(self, card: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal project review logic

        WHY: Separate execution wrapper from core logic
        """
        card_id = card.get('card_id')
        task_title = card.get('title', 'Unknown Task')

        self.logger.log(f"Project Review: {task_title}", "INFO")
        self.update_progress({"step": "starting", "progress_percent": 5})

        self._notify_review_started(card_id, task_title)

        # Check iteration limit using guard clause
        iteration_count = context.get('review_iteration_count', 0)
        if iteration_count >= self.max_review_iterations:
            return self.approval_handler.force_approval(card_id, task_title, context)

        # Extract plans
        self.update_progress({"step": "extracting_plans", "progress_percent": 15})
        architecture = context.get('architecture', {})
        sprints = context.get('sprints', [])

        # Perform reviews
        arch_review = self._perform_architecture_review(architecture, task_title)
        sprint_review = self._perform_sprint_review(sprints, architecture)
        quality_review = self._perform_quality_review(architecture, context)

        # Calculate score and decision
        self.update_progress({"step": "calculating_score", "progress_percent": 80})
        overall_score, decision = self.review_scorer.calculate_review_score(
            arch_review,
            sprint_review,
            quality_review
        )

        # Handle decision
        result = self._handle_decision(
            decision,
            card_id,
            task_title,
            overall_score,
            arch_review,
            sprint_review,
            quality_review,
            context,
            iteration_count
        )

        # Store review
        self.update_progress({"step": "storing_review", "progress_percent": 95})
        self._store_review(card_id, task_title, result)

        self.update_progress({"step": "complete", "progress_percent": 100})
        self.logger.log(
            f"Review complete: {decision}",
            "SUCCESS" if decision == "APPROVED" else "WARNING"
        )

        return result

    def _perform_architecture_review(
        self,
        architecture: Dict[str, Any],
        task_title: str
    ) -> Dict[str, Any]:
        """Perform architecture review using ArchitectureReviewer"""
        if not architecture:
            self.logger.log(
                "No architecture found - skipping architecture review",
                "WARNING"
            )
            self.update_progress({"step": "skipping_architecture", "progress_percent": 30})
            return self.architecture_reviewer.review_architecture({}, task_title)

        self.update_progress({"step": "reviewing_architecture", "progress_percent": 30})
        return self.architecture_reviewer.review_architecture(architecture, task_title)

    def _perform_sprint_review(
        self,
        sprints: List[Dict[str, Any]],
        architecture: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform sprint review using SprintValidator"""
        self.update_progress({"step": "reviewing_sprints", "progress_percent": 50})
        return self.sprint_validator.review_sprints(sprints, architecture)

    def _perform_quality_review(
        self,
        architecture: Optional[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform quality analysis using QualityAnalyzer"""
        self.update_progress({"step": "checking_quality", "progress_percent": 65})
        return self.quality_analyzer.check_quality_issues(architecture, context)

    def _handle_decision(
        self,
        decision: str,
        card_id: str,
        task_title: str,
        overall_score: float,
        arch_review: Dict[str, Any],
        sprint_review: Dict[str, Any],
        quality_review: Dict[str, Any],
        context: Dict[str, Any],
        iteration_count: int
    ) -> Dict[str, Any]:
        """
        Handle approval or rejection decision

        WHY: Route to appropriate handler based on decision
        """
        self.update_progress({"step": "processing_decision", "progress_percent": 90})

        if decision == "APPROVED":
            return self.approval_handler.handle_approval(
                card_id,
                task_title,
                overall_score,
                context
            )

        # Compile feedback for rejection
        feedback = self.feedback_compiler.compile_feedback(
            arch_review,
            sprint_review,
            quality_review
        )

        return self.approval_handler.handle_rejection(
            card_id,
            task_title,
            overall_score,
            feedback,
            context,
            iteration_count
        )

    def _notify_review_started(self, card_id: str, task_title: str) -> None:
        """Notify observers that review has started"""
        if not self.observable:
            return

        event = PipelineEvent(
            event_type=EventType.STAGE_STARTED,
            card_id=card_id,
            stage_name="project_review",
            data={"task_title": task_title}
        )
        self.observable.notify(event)

    def _store_review(
        self,
        card_id: str,
        task_title: str,
        result: Dict[str, Any]
    ) -> None:
        """
        Store review in RAG for learning

        WHY: Build knowledge base of review decisions
        """
        content = f"""Project Review: {task_title}

Status: {result.get('status')}
Score: {result.get('score', 0):.1f}/10

"""
        if result.get('feedback'):
            import json
            content += f"\nFeedback provided for revision:\n{json.dumps(result['feedback'], indent=2)}"

        RAGStorageHelper.store_stage_artifact(
            rag=self.rag,
            stage_name="project_review",
            card_id=card_id,
            task_title=task_title,
            content=content,
            metadata=result
        )

    def _get_max_iterations(self, config: Any, default: int) -> int:
        """Load max iterations from config"""
        if not config:
            return default
        return config.get('project_review.max_iterations', default)

    def _load_review_weights(self, config: Any) -> Dict[str, float]:
        """Load review weights from config"""
        if not config:
            return {
                'architecture_quality': 0.30,
                'sprint_feasibility': 0.25,
                'technical_debt': 0.20,
                'scalability': 0.15,
                'maintainability': 0.10
            }

        return {
            'architecture_quality': config.get('project_review.weights.architecture_quality', 0.30),
            'sprint_feasibility': config.get('project_review.weights.sprint_feasibility', 0.25),
            'technical_debt': config.get('project_review.weights.technical_debt', 0.20),
            'scalability': config.get('project_review.weights.scalability', 0.15),
            'maintainability': config.get('project_review.weights.maintainability', 0.10)
        }

    def _load_capacity_thresholds(self, config: Any) -> Dict[str, float]:
        """Load capacity thresholds from config"""
        if not config:
            return {'high': 0.95, 'low': 0.70}

        return {
            'high': config.get('project_review.capacity_high_threshold', 0.95),
            'low': config.get('project_review.capacity_low_threshold', 0.70)
        }

    def _load_tech_debt_penalty(self, config: Any) -> float:
        """Load tech debt penalty from config"""
        if not config:
            return 0.5
        return config.get('project_review.tech_debt_penalty', 0.5)
