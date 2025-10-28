# Testing Selector Package - Architecture

## Package Structure

```
testing/
└── selector/
    ├── __init__.py              # Public API exports
    ├── models.py                # Data models and enums
    ├── detector.py              # Project/framework detection
    ├── selector.py              # Framework selection logic
    ├── configurator.py          # Framework configuration
    └── selector_core.py         # Main orchestration (Facade)
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   test_framework_selector.py                    │
│                  (Backward Compatibility Wrapper)               │
│                         Facade Pattern                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    testing.selector.__init__                    │
│                        (Public API)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TestFrameworkSelector                        │
│                      (selector_core.py)                         │
│                    Main Orchestrator / Facade                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  • Coordinates all components                           │  │
│  │  • Provides unified API                                 │  │
│  │  • Caches project type                                  │  │
│  │  • Dependency Injection enabled                         │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────┬──────────────────┬──────────────────┬──────────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌─────────────────┐
│ ProjectDetector│   │FrameworkDetector│   │FrameworkSelector│
│ (detector.py)│   │  (detector.py)  │   │  (selector.py)  │
│              │   │                 │   │                 │
│ • Detect     │   │ • Detect        │   │ • Select best   │
│   project    │   │   existing      │   │   framework     │
│   type       │   │   framework     │   │ • Apply rules   │
│ • Infer      │   │ • Check config  │   │ • Strategy      │
│   language   │   │   files         │   │   dispatch      │
│ • Strategy   │   │ • Parse imports │   │                 │
│   dispatch   │   │ • Strategy      │   │                 │
│              │   │   dispatch      │   │                 │
└──────────────┘   └──────────────┘   └─────────────────┘
        │                  │                  │
        │                  │                  ▼
        │                  │           ┌─────────────────┐
        │                  │           │FrameworkConfigurator│
        │                  │           │(configurator.py)│
        │                  │           │                 │
        │                  │           │ • Provide       │
        │                  │           │   config        │
        │                  │           │ • Install cmds  │
        │                  │           │ • Dependencies  │
        │                  │           │ • Strategy      │
        │                  │           │   dispatch      │
        │                  │           └─────────────────┘
        │                  │
        ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         models.py                               │
│                    (Data Models Layer)                          │
│                                                                 │
│  • ProjectType (Enum)                                          │
│  • TestType (Enum)                                             │
│  • FrameworkRecommendation (Dataclass)                         │
│  • SelectionRequirements (Dataclass)                           │
│  • FrameworkCapabilities (Dataclass)                           │
│  • FrameworkConfiguration (Dataclass)                          │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌───────────┐
│   User    │
└─────┬─────┘
      │
      │ 1. Call select_framework(requirements)
      ▼
┌─────────────────────────┐
│ TestFrameworkSelector   │
│   (selector_core.py)    │
└─────┬───────────────────┘
      │
      │ 2. Convert requirements to SelectionRequirements
      ▼
┌─────────────────────────┐
│ SelectionRequirements   │
│     (models.py)         │
└─────┬───────────────────┘
      │
      │ 3. Detect project type
      ▼
┌─────────────────────────┐
│   ProjectDetector       │
│    (detector.py)        │
└─────┬───────────────────┘
      │
      │ 4. Check existing framework
      ▼
┌─────────────────────────┐
│  FrameworkDetector      │
│    (detector.py)        │
└─────┬───────────────────┘
      │
      │ 5. Select framework
      ▼
┌─────────────────────────┐
│  FrameworkSelector      │
│    (selector.py)        │
└─────┬───────────────────┘
      │
      │ 6. Return recommendation
      ▼
┌─────────────────────────┐
│ FrameworkRecommendation │
│     (models.py)         │
└─────┬───────────────────┘
      │
      │ 7. Get configuration (optional)
      ▼
┌─────────────────────────┐
│ FrameworkConfigurator   │
│   (configurator.py)     │
└─────┬───────────────────┘
      │
      │ 8. Return configuration
      ▼
┌─────────────────────────┐
│ FrameworkConfiguration  │
│     (models.py)         │
└─────────────────────────┘
```

## Design Patterns

### 1. Strategy Pattern

**Location**: All selector modules
**Purpose**: Extensible selection logic without modification

```python
# detector.py
detection_strategies = {
    "python": self._is_python_project,
    "java": self._is_java_project,
    # Add new strategies here
}

# selector.py
test_type_strategies = {
    TestType.MOBILE: self._select_mobile_framework,
    TestType.PERFORMANCE: self._select_performance_framework,
    # Add new strategies here
}

language_strategies = {
    "python": self._select_python_framework,
    "javascript": self._select_javascript_framework,
    # Add new strategies here
}
```

### 2. Facade Pattern

**Location**: selector_core.py, __init__.py
**Purpose**: Unified API hiding complexity

```python
# selector_core.py provides single entry point
class TestFrameworkSelector:
    def select_framework(self, requirements):
        # Orchestrates multiple components
        # Hides internal complexity
```

### 3. Factory Pattern

**Location**: models.py
**Purpose**: Object creation from different input formats

```python
# models.py
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "SelectionRequirements":
    return cls(
        test_type=data.get("type", "unit"),
        language=data.get("language"),
        # ...
    )
```

### 4. Dependency Injection

**Location**: selector_core.py
**Purpose**: Testability and flexibility

```python
def __init__(
    self,
    project_detector: Optional[ProjectDetector] = None,
    framework_detector: Optional[FrameworkDetector] = None,
    framework_selector: Optional[FrameworkSelector] = None
):
    # Components can be injected for testing
```

### 5. Chain of Responsibility

**Location**: selector.py
**Purpose**: Priority-based framework selection

```python
def select_framework(self, requirements):
    # Guard clause: Check existing framework first
    if existing_framework:
        return early_recommendation

    # Guard clause: Check specialized test types
    if test_type in specialized_strategies:
        return specialized_recommendation

    # Guard clause: Check language strategies
    if language in language_strategies:
        return language_recommendation

    # Default fallback
    return default_recommendation
```

## Module Responsibilities

### models.py (204 lines)
- Define ProjectType enum
- Define TestType enum
- Define FrameworkRecommendation dataclass
- Define SelectionRequirements dataclass
- Define FrameworkCapabilities dataclass
- Define FrameworkConfiguration dataclass
- Provide data conversion methods

### detector.py (330 lines)
- ProjectDetector class
  - Detect project type from files
  - Infer language from project type
  - Use dispatch tables for detection
- FrameworkDetector class
  - Detect existing frameworks
  - Check configuration files
  - Parse test file imports
  - Use dispatch tables for detection

### selector.py (340 lines)
- FrameworkSelector class
  - Select framework based on requirements
  - Apply test type strategies
  - Apply language strategies
  - Use dispatch tables for selection
  - Return FrameworkRecommendation

### configurator.py (224 lines)
- FrameworkConfigurator class
  - Provide configuration for frameworks
  - Generate install commands
  - List dependencies
  - Specify config files
  - Use dispatch tables for configuration

### selector_core.py (189 lines)
- TestFrameworkSelector class
  - Orchestrate all components
  - Provide unified API
  - Cache project analysis
  - Enable dependency injection
  - Handle requirement conversion

### __init__.py (67 lines)
- Export public API
- Define __all__ for explicit exports
- Provide documentation

## Extension Points

### Adding New Language Support

1. **models.py**: Add enum value to ProjectType
   ```python
   class ProjectType(Enum):
       RUST = "rust"
   ```

2. **detector.py**: Add detection strategy
   ```python
   def _is_rust_project(self) -> bool:
       return bool(list(self.project_dir.glob("**/Cargo.toml")))

   detection_strategies["rust"] = self._is_rust_project
   ```

3. **selector.py**: Add selection strategy
   ```python
   def _select_rust_framework(self, requirements):
       return FrameworkRecommendation(...)

   self._language_strategies["rust"] = self._select_rust_framework
   ```

4. **configurator.py**: Add configuration
   ```python
   def _configure_cargo_test(self):
       return FrameworkConfiguration(...)

   self._config_strategies["cargo test"] = self._configure_cargo_test
   ```

### Adding New Test Type

1. **models.py**: Add enum value to TestType
   ```python
   class TestType(Enum):
       SECURITY = "security"
   ```

2. **selector.py**: Add test type strategy
   ```python
   def _select_security_framework(self, requirements):
       return FrameworkRecommendation(...)

   self._test_type_strategies[TestType.SECURITY] = self._select_security_framework
   ```

### Adding New Framework

1. **configurator.py**: Add configuration
   ```python
   def _configure_new_framework(self):
       return FrameworkConfiguration(
           framework_name="new_framework",
           install_commands=["pip install new_framework"],
           dependencies=["new_framework"],
           config_files={},
           run_command="new_framework test",
           setup_instructions="..."
       )

   self._config_strategies["new_framework"] = self._configure_new_framework
   ```

2. **selector.py**: Reference in appropriate strategy

## Type Hints Usage

All functions include complete type hints:

```python
from typing import Dict, List, Optional, Any, Callable

def select_framework(
    self,
    requirements: SelectionRequirements,
    existing_framework: Optional[str] = None
) -> FrameworkRecommendation:
    pass

def get_configuration(
    self,
    framework_name: str
) -> Optional[FrameworkConfiguration]:
    pass
```

## Guard Clauses Pattern

All modules use guard clauses for flat control flow:

```python
def detect_existing_framework(self) -> Optional[str]:
    # Guard clause: Early return if no directory
    if not self.project_dir:
        return None

    # Guard clause: Early return for pytest
    if self._has_pytest():
        return "pytest"

    # Guard clause: Early return for jest
    if self._has_jest():
        return "jest"

    # Fallback
    return self._detect_from_imports()
```

## Performance Characteristics

- **Detection**: O(n) file system scans, cached in instance
- **Selection**: O(1) dictionary lookups
- **Configuration**: O(1) dictionary lookups
- **Overall**: O(1) after initial detection, results can be cached

## Thread Safety

Currently not thread-safe. For concurrent usage:
- Create separate instances per thread
- Use locks for shared state
- Consider read-only configurations

## Future Enhancements

1. **Plugin System**: Load strategies from external modules
2. **Configuration Cache**: Persist detection results
3. **ML-Based Selection**: Learn preferences from history
4. **Cloud Integration**: Fetch framework metadata from API
5. **Parallel Detection**: Detect multiple aspects concurrently
6. **Custom Strategies**: User-defined selection strategies
7. **Framework Comparison**: Compare frameworks side-by-side
