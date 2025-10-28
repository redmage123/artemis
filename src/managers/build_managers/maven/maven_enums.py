#!/usr/bin/env python3
"""
Module: Maven Enumerations

WHY: Centralized type-safe enumeration definitions for Maven build system.
RESPONSIBILITY: Define Maven lifecycle phases, scopes, and other enum types.
PATTERNS: Enum pattern for type safety and IDE autocomplete support.

Dependencies: None (pure enum definitions)
"""

from enum import Enum


class MavenPhase(Enum):
    """
    Maven build lifecycle phases.

    WHY: Type-safe representation prevents typos and provides IDE autocomplete.
         Maven phases execute in a specific order - running 'package' automatically
         runs validate, compile, and test first.

    RESPONSIBILITY: Define standard Maven lifecycle phases.

    Phase Execution Order:
    - VALIDATE: Check project structure is correct
    - COMPILE: Compile source code to bytecode
    - TEST: Run unit tests (compiled test code)
    - PACKAGE: Package into distributable format (JAR/WAR)
    - VERIFY: Run integration tests and quality checks
    - INSTALL: Install to local Maven repository (~/.m2/repository)
    - DEPLOY: Deploy to remote repository for sharing

    Special Phases:
    - CLEAN: Delete target/ directory (separate lifecycle)
    - SITE: Generate project documentation website

    PATTERNS: Enum pattern for compile-time type checking.
    """
    VALIDATE = "validate"
    COMPILE = "compile"
    TEST = "test"
    PACKAGE = "package"
    VERIFY = "verify"
    INSTALL = "install"
    DEPLOY = "deploy"
    CLEAN = "clean"
    SITE = "site"


class MavenScope(Enum):
    """
    Maven dependency scopes.

    WHY: Dependencies have different classpaths based on scope (compile, test, runtime).
    RESPONSIBILITY: Define valid Maven dependency scopes.

    Scope Meanings:
    - COMPILE: Available in all classpaths (default)
    - PROVIDED: Available at compile time but not runtime (e.g., servlet-api)
    - RUNTIME: Not needed for compilation but needed at runtime
    - TEST: Only available for test compilation and execution
    - SYSTEM: Similar to PROVIDED but must explicitly provide JAR path
    - IMPORT: Only used with dependencyManagement in POM (not transitive)

    PATTERNS: Enum pattern for type safety.
    """
    COMPILE = "compile"
    PROVIDED = "provided"
    RUNTIME = "runtime"
    TEST = "test"
    SYSTEM = "system"
    IMPORT = "import"
