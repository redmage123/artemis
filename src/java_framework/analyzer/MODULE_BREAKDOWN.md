# Java Framework Analyzer - Module Breakdown

## Overview
Modular breakdown of the Java framework analyzer following claude.md standards.

## Module Responsibilities

### 1. build_system_detector.py (69 lines)
**RESPONSIBILITY**: Detects Java build systems (Maven/Gradle)

**Key Functions**:
- `detect()` - Identifies build system by checking for build files
- `get_maven_path()` - Returns path to pom.xml
- `get_gradle_path()` - Returns path to build.gradle/build.gradle.kts

**Patterns**: Guard Clauses, Strategy Pattern

---

### 2. dependency_parser.py (132 lines)
**RESPONSIBILITY**: Parses dependencies from build files

**Key Functions**:
- `parse(build_system, build_file)` - Routes to appropriate parser
- `_parse_maven_dependencies()` - Parses Maven POM XML
- `_parse_gradle_dependencies()` - Parses Gradle build files with regex

**Patterns**: Strategy Pattern (dispatch table), Guard Clauses

**Returns**: `Dict[str, str]` mapping "group:artifact" to version

---

### 3. technology_detector.py (368 lines)
**RESPONSIBILITY**: Detects all Java web technologies

**Key Functions**:
- `detect_web_server()` - Detects Tomcat, Jetty, Undertow, Netty
- `detect_template_engines()` - Detects Thymeleaf, FreeMarker, JSP, etc.
- `detect_database_technologies()` - Detects JPA, Hibernate, MyBatis, etc.
- `detect_databases()` - Detects PostgreSQL, MySQL, MongoDB, etc.
- `detect_rest_api()` - Detects Spring Web, JAX-RS, Dropwizard
- `detect_graphql()` - Detects GraphQL support
- `detect_soap()` - Detects SOAP/Web Services
- `detect_security_frameworks()` - Detects Spring Security, Shiro, etc.
- `detect_oauth()` - Detects OAuth support
- `detect_jwt()` - Detects JWT support
- `detect_test_frameworks()` - Detects JUnit, TestNG, Mockito, etc.
- `detect_messaging()` - Detects Kafka, RabbitMQ, JMS, etc.
- `detect_caching()` - Detects Redis, Hazelcast, EhCache, etc.
- `detect_config_format()` - Detects YAML, Properties, HOCON

**Patterns**: Strategy Pattern (dispatch tables for all detection), Guard Clauses

---

### 4. architecture_analyzer.py (76 lines)
**RESPONSIBILITY**: Analyzes project architecture patterns

**Key Functions**:
- `analyze()` - Determines microservices vs monolithic architecture
- `_extract_maven_modules()` - Extracts Maven multi-module structure

**Detection Criteria**:
- Microservices: Multiple modules, docker-compose.yml, Dockerfiles, kubernetes/
- Monolithic: Single module, no containerization

**Patterns**: Guard Clauses, Functional Programming

---

### 5. version_extractor.py (100 lines)
**RESPONSIBILITY**: Extracts version information for frameworks and servers

**Key Functions**:
- `get_framework_version()` - Extracts Spring Boot, Micronaut, Quarkus versions
- `get_web_server_version()` - Extracts Tomcat, Jetty, Undertow, Netty versions
- `_find_version_by_keyword()` - Common utility for version lookup (DRY)

**Patterns**: Strategy Pattern (dispatch tables), Guard Clauses, DRY Principle

---

### 6. main_analyzer.py (157 lines)
**RESPONSIBILITY**: Main facade orchestrating all analysis components

**Key Functions**:
- `analyze()` - Orchestrates full analysis workflow
- `_parse_dependencies_for_build_system()` - Helper for dependency parsing

**Analysis Workflow**:
1. Detect build system
2. Parse dependencies
3. Detect primary framework
4. Detect web server
5. Detect template engines
6. Detect database technologies
7. Detect API technologies (REST/GraphQL/SOAP)
8. Detect security frameworks
9. Detect test frameworks
10. Detect messaging and caching
11. Detect configuration format
12. Analyze architecture

**Patterns**: Facade Pattern, Dependency Injection, Strategy Pattern

**Returns**: `JavaWebFrameworkAnalysis` with complete analysis results

---

### 7. __init__.py (41 lines)
**RESPONSIBILITY**: Public API exports and documentation

**Exports**:
- `JavaWebFrameworkAnalyzer` - Main facade
- `BuildSystemDetector` - For advanced usage
- `DependencyParser` - For advanced usage
- `TechnologyDetector` - For advanced usage
- `ArchitectureAnalyzer` - For advanced usage
- `VersionExtractor` - For advanced usage

---

## Usage Examples

### Standard Usage (Facade Pattern)
```python
from java_framework.analyzer import JavaWebFrameworkAnalyzer

analyzer = JavaWebFrameworkAnalyzer(project_dir="/path/to/project")
analysis = analyzer.analyze()

print(f"Framework: {analysis.primary_framework.value}")
print(f"Version: {analysis.framework_version}")
print(f"Web Server: {analysis.web_server.value}")
print(f"Databases: {analysis.databases}")
print(f"Architecture: {'Microservices' if analysis.is_microservices else 'Monolithic'}")
```

### Modular Usage (Individual Components)
```python
from java_framework.analyzer import (
    BuildSystemDetector,
    DependencyParser,
    TechnologyDetector
)

# Detect build system
build_detector = BuildSystemDetector(project_dir)
build_system = build_detector.detect()

# Parse dependencies
parser = DependencyParser()
if build_system == "Maven":
    deps = parser.parse(build_system, build_detector.get_maven_path())
    
# Detect specific technologies
tech_detector = TechnologyDetector(project_dir)
web_server = tech_detector.detect_web_server(deps)
databases = tech_detector.detect_databases(deps)
```

---

## Design Patterns Used

### 1. Facade Pattern
- `JavaWebFrameworkAnalyzer` hides complexity of multiple analyzers
- Provides simple interface: `analyzer.analyze()`

### 2. Strategy Pattern
- Dispatch tables throughout for extensibility
- Build system selection: Maven vs Gradle
- Technology detection: keyword → technology mapping
- Version extraction: framework → keyword mapping

### 3. Dependency Injection
- All components injected into main analyzer
- Promotes testability and loose coupling

### 4. Single Responsibility Principle
- Each module has ONE clear responsibility
- No module does more than its stated purpose

---

## Testing Strategy

### Unit Tests by Module

**test_build_system_detector.py**:
- Test Maven detection with pom.xml
- Test Gradle detection with build.gradle
- Test Gradle Kotlin detection with build.gradle.kts
- Test unknown build system handling

**test_dependency_parser.py**:
- Test Maven POM parsing with valid XML
- Test Gradle parsing with various dependency formats
- Test malformed file handling
- Test missing file handling

**test_technology_detector.py**:
- Test each detection method independently
- Test dispatch table mappings
- Test filesystem checks (JSP detection)

**test_architecture_analyzer.py**:
- Test microservices detection with multiple modules
- Test microservices detection with Docker
- Test monolithic detection
- Test Maven module extraction

**test_version_extractor.py**:
- Test framework version extraction
- Test web server version extraction
- Test missing version handling

**test_main_analyzer.py**:
- Test full analysis integration
- Test component orchestration
- Test error handling

---

## Performance Considerations

1. **No nested loops**: All detection uses single passes
2. **Compiled regex**: Patterns compiled once in parser
3. **Early returns**: Guard clauses prevent unnecessary work
4. **Dispatch tables**: O(1) lookup vs O(n) if/elif chains
5. **Selective imports**: Modular structure allows importing only what's needed

---

## Extension Points

### Adding New Build System
Edit `dependency_parser.py`:
```python
self._parser_dispatch["NewBuildSystem"] = self._parse_new_build_system
```

### Adding New Technology
Edit `technology_detector.py` dispatch tables:
```python
tech_checks["new-tech"] = "New Technology"
```

### Adding New Framework Version
Edit `version_extractor.py` dispatch tables:
```python
self._framework_keywords[JavaWebFramework.NEW_FRAMEWORK] = "new-framework-core"
```

---

## Claude.md Compliance

✅ **No elif chains** - All replaced with dispatch tables
✅ **No nested loops** - None present
✅ **No nested ifs** - Guard clauses used
✅ **Complete type hints** - All functions annotated
✅ **WHY/RESPONSIBILITY/PATTERNS** - Every module documented
✅ **Single Responsibility** - Each module has ONE purpose
✅ **Design Patterns** - Facade, Strategy, Dependency Injection
✅ **Guard Clauses** - Early returns for validation
✅ **DRY Principle** - Common logic extracted

---

## Backward Compatibility

The original `analyzer.py` is now a 49-line wrapper that re-exports from the new package:

```python
from java_framework.analyzer.main_analyzer import JavaWebFrameworkAnalyzer
```

All existing code continues to work without modification.
