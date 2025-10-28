#!/usr/bin/env python3
"""
WHY: Resource limit management for sandboxed code execution.

RESPONSIBILITY:
    - Set CPU time limits for processes
    - Set memory limits for processes
    - Set file size limits for processes
    - Provide cross-platform resource limiting
    - Handle platform-specific resource limit APIs

PATTERNS:
    - Factory pattern for platform-specific limiters
    - Guard clauses for platform checks
    - Context manager for safe resource limit application
    - Dispatch table for resource limit types
"""

import resource
from typing import Callable, Dict, Any, Optional
from contextlib import contextmanager
from .models import SandboxConfig


class ResourceLimiter:
    """
    Manages resource limits for sandboxed execution.

    Sets CPU, memory, and file size limits on child processes
    using OS-level resource limit APIs.
    """

    # Dispatch table for resource limit setters
    LIMIT_SETTERS: Dict[str, Callable[[int], None]] = {}

    def __init__(self, config: SandboxConfig):
        """
        Initialize resource limiter.

        Args:
            config: Sandbox configuration with resource limits
        """
        self.config = config
        self._init_limit_setters()

    def _init_limit_setters(self) -> None:
        """Initialize resource limit setter dispatch table."""
        # Guard: Only initialize once
        if self.LIMIT_SETTERS:
            return

        self.LIMIT_SETTERS.update({
            "cpu": self._set_cpu_limit,
            "memory": self._set_memory_limit,
            "file_size": self._set_file_size_limit,
        })

    def set_all_limits(self) -> None:
        """
        Set all resource limits based on configuration.

        This should be called in the child process before execution.
        """
        # Guard: Check if resource module is available
        if not hasattr(resource, 'setrlimit'):
            return

        # Apply all limits
        for limit_type in self.LIMIT_SETTERS:
            setter = self.LIMIT_SETTERS[limit_type]
            setter(self.config)

    def _set_cpu_limit(self, config: SandboxConfig) -> None:
        """
        Set CPU time limit.

        Args:
            config: Sandbox configuration
        """
        # Guard: Check if RLIMIT_CPU is available
        if not hasattr(resource, 'RLIMIT_CPU'):
            return

        cpu_limit = config.max_cpu_time
        resource.setrlimit(
            resource.RLIMIT_CPU,
            (cpu_limit, cpu_limit)
        )

    def _set_memory_limit(self, config: SandboxConfig) -> None:
        """
        Set memory limit (address space).

        Args:
            config: Sandbox configuration
        """
        # Guard: Check if RLIMIT_AS is available
        if not hasattr(resource, 'RLIMIT_AS'):
            return

        memory_bytes = config.max_memory_mb * 1024 * 1024
        resource.setrlimit(
            resource.RLIMIT_AS,
            (memory_bytes, memory_bytes)
        )

    def _set_file_size_limit(self, config: SandboxConfig) -> None:
        """
        Set file size limit.

        Args:
            config: Sandbox configuration
        """
        # Guard: Check if RLIMIT_FSIZE is available
        if not hasattr(resource, 'RLIMIT_FSIZE'):
            return

        file_size_bytes = config.max_file_size_mb * 1024 * 1024
        resource.setrlimit(
            resource.RLIMIT_FSIZE,
            (file_size_bytes, file_size_bytes)
        )

    def get_preexec_fn(self) -> Callable[[], None]:
        """
        Get preexec function for subprocess.

        Returns:
            Function to call before exec in child process
        """
        def preexec() -> None:
            """Set resource limits in child process."""
            self.set_all_limits()

        return preexec


class DockerResourceLimiter:
    """
    Manages resource limits for Docker-based sandboxes.

    Translates sandbox configuration into Docker runtime parameters.
    """

    def __init__(self, config: SandboxConfig):
        """
        Initialize Docker resource limiter.

        Args:
            config: Sandbox configuration
        """
        self.config = config

    def get_docker_args(self) -> list[str]:
        """
        Get Docker command-line arguments for resource limits.

        Returns:
            List of Docker arguments
        """
        args = []

        # Memory limit
        args.append(f"--memory={self.config.max_memory_mb}m")

        # CPU limit (convert CPU seconds to CPU cores)
        # Rough approximation: CPU seconds / 60 = CPU cores
        cpu_cores = max(0.1, self.config.max_cpu_time / 60.0)
        args.append(f"--cpus={cpu_cores:.1f}")

        # Network access
        if not self.config.allow_network:
            args.append("--network=none")
        else:
            args.append("--network=bridge")

        # Read-only filesystem
        args.append("--read-only")

        # Remove container after execution
        args.append("--rm")

        return args

    def get_volume_mounts(self, script_dir: str) -> list[str]:
        """
        Get Docker volume mount arguments.

        Args:
            script_dir: Directory containing script

        Returns:
            List of volume mount arguments
        """
        args = []

        # Mount script directory as read-only
        args.append(f"--volume={script_dir}:/workspace:ro")

        # Mount allowed paths as read-write
        for allowed_path in self.config.allowed_paths:
            args.append(f"--volume={allowed_path}:/mnt/{allowed_path.replace('/', '_')}:rw")

        return args


@contextmanager
def temporary_limits(config: SandboxConfig):
    """
    Context manager for temporary resource limits.

    Args:
        config: Sandbox configuration

    Yields:
        ResourceLimiter instance
    """
    limiter = ResourceLimiter(config)

    # Guard: Save original limits (if available)
    original_limits = {}
    if hasattr(resource, 'getrlimit'):
        try:
            original_limits['cpu'] = resource.getrlimit(resource.RLIMIT_CPU)
            original_limits['memory'] = resource.getrlimit(resource.RLIMIT_AS)
            original_limits['file_size'] = resource.getrlimit(resource.RLIMIT_FSIZE)
        except Exception:
            pass  # Some platforms may not support these

    try:
        yield limiter
    finally:
        # Restore original limits (best effort)
        if hasattr(resource, 'setrlimit'):
            try:
                if 'cpu' in original_limits:
                    resource.setrlimit(resource.RLIMIT_CPU, original_limits['cpu'])
                if 'memory' in original_limits:
                    resource.setrlimit(resource.RLIMIT_AS, original_limits['memory'])
                if 'file_size' in original_limits:
                    resource.setrlimit(resource.RLIMIT_FSIZE, original_limits['file_size'])
            except Exception:
                pass  # Restoration is best-effort
