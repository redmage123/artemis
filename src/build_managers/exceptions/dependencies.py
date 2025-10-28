#!/usr/bin/env python3
"""
Build System Dependency Exceptions

WHY: Separates dependency management errors from other build failures,
     enabling targeted dependency resolution and retry strategies.

RESPONSIBILITY: Define exceptions for dependency installation and resolution
                failures (package not found, version conflicts, network issues).

PATTERNS:
- Exception Hierarchy: Specialized exceptions for install vs resolution failures
- Package Tracking: Captures package names, versions, and conflict information
- Resolution Strategy: Different errors suggest different resolution approaches

Design Philosophy:
- Installation errors (missing package) are different from resolution errors (conflicts)
- Version conflicts need different handling than network failures
- Rich context enables automated dependency resolution strategies
- Package metadata preserved for troubleshooting and retries
"""

from typing import Dict, Any, Optional, List
from build_managers.exceptions.base import BuildSystemError, CONTEXT_BUILD_SYSTEM


class DependencyInstallError(BuildSystemError):
    """
    Error installing dependency package.

    WHY: Distinguishes package installation failures from resolution conflicts,
         enabling retry strategies for transient failures (network) vs permanent
         failures (package doesn't exist).

    RESPONSIBILITY: Signal that dependency installation failed due to package
                   not found, network issues, permission problems, or registry
                   unavailability.

    PATTERNS:
    - Package Context: Captures package name, version, registry
    - Failure Reason: Distinguishes network vs not found vs permission
    - Retry Guidance: Suggests whether retry is appropriate

    Example:
        >>> raise DependencyInstallError(
        ...     "Failed to install package 'react@99.0.0'",
        ...     context={
        ...         'build_system': 'npm',
        ...         'package': 'react',
        ...         'version': '99.0.0',
        ...         'reason': 'No matching version found',
        ...         'registry': 'https://registry.npmjs.org',
        ...         'suggested_versions': ['18.2.0', '17.0.2'],
        ...         'retryable': False
        ...     }
        ... )

    Common Context Keys:
        - build_system: Name of the build system (npm, maven, pip, cargo)
        - package: Package name that failed to install
        - version: Requested version
        - reason: Failure reason (not found, network, permission)
        - registry: Package registry URL
        - suggested_versions: List of available versions if applicable
        - retryable: Boolean indicating if retry might succeed
        - network_error: Network error details if applicable
    """

    def get_package(self) -> Optional[str]:
        """
        Get package name that failed to install.

        WHY: Functional accessor for package name without exposing context.

        Returns:
            Package name or None

        Example:
            >>> error.get_package()
            'react'
        """
        return self.get_context_value('package')

    def get_version(self) -> Optional[str]:
        """
        Get requested version.

        WHY: Version information helps determine resolution strategy.

        Returns:
            Version string or None

        Example:
            >>> error.get_version()
            '99.0.0'
        """
        return self.get_context_value('version')

    def get_suggested_versions(self) -> List[str]:
        """
        Get list of available versions.

        WHY: Enables automated version selection or user guidance.

        Returns:
            List of available version strings (empty if none)

        Example:
            >>> error.get_suggested_versions()
            ['18.2.0', '17.0.2', '16.14.0']
        """
        return self.get_context_value('suggested_versions', [])

    def is_retryable(self) -> bool:
        """
        Check if retry might succeed.

        WHY: Guides retry strategy (network failures are retryable,
             "package not found" is not).

        Returns:
            True if retry might succeed, False otherwise

        Example:
            >>> error.is_retryable()
            False  # Package doesn't exist, retry won't help
        """
        return self.get_context_value('retryable', False)

    def get_reason(self) -> Optional[str]:
        """
        Get failure reason.

        WHY: Reason categorization enables targeted error handling.

        Returns:
            Failure reason string or None

        Example:
            >>> error.get_reason()
            'No matching version found'
        """
        return self.get_context_value('reason')


class DependencyResolutionError(BuildSystemError):
    """
    Dependency resolution failed.

    WHY: Distinguishes version conflicts and transitive dependency issues
         from installation failures, enabling dependency graph analysis
         and conflict resolution strategies.

    RESPONSIBILITY: Signal that build system cannot resolve dependencies
                   due to version conflicts, incompatible constraints, or
                   missing transitive dependencies.

    PATTERNS:
    - Conflict Detection: Captures conflicting version requirements
    - Dependency Graph: Tracks which packages require conflicting versions
    - Resolution Strategies: Context suggests possible resolutions

    Example:
        >>> raise DependencyResolutionError(
        ...     "Version conflict for 'jackson-databind'",
        ...     context={
        ...         'build_system': 'maven',
        ...         'package': 'jackson-databind',
        ...         'conflicting_versions': ['2.12.0', '2.15.0'],
        ...         'required_by': {
        ...             '2.12.0': ['spring-boot-starter-web:2.5.0'],
        ...             '2.15.0': ['spring-cloud-starter:3.1.0']
        ...         },
        ...         'resolution_strategy': 'force_version',
        ...         'suggested_resolution': 'Use version 2.15.0 (highest)'
        ...     }
        ... )

    Common Context Keys:
        - build_system: Name of the build system
        - package: Package with version conflict
        - conflicting_versions: List of conflicting version requirements
        - required_by: Dictionary mapping versions to requiring packages
        - resolution_strategy: Suggested strategy (force_version, exclude, etc.)
        - suggested_resolution: Specific resolution recommendation
        - dependency_tree: Full dependency tree if available
    """

    def get_conflicting_versions(self) -> List[str]:
        """
        Get list of conflicting versions.

        WHY: Version list enables automated resolution strategy selection.

        Returns:
            List of conflicting version strings (empty if none)

        Example:
            >>> error.get_conflicting_versions()
            ['2.12.0', '2.15.0']
        """
        return self.get_context_value('conflicting_versions', [])

    def get_required_by(self) -> Dict[str, List[str]]:
        """
        Get dependency graph showing which packages require which versions.

        WHY: Dependency graph enables root cause analysis of conflicts.

        Returns:
            Dictionary mapping versions to list of requiring packages

        Example:
            >>> error.get_required_by()
            {'2.12.0': ['spring-boot-starter-web:2.5.0'],
             '2.15.0': ['spring-cloud-starter:3.1.0']}
        """
        return self.get_context_value('required_by', {})

    def get_suggested_resolution(self) -> Optional[str]:
        """
        Get suggested resolution strategy.

        WHY: Provides actionable guidance for resolving conflict.

        Returns:
            Resolution suggestion or None

        Example:
            >>> error.get_suggested_resolution()
            'Use version 2.15.0 (highest)'
        """
        return self.get_context_value('suggested_resolution')

    def get_highest_version(self) -> Optional[str]:
        """
        Get highest conflicting version.

        WHY: Common resolution strategy is to use highest compatible version.

        PERFORMANCE: O(n) where n is number of versions (uses max with key)

        Returns:
            Highest version string or None

        Example:
            >>> error.get_highest_version()
            '2.15.0'
        """
        versions = self.get_conflicting_versions()

        # Guard clause: Return None if no versions
        if not versions:
            return None

        # Functional approach: Use max() instead of loop
        # Note: This does lexicographic comparison, not semantic versioning
        # For production, use packaging.version.Version for proper comparison
        return max(versions)


# Module-level constants for dependency context keys (DRY principle)
CONTEXT_PACKAGE = "package"
CONTEXT_VERSION = "version"
CONTEXT_REASON = "reason"
CONTEXT_REGISTRY = "registry"
CONTEXT_SUGGESTED_VERSIONS = "suggested_versions"
CONTEXT_RETRYABLE = "retryable"
CONTEXT_NETWORK_ERROR = "network_error"
CONTEXT_CONFLICTING_VERSIONS = "conflicting_versions"
CONTEXT_REQUIRED_BY = "required_by"
CONTEXT_RESOLUTION_STRATEGY = "resolution_strategy"
CONTEXT_SUGGESTED_RESOLUTION = "suggested_resolution"
CONTEXT_DEPENDENCY_TREE = "dependency_tree"

# Common dependency failure reasons (constants for DRY)
REASON_NOT_FOUND = "package_not_found"
REASON_NETWORK = "network_error"
REASON_PERMISSION = "permission_denied"
REASON_VERSION_CONFLICT = "version_conflict"
REASON_CHECKSUM_FAILED = "checksum_verification_failed"
REASON_REGISTRY_UNAVAILABLE = "registry_unavailable"
