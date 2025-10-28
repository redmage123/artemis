#!/usr/bin/env python3
"""
.NET Framework Detector

WHY: Identify .NET runtime versions and capabilities for build configuration.
RESPONSIBILITY: Detect installed SDKs, determine framework compatibility.
PATTERNS: Strategy pattern for version detection, Guard clauses.

Part of: managers.build_managers.dotnet
Dependencies: models
"""

import re
from pathlib import Path
from typing import Optional, List, Dict, Callable, Any

from managers.build_managers.dotnet.models import TargetFramework


class FrameworkDetector:
    """
    Detector for .NET framework versions and SDK capabilities.

    WHY: Enable automatic framework selection and validation.
    RESPONSIBILITY: Query dotnet SDK and parse version information.
    PATTERNS: Strategy pattern, Information Expert.
    """

    # Dispatch table for framework family detection
    FRAMEWORK_FAMILIES: Dict[str, List[str]] = {
        "net_core": ["net5.0", "net6.0", "net7.0", "net8.0"],
        "net_standard": ["netstandard2.0", "netstandard2.1"],
        "net_framework": ["net48", "net472", "net471", "net47", "net462", "net461"]
    }

    def __init__(
        self,
        execute_command: Callable,
        logger: Any
    ):
        """
        Initialize framework detector.

        WHY: Dependency injection for command execution.

        Args:
            execute_command: Command execution function
            logger: Logger instance
        """
        self._execute_command = execute_command
        self.logger = logger

    def get_installed_sdks(self) -> List[str]:
        """
        List all installed .NET SDKs.

        WHY: Determine available build targets.

        Returns:
            List of SDK version strings

        Example output:
            ["6.0.100", "7.0.203", "8.0.100"]
        """
        try:
            result = self._execute_command(
                ["dotnet", "--list-sdks"],
                timeout=10
            )

            if not result.success:
                return []

            sdks = []
            for line in result.output.strip().split('\n'):
                # Format: "8.0.100 [/usr/share/dotnet/sdk]"
                match = re.match(r'^(\S+)\s+\[', line)
                if match:
                    sdks.append(match.group(1))

            return sdks

        except Exception as e:
            self.logger.warning(f"Failed to list SDKs: {e}")
            return []

    def get_installed_runtimes(self) -> Dict[str, List[str]]:
        """
        List all installed .NET runtimes by type.

        WHY: Determine what can be executed on this machine.

        Returns:
            Dictionary mapping runtime type to version list

        Example:
            {
                "Microsoft.NETCore.App": ["6.0.15", "8.0.0"],
                "Microsoft.AspNetCore.App": ["6.0.15", "8.0.0"]
            }
        """
        try:
            result = self._execute_command(
                ["dotnet", "--list-runtimes"],
                timeout=10
            )

            if not result.success:
                return {}

            runtimes: Dict[str, List[str]] = {}

            for line in result.output.strip().split('\n'):
                # Format: "Microsoft.NETCore.App 8.0.0 [/usr/share/dotnet/shared/Microsoft.NETCore.App]"
                match = re.match(r'^(\S+)\s+(\S+)\s+\[', line)
                if not match:
                    continue

                runtime_type = match.group(1)
                version = match.group(2)

                if runtime_type not in runtimes:
                    runtimes[runtime_type] = []

                runtimes[runtime_type].append(version)

            return runtimes

        except Exception as e:
            self.logger.warning(f"Failed to list runtimes: {e}")
            return {}

    def detect_framework_family(self, framework: str) -> Optional[str]:
        """
        Determine framework family from target framework moniker.

        WHY: Enable framework-specific build logic.

        Args:
            framework: Target framework moniker (e.g., "net8.0")

        Returns:
            Framework family ("net_core", "net_standard", "net_framework") or None

        Guards:
            - framework must not be empty
        """
        if not framework:
            return None

        framework_lower = framework.lower()

        for family, patterns in self.FRAMEWORK_FAMILIES.items():
            if any(pattern in framework_lower for pattern in patterns):
                return family

        return None

    def is_framework_supported(self, framework: str) -> bool:
        """
        Check if target framework is supported by installed SDKs.

        WHY: Validate build configuration before attempting build.

        Args:
            framework: Target framework moniker

        Returns:
            True if framework is supported

        Guards:
            - framework must not be empty
        """
        if not framework:
            return False

        sdks = self.get_installed_sdks()

        if not sdks:
            self.logger.warning("No SDKs found, cannot validate framework support")
            return False

        # Extract major version from framework (e.g., "net8.0" -> "8")
        version_match = re.search(r'net(\d+)', framework.lower())

        if not version_match:
            return False

        target_version = int(version_match.group(1))

        # Check if any SDK supports this version
        for sdk in sdks:
            sdk_version_match = re.match(r'^(\d+)', sdk)

            if not sdk_version_match:
                continue

            sdk_major = int(sdk_version_match.group(1))

            if sdk_major >= target_version:
                return True

        return False

    @staticmethod
    def normalize_framework_name(framework: str) -> str:
        """
        Normalize framework name to standard format.

        WHY: Handle various framework name formats consistently.

        Args:
            framework: Framework name in any format

        Returns:
            Normalized framework name

        Example:
            ".NET 8.0" -> "net8.0"
            "netcoreapp3.1" -> "net3.1"
        """
        if not framework:
            return ""

        framework_lower = framework.lower().strip()

        # Remove common prefixes
        framework_lower = framework_lower.replace(".net ", "net")
        framework_lower = framework_lower.replace("netcoreapp", "net")
        framework_lower = framework_lower.replace(" ", "")

        return framework_lower


__all__ = ["FrameworkDetector"]
