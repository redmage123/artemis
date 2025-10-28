#!/usr/bin/env python3
"""
Infrastructure Workflow Handlers

WHY:
Handles system resource issues like hanging processes, memory management,
disk space, network connectivity, and temporary file cleanup.

RESPONSIBILITY:
- Kill hanging processes
- Manage memory and disk space
- Handle network retries
- Clean up temporary files
- Monitor system resources

PATTERNS:
- Strategy Pattern: Each handler implements different recovery strategy
- Guard Clauses: Early returns for invalid inputs
- Single Responsibility: Each handler focuses on one infrastructure concern

INTEGRATION:
- Extends: WorkflowHandler base class
- Used by: WorkflowHandlerFactory for infrastructure actions
- Imported from: artemis_constants for retry configuration
"""

import os
import psutil
import shutil
import time
import gc
from typing import Dict, Any
from pathlib import Path

from artemis_constants import (
    MAX_RETRY_ATTEMPTS,
    DEFAULT_RETRY_INTERVAL_SECONDS,
    RETRY_BACKOFF_FACTOR
)
from workflows.handlers.base_handler import WorkflowHandler


class KillHangingProcessHandler(WorkflowHandler):
    """
    Kill hanging process

    WHY: Recover from stuck processes that block pipeline execution
    RESPONSIBILITY: Terminate unresponsive processes gracefully, then forcefully
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        pid = context.get("pid")
        if not pid:
            return False

        return self._kill_process(pid)

    def _kill_process(self, pid: int) -> bool:
        try:
            process = psutil.Process(pid)
            process.terminate()
            time.sleep(DEFAULT_RETRY_INTERVAL_SECONDS - 3)  # 2 seconds

            if process.is_running():
                process.kill()

            print(f"[Workflow] Killed hanging process {pid}")
            return True
        except Exception as e:
            print(f"[Workflow] Failed to kill process {pid}: {e}")
            return False


class IncreaseTimeoutHandler(WorkflowHandler):
    """
    Increase timeout for stage

    WHY: Adapt to longer-running operations without failing prematurely
    RESPONSIBILITY: Double current timeout and update context
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        stage_name = context.get("stage_name")
        current_timeout = context.get("timeout_seconds", 300)
        new_timeout = current_timeout * 2

        context["timeout_seconds"] = new_timeout
        print(f"[Workflow] Increased timeout for {stage_name}: {current_timeout}s → {new_timeout}s")
        return True


class FreeMemoryHandler(WorkflowHandler):
    """
    Free up memory

    WHY: Prevent out-of-memory errors by triggering garbage collection
    RESPONSIBILITY: Force Python garbage collection to reclaim memory
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        try:
            gc.collect()
            print("[Workflow] Freed memory")
            return True
        except Exception as e:
            print(f"[Workflow] Failed to free memory: {e}")
            return False


class CleanupTempFilesHandler(WorkflowHandler):
    """
    Clean up temporary files

    WHY: Recover disk space and prevent stale artifacts from interfering
    RESPONSIBILITY: Remove temporary directories for developers and ADR
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        try:
            developer_base_dir = self._get_developer_base_dir()
            temp_dirs = self._build_temp_dirs_list(developer_base_dir)

            for temp_dir in temp_dirs:
                self._cleanup_directory(temp_dir)

            return True
        except Exception as e:
            print(f"[Workflow] Failed to cleanup temp files: {e}")
            return False

    def _get_developer_base_dir(self) -> Path:
        developer_base_dir = os.getenv("ARTEMIS_DEVELOPER_DIR", "/tmp")

        if os.path.isabs(developer_base_dir):
            return Path(developer_base_dir)

        script_dir = Path(__file__).parent.resolve()
        return script_dir / developer_base_dir

    def _build_temp_dirs_list(self, developer_base_dir: Path) -> list:
        return [
            str(developer_base_dir / "developer-a"),
            str(developer_base_dir / "developer-b"),
            "/tmp/adr"  # ADR still uses /tmp (could be made configurable too)
        ]

    def _cleanup_directory(self, temp_dir: str) -> None:
        if not Path(temp_dir).exists():
            return

        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"[Workflow] Cleaned up {temp_dir}")


class CheckDiskSpaceHandler(WorkflowHandler):
    """
    Check and report disk space

    WHY: Prevent pipeline failures due to insufficient disk space
    RESPONSIBILITY: Monitor disk space and warn when critically low
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        try:
            usage = shutil.disk_usage("/")
            free_gb = usage.free / (1024**3)

            print(f"[Workflow] Disk space: {free_gb:.2f} GB free")

            if free_gb < 1:
                print("[Workflow] Low disk space!")
                return False

            return True
        except Exception as e:
            print(f"[Workflow] Failed to check disk space: {e}")
            return False


class RetryNetworkRequestHandler(WorkflowHandler):
    """
    Retry network request with exponential backoff

    WHY: Handle transient network failures gracefully
    RESPONSIBILITY: Retry network operations with increasing delays
    PATTERNS: Exponential backoff for retry strategy
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        for attempt in range(MAX_RETRY_ATTEMPTS):
            if self._attempt_network_request(attempt):
                return True

            if attempt == MAX_RETRY_ATTEMPTS - 1:
                return False

        return False

    def _attempt_network_request(self, attempt: int) -> bool:
        try:
            # TODO: Implement actual network retry
            time.sleep(RETRY_BACKOFF_FACTOR ** attempt)
            print(f"[Workflow] Network retry {attempt + 1}/{MAX_RETRY_ATTEMPTS}")
            return True
        except Exception:
            return False
