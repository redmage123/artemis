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
import fcntl
from typing import Dict, Any
from pathlib import Path

from workflows.handlers.base_handler import WorkflowHandler
from artemis_logger import get_logger

logger = get_logger("workflow.system_handlers")


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

        if not file_path:
            logger.warning("No file path provided for lock release")
            return False

        try:
            path = Path(file_path)

            if not path.exists():
                logger.warning(f"File does not exist, no lock to release: {file_path}")
                return True

            # On Unix-like systems, file locks are typically advisory and automatically
            # released when the file descriptor is closed or process terminates.
            # However, we can attempt to release any locks held by this process.

            # Try to open and unlock the file if it's locked
            try:
                with open(file_path, 'r+') as f:
                    # Try to unlock the file (POSIX systems)
                    try:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                        logger.info(f"Released flock lock on: {file_path}")
                    except (OSError, IOError) as e:
                        # File might not have been locked with flock
                        logger.debug(f"No flock lock to release on {file_path}: {e}")

                    # Try to unlock fcntl locks (POSIX systems)
                    try:
                        fcntl.lockf(f.fileno(), fcntl.LOCK_UN)
                        logger.info(f"Released lockf lock on: {file_path}")
                    except (OSError, IOError) as e:
                        # File might not have been locked with lockf
                        logger.debug(f"No lockf lock to release on {file_path}: {e}")

                logger.info(f"File lock release completed for: {file_path}")
                return True

            except PermissionError as e:
                logger.error(f"Permission denied accessing file {file_path}: {e}")
                return False

            except IOError as e:
                logger.warning(f"Unable to open file for lock release {file_path}: {e}")
                # File might be locked by another process, log and continue
                return True

        except Exception as e:
            logger.error(f"Failed to release file lock on {file_path}: {e}")
            return False


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
