# Validators Package

**Modular configuration validation for Artemis**

## Overview

This package provides modular, testable configuration validation with clean separation of concerns. Refactored from a 619-line monolithic file into 9 focused modules.

## Usage

### Simple Usage (Recommended)

```python
from config.validators import ValidatorFacade

# Run all validations at once
facade = ValidatorFacade()
results = facade.run_all_validations()

for result in results:
    if not result.passed:
        print(f"❌ {result.check_name}: {result.message}")
```

### Individual Validators

```python
from config.validators import (
    LLMProviderValidator,
    PathValidator,
    DatabaseValidator,
    MessengerValidator,
    RAGDatabaseValidator,
    ResourceLimitValidator,
    OptionalServiceValidator
)

# Use individual validators
llm_validator = LLMProviderValidator()
result = llm_validator.validate_provider()
```

## Package Structure

```
validators/
├── __init__.py                      # Public API exports
├── llm_validator.py                 # LLM provider & API key validation
├── path_validator.py                # File system path validation
├── database_validator.py            # Database connectivity validation
├── messenger_validator.py           # Messenger backend validation
├── rag_validator.py                 # RAG database validation
├── resource_validator.py            # Resource limit validation
├── optional_service_validator.py    # Optional service validation
└── facade.py                        # Orchestration facade
```

## Validators

### LLMProviderValidator
Validates LLM provider configuration and API keys.

**Methods**:
- `validate_provider()` - Check provider selection
- `validate_api_keys()` - Validate API key presence/format

### PathValidator
Validates file system paths exist and are writable.

**Methods**:
- `validate_paths()` - Check all required paths

### DatabaseValidator
Validates database connectivity.

**Methods**:
- `validate_database()` - Check database access

### MessengerValidator
Validates messenger backend availability.

**Methods**:
- `validate_messenger()` - Check messenger configuration

### RAGDatabaseValidator
Validates RAG database (ChromaDB) access.

**Methods**:
- `validate_rag_database()` - Check ChromaDB availability

### ResourceLimitValidator
Validates resource limits are reasonable.

**Methods**:
- `validate_resource_limits()` - Check resource configurations

### OptionalServiceValidator
Validates optional services (e.g., Redis).

**Methods**:
- `validate_optional_services()` - Check optional service availability

### ValidatorFacade
Orchestrates all validators.

**Methods**:
- `run_all_validations()` - Execute all validation checks

## Design Patterns

- **Strategy Pattern**: Dictionary dispatch for validator selection
- **Facade Pattern**: Simplified interface via ValidatorFacade
- **Single Responsibility**: Each validator has one focus
- **Guard Clauses**: Early returns for clean control flow
- **Dependency Injection**: Validators can be tested independently

## Code Standards

All modules follow claude.md standards:
- ✅ Module-level docstrings with WHY/RESPONSIBILITY/PATTERNS
- ✅ Complete type hints on all functions
- ✅ Guard clauses instead of nested ifs
- ✅ Strategy pattern via dispatch tables
- ✅ Single Responsibility Principle
- ✅ Comprehensive documentation

## Testing

Each validator can be tested independently:

```python
import unittest
from config.validators import LLMProviderValidator

class TestLLMValidator(unittest.TestCase):
    def test_validate_provider(self):
        validator = LLMProviderValidator()
        result = validator.validate_provider()
        self.assertIsNotNone(result)
```

## Backward Compatibility

All existing imports continue to work:

```python
# Old code still works
from config.validators import LLMProviderValidator
```

## Metrics

- **Original File**: 619 lines
- **New Wrapper**: 48 lines (92.2% reduction)
- **Modules Created**: 9
- **Total New Code**: 822 lines (includes documentation)

## Documentation

See `REFACTORING_REPORT.md` for detailed refactoring information.
