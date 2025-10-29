#!/usr/bin/env python3
"""
Code Review Stage Core

WHY: Orchestrate comprehensive code review workflow
RESPONSIBILITY: Coordinate multi-developer review, aggregation, and reporting
PATTERNS: Facade Pattern, Single Responsibility, Guard Clauses
"""

import os
from typing import Dict, Optional, Any

from artemis_stage_interface import PipelineStage, LoggerInterface
from agent_messenger import AgentMessenger
from rag_agent import RAGAgent
from pipeline_observer import PipelineObservable
from supervised_agent_mixin import SupervisedStageMixin
from debug_mixin import DebugMixin
from artemis_exceptions import PipelineStageError, wrap_exception

from .review_coordinator import MultiDeveloperReviewCoordinator
from .review_aggregator import ReviewResultAggregator
from .review_notifications import ReviewNotificationManager
from .storage_handlers import ReviewStorageHandler
from .refactoring_generator import RefactoringSuggestionGenerator


class CodeReviewStage(PipelineStage, SupervisedStageMixin, DebugMixin):
    """
    Code Review Stage - Security, Quality, GDPR, and Accessibility Review.

    WHY: Orchestrate code review for security, quality, GDPR, and accessibility
    RESPONSIBILITY: Coordinate review workflow components
    PATTERNS: Facade Pattern, Dependency Injection, Guard Clauses

    Reviews developer implementations for:
    - Security vulnerabilities (OWASP Top 10)
    - Code quality and anti-patterns
    - GDPR compliance
    - Accessibility (WCAG 2.1 AA)

    Integrates with supervisor for:
    - LLM cost tracking for code review
    - Critical security finding alerts
    - Code review failure recovery
    - Automatic heartbeat and health monitoring
    """

    def __init__(
        self,
        messenger: AgentMessenger,
        rag: RAGAgent,
        logger: LoggerInterface,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        observable: Optional[PipelineObservable] = None,
        supervisor: Optional['SupervisorAgent'] = None,
        code_review_dir: Optional[str] = None,
        ai_service: Optional['AIQueryService'] = None
    ):
        """
        Initialize Code Review Stage.

        WHY: Dependency injection for all review components
        PATTERN: Constructor injection with defaults

        Args:
            messenger: Agent messenger for inter-agent communication
            rag: RAG agent for storing review results
            logger: Logger interface
            llm_provider: LLM provider (openai/anthropic)
            llm_model: Specific model to use
            observable: Optional PipelineObservable for event broadcasting
            supervisor: Optional SupervisorAgent for monitoring
            code_review_dir: Directory for code review output
            ai_service: Optional AI Query Service
        """
        # Initialize PipelineStage
        PipelineStage.__init__(self)

        # Initialize SupervisedStageMixin for health monitoring
        # Code review typically takes longer, so use 20 second heartbeat
        SupervisedStageMixin.__init__(
            self,
            supervisor=supervisor,
            stage_name="CodeReviewStage",
            heartbeat_interval=20  # Longer interval for LLM-heavy stage
        )

        # Initialize DebugMixin
        DebugMixin.__init__(self, component_name="code_review")

        self.messenger = messenger
        self.rag = rag
        self.logger = logger
        self.ai_service = ai_service
        self.observable = observable

        # Configure LLM settings
        self.llm_provider = llm_provider or os.getenv("ARTEMIS_LLM_PROVIDER", "openai")
        self.llm_model = llm_model or os.getenv("ARTEMIS_LLM_MODEL")

        # Set code review directory
        self.code_review_dir = self._resolve_code_review_directory(code_review_dir)

        # Initialize components
        self.coordinator = MultiDeveloperReviewCoordinator(
            logger=logger,
            llm_provider=self.llm_provider,
            llm_model=self.llm_model,
            rag_agent=rag,
            code_review_dir=self.code_review_dir,
            debug_component=self
        )

        self.aggregator = ReviewResultAggregator(logger=logger)

        self.notification_manager = ReviewNotificationManager(
            observable=observable,
            messenger=messenger,
            logger=logger
        )

        self.storage_handler = ReviewStorageHandler(
            rag=rag,
            logger=logger
        )

        self.refactoring_generator = RefactoringSuggestionGenerator(
            rag=rag,
            logger=logger
        )

    def _resolve_code_review_directory(self, code_review_dir: Optional[str]) -> str:
        """
        Resolve code review directory path.

        WHY: Centralized directory resolution logic
        PATTERN: Guard clause, Early return
        """
        if code_review_dir is not None:
            return code_review_dir

        code_review_dir = os.getenv("ARTEMIS_CODE_REVIEW_DIR", "../../.artemis_data/code_reviews")

        if os.path.isabs(code_review_dir):
            return code_review_dir

        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, code_review_dir)

    @wrap_exception(PipelineStageError, "Code review stage execution failed")
    def execute(self, card: Dict, context: Dict) -> Dict:
        """
        Execute code review with supervisor monitoring.

        WHY: Main entry point for stage execution
        PATTERN: Template Method, Supervised execution
        """
        metadata = {
            "task_id": card.get('card_id'),
            "stage": "code_review"
        }

        with self.supervised_execution(metadata):
            return self._do_code_review(card, context)

    def _do_code_review(self, card: Dict, context: Dict) -> Dict:
        """
        Internal method - performs code review on all developer implementations.

        WHY: Separate internal implementation from public interface
        RESPONSIBILITY: Orchestrate complete review workflow
        PATTERN: Guard clauses, Progressive disclosure

        Reviews each developer's implementation for:
        - OWASP Top 10 security vulnerabilities
        - Code quality and anti-patterns
        - GDPR compliance
        - WCAG 2.1 AA accessibility

        Args:
            card: Kanban card with task details
            context: Context from previous stages (includes developers)

        Returns:
            Dict with review results for all developers
        """
        self.logger.log("Starting Code Review Stage", "STAGE")
        self.logger.log("🔍 Comprehensive Security & Quality Analysis", "INFO")

        card_id = card['card_id']
        task_title = card.get('title', 'Unknown Task')
        task_description = card.get('description', '')

        # Get adaptive config and code review depth
        adaptive_config = context.get('adaptive_config', None)
        if adaptive_config:
            code_review_depth = adaptive_config.code_review_depth
            self.logger.log(f"🔧 Using adaptive code review depth: {code_review_depth}", "INFO")
            self._apply_review_depth_to_coordinator(code_review_depth)
        else:
            code_review_depth = 'standard'

        # DEBUG: Log stage entry
        self.debug_log("Starting code review", card_id=card_id, task_title=task_title, review_depth=code_review_depth)

        # Update progress: starting
        self.update_progress({"step": "starting", "progress_percent": 5})

        # Get developer results from context
        developers = context.get('developers', [])
        if not developers:
            return self._handle_no_developers()

        self.logger.log(f"Reviewing {len(developers)} developer implementation(s)", "INFO")
        self.debug_log(
            "Developers found for review",
            developer_count=len(developers),
            developer_names=[d if isinstance(d, str) else d.get('name', 'unknown') for d in developers]
        )

        # Update progress: initializing reviews
        self.update_progress({"step": "initializing_reviews", "progress_percent": 10})

        # Review all developers
        review_results = self.coordinator.review_all_developers(
            developers=developers,
            card_id=card_id,
            task_title=task_title,
            task_description=task_description,
            progress_callback=self.update_progress,
            notification_manager=self.notification_manager
        )

        # Aggregate results
        aggregated = self.aggregator.aggregate_reviews(review_results)

        # Update progress: summarizing results
        self.update_progress({"step": "summarizing_results", "progress_percent": 85})

        # DEBUG: Dump review results
        self.debug_dump_if_enabled('dump_review_results', "Code Review Results", {
            "review_count": len(review_results),
            "critical_issues": aggregated['total_critical_issues'],
            "high_issues": aggregated['total_high_issues'],
            "all_pass": aggregated['all_reviews_pass'],
            "reviews": review_results
        })

        # Log summary
        self._log_review_summary(aggregated)

        # Update progress: determining status
        self.update_progress({"step": "determining_status", "progress_percent": 95})

        # Determine overall stage status
        stage_status = self._determine_stage_status(aggregated)

        # Generate refactoring suggestions if needed
        refactoring_suggestions = self._generate_refactoring_if_needed(
            stage_status, review_results, card_id, task_title
        )

        # Update progress: complete
        self.update_progress({"step": "complete", "progress_percent": 100})

        # Build final result
        result = {
            "stage": "code_review",
            "status": stage_status,
            "reviews": review_results,
            "total_critical_issues": aggregated['total_critical_issues'],
            "total_high_issues": aggregated['total_high_issues'],
            "all_reviews_pass": aggregated['all_reviews_pass'],
            "implementations_reviewed": len(review_results)
        }

        if refactoring_suggestions:
            result["refactoring_suggestions"] = refactoring_suggestions

        return result

    def _handle_no_developers(self) -> Dict:
        """
        Handle case when no developers are available.

        WHY: Extract early return case for clarity
        PATTERN: Guard clause, Named return
        """
        self.logger.log("No developer implementations found to review", "WARNING")
        self.debug_log("No developers to review", developer_count=0)

        return {
            "stage": "code_review",
            "status": "SKIPPED",
            "reason": "No implementations to review"
        }

    def _log_review_summary(self, aggregated: Dict) -> None:
        """
        Log review summary to console.

        WHY: Separate presentation logic
        PATTERN: Single Responsibility
        """
        self.logger.log(f"\n{'='*60}", "INFO")
        self.logger.log("📊 Code Review Summary", "INFO")
        self.logger.log(f"{'='*60}", "INFO")
        self.logger.log(f"Implementations Reviewed: {aggregated['review_count']}", "INFO")
        self.logger.log(f"Total Critical Issues: {aggregated['total_critical_issues']}", "INFO")
        self.logger.log(f"Total High Issues: {aggregated['total_high_issues']}", "INFO")

    def _determine_stage_status(self, aggregated: Dict) -> str:
        """
        Determine overall stage status based on aggregated results.

        WHY: Centralized status determination logic
        PATTERN: Strategy pattern using dispatch table
        """
        total_critical = aggregated['total_critical_issues']
        all_pass = aggregated['all_reviews_pass']

        if total_critical > 0:
            self.logger.log("❌ Code review FAILED - Critical security/compliance issues found", "ERROR")
            return "FAIL"

        if not all_pass:
            self.logger.log("⚠️  Code review completed with warnings", "WARNING")
            return "NEEDS_IMPROVEMENT"

        self.logger.log("✅ Code review PASSED - All implementations meet standards", "SUCCESS")
        return "PASS"

    def _generate_refactoring_if_needed(
        self,
        stage_status: str,
        review_results: list,
        card_id: str,
        task_title: str
    ) -> Optional[str]:
        """
        Generate refactoring suggestions if review failed or needs improvement.

        WHY: Conditional refactoring generation
        PATTERN: Guard clause, Early return
        """
        if stage_status not in ["FAIL", "NEEDS_IMPROVEMENT"]:
            return None

        return self.refactoring_generator.generate_suggestions(
            review_results=review_results,
            card_id=card_id,
            task_title=task_title
        )

    def _apply_review_depth_to_coordinator(self, code_review_depth: str) -> None:
        """
        Apply code review depth setting to coordinator.

        WHY: Adaptive review depth based on task complexity and resources
        RESPONSIBILITY: Configure coordinator based on review depth

        Args:
            code_review_depth: "quick", "standard", or "thorough"

        Mapping:
            quick -> minimal checks, no advanced validation, skip property tests
            standard -> normal checks, code standards + static analysis
            thorough -> all checks, strict severity, all validations enabled
        """
        if code_review_depth == "quick":
            # Quick review: minimal checks for fast feedback
            self.coordinator.enable_code_standards = True
            self.coordinator.code_standards_reviewer.severity_threshold = "critical"
            self.coordinator.enable_advanced_validation = False
            self.coordinator.advanced_validation_reviewer.enable_static_analysis = False
            self.coordinator.advanced_validation_reviewer.enable_property_tests = False
            self.logger.log("   Quick review: Critical issues only, skip advanced validation", "INFO")

        elif code_review_depth == "thorough":
            # Thorough review: all checks enabled, strict thresholds
            self.coordinator.enable_code_standards = True
            self.coordinator.code_standards_reviewer.severity_threshold = "info"
            self.coordinator.enable_advanced_validation = True
            self.coordinator.advanced_validation_reviewer.enable_static_analysis = True
            self.coordinator.advanced_validation_reviewer.enable_property_tests = True
            # Lower max complexity for stricter checks
            reviewer = self.coordinator.advanced_validation_reviewer
            if hasattr(reviewer, 'static_analysis_config') and reviewer.static_analysis_config:
                reviewer.static_analysis_config['max_complexity'] = 8
            self.logger.log("   Thorough review: All checks enabled, strict thresholds", "INFO")

        else:  # standard
            # Standard review: balanced approach (defaults)
            self.coordinator.enable_code_standards = True
            self.coordinator.code_standards_reviewer.severity_threshold = "warning"
            self.coordinator.enable_advanced_validation = True
            self.coordinator.advanced_validation_reviewer.enable_static_analysis = True
            self.coordinator.advanced_validation_reviewer.enable_property_tests = False  # Skip property tests by default
            self.logger.log("   Standard review: Balanced checks, warning+ severity", "INFO")

    def get_stage_name(self) -> str:
        """
        Return stage name.

        WHY: Required by PipelineStage interface
        """
        return "code_review"
