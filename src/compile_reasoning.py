#!/usr/bin/env python3
"""
Compile all reasoning package modules.
"""

import py_compile
import sys
from pathlib import Path

def compile_modules():
    """Compile all reasoning package modules"""
    base_path = Path("/home/bbrelin/src/repos/artemis/src")

    modules = [
        "reasoning/__init__.py",
        "reasoning/models.py",
        "reasoning/strategy_selector.py",
        "reasoning/prompt_enhancer.py",
        "reasoning/executors.py",
        "reasoning/llm_client_wrapper.py",
        "reasoning_integration.py"
    ]

    success_count = 0
    error_count = 0

    for module in modules:
        module_path = base_path / module
        try:
            py_compile.compile(str(module_path), doraise=True)
            print(f"✓ Compiled: {module}")
            success_count += 1
        except py_compile.PyCompileError as e:
            print(f"✗ Failed: {module}")
            print(f"  Error: {e}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"Compilation Results:")
    print(f"  Success: {success_count}")
    print(f"  Errors:  {error_count}")
    print(f"{'='*60}")

    return error_count == 0

if __name__ == "__main__":
    success = compile_modules()
    sys.exit(0 if success else 1)
