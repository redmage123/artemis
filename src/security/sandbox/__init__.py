#!/usr/bin/env python3
"""
WHY: Unified interface for secure sandbox execution package.

RESPONSIBILITY:
    - Export public API for sandbox execution
    - Provide backward-compatible imports
    - Document package structure and usage
    - Organize components for easy access

PATTERNS:
    - Facade pattern for package-level API
    - Explicit exports via __all__
    - Clean namespace management
"""

from .models import (
    SandboxConfig,
    ExecutionResult,
    SecurityScanResult,
)
from .validator import SecurityValidator
from .resource_limiter import (
    ResourceLimiter,
    DockerResourceLimiter,
    temporary_limits,
)
from .isolation_manager import (
    IsolationBackend,
    SubprocessIsolation,
    DockerIsolation,
    IsolationManager,
)
from .executor_core import SandboxExecutor

# Legacy compatibility aliases
SecurityScanner = SecurityValidator
SubprocessSandbox = SubprocessIsolation
DockerSandbox = DockerIsolation

__all__ = [
    # Core executor
    "SandboxExecutor",

    # Models
    "SandboxConfig",
    "ExecutionResult",
    "SecurityScanResult",

    # Validator
    "SecurityValidator",
    "SecurityScanner",  # Legacy alias

    # Resource limiting
    "ResourceLimiter",
    "DockerResourceLimiter",
    "temporary_limits",

    # Isolation backends
    "IsolationBackend",
    "SubprocessIsolation",
    "DockerIsolation",
    "IsolationManager",
    "SubprocessSandbox",  # Legacy alias
    "DockerSandbox",  # Legacy alias
]

__version__ = "2.0.0"
__author__ = "Artemis Development Team"
__description__ = "Secure sandbox execution environment for Python code"
