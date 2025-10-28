#!/usr/bin/env python3
"""
Package: services.core

WHY: Core service layer providing fundamental operations (testing, validation,
     logging, file I/O) that are used throughout the Artemis pipeline.
     Centralizes these concerns for consistency, testability, and maintainability.

RESPONSIBILITY: Provide core service implementations with clean interfaces.

PATTERNS:
- Service Layer: Encapsulates business logic as reusable services
- Facade: Provides simple interface to complex subsystems
- Factory: Factory functions for dependency injection
- Single Responsibility: Each service has one clear purpose

ARCHITECTURE:
- test_runner: Test execution (pytest)
- html_validator: HTML syntax validation (BeautifulSoup)
- pipeline_logger: Formatted logging with timestamps/emojis
- file_manager: File I/O operations (JSON, text, binary)

DESIGN PRINCIPLES:
1. All services implement appropriate interfaces (core.interfaces)
2. All services use guard clauses (max 1 level nesting)
3. All services use dispatch tables instead of if/elif chains
4. All services have comprehensive type hints
5. All services include WHY/RESPONSIBILITY/PATTERNS documentation

Dependencies: core.interfaces, core.constants

Example:
    >>> from services.core import TestRunner, PipelineLogger, FileManager
    >>>
    >>> # Use services in pipeline
    >>> logger = PipelineLogger()
    >>> logger.info("Starting tests...")
    >>>
    >>> runner = TestRunner()
    >>> results = runner.run_tests("tests/")
    >>>
    >>> FileManager.write_json("results.json", results)
"""

# Import all service classes
from services.core.test_runner import (
    TestRunner,
    create_test_runner
)

from services.core.html_validator import (
    HTMLValidator,
    create_html_validator
)

from services.core.pipeline_logger import (
    PipelineLogger,
    create_logger,
    create_silent_logger
)

from services.core.file_manager import (
    FileManager,
    create_file_manager
)


# Version information
__version__ = "1.0.0"
__author__ = "Artemis Team"


# Public API exports
__all__ = [
    # Service classes
    "TestRunner",
    "HTMLValidator",
    "PipelineLogger",
    "FileManager",

    # Factory functions
    "create_test_runner",
    "create_html_validator",
    "create_logger",
    "create_silent_logger",
    "create_file_manager",
]


# Service registry (Service Locator pattern)
class ServiceRegistry:
    """
    Service locator for dependency injection.

    WHY: Centralized service management enables easy testing and configuration.
    PATTERN: Service Locator pattern

    Example:
        >>> ServiceRegistry.register('logger', PipelineLogger(verbose=True))
        >>> logger = ServiceRegistry.get('logger')
        >>> logger.info("Hello!")
    """

    _services = {}

    @classmethod
    def register(cls, name: str, service: object) -> None:
        """Register a service instance."""
        cls._services[name] = service

    @classmethod
    def get(cls, name: str) -> object:
        """Get a registered service instance."""
        if name not in cls._services:
            raise KeyError(f"Service not registered: {name}")
        return cls._services[name]

    @classmethod
    def has(cls, name: str) -> bool:
        """Check if service is registered."""
        return name in cls._services

    @classmethod
    def clear(cls) -> None:
        """Clear all registered services (for testing)."""
        cls._services.clear()


# Default service factory (Factory pattern)
def create_default_services() -> dict:
    """
    Create default service instances for typical usage.

    WHY: Provides convenient defaults for common scenarios.
    PATTERN: Abstract Factory pattern

    Returns:
        Dictionary of service name -> instance

    Example:
        >>> services = create_default_services()
        >>> services['logger'].info("Starting...")
        >>> results = services['test_runner'].run_tests("tests/")
    """
    return {
        'test_runner': create_test_runner(),
        'html_validator': create_html_validator(),
        'logger': create_logger(verbose=True),
        'file_manager': create_file_manager(),
    }


# Convenience function for pipeline initialization
def initialize_services(verbose: bool = True) -> None:
    """
    Initialize and register default services in ServiceRegistry.

    WHY: One-line setup for typical pipeline usage.

    Args:
        verbose: Enable verbose logging

    Example:
        >>> from services.core import initialize_services, ServiceRegistry
        >>> initialize_services(verbose=True)
        >>> logger = ServiceRegistry.get('logger')
        >>> logger.info("Services initialized!")
    """
    services = create_default_services()

    # Update logger verbosity
    services['logger'] = create_logger(verbose=verbose)

    # Register all services
    for name, service in services.items():
        ServiceRegistry.register(name, service)
