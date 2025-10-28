#!/usr/bin/env python3
"""
WHY: Core sandbox executor orchestrating security validation and isolated execution.

RESPONSIBILITY:
    - Orchestrate security scanning and code execution
    - Manage temporary file creation for code execution
    - Provide high-level API for sandboxed execution
    - Coordinate validator and isolation manager components
    - Handle both code strings and file execution

PATTERNS:
    - Facade pattern for simplified API
    - Guard clauses for validation checks
    - Context managers for resource cleanup
    - Composition of validator and isolation components
"""

import tempfile
from pathlib import Path
from typing import Optional, List, Dict, Any
from .models import SandboxConfig, ExecutionResult
from .validator import SecurityValidator
from .isolation_manager import IsolationManager


class SandboxExecutor:
    """
    Main sandbox executor for secure code execution.

    Provides high-level API for executing Python code with security scanning
    and resource isolation. Automatically selects best isolation backend.
    """

    def __init__(
        self,
        config: Optional[SandboxConfig] = None,
        prefer_docker: bool = False
    ):
        """
        Initialize sandbox executor.

        Args:
            config: Sandbox configuration (uses defaults if None)
            prefer_docker: Prefer Docker isolation if available
        """
        self.config = config or SandboxConfig()
        self.validator = SecurityValidator()
        self.isolation_manager = IsolationManager(self.config, prefer_docker)
        self.backend_name = self.isolation_manager.backend_name

    def execute_python_code(
        self,
        code: str,
        scan_security: bool = True,
        allow_risky: bool = False
    ) -> ExecutionResult:
        """
        Execute Python code string in sandbox.

        Args:
            code: Python code to execute
            scan_security: Perform security scan before execution
            allow_risky: Allow medium-risk code to execute

        Returns:
            ExecutionResult with execution details
        """
        # Guard: Validate empty code
        if not code or not code.strip():
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr="Empty code provided",
                execution_time=0.0,
                killed=True,
                kill_reason="Empty code"
            )

        # Security scan if requested
        if scan_security:
            scan_result = self._perform_security_scan(code, allow_risky)
            # Guard: Return early if scan failed
            if scan_result is not None:
                return scan_result

        # Execute code via temporary file
        return self._execute_code_from_temp_file(code)

    def execute_python_file(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        scan_security: bool = True,
        allow_risky: bool = False
    ) -> ExecutionResult:
        """
        Execute Python file in sandbox.

        Args:
            script_path: Path to Python script
            args: Command-line arguments for script
            scan_security: Perform security scan before execution
            allow_risky: Allow medium-risk code to execute

        Returns:
            ExecutionResult with execution details
        """
        # Guard: Check file exists
        script_file = Path(script_path)
        if not script_file.exists():
            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Script not found: {script_path}",
                execution_time=0.0,
                killed=True,
                kill_reason="Script not found"
            )

        # Security scan if requested
        if scan_security:
            code = self._read_file_safe(script_path)
            # Guard: Return early if read failed
            if code is None:
                return ExecutionResult(
                    success=False,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Failed to read script: {script_path}",
                    execution_time=0.0,
                    killed=True,
                    kill_reason="Failed to read script"
                )

            scan_result = self._perform_security_scan(code, allow_risky)
            # Guard: Return early if scan failed
            if scan_result is not None:
                return scan_result

        # Execute file directly
        return self.isolation_manager.execute_python(script_path, args=args)

    def _perform_security_scan(
        self,
        code: str,
        allow_risky: bool
    ) -> Optional[ExecutionResult]:
        """
        Perform security scan on code.

        Args:
            code: Python code to scan
            allow_risky: Allow medium-risk code

        Returns:
            ExecutionResult if scan failed, None if scan passed
        """
        is_safe, reason = self.validator.validate_safe(code, allow_risky=allow_risky)

        # Guard: Return None if code is safe
        if is_safe:
            return None

        # Get detailed scan results
        scan_result = self.validator.scan_code(code)

        return ExecutionResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=f"Security scan failed: {reason}\nIssues: {scan_result.issues}",
            execution_time=0.0,
            killed=True,
            kill_reason="Failed security scan"
        )

    def _execute_code_from_temp_file(self, code: str) -> ExecutionResult:
        """
        Execute code by writing to temporary file.

        Args:
            code: Python code to execute

        Returns:
            ExecutionResult with execution details
        """
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(code)
            script_path = f.name

        try:
            # Execute in sandbox
            return self.isolation_manager.execute_python(script_path)
        finally:
            # Cleanup temporary file
            Path(script_path).unlink(missing_ok=True)

    def _read_file_safe(self, file_path: str) -> Optional[str]:
        """
        Safely read file contents.

        Args:
            file_path: Path to file

        Returns:
            File contents or None if read failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None

    def get_backend_info(self) -> Dict[str, Any]:
        """
        Get information about current backend.

        Returns:
            Dictionary with backend information
        """
        return {
            "backend": self.backend_name,
            "config": {
                "max_cpu_time": self.config.max_cpu_time,
                "max_memory_mb": self.config.max_memory_mb,
                "max_file_size_mb": self.config.max_file_size_mb,
                "timeout": self.config.timeout,
                "allow_network": self.config.allow_network,
            }
        }
