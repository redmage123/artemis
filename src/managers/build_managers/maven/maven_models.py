#!/usr/bin/env python3
"""
Module: Maven Data Models

WHY: Centralized data structures for Maven project information, dependencies, and build results.
RESPONSIBILITY: Define immutable, type-safe data models using dataclasses.
PATTERNS: Data Transfer Object (DTO), Value Object pattern.

Dependencies: maven_enums (for type hints)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MavenDependency:
    """
    Maven dependency representation.

    WHY: Type-safe representation of Maven dependencies with all coordinates.
    RESPONSIBILITY: Store dependency metadata and convert to POM XML format.

    PATTERNS: Data Transfer Object, Builder pattern (via dataclass).

    Maven Coordinates:
    - group_id: Organization/group (e.g., org.springframework.boot)
    - artifact_id: Specific artifact (e.g., spring-boot-starter-web)
    - version: Version number (e.g., 3.2.0)
    - scope: When dependency is available (compile/test/runtime/provided)
    - type: Packaging type (jar/war/pom)
    - classifier: Variant (e.g., javadoc, sources)
    - optional: True if dependency is optional for consumers
    """
    group_id: str
    artifact_id: str
    version: str
    scope: str = "compile"
    type: str = "jar"
    classifier: Optional[str] = None
    optional: bool = False

    def to_xml(self) -> str:
        """
        Convert to POM XML format.

        WHY: Enables programmatic addition of dependencies to pom.xml.
        RESPONSIBILITY: Generate properly formatted XML snippet.

        Returns:
            XML string for <dependency> element
        """
        xml_parts = [
            f"""        <dependency>
            <groupId>{self.group_id}</groupId>
            <artifactId>{self.artifact_id}</artifactId>
            <version>{self.version}</version>"""
        ]

        # Use list comprehension with guard clause pattern
        conditional_parts = [
            (self.scope != "compile", f"            <scope>{self.scope}</scope>"),
            (self.type != "jar", f"            <type>{self.type}</type>"),
            (self.classifier, f"            <classifier>{self.classifier}</classifier>"),
            (self.optional, f"            <optional>true</optional>")
        ]

        for condition, part in conditional_parts:
            if condition:
                xml_parts.append(part)

        xml_parts.append("        </dependency>")
        return "\n".join(xml_parts)


@dataclass
class MavenPlugin:
    """
    Maven plugin representation.

    WHY: Maven plugins execute goals during build lifecycle (e.g., compiler, surefire).
    RESPONSIBILITY: Store plugin metadata including configuration and executions.

    PATTERNS: Data Transfer Object.

    Plugin Coordinates:
    - group_id: Plugin group (often org.apache.maven.plugins)
    - artifact_id: Plugin name (e.g., maven-compiler-plugin)
    - version: Plugin version
    - configuration: Plugin settings (Java version, encoding, etc.)
    - executions: When to run plugin and what goals to execute
    """
    group_id: str
    artifact_id: str
    version: str
    configuration: Dict = field(default_factory=dict)
    executions: List[Dict] = field(default_factory=list)


@dataclass
class MavenProjectInfo:
    """
    Complete Maven project information.

    WHY: Centralized container for all POM metadata parsed from pom.xml.
    RESPONSIBILITY: Store comprehensive project information including dependencies,
                    plugins, modules, and properties.

    PATTERNS: Aggregate pattern (contains other value objects like MavenDependency).

    Fields:
    - group_id, artifact_id, version: Maven coordinates for this project
    - name: Human-readable project name
    - packaging: Output type (jar, war, pom for parent projects)
    - description: Project description
    - parent: Parent POM coordinates (for inheritance)
    - modules: Child module directories (for multi-module projects)
    - dependencies: All project dependencies
    - plugins: Build plugins
    - properties: Maven properties (${property.name} substitution)
    - is_multi_module: True if this is a parent aggregator project
    """
    group_id: str
    artifact_id: str
    version: str
    name: str
    packaging: str
    description: Optional[str] = None
    parent: Optional[Dict] = None
    modules: List[str] = field(default_factory=list)
    dependencies: List[MavenDependency] = field(default_factory=list)
    plugins: List[MavenPlugin] = field(default_factory=list)
    properties: Dict[str, str] = field(default_factory=dict)
    is_multi_module: bool = False

    def __str__(self) -> str:
        """Return standard Maven coordinate format: groupId:artifactId:version"""
        return f"{self.group_id}:{self.artifact_id}:{self.version}"


@dataclass
class MavenBuildResult:
    """
    Maven build execution result.

    WHY: Structured representation of build outcomes for analysis and reporting.
    RESPONSIBILITY: Capture all build metrics including test results, errors, warnings.

    PATTERNS: Result Object pattern (encapsulates operation outcome).

    Fields:
    - success: Overall build success (exit code 0 + "BUILD SUCCESS" in output)
    - exit_code: Maven process exit code
    - duration: Build time in seconds
    - output: Complete stdout/stderr output
    - phase: Maven phase that was executed
    - tests_run, tests_passed, tests_failed, tests_skipped: Test metrics
    - errors: List of [ERROR] messages from Maven output
    - warnings: List of [WARNING] messages from Maven output
    """
    success: bool
    exit_code: int
    duration: float
    output: str
    phase: str
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
