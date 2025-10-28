#!/usr/bin/env python3
"""
WHY: Detects Java web technologies and frameworks
RESPONSIBILITY: Identifies web servers, template engines, databases, REST/GraphQL/SOAP,
               security frameworks, test frameworks, messaging, and caching technologies
PATTERNS: Strategy Pattern (dispatch tables), Guard Clauses, Single Responsibility
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from java_framework.models import TemplateEngine, WebServer


class TechnologyDetector:
    """
    WHY: Comprehensive technology detection for Java projects
    RESPONSIBILITY: Detects all technology stacks used in Java web applications
    PATTERNS: Strategy Pattern with dispatch tables for extensible detection
    """

    def __init__(self, project_dir: Path):
        """
        Initialize technology detector

        Args:
            project_dir: Java project root directory
        """
        self.project_dir = project_dir

    def detect_web_server(self, dependencies: Dict[str, str]) -> WebServer:
        """
        WHY: Identifies embedded web server using dispatch table
        RESPONSIBILITY: Checks dependencies against known web servers

        Args:
            dependencies: Project dependencies

        Returns:
            Detected WebServer
        """
        # Dispatch table for web server detection
        server_checks: Dict[str, WebServer] = {
            "tomcat": WebServer.TOMCAT,
            "jetty": WebServer.JETTY,
            "undertow": WebServer.UNDERTOW,
            "netty": WebServer.NETTY,
        }

        for keyword, server in server_checks.items():
            if any(keyword in dep for dep in dependencies):
                return server

        return WebServer.UNKNOWN

    def detect_template_engines(self, dependencies: Dict[str, str]) -> List[TemplateEngine]:
        """
        WHY: Identifies template engines using dispatch table
        RESPONSIBILITY: Checks dependencies and filesystem for templates

        Args:
            dependencies: Project dependencies

        Returns:
            List of detected template engines
        """
        engines = []

        # Dispatch table for template engine detection
        engine_checks: Dict[str, TemplateEngine] = {
            "thymeleaf": TemplateEngine.THYMELEAF,
            "freemarker": TemplateEngine.FREEMARKER,
            "velocity": TemplateEngine.VELOCITY,
            "mustache": TemplateEngine.MUSTACHE,
            "pebble": TemplateEngine.PEBBLE,
            "groovy-templates": TemplateEngine.GROOVY,
        }

        for keyword, engine in engine_checks.items():
            if any(keyword in dep for dep in dependencies):
                engines.append(engine)

        # Check for JSP files in project
        if list(self.project_dir.glob("**/*.jsp")):
            engines.append(TemplateEngine.JSP)

        return engines

    def detect_database_technologies(self, dependencies: Dict[str, str]) -> List[str]:
        """
        WHY: Identifies database access technologies
        RESPONSIBILITY: Checks for ORM and database frameworks

        Args:
            dependencies: Project dependencies

        Returns:
            List of database technologies
        """
        techs = []

        # Dispatch table for database technology detection
        tech_checks: Dict[str, str] = {
            "spring-data-jpa": "JPA",
            "jakarta.persistence-api": "JPA",
            "hibernate": "Hibernate",
            "mybatis": "MyBatis",
            "jooq": "jOOQ",
            "jdbc": "JDBC",
            "spring-data-mongodb": "Spring Data MongoDB",
            "spring-data-redis": "Spring Data Redis",
        }

        for keyword, tech_name in tech_checks.items():
            if any(keyword in dep for dep in dependencies):
                # Guard clause: avoid duplicates
                if tech_name not in techs:
                    techs.append(tech_name)

        return techs

    def detect_databases(self, dependencies: Dict[str, str]) -> List[str]:
        """
        WHY: Identifies database drivers
        RESPONSIBILITY: Checks for database driver dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            List of databases
        """
        dbs = []

        # Dispatch table for database detection
        db_checks: Dict[str, str] = {
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
            "mariadb": "MariaDB",
            "h2": "H2",
            "hsqldb": "HSQLDB",
            "oracle": "Oracle",
            "mongodb": "MongoDB",
            "redis": "Redis",
        }

        # Handle SQL Server special cases
        for dep in dependencies:
            if "sqlserver" in dep or "mssql" in dep:
                if "SQL Server" not in dbs:
                    dbs.append("SQL Server")

        for keyword, db_name in db_checks.items():
            if any(keyword in dep for dep in dependencies):
                dbs.append(db_name)

        return dbs

    def detect_rest_api(self, dependencies: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """
        WHY: Identifies REST API framework
        RESPONSIBILITY: Checks for REST API dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            Tuple of (has_rest_api, rest_framework_name)
        """
        # Dispatch table for REST framework detection
        rest_checks = [
            (["spring-web", "spring-webmvc"], "Spring Web"),
            (["jax-rs", "jersey", "resteasy"], "JAX-RS"),
            (["dropwizard"], "Dropwizard"),
        ]

        for keywords, framework_name in rest_checks:
            if any(any(kw in dep for dep in dependencies) for kw in keywords):
                return True, framework_name

        return False, None

    def detect_graphql(self, dependencies: Dict[str, str]) -> bool:
        """
        WHY: Detect GraphQL support
        RESPONSIBILITY: Checks for GraphQL dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            True if GraphQL is detected
        """
        return any("graphql" in dep for dep in dependencies)

    def detect_soap(self, dependencies: Dict[str, str]) -> bool:
        """
        WHY: Detect SOAP support
        RESPONSIBILITY: Checks for SOAP/Web Services dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            True if SOAP is detected
        """
        return any("cxf" in dep or "jax-ws" in dep or "axis" in dep for dep in dependencies)

    def detect_security_frameworks(self, dependencies: Dict[str, str]) -> List[str]:
        """
        WHY: Identifies security frameworks
        RESPONSIBILITY: Checks for security framework dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            List of security frameworks
        """
        frameworks = []

        # Dispatch table for security framework detection
        security_checks: Dict[str, str] = {
            "spring-security": "Spring Security",
            "shiro": "Apache Shiro",
            "keycloak": "Keycloak",
        }

        for keyword, framework_name in security_checks.items():
            if any(keyword in dep for dep in dependencies):
                frameworks.append(framework_name)

        return frameworks

    def detect_oauth(self, dependencies: Dict[str, str]) -> bool:
        """
        WHY: Detect OAuth support
        RESPONSIBILITY: Checks for OAuth dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            True if OAuth is detected
        """
        return any("oauth" in dep for dep in dependencies)

    def detect_jwt(self, dependencies: Dict[str, str]) -> bool:
        """
        WHY: Detect JWT support
        RESPONSIBILITY: Checks for JWT dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            True if JWT is detected
        """
        return any("jwt" in dep or "jjwt" in dep for dep in dependencies)

    def detect_test_frameworks(self, dependencies: Dict[str, str]) -> List[str]:
        """
        WHY: Identifies testing frameworks
        RESPONSIBILITY: Checks for test framework dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            List of test frameworks
        """
        frameworks = []

        # Dispatch table for test framework detection
        test_checks: Dict[str, str] = {
            "junit": "JUnit",
            "testng": "TestNG",
            "mockito": "Mockito",
            "rest-assured": "REST Assured",
            "spring-boot-starter-test": "Spring Boot Test",
        }

        for keyword, framework_name in test_checks.items():
            if any(keyword in dep for dep in dependencies):
                frameworks.append(framework_name)

        return frameworks

    def detect_messaging(self, dependencies: Dict[str, str]) -> List[str]:
        """
        WHY: Identifies messaging technologies
        RESPONSIBILITY: Checks for messaging dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            List of messaging technologies
        """
        messaging = []

        # Dispatch table for messaging detection
        messaging_checks: Dict[str, str] = {
            "kafka": "Apache Kafka",
            "rabbitmq": "RabbitMQ",
            "activemq": "ActiveMQ",
            "jms": "JMS",
        }

        for keyword, tech_name in messaging_checks.items():
            if any(keyword in dep for dep in dependencies):
                messaging.append(tech_name)

        return messaging

    def detect_caching(self, dependencies: Dict[str, str]) -> List[str]:
        """
        WHY: Identifies caching technologies
        RESPONSIBILITY: Checks for cache dependencies

        Args:
            dependencies: Project dependencies

        Returns:
            List of caching technologies
        """
        caching = []

        # Dispatch table for caching detection
        cache_checks: Dict[str, str] = {
            "redis": "Redis",
            "hazelcast": "Hazelcast",
            "ehcache": "EhCache",
            "caffeine": "Caffeine",
        }

        for keyword, tech_name in cache_checks.items():
            if any(keyword in dep for dep in dependencies):
                caching.append(tech_name)

        return caching

    def detect_config_format(self) -> str:
        """
        WHY: Identifies configuration file format
        RESPONSIBILITY: Checks for config files in resources directory

        Returns:
            Configuration format (YAML, Properties, HOCON, or Unknown)
        """
        resources_dir = self.project_dir / "src" / "main" / "resources"

        # Guard clause: check if resources directory exists
        if not resources_dir.exists():
            return "Unknown"

        # Dispatch table for config format detection
        config_checks: Dict[str, List[str]] = {
            "YAML": ["application.yml", "application.yaml"],
            "Properties": ["application.properties"],
            "HOCON": ["application.conf"],
        }

        for format_name, filenames in config_checks.items():
            if any((resources_dir / filename).exists() for filename in filenames):
                return format_name

        return "Unknown"
