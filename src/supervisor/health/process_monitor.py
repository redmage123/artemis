#!/usr/bin/env python3
"""
WHY: Monitor process-level health (CPU, memory, hanging detection)
RESPONSIBILITY: Track process resources, detect hanging processes, kill processes
PATTERNS: Monitor (resource tracking), Command (kill operations)
"""

import psutil
import threading
from datetime import datetime
from typing import Dict, List, Optional

from .event_types import ProcessHealth


class ProcessMonitor:
    """
    WHY: Separate process monitoring from agent health
    RESPONSIBILITY: Track process resources, detect hangs, manage process lifecycle
    PATTERNS: Monitor, Thread-safe
    """

    def __init__(self):
        """
        WHY: Initialize process monitoring
        RESPONSIBILITY: Setup process registry and statistics
        """
        self.process_registry: Dict[int, ProcessHealth] = {}
        self._process_lock = threading.Lock()
        self.stats = {
            "hangs_detected": 0,
            "processes_killed": 0,
            "zombie_processes_cleaned": 0
        }

    def register_process(
        self,
        pid: int,
        stage_name: str,
        start_time: Optional[datetime] = None
    ) -> None:
        """
        WHY: Track process for monitoring
        RESPONSIBILITY: Add process to registry
        """
        if start_time is None:
            start_time = datetime.now()

        with self._process_lock:
            self.process_registry[pid] = ProcessHealth(
                pid=pid,
                stage_name=stage_name,
                start_time=start_time,
                cpu_percent=0.0,
                memory_mb=0.0,
                status="running",
                is_hanging=False,
                is_timeout=False
            )

    def unregister_process(self, pid: int) -> None:
        """
        WHY: Clean up completed processes
        RESPONSIBILITY: Remove process from registry
        """
        with self._process_lock:
            if pid in self.process_registry:
                del self.process_registry[pid]

    def detect_hanging_processes(self) -> List[ProcessHealth]:
        """
        WHY: Find processes that are consuming CPU but not making progress
        RESPONSIBILITY: Detect hanging based on CPU and elapsed time heuristics
        PATTERNS: Guard clause (early continue), Resource threshold detection

        Heuristic: high CPU (>90%) for long time (>5 minutes) = hanging

        Returns:
            List of hanging processes
        """
        hanging = []

        with self._process_lock:
            for pid, process_health in list(self.process_registry.items()):
                if not self._check_process_hanging(pid, process_health, hanging):
                    # Process no longer exists, was removed
                    continue

        if hanging:
            self.stats["hangs_detected"] += len(hanging)

        return hanging

    def _check_process_hanging(
        self,
        pid: int,
        process_health: ProcessHealth,
        hanging: List[ProcessHealth]
    ) -> bool:
        """
        WHY: Check individual process for hanging
        RESPONSIBILITY: Evaluate process CPU and elapsed time
        PATTERNS: Guard clause (exception handling)

        Returns:
            True if process still exists, False if removed
        """
        try:
            process = psutil.Process(pid)

            cpu_percent = process.cpu_percent(interval=0.1)
            elapsed = (datetime.now() - process_health.start_time).total_seconds()

            # Heuristic: high CPU for long time = hanging
            if cpu_percent > 90 and elapsed > 300:  # 5 minutes
                process_health.is_hanging = True
                process_health.cpu_percent = cpu_percent
                hanging.append(process_health)

            return True

        except psutil.NoSuchProcess:
            # Process terminated, remove from registry
            del self.process_registry[pid]
            return False
        except Exception:
            # Other error, keep process in registry
            return True

    def kill_process(self, pid: int, force: bool = False) -> bool:
        """
        WHY: Terminate hanging or problematic processes
        RESPONSIBILITY: Send termination signal to process
        PATTERNS: Command (kill operation), Guard clause (exception handling)

        Args:
            pid: Process ID
            force: Use SIGKILL instead of SIGTERM

        Returns:
            True if killed successfully
        """
        try:
            process = psutil.Process(pid)

            if force:
                process.kill()  # SIGKILL
            else:
                process.terminate()  # SIGTERM

            self.stats["processes_killed"] += 1

            # Remove from registry
            with self._process_lock:
                if pid in self.process_registry:
                    del self.process_registry[pid]

            return True

        except Exception:
            return False

    def cleanup_zombie_processes(self) -> int:
        """
        WHY: Clean up zombie processes to prevent resource leaks
        RESPONSIBILITY: Detect and wait for zombie processes
        PATTERNS: Guard clause (exception handling)

        Returns:
            Number of zombies cleaned
        """
        cleaned = 0

        with self._process_lock:
            for pid in list(self.process_registry.keys()):
                if self._clean_zombie_if_exists(pid):
                    cleaned += 1

        if cleaned > 0:
            self.stats["zombie_processes_cleaned"] += cleaned

        return cleaned

    def _clean_zombie_if_exists(self, pid: int) -> bool:
        """
        WHY: Clean individual zombie process
        RESPONSIBILITY: Check status and wait for zombie
        PATTERNS: Guard clause

        Returns:
            True if zombie was cleaned
        """
        try:
            process = psutil.Process(pid)

            # Check if zombie
            if process.status() == psutil.STATUS_ZOMBIE:
                process.wait()  # Clean up zombie
                del self.process_registry[pid]
                return True

            return False

        except psutil.NoSuchProcess:
            # Process already gone, remove from registry
            del self.process_registry[pid]
            return False
        except Exception:
            return False

    def get_process_count(self) -> int:
        """
        WHY: Report monitored process count
        RESPONSIBILITY: Thread-safe count
        """
        with self._process_lock:
            return len(self.process_registry)

    def get_process_info(self, pid: int) -> Optional[ProcessHealth]:
        """
        WHY: Retrieve process health information
        RESPONSIBILITY: Thread-safe process info retrieval
        """
        with self._process_lock:
            return self.process_registry.get(pid)
