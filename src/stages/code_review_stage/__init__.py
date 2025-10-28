#!/usr/bin/env python3
"""
Code Review Stage Package - Public API

WHY: Provide clean public interface and maintain backward compatibility.
RESPONSIBILITY: Export main CodeReviewStage class and public types.
PATTERNS: Facade pattern - simplify access to complex subsystem.

This package provides comprehensive code review functionality including:
- Security vulnerability detection (OWASP Top 10)
- Code quality analysis
- GDPR compliance checking
- Accessibility standards (WCAG 2.1 AA)
- Refactoring suggestions generation
"""

import os
from typing import Dict, Optional

from artemis_stage_interface import PipelineStage, LoggerInterface
from agent_messenger import AgentMessenger
from rag_agent import RAGAgent
from pipeline_observer import PipelineObservable
from supervised_agent_mixin import SupervisedStageMixin
from debug_mixin import DebugMixin
from artemis_exceptions import PipelineStageError, wrap_exception

from .models import (
    ReviewStatus,
    ReviewMetrics,
    DeveloperReviewResult,
    StageProgress,
    CodeReviewStageResult
)
from .review_executor import ReviewExecutor
from .review_notifier import ReviewNotifier
from .storage_manager import ReviewStorageManager
from .refactoring_suggestions import RefactoringSuggestionsGenerator


class CodeReviewStage(PipelineStage, SupervisedStageMixin, DebugMixin):
    """
    Code review pipeline stage.

    WHY: Review developer implementations for security, quality, GDPR, and accessibility.
    RESPONSIBILITY: Orchestrate code review workflow across all components.
    PATTERNS: Facade pattern - provides simple interface to complex review subsystem.

    This stage reviews all developer implementations and provides comprehensive
    reports on security vulnerabilities, code quality issues, GDPR compliance,
    and accessibility standards.

    Integrates with supervisor for:
    - LLM cost tracking for code review
    - Critical security finding alerts
    - Code review failure recovery
    - Automatic heartbeat and health monitoring

    Attributes:
        messenger: Agent messenger for inter-agent communication
        rag: RAG agent for storing review results
        logger: Logger interface
        ai_service: Optional AI query service
        llm_provider: LLM provider (openai/anthropic)
        llm_model: Specific model to use
        observable: Optional PipelineObservable for event broadcasting
        code_review_dir: Directory for code review output
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

        Args:
            messenger: Agent messenger for inter-agent communication
            rag: RAG agent for storing review results
            logger: Logger interface
            llm_provider: LLM provider (openai/anthropic)
            llm_model: Specific model to use
            observable: Optional PipelineObservable for event broadcasting
            supervisor: Optional SupervisorAgent for monitoring
            code_review_dir: Directory for code review output
            ai_service: Optional AI query service for future use
        """
        # Initialize parent classes
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
        self.llm_provider = llm_provider or os.getenv("ARTEMIS_LLM_PROVIDER", "openai")
        self.llm_model = llm_model or os.getenv("ARTEMIS_LLM_MODEL")
        self.observable = observable

        # Set code review directory from config or use default
        self.code_review_dir = self._resolve_code_review_dir(code_review_dir)

        # Initialize subsystem components
        self.notifier = ReviewNotifier(observable, logger)
        self.storage = ReviewStorageManager(rag, messenger, logger)
        self.suggestions = RefactoringSuggestionsGenerator(rag, logger)
        self.executor = ReviewExecutor(
            llm_provider=self.llm_provider,
            llm_model=self.llm_model,
            code_review_dir=self.code_review_dir,
            logger=logger,
            notifier=self.notifier,
            storage=self.storage,
            progress_callback=self.update_progress
        )

    def _resolve_code_review_dir(self, code_review_dir: Optional[str]) -> str:
        """
        Resolve code review directory path.

        WHY: DRY - centralize directory resolution logic.

        Args:
            code_review_dir: Optional directory path from config

        Returns:
            Absolute path to code review directory
        """
        if code_review_dir:
            return code_review_dir

        default_dir = os.getenv(
            "ARTEMIS_CODE_REVIEW_DIR",
            "../../.artemis_data/code_reviews"
        )

        if os.path.isabs(default_dir):
            return default_dir

        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, default_dir)

    @wrap_exception(PipelineStageError, "Code review stage execution failed")
    def execute(self, card: Dict, context: Dict) -> Dict:
        """
        Execute code review with supervisor monitoring.

        WHY: Main entry point for pipeline integration.

        Args:
            card: Kanban card with task details
            context: Context from previous stages (includes developers)

        Returns:
            Dictionary with review results
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

        WHY: Separate internal logic from supervised wrapper.
        RESPONSIBILITY: Coordinate full review workflow.

        Reviews each developer's implementation for:
        - OWASP Top 10 security vulnerabilities
        - Code quality and anti-patterns
        - GDPR compliance
        - WCAG 2.1 AA accessibility

        Args:
            card: Kanban card with task details
            context: Context from previous stages (includes developers)

        Returns:
            Dictionary with review results
        """
        self.logger.log("Starting Code Review Stage", "STAGE")
        self.logger.log("🔍 Comprehensive Security & Quality Analysis", "INFO")

        card_id = card['card_id']
        task_title = card.get('title', 'Unknown Task')
        task_description = card.get('description', '')

        # DEBUG: Log stage entry
        self.debug_log("Starting code review", card_id=card_id, task_title=task_title)

        # Update progress: starting
        self.update_progress({"step": "starting", "progress_percent": 5})

        # Get developer results from context
        developers = context.get('developers', [])

        # Guard clause: Check if developers exist
        if not developers:
            return self._handle_no_developers()

        self.logger.log(f"Reviewing {len(developers)} developer implementation(s)", "INFO")
        self.debug_log(
            "Developers found for review",
            developer_count=len(developers),
            developer_names=[
                d if isinstance(d, str) else d.get('name', 'unknown')
                for d in developers
            ]
        )

        # Update progress: initializing reviews
        self.update_progress({"step": "initializing_reviews", "progress_percent": 10})

        # Review all developers
        review_results, all_reviews_pass, total_critical, total_high = (
            self.executor.review_all_developers(
                developers,
                card_id,
                task_title,
                task_description
            )
        )

        # Update progress: summarizing results
        self.update_progress({"step": "summarizing_results", "progress_percent": 85})

        # DEBUG: Dump review results
        self.debug_dump_if_enabled('dump_review_results', "Code Review Results", {
            "review_count": len(review_results),
            "critical_issues": total_critical,
            "high_issues": total_high,
            "all_pass": all_reviews_pass,
            "reviews": review_results
        })

        # Log summary
        self._log_review_summary(
            len(review_results),
            total_critical,
            total_high
        )

        # Update progress: determining status
        self.update_progress({"step": "determining_status", "progress_percent": 95})

        # Determine stage status
        stage_status = self._determine_stage_status(total_critical, all_reviews_pass)

        # Generate refactoring suggestions if needed
        refactoring_suggestions = None
        if stage_status in ["FAIL", "NEEDS_IMPROVEMENT"]:
            refactoring_suggestions = self.suggestions.generate_suggestions(
                review_results,
                card_id,
                task_title
            )

        # Update progress: complete
        self.update_progress({"step": "complete", "progress_percent": 100})

        # Build result
        result = CodeReviewStageResult(
            stage="code_review",
            status=stage_status,
            reviews=review_results,
            total_critical_issues=total_critical,
            total_high_issues=total_high,
            all_reviews_pass=all_reviews_pass,
            implementations_reviewed=len(review_results),
            refactoring_suggestions=refactoring_suggestions
        )

        return result.to_dict()

    def _handle_no_developers(self) -> Dict:
        """
        Handle case when no developers found.

        WHY: Guard clause extracted to method for clarity.

        Returns:
            SKIPPED result dictionary
        """
        self.logger.log("No developer implementations found to review", "WARNING")
        self.debug_log("No developers to review", developer_count=0)

        result = CodeReviewStageResult.skipped("No implementations to review")
        return result.to_dict()

    def _log_review_summary(
        self,
        review_count: int,
        critical_issues: int,
        high_issues: int
    ) -> None:
        """
        Log overall review summary.

        WHY: DRY - centralize summary logging.

        Args:
            review_count: Number of reviews completed
            critical_issues: Total critical issues
            high_issues: Total high priority issues
        """
        self.logger.log(f"\n{'='*60}", "INFO")
        self.logger.log("📊 Code Review Summary", "INFO")
        self.logger.log(f"{'='*60}", "INFO")
        self.logger.log(f"Implementations Reviewed: {review_count}", "INFO")
        self.logger.log(f"Total Critical Issues: {critical_issues}", "INFO")
        self.logger.log(f"Total High Issues: {high_issues}", "INFO")

    def _determine_stage_status(
        self,
        critical_issues: int,
        all_reviews_pass: bool
    ) -> str:
        """
        Determine overall stage status.

        WHY: Strategy pattern for status determination with clear logging.
        PATTERNS: Strategy pattern via conditional logic.

        Args:
            critical_issues: Total critical issues count
            all_reviews_pass: Whether all reviews passed

        Returns:
            Stage status string (PASS/FAIL/NEEDS_IMPROVEMENT)
        """
        # Guard clause: Critical issues always fail
        if critical_issues > 0:
            self.logger.log(
                "❌ Code review FAILED - Critical security/compliance issues found",
                "ERROR"
            )
            return "FAIL"

        # Guard clause: Check if any review needs improvement
        if not all_reviews_pass:
            self.logger.log(
                "⚠️  Code review completed with warnings",
                "WARNING"
            )
            return "NEEDS_IMPROVEMENT"

        # All reviews passed
        self.logger.log(
            "✅ Code review PASSED - All implementations meet standards",
            "SUCCESS"
        )
        return "PASS"

    def get_stage_name(self) -> str:
        """
        Return stage name.

        Returns:
            Stage name string
        """
        return "code_review"


# Export public API
__all__ = [
    'CodeReviewStage',
    'ReviewStatus',
    'ReviewMetrics',
    'DeveloperReviewResult',
    'StageProgress',
    'CodeReviewStageResult'
]
