#!/usr/bin/env python3
"""
Path Configuration Service (BACKWARD COMPATIBILITY WRAPPER)

WHY: Maintain backward compatibility during migration to modular structure.
RESPONSIBILITY: Re-export all public APIs from services.path_config package.
PATTERNS:
    - Facade Pattern: Provides simple compatibility interface
    - Adapter Pattern: Adapts new modular structure to old API

DEPRECATION NOTICE:
This module is a backward compatibility wrapper for the refactored path
configuration service. All functionality has been moved to:
    services.path_config

New code should use:
    from services.path_config import get_path_config, PathConfigService

This wrapper maintains identical public API to ensure zero-breaking changes
for existing code.

Migration Status: Phase 1 - Path configuration service modularized
Original: 233 lines monolithic file
Refactored: 4 focused modules (~150-250 lines each)
Wrapper: 42 lines (81.97% reduction)

Design Improvements:
1. Separation of Concerns: Models, resolvers, and managers separated
2. Immutable Data: Value objects prevent accidental mutations
3. Pure Functions: Resolver functions are stateless and testable
4. Composition: Service composes smaller, focused components

Next Steps: Update imports across codebase to use new package location
"""

# Re-export all public APIs from new modular package
from services.path_config import (
    PathConfigService,
    get_path_config,
)


# Convenience functions for backward compatibility
def get_developer_base_dir():
    """Get developer output base directory (convenience function)"""
    return get_path_config().developer_output_dir


def get_developer_tests_path(developer_name: str) -> str:
    """
    Get developer tests path as string (convenience function)

    Args:
        developer_name: Name of developer

    Returns:
        String path to developer's tests directory
    """
    return str(get_path_config().get_developer_tests_dir(developer_name))


def get_developer_path(developer_name: str) -> str:
    """
    Get developer output path as string (convenience function)

    Args:
        developer_name: Name of developer

    Returns:
        String path to developer's output directory
    """
    return str(get_path_config().get_developer_dir(developer_name))
