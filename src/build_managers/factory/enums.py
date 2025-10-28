#!/usr/bin/env python3
"""
WHY: Define supported build systems
RESPONSIBILITY: Centralize build system identifiers
PATTERNS: Enum (type-safe constants)

BuildSystem enum provides unified identifiers across factory.
"""

from enum import Enum


class BuildSystem(Enum):
    """
    Supported build systems.

    WHY: Type-safe identifiers prevent string typos.
    RESPONSIBILITY: Define all supported build systems.
    PATTERNS: Enum (type-safe constants).
    """

    # Java build systems
    MAVEN = "maven"
    GRADLE = "gradle"
    ANT = "ant"

    # JavaScript/TypeScript build systems
    NPM = "npm"
    YARN = "yarn"
    PNPM = "pnpm"

    # Python build systems
    PIP = "pip"
    POETRY = "poetry"
    PIPENV = "pipenv"
    CONDA = "conda"

    # C/C++ build systems
    CMAKE = "cmake"
    MAKE = "make"

    # Rust build system
    CARGO = "cargo"

    # Go build system
    GO_MOD = "go"

    # .NET build system
    DOTNET = "dotnet"

    # Ruby build system
    BUNDLER = "bundler"

    # PHP build system
    COMPOSER = "composer"

    # Infrastructure/Shell
    TERRAFORM = "terraform"
    BASH = "bash"

    # Lua build system
    LUA = "lua"
