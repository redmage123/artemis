# Services Core - Quick Reference Guide

## Import Statements

### Recommended (New)
```python
from services.core import TestRunner, HTMLValidator, PipelineLogger, FileManager
```

### Deprecated (Old - Still Works)
```python
from artemis_services import TestRunner, HTMLValidator, PipelineLogger, FileManager
# Warning: Deprecation warning will be shown
```

---

## TestRunner - Test Execution

### Basic Usage
```python
from services.core import TestRunner

runner = TestRunner()
results = runner.run_tests("tests/", timeout=60)

print(f"Pass rate: {results['pass_rate']}")
print(f"Passed: {results['passed']}")
print(f"Failed: {results['failed']}")
```

### With Custom Pytest Path
```python
from services.core import create_test_runner

runner = create_test_runner(pytest_path="/custom/pytest")
results = runner.run_tests("tests/unit/")
```

### Result Dictionary
```python
{
    "total": 10,           # Total tests run
    "passed": 8,           # Tests passed
    "failed": 1,           # Tests failed
    "skipped": 1,          # Tests skipped
    "pass_rate": "80.0%",  # Pass rate percentage
    "exit_code": 1,        # Pytest exit code (0 = all passed)
    "output": "..."        # Full pytest output
}
```

---

## HTMLValidator - HTML Validation

### Basic Validation
```python
from services.core import HTMLValidator
from pathlib import Path

validator = HTMLValidator()
result = validator.validate(Path("index.html"))

if result['status'] == 'PASS':
    print("HTML is valid!")
else:
    print(f"Errors: {result['note']}")
```

### Strict Validation (NEW)
```python
from services.core import create_html_validator

# Strict mode checks: DOCTYPE, lang, head, body
validator = create_html_validator(strict=True)
result = validator.validate(Path("page.html"))
```

### With Different Parser
```python
# Options: 'html.parser' (default), 'lxml', 'xml', 'html5lib'
validator = HTMLValidator(parser='lxml')
result = validator.validate(Path("index.html"))
```

### Result Dictionary
```python
{
    "status": "PASS",                    # PASS or FAIL
    "errors": 0,                         # Number of errors
    "note": "HTML is valid",             # Human-readable message
    "file_path": "/path/to/file.html"    # Path to validated file
}
```

---

## PipelineLogger - Formatted Logging

### Basic Logging
```python
from services.core import PipelineLogger

logger = PipelineLogger(verbose=True)

logger.info("Processing started")        # ℹ️ [12:34:56] Processing started
logger.success("Task completed")         # ✅ [12:34:57] Task completed
logger.warning("Low disk space")         # ⚠️ [12:34:58] Low disk space
logger.error("Task failed")              # ❌ [12:34:59] Task failed
```

### Extended Log Levels (NEW)
```python
logger.debug("Debug info")               # 🔍 Debug info
logger.critical("System failure")        # 🔥 System failure
logger.stage("Starting stage 2")         # 🔄 Starting stage 2
logger.pipeline("Pipeline initialized")  # ⚙️ Pipeline initialized
```

### Silent Logger for Testing
```python
from services.core import create_silent_logger

logger = create_silent_logger()
logger.info("This won't print")
```

### Control Verbosity
```python
logger = PipelineLogger(verbose=True)
logger.set_verbose(False)  # Turn off logging
logger.info("Silent")
logger.set_verbose(True)   # Turn on logging
logger.info("Visible")
```

---

## FileManager - File Operations

### JSON Operations
```python
from services.core import FileManager
from pathlib import Path

# Read JSON
data = FileManager.read_json("config.json")

# Write JSON
FileManager.write_json("output.json", {"key": "value"}, indent=2)
```

### Text Operations
```python
# Read text
content = FileManager.read_text("README.md")

# Write text
FileManager.write_text("output.txt", "Hello, World!")

# Append text (NEW)
FileManager.append_text("log.txt", "New log entry\n")
```

### Line Operations (NEW)
```python
# Read lines (newlines stripped)
lines = FileManager.read_lines("data.txt")
for line in lines:
    print(line)

# Write lines (adds newlines)
FileManager.write_lines("output.txt", ["Line 1", "Line 2", "Line 3"])
```

### Directory Operations
```python
# Ensure directory exists (creates if needed)
FileManager.ensure_directory("output/reports/2024")

# Check if directory exists
if FileManager.directory_exists("output"):
    print("Directory exists")
```

### File Utilities (NEW)
```python
# Check if file exists
if FileManager.file_exists("config.json"):
    config = FileManager.read_json("config.json")

# Get file size in bytes
size = FileManager.get_file_size("data.json")
print(f"File size: {size} bytes")

# Delete file (safe - won't fail if doesn't exist)
FileManager.delete_file("temp.txt")
```

---

## Service Registry - Service Management

### Initialize All Services
```python
from services.core import initialize_services, ServiceRegistry

# One-line setup
initialize_services(verbose=True)

# Get services from registry
logger = ServiceRegistry.get('logger')
runner = ServiceRegistry.get('test_runner')
validator = ServiceRegistry.get('html_validator')
file_manager = ServiceRegistry.get('file_manager')
```

### Register Custom Services
```python
from services.core import ServiceRegistry, PipelineLogger

# Create and register custom service
custom_logger = PipelineLogger(verbose=False)
ServiceRegistry.register('custom_logger', custom_logger)

# Retrieve later
logger = ServiceRegistry.get('custom_logger')
```

### Check Service Registration
```python
if ServiceRegistry.has('logger'):
    logger = ServiceRegistry.get('logger')
else:
    logger = PipelineLogger()
    ServiceRegistry.register('logger', logger)
```

### Clear Services (for Testing)
```python
# Clear all registered services
ServiceRegistry.clear()
```

---

## Factory Functions - Dependency Injection

### Create Services with Custom Configuration
```python
from services.core import (
    create_test_runner,
    create_html_validator,
    create_logger,
    create_silent_logger,
    create_file_manager
)

# Test runner with custom pytest path
runner = create_test_runner(pytest_path="/usr/local/bin/pytest")

# HTML validator with strict mode
validator = create_html_validator(parser='lxml', strict=True)

# Logger with custom verbosity
logger = create_logger(verbose=True)

# Silent logger for testing
silent_logger = create_silent_logger()

# File manager (for consistency)
fm = create_file_manager()
```

### Create Default Services
```python
from services.core import create_default_services

# Get all default services as dict
services = create_default_services()

logger = services['logger']
runner = services['test_runner']
validator = services['html_validator']
fm = services['file_manager']
```

---

## Common Patterns

### Pipeline Stage with Logging
```python
from services.core import PipelineLogger

def my_pipeline_stage(logger: PipelineLogger):
    logger.stage("Starting my stage...")

    try:
        # Do work
        logger.info("Processing items...")
        # ...
        logger.success("Stage completed!")
    except Exception as e:
        logger.error(f"Stage failed: {e}")
        raise

# Use it
logger = PipelineLogger()
my_pipeline_stage(logger)
```

### Test Execution with Results
```python
from services.core import TestRunner, PipelineLogger, FileManager

logger = PipelineLogger()
runner = TestRunner()

logger.stage("Running test suite...")
results = runner.run_tests("tests/")

if results['exit_code'] == 0:
    logger.success(f"All tests passed! ({results['pass_rate']})")
else:
    logger.error(f"Tests failed! {results['failed']} failures")

# Save results
FileManager.write_json("test_results.json", results)
```

### HTML Validation Pipeline
```python
from services.core import HTMLValidator, PipelineLogger, FileManager
from pathlib import Path

logger = PipelineLogger()
validator = HTMLValidator(strict=True)

html_files = Path("dist").glob("**/*.html")
results = []

for html_file in html_files:
    logger.info(f"Validating {html_file.name}...")
    result = validator.validate(html_file)
    results.append(result)

    if result['status'] == 'FAIL':
        logger.error(f"Validation failed: {result['note']}")

# Save validation report
FileManager.write_json("validation_report.json", {
    "total": len(results),
    "passed": sum(1 for r in results if r['status'] == 'PASS'),
    "failed": sum(1 for r in results if r['status'] == 'FAIL'),
    "results": results
})
```

---

## Migration from Old Code

### Before (Old)
```python
from artemis_services import TestRunner, PipelineLogger

logger = PipelineLogger(verbose=True)
runner = TestRunner()

logger.info("Starting tests...")
results = runner.run_tests("tests/")
```

### After (New)
```python
from services.core import TestRunner, PipelineLogger

logger = PipelineLogger(verbose=True)
runner = TestRunner()

logger.info("Starting tests...")
results = runner.run_tests("tests/")
```

**No code changes needed - just update the import!**

---

## New Features Summary

### TestRunner
- ✅ Configurable pytest arguments
- ✅ Better error messages
- ✅ Factory function support

### HTMLValidator
- ✅ **Strict validation mode** (NEW)
- ✅ **Multiple parser support** (NEW)
- ✅ Enhanced error reporting

### PipelineLogger
- ✅ **Extended log levels** (SUCCESS, CRITICAL, STAGE, etc.) (NEW)
- ✅ **Custom formatter support** (NEW)
- ✅ **Runtime verbosity control** (NEW)

### FileManager
- ✅ **Line-based operations** (NEW)
- ✅ **File existence checks** (NEW)
- ✅ **File size queries** (NEW)
- ✅ **Safe file deletion** (NEW)

### Service Management
- ✅ **ServiceRegistry** for centralized management (NEW)
- ✅ **Factory functions** for all services (NEW)
- ✅ **One-line initialization** (NEW)

---

## Quick Tips

1. **Use factory functions for testing**: `create_silent_logger()` for tests
2. **Use ServiceRegistry for pipelines**: Centralized service management
3. **Use strict mode for production HTML**: Catches more issues early
4. **Use guard clauses in your code**: Follow the pattern from services.core
5. **Check the deprecation warning**: Update imports to services.core

---

## Help and Documentation

- **Full API Docs**: See individual module files in `services/core/`
- **Package Structure**: See `services/core/PACKAGE_STRUCTURE.md`
- **Refactoring Report**: See `SERVICES_CORE_REFACTORING_REPORT.md`
- **This Quick Reference**: `services/core/QUICK_REFERENCE.md`

---

**Version:** 1.0.0
**Status:** ✅ Production Ready
**Compatibility:** 100% backward compatible with artemis_services.py
