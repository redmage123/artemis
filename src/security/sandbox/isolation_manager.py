#!/usr/bin/env python3
"""
WHY: Process isolation strategies for sandboxed code execution.

RESPONSIBILITY:
    - Provide subprocess-based isolation
    - Provide Docker-based container isolation
    - Manage execution backends with automatic selection
    - Handle platform-specific isolation mechanisms
    - Execute code with proper isolation and resource limits

PATTERNS:
    - Strategy pattern for different isolation backends
    - Factory pattern for backend selection
    - Guard clauses for availability checks
    - Dispatch table for backend selection logic
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from .models import SandboxConfig, ExecutionResult
from .resource_limiter import ResourceLimiter, DockerResourceLimiter


class IsolationBackend:
    """
    Base class for isolation backends.

    Defines the interface for executing code in isolated environments.
    """

    def __init__(self, config: SandboxConfig):
        """
        Initialize isolation backend.

        Args:
            config: Sandbox configuration
        """
        self.config = config

    def is_available(self) -> bool:
        """
        Check if this backend is available.

        Returns:
            True if backend can be used
        """
        raise NotImplementedError("Subclasses must implement is_available")

    def execute_python(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        Execute Python script in isolated environment.

        Args:
            script_path: Path to Python script
            args: Command-line arguments
            env: Environment variables

        Returns:
            ExecutionResult with execution details
        """
        raise NotImplementedError("Subclasses must implement execute_python")


class SubprocessIsolation(IsolationBackend):
    """
    Subprocess-based isolation using OS resource limits.

    Provides basic process-level isolation with CPU, memory, and file limits.
    """

    def is_available(self) -> bool:
        """Check if subprocess isolation is available."""
        # Subprocess is always available
        return True

    def execute_python(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        Execute Python script using subprocess with resource limits.

        Args:
            script_path: Path to Python script
            args: Command-line arguments
            env: Environment variables

        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()

        # Build command
        cmd = ["python3", script_path]
        if args:
            cmd.extend(args)

        # Prepare environment
        if env is None:
            env = {}

        # Create resource limiter
        limiter = ResourceLimiter(self.config)
        preexec_fn = limiter.get_preexec_fn()

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.config.timeout,
                preexec_fn=preexec_fn,
                env=env,
                text=True
            )

            execution_time = time.time() - start_time

            return ExecutionResult(
                success=(result.returncode == 0),
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                killed=False
            )

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time

            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=e.stderr.decode() if e.stderr else "",
                execution_time=execution_time,
                killed=True,
                kill_reason=f"Timeout ({self.config.timeout}s)"
            )

        except Exception as e:
            execution_time = time.time() - start_time

            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                killed=True,
                kill_reason=f"Execution error: {e}"
            )


class DockerIsolation(IsolationBackend):
    """
    Docker-based isolation using containers.

    Provides full container-level isolation with filesystem, network,
    and resource isolation.
    """

    def __init__(self, config: SandboxConfig):
        """
        Initialize Docker isolation.

        Args:
            config: Sandbox configuration
        """
        super().__init__(config)
        self.image = "python:3.11-slim"

    def is_available(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def execute_python(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        Execute Python script in Docker container.

        Args:
            script_path: Path to Python script
            args: Command-line arguments
            env: Environment variables

        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()

        # Prepare paths
        script_dir = Path(script_path).parent
        script_name = Path(script_path).name

        # Build Docker command
        docker_cmd = self._build_docker_command(script_dir, script_name, args, env)

        try:
            result = subprocess.run(
                docker_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.config.timeout,
                text=True
            )

            execution_time = time.time() - start_time

            return ExecutionResult(
                success=(result.returncode == 0),
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                killed=False
            )

        except subprocess.TimeoutExpired as e:
            execution_time = time.time() - start_time

            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=e.stderr.decode() if e.stderr else "",
                execution_time=execution_time,
                killed=True,
                kill_reason=f"Timeout ({self.config.timeout}s)"
            )

        except Exception as e:
            execution_time = time.time() - start_time

            return ExecutionResult(
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                killed=True,
                kill_reason=f"Docker error: {e}"
            )

    def _build_docker_command(
        self,
        script_dir: Path,
        script_name: str,
        args: Optional[List[str]],
        env: Optional[Dict[str, str]]
    ) -> List[str]:
        """
        Build Docker command with resource limits.

        Args:
            script_dir: Directory containing script
            script_name: Script filename
            args: Command-line arguments
            env: Environment variables

        Returns:
            Docker command as list
        """
        # Start with base command
        cmd = ["docker", "run"]

        # Add resource limits
        limiter = DockerResourceLimiter(self.config)
        cmd.extend(limiter.get_docker_args())

        # Add volume mounts
        cmd.extend(limiter.get_volume_mounts(str(script_dir)))
        cmd.append("--workdir=/workspace")

        # Add environment variables
        if env:
            for key, value in env.items():
                cmd.append(f"--env={key}={value}")

        # Add image and command
        cmd.append(self.image)
        cmd.append("python3")
        cmd.append(script_name)

        # Add script arguments
        if args:
            cmd.extend(args)

        return cmd


class IsolationManager:
    """
    Manages isolation backend selection and execution.

    Automatically selects the best available isolation backend.
    """

    # Backend priority dispatch table
    BACKEND_DISPATCH: Dict[str, Callable[[SandboxConfig], IsolationBackend]] = {
        "docker": lambda config: DockerIsolation(config),
        "subprocess": lambda config: SubprocessIsolation(config),
    }

    def __init__(self, config: SandboxConfig, prefer_docker: bool = False):
        """
        Initialize isolation manager.

        Args:
            config: Sandbox configuration
            prefer_docker: Prefer Docker if available
        """
        self.config = config
        self.backend = self._select_backend(prefer_docker)
        self.backend_name = self._get_backend_name()

    def _select_backend(self, prefer_docker: bool) -> IsolationBackend:
        """
        Select best available backend.

        Args:
            prefer_docker: Prefer Docker if available

        Returns:
            Selected isolation backend
        """
        # Guard: Try Docker first if preferred
        if prefer_docker:
            docker = DockerIsolation(self.config)
            if docker.is_available():
                return docker

        # Fallback to subprocess
        return SubprocessIsolation(self.config)

    def _get_backend_name(self) -> str:
        """Get name of current backend."""
        if isinstance(self.backend, DockerIsolation):
            return "docker"
        return "subprocess"

    def execute_python(
        self,
        script_path: str,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """
        Execute Python script using selected backend.

        Args:
            script_path: Path to Python script
            args: Command-line arguments
            env: Environment variables

        Returns:
            ExecutionResult with execution details
        """
        return self.backend.execute_python(script_path, args, env)
