#!/usr/bin/env python3
"""
Dependency Management Workflow Handlers

WHY:
Handles package dependency issues including missing packages,
version conflicts, and import errors.

RESPONSIBILITY:
- Install missing dependencies
- Resolve version conflicts
- Fix import errors
- Manage package installations

PATTERNS:
- Strategy Pattern: Different dependency resolution strategies
- Guard Clauses: Validate package names before installation
- Command Builder: Construct pip install commands dynamically

INTEGRATION:
- Extends: WorkflowHandler base class
- Used by: WorkflowHandlerFactory for dependency actions
- Executes: pip for package management
"""

import subprocess
from typing import Dict, Any, List

from workflows.handlers.base_handler import WorkflowHandler


class InstallMissingDependencyHandler(WorkflowHandler):
    """
    Install missing dependency

    WHY: Recover from missing package errors automatically
    RESPONSIBILITY: Install specified package using pip
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        package = context.get("package")
        if not package:
            return False

        try:
            subprocess.run(
                ["pip", "install", package],
                check=True,
                capture_output=True,
                timeout=300
            )
            print(f"[Workflow] Installed dependency: {package}")
            return True
        except Exception as e:
            print(f"[Workflow] Failed to install {package}: {e}")
            return False


class ResolveVersionConflictHandler(WorkflowHandler):
    """
    Resolve package version conflict

    WHY: Handle incompatible package versions automatically
    RESPONSIBILITY: Install specific version or upgrade to latest
    PATTERNS: Command builder for version-specific installation
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        package = context.get("package")
        version = context.get("version")

        return self._install_package_version(package, version)

    def _install_package_version(self, package: str, version: str) -> bool:
        try:
            install_cmd = self._build_install_command(package, version)
            subprocess.run(
                install_cmd,
                check=True,
                capture_output=True,
                timeout=300
            )
            print(f"[Workflow] Resolved version conflict for {package}")
            return True
        except Exception as e:
            print(f"[Workflow] Failed to resolve version conflict: {e}")
            return False

    def _build_install_command(self, package: str, version: str) -> List[str]:
        if version:
            return ["pip", "install", f"{package}=={version}"]
        return ["pip", "install", "--upgrade", package]


class FixImportErrorHandler(WorkflowHandler):
    """
    Fix import error

    WHY: Resolve import errors by installing missing modules
    RESPONSIBILITY: Install module that failed to import
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        module_name = context.get("module")

        try:
            subprocess.run(
                ["pip", "install", module_name],
                check=True,
                capture_output=True,
                timeout=300
            )
            print(f"[Workflow] Fixed import error for {module_name}")
            return True
        except Exception as e:
            print(f"[Workflow] Failed to fix import error: {e}")
            return False
