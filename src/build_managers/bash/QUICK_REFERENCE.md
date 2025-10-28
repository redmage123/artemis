# Bash Manager - Quick Reference Guide

## Package Structure

```
build_managers/bash/
├── __init__.py           - Package exports
├── models.py            - Data structures (233 lines)
├── script_detector.py   - Script discovery (285 lines)
├── linter.py           - Shellcheck wrapper (283 lines)
├── formatter.py        - Shfmt wrapper (303 lines)
├── test_runner.py      - Bats test runner (345 lines)
└── manager.py          - Main orchestrator (317 lines)
```

---

## Basic Usage

### Simple Detection and Build

```python
from build_managers.bash import BashManager
from pathlib import Path

# Initialize
manager = BashManager(Path("/path/to/project"))

# Detect if bash project
if manager.detect():
    # Run quality checks (shellcheck + shfmt)
    success = manager.build()

    # Run tests
    if manager.run_tests():
        print("All checks passed!")
```

---

## Advanced Usage

### Custom Configuration

```python
from build_managers.bash import (
    BashManager,
    QualityCheckConfig,
    ShellDialect,
    CheckSeverity
)

# Create custom config
config = QualityCheckConfig(
    shell_dialect=ShellDialect.BASH,
    min_severity=CheckSeverity.WARNING,
    shfmt_indent=4,
    shfmt_case_indent=True,
    enable_shellcheck=True,
    enable_shfmt=True
)

# Apply to manager (after initialization)
manager = BashManager(project_dir)
manager.config = config
```

### Direct Component Usage

```python
from build_managers.bash import (
    ScriptDetector,
    ShellcheckLinter,
    ShfmtFormatter,
    BatsTestRunner,
    QualityCheckConfig
)
import subprocess
from pathlib import Path

# Script detection
detector = ScriptDetector(project_dir=Path.cwd())
scripts = detector.detect_scripts()
print(f"Found {len(scripts)} scripts")

# Linting
def execute_cmd(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

config = QualityCheckConfig()
linter = ShellcheckLinter(config, execute_cmd)
lint_results = linter.lint_scripts(scripts)

for result in lint_results:
    if not result.passed:
        print(f"✗ {result.script.name}: {len(result.errors)} errors")

# Formatting
formatter = ShfmtFormatter(config, execute_cmd)
format_results = formatter.check_formats(scripts)

# Testing
test_runner = BatsTestRunner(Path.cwd(), execute_cmd)
test_result = test_runner.run_tests()
print(f"Tests: {test_result.tests_passed}/{test_result.tests_run}")
```

---

## Data Models

### ShellScript (Immutable)

```python
from build_managers.bash import ShellScript
from pathlib import Path

script = ShellScript(
    path=Path("/project/script.sh"),
    relative_path=Path("script.sh"),
    size_bytes=1024
)

# Properties
print(script.name)           # "script.sh"
print(script.relative_path)  # "script.sh"
print(script.size_bytes)     # 1024
```

### LintResult (Immutable)

```python
result = linter.lint_script(script)

if result.passed:
    print("✓ Linting passed")
else:
    print(f"✗ Errors: {len(result.errors)}")
    print(f"⚠ Warnings: {len(result.warnings)}")

    for error in result.errors:
        print(f"  - {error}")
```

### FormatResult (Immutable)

```python
result = formatter.check_format(script)

if result.formatted:
    print("✓ Properly formatted")
else:
    print("✗ Needs formatting:")
    print(result.diff)
```

### TestResult (Immutable)

```python
result = test_runner.run_tests()

print(f"Tests run: {result.tests_run}")
print(f"Passed: {result.tests_passed}")
print(f"Failed: {result.tests_failed}")
print(f"Skipped: {result.tests_skipped}")
print(f"Duration: {result.duration:.2f}s")
```

---

## Enums

### ShellDialect

```python
from build_managers.bash import ShellDialect

config.shell_dialect = ShellDialect.BASH   # Bash
config.shell_dialect = ShellDialect.SH     # POSIX sh
config.shell_dialect = ShellDialect.DASH   # Debian Almquist shell
config.shell_dialect = ShellDialect.KSH    # Korn shell
config.shell_dialect = ShellDialect.ZSH    # Z shell
```

### CheckSeverity

```python
from build_managers.bash import CheckSeverity

config.min_severity = CheckSeverity.ERROR    # Only errors
config.min_severity = CheckSeverity.WARNING  # Warnings and above
config.min_severity = CheckSeverity.INFO     # Info and above
config.min_severity = CheckSeverity.STYLE    # All issues
```

---

## Filtering and Grouping

### Filter Scripts

```python
detector = ScriptDetector(project_dir)
all_scripts = detector.detect_scripts()

# Filter large scripts (>10KB)
large_scripts = detector.filter_scripts(
    all_scripts,
    lambda s: s.size_bytes > 10240
)

# Filter by name pattern
test_scripts = detector.filter_scripts(
    all_scripts,
    lambda s: "test" in s.name.lower()
)
```

### Group by Directory

```python
grouped = detector.get_scripts_by_directory(all_scripts)

for directory, scripts in grouped.items():
    print(f"{directory}: {len(scripts)} scripts")
```

---

## Error Handling

### Graceful Degradation

All components handle errors gracefully:

```python
# If shellcheck not installed
lint_results = linter.lint_scripts(scripts)
# Returns results with error messages, doesn't crash

# If bats not installed
test_result = test_runner.run_tests()
# Returns error result, doesn't crash

# If no tests exist
test_result = test_runner.run_tests()
# Returns "no tests" result (passed=True)
```

### Result Pattern

```python
# All operations return Result objects
lint_result = linter.lint_script(script)
format_result = formatter.check_format(script)
test_result = test_runner.run_tests()

# Always check passed flag
if result.passed:
    # Success
else:
    # Handle failure
    print(result.output)
```

---

## Project Metadata

```python
metadata = manager.get_metadata()

print(f"Manager: {metadata['manager']}")
print(f"Scripts: {metadata['script_count']}")
print(f"Has tests: {metadata['has_tests']}")
print(f"Total size: {metadata['total_size_bytes']} bytes")

for script in metadata['shell_scripts']:
    print(f"  - {script}")
```

---

## Design Patterns

### Template Method
```python
# BashManager extends BuildManagerBase
class BashManager(BuildManagerBase):
    def detect(self) -> bool: ...
    def build(self) -> bool: ...
    def run_tests(self) -> bool: ...
```

### Strategy Pattern
```python
# Configurable behavior via QualityCheckConfig
config = QualityCheckConfig(
    shell_dialect=ShellDialect.BASH,
    min_severity=CheckSeverity.WARNING
)
```

### Facade Pattern
```python
# BashManager provides simple API
manager = BashManager(project_dir)
manager.build()  # Internally: detect → lint → format
```

### Composition
```python
# BashManager delegates to components
class BashManager:
    def __init__(self):
        self.detector = ScriptDetector(...)
        self.linter = ShellcheckLinter(...)
        self.formatter = ShfmtFormatter(...)
```

### Value Objects
```python
# All data models are immutable
@dataclass(frozen=True)
class ShellScript:
    path: Path
    relative_path: Path
    size_bytes: int
```

---

## Testing

### Unit Testing Components

```python
import unittest
from unittest.mock import Mock
from build_managers.bash import ShellcheckLinter, QualityCheckConfig

class TestLinter(unittest.TestCase):
    def test_lint_script(self):
        # Mock command executor
        mock_executor = Mock()
        mock_executor.return_value = Mock(
            returncode=0,
            stdout="",
            stderr=""
        )

        # Create linter with mock
        config = QualityCheckConfig()
        linter = ShellcheckLinter(config, mock_executor)

        # Test
        script = ShellScript(...)
        result = linter.lint_script(script)

        # Assert
        self.assertTrue(result.passed)
        mock_executor.assert_called_once()
```

---

## Migration from Old API

### Before (Monolithic)
```python
from bash_manager import BashManager

manager = BashManager(project_dir)
manager.detect()
manager.build()
```

### After (Modular) - Still Works!
```python
# Same exact code works
from bash_manager import BashManager

manager = BashManager(project_dir)
manager.detect()
manager.build()
```

### After (Recommended)
```python
# New import path
from build_managers.bash import BashManager

manager = BashManager(project_dir)
manager.detect()
manager.build()
```

---

## Common Patterns

### Full Build Pipeline

```python
from build_managers.bash import BashManager
from pathlib import Path

def build_pipeline(project_path: str) -> bool:
    manager = BashManager(Path(project_path))

    # 1. Detect
    if not manager.detect():
        print("Not a bash project")
        return False

    # 2. Install dependencies (no-op for bash)
    manager.install_dependencies()

    # 3. Build (lint + format)
    if not manager.build():
        print("Build failed")
        return False

    # 4. Test
    if not manager.run_tests():
        print("Tests failed")
        return False

    # 5. Clean (no-op for bash)
    manager.clean()

    return True
```

### Custom Quality Checks

```python
from build_managers.bash import (
    BashManager,
    ScriptDetector,
    ShellcheckLinter,
    QualityCheckConfig,
    CheckSeverity
)

def strict_quality_check(project_dir):
    # Strict configuration
    config = QualityCheckConfig(
        min_severity=CheckSeverity.STYLE,  # Even style issues fail
        enable_shellcheck=True,
        enable_shfmt=True
    )

    # Detect scripts
    detector = ScriptDetector(project_dir)
    scripts = detector.detect_scripts()

    # Lint with strict config
    linter = ShellcheckLinter(config, subprocess.run)
    results = linter.lint_scripts(scripts)

    # Report
    for result in results:
        if not result.passed:
            print(f"✗ {result.script.name}")
            for error in result.errors:
                print(f"  ERROR: {error}")
            for warning in result.warnings:
                print(f"  WARN: {warning}")

    return linter.all_passed(results)
```

---

## Performance Tips

1. **Reuse Detector:** Create once, call `detect_scripts()` once
2. **Batch Operations:** Use `lint_scripts()` not individual `lint_script()`
3. **Filter Early:** Use `filter_scripts()` before expensive operations
4. **Cache Results:** Store results in variables, don't recompute

```python
# Good: Reuse detector results
detector = ScriptDetector(project_dir)
scripts = detector.detect_scripts()  # Once
large_scripts = detector.filter_scripts(scripts, lambda s: s.size_bytes > 1024)
linter.lint_scripts(large_scripts)

# Bad: Multiple traversals
if detector.has_scripts():
    scripts = detector.detect_scripts()  # Traversal #1
    more_scripts = detector.detect_scripts()  # Traversal #2 (unnecessary)
```

---

## See Also

- **REFACTORING_REPORT.md** - Complete refactoring documentation
- **models.py** - Data structure reference
- **manager.py** - Main API implementation
