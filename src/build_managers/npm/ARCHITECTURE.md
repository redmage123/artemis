# NPM Manager Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         npm_manager.py (86 lines)                        │
│                      Backward Compatibility Wrapper                      │
│                                                                           │
│  Re-exports all components from build_managers.npm                       │
│  Maintains old import paths: from npm_manager import NpmManager          │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ imports from
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   build_managers/npm/__init__.py (62 lines)              │
│                            Package Interface                             │
│                                                                           │
│  Exports: NpmManager, PackageManager, NpmProjectInfo,                    │
│          all component managers, all CLI handlers                        │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│   models.py (91 lines)           │   │  cli_handlers.py (207 lines)     │
│   Data Models                    │   │  CLI Interface                   │
│                                  │   │                                  │
│  • PackageManager(Enum)          │   │  • handle_info()                 │
│    - NPM                         │   │  • handle_build()                │
│    - YARN                        │   │  • handle_test()                 │
│    - PNPM                        │   │  • handle_install()              │
│                                  │   │  • handle_clean()                │
│  • NpmProjectInfo(dataclass)     │   │  • get_command_handlers()        │
│    - name, version               │   │  • create_argument_parser()      │
│    - dependencies                │   │  • execute_cli_command()         │
│    - scripts                     │   │                                  │
│    - to_dict()                   │   │  PATTERN: Command pattern        │
│                                  │   │  DISPATCH: Command routing       │
│  PATTERN: DTO, Enum              │   └──────────────────────────────────┘
└──────────────────────────────────┘
                    │
                    │ used by all components
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              manager_core.py (342 lines) - NpmManager                    │
│                         Main Orchestrator                                │
│                                                                           │
│  Inherits: BuildManagerBase                                              │
│  Registers: @register_build_manager(BuildSystem.NPM)                     │
│                                                                           │
│  Delegates to component managers:                                        │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ self.config_parser    → Configuration operations                 │   │
│  │ self.version_manager  → Version detection and validation         │   │
│  │ self.dependency_mgr   → Dependency installation/removal          │   │
│  │ self.build_ops        → Build, test, script execution            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                           │
│  Public API:                                                              │
│  • get_project_info() → config_parser                                    │
│  • build()           → build_ops                                         │
│  • test()            → build_ops                                         │
│  • install_dep()     → dependency_mgr                                    │
│  • install_deps()    → dependency_mgr                                    │
│  • clean()           → build_ops                                         │
│                                                                           │
│  PATTERN: Facade, Composition, Template Method                           │
└─────────────────────────────────────────────────────────────────────────┘
          │                │                 │                  │
          │                │                 │                  │
          ▼                ▼                 ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐  ┌──────────────────┐
│config_parser │ │version_mgr   │ │dependency_mgr│  │build_operations  │
│(157 lines)   │ │(114 lines)   │ │(251 lines)   │  │(328 lines)       │
│              │ │              │ │              │  │                  │
│Configuration │ │Version       │ │Dependency    │  │Build & Test      │
│Parsing       │ │Detection     │ │Management    │  │Operations        │
│              │ │              │ │              │  │                  │
│• validate_   │ │• detect_pkg_ │ │• install_dep │  │• build()         │
│  project()   │ │  manager()   │ │• install_    │  │• test()          │
│• parse_      │ │  - pnpm-lock │ │  deps()      │  │• run_script()    │
│  project_    │ │  - yarn.lock │ │• remove_dep  │  │• clean()         │
│  info()      │ │  - default   │ │              │  │• extract_test_   │
│• get_        │ │    to npm    │ │DISPATCH:     │  │  stats()         │
│  scripts()   │ │• validate_   │ │• _install_   │  │                  │
│• has_script()│ │  install()   │ │  commands    │  │PARSERS:          │
│              │ │              │ │  {npm, yarn, │  │• Jest output     │
│PATTERN:      │ │PATTERN:      │ │   pnpm}      │  │• Mocha output    │
│Parser,       │ │Strategy,     │ │• _dev_flags  │  │                  │
│Guard clauses │ │Guard clauses │ │• _remove_cmd │  │PATTERN:          │
│              │ │              │ │              │  │Command,          │
│              │ │              │ │PATTERN:      │  │Strategy,         │
│              │ │              │ │Strategy,     │  │Template Method   │
│              │ │              │ │Dispatch      │  │                  │
└──────────────┘ └──────────────┘ └──────────────┘  └──────────────────┘
```

## Data Flow

### 1. Initialization Flow
```
User creates NpmManager
        ↓
NpmManager.__init__()
        ↓
Detect package manager (version_manager.detect_package_manager())
        ├─ Check pnpm-lock.yaml → PackageManager.PNPM
        ├─ Check yarn.lock → PackageManager.YARN
        └─ Default → PackageManager.NPM
        ↓
super().__init__() [BuildManagerBase]
        ↓
_validate_installation() → version_manager.validate_installation()
        ↓
_validate_project() → config_parser.validate_project()
        ↓
_init_components()
        ├─ Create config_parser
        ├─ Create version_manager
        ├─ Create dependency_manager
        └─ Create build_ops
```

### 2. Build Flow
```
npm.build(script_name="build", production=True)
        ↓
NpmManager.build()
        ↓
Check script exists (config_parser.has_script())
        ↓
build_ops.build(script_name, production)
        ↓
Build command based on package manager
        ├─ npm: ["npm", "run", "build", "--production"]
        ├─ yarn: ["yarn", "run", "build"]
        └─ pnpm: ["pnpm", "run", "build"]
        ↓
self._execute_command() [from BuildManagerBase]
        ↓
Return BuildResult
```

### 3. Dependency Installation Flow
```
npm.install_dependency("react", version="18.2.0", dev=False)
        ↓
NpmManager.install_dependency()
        ↓
dependency_manager.install_dependency()
        ↓
_build_install_command()
        ↓
Dispatch table lookup:
        ├─ npm: ["npm", "install", "react@18.2.0"]
        ├─ yarn: ["yarn", "add", "react@18.2.0"]
        └─ pnpm: ["pnpm", "add", "react@18.2.0"]
        ↓
Add dev flag if needed (dispatch table):
        ├─ npm: --save-dev
        ├─ yarn: --dev
        └─ pnpm: --dev
        ↓
self._execute_command()
        ↓
Return True on success
```

### 4. Test Flow
```
npm.test(coverage=True)
        ↓
NpmManager.test()
        ↓
build_ops.test(coverage=True)
        ↓
Build command: ["npm", "test", "--coverage"]
        ↓
self._execute_command()
        ↓
Parse output (extract_test_stats())
        ├─ Try Jest parser (_parse_jest_output())
        │   Pattern: "Tests: X passed, Y total"
        ├─ Try Mocha parser (_parse_mocha_output())
        │   Pattern: "X passing", "Y failing"
        └─ Return stats dict
        ↓
Return BuildResult with test statistics
```

## Component Dependencies

```
manager_core.py
    ├─ depends on → models.py (PackageManager, NpmProjectInfo)
    ├─ depends on → config_parser.py (NpmConfigParser)
    ├─ depends on → version_manager.py (VersionManager)
    ├─ depends on → dependency_manager.py (DependencyManager)
    ├─ depends on → build_operations.py (BuildOperations)
    └─ inherits → BuildManagerBase (from parent)

config_parser.py
    ├─ depends on → models.py (NpmProjectInfo, PackageManager)
    ├─ uses → artemis_exceptions.wrap_exception
    └─ uses → build_system_exceptions.ProjectConfigurationError

version_manager.py
    ├─ depends on → models.py (PackageManager)
    ├─ uses → artemis_exceptions.wrap_exception
    ├─ uses → build_system_exceptions.BuildSystemNotFoundError
    └─ uses → build_manager_base.BuildResult

dependency_manager.py
    ├─ depends on → models.py (PackageManager)
    ├─ uses → artemis_exceptions.wrap_exception
    ├─ uses → build_system_exceptions (multiple)
    └─ uses → build_manager_base.BuildResult

build_operations.py
    ├─ depends on → models.py (PackageManager)
    ├─ uses → artemis_exceptions.wrap_exception
    ├─ uses → build_system_exceptions (multiple)
    └─ uses → build_manager_base.BuildResult

cli_handlers.py
    └─ depends on → manager_core.py (NpmManager)

__init__.py
    ├─ exports → models.py (all)
    ├─ exports → config_parser.py (NpmConfigParser)
    ├─ exports → version_manager.py (VersionManager)
    ├─ exports → dependency_manager.py (DependencyManager)
    ├─ exports → build_operations.py (BuildOperations)
    ├─ exports → cli_handlers.py (all handlers)
    └─ exports → manager_core.py (NpmManager)

npm_manager.py (wrapper)
    └─ re-exports → build_managers.npm.__init__ (all)
```

## Responsibility Matrix

| Component | Primary Responsibility | Secondary Responsibilities |
|-----------|----------------------|---------------------------|
| **models.py** | Data structures | Type definitions, Enums, Serialization |
| **config_parser.py** | Parse package.json | Validate configuration, Extract scripts |
| **version_manager.py** | Detect package manager | Validate installation, Version checking |
| **dependency_manager.py** | Dependency operations | Install, Remove, Command building |
| **build_operations.py** | Build operations | Test, Scripts, Clean, Parse output |
| **manager_core.py** | Orchestration | Component coordination, API facade |
| **cli_handlers.py** | CLI interface | Command routing, Argument parsing |
| **__init__.py** | Package interface | Component exports, Public API |
| **npm_manager.py** | Backward compatibility | Re-export from new location |

## Design Pattern Application

### 1. Facade Pattern
```
NpmManager (facade)
    → Provides simple interface
    → Hides component complexity
    → Delegates to specialists
```

### 2. Strategy Pattern
```
Package Manager Strategy
    ├─ NPM strategy    (npm install, --save-dev)
    ├─ Yarn strategy   (yarn add, --dev)
    └─ PNPM strategy   (pnpm add, --dev)

Test Framework Strategy
    ├─ Jest parser     (Tests: X passed, Y total)
    └─ Mocha parser    (X passing, Y failing)
```

### 3. Template Method Pattern
```
BuildManagerBase (template)
    ├─ __init__() calls hooks:
    │   ├─ _validate_installation() → implemented by NpmManager
    │   └─ _validate_project() → implemented by NpmManager
    └─ Provides _execute_command()
```

### 4. Dependency Injection
```
NpmManager injects into components:
    ├─ self._execute_command → injected to all managers
    ├─ logger → injected to all managers
    └─ package_manager → injected to dependent managers
```

### 5. Dispatch Table
```
Command routing (cli_handlers.py):
    command_handlers = {
        "info": handle_info,
        "build": handle_build,
        "test": handle_test,
        "install": handle_install,
        "clean": handle_clean
    }

Package manager commands (dependency_manager.py):
    _install_commands = {
        PackageManager.NPM: "install",
        PackageManager.YARN: "add",
        PackageManager.PNPM: "add"
    }

    _dev_flags = {
        PackageManager.NPM: "--save-dev",
        PackageManager.YARN: "--dev",
        PackageManager.PNPM: "--dev"
    }
```

### 6. Command Pattern
```
CLI handlers as commands:
    handle_info(npm, args) → Command
    handle_build(npm, args) → Command
    handle_test(npm, args) → Command
```

### 7. Data Transfer Object
```
NpmProjectInfo
    → Encapsulates project data
    → Provides to_dict() serialization
    → Type-safe data transfer
```

### 8. Parser Pattern
```
Config parsing:
    package.json → NpmConfigParser → NpmProjectInfo

Test output parsing:
    Jest output → _parse_jest_output() → test stats dict
    Mocha output → _parse_mocha_output() → test stats dict
```

### 9. Composition Over Inheritance
```
NpmManager
    └─ has-a config_parser
    └─ has-a version_manager
    └─ has-a dependency_manager
    └─ has-a build_ops
    (Rather than multiple inheritance)
```

## Guard Clauses Example

### Before (nested):
```python
def validate_project(self, project_dir: Path) -> Path:
    package_json_path = project_dir / "package.json"
    if package_json_path.exists():
        return package_json_path
    else:
        raise ProjectConfigurationError("package.json not found")
```

### After (guard clause):
```python
def validate_project(self, project_dir: Path) -> Path:
    package_json_path = project_dir / "package.json"

    if not package_json_path.exists():
        raise ProjectConfigurationError(
            "package.json not found",
            {"project_dir": str(project_dir)}
        )

    return package_json_path  # Single level, early return
```

## Type Hints Example

```python
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path

def install_dependency(
    self,
    package: str,
    version: Optional[str] = None,
    dev: bool = False,
    **kwargs: Any
) -> bool:
    """Install a dependency."""
    ...

def _build_install_command(
    self,
    package: str,
    version: Optional[str],
    dev: bool
) -> List[str]:
    """Build install command."""
    ...
```

## Import Paths

### Old Style (still works):
```python
from npm_manager import NpmManager, PackageManager
```

### New Style (recommended):
```python
from build_managers.npm import NpmManager, PackageManager
```

### Component Imports:
```python
from build_managers.npm.config_parser import NpmConfigParser
from build_managers.npm.dependency_manager import DependencyManager
from build_managers.npm.build_operations import BuildOperations
from build_managers.npm.models import PackageManager, NpmProjectInfo
```

## Summary

The refactored architecture provides:

✅ **Modularity** - 7 focused components with clear responsibilities
✅ **Maintainability** - Each module < 350 lines, easy to understand
✅ **Testability** - Components independently testable
✅ **Extensibility** - Easy to add new package managers or features
✅ **Type Safety** - Complete type hints throughout
✅ **Pattern Usage** - 9 design patterns properly applied
✅ **Documentation** - WHY/RESPONSIBILITY/PATTERNS on every module
✅ **Backward Compatible** - Zero breaking changes
✅ **Clean Code** - Guard clauses, dispatch tables, no nesting

The architecture follows the same successful pattern as the Poetry manager
refactoring, ensuring consistency across the codebase.
