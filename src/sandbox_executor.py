#!/usr/bin/env python3
"""
Sandbox Executor - Backward Compatibility Wrapper

DEPRECATED: This module is deprecated. Use security.sandbox package instead.

This wrapper provides backward compatibility for existing code.
All functionality has been moved to the modular security.sandbox package.

Migration guide:
    Old: from sandbox_executor import SandboxExecutor, SandboxConfig
    New: from security.sandbox import SandboxExecutor, SandboxConfig

The modular package provides:
    - security.sandbox.models - Data models
    - security.sandbox.validator - Security validation
    - security.sandbox.resource_limiter - Resource limits
    - security.sandbox.isolation_manager - Process isolation
    - security.sandbox.executor_core - Main executor
"""

import warnings
from security.sandbox import (
    SandboxConfig,
    ExecutionResult,
    SecurityScanResult,
    SecurityValidator,
    SecurityScanner,
    ResourceLimiter,
    DockerResourceLimiter,
    temporary_limits,
    IsolationBackend,
    SubprocessIsolation,
    DockerIsolation,
    IsolationManager,
    SubprocessSandbox,
    DockerSandbox,
    SandboxExecutor,
)

# Issue deprecation warning
warnings.warn(
    "sandbox_executor module is deprecated. Use security.sandbox package instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = [
    "SandboxExecutor",
    "SandboxConfig",
    "ExecutionResult",
    "SecurityScanResult",
    "SecurityValidator",
    "SecurityScanner",
    "ResourceLimiter",
    "DockerResourceLimiter",
    "temporary_limits",
    "IsolationBackend",
    "SubprocessIsolation",
    "DockerIsolation",
    "IsolationManager",
    "SubprocessSandbox",
    "DockerSandbox",
]


if __name__ == "__main__":
    """Example usage and testing"""
    print("Sandbox Executor - Example Usage")
    print("=" * 70)
    print("NOTE: Using backward compatibility wrapper")
    print("Consider migrating to: from security.sandbox import SandboxExecutor")
    print("=" * 70 + "\n")

    # Create executor
    config = SandboxConfig(
        max_cpu_time=10,  # 10 seconds CPU
        max_memory_mb=256,  # 256 MB
        timeout=15  # 15 seconds overall
    )

    executor = SandboxExecutor(config)
    print(f"Using backend: {executor.backend_name}\n")

    # Test 1: Safe code
    print("1. Executing safe code...")
    safe_code = """
print("Hello from sandbox!")
import math
print(f"Pi = {math.pi}")
"""

    result = executor.execute_python_code(safe_code)
    print(f"   Success: {result.success}")
    print(f"   Output: {result.stdout.strip()}")
    print(f"   Time: {result.execution_time:.2f}s")

    # Test 2: Security scan
    print("\n2. Testing security scan...")
    unsafe_code = """
import os
os.system("ls /")
"""

    result = executor.execute_python_code(unsafe_code, scan_security=True)
    print(f"   Success: {result.success}")
    print(f"   Killed: {result.killed}")
    print(f"   Reason: {result.kill_reason}")

    # Test 3: Timeout
    print("\n3. Testing timeout...")
    timeout_code = """
import time
time.sleep(20)  # Will timeout
"""

    result = executor.execute_python_code(timeout_code, scan_security=False)
    print(f"   Success: {result.success}")
    print(f"   Killed: {result.killed}")
    print(f"   Reason: {result.kill_reason}")

    print("\n" + "=" * 70)
    print("✅ Sandbox executor working correctly!")
