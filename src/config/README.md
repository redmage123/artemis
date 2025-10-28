# Config Validator Package

**WHY**: Modular configuration validation for Artemis startup with fail-fast error detection

**RESPONSIBILITY**: Validate all prerequisites before pipeline runs

**PATTERNS**: Strategy pattern for validation checks, Single Responsibility Principle

## Package Structure

```
config/
├── __init__.py              # Package exports and public API
├── models.py                # Data models (ValidationResult, ValidationReport)
├── constants.py             # Configuration constants and defaults
├── path_utils.py            # Path resolution utilities
├── validators.py            # Validator strategies (785 lines → 619 lines)
├── report_generator.py      # Report generation and formatting
└── validator.py             # Main validator orchestrator
```

## Line Count Reduction

**Original**: 785 lines in single file
**Refactored**: 1,186 lines across 7 focused modules
**Wrapper**: 104 lines for backward compatibility

**Benefits**:
- Each module has single responsibility
- Maximum nesting: 1 level (guard clauses)
- Easy to test individual validators
- Clear separation of concerns

## Module Breakdown

### models.py (57 lines)
- `ValidationResult`: Individual check result
- `ValidationReport`: Aggregated report

### constants.py (65 lines)
- Valid provider/messenger/persistence types
- Default configuration values
- Provider configurations (strategy pattern)

### path_utils.py (77 lines)
- `resolve_relative_path()`: Convert relative to absolute paths
- `ensure_directory_writable()`: Validate directory access
- `get_script_directory()`: Get src directory path

### validators.py (619 lines)
Strategy pattern implementation for validation:
- `LLMProviderValidator`: LLM provider and API key validation
- `PathValidator`: File path validation
- `DatabaseValidator`: Database access validation (SQLite, PostgreSQL)
- `MessengerValidator`: Messenger backend validation (File, RabbitMQ, Mock)
- `RAGDatabaseValidator`: ChromaDB validation
- `ResourceLimitValidator`: Resource limit validation
- `OptionalServiceValidator`: Optional service validation (Redis)

### report_generator.py (114 lines)
- `generate_report()`: Aggregate results into report
- `print_report()`: Format and print summary
- `print_result()`: Print individual result

### validator.py (177 lines)
Main orchestrator that:
- Coordinates all validation checks
- Delegates to strategy validators
- Generates comprehensive report

### __init__.py (77 lines)
Public API exports for easy importing

## Usage

### Direct Import (Recommended for new code)
```python
from config import ConfigValidator, validate_config_or_exit
from config.models import ValidationResult, ValidationReport

# Run all validation checks
validator = ConfigValidator(verbose=True)
report = validator.validate_all()

# Or use convenience function that exits on failure
report = validate_config_or_exit(verbose=True)
```

### Backward Compatibility Import
```python
# Old code continues to work
from config_validator import ConfigValidator, validate_config_or_exit
```

### Using Individual Validators
```python
from config import (
    LLMProviderValidator,
    PathValidator,
    DatabaseValidator
)

# Use specific validators
llm_validator = LLMProviderValidator()
result = llm_validator.validate_api_keys()

if not result.passed:
    print(f"Error: {result.message}")
    if result.fix_suggestion:
        print(f"Fix: {result.fix_suggestion}")
```

## Standards Compliance

### WHY/RESPONSIBILITY/PATTERNS Documentation
Every module has clear documentation explaining:
- **WHY**: Purpose and motivation
- **RESPONSIBILITY**: What it's responsible for
- **PATTERNS**: Design patterns used

### Guard Clauses (Max 1 Level Nesting)
All validators use guard clauses for early returns:
```python
# Guard clause: Already absolute
if os.path.isabs(path):
    return path

# Guard clause: Invalid provider
if provider not in VALID_LLM_PROVIDERS:
    return ValidationResult(...)

# Success case (no nesting)
return ValidationResult(...)
```

### Type Hints
All functions have complete type hints:
```python
def validate_paths(self) -> List[ValidationResult]:
def generate_report(results: List[ValidationResult]) -> ValidationReport:
def resolve_relative_path(path: str, script_dir: Optional[str] = None) -> str:
```

### Dispatch Tables (No elif chains)
Strategy pattern via dispatch tables:
```python
# Instead of if/elif chain
messenger_checks: Dict[str, Callable[[], ValidationResult]] = {
    "file": self._check_file_messenger,
    "rabbitmq": self._check_rabbitmq_messenger,
    "mock": self._check_mock_messenger
}
check_func = messenger_checks.get(messenger_type)
```

### Single Responsibility Principle
Each validator class has one clear responsibility:
- `LLMProviderValidator`: Only LLM validation
- `PathValidator`: Only path validation
- `DatabaseValidator`: Only database validation
- etc.

## Validation Checks

1. **LLM Provider**: Valid provider selected (openai, anthropic, mock)
2. **LLM API Keys**: API keys present and valid format
3. **File Paths**: Directories exist and writable
4. **Database**: Database accessible (SQLite or PostgreSQL)
5. **Messenger**: Messenger backend available (File, RabbitMQ, or Mock)
6. **RAG Database**: ChromaDB accessible (optional)
7. **Resource Limits**: Parallel developers within bounds, budgets valid
8. **Optional Services**: Redis accessible if configured (optional)

## Exit Codes

When run as main script:
- `0`: All checks passed
- `1`: Validation failed (errors present)
- `2`: Warnings only (no errors)

## Testing

Run the verification test:
```bash
python3 test_config_refactoring.py
```

Tests verify:
- All modules compile successfully
- Backward compatibility maintained
- All validator strategies work
- Report generation works
- Path utilities work

## Migration Guide

### For New Code
Use direct imports:
```python
from config import ConfigValidator, validate_config_or_exit
from config.validators import LLMProviderValidator
from config.models import ValidationResult
```

### For Existing Code
No changes needed! The backward compatibility wrapper (`config_validator_refactored.py`) maintains full compatibility:
```python
# This still works
from config_validator import ConfigValidator
```

## Design Patterns

1. **Strategy Pattern**: Different validators for different checks
2. **Dispatch Tables**: Dictionary mapping instead of if/elif chains
3. **Guard Clauses**: Early returns to avoid nesting
4. **Facade Pattern**: Backward compatibility wrapper
5. **Single Responsibility**: Each class has one job
6. **Dataclasses**: Immutable value objects for results

## Performance

- O(n) overall: where n is number of validation checks
- O(1) per check: Most checks are environment variable lookups
- O(n) network checks: Database, Redis, RabbitMQ with timeouts
- List comprehensions for aggregation (faster than loops)

## Future Enhancements

Easy to add new validators:
1. Create new validator class in `validators.py`
2. Add check method to `ConfigValidator` in `validator.py`
3. Add to validation checks list

Example:
```python
class NewServiceValidator:
    def validate_service(self) -> ValidationResult:
        # Implementation
        pass

# In ConfigValidator.validate_all():
validation_checks.append(self._check_new_service)
```
