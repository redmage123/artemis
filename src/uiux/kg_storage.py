#!/usr/bin/env python3
"""
WHY: Handle Knowledge Graph and RAG storage for UI/UX evaluations
RESPONSIBILITY: Store evaluation results in KG and RAG
PATTERNS: Repository pattern, Best-effort storage

This module handles persistent storage of UI/UX evaluation results.
"""

from pathlib import Path
from typing import List, Any
from .models import DeveloperEvaluation
from .ui_analyzer import UIFileAnalyzer
from rag_storage_helper import RAGStorageHelper
from knowledge_graph_factory import get_knowledge_graph


class EvaluationStorage:
    """
    WHY: Centralized storage logic for UI/UX evaluations
    RESPONSIBILITY: Store evaluations in RAG and Knowledge Graph
    PATTERNS: Repository pattern, Best-effort storage

    Benefits:
    - Isolates storage logic
    - Best-effort storage doesn't fail evaluations
    - Clean error handling
    - Reusable across evaluations
    """

    def __init__(self, rag: Any, logger: Any):
        """
        WHY: Initialize with dependencies
        RESPONSIBILITY: Set up RAG agent and logger

        Args:
            rag: RAG agent for storing evaluation results
            logger: Logger interface
        """
        self.rag = rag
        self.logger = logger

    def store_evaluation_in_rag(
        self,
        card_id: str,
        task_title: str,
        evaluation_result: DeveloperEvaluation
    ):
        """
        WHY: Store UI/UX evaluation results in RAG for future learning
        RESPONSIBILITY: Persist evaluation to RAG
        PATTERNS: Best-effort storage (no exceptions raised)

        Args:
            card_id: Task card ID
            task_title: Task title
            evaluation_result: Full evaluation results
        """
        try:
            # Create summary of key findings
            content = f"""UI/UX Evaluation for {evaluation_result.developer} - {task_title}

Evaluation Status: {evaluation_result.evaluation_status}
UX Score: {evaluation_result.ux_score}/100

Accessibility:
- WCAG AA Compliance: {evaluation_result.wcag_aa_compliance}
- Accessibility Issues: {evaluation_result.accessibility_issues}

GDPR Compliance:
- GDPR Issues: {evaluation_result.gdpr_issues}
- Compliant: {evaluation_result.gdpr_issues == 0}

This evaluation can inform future implementations to improve UX.
"""

            # Store in RAG using helper (DRY)
            RAGStorageHelper.store_stage_artifact(
                rag=self.rag,
                stage_name="uiux_evaluation",
                card_id=card_id,
                task_title=task_title,
                content=content,
                metadata={
                    "developer": evaluation_result.developer,
                    "evaluation_status": evaluation_result.evaluation_status,
                    "ux_score": evaluation_result.ux_score,
                    "accessibility_issues": evaluation_result.accessibility_issues,
                    "wcag_aa_compliance": evaluation_result.wcag_aa_compliance,
                    "ux_issues": evaluation_result.ux_issues
                }
            )

            self.logger.log(
                f"Stored UI/UX evaluation results in RAG for {evaluation_result.developer}",
                "DEBUG"
            )

        except Exception as e:
            # Best-effort: Don't fail evaluation if storage fails
            self.logger.log(f"Error storing UI/UX evaluation in RAG: {e}", "WARNING")

    def store_evaluation_in_knowledge_graph(
        self,
        card_id: str,
        developer_name: str,
        evaluation_result: DeveloperEvaluation,
        implementation_dir: str
    ):
        """
        WHY: Store UI/UX evaluation in Knowledge Graph for traceability
        RESPONSIBILITY: Link evaluation to task in KG
        PATTERNS: Best-effort storage (no exceptions raised)

        Args:
            card_id: Task card ID
            developer_name: Developer name
            evaluation_result: Full evaluation results
            implementation_dir: Implementation directory path
        """
        kg = get_knowledge_graph()

        # Guard clause: KG not available
        if not kg:
            self.logger.log("Knowledge Graph not available - skipping KG storage", "DEBUG")
            return

        try:
            self.logger.log(
                f"Storing UI/UX evaluation for {developer_name} in Knowledge Graph...",
                "DEBUG"
            )

            # Generate unique evaluation ID
            eval_id = f"{card_id}-{developer_name}-uiux-eval"

            # Find UI files in implementation directory
            impl_path = Path(implementation_dir)
            ui_files = UIFileAnalyzer.find_ui_files(impl_path)

            # Link UI files to task (limit to 20 files to avoid overload)
            files_linked = self._link_ui_files_to_task(kg, card_id, ui_files[:20])

            if files_linked > 0:
                self.logger.log(
                    f"✅ Stored UI/UX evaluation {eval_id} with {files_linked} UI file links",
                    "INFO"
                )
            else:
                self.logger.log(
                    f"✅ Stored UI/UX evaluation {eval_id} in Knowledge Graph",
                    "INFO"
                )

        except Exception as e:
            # Best-effort: Don't fail evaluation if KG storage fails
            self.logger.log(
                f"Warning: Could not store UI/UX evaluation in Knowledge Graph: {e}",
                "WARNING"
            )
            self.logger.log(f"   Exception details: {type(e).__name__}", "DEBUG")

    def _link_ui_files_to_task(
        self,
        kg: Any,
        card_id: str,
        ui_files: List[Path]
    ) -> int:
        """
        WHY: Link UI files to task in knowledge graph
        RESPONSIBILITY: Create relationships between task and UI files
        PATTERNS: Single Responsibility - only links files to task

        Args:
            kg: Knowledge graph instance
            card_id: Task card ID
            ui_files: List of UI file paths to link

        Returns:
            Number of files successfully linked
        """
        files_linked = 0

        for file_path in ui_files:
            try:
                file_path_str = str(file_path)
                file_type = UIFileAnalyzer.detect_ui_file_type(file_path_str)

                # Add file node
                kg.add_file(file_path_str, file_type)

                # Link to task
                kg.link_task_to_file(card_id, file_path_str)

                files_linked += 1

            except Exception as e:
                self.logger.log(f"   Could not link UI file {file_path}: {e}", "DEBUG")

        return files_linked
