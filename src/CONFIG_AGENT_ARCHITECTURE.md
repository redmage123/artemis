# Configuration Agent Architecture

## Package Structure

```
agents/config/
├── __init__.py          (71 lines)   - Public API exports
├── models.py            (237 lines)  - Data models & schema
├── loader.py            (219 lines)  - Configuration loading
├── validator.py         (253 lines)  - Validation logic
├── generator.py         (302 lines)  - Report generation
└── agent_core.py        (236 lines)  - Main agent (facade)

config_agent.py          (100 lines)  - Backward compatibility wrapper
```

## Module Dependencies

```
┌─────────────────────┐
│  config_agent.py    │  (Backward Compatibility Wrapper)
│  (100 lines)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  __init__.py        │  (Package API)
│  (71 lines)         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  agent_core.py      │  (Facade - Coordinates All)
│  (236 lines)        │
│                     │
│  ConfigurationAgent │
│  - load_config()    │
│  - validate_config()│
│  - print_report()   │
│  - export_to_dict() │
└──────────┬──────────┘
           │
           ├─────────────────┬─────────────────┬─────────────────┐
           ▼                 ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐    ┌──────────┐      ┌──────────┐
    │ models.py│      │loader.py │    │validator │      │generator │
    │ (237 L)  │◄─────┤ (219 L)  │    │  (253 L) │      │  (302 L) │
    │          │      │          │    │          │      │          │
    │ Schema   │      │ Load env │    │ Validate │      │ Reports  │
    │ Models   │      │ .env     │    │ Keys     │      │ JSON     │
    │ Constants│      │ Convert  │    │ Values   │      │ Exports  │
    └──────────┘      │ Mask     │    │ Limits   │      └──────────┘
                      └──────────┘    └──────────┘
                           │                │
                           └────────────────┘
                                   │
                                   ▼
                            ┌──────────┐
                            │ models.py│
                            │ (shared) │
                            └──────────┘
```

## Component Responsibilities

### 1. models.py (237 lines)
**WHY**: Centralize all data structures and schema definitions
**RESPONSIBILITY**: Define configuration models and schema
**EXPORTS**:
- `ConfigValidationResult` - Validation result dataclass
- `ConfigSchema` - Schema definition and accessors
- `BOOL_STRING_MAP` - Boolean conversion dispatch table
- `PROVIDER_KEY_MAP` - Provider key mapping dispatch table

### 2. loader.py (219 lines)
**WHY**: Separate loading concerns from validation and reporting
**RESPONSIBILITY**: Load configuration from various sources
**EXPORTS**:
- `ConfigLoader` - Static methods for loading
  - `load_dotenv()` - Load .env file
  - `load_from_environment()` - Load from env vars
  - `convert_boolean_string()` - Type conversion
  - `mask_sensitive_value()` - Safe masking
  - `export_config()` - Export with masking
  - `set_test_defaults()` - Testing configuration

### 3. validator.py (253 lines)
**WHY**: Isolate validation logic for independent testing
**RESPONSIBILITY**: Validate configuration against rules
**EXPORTS**:
- `ConfigValidator` - Static methods for validation
  - `validate_configuration()` - Main validation
  - `validate_llm_keys()` - Provider-specific keys
  - `validate_config_values()` - Value constraints
  - `validate_cost_limit()` - Cost limit validation
  - `generate_config_summary()` - Summary generation
  - `is_valid_provider()` - Provider validation

### 4. generator.py (302 lines)
**WHY**: Separate presentation from business logic
**RESPONSIBILITY**: Generate reports and exports
**EXPORTS**:
- `ConfigGenerator` - Static methods for generation
  - `print_configuration_report()` - Full report
  - `print_provider_section()` - Provider info
  - `print_storage_section()` - Storage info
  - `print_pipeline_section()` - Pipeline info
  - `print_security_section()` - Security info
  - `print_logging_section()` - Logging info
  - `print_cost_section()` - Cost info
  - `print_validation_section()` - Validation results
  - `export_to_json()` - JSON export
  - `generate_summary()` - Quick summary

### 5. agent_core.py (236 lines)
**WHY**: Provide simple unified API (Facade pattern)
**RESPONSIBILITY**: Coordinate all configuration operations
**EXPORTS**:
- `ConfigurationAgent` - Main agent class
  - `load_configuration()` - Load config
  - `validate_configuration()` - Validate config
  - `get()` - Get config value
  - `get_masked()` - Get masked value
  - `print_configuration_report()` - Print report
  - `export_to_dict()` - Export dict
  - `export_to_json()` - Export JSON
  - `set_defaults_for_testing()` - Test mode
  - `reload_configuration()` - Reload config
- `get_config()` - Singleton getter
- `reset_config()` - Singleton reset

### 6. __init__.py (71 lines)
**WHY**: Define clean public API for package
**RESPONSIBILITY**: Export public interfaces
**EXPORTS**: All public classes and functions

### 7. config_agent.py (100 lines)
**WHY**: Maintain backward compatibility
**RESPONSIBILITY**: Re-export package API
**EXPORTS**: All APIs from agents.config package

## Data Flow

### Loading Configuration
```
1. User calls get_config() or ConfigurationAgent()
2. agent_core.ConfigurationAgent.__init__()
3. agent_core.load_configuration()
4. loader.ConfigLoader.load_configuration()
   a. loader.load_dotenv() - Load .env file
   b. loader.load_from_environment() - Load env vars
   c. loader.convert_boolean_string() - Type conversion
5. Store in agent.config dict
```

### Validating Configuration
```
1. User calls agent.validate_configuration()
2. agent_core delegates to validator.ConfigValidator
3. validator.validate_configuration()
   a. validator.validate_llm_keys() - Check API keys
   b. validator.validate_config_values() - Check constraints
   c. validator.validate_cost_limit() - Check cost limits
   d. validator.generate_config_summary() - Create summary
4. Return ConfigValidationResult
```

### Generating Reports
```
1. User calls agent.print_configuration_report()
2. agent_core calls validate_configuration() first
3. agent_core delegates to generator.ConfigGenerator
4. generator.print_configuration_report()
   a. Print header
   b. For each section in dispatch table:
      - generator.print_provider_section()
      - generator.print_storage_section()
      - generator.print_pipeline_section()
      - generator.print_security_section()
      - generator.print_logging_section()
      - generator.print_cost_section()
   c. generator.print_validation_section()
   d. Print footer
```

## Design Patterns Applied

### 1. Facade Pattern
`ConfigurationAgent` provides simple interface hiding complexity:
```python
config = get_config()              # Simple
result = config.validate_config()  # Simple
config.print_report()              # Simple

# Instead of:
loader = ConfigLoader()
validator = ConfigValidator()
generator = ConfigGenerator()
config_dict = loader.load_configuration()
result = validator.validate_configuration(config_dict)
generator.print_report(config_dict, result)
```

### 2. Strategy Pattern (Dispatch Tables)
Replace if/elif with dictionaries:
```python
# Boolean conversion
value = BOOL_STRING_MAP.get(str_value, str_value)

# Provider key mapping
key = PROVIDER_KEY_MAP.get(provider)

# Section generators
for generator in section_generators:
    generator(config)
```

### 3. Singleton Pattern
Single configuration instance:
```python
def get_config() -> ConfigurationAgent:
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigurationAgent()
    return _config_instance
```

### 4. Guard Clauses
Reduce nesting to max 1 level:
```python
def validate_llm_keys(config, provider, require_key, missing):
    # Guard: early return if not required
    if not require_key:
        return

    # Guard: early return if no mapping
    required_key = PROVIDER_KEY_MAP.get(provider)
    if not required_key:
        return

    # Main logic at single nesting level
    if not config.get(required_key):
        missing.append(required_key)
```

## Testing Strategy

Each module can be tested independently:

```python
# Test models
schema = ConfigSchema.get_schema()
assert 'ARTEMIS_LLM_PROVIDER' in schema

# Test loader
config = ConfigLoader.load_configuration()
assert 'ARTEMIS_LLM_PROVIDER' in config

# Test validator
result = ConfigValidator.validate_configuration(config)
assert result.is_valid

# Test generator
json_str = ConfigGenerator.export_to_json(config)
assert 'provider' in json_str

# Test agent (integration)
agent = ConfigurationAgent()
result = agent.validate_configuration()
assert result.is_valid
```

## Extension Points

### Add New Configuration Source
Edit `loader.py`:
```python
@staticmethod
def load_from_yaml(file_path: str) -> Dict[str, Any]:
    # Load from YAML file
    pass
```

### Add New Validation Rule
Edit `validator.py`:
```python
@staticmethod
def validate_custom_rule(config: Dict[str, Any], errors: List[str]) -> None:
    # Custom validation logic
    pass
```

### Add New Report Format
Edit `generator.py`:
```python
@staticmethod
def export_to_yaml(config: Dict[str, Any]) -> str:
    # Generate YAML report
    pass
```

### Add New Configuration Key
Edit `models.py`:
```python
ConfigSchema.SCHEMA['NEW_KEY'] = {
    'default': 'value',
    'required': False,
    'sensitive': False,
    'description': 'New configuration key'
}
```

## Summary

This architecture achieves:
- **Modularity**: Each module has single responsibility
- **Testability**: Components tested independently
- **Extensibility**: Clear extension points per concern
- **Maintainability**: ~220 lines per module vs 531 monolithic
- **Backward Compatibility**: 100% via wrapper
- **Code Quality**: Guard clauses, type hints, dispatch tables
- **Documentation**: WHY/RESPONSIBILITY/PATTERNS on every module
