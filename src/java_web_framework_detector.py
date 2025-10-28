#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

WHY: Maintains backward compatibility with existing code
RESPONSIBILITY: Re-exports classes from refactored java_framework package
PATTERNS: Facade Pattern, Adapter Pattern

This module serves as a backward compatibility wrapper for the refactored
java_framework package. All functionality has been moved to the java_framework/
package with improved modularity and maintainability.

Old usage (still works):
    from java_web_framework_detector import JavaWebFrameworkDetector

    detector = JavaWebFrameworkDetector(project_dir="/path/to/project")
    analysis = detector.analyze()

New usage (recommended):
    from java_framework import JavaWebFrameworkAnalyzer

    analyzer = JavaWebFrameworkAnalyzer(project_dir="/path/to/project")
    analysis = analyzer.analyze()

MIGRATION NOTE:
The class JavaWebFrameworkDetector has been renamed to JavaWebFrameworkAnalyzer
in the new package to better reflect its purpose. This wrapper maintains the old
name for backward compatibility.
"""

# Re-export models from new package
from java_framework.models import (
    JavaWebFramework,
    JavaWebFrameworkAnalysis,
    TemplateEngine,
    WebServer,
)

# Import analyzer from new package
from java_framework.analyzer import JavaWebFrameworkAnalyzer


# Backward compatibility alias
class JavaWebFrameworkDetector(JavaWebFrameworkAnalyzer):
    """
    WHY: Backward compatibility alias for JavaWebFrameworkAnalyzer
    RESPONSIBILITY: Maintains old class name for existing code
    PATTERNS: Adapter Pattern

    DEPRECATED: Use java_framework.JavaWebFrameworkAnalyzer instead
    """
    pass


# CLI functionality - maintain backward compatibility
if __name__ == "__main__":
    import argparse
    import json
    import logging

    parser = argparse.ArgumentParser(
        description="Java Web Framework Detector and Analyzer"
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Java project directory"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Create detector (using backward compatible name)
    detector = JavaWebFrameworkDetector(project_dir=args.project_dir)

    # Analyze project
    analysis = detector.analyze()

    # Output results
    if args.json:
        _output_json_format(analysis)
    else:
        _output_human_readable_format(analysis)


def _output_json_format(analysis: JavaWebFrameworkAnalysis) -> None:
    """Output analysis results in JSON format"""
    import json
    result = {
        "framework": analysis.primary_framework.value,
        "framework_version": analysis.framework_version,
        "web_server": analysis.web_server.value,
        "web_server_version": analysis.web_server_version,
        "build_system": analysis.build_system,
        "template_engines": [e.value for e in analysis.template_engines],
        "database_technologies": analysis.database_technologies,
        "databases": analysis.databases,
        "has_rest_api": analysis.has_rest_api,
        "rest_framework": analysis.rest_framework,
        "has_graphql": analysis.has_graphql,
        "security_frameworks": analysis.security_frameworks,
        "test_frameworks": analysis.test_frameworks,
        "architecture": "Microservices" if analysis.is_microservices else "Monolith"
    }
    print(json.dumps(result, indent=2))


def _output_human_readable_format(analysis: JavaWebFrameworkAnalysis) -> None:
    """Output analysis results in human-readable format"""
    _print_header()
    _print_core_info(analysis)
    _print_optional_info(analysis)
    _print_footer()


def _print_header() -> None:
    """Print report header"""
    print(f"\n{'='*60}")
    print(f"Java Web Framework Analysis")
    print(f"{'='*60}")


def _print_core_info(analysis: JavaWebFrameworkAnalysis) -> None:
    """Print core framework information"""
    print(f"Framework:     {analysis.primary_framework.value}")

    if analysis.framework_version:
        print(f"Version:       {analysis.framework_version}")

    print(f"Build System:  {analysis.build_system}")
    print(f"Web Server:    {analysis.web_server.value}")

    if analysis.web_server_version:
        print(f"Server Version: {analysis.web_server_version}")


def _print_optional_info(analysis: JavaWebFrameworkAnalysis) -> None:
    """Print optional technology information"""
    if analysis.template_engines:
        print(f"Templates:     {', '.join(e.value for e in analysis.template_engines)}")

    if analysis.database_technologies:
        print(f"Data Access:   {', '.join(analysis.database_technologies)}")

    if analysis.databases:
        print(f"Databases:     {', '.join(analysis.databases)}")

    if analysis.has_rest_api:
        print(f"REST API:      Yes ({analysis.rest_framework})")

    if analysis.has_graphql:
        print(f"GraphQL:       Yes")

    if analysis.security_frameworks:
        print(f"Security:      {', '.join(analysis.security_frameworks)}")

    if analysis.test_frameworks:
        print(f"Testing:       {', '.join(analysis.test_frameworks)}")

    print(f"Architecture:  {'Microservices' if analysis.is_microservices else 'Monolith'}")

    if analysis.modules:
        print(f"Modules:       {', '.join(analysis.modules)}")


def _print_footer() -> None:
    """Print report footer"""
    print(f"{'='*60}\n")


# Re-export all public symbols for backward compatibility
__all__ = [
    "JavaWebFrameworkDetector",
    "JavaWebFramework",
    "JavaWebFrameworkAnalysis",
    "WebServer",
    "TemplateEngine",
]
