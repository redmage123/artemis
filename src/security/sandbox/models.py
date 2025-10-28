#!/usr/bin/env python3
"""
WHY: Data models for sandbox execution configuration and results.

RESPONSIBILITY:
    - Define sandbox configuration parameters
    - Define execution result structure
    - Provide immutable data containers for sandbox operations
    - Ensure type safety across sandbox components

PATTERNS:
    - Dataclass pattern for immutable data structures
    - Type hints for all fields
    - Default values for optional configuration
    - Clear separation of input (config) and output (result) models
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any


@dataclass
class SandboxConfig:
    """
    Configuration for sandbox execution environment.

    Defines resource limits and security constraints for sandboxed code execution.
    All limits are enforced at the process or container level.
    """
    max_cpu_time: int = 300  # seconds - CPU time limit
    max_memory_mb: int = 512  # MB - Memory limit
    max_file_size_mb: int = 100  # MB - File size limit
    allow_network: bool = False  # Network access allowed
    allowed_paths: Optional[List[str]] = None  # Writable filesystem paths
    timeout: int = 600  # seconds - Overall execution timeout

    def __post_init__(self) -> None:
        """Validate configuration values."""
        if self.allowed_paths is None:
            self.allowed_paths = []

        # Guard: Validate positive values
        if self.max_cpu_time <= 0:
            raise ValueError("max_cpu_time must be positive")

        if self.max_memory_mb <= 0:
            raise ValueError("max_memory_mb must be positive")

        if self.max_file_size_mb <= 0:
            raise ValueError("max_file_size_mb must be positive")

        if self.timeout <= 0:
            raise ValueError("timeout must be positive")


@dataclass
class ExecutionResult:
    """
    Result of sandbox code execution.

    Contains all information about the execution including success status,
    output, resource usage, and termination details.
    """
    success: bool  # Execution completed successfully
    exit_code: int  # Process exit code
    stdout: str  # Standard output
    stderr: str  # Standard error
    execution_time: float  # Actual execution time in seconds
    memory_used_mb: Optional[float] = None  # Peak memory usage
    killed: bool = False  # Process was killed
    kill_reason: Optional[str] = None  # Reason for termination

    def __post_init__(self) -> None:
        """Validate result values."""
        # Guard: Ensure execution_time is non-negative
        if self.execution_time < 0:
            raise ValueError("execution_time cannot be negative")

        # Guard: Ensure memory_used_mb is non-negative if provided
        if self.memory_used_mb is not None and self.memory_used_mb < 0:
            raise ValueError("memory_used_mb cannot be negative")


@dataclass
class SecurityScanResult:
    """
    Result of security scan on code before execution.

    Contains information about detected security issues and overall risk assessment.
    """
    safe: bool  # Code is safe to execute
    issues: List[dict] = field(default_factory=list)  # List of security issues found
    risk_level: str = "low"  # Overall risk: "low", "medium", "high"

    def __post_init__(self) -> None:
        """Validate scan result."""
        # Guard: Validate risk_level
        valid_levels = {"low", "medium", "high"}
        if self.risk_level not in valid_levels:
            raise ValueError(f"risk_level must be one of {valid_levels}")
