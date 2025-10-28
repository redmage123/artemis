#!/usr/bin/env python3
"""
Test Framework Selector - Backward Compatibility Wrapper

WHY: Maintains backward compatibility with existing code that imports from
test_framework_selector.py. Delegates to refactored testing.selector package
while preserving the original API.

RESPONSIBILITY: Provide backward-compatible API surface. Single responsibility -
API compatibility, delegates all logic to testing.selector package.

PATTERNS: Facade pattern for API compatibility. Proxy pattern for delegation.

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from testing.selector package directly:

    # Preferred (new):
    from testing.selector import TestFrameworkSelector

    # Legacy (deprecated):
    from test_framework_selector import TestFrameworkSelector

Usage:
    from test_framework_selector import TestFrameworkSelector

    selector = TestFrameworkSelector(project_dir="/path/to/project")
    framework = selector.select_framework(requirements={"type": "unit", "language": "python"})

    # Returns: "pytest", "jest", "selenium", etc.
"""

# Import all public API from refactored package
from testing.selector import (
    TestFrameworkSelector,
    ProjectType,
    TestType,
    FrameworkRecommendation,
    ProjectDetector,
    FrameworkDetector,
    FrameworkSelector,
    FrameworkConfiguration,
    FrameworkConfigurator
)

# Maintain backward compatibility for all exported symbols
__all__ = [
    "TestFrameworkSelector",
    "ProjectType",
    "TestType",
    "FrameworkRecommendation",
    "ProjectDetector",
    "FrameworkDetector",
    "FrameworkSelector",
    "FrameworkConfiguration",
    "FrameworkConfigurator"
]

# ============================================================================
# COMMAND-LINE INTERFACE (Preserved for backward compatibility)
# ============================================================================

if __name__ == "__main__":
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Test Framework Selector - Recommend test framework for projects"
    )
    parser.add_argument(
        "--project-dir",
        help="Project directory to analyze"
    )
    parser.add_argument(
        "--test-type",
        choices=["unit", "integration", "e2e", "browser", "mobile", "performance", "api", "acceptance", "property_based"],
        default="unit",
        help="Type of testing required"
    )
    parser.add_argument(
        "--language",
        help="Programming language (python, javascript, java, cpp, etc.)"
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Requires browser automation"
    )
    parser.add_argument(
        "--mobile",
        action="store_true",
        help="Requires mobile testing"
    )
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Requires performance/load testing"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Create selector
    selector = TestFrameworkSelector(project_dir=args.project_dir)

    # Build requirements
    requirements = {}
    if args.language:
        requirements["language"] = args.language
    if args.browser:
        requirements["browser"] = True
    if args.mobile:
        requirements["mobile"] = True
    if args.performance:
        requirements["performance"] = True

    # Get recommendation
    recommendation = selector.select_framework(
        requirements=requirements,
        test_type=args.test_type
    )

    # Guard clause: Output JSON and exit if requested
    if args.json:
        print(json.dumps({
            "framework": recommendation.framework,
            "confidence": recommendation.confidence,
            "rationale": recommendation.rationale,
            "alternatives": recommendation.alternatives
        }, indent=2))
        exit(0)

    # Output human-readable results
    print(f"\n{'='*60}")
    print(f"Test Framework Recommendation")
    print(f"{'='*60}")
    print(f"Framework:    {recommendation.framework}")
    print(f"Confidence:   {recommendation.confidence * 100:.0f}%")
    print(f"Rationale:    {recommendation.rationale}")
    if recommendation.alternatives:
        print(f"Alternatives: {', '.join(recommendation.alternatives)}")
    print(f"{'='*60}\n")
