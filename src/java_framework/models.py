#!/usr/bin/env python3
"""
WHY: Centralized data models for Java framework detection
RESPONSIBILITY: Defines all enums and dataclasses representing Java web frameworks,
               servers, template engines, and analysis results
PATTERNS: Enum pattern for type safety, Dataclass pattern for immutable data structures
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class JavaWebFramework(Enum):
    """
    WHY: Type-safe enumeration of Java web frameworks
    RESPONSIBILITY: Defines all supported Java web frameworks
    """
    SPRING_BOOT = "Spring Boot"
    SPRING_MVC = "Spring MVC"
    JAKARTA_EE = "Jakarta EE"
    MICRONAUT = "Micronaut"
    QUARKUS = "Quarkus"
    PLAY = "Play Framework"
    DROPWIZARD = "Dropwizard"
    VERTX = "Vert.x"
    SPARK = "Spark Framework"
    STRUTS = "Apache Struts"
    JSF = "JavaServer Faces"
    VAADIN = "Vaadin"
    GRAILS = "Grails"
    UNKNOWN = "Unknown"


class WebServer(Enum):
    """
    WHY: Type-safe enumeration of Java web servers
    RESPONSIBILITY: Defines all supported web servers and servlet containers
    """
    TOMCAT = "Apache Tomcat"
    JETTY = "Eclipse Jetty"
    UNDERTOW = "Undertow"
    NETTY = "Netty"
    GLASSFISH = "GlassFish"
    WILDFLY = "WildFly"
    WEBLOGIC = "WebLogic"
    WEBSPHERE = "WebSphere"
    JBOSS = "JBoss"
    UNKNOWN = "Unknown"


class TemplateEngine(Enum):
    """
    WHY: Type-safe enumeration of Java template engines
    RESPONSIBILITY: Defines all supported template engines
    """
    THYMELEAF = "Thymeleaf"
    FREEMARKER = "FreeMarker"
    VELOCITY = "Velocity"
    JSP = "JavaServer Pages"
    MUSTACHE = "Mustache"
    PEBBLE = "Pebble"
    GROOVY = "Groovy Templates"
    UNKNOWN = "Unknown"


@dataclass
class DetectionResult:
    """
    WHY: Represents the result of a framework detection attempt
    RESPONSIBILITY: Encapsulates framework detection outcome with confidence and metadata
    """
    framework: JavaWebFramework
    version: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0
    detected_by: str = ""


@dataclass
class JavaWebFrameworkAnalysis:
    """
    WHY: Comprehensive analysis result for Java web projects
    RESPONSIBILITY: Aggregates all detected technologies, frameworks, and project characteristics
    PATTERNS: Dataclass with sensible defaults, immutable after creation
    """
    primary_framework: JavaWebFramework
    framework_version: Optional[str] = None
    web_server: WebServer = WebServer.UNKNOWN
    web_server_version: Optional[str] = None

    # Build system
    build_system: str = "Unknown"  # Maven, Gradle

    # Template engines
    template_engines: List[TemplateEngine] = field(default_factory=list)

    # Database
    database_technologies: List[str] = field(default_factory=list)  # JPA, Hibernate, MyBatis, JDBC
    databases: List[str] = field(default_factory=list)  # PostgreSQL, MySQL, H2, etc.

    # APIs
    has_rest_api: bool = False
    has_graphql: bool = False
    has_soap: bool = False
    rest_framework: Optional[str] = None  # JAX-RS, Spring Web

    # Security
    security_frameworks: List[str] = field(default_factory=list)  # Spring Security, Shiro, etc.
    has_oauth: bool = False
    has_jwt: bool = False

    # Testing
    test_frameworks: List[str] = field(default_factory=list)  # JUnit, TestNG, Mockito, etc.

    # Additional technologies
    messaging: List[str] = field(default_factory=list)  # JMS, Kafka, RabbitMQ
    caching: List[str] = field(default_factory=list)  # Redis, Hazelcast, EhCache

    # Configuration
    config_format: str = "Unknown"  # application.properties, application.yml, etc.

    # Detected dependencies
    dependencies: Dict[str, str] = field(default_factory=dict)

    # Source structure
    is_microservices: bool = False
    is_monolith: bool = True
    modules: List[str] = field(default_factory=list)
