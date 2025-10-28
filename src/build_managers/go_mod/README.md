# Go Modules Build Manager - Modularized

## Overview

Enterprise-grade Go modules manager refactored into specialized, single-responsibility modules.

## Architecture

```
build_managers/go_mod/
├── __init__.py                 (26 lines)  - Package exports
├── models.py                   (78 lines)  - Data structures and enums
├── parser.py                  (133 lines)  - go.mod parsing
├── version_detector.py         (83 lines)  - Go installation detection
├── dependency_manager.py      (148 lines)  - Dependency operations
├── build_operations.py        (282 lines)  - Build/test/quality operations
├── manager.py                 (329 lines)  - Main orchestrator
└── cli.py                     (256 lines)  - Command-line interface
```

## Module Breakdown

### models.py (78 lines)
**WHY**: Centralize all data structures and enums
**RESPONSIBILITY**: Type-safe models for build modes, architectures, OS targets, and module info
**EXPORTS**:
- `BuildMode` - Enum for build modes (DEFAULT, PIE, C_ARCHIVE, etc.)
- `GoArch` - Enum for architectures (AMD64, ARM64, ARM, I386)
- `GoOS` - Enum for operating systems (LINUX, DARWIN, WINDOWS, FREEBSD)
- `GoModuleInfo` - Dataclass for go.mod metadata

### parser.py (133 lines)
**WHY**: Dedicated go.mod parsing logic
**RESPONSIBILITY**: Extract all metadata from go.mod files
**KEY FEATURES**:
- Parse module path and Go version
- Extract dependencies from require blocks
- Parse replace and exclude directives
- Validate go.mod structure
**METHODS**:
- `parse_go_mod()` - Main parsing entry point
- Private extraction methods for each directive type

### version_detector.py (83 lines)
**WHY**: Separate Go installation validation
**RESPONSIBILITY**: Detect and validate Go installation
**KEY FEATURES**:
- Execute 'go version' command
- Extract version number via regex
- Validate Go is in PATH
**METHODS**:
- `validate_installation()` - Check Go availability
- `_extract_version()` - Parse version from output

### dependency_manager.py (148 lines)
**WHY**: Centralize dependency operations
**RESPONSIBILITY**: All dependency-related commands
**KEY FEATURES**:
- Install dependencies with version specs
- Download all dependencies
- Tidy unused dependencies
- Verify dependency integrity
**METHODS**:
- `install_dependency()` - Add module via 'go get'
- `download_dependencies()` - Run 'go mod download'
- `tidy()` - Clean go.mod/go.sum
- `verify()` - Verify checksums

### build_operations.py (282 lines)
**WHY**: Centralize build, test, and quality operations
**RESPONSIBILITY**: Execute all build-related commands
**KEY FEATURES**:
- Build with cross-compilation support
- Run tests with coverage/race detection
- Format code (go fmt)
- Static analysis (go vet)
- Clean build cache
- Extract test statistics
**METHODS**:
- `build()` - Compile Go code
- `test()` - Run tests with options
- `fmt()` - Format code
- `vet()` - Static analysis
- `clean()` - Clear cache
- `extract_test_stats()` - Parse test results

### manager.py (329 lines)
**WHY**: Main orchestrator using facade pattern
**RESPONSIBILITY**: Coordinate all operations through unified interface
**KEY FEATURES**:
- Inherits from BuildManagerBase
- Composes all specialized components
- Delegates to appropriate managers
- Maintains backward compatibility
**PATTERN**: Facade - delegates to specialized components

### cli.py (256 lines)
**WHY**: Separate CLI from core logic
**RESPONSIBILITY**: Command-line interface
**KEY FEATURES**:
- Argument parsing
- Command dispatch table
- Structured handlers for each command
**COMMANDS**: info, build, test, get, download, tidy, verify, fmt, vet, clean

## Design Patterns Applied

### 1. Single Responsibility Principle
Each module has one clear purpose:
- `models.py` - Data structures only
- `parser.py` - Parsing only
- `version_detector.py` - Version detection only
- `dependency_manager.py` - Dependencies only
- `build_operations.py` - Build/test/quality only
- `manager.py` - Orchestration only
- `cli.py` - CLI only

### 2. Facade Pattern
`GoModManager` delegates to specialized components:
```python
self._version_detector.validate_installation()
self._dependency_manager.install_dependency(module, version)
self._build_operations.build(output=output, tags=tags)
```

### 3. Dependency Injection
All components accept their dependencies:
```python
GoDependencyManager(execute_command=..., logger=...)
```

### 4. Dispatch Table (CLI)
Command handlers in dictionary instead of elif chain:
```python
command_handlers = {
    "info": self._handle_info,
    "build": self._handle_build,
    ...
}
```

### 5. Guard Clauses
Maximum 1 level of nesting throughout:
```python
if not go_mod_path.exists():
    raise ProjectConfigurationError(...)

# Continue with main logic
```

## Type Safety

All modules use comprehensive type hints:
```python
from typing import Dict, Optional, List, Any, Callable

def build(
    self,
    output: Optional[str] = None,
    tags: Optional[List[str]] = None,
    race: bool = False
) -> BuildResult:
```

## Usage

### New Code (Recommended)
```python
from build_managers.go_mod import GoModManager, BuildMode, GoArch

manager = GoModManager(project_dir="/path/to/project")
result = manager.build(output="app", race=True)
```

### Legacy Code (Backward Compatible)
```python
from go_mod_manager import GoModManager, BuildMode, GoArch

manager = GoModManager(project_dir="/path/to/project")
result = manager.build(output="app", race=True)
```

### Direct Component Usage
```python
from build_managers.go_mod import GoModParser

info = GoModParser.parse_go_mod(go_mod_path, go_sum_path)
print(info.module_path, info.go_version)
```

## Line Count Summary

**Original**: 646 lines (monolithic)
**Refactored**: 1378 lines total (modularized)
- Modular components: 1335 lines
- Backward compatibility wrapper: 43 lines

**Breakdown by module**:
- models.py: 78 lines
- parser.py: 133 lines
- version_detector.py: 83 lines
- dependency_manager.py: 148 lines
- build_operations.py: 282 lines
- manager.py: 329 lines
- cli.py: 256 lines
- __init__.py: 26 lines
- go_mod_manager.py (wrapper): 43 lines

**Added Documentation**: ~113% increase in lines due to:
- Comprehensive WHY/RESPONSIBILITY/PATTERNS documentation
- Detailed docstrings for all methods
- Type hints on all functions
- Inline comments explaining logic
- Guard clauses replacing nested conditions

## Benefits

1. **Testability**: Each component can be tested independently
2. **Maintainability**: Clear separation of concerns
3. **Reusability**: Components can be used independently
4. **Extensibility**: Easy to add new build modes or operations
5. **Type Safety**: Full type hints throughout
6. **Documentation**: Every module/class/method documented
7. **Backward Compatibility**: Existing code works without changes

## Migration Path

1. **Phase 1**: Use backward compatibility wrapper (no changes needed)
2. **Phase 2**: Update imports to new location
3. **Phase 3**: Leverage individual components where needed

## Standards Compliance

- WHY/RESPONSIBILITY/PATTERNS on all modules
- Guard clauses (max 1 level nesting)
- Type hints (List, Dict, Any, Optional, Callable)
- Dispatch tables instead of elif chains
- Single Responsibility Principle throughout
- All code compiles with py_compile
