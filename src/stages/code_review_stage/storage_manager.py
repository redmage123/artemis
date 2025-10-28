#!/usr/bin/env python3
"""
Code Review Stage - Storage Manager for RAG and Knowledge Graph

WHY: Separate storage operations from review logic for better testability and SRP.
RESPONSIBILITY: Handle all storage operations for code review results.
PATTERNS: Repository pattern for data persistence, Strategy pattern for storage types.

This module manages storage of code review results to RAG (for learning) and
Knowledge Graph (for traceability).
"""

from typing import Dict, List, Optional
from pathlib import Path

from agent_messenger import AgentMessenger
from rag_agent import RAGAgent
from knowledge_graph_factory import get_knowledge_graph
from rag_storage_helper import RAGStorageHelper


class ReviewStorageManager:
    """
    Storage manager for code review results.

    WHY: Centralize storage logic to avoid duplication and enable testing.
    RESPONSIBILITY: Store review results in RAG and Knowledge Graph.
    PATTERNS: Repository pattern, Strategy pattern for different storage backends.

    Attributes:
        rag: RAG agent for storing review results
        messenger: Agent messenger for notifications
        logger: Logger interface for debug/error logging
    """

    # File extension to type mapping (Strategy pattern)
    FILE_TYPE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'javascript',
        '.tsx': 'javascript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust',
        '.c': 'c++',
        '.cpp': 'c++',
        '.h': 'c++',
        '.hpp': 'c++',
        '.md': 'markdown',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json'
    }

    def __init__(
        self,
        rag: RAGAgent,
        messenger: AgentMessenger,
        logger: 'LoggerInterface'
    ):
        """
        Initialize storage manager.

        Args:
            rag: RAG agent for storing results
            messenger: Agent messenger for notifications
            logger: Logger interface
        """
        self.rag = rag
        self.messenger = messenger
        self.logger = logger

    def store_review_in_rag(
        self,
        card_id: str,
        task_title: str,
        developer_name: str,
        review_result: Dict
    ) -> None:
        """
        Store code review results in RAG for future learning.

        WHY: Enable learning from past reviews to improve future code generation.

        Args:
            card_id: Task card identifier
            task_title: Task title
            developer_name: Name of developer reviewed
            review_result: Complete review result dictionary
        """
        if not self.rag:
            return

        try:
            content = self._build_rag_content(
                developer_name,
                task_title,
                review_result
            )

            metadata = self._build_rag_metadata(developer_name, review_result)

            RAGStorageHelper.store_stage_artifact(
                rag=self.rag,
                stage_name="code_review",
                card_id=card_id,
                task_title=task_title,
                content=content,
                metadata=metadata
            )

            self.logger.log(
                f"Stored review results in RAG for {developer_name}",
                "DEBUG"
            )

        except Exception as e:
            self.logger.log(
                f"Warning: Could not store review in RAG: {e}",
                "WARNING"
            )

    def store_review_in_knowledge_graph(
        self,
        card_id: str,
        developer_name: str,
        review_result: Dict,
        implementation_dir: str
    ) -> None:
        """
        Store code review results in Knowledge Graph for traceability.

        WHY: Enable tracing which files were reviewed and their status.

        Args:
            card_id: Task card identifier
            developer_name: Name of developer reviewed
            review_result: Complete review result dictionary
            implementation_dir: Directory containing implementation
        """
        kg = get_knowledge_graph()
        if not kg:
            self.logger.log(
                "Knowledge Graph not available - skipping KG storage",
                "DEBUG"
            )
            return

        try:
            self._store_in_kg(kg, card_id, developer_name, review_result)
        except Exception as e:
            self.logger.log(
                f"Warning: Could not store review in Knowledge Graph: {e}",
                "WARNING"
            )
            self.logger.log(f"   Exception details: {type(e).__name__}", "DEBUG")

    def send_review_notification(
        self,
        card_id: str,
        developer_name: str,
        review_result: Dict
    ) -> None:
        """
        Send code review notification to other agents.

        WHY: Enable other agents to react to review completion.

        Args:
            card_id: Task card identifier
            developer_name: Name of developer reviewed
            review_result: Complete review result dictionary
        """
        try:
            self.messenger.send_notification(
                to_agent="all",
                card_id=card_id,
                notification_type="code_review_completed",
                data={
                    "developer": developer_name,
                    "review_status": review_result.get('review_status', 'UNKNOWN'),
                    "overall_score": review_result.get('overall_score', 0),
                    "critical_issues": review_result.get('critical_issues', 0),
                    "high_issues": review_result.get('high_issues', 0),
                    "report_file": review_result.get('report_file', '')
                }
            )

            self.messenger.update_shared_state(
                card_id=card_id,
                updates={
                    f"code_review_{developer_name}_status": review_result.get('review_status', 'UNKNOWN'),
                    f"code_review_{developer_name}_score": review_result.get('overall_score', 0),
                    "current_stage": "code_review_complete"
                }
            )

        except Exception as e:
            self.logger.log(
                f"Warning: Could not send review notification: {e}",
                "WARNING"
            )

    def _build_rag_content(
        self,
        developer_name: str,
        task_title: str,
        review_result: Dict
    ) -> str:
        """
        Build RAG storage content.

        WHY: DRY - centralize content formatting logic.

        Args:
            developer_name: Name of developer
            task_title: Task title
            review_result: Review result dictionary

        Returns:
            Formatted content string
        """
        return f"""Code Review for {developer_name} - {task_title}

Review Status: {review_result.get('review_status', 'UNKNOWN')}
Overall Score: {review_result.get('overall_score', 0)}/100

Issues Found:
- Critical: {review_result.get('critical_issues', 0)}
- High: {review_result.get('high_issues', 0)}
- Total: {review_result.get('total_issues', 0)}

This review can inform future implementations to avoid similar issues.
"""

    def _build_rag_metadata(
        self,
        developer_name: str,
        review_result: Dict
    ) -> Dict:
        """
        Build RAG storage metadata.

        WHY: DRY - centralize metadata formatting logic.

        Args:
            developer_name: Name of developer
            review_result: Review result dictionary

        Returns:
            Metadata dictionary
        """
        return {
            "developer": developer_name,
            "review_status": review_result.get('review_status', 'UNKNOWN'),
            "overall_score": review_result.get('overall_score', 0),
            "critical_issues": review_result.get('critical_issues', 0),
            "high_issues": review_result.get('high_issues', 0),
            "total_issues": review_result.get('total_issues', 0),
            "report_file": review_result.get('report_file', '')
        }

    def _store_in_kg(
        self,
        kg,
        card_id: str,
        developer_name: str,
        review_result: Dict
    ) -> None:
        """
        Store review in knowledge graph.

        WHY: Extracted to reduce nesting in public method.

        Args:
            kg: Knowledge graph instance
            card_id: Task card identifier
            developer_name: Name of developer
            review_result: Review result dictionary
        """
        self.logger.log(
            f"Storing code review for {developer_name} in Knowledge Graph...",
            "DEBUG"
        )

        review_id = f"{card_id}-{developer_name}-review"

        kg.add_code_review(
            review_id=review_id,
            card_id=card_id,
            status=review_result.get('review_status', 'UNKNOWN'),
            score=review_result.get('overall_score', 0),
            critical_issues=review_result.get('critical_issues', 0),
            high_issues=review_result.get('high_issues', 0)
        )

        modified_files = review_result.get('modified_files', [])
        if not modified_files:
            self.logger.log(
                f"✅ Stored code review {review_id} in Knowledge Graph",
                "INFO"
            )
            return

        self._link_files_to_task(kg, card_id, modified_files)
        self.logger.log(
            f"✅ Stored code review {review_id} with {len(modified_files)} file links",
            "INFO"
        )

    def _link_files_to_task(
        self,
        kg,
        card_id: str,
        modified_files: List
    ) -> None:
        """
        Link modified files to task in knowledge graph.

        WHY: Extracted to reduce nesting and improve readability.
        PERFORMANCE: Limits to 10 files to avoid overwhelming the graph.

        Args:
            kg: Knowledge graph instance
            card_id: Task card identifier
            modified_files: List of file paths
        """
        for file_path in modified_files[:10]:  # Limit to 10 files
            try:
                file_path_str = str(file_path)
                file_type = self._detect_file_type(file_path_str)
                kg.add_file(file_path_str, file_type)
                kg.link_task_to_file(card_id, file_path_str)
            except Exception as e:
                self.logger.log(
                    f"   Could not link file {file_path}: {e}",
                    "DEBUG"
                )

    def _detect_file_type(self, file_path: str) -> str:
        """
        Detect file type from path using extension mapping.

        WHY: Strategy pattern via dictionary lookup for O(1) performance.
        RESPONSIBILITY: Map file extensions to type names.
        PATTERNS: Strategy pattern - dictionary mapping instead of if/elif chain.
        PERFORMANCE: O(1) lookup vs O(n) sequential checks.

        Args:
            file_path: Path to file

        Returns:
            File type string ('python', 'javascript', etc.) or 'unknown'
        """
        # Strategy pattern: Use dictionary lookup instead of if/elif chain
        for ext, file_type in self.FILE_TYPE_MAP.items():
            if file_path.endswith(ext):
                return file_type

        return 'unknown'
