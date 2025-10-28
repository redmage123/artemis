#!/usr/bin/env python3
"""
Compile Java Ecosystem Package Modules

WHY: Validates syntax of all refactored modules before deployment.
"""

import py_compile
import sys
from pathlib import Path

def compile_module(module_path: Path) -> bool:
    """
    Compile a Python module.

    Args:
        module_path: Path to module

    Returns:
        True if compilation successful
    """
    try:
        py_compile.compile(str(module_path), doraise=True)
        print(f"✓ {module_path.name}")
        return True
    except py_compile.PyCompileError as e:
        print(f"✗ {module_path.name}: {e}")
        return False

def main():
    """Main compilation function."""
    base_dir = Path(__file__).parent / "java_ecosystem"

    modules = [
        base_dir / "__init__.py",
        base_dir / "models.py",
        base_dir / "maven_integration.py",
        base_dir / "gradle_integration.py",
        base_dir / "dependency_resolver.py",
        base_dir / "build_coordinator.py",
        base_dir / "ecosystem_core.py",
    ]

    # Also compile wrapper
    modules.append(Path(__file__).parent / "java_ecosystem_integration.py")

    print("Compiling Java Ecosystem modules...")
    print("=" * 60)

    all_success = True
    for module in modules:
        if not compile_module(module):
            all_success = False

    print("=" * 60)

    if all_success:
        print("All modules compiled successfully!")
        return 0
    else:
        print("Some modules failed to compile!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
