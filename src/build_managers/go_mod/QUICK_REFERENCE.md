# Go Mod Manager - Quick Reference

## Import Paths

### Backward Compatible (Old)
```python
from go_mod_manager import GoModManager, BuildMode, GoArch, GoOS
```

### Recommended (New)
```python
from build_managers.go_mod import GoModManager, BuildMode, GoArch, GoOS
```

### Direct Component Access
```python
from build_managers.go_mod import (
    GoModParser,           # Parse go.mod files
    GoDependencyManager,   # Manage dependencies
    GoBuildOperations,     # Build/test operations
    GoVersionDetector      # Detect Go installation
)
```

## Quick Usage Examples

### Basic Build
```python
from build_managers.go_mod import GoModManager

manager = GoModManager(project_dir="/path/to/project")
result = manager.build(output="myapp")
print(f"Build {'succeeded' if result.success else 'failed'}")
```

### Cross-Compilation
```python
from build_managers.go_mod import GoModManager, GoOS, GoArch

manager = GoModManager(project_dir="/path/to/project")
result = manager.build(
    output="myapp-linux-arm64",
    goos=GoOS.LINUX.value,
    goarch=GoArch.ARM64.value
)
```

### Run Tests with Coverage
```python
manager = GoModManager(project_dir="/path/to/project")
result = manager.test(verbose=True, cover=True, race=True)
```

### Dependency Management
```python
manager = GoModManager(project_dir="/path/to/project")

# Add dependency
manager.install_dependency("github.com/gin-gonic/gin", version="v1.9.0")

# Download all dependencies
manager.download_dependencies()

# Tidy up go.mod
manager.tidy()

# Verify checksums
manager.verify()
```

### Code Quality Operations
```python
manager = GoModManager(project_dir="/path/to/project")

# Format code
manager.fmt()

# Static analysis
manager.vet()

# Clean cache
manager.clean()
```

### Parse go.mod Directly
```python
from build_managers.go_mod import GoModParser
from pathlib import Path

info = GoModParser.parse_go_mod(
    Path("/path/to/go.mod"),
    Path("/path/to/go.sum")
)

print(f"Module: {info.module_path}")
print(f"Go version: {info.go_version}")
print(f"Dependencies: {len(info.dependencies)}")
for dep, version in info.dependencies.items():
    print(f"  {dep}: {version}")
```

## CLI Usage

```bash
# Get project info
python -m go_mod_manager --project-dir . info

# Build
python -m go_mod_manager --project-dir . build --output myapp

# Build with tags
python -m go_mod_manager --project-dir . build --output myapp --tags production,sqlite

# Run tests
python -m go_mod_manager --project-dir . test --verbose --cover

# Add dependency
python -m go_mod_manager --project-dir . get --module github.com/gin-gonic/gin --version v1.9.0

# Download dependencies
python -m go_mod_manager --project-dir . download

# Tidy
python -m go_mod_manager --project-dir . tidy

# Format
python -m go_mod_manager --project-dir . fmt

# Vet
python -m go_mod_manager --project-dir . vet
```

## Module Breakdown

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| `models.py` | Data structures | BuildMode, GoArch, GoOS, GoModuleInfo |
| `parser.py` | Parse go.mod | GoModParser.parse_go_mod() |
| `version_detector.py` | Detect Go | GoVersionDetector.validate_installation() |
| `dependency_manager.py` | Dependencies | install_dependency(), tidy(), verify() |
| `build_operations.py` | Build/test | build(), test(), fmt(), vet(), clean() |
| `manager.py` | Main interface | GoModManager (facade) |
| `cli.py` | CLI | GoModCLI |

## Common Patterns

### Custom Build Configuration
```python
manager = GoModManager(project_dir=".")
result = manager.build(
    output="app",
    tags=["production", "postgres"],
    ldflags="-s -w -X main.version=1.0.0",
    race=True
)
```

### Test with Benchmarks
```python
result = manager.test(
    package="./pkg/core",
    verbose=True,
    bench=True,
    race=True
)
```

### Build for Multiple Platforms
```python
platforms = [
    (GoOS.LINUX, GoArch.AMD64),
    (GoOS.LINUX, GoArch.ARM64),
    (GoOS.DARWIN, GoArch.AMD64),
    (GoOS.WINDOWS, GoArch.AMD64),
]

for os, arch in platforms:
    result = manager.build(
        output=f"app-{os.value}-{arch.value}",
        goos=os.value,
        goarch=arch.value
    )
    print(f"Built for {os.value}/{arch.value}: {result.success}")
```

## Enums Reference

### BuildMode
- `BuildMode.DEFAULT` - Standard build
- `BuildMode.PIE` - Position independent executable
- `BuildMode.C_ARCHIVE` - C archive library
- `BuildMode.C_SHARED` - C shared library
- `BuildMode.PLUGIN` - Go plugin

### GoArch
- `GoArch.AMD64` - x86-64
- `GoArch.ARM64` - ARM 64-bit
- `GoArch.ARM` - ARM 32-bit
- `GoArch.I386` - x86 32-bit

### GoOS
- `GoOS.LINUX` - Linux
- `GoOS.DARWIN` - macOS
- `GoOS.WINDOWS` - Windows
- `GoOS.FREEBSD` - FreeBSD

## Error Handling

All operations raise specific exceptions:
- `BuildSystemNotFoundError` - Go not installed
- `ProjectConfigurationError` - Invalid go.mod
- `BuildExecutionError` - Build/clean/fmt/vet failed
- `TestExecutionError` - Tests failed
- `DependencyInstallError` - Dependency operation failed

```python
from build_system_exceptions import BuildExecutionError

try:
    result = manager.build(output="app")
except BuildExecutionError as e:
    print(f"Build failed: {e}")
    print(f"Context: {e.context}")
```

## Best Practices

1. **Use type hints** for IDE support
2. **Handle exceptions** appropriately
3. **Use enums** for build modes, architectures, OS
4. **Leverage components** directly when needed
5. **Prefer new import path** for new code
6. **Document build configurations** in code

## Migration Checklist

- [ ] Update imports from `go_mod_manager` to `build_managers.go_mod`
- [ ] Replace elif chains with dispatch tables (if any)
- [ ] Add type hints to custom code
- [ ] Use guard clauses instead of nested ifs
- [ ] Document WHY/RESPONSIBILITY/PATTERNS
- [ ] Test with both import paths during transition
- [ ] Update CI/CD scripts if needed
