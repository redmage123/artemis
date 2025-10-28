#!/usr/bin/env python3
"""
WHY: Core UI/UX Stage implementation
RESPONSIBILITY: Orchestrate UI/UX and accessibility evaluation
PATTERNS: Facade pattern, Dependency injection, Observer pattern

This is the main UI/UX stage that coordinates all evaluation components.
"""

import tempfile
from typing import Dict, Optional, List, Any

from artemis_stage_interface import PipelineStage, LoggerInterface
from agent_messenger import AgentMessenger
from rag_agent import RAGAgent
from kanban_manager import KanbanBoard
from pipeline_observer import PipelineObservable
from supervised_agent_mixin import SupervisedStageMixin
from debug_mixin import DebugMixin
from stage_notifications import StageNotificationHelper
from artemis_exceptions import UIUXEvaluationError, wrap_exception

from .models import DeveloperEvaluation
from .score_calculator import ScoreCalculator
from .accessibility_evaluator import AccessibilityEvaluator
from .gdpr_evaluator import GDPRComplianceEvaluator
from .feedback_manager import FeedbackManager
from .kg_storage import EvaluationStorage

# Import AIQueryService for KG-First accessibility pattern retrieval
try:
    from ai_query_service import create_ai_query_service
    AI_QUERY_SERVICE_AVAILABLE = True
except ImportError:
    AI_QUERY_SERVICE_AVAILABLE = False


class UIUXStage(PipelineStage, SupervisedStageMixin, DebugMixin):
    """
    WHY: Evaluate UI/UX and accessibility compliance
    RESPONSIBILITY: Orchestrate WCAG, GDPR, and UX evaluation
    PATTERNS: Facade pattern, Composition over inheritance

    This stage evaluates user experience, accessibility, and design quality.

    Integrates with supervisor for:
    - UI/UX evaluation tracking
    - Accessibility compliance monitoring
    - Automatic heartbeat and health monitoring

    IMPROVEMENTS:
    - Configuration from Hydra (no magic numbers)
    - Specific exceptions (no bare Exception)
    - StageNotificationHelper (DRY observer pattern)
    - Value Objects (DeveloperEvaluation)
    - List comprehensions (Pythonic)
    - Removed speculative generality (NOT_EVALUATED fields)
    - Modularized into specialized components
    """

    def __init__(
        self,
        board: KanbanBoard,
        messenger: AgentMessenger,
        rag: RAGAgent,
        logger: LoggerInterface,
        observable: Optional[PipelineObservable] = None,
        supervisor: Optional['SupervisorAgent'] = None,
        config: Optional[Any] = None,
        ai_service: Optional['AIQueryService'] = None
    ):
        """
        WHY: Initialize UI/UX Stage with all dependencies
        RESPONSIBILITY: Set up stage and all sub-components

        Args:
            board: Kanban board for status updates
            messenger: Agent messenger for inter-agent communication
            rag: RAG agent for storing evaluation results
            logger: Logger interface
            observable: Optional PipelineObservable for event broadcasting
            supervisor: Optional SupervisorAgent for monitoring
            config: Optional ConfigurationAgent for settings
            ai_service: AI Query Service for KG-First pattern retrieval (optional)
        """
        # Initialize PipelineStage
        PipelineStage.__init__(self)

        # Initialize SupervisedStageMixin for health monitoring
        # UI/UX evaluation can be time-consuming, use 25 second heartbeat
        SupervisedStageMixin.__init__(
            self,
            supervisor=supervisor,
            stage_name="UIUXStage",
            heartbeat_interval=25  # Longer interval for evaluation-heavy stage
        )

        # Initialize DebugMixin
        DebugMixin.__init__(self, component_name="uiux")

        self.board = board
        self.messenger = messenger
        self.rag = rag
        self.logger = logger
        self.observable = observable
        self.config = config

        # Initialize notification helper (DRY - reduces 30 lines to 3)
        self.notifier = StageNotificationHelper(observable, "uiux")

        # Initialize sub-components
        self._initialize_components(config, ai_service)

    def _initialize_components(self, config: Optional[Any], ai_service: Optional[Any]):
        """
        WHY: Initialize all sub-components
        RESPONSIBILITY: Create specialized evaluators and managers
        PATTERNS: Dependency injection

        Args:
            config: Optional configuration agent
            ai_service: Optional AI Query Service
        """
        # Initialize AI Query Service for KG-First accessibility pattern retrieval
        self.ai_service = None
        if AI_QUERY_SERVICE_AVAILABLE:
            try:
                if ai_service:
                    self.ai_service = ai_service
                    self.logger.log(
                        "✅ Using provided AI Query Service for pattern retrieval",
                        "INFO"
                    )
                else:
                    self.ai_service = create_ai_query_service(
                        llm_client=None,  # UI/UX stage doesn't need LLM
                        rag=self.rag,
                        logger=self.logger,
                        verbose=False
                    )
                    self.logger.log(
                        "✅ AI Query Service initialized for accessibility patterns",
                        "INFO"
                    )
            except Exception as e:
                self.logger.log(
                    f"⚠️  Could not initialize AI Query Service: {e}",
                    "WARNING"
                )
                self.ai_service = None

        # Initialize specialized components
        self.score_calculator = ScoreCalculator(config)
        self.accessibility_evaluator = AccessibilityEvaluator(self.logger, self.ai_service)
        self.gdpr_evaluator = GDPRComplianceEvaluator(self.logger)
        self.feedback_manager = FeedbackManager(self.messenger, self.logger)
        self.evaluation_storage = EvaluationStorage(self.rag, self.logger)

    def execute(self, card: Dict, context: Dict) -> Dict:
        """
        WHY: Execute UI/UX evaluation with supervisor monitoring
        RESPONSIBILITY: Run evaluation pipeline
        PATTERNS: Template method pattern

        Raises:
            UIUXEvaluationError: On evaluation failures
        """
        metadata = {
            "task_id": card.get('card_id'),
            "stage": "uiux"
        }

        try:
            with self.supervised_execution(metadata):
                return self._evaluate_uiux(card, context)
        except UIUXEvaluationError:
            raise  # Re-raise specific errors
        except Exception as e:
            # Wrap unexpected errors in specific exception
            raise wrap_exception(
                e,
                UIUXEvaluationError,
                "Unexpected error during UI/UX evaluation",
                {"card_id": card.get('card_id')}
            )

    def _evaluate_uiux(self, card: Dict, context: Dict) -> Dict:
        """
        WHY: Internal method - performs UI/UX and accessibility evaluation
        RESPONSIBILITY: Coordinate evaluation of all developers
        PATTERNS: Template method pattern

        Evaluates each developer's implementation for:
        - WCAG 2.1 AA accessibility standards
        - GDPR compliance (data privacy, consent, user rights)
        - User experience metrics

        Args:
            card: Kanban card with task details
            context: Context from previous stages (includes developers)

        Returns:
            Dict with evaluation results for all developers
        """
        card_id = card['card_id']
        task_title = card.get('title', 'Unknown Task')

        # Context manager handles STAGE_STARTED/COMPLETED/FAILED automatically
        with self.notifier.stage_lifecycle(card_id, {'task_title': task_title}):
            self.logger.log("Starting UI/UX Evaluation Stage", "STAGE")
            self.logger.log("🎨 Comprehensive UI/UX and Accessibility Analysis", "INFO")

            # Update progress: starting
            self.update_progress({"step": "starting", "progress_percent": 5})

            # Get developer results from context
            developers = context.get('developers', [])

            # Guard clause: no developers to evaluate
            if not developers:
                self.logger.log("No developer implementations found to evaluate", "WARNING")
                return {
                    "stage": "uiux",
                    "status": "SKIPPED",
                    "reason": "No implementations to evaluate"
                }

            self.logger.log(f"Evaluating {len(developers)} developer implementation(s)", "INFO")

            # Update progress: initializing evaluations
            self.update_progress({"step": "initializing_evaluations", "progress_percent": 10})

            # Evaluate each developer's implementation
            evaluation_results = self._evaluate_all_developers(
                developers, card_id, task_title
            )

            # Calculate summary metrics (using list comprehensions - Pythonic!)
            total_accessibility_issues = sum(
                eval_result.accessibility_issues
                for eval_result in evaluation_results
            )
            total_ux_issues = sum(
                eval_result.ux_issues
                for eval_result in evaluation_results
            )
            all_evaluations_pass = all(
                eval_result.evaluation_status == "PASS"
                for eval_result in evaluation_results
            )

            # Update progress: summarizing results
            self.update_progress({"step": "summarizing_results", "progress_percent": 85})

            # Log summary
            self._log_evaluation_summary(
                len(evaluation_results),
                total_accessibility_issues,
                total_ux_issues
            )

            # Update progress: determining status
            self.update_progress({"step": "determining_status", "progress_percent": 95})

            # Determine overall stage status
            stage_status = self._determine_stage_status(
                total_accessibility_issues,
                all_evaluations_pass
            )

            # Update Kanban
            self.board.update_card(card_id, {
                "uiux_status": stage_status,
                "accessibility_issues": total_accessibility_issues,
                "ux_issues": total_ux_issues
            })

            # Update progress: complete
            self.update_progress({"step": "complete", "progress_percent": 100})

            return {
                "stage": "uiux",
                "status": stage_status,
                "evaluations": [e.to_dict() for e in evaluation_results],
                "total_accessibility_issues": total_accessibility_issues,
                "total_ux_issues": total_ux_issues,
                "all_evaluations_pass": all_evaluations_pass,
                "implementations_evaluated": len(evaluation_results)
            }

    def _evaluate_all_developers(
        self,
        developers: List[Dict],
        card_id: str,
        task_title: str
    ) -> List[DeveloperEvaluation]:
        """
        WHY: Evaluate all developers' implementations
        RESPONSIBILITY: Iterate through developers and evaluate each
        PATTERNS: Collection processing

        Returns list of DeveloperEvaluation value objects

        Args:
            developers: List of developer results
            card_id: Task card ID
            task_title: Task title

        Returns:
            List of DeveloperEvaluation objects
        """
        evaluation_results = []

        for i, dev_result in enumerate(developers):
            developer_name = dev_result.get('developer', 'unknown')
            implementation_dir = dev_result.get(
                'output_dir',
                f'{tempfile.gettempdir()}/{developer_name}/'
            )

            # Update progress for each developer evaluation (10% to 80% dynamically)
            progress = 10 + ((i + 1) / len(developers)) * 70
            self.update_progress({
                "step": f"evaluating_{developer_name}",
                "progress_percent": int(progress),
                "current_developer": developer_name,
                "total_developers": len(developers)
            })

            self.logger.log(f"\n{'='*60}", "INFO")
            self.logger.log(f"🎨 Evaluating {developer_name} implementation", "INFO")
            self.logger.log(f"{'='*60}", "INFO")

            # Perform evaluation
            evaluation_result = self._evaluate_developer_uiux(
                developer_name=developer_name,
                implementation_dir=implementation_dir,
                task_title=task_title
            )

            evaluation_results.append(evaluation_result)

            # Log evaluation summary
            self._log_developer_evaluation(evaluation_result, developer_name)

            # Store evaluation in RAG and KG for learning
            self.evaluation_storage.store_evaluation_in_rag(
                card_id, task_title, evaluation_result
            )
            self.evaluation_storage.store_evaluation_in_knowledge_graph(
                card_id, developer_name, evaluation_result, implementation_dir
            )

            # Send evaluation notification to other agents
            self.feedback_manager.send_evaluation_notification(card_id, evaluation_result)

            # Send feedback to developer for iteration if issues found
            if evaluation_result.ux_issues > 0:
                self.feedback_manager.send_feedback_to_developer(card_id, evaluation_result)

            # Notify evaluation progress for this developer
            self.notifier.notify_progress(
                card_id,
                step=f'evaluated_{developer_name}',
                progress_percent=int(progress),
                developer=developer_name,
                evaluation_status=evaluation_result.evaluation_status,
                ux_score=evaluation_result.ux_score,
                accessibility_issues=evaluation_result.accessibility_issues
            )

        return evaluation_results

    def _evaluate_developer_uiux(
        self,
        developer_name: str,
        implementation_dir: str,
        task_title: str
    ) -> DeveloperEvaluation:
        """
        WHY: Evaluate a single developer's implementation for UI/UX
        RESPONSIBILITY: Coordinate WCAG and GDPR evaluation
        PATTERNS: Composition pattern

        Uses real WCAG and GDPR evaluators to perform compliance checks.
        Queries KG for accessibility patterns to improve evaluation context.

        Args:
            developer_name: Name of the developer
            implementation_dir: Directory containing implementation
            task_title: Title of the task

        Returns:
            DeveloperEvaluation value object
        """
        self.logger.log(f"Evaluating UI/UX for {developer_name}...", "INFO")

        # Query for accessibility patterns (KG-First approach)
        patterns = self.accessibility_evaluator.query_accessibility_patterns(task_title)
        if patterns:
            self.logger.log(
                f"📚 Found {patterns['pattern_count']} accessibility pattern(s) in KG",
                "INFO"
            )

        # Run WCAG 2.1 AA accessibility evaluation
        wcag_results = self.accessibility_evaluator.evaluate_accessibility(
            developer_name, implementation_dir
        )

        # Run GDPR compliance evaluation
        gdpr_results = self.gdpr_evaluator.evaluate_gdpr_compliance(
            developer_name, implementation_dir
        )

        # Calculate overall scores
        accessibility_issues = wcag_results.get('accessibility_issues', 0)
        gdpr_issues = gdpr_results.get('gdpr_issues', 0)
        total_issues = accessibility_issues + gdpr_issues

        # Determine evaluation status
        evaluation_status = self.score_calculator.determine_evaluation_status(
            wcag_results, gdpr_results, total_issues
        )

        # Calculate UX score (0-100)
        ux_score = self.score_calculator.calculate_ux_score(wcag_results, gdpr_results)

        # Compile comprehensive evaluation (Value Object)
        evaluation = DeveloperEvaluation(
            developer=developer_name,
            task_title=task_title,
            evaluation_status=evaluation_status,
            ux_score=ux_score,
            # WCAG Accessibility results
            accessibility_issues=accessibility_issues,
            wcag_aa_compliance=wcag_results.get('wcag_aa_compliance', False),
            accessibility_details=wcag_results.get('accessibility_details', {}),
            accessibility_issues_list=wcag_results.get('issues', []),
            # UX issues
            ux_issues=total_issues,
            ux_issues_details=wcag_results.get('issues', []) + gdpr_results.get('issues', []),
            # GDPR compliance results
            gdpr_compliance=gdpr_results.get('gdpr_compliance', {}),
            gdpr_issues=gdpr_issues,
            gdpr_issues_list=gdpr_results.get('issues', [])
        )

        # Log results summary
        self.logger.log(f"WCAG Issues: {accessibility_issues}", "INFO")
        self.logger.log(f"GDPR Issues: {gdpr_issues}", "INFO")
        self.logger.log(f"UX Score: {ux_score}/100", "INFO")
        self.logger.log(f"Status: {evaluation_status}", "INFO")

        return evaluation

    def _log_developer_evaluation(
        self,
        evaluation_result: DeveloperEvaluation,
        developer_name: str
    ):
        """
        WHY: Log individual developer evaluation results
        RESPONSIBILITY: Provide consistent logging format
        PATTERNS: Strategy pattern with message mapping

        Args:
            evaluation_result: Evaluation results
            developer_name: Developer name
        """
        self.logger.log(f"Evaluation Status: {evaluation_result.evaluation_status}", "INFO")
        self.logger.log(f"UX Score: {evaluation_result.ux_score}/100", "INFO")
        self.logger.log(
            f"Accessibility Issues: {evaluation_result.accessibility_issues}",
            "INFO"
        )

        # Status-specific messages using dispatch table
        status_messages = {
            "FAIL": (
                f"❌ {developer_name} implementation FAILED UI/UX evaluation",
                "ERROR"
            ),
            "NEEDS_IMPROVEMENT": (
                f"⚠️  {developer_name} implementation needs UI/UX improvement",
                "WARNING"
            ),
        }

        # Get message and log level, default to success
        message, level = status_messages.get(
            evaluation_result.evaluation_status,
            (f"✅ {developer_name} implementation PASSED UI/UX evaluation", "SUCCESS")
        )
        self.logger.log(message, level)

    def _log_evaluation_summary(
        self,
        implementations_count: int,
        total_accessibility_issues: int,
        total_ux_issues: int
    ):
        """
        WHY: Log overall evaluation summary
        RESPONSIBILITY: Provide summary statistics
        PATTERNS: Presentation pattern

        Args:
            implementations_count: Number of implementations evaluated
            total_accessibility_issues: Total accessibility issues
            total_ux_issues: Total UX issues
        """
        self.logger.log(f"\n{'='*60}", "INFO")
        self.logger.log("📊 UI/UX Evaluation Summary", "INFO")
        self.logger.log(f"{'='*60}", "INFO")
        self.logger.log(f"Implementations Evaluated: {implementations_count}", "INFO")
        self.logger.log(f"Total Accessibility Issues: {total_accessibility_issues}", "INFO")
        self.logger.log(f"Total UX Issues: {total_ux_issues}", "INFO")

    def _determine_stage_status(
        self,
        total_accessibility_issues: int,
        all_evaluations_pass: bool
    ) -> str:
        """
        WHY: Determine overall stage status with logging
        RESPONSIBILITY: Calculate status and log decision
        PATTERNS: Delegation to score calculator

        Args:
            total_accessibility_issues: Total accessibility issues found
            all_evaluations_pass: Whether all evaluations passed

        Returns:
            Stage status ("PASS", "NEEDS_IMPROVEMENT", "FAIL")
        """
        status = self.score_calculator.determine_stage_status(
            total_accessibility_issues,
            all_evaluations_pass
        )

        # Log status-specific messages
        threshold = self.score_calculator.get_critical_threshold()

        if status == "FAIL":
            self.logger.log(
                f"❌ UI/UX evaluation FAILED - Critical accessibility issues found "
                f"({total_accessibility_issues} > {threshold})",
                "ERROR"
            )
        elif status == "NEEDS_IMPROVEMENT":
            self.logger.log("⚠️  UI/UX evaluation completed with warnings", "WARNING")
        else:
            self.logger.log(
                "✅ UI/UX evaluation PASSED - All implementations meet standards",
                "SUCCESS"
            )

        return status

    def get_stage_name(self) -> str:
        """
        WHY: Return stage name for identification
        RESPONSIBILITY: Provide stage identifier

        Returns:
            Stage name
        """
        return "uiux"
