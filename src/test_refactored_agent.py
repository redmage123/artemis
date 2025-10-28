#!/usr/bin/env python3
"""
Test script to demonstrate the refactored code_refactoring_agent.

Tests both old-style (backward compatible) and new-style imports.
"""

import sys
from pathlib import Path

def test_backward_compatible_import():
    """Test that old imports still work."""
    print("=" * 70)
    print("TEST 1: Backward Compatible Import")
    print("=" * 70)

    try:
        from code_refactoring_agent import CodeRefactoringAgent, create_refactoring_agent
        print("✓ Successfully imported from code_refactoring_agent (old style)")

        agent = create_refactoring_agent(verbose=False)
        print("✓ Created agent using factory function")

        # Analyze a sample file
        file_path = Path(__file__)
        analysis = agent.analyze_file_for_refactoring(file_path)

        print(f"✓ Analyzed {file_path.name}")
        print(f"  - Total issues found: {analysis['total_issues']}")
        print(f"  - Long methods: {len(analysis.get('long_methods', []))}")
        print(f"  - Simple loops: {len(analysis.get('simple_loops', []))}")
        print(f"  - If/elif chains: {len(analysis.get('if_elif_chains', []))}")

        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_new_package_import():
    """Test that new package imports work."""
    print("\n" + "=" * 70)
    print("TEST 2: New Package Import")
    print("=" * 70)

    try:
        from agents.refactoring import (
            CodeRefactoringAgent,
            create_refactoring_agent,
            RefactoringAnalysis,
            PatternType,
            RefactoringPriority
        )
        print("✓ Successfully imported from agents.refactoring (new style)")

        agent = create_refactoring_agent(verbose=False)
        print("✓ Created agent using factory function")

        # Test type hints work
        print("✓ Type hints available:")
        print(f"  - PatternType.LOOP: {PatternType.LOOP.value}")
        print(f"  - PatternType.LONG_METHOD: {PatternType.LONG_METHOD.value}")
        print(f"  - RefactoringPriority.CRITICAL: {RefactoringPriority.CRITICAL.value}")

        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def test_component_isolation():
    """Test that individual components can be used independently."""
    print("\n" + "=" * 70)
    print("TEST 3: Component Isolation")
    print("=" * 70)

    try:
        from agents.refactoring.analyzer import CodeSmellAnalyzer
        from agents.refactoring.suggestion_generator import RefactoringSuggestionGenerator
        from agents.refactoring.models import PatternType

        print("✓ Successfully imported individual components")

        # Create analyzer directly
        analyzer = CodeSmellAnalyzer(verbose=False)
        print("✓ Created CodeSmellAnalyzer independently")

        # Analyze file
        file_path = Path(__file__)
        analysis = analyzer.analyze_file(file_path)
        print(f"✓ Used analyzer directly on {file_path.name}")
        print(f"  - Analysis object type: {type(analysis).__name__}")
        print(f"  - Has {analysis.total_issues} issues")

        # Create generator directly
        generator = RefactoringSuggestionGenerator()
        print("✓ Created RefactoringSuggestionGenerator independently")

        # Generate instructions
        instructions = generator.generate_instructions(analysis)
        print(f"✓ Generated instructions ({len(instructions)} characters)")

        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_compatibility():
    """Test that API is identical to original."""
    print("\n" + "=" * 70)
    print("TEST 4: API Compatibility")
    print("=" * 70)

    try:
        from code_refactoring_agent import create_refactoring_agent

        agent = create_refactoring_agent(verbose=False)

        # Test all public methods exist
        methods = [
            'analyze_file_for_refactoring',
            'generate_refactoring_instructions',
            'apply_automated_refactoring',
            'log'
        ]

        for method_name in methods:
            if hasattr(agent, method_name):
                print(f"✓ Method exists: {method_name}")
            else:
                print(f"✗ Missing method: {method_name}")
                return False

        # Test REFACTORING_RULES class attribute
        if hasattr(agent, 'REFACTORING_RULES'):
            print(f"✓ REFACTORING_RULES attribute exists ({len(agent.REFACTORING_RULES)} rules)")
        else:
            print("✗ Missing REFACTORING_RULES attribute")
            return False

        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║       REFACTORED CODE REFACTORING AGENT - TEST SUITE            ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    results = []

    # Run tests
    results.append(("Backward Compatible Import", test_backward_compatible_import()))
    results.append(("New Package Import", test_new_package_import()))
    results.append(("Component Isolation", test_component_isolation()))
    results.append(("API Compatibility", test_api_compatibility()))

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {test_name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Refactoring successful.")
        return 0
    else:
        print("\n✗ Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
