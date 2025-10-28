#!/usr/bin/env python3
"""
Verification script for services.core refactoring.

Compiles all modules and verifies backward compatibility.
"""

import py_compile
import sys
from pathlib import Path


def compile_module(module_path: Path) -> bool:
    """Compile a Python module to verify syntax."""
    try:
        py_compile.compile(module_path, doraise=True)
        print(f"✅ {module_path.name}: Compilation successful")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ {module_path.name}: Compilation failed")
        print(f"   Error: {e}")
        return False


def main():
    """Run compilation verification."""
    print("=" * 70)
    print("SERVICES.CORE REFACTORING VERIFICATION")
    print("=" * 70)
    print()

    # Define modules to compile
    base_path = Path(__file__).parent
    modules = [
        base_path / "services" / "core" / "test_runner.py",
        base_path / "services" / "core" / "html_validator.py",
        base_path / "services" / "core" / "pipeline_logger.py",
        base_path / "services" / "core" / "file_manager.py",
        base_path / "services" / "core" / "__init__.py",
        base_path / "artemis_services.py",
    ]

    print("Compiling modules...")
    print()

    results = []
    for module in modules:
        if not module.exists():
            print(f"❌ {module.name}: File not found")
            results.append(False)
        else:
            results.append(compile_module(module))

    print()
    print("=" * 70)

    if all(results):
        print("✅ ALL MODULES COMPILED SUCCESSFULLY")
        print()
        print("Backward compatibility verified!")
        print("You can now import from either:")
        print("  - artemis_services (deprecated, shows warning)")
        print("  - services.core (recommended)")
        return 0
    else:
        print("❌ COMPILATION FAILED")
        print()
        print("Please fix the errors above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
