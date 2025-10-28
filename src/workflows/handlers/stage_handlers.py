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

            # Try to trigger architecture stage re-run
            if orchestrator and hasattr(orchestrator, "run_stage"):
                logger.info("Triggering architecture stage via orchestrator...")
                result = orchestrator.run_stage("architecture")
                if result:
                    logger.info("Architecture stage completed successfully")
                    return True
                else:
                    logger.error("Architecture stage failed")
                    return False

            elif pipeline and hasattr(pipeline, "execute_stage"):
                logger.info("Triggering architecture stage via pipeline...")
                result = pipeline.execute_stage("architecture")
                if result:
                    logger.info("Architecture stage completed successfully")
                    return True
                else:
                    logger.error("Architecture stage failed")
                    return False

            else:
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
                file_path = conflict_file.get("file_path")
                versions = conflict_file.get("versions", [])

                if not file_path or not versions:
                    logger.warning(f"Invalid conflict file entry: {conflict_file}")
                    failed_files.append(file_path)
                    continue

                logger.info(f"Resolving conflict in: {file_path}")

                # Strategy 1: Score-based selection
                if resolution_strategy == "score_based":
                    best_version = max(versions, key=lambda v: v.get("score", 0))
                    resolved_content = best_version.get("content")
                    logger.info(f"Resolved {file_path} using highest score: {best_version.get('score')}")

                # Strategy 2: Timestamp-based (latest wins)
                elif resolution_strategy == "latest":
                    best_version = max(versions, key=lambda v: v.get("timestamp", 0))
                    resolved_content = best_version.get("content")
                    logger.info(f"Resolved {file_path} using latest timestamp")

                # Strategy 3: Author-based (prefer specific author)
                elif resolution_strategy == "author_preference":
                    preferred_author = context.get("preferred_author")
                    matching_versions = [v for v in versions if v.get("author") == preferred_author]
                    if matching_versions:
                        best_version = matching_versions[0]
                        resolved_content = best_version.get("content")
                        logger.info(f"Resolved {file_path} using preferred author: {preferred_author}")
                    else:
                        # Fallback to score-based
                        best_version = max(versions, key=lambda v: v.get("score", 0))
                        resolved_content = best_version.get("content")
                        logger.info(f"Resolved {file_path} using score (no preferred author)")

                else:
                    logger.warning(f"Unknown resolution strategy: {resolution_strategy}, using score-based")
                    best_version = max(versions, key=lambda v: v.get("score", 0))
                    resolved_content = best_version.get("content")

                # Store resolved file
                resolved_files.append({
                    "file_path": file_path,
                    "content": resolved_content,
                    "selected_version": best_version
                })

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

    def handle(self, context: Dict[str, Any]) -> bool:
        logger.info("Re-running validation...")

        try:
            # Get stage orchestrator or pipeline from context
            orchestrator = context.get("orchestrator")
            pipeline = context.get("pipeline")
            validator = context.get("validator")

            # Try multiple approaches to trigger validation

            # Approach 1: Direct validator call
            if validator and hasattr(validator, "validate"):
                logger.info("Running validation via validator instance...")
                validation_results = validator.validate()
                context["validation_results"] = validation_results

                if validation_results.get("success", False):
                    logger.info("Validation completed successfully")
                    return True
                else:
                    logger.error("Validation failed")
                    return False

            # Approach 2: Orchestrator stage execution
            elif orchestrator and hasattr(orchestrator, "run_stage"):
                logger.info("Triggering validation stage via orchestrator...")
                result = orchestrator.run_stage("validation")
                if result:
                    logger.info("Validation stage completed successfully")
                    return True
                else:
                    logger.error("Validation stage failed")
                    return False

            # Approach 3: Pipeline stage execution
            elif pipeline and hasattr(pipeline, "execute_stage"):
                logger.info("Triggering validation stage via pipeline...")
                result = pipeline.execute_stage("validation")
                if result:
                    logger.info("Validation stage completed successfully")
                    return True
                else:
                    logger.error("Validation stage failed")
                    return False

            else:
                logger.warning(
                    "No validator, orchestrator, or pipeline provided in context. "
                    "To fully implement, provide one of: context['validator'], "
                    "context['orchestrator'], or context['pipeline']."
                )
                return False

        except Exception as e:
            logger.error(f"Failed to re-run validation: {e}")
            return False
