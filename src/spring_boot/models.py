#!/usr/bin/env python3
"""
WHY: Centralized data models for Spring Boot analysis results
RESPONSIBILITY: Define immutable data structures representing Spring Boot project components
PATTERNS: Data Transfer Objects (DTOs), Immutable dataclasses

This module contains all data models used throughout the Spring Boot analyzer:
- RestEndpoint: REST API endpoint metadata
- DatabaseConfig: Database connection configuration
- SecurityConfig: Spring Security settings
- SpringBootAnalysis: Complete analysis results container
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RestEndpoint:
    """
    REST API endpoint metadata.

    Represents a single REST endpoint with its HTTP methods,
    path, controller class, and parameter information.
    """
    path: str
    methods: List[str]  # GET, POST, PUT, DELETE, etc.
    controller_class: str
    method_name: str
    request_params: List[str] = field(default_factory=list)
    path_variables: List[str] = field(default_factory=list)


@dataclass
class DatabaseConfig:
    """
    Database configuration metadata.

    Captures JDBC connection details and database type
    extracted from Spring Boot properties.
    """
    url: Optional[str] = None
    driver_class: Optional[str] = None
    username: Optional[str] = None
    datasource_type: Optional[str] = None  # H2, PostgreSQL, MySQL, etc.


@dataclass
class SecurityConfig:
    """
    Spring Security configuration metadata.

    Represents detected security features including
    authentication mechanisms and CSRF/CORS settings.
    """
    enabled: bool = False
    oauth_enabled: bool = False
    jwt_enabled: bool = False
    basic_auth: bool = False
    form_login: bool = False
    cors_enabled: bool = False
    csrf_enabled: bool = True


@dataclass
class SpringBootAnalysis:
    """
    Comprehensive Spring Boot project analysis results.

    Central data structure containing all detected information
    about a Spring Boot application including structure, layers,
    REST endpoints, database, security, and feature configuration.
    """
    # Application structure
    main_application_class: Optional[str] = None
    base_package: Optional[str] = None
    spring_boot_version: Optional[str] = None

    # Layers
    controllers: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    repositories: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    configurations: List[str] = field(default_factory=list)

    # REST API
    rest_endpoints: List[RestEndpoint] = field(default_factory=list)

    # Database
    database_config: Optional[DatabaseConfig] = None
    uses_jpa: bool = False
    uses_liquibase: bool = False
    uses_flyway: bool = False

    # Security
    security_config: Optional[SecurityConfig] = None

    # Spring Boot features
    actuator_enabled: bool = False
    actuator_endpoints: List[str] = field(default_factory=list)
    devtools_enabled: bool = False

    # Async/Scheduling
    has_async_methods: bool = False
    has_scheduled_tasks: bool = False

    # Caching
    caching_enabled: bool = False
    cache_provider: Optional[str] = None

    # Properties
    application_properties: Dict[str, str] = field(default_factory=dict)
    active_profiles: List[str] = field(default_factory=list)

    # Testing
    test_classes: List[str] = field(default_factory=list)
    uses_testcontainers: bool = False
