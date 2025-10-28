#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in java_ecosystem/.

All functionality has been refactored into:
- java_ecosystem/ecosystem_core.py - JavaEcosystemManager core logic
- java_ecosystem/models.py - JavaEcosystemAnalysis data models
- java_ecosystem/maven_integration.py - Maven integration
- java_ecosystem/gradle_integration.py - Gradle integration
- java_ecosystem/dependency_resolver.py - Dependency resolution
- java_ecosystem/build_coordinator.py - Build coordination
- java_ecosystem/cli/__init__.py - CLI entry point
- java_ecosystem/cli/commands.py - Command handlers
- java_ecosystem/cli/formatters.py - Output formatting
- java_ecosystem/cli/parser.py - Argument parsing

To migrate your code:
    OLD: from java_ecosystem_integration import JavaEcosystemManager
    NEW: from java_ecosystem import JavaEcosystemManager

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from java_ecosystem package
from java_ecosystem import (
    JavaEcosystemManager,
    JavaEcosystemAnalysis,
)

__all__ = [
    'JavaEcosystemManager',
    'JavaEcosystemAnalysis',
]


# CLI entry point - delegate to java_ecosystem.cli
if __name__ == "__main__":
    from java_ecosystem.cli import main
    import sys
    sys.exit(main())
