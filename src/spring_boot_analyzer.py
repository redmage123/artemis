#!/usr/bin/env python3
"""
WHY: Maintain backward compatibility with existing code
RESPONSIBILITY: Provide legacy API that delegates to new modular implementation
PATTERNS: Facade Pattern, Adapter Pattern, Deprecation Wrapper

Spring Boot Project Analyzer - Backward Compatibility Wrapper
==============================================================

This module provides backward compatibility for code that imports from
spring_boot_analyzer.py. All functionality has been moved to the spring_boot/
package for better modularity and maintainability.

DEPRECATED: This module is maintained for backward compatibility only.
New code should import from the spring_boot package:

    # New (preferred)
    from spring_boot import SpringBootAnalyzer, SpringBootAnalysis

    # Old (deprecated but still works)
    from spring_boot_analyzer import SpringBootAnalyzer, SpringBootAnalysis

Usage:
    from spring_boot_analyzer import SpringBootAnalyzer

    analyzer = SpringBootAnalyzer(project_dir="/path/to/spring-boot-app")
    analysis = analyzer.analyze()

    print(f"Main Application: {analysis.main_application_class}")
    print(f"REST Endpoints: {len(analysis.rest_endpoints)}")
"""

import json
import logging
from pathlib import Path
from typing import Optional

# Import from new modular package
from spring_boot import (
    SpringBootAnalyzer,
    SpringBootAnalysis,
    RestEndpoint,
    DatabaseConfig,
    SecurityConfig
)

# Re-export for backward compatibility
__all__ = [
    'SpringBootAnalyzer',
    'SpringBootAnalysis',
    'RestEndpoint',
    'DatabaseConfig',
    'SecurityConfig'
]


# ============================================================================
# COMMAND-LINE INTERFACE (preserved from original)
# ============================================================================

def _output_json_results(analysis: SpringBootAnalysis) -> None:
    """
    Output analysis results in JSON format.

    Args:
        analysis: SpringBootAnalysis instance with project analysis
    """
    result = {
        "main_class": analysis.main_application_class,
        "base_package": analysis.base_package,
        "spring_boot_version": analysis.spring_boot_version,
        "controllers": len(analysis.controllers),
        "services": len(analysis.services),
        "repositories": len(analysis.repositories),
        "entities": len(analysis.entities),
        "rest_endpoints": len(analysis.rest_endpoints),
        "database": analysis.database_config.datasource_type if analysis.database_config else None,
        "security_enabled": analysis.security_config.enabled if analysis.security_config else False,
        "actuator_enabled": analysis.actuator_enabled,
        "test_classes": len(analysis.test_classes)
    }
    print(json.dumps(result, indent=2))


def _output_text_results(analysis: SpringBootAnalysis) -> None:
    """
    Output analysis results in human-readable text format.

    Args:
        analysis: SpringBootAnalysis instance with project analysis
    """
    _print_header(analysis)
    _print_layers(analysis)
    _print_rest_api(analysis)
    _print_database_info(analysis)
    _print_security_info(analysis)
    _print_actuator_info(analysis)
    _print_testing_info(analysis)
    print(f"{'='*60}\n")


def _print_header(analysis: SpringBootAnalysis) -> None:
    """Print application header information."""
    print(f"\n{'='*60}")
    print(f"Spring Boot Application Analysis")
    print(f"{'='*60}")
    print(f"Main Class:    {analysis.main_application_class}")
    print(f"Base Package:  {analysis.base_package}")

    if not analysis.spring_boot_version:
        return

    print(f"Spring Boot:   {analysis.spring_boot_version}")


def _print_layers(analysis: SpringBootAnalysis) -> None:
    """Print application layer information."""
    print(f"\nLayers:")
    print(f"  Controllers:  {len(analysis.controllers)}")
    print(f"  Services:     {len(analysis.services)}")
    print(f"  Repositories: {len(analysis.repositories)}")
    print(f"  Entities:     {len(analysis.entities)}")


def _print_rest_api(analysis: SpringBootAnalysis) -> None:
    """Print REST API endpoint information."""
    print(f"\nREST API:")
    print(f"  Endpoints:    {len(analysis.rest_endpoints)}")

    for endpoint in analysis.rest_endpoints[:5]:  # Show first 5
        print(f"    {', '.join(endpoint.methods):6} {endpoint.path}")


def _print_database_info(analysis: SpringBootAnalysis) -> None:
    """Print database configuration information."""
    if not analysis.database_config:
        return

    if not analysis.database_config.datasource_type:
        return

    print(f"\nDatabase:")
    print(f"  Type:         {analysis.database_config.datasource_type}")
    print(f"  JPA:          {'Yes' if analysis.uses_jpa else 'No'}")


def _print_security_info(analysis: SpringBootAnalysis) -> None:
    """Print security configuration information."""
    if not analysis.security_config:
        return

    if not analysis.security_config.enabled:
        return

    print(f"\nSecurity:")
    print(f"  OAuth:        {'Yes' if analysis.security_config.oauth_enabled else 'No'}")
    print(f"  JWT:          {'Yes' if analysis.security_config.jwt_enabled else 'No'}")


def _print_actuator_info(analysis: SpringBootAnalysis) -> None:
    """Print Spring Boot Actuator information."""
    if not analysis.actuator_enabled:
        return

    print(f"\nActuator:")
    print(f"  Endpoints:    {', '.join(analysis.actuator_endpoints)}")


def _print_testing_info(analysis: SpringBootAnalysis) -> None:
    """Print testing configuration information."""
    print(f"\nTesting:")
    print(f"  Test Classes: {len(analysis.test_classes)}")
    print(f"  Testcontainers: {'Yes' if analysis.uses_testcontainers else 'No'}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Spring Boot Project Analyzer"
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Spring Boot project directory"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Create analyzer
    analyzer = SpringBootAnalyzer(project_dir=args.project_dir)

    # Analyze project
    analysis = analyzer.analyze()

    # Output results
    if args.json:
        _output_json_results(analysis)
    else:
        _output_text_results(analysis)
