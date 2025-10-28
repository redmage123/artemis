#!/usr/bin/env python3
"""
Test Framework Selector Refactoring - Verification Tests

WHY: Verify backward compatibility and correct functionality of refactored
testing.selector package. Ensures original API surface is preserved.

RESPONSIBILITY: Test harness for verifying refactoring success.
"""

from pathlib import Path
import sys


def test_backward_compatibility():
    """Test that old imports still work."""
    print("Testing backward compatibility...")

    # Test old import style (backward compatibility)
    from test_framework_selector import (
        TestFrameworkSelector,
        ProjectType,
        TestType,
        FrameworkRecommendation
    )

    print("✓ Old-style imports work")

    # Test new import style (preferred)
    from testing.selector import (
        TestFrameworkSelector as NewSelector,
        ProjectType as NewProjectType
    )

    print("✓ New-style imports work")

    # Verify they're the same classes
    assert TestFrameworkSelector is NewSelector
    assert ProjectType is NewProjectType
    print("✓ Old and new imports reference same classes")


def test_basic_functionality():
    """Test basic framework selection functionality."""
    print("\nTesting basic functionality...")

    from testing.selector import TestFrameworkSelector

    # Test without project directory
    selector = TestFrameworkSelector()
    recommendation = selector.select_framework(
        requirements={"language": "python"},
        test_type="unit"
    )

    assert recommendation.framework == "pytest"
    assert recommendation.confidence > 0.0
    assert len(recommendation.rationale) > 0
    print(f"✓ Python unit test recommendation: {recommendation.framework}")

    # Test JavaScript
    recommendation = selector.select_framework(
        requirements={"language": "javascript"},
        test_type="unit"
    )

    assert recommendation.framework == "jest"
    print(f"✓ JavaScript unit test recommendation: {recommendation.framework}")

    # Test Java
    recommendation = selector.select_framework(
        requirements={"language": "java"},
        test_type="unit"
    )

    assert recommendation.framework == "junit"
    print(f"✓ Java unit test recommendation: {recommendation.framework}")


def test_specialized_frameworks():
    """Test specialized framework selection."""
    print("\nTesting specialized frameworks...")

    from testing.selector import TestFrameworkSelector

    selector = TestFrameworkSelector()

    # Test mobile
    recommendation = selector.select_framework(
        requirements={"mobile": True},
        test_type="mobile"
    )
    assert recommendation.framework == "appium"
    print(f"✓ Mobile test recommendation: {recommendation.framework}")

    # Test performance
    recommendation = selector.select_framework(
        requirements={"performance": True},
        test_type="performance"
    )
    assert recommendation.framework == "jmeter"
    print(f"✓ Performance test recommendation: {recommendation.framework}")

    # Test browser
    recommendation = selector.select_framework(
        requirements={"browser": True},
        test_type="browser"
    )
    assert recommendation.framework == "playwright"
    print(f"✓ Browser test recommendation: {recommendation.framework}")


def test_configuration():
    """Test framework configuration functionality."""
    print("\nTesting configuration...")

    from testing.selector import TestFrameworkSelector

    selector = TestFrameworkSelector()

    # Get pytest configuration
    config = selector.get_framework_configuration("pytest")
    assert config is not None
    assert config.framework_name == "pytest"
    assert len(config.install_commands) > 0
    assert len(config.dependencies) > 0
    print(f"✓ pytest configuration: {len(config.dependencies)} dependencies")

    # Get jest configuration
    config = selector.get_framework_configuration("jest")
    assert config is not None
    assert config.framework_name == "jest"
    print(f"✓ jest configuration: {config.run_command}")


def test_models():
    """Test data models."""
    print("\nTesting data models...")

    from testing.selector.models import (
        SelectionRequirements,
        FrameworkRecommendation
    )

    # Test SelectionRequirements
    reqs = SelectionRequirements(
        test_type="unit",
        language="python",
        browser=False
    )
    assert reqs.test_type == "unit"
    assert reqs.language == "python"
    print("✓ SelectionRequirements model works")

    # Test from_dict
    reqs_dict = {
        "type": "integration",
        "language": "java",
        "browser": True
    }
    reqs = SelectionRequirements.from_dict(reqs_dict)
    assert reqs.test_type == "integration"
    assert reqs.language == "java"
    assert reqs.browser is True
    print("✓ SelectionRequirements.from_dict() works")

    # Test to_dict
    reqs_dict = reqs.to_dict()
    assert reqs_dict["type"] == "integration"
    assert reqs_dict["language"] == "java"
    print("✓ SelectionRequirements.to_dict() works")


def test_components():
    """Test individual components."""
    print("\nTesting individual components...")

    from testing.selector.detector import ProjectDetector, FrameworkDetector
    from testing.selector.selector import FrameworkSelector
    from testing.selector.configurator import FrameworkConfigurator

    # Test ProjectDetector
    detector = ProjectDetector()
    project_type = detector.detect_project_type()
    print(f"✓ ProjectDetector instantiates: {project_type}")

    # Test FrameworkDetector
    detector = FrameworkDetector()
    framework = detector.detect_existing_framework()
    print(f"✓ FrameworkDetector instantiates: {framework}")

    # Test FrameworkSelector
    selector = FrameworkSelector()
    from testing.selector.models import SelectionRequirements
    reqs = SelectionRequirements(language="python")
    recommendation = selector.select_framework(reqs)
    assert recommendation.framework == "pytest"
    print(f"✓ FrameworkSelector works: {recommendation.framework}")

    # Test FrameworkConfigurator
    configurator = FrameworkConfigurator()
    config = configurator.get_configuration("pytest")
    assert config is not None
    print(f"✓ FrameworkConfigurator works")


def run_all_tests():
    """Run all verification tests."""
    print("="*70)
    print("TEST FRAMEWORK SELECTOR REFACTORING - VERIFICATION TESTS")
    print("="*70)

    try:
        test_backward_compatibility()
        test_basic_functionality()
        test_specialized_frameworks()
        test_configuration()
        test_models()
        test_components()

        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED")
        print("="*70)
        return 0

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
