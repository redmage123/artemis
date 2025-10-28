#!/usr/bin/env python3
"""
Review Storage Handlers

WHY: Handle persistent storage of review results in RAG and Knowledge Graph
RESPONSIBILITY: Store review artifacts for future learning and traceability
PATTERNS: Repository Pattern, Single Responsibility, Guard Clauses
"""

from typing import Dict, List, Optional

from artemis_stage_interface import LoggerInterface
from rag_agent import RAGAgent
from rag_storage_helper import RAGStorageHelper
from knowledge_graph_factory import get_knowledge_graph


class ReviewStorageHandler:
    """
    Handle storage of code review results.

    WHY: Separate storage logic from review execution
    RESPONSIBILITY: Persist review data to RAG and Knowledge Graph
    PATTERNS: Repository Pattern, Guard Clauses
    """

    def __init__(self, rag: RAGAgent, logger: LoggerInterface):
        """
        Initialize storage handler.

        Args:
            rag: RAG agent for storage
            logger: Logger interface
        """
        self.rag = rag
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

        WHY: Enable learning from past reviews
        RESPONSIBILITY: Format and store review in RAG
        PATTERN: Repository Pattern, Guard Clause
        """
        try:
            content = self._format_review_content(developer_name, task_title, review_result)

            RAGStorageHelper.store_stage_artifact(
                rag=self.rag,
                stage_name="code_review",
                card_id=card_id,
                task_title=task_title,
                content=content,
                metadata=self._build_review_metadata(developer_name, review_result)
            )

            self.logger.log(f"Stored review results in RAG for {developer_name}", "DEBUG")

        except Exception as e:
            self.logger.log(f"Warning: Could not store review in RAG: {e}", "WARNING")

    def _format_review_content(
        self,
        developer_name: str,
        task_title: str,
        review_result: Dict
    ) -> str:
        """
        Format review content for RAG storage.

        WHY: Consistent formatting for RAG queries
        PATTERN: Formatter Pattern
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

    def _build_review_metadata(self, developer_name: str, review_result: Dict) -> Dict:
        """
        Build metadata dictionary for review storage.

        WHY: Structured metadata for queries and filtering
        PATTERN: Builder Pattern
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

    def store_review_in_knowledge_graph(
        self,
        card_id: str,
        developer_name: str,
        review_result: Dict,
        implementation_dir: str
    ) -> None:
        """
        Store code review results in Knowledge Graph for traceability.

        WHY: Enable traceability between tasks, reviews, and files
        RESPONSIBILITY: Create nodes and relationships in KG
        PATTERN: Repository Pattern, Guard Clauses
        """
        kg = get_knowledge_graph()

        if not kg:
            self.logger.log("Knowledge Graph not available - skipping KG storage", "DEBUG")
            return

        try:
            self._add_review_to_knowledge_graph(kg, card_id, developer_name, review_result)
        except Exception as e:
            self.logger.log(f"Warning: Could not store review in Knowledge Graph: {e}", "WARNING")
            self.logger.log(f"   Exception details: {type(e).__name__}", "DEBUG")

    def _add_review_to_knowledge_graph(
        self,
        kg,
        card_id: str,
        developer_name: str,
        review_result: Dict
    ) -> None:
        """
        Add code review and file links to knowledge graph.

        WHY: Separate KG operations for testability
        PATTERN: Single Responsibility
        """
        self.logger.log(f"Storing code review for {developer_name} in Knowledge Graph...", "DEBUG")

        # Generate unique review ID
        review_id = f"{card_id}-{developer_name}-review"

        # Add code review node
        kg.add_code_review(
            review_id=review_id,
            card_id=card_id,
            status=review_result.get('review_status', 'UNKNOWN'),
            score=review_result.get('overall_score', 0),
            critical_issues=review_result.get('critical_issues', 0),
            high_issues=review_result.get('high_issues', 0)
        )

        # Link modified files to task
        modified_files = review_result.get('modified_files', [])

        if not modified_files:
            self.logger.log(f"✅ Stored code review {review_id} in Knowledge Graph", "INFO")
            return

        self._link_modified_files_to_task(kg, card_id, modified_files)
        self.logger.log(f"✅ Stored code review {review_id} with {len(modified_files)} file links", "INFO")

    def _link_modified_files_to_task(self, kg, card_id: str, modified_files: List) -> None:
        """
        Link modified files to task in knowledge graph.

        WHY: Extract file linking for clarity
        PATTERN: Iterator Pattern, Guard Clause
        """
        for file_path in modified_files[:10]:  # Limit to 10 files
            try:
                file_path_str = str(file_path)
                file_type = FileTypeDetector.detect_file_type(file_path_str)
                kg.add_file(file_path_str, file_type)
                kg.link_task_to_file(card_id, file_path_str)
            except Exception as e:
                self.logger.log(f"   Could not link file {file_path}: {e}", "DEBUG")


class FileTypeDetector:
    """
    Detect file types from file paths.

    WHY: Separate file type detection logic
    RESPONSIBILITY: Map file extensions to types
    PATTERNS: Strategy Pattern, Lookup Table
    """

    # Extension to file type mapping
    EXTENSION_MAP = {
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

    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """
        Detect file type from path using extension mapping.

        WHY: O(1) lookup vs O(n) sequential checks
        RESPONSIBILITY: Map extension to type
        PATTERN: Lookup table (dispatch table)

        Args:
            file_path: Path to file

        Returns:
            File type string or 'unknown'
        """
        for ext, file_type in FileTypeDetector.EXTENSION_MAP.items():
            if file_path.endswith(ext):
                return file_type

        return 'unknown'
