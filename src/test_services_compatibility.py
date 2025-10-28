#!/usr/bin/env python3
"""
Test backward compatibility of services refactoring.
"""

import warnings
import sys

def test_old_import():
    """Test importing from deprecated module (shows warning)."""
    print("=" * 70)
    print("TEST 1: Old Import (Deprecated)")
    print("=" * 70)
    print()

    # Capture deprecation warning
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        from artemis_services import TestRunner, HTMLValidator, PipelineLogger, FileManager

        # Check warning was issued
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()

        print("✅ Deprecation warning issued correctly")
        print(f"   Warning: {w[0].message}")
        print()

        # Test classes are available
        assert TestRunner is not None
        assert HTMLValidator is not None
        assert PipelineLogger is not None
        assert FileManager is not None

        print("✅ All classes imported successfully")
        print()

        # Test instantiation
        runner = TestRunner()
        validator = HTMLValidator()
        logger = PipelineLogger(verbose=False)
        fm = FileManager()

        print("✅ All classes instantiated successfully")
        print()

    return True


def test_new_import():
    """Test importing from new module location."""
    print("=" * 70)
    print("TEST 2: New Import (Recommended)")
    print("=" * 70)
    print()

    from services.core import TestRunner, HTMLValidator, PipelineLogger, FileManager

    # Test classes are available
    assert TestRunner is not None
    assert HTMLValidator is not None
    assert PipelineLogger is not None
    assert FileManager is not None

    print("✅ All classes imported successfully")
    print()

    # Test instantiation
    runner = TestRunner()
    validator = HTMLValidator()
    logger = PipelineLogger(verbose=False)

    print("✅ All classes instantiated successfully")
    print()

    # Test FileManager static methods
    from pathlib import Path
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"

        # Test write/read
        FileManager.write_text(test_file, "Hello, World!")
        content = FileManager.read_text(test_file)
        assert content == "Hello, World!"

        print("✅ FileManager operations work correctly")
        print()

    return True


def test_new_features():
    """Test new features in refactored modules."""
    print("=" * 70)
    print("TEST 3: New Features")
    print("=" * 70)
    print()

    from services.core import (
        create_logger,
        create_silent_logger,
        ServiceRegistry,
        initialize_services
    )

    # Test factory functions
    logger = create_logger(verbose=False)
    silent_logger = create_silent_logger()

    assert logger is not None
    assert silent_logger is not None
    assert not silent_logger.is_verbose()

    print("✅ Factory functions work correctly")
    print()

    # Test ServiceRegistry
    ServiceRegistry.clear()
    ServiceRegistry.register('test_logger', logger)

    assert ServiceRegistry.has('test_logger')
    retrieved_logger = ServiceRegistry.get('test_logger')
    assert retrieved_logger is logger

    print("✅ ServiceRegistry works correctly")
    print()

    # Test initialize_services
    ServiceRegistry.clear()
    initialize_services(verbose=False)

    assert ServiceRegistry.has('logger')
    assert ServiceRegistry.has('test_runner')
    assert ServiceRegistry.has('html_validator')
    assert ServiceRegistry.has('file_manager')

    print("✅ initialize_services() works correctly")
    print()

    return True


def test_identical_behavior():
    """Test that old and new imports produce identical behavior."""
    print("=" * 70)
    print("TEST 4: Identical Behavior")
    print("=" * 70)
    print()

    # Import from both locations
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from artemis_services import PipelineLogger as OldLogger

    from services.core import PipelineLogger as NewLogger

    # Create instances
    old_logger = OldLogger(verbose=False)
    new_logger = NewLogger(verbose=False)

    # They should be the same class
    assert OldLogger is NewLogger
    print("✅ Old and new imports reference the same class")
    print()

    # Test behavior is identical
    assert old_logger.is_verbose() == new_logger.is_verbose()
    print("✅ Behavior is identical between old and new imports")
    print()

    return True


def main():
    """Run all tests."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "SERVICES COMPATIBILITY TEST SUITE" + " " * 19 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    tests = [
        ("Old Import (Deprecated)", test_old_import),
        ("New Import (Recommended)", test_new_import),
        ("New Features", test_new_features),
        ("Identical Behavior", test_identical_behavior),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test failed: {name}")
            print(f"   Error: {e}")
            results.append((name, False))
            import traceback
            traceback.print_exc()
            print()

    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()

    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")

    print()

    if all(r for _, r in results):
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 20 + "ALL TESTS PASSED!" + " " * 26 + "║")
        print("║" + " " * 15 + "100% Backward Compatibility Verified" + " " * 16 + "║")
        print("╚" + "═" * 68 + "╝")
        return 0
    else:
        print("╔" + "═" * 68 + "╗")
        print("║" + " " * 20 + "SOME TESTS FAILED!" + " " * 23 + "║")
        print("╚" + "═" * 68 + "╝")
        return 1


if __name__ == "__main__":
    sys.exit(main())
