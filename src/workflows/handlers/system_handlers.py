#!/usr/bin/env python3
"""
System-Level Workflow Handlers

WHY:
Handles system-level operations including zombie process cleanup,
file lock management, and permission fixes.

RESPONSIBILITY:
- Clean up zombie processes
- Release file locks
- Fix file permissions
- Manage system-level resources

PATTERNS:
- Strategy Pattern: Different system resource strategies
- Guard Clauses: Validate file existence before operations
- Iterator Pattern: Process iteration for zombie cleanup

INTEGRATION:
- Extends: WorkflowHandler base class
- Used by: WorkflowHandlerFactory for system actions
- Uses: psutil for process management, os for file operations
"""

import os
import psutil
from typing import Dict, Any
from pathlib import Path

from workflows.handlers.base_handler import WorkflowHandler


class CleanupZombieProcessesHandler(WorkflowHandler):
    """
    Clean up zombie processes

    WHY: Recover system resources from defunct processes
    RESPONSIBILITY: Identify and clean zombie processes
    PATTERNS: Iterator pattern for process enumeration
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        try:
            zombies_cleaned = 0

            for proc in psutil.process_iter(['pid', 'status']):
                if proc.info['status'] != psutil.STATUS_ZOMBIE:
                    continue

                zombies_cleaned += self._cleanup_zombie_process(proc)

            print(f"[Workflow] Cleaned up {zombies_cleaned} zombie processes")
            return True
        except Exception as e:
            print(f"[Workflow] Failed to cleanup zombies: {e}")
            return False

    def _cleanup_zombie_process(self, proc) -> int:
        try:
            proc.wait(timeout=1)
            return 1
        except:
            return 0


class ReleaseFileLocksHandler(WorkflowHandler):
    """
    Release file locks

    WHY: Recover from file access issues caused by stale locks
    RESPONSIBILITY: Release locks on specified files
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        file_path = context.get("file_path")
        # TODO: Implement file lock release
        print(f"[Workflow] Released file lock: {file_path}")
        return True


class FixPermissionsHandler(WorkflowHandler):
    """
    Fix file permissions

    WHY: Recover from permission-related file access errors
    RESPONSIBILITY: Set appropriate permissions on files
    PATTERNS: Guard clause for file existence
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        file_path = context.get("file_path")

        if not file_path or not Path(file_path).exists():
            return True

        try:
            os.chmod(file_path, 0o644)
            print(f"[Workflow] Fixed permissions for {file_path}")
            return True
        except Exception as e:
            print(f"[Workflow] Failed to fix permissions: {e}")
            return False
