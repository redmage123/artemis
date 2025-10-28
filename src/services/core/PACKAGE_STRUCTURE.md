# Services Core Package Structure

## Directory Tree

```
services/core/
├── __init__.py (176 lines)
│   ├── TestRunner (re-export)
│   ├── HTMLValidator (re-export)
│   ├── PipelineLogger (re-export)
│   ├── FileManager (re-export)
│   ├── ServiceRegistry (Service Locator)
│   ├── create_default_services() (Factory)
│   └── initialize_services() (Convenience)
│
├── test_runner.py (181 lines)
│   ├── TestRunner class
│   │   ├── run_tests(test_path, timeout)
│   │   └── _parse_pytest_output(output)
│   └── create_test_runner(pytest_path) (Factory)
│
├── html_validator.py (313 lines)
│   ├── HTMLValidator class
│   │   ├── validate(file_path)
│   │   ├── _is_html_file(file_path)
│   │   ├── _read_html_file(file_path)
│   │   ├── _parse_html(html_content)
│   │   ├── _strict_validation(soup, file_path)
│   │   └── _create_result(status, errors, note, file_path)
│   └── create_html_validator(parser, strict) (Factory)
│
├── pipeline_logger.py (340 lines)
│   ├── PipelineLogger class
│   │   ├── log(message, level, **kwargs)
│   │   ├── _get_timestamp()
│   │   ├── _get_emoji(level)
│   │   ├── _format_message(timestamp, emoji, message)
│   │   ├── debug(message, **kwargs)
│   │   ├── info(message, **kwargs)
│   │   ├── warning(message, **kwargs)
│   │   ├── error(message, **kwargs)
│   │   ├── critical(message, **kwargs)
│   │   ├── success(message, **kwargs)
│   │   ├── stage(message, **kwargs)
│   │   ├── pipeline(message, **kwargs)
│   │   ├── set_verbose(verbose)
│   │   └── is_verbose()
│   ├── create_logger(verbose) (Factory)
│   └── create_silent_logger() (Factory)
│
└── file_manager.py (443 lines)
    ├── FileManager class (static methods)
    │   ├── read_json(file_path)
    │   ├── write_json(file_path, data, indent)
    │   ├── read_text(file_path)
    │   ├── write_text(file_path, content)
    │   ├── read_lines(file_path)
    │   ├── write_lines(file_path, lines)
    │   ├── append_text(file_path, content)
    │   ├── ensure_directory(dir_path)
    │   ├── file_exists(file_path)
    │   ├── directory_exists(dir_path)
    │   ├── delete_file(file_path)
    │   └── get_file_size(file_path)
    └── create_file_manager() (Factory)
```

## Module Dependencies

```
services/core/
├── test_runner.py
│   └── depends on: core.interfaces.TestRunnerInterface
│                   core.constants.PYTEST_PATH
│
├── html_validator.py
│   └── depends on: core.interfaces.ValidatorInterface
│                   bs4.BeautifulSoup (external)
│
├── pipeline_logger.py
│   └── depends on: core.interfaces.LoggerInterface
│
└── file_manager.py
    └── depends on: (no external dependencies, stdlib only)
```

## Import Patterns

### Old Way (Deprecated)
```python
from artemis_services import TestRunner, HTMLValidator, PipelineLogger, FileManager
```

### New Way (Recommended)
```python
from services.core import TestRunner, HTMLValidator, PipelineLogger, FileManager
```

### With Service Registry
```python
from services.core import initialize_services, ServiceRegistry

initialize_services(verbose=True)
logger = ServiceRegistry.get('logger')
runner = ServiceRegistry.get('test_runner')
```

### With Factory Functions
```python
from services.core import create_logger, create_test_runner

logger = create_logger(verbose=True)
runner = create_test_runner(pytest_path="/custom/pytest")
```

## Class Hierarchy

```
TestRunnerInterface (core.interfaces)
    └── TestRunner (services.core.test_runner)

ValidatorInterface (core.interfaces)
    └── HTMLValidator (services.core.html_validator)

LoggerInterface (core.interfaces)
    └── PipelineLogger (services.core.pipeline_logger)

(No interface)
    └── FileManager (services.core.file_manager)
        └── Static methods only
```

## Design Patterns Used

### 1. Service Layer Pattern
- **All modules**: Encapsulate business logic as services
- **Benefit**: Clear separation of concerns

### 2. Factory Method Pattern
- `create_test_runner()`
- `create_html_validator()`
- `create_logger()` / `create_silent_logger()`
- `create_file_manager()`
- `create_default_services()`
- **Benefit**: Dependency injection, easier testing

### 3. Service Locator Pattern
- `ServiceRegistry` class in `__init__.py`
- **Methods**: `register()`, `get()`, `has()`, `clear()`
- **Benefit**: Centralized service management

### 4. Singleton Pattern (Optional)
- Services can be registered once in ServiceRegistry
- **Benefit**: Single instance across pipeline

### 5. Strategy Pattern
- `HTMLValidator`: Multiple parsers (html.parser, lxml, etc.)
- `PipelineLogger`: Custom formatters
- **Benefit**: Runtime algorithm selection

### 6. Dispatch Table Pattern
- `PipelineLogger.EMOJI_MAP`: Log level → emoji
- `HTMLValidator.PARSER_OPTIONS`: Parser name → parser
- **Benefit**: No if/elif chains, easy to extend

### 7. Guard Clause Pattern
- **All methods**: Early return on invalid input
- **Benefit**: Max 1 level nesting, readable code

## API Summary

### TestRunner
```python
runner = TestRunner(pytest_path="/usr/bin/pytest")
results = runner.run_tests("tests/", timeout=60)
# Returns: {total, passed, failed, skipped, pass_rate, exit_code, output}
```

### HTMLValidator
```python
validator = HTMLValidator(parser='html.parser', strict=False)
result = validator.validate(Path("index.html"))
# Returns: {status, errors, note, file_path}

# Strict mode (new feature)
validator_strict = HTMLValidator(strict=True)
result = validator_strict.validate(Path("page.html"))
# Also checks: DOCTYPE, lang, head, body
```

### PipelineLogger
```python
logger = PipelineLogger(verbose=True)
logger.info("Information message")      # ℹ️
logger.success("Success message")       # ✅
logger.warning("Warning message")       # ⚠️
logger.error("Error message")           # ❌
logger.critical("Critical message")     # 🔥
logger.stage("Stage message")           # 🔄
logger.pipeline("Pipeline message")     # ⚙️
logger.set_verbose(False)               # Silence output
```

### FileManager
```python
# JSON operations
data = FileManager.read_json("config.json")
FileManager.write_json("output.json", data, indent=2)

# Text operations
content = FileManager.read_text("README.md")
FileManager.write_text("output.txt", "Hello!")

# Line operations (new features)
lines = FileManager.read_lines("data.txt")
FileManager.write_lines("output.txt", ["Line 1", "Line 2"])
FileManager.append_text("log.txt", "New entry\n")

# Utilities (new features)
FileManager.ensure_directory("output/reports/")
exists = FileManager.file_exists("config.json")
size = FileManager.get_file_size("data.json")
FileManager.delete_file("temp.txt")
```

### ServiceRegistry
```python
# Register services
ServiceRegistry.register('logger', PipelineLogger(verbose=True))
ServiceRegistry.register('runner', TestRunner())

# Retrieve services
logger = ServiceRegistry.get('logger')
runner = ServiceRegistry.get('runner')

# Check registration
if ServiceRegistry.has('logger'):
    logger = ServiceRegistry.get('logger')

# Clear all (for testing)
ServiceRegistry.clear()
```

## File Size Summary

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 176 | Package exports + ServiceRegistry |
| `test_runner.py` | 181 | Test execution via pytest |
| `html_validator.py` | 313 | HTML syntax/structure validation |
| `pipeline_logger.py` | 340 | Formatted console logging |
| `file_manager.py` | 443 | File I/O operations |
| **Total** | **1,453** | **Complete service layer** |

## Quality Metrics

- ✅ **100% type hints** on all public methods
- ✅ **100% guard clauses** (max 1 level nesting)
- ✅ **0 if/elif chains** (all use dispatch tables)
- ✅ **WHY/RESPONSIBILITY/PATTERNS** docs on all modules
- ✅ **Factory functions** for all services
- ✅ **Service locator** for centralized management
- ✅ **Backward compatible** (100% with artemis_services.py)
- ✅ **Compilation verified** (all modules compile)

## Testing Strategy

### Unit Testing
```python
from services.core import create_silent_logger, create_test_runner

def test_with_silent_logger():
    logger = create_silent_logger()
    logger.info("This won't print")
    assert logger.is_verbose() == False

def test_with_mock_runner():
    runner = create_test_runner(pytest_path="/mock/pytest")
    # Test with mock...
```

### Integration Testing
```python
from services.core import initialize_services, ServiceRegistry

def test_service_integration():
    ServiceRegistry.clear()
    initialize_services(verbose=False)

    runner = ServiceRegistry.get('test_runner')
    logger = ServiceRegistry.get('logger')

    # Test integration...
```

## Maintenance Guide

### Adding a New Service
1. Create new file in `services/core/`
2. Implement service class with interface
3. Add factory function
4. Export in `__init__.py`
5. Add to `create_default_services()`
6. Update this documentation

### Adding a New Feature
1. Add method to appropriate service class
2. Add guard clauses for validation
3. Add type hints
4. Document with WHY/WHAT
5. Add usage example in docstring
6. Update package documentation

### Adding a New Pattern
1. Use dispatch table for conditionals
2. Use guard clauses for validation
3. Use factory functions for DI
4. Document pattern choice in WHY section

---

**Package Version:** 1.0.0
**Last Updated:** 2025-10-28
**Status:** ✅ Production Ready
