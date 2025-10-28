#!/usr/bin/env python3
"""
WHY: Track and persist git operations for audit and debugging
RESPONSIBILITY: Log operations, maintain history, and generate reports
PATTERNS: Single Responsibility Principle, repository pattern
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import asdict

from artemis_logger import ArtemisLogger

from .models import GitOperation
from .config import RepositoryConfig


class OperationsLogger:
    """
    WHY: Maintain audit trail of all git operations
    RESPONSIBILITY: Log operations and generate summaries
    PATTERNS: Repository pattern for data persistence
    """

    def __init__(
        self,
        logger: ArtemisLogger,
        repo_config: Optional[RepositoryConfig] = None
    ):
        """
        WHY: Initialize logger with dependencies
        RESPONSIBILITY: Set up logging infrastructure
        """
        self.logger = logger
        self.repo_config = repo_config
        self.operations_history: List[GitOperation] = []

    def log_operation(
        self,
        operation_type: str,
        status: str,
        details: Dict,
        error: Optional[str] = None
    ) -> None:
        """
        WHY: Record individual git operation
        RESPONSIBILITY: Create and store operation record
        PATTERNS: Single Responsibility Principle
        """
        operation = GitOperation(
            operation_type=operation_type,
            timestamp=datetime.utcnow().isoformat() + 'Z',
            status=status,
            details=details,
            error=error
        )
        self.operations_history.append(operation)

    def get_operations_summary(self) -> Dict:
        """
        WHY: Provide analytics on git operations
        RESPONSIBILITY: Calculate statistics and format history
        PATTERNS: Aggregation pattern
        """
        total = len(self.operations_history)
        successful = len([op for op in self.operations_history if op.status == 'success'])
        failed = len([op for op in self.operations_history if op.status == 'failed'])

        return {
            'total_operations': total,
            'successful': successful,
            'failed': failed,
            'success_rate': f"{(successful/total*100):.1f}%" if total > 0 else "0%",
            'operations': [asdict(op) for op in self.operations_history]
        }

    def save_operations_log(self, output_path: Optional[str] = None) -> str:
        """
        WHY: Persist operations log for later analysis
        RESPONSIBILITY: Write operations to JSON file
        PATTERNS: Guard clauses, path handling
        """
        # Guard: Generate default path if not provided
        if not output_path:
            output_path = self._generate_log_path()

        summary = self.get_operations_summary()
        summary['repository'] = self.repo_config.to_dict() if self.repo_config else None

        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f"Operations log saved: {output_path}")
        return str(output_path)

    def _generate_log_path(self) -> Path:
        """
        WHY: Create consistent log file paths
        RESPONSIBILITY: Generate timestamped log filename
        PATTERNS: Single Responsibility Principle
        """
        git_ops_dir = os.getenv("ARTEMIS_GIT_OPS_DIR", "../.artemis_data/git_operations")
        git_ops_dir = Path(git_ops_dir)
        git_ops_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return git_ops_dir / f"git_agent_log_{timestamp}.json"

    def clear_history(self) -> None:
        """
        WHY: Reset operations history for new sessions
        RESPONSIBILITY: Clear stored operations
        """
        self.operations_history = []

    def get_operations_by_type(self, operation_type: str) -> List[GitOperation]:
        """
        WHY: Filter operations for specific analysis
        RESPONSIBILITY: Return operations matching type
        PATTERNS: Filter pattern
        """
        return [op for op in self.operations_history if op.operation_type == operation_type]

    def get_failed_operations(self) -> List[GitOperation]:
        """
        WHY: Identify failed operations for troubleshooting
        RESPONSIBILITY: Return all failed operations
        PATTERNS: Filter pattern
        """
        return [op for op in self.operations_history if op.status == 'failed']
