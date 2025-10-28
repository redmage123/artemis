#!/usr/bin/env python3
"""
Multi-Agent Coordination Workflow Handlers

WHY:
Handles multi-agent coordination issues including arbitration deadlocks,
solution merging, and messenger service management.

RESPONSIBILITY:
- Break arbitration deadlocks between agents
- Merge conflicting developer solutions
- Restart messenger services
- Coordinate agent interactions

PATTERNS:
- Strategy Pattern: Different arbitration strategies
- Mediator Pattern: Coordinate between agents
- Random Selection: Tie-breaking for equal scores

INTEGRATION:
- Extends: WorkflowHandler base class
- Used by: WorkflowHandlerFactory for multi-agent actions
- Coordinates with: Developer agents and messenger system
"""

import random
from typing import Dict, Any, List

from workflows.handlers.base_handler import WorkflowHandler
from artemis_logger import get_logger

logger = get_logger("workflow.multi_agent_handlers")


class BreakArbitrationDeadlockHandler(WorkflowHandler):
    """
    Break arbitration deadlock

    WHY: Resolve tie situations when agents produce equal quality solutions
    RESPONSIBILITY: Choose solution based on score or random selection
    PATTERNS: Decision strategy with fallback to random selection
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        developer_a_score = context.get("developer_a_score", 0)
        developer_b_score = context.get("developer_b_score", 0)

        # Choose based on scores, or random if tied
        if developer_a_score > developer_b_score:
            context["chosen_solution"] = "developer_a"
            print("[Workflow] Arbitration: Chose Developer A (higher score)")
        elif developer_b_score > developer_a_score:
            context["chosen_solution"] = "developer_b"
            print("[Workflow] Arbitration: Chose Developer B (higher score)")
        else:
            context["chosen_solution"] = random.choice(["developer_a", "developer_b"])
            print(f"[Workflow] Arbitration: Randomly chose {context['chosen_solution']}")

        return True


class MergeDeveloperSolutionsHandler(WorkflowHandler):
    """
    Merge conflicting developer solutions

    WHY: Combine best aspects of multiple solutions intelligently
    RESPONSIBILITY: Implement intelligent merge logic for code solutions
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        logger.info("Merging developer solutions...")

        try:
            # Get solutions from context
            solution_a = context.get("solution_a", {})
            solution_b = context.get("solution_b", {})

            if not solution_a or not solution_b:
                logger.error("Missing developer solutions for merge")
                return False

            # Extract file changes from both solutions
            files_a = solution_a.get("files", {})
            files_b = solution_b.get("files", {})

            merged_solution = {
                "files": {},
                "metadata": {
                    "merge_strategy": "intelligent",
                    "conflicts": []
                }
            }

            # Get all unique file paths
            all_files = set(files_a.keys()) | set(files_b.keys())

            for file_path in all_files:
                file_a_content = files_a.get(file_path)
                file_b_content = files_b.get(file_path)
                self._merge_file_content(
                    file_path, file_a_content, file_b_content,
                    solution_a, solution_b, merged_solution
                )

            # Store merged solution in context
            context["merged_solution"] = merged_solution
            context["merge_conflicts"] = merged_solution["metadata"]["conflicts"]

            conflict_count = len(merged_solution["metadata"]["conflicts"])
            logger.info(f"Merge completed: {len(merged_solution['files'])} files, {conflict_count} conflicts")

            return True

        except Exception as e:
            logger.error(f"Failed to merge developer solutions: {e}")
            return False

    @staticmethod
    def _merge_file_content(
        file_path: str,
        file_a_content: Any,
        file_b_content: Any,
        solution_a: Dict,
        solution_b: Dict,
        merged_solution: Dict
    ) -> None:
        """
        Merge content for a single file from two solutions.

        WHY: Separate file merging logic to avoid nested control flow
        RESPONSIBILITY: Handle different merge scenarios (only A, only B, identical, conflict)
        PATTERNS: Guard clauses for early returns
        """
        # Guard: File only in solution A
        if file_a_content and not file_b_content:
            merged_solution["files"][file_path] = file_a_content
            logger.debug(f"Taking file from solution A: {file_path}")
            return

        # Guard: File only in solution B
        if file_b_content and not file_a_content:
            merged_solution["files"][file_path] = file_b_content
            logger.debug(f"Taking file from solution B: {file_path}")
            return

        # Guard: Identical content in both
        if file_a_content == file_b_content:
            merged_solution["files"][file_path] = file_a_content
            logger.debug(f"Files identical, using either: {file_path}")
            return

        # Content differs - mark as conflict and use score-based selection
        logger.warning(f"Conflict detected in file: {file_path}")
        merged_solution["metadata"]["conflicts"].append(file_path)

        # Use score-based selection
        score_a = solution_a.get("score", 0)
        score_b = solution_b.get("score", 0)

        if score_a >= score_b:
            merged_solution["files"][file_path] = file_a_content
            logger.info(f"Using solution A for {file_path} (score: {score_a} >= {score_b})")
        else:
            merged_solution["files"][file_path] = file_b_content
            logger.info(f"Using solution B for {file_path} (score: {score_b} > {score_a})")


class RestartMessengerHandler(WorkflowHandler):
    """
    Restart messenger service

    WHY: Recover from messenger communication failures
    RESPONSIBILITY: Restart inter-agent communication service
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        logger.info("Restarting messenger service...")

        try:
            # Get messenger instance from context
            messenger = context.get("messenger")

            # Guard: No messenger provided
            if not messenger:
                logger.warning(
                    "No messenger instance provided in context. "
                    "To fully implement, provide messenger instance via context['messenger']."
                )
                return False

            # Attempt to restart messenger using available methods
            return self._restart_messenger(messenger)

        except Exception as e:
            logger.error(f"Failed to restart messenger: {e}")
            return False

    @staticmethod
    def _restart_messenger(messenger) -> bool:
        """
        Restart messenger using available methods.

        WHY: Separate method selection to avoid nested control flow
        RESPONSIBILITY: Try different restart strategies with guard clauses
        PATTERNS: Guard clauses for early returns
        """
        # Try restart method
        if hasattr(messenger, "restart"):
            logger.info("Calling messenger.restart()...")
            messenger.restart()
            logger.info("Messenger restarted successfully")
            return True

        # Try reconnect method
        if hasattr(messenger, "reconnect"):
            logger.info("Calling messenger.reconnect()...")
            messenger.reconnect()
            logger.info("Messenger reconnected successfully")
            return True

        # Try disconnect/connect pair
        if hasattr(messenger, "disconnect") and hasattr(messenger, "connect"):
            logger.info("Disconnecting and reconnecting messenger...")
            messenger.disconnect()
            messenger.connect()
            logger.info("Messenger restarted successfully")
            return True

        # No supported method found
        logger.error(
            "Messenger instance does not have supported restart methods "
            "(restart, reconnect, or disconnect/connect)"
        )
        return False
