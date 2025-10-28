#!/usr/bin/env python3
"""
Package: build_managers.universal

WHY: Universal build system orchestration for multi-language projects. Provides
     unified interface for detecting, configuring, and executing builds across
     all supported build systems.

RESPONSIBILITY:
- Orchestrate builds across multiple languages and build systems
- Factory for creating appropriate build manager instances
- Unified build/test interface regardless of underlying build system

PATTERNS:
- Facade Pattern: Simplified interface over complex build tool ecosystem
- Factory Pattern: Create appropriate build managers dynamically
- Adapter Pattern: Adapt different build systems to common interface

USAGE:
    from build_managers.universal import UniversalBuildSystem

    ubs = UniversalBuildSystem(project_dir="/path/to/project")

    # Auto-detect and build
    result = ubs.build()

    # Run tests
    test_result = ubs.test()

    # Get build manager for specific system
    maven_manager = ubs.get_build_manager(BuildSystem.MAVEN)
"""

from build_managers.universal.orchestrator import UniversalBuildSystem

__all__ = ['UniversalBuildSystem']
