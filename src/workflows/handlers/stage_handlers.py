#!/usr/bin/env python3
"""
Pipeline Stage Workflow Handlers

WHY:
Handles pipeline stage-specific issues including architecture regeneration,
code review revisions, integration conflicts, and validation reruns.

RESPONSIBILITY:
- Regenerate architecture documents
- Request code review revisions
- Resolve integration conflicts
- Re-run validation stages

PATTERNS:
- Strategy Pattern: Different stage recovery strategies
- Template Method: Common stage operation patterns
- Guard Clauses: Validate stage state before operations

INTEGRATION:
- Extends: WorkflowHandler base class
- Used by: WorkflowHandlerFactory for stage actions
- Coordinates with: Stage execution pipeline
"""

from typing import Dict, Any, List

from workflows.handlers.base_handler import WorkflowHandler
from artemis_logger import get_logger

logger = get_logger("workflow.stage_handlers")


class RegenerateArchitectureHandler(WorkflowHandler):
    """
    Regenerate architecture document

    WHY: Recover from architecture document errors or inconsistencies
    RESPONSIBILITY: Trigger architecture stage re-execution
    """

    def _execute_architecture_via_orchestrator(self, orchestrator) -> bool:
        """Execute architecture stage via orchestrator with guard clauses."""
        if not hasattr(orchestrator, "run_stage"):
            return False

        logger.info("Triggering architecture stage via orchestrator...")
        result = orchestrator.run_stage("architecture")

        if not result:
            logger.error("Architecture stage failed")
            return False

        logger.info("Architecture stage completed successfully")
        return True

    def _execute_architecture_via_pipeline(self, pipeline) -> bool:
        """Execute architecture stage via pipeline with guard clauses."""
        if not hasattr(pipeline, "execute_stage"):
            return False

        logger.info("Triggering architecture stage via pipeline...")
        result = pipeline.execute_stage("architecture")

        if not result:
            logger.error("Architecture stage failed")
            return False

        logger.info("Architecture stage completed successfully")
        return True

    def handle(self, context: Dict[str, Any]) -> bool:
        logger.info("Regenerating architecture...")

        try:
            # Get stage orchestrator or pipeline from context
            orchestrator = context.get("orchestrator")
            pipeline = context.get("pipeline")

            if not orchestrator and not pipeline:
                logger.warning(
                    "No orchestrator or pipeline provided in context. "
                    "To fully implement, provide orchestrator via context['orchestrator'] "
                    "or pipeline via context['pipeline']."
                )
                return False

            # Try orchestrator approach first
            if orchestrator:
                result = self._execute_architecture_via_orchestrator(orchestrator)
                if result:
                    return True

            # Try pipeline approach
            if pipeline:
                result = self._execute_architecture_via_pipeline(pipeline)
                if result:
                    return True

            logger.error("Neither orchestrator nor pipeline has required method for stage execution")
            return False

        except Exception as e:
            logger.error(f"Failed to regenerate architecture: {e}")
            return False


class RequestCodeReviewRevisionHandler(WorkflowHandler):
    """
    Request code review revision

    WHY: Address code review issues through developer agents
    RESPONSIBILITY: Send revision requests for identified issues
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        issues = context.get("review_issues", [])

        if not issues:
            logger.warning("No review issues provided for revision request")
            return True

        logger.info(f"Requesting revision for {len(issues)} code review issues")

        try:
            # Get developer agents from context
            developer_agents = context.get("developer_agents", [])
            messenger = context.get("messenger")

            if not developer_agents and not messenger:
                logger.warning(
                    "No developer agents or messenger provided in context. "
                    "To fully implement, provide developer_agents list or messenger instance."
                )
                return False

            revision_requests = []
            for i, issue in enumerate(issues):
                revision_request = {
                    "issue_id": i,
                    "file_path": issue.get("file_path"),
                    "line_number": issue.get("line_number"),
                    "severity": issue.get("severity", "medium"),
                    "description": issue.get("description"),
                    "suggested_fix": issue.get("suggested_fix"),
                }
                revision_requests.append(revision_request)

            # Send to developer agents directly
            if developer_agents:
                for agent in developer_agents:
                    if hasattr(agent, "handle_revision_request"):
                        logger.info(f"Sending revision request to developer agent: {agent}")
                        agent.handle_revision_request(revision_requests)

            # Or send via messenger
            elif messenger and hasattr(messenger, "send_message"):
                logger.info("Sending revision requests via messenger")
                messenger.send_message(
                    topic="code_review_revision",
                    message={
                        "type": "revision_request",
                        "issues": revision_requests
                    }
                )

            # Store revision requests in context for tracking
            context["revision_requests"] = revision_requests
            logger.info(f"Revision requests sent for {len(revision_requests)} issues")
            return True

        except Exception as e:
            logger.error(f"Failed to send revision requests: {e}")
            return False


class ResolveIntegrationConflictHandler(WorkflowHandler):
    """
    Resolve integration conflict

    WHY: Handle merge conflicts between developer solutions
    RESPONSIBILITY: Identify and resolve conflicting files
    """

    def _resolve_score_based(self, file_path: str, versions: List[Dict[str, Any]]) -> tuple:
        """Resolve conflict using score-based selection."""
        best_version = max(versions, key=lambda v: v.get("score", 0))
        resolved_content = best_version.get("content")
        logger.info(f"Resolved {file_path} using highest score: {best_version.get('score')}")
        return best_version, resolved_content

    def _resolve_latest(self, file_path: str, versions: List[Dict[str, Any]]) -> tuple:
        """Resolve conflict using latest timestamp."""
        best_version = max(versions, key=lambda v: v.get("timestamp", 0))
        resolved_content = best_version.get("content")
        logger.info(f"Resolved {file_path} using latest timestamp")
        return best_version, resolved_content

    def _resolve_author_preference(self, file_path: str, versions: List[Dict[str, Any]],
                                   preferred_author: str) -> tuple:
        """Resolve conflict using author preference with guard clauses."""
        matching_versions = [v for v in versions if v.get("author") == preferred_author]

        # Guard clause: No matching author found, fallback to score-based
        if not matching_versions:
            best_version = max(versions, key=lambda v: v.get("score", 0))
            resolved_content = best_version.get("content")
            logger.info(f"Resolved {file_path} using score (no preferred author)")
            return best_version, resolved_content

        # Preferred author found
        best_version = matching_versions[0]
        resolved_content = best_version.get("content")
        logger.info(f"Resolved {file_path} using preferred author: {preferred_author}")
        return best_version, resolved_content

    def _resolve_conflict(self, conflict_file: Dict[str, Any], resolution_strategy: str,
                         context: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a single conflict file using the specified strategy."""
        file_path = conflict_file.get("file_path")
        versions = conflict_file.get("versions", [])

        if not file_path or not versions:
            logger.warning(f"Invalid conflict file entry: {conflict_file}")
            return None

        logger.info(f"Resolving conflict in: {file_path}")

        # Dispatch table for resolution strategies
        strategy_handlers = {
            "score_based": lambda: self._resolve_score_based(file_path, versions),
            "latest": lambda: self._resolve_latest(file_path, versions),
            "author_preference": lambda: self._resolve_author_preference(
                file_path, versions, context.get("preferred_author")
            )
        }

        # Get handler from dispatch table or use default
        handler = strategy_handlers.get(resolution_strategy)

        if not handler:
            logger.warning(f"Unknown resolution strategy: {resolution_strategy}, using score-based")
            handler = strategy_handlers["score_based"]

        best_version, resolved_content = handler()

        return {
            "file_path": file_path,
            "content": resolved_content,
            "selected_version": best_version
        }

    def handle(self, context: Dict[str, Any]) -> bool:
        conflict_files = context.get("conflict_files", [])

        if not conflict_files:
            logger.info("No conflict files to resolve")
            return True

        logger.info(f"Resolving conflicts in {len(conflict_files)} files")

        try:
            resolution_strategy = context.get("resolution_strategy", "score_based")
            resolved_files = []
            failed_files = []

            for conflict_file in conflict_files:
                resolved = self._resolve_conflict(conflict_file, resolution_strategy, context)

                if resolved:
                    resolved_files.append(resolved)
                else:
                    failed_files.append(conflict_file.get("file_path"))

            # Store results in context
            context["resolved_files"] = resolved_files
            context["resolution_failures"] = failed_files

            logger.info(
                f"Conflict resolution completed: {len(resolved_files)} resolved, "
                f"{len(failed_files)} failed"
            )

            return len(failed_files) == 0

        except Exception as e:
            logger.error(f"Failed to resolve integration conflicts: {e}")
            return False


class RerunValidationHandler(WorkflowHandler):
    """
    Re-run validation

    WHY: Verify fixes by re-executing validation checks
    RESPONSIBILITY: Trigger validation stage re-execution
    """

    def _validate_via_validator(self, validator, context: Dict[str, Any]) -> bool:
        """Execute validation via validator instance with guard clauses."""
        if not hasattr(validator, "validate"):
            return False

        logger.info("Running validation via validator instance...")
        validation_results = validator.validate()
        context["validation_results"] = validation_results

        if not validation_results.get("success", False):
            logger.error("Validation failed")
            return False

        logger.info("Validation completed successfully")
        return True

    def _validate_via_orchestrator(self, orchestrator) -> bool:
        """Execute validation stage via orchestrator with guard clauses."""
        if not hasattr(orchestrator, "run_stage"):
            return False

        logger.info("Triggering validation stage via orchestrator...")
        result = orchestrator.run_stage("validation")

        if not result:
            logger.error("Validation stage failed")
            return False

        logger.info("Validation stage completed successfully")
        return True

    def _validate_via_pipeline(self, pipeline) -> bool:
        """Execute validation stage via pipeline with guard clauses."""
        if not hasattr(pipeline, "execute_stage"):
            return False

        logger.info("Triggering validation stage via pipeline...")
        result = pipeline.execute_stage("validation")

        if not result:
            logger.error("Validation stage failed")
            return False

        logger.info("Validation stage completed successfully")
        return True

    def handle(self, context: Dict[str, Any]) -> bool:
        logger.info("Re-running validation...")

        try:
            # Get stage orchestrator or pipeline from context
            orchestrator = context.get("orchestrator")
            pipeline = context.get("pipeline")
            validator = context.get("validator")

            # Try multiple approaches to trigger validation in priority order

            # Approach 1: Direct validator call
            if validator:
                result = self._validate_via_validator(validator, context)
                if result:
                    return True

            # Approach 2: Orchestrator stage execution
            if orchestrator:
                result = self._validate_via_orchestrator(orchestrator)
                if result:
                    return True

            # Approach 3: Pipeline stage execution
            if pipeline:
                result = self._validate_via_pipeline(pipeline)
                if result:
                    return True

            logger.warning(
                "No validator, orchestrator, or pipeline provided in context. "
                "To fully implement, provide one of: context['validator'], "
                "context['orchestrator'], or context['pipeline']."
            )
            return False

        except Exception as e:
            logger.error(f"Failed to re-run validation: {e}")
            return False
