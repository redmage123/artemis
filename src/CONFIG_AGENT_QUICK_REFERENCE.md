# Configuration Agent Quick Reference

## Import Statements

### Backward Compatible (Old Code)
```python
from config_agent import ConfigurationAgent, get_config
from config_agent import ConfigValidationResult
```

### New Package Import (Preferred)
```python
from agents.config import ConfigurationAgent, get_config
from agents.config import ConfigValidationResult, ConfigSchema
```

### Component-Specific Imports
```python
from agents.config.loader import ConfigLoader
from agents.config.validator import ConfigValidator
from agents.config.generator import ConfigGenerator
```

## Basic Usage

### Get Configuration
```python
from agents.config import get_config

# Get singleton instance
config = get_config()

# Access values
provider = config.get('ARTEMIS_LLM_PROVIDER')
api_key = config.get('OPENAI_API_KEY')

# Get with default
max_devs = config.get('ARTEMIS_MAX_PARALLEL_DEVELOPERS', 3)
```

### Validate Configuration
```python
from agents.config import get_config

config = get_config()
result = config.validate_configuration()

if result.is_valid:
    print("Configuration is valid")
else:
    print(f"Missing keys: {result.missing_keys}")
    print(f"Invalid keys: {result.invalid_keys}")
    print(f"Warnings: {result.warnings}")
```

### Print Configuration Report
```python
from agents.config import get_config

config = get_config()
config.print_configuration_report()
```

### Export Configuration
```python
from agents.config import get_config

config = get_config()

# Export as dictionary (masked)
config_dict = config.export_to_dict(mask_sensitive=True)

# Export as JSON (masked)
json_str = config.export_to_json(mask_sensitive=True)

# Export without masking (use with caution)
unmasked = config.export_to_dict(mask_sensitive=False)
```

### Test Mode
```python
from agents.config import get_config

config = get_config()
config.set_defaults_for_testing()

# Now using mock provider, no real API calls
```

## Advanced Usage

### Direct Loader Usage
```python
from agents.config.loader import ConfigLoader
from agents.config.models import ConfigSchema

# Load configuration
schema = ConfigSchema.get_schema()
config = ConfigLoader.load_from_environment(schema)

# Mask sensitive value
masked = ConfigLoader.mask_sensitive_value('OPENAI_API_KEY', api_key)

# Convert boolean
enabled = ConfigLoader.convert_boolean_string('true')  # Returns True
```

### Direct Validator Usage
```python
from agents.config.validator import ConfigValidator

# Validate configuration dictionary
result = ConfigValidator.validate_configuration(
    config_dict,
    require_llm_key=True
)

# Check if provider is valid
is_valid = ConfigValidator.is_valid_provider('openai')  # True

# Validate specific required keys
missing = ConfigValidator.validate_required_keys(
    config_dict,
    ['OPENAI_API_KEY', 'ARTEMIS_LLM_PROVIDER']
)
```

### Direct Generator Usage
```python
from agents.config.generator import ConfigGenerator
from agents.config.validator import ConfigValidator

# Generate full report
validation = ConfigValidator.validate_configuration(config_dict)
ConfigGenerator.print_configuration_report(config_dict, validation)

# Export to JSON
json_str = ConfigGenerator.export_to_json(config_dict, mask_sensitive=True)

# Generate summary
summary = ConfigGenerator.generate_summary(config_dict)
```

### Schema Access
```python
from agents.config.models import ConfigSchema

# Get full schema
schema = ConfigSchema.get_schema()

# Get specific key schema
key_schema = ConfigSchema.get_key_schema('ARTEMIS_LLM_PROVIDER')

# Check if sensitive
is_sensitive = ConfigSchema.is_sensitive('OPENAI_API_KEY')  # True

# Get default value
default = ConfigSchema.get_default('ARTEMIS_LOG_LEVEL')  # 'INFO'

# Get valid values
valid = ConfigSchema.get_valid_values('ARTEMIS_LLM_PROVIDER')
# Returns: ['openai', 'anthropic']
```

## CLI Usage

### Validate Configuration
```bash
python config_agent.py --validate
# Exit code 0 if valid, 1 if invalid
```

### Print Report
```bash
python config_agent.py --report
# Or just:
python config_agent.py
```

### Export as JSON
```bash
python config_agent.py --export
# Outputs JSON to stdout
```

### Pipe to File
```bash
python config_agent.py --export > config.json
```

## Environment Variables

### LLM Provider
```bash
export ARTEMIS_LLM_PROVIDER=openai          # or anthropic
export ARTEMIS_LLM_MODEL=gpt-4              # optional
export OPENAI_API_KEY=sk-...                # required for openai
export ANTHROPIC_API_KEY=sk-ant-...         # required for anthropic
```

### Storage
```bash
export ARTEMIS_RAG_DB_PATH=db               # relative to .agents/agile
export ARTEMIS_TEMP_DIR=/tmp/artemis        # temp directory
```

### Pipeline
```bash
export ARTEMIS_MAX_PARALLEL_DEVELOPERS=3    # max parallel devs
export ARTEMIS_ENABLE_CODE_REVIEW=true      # enable code review
export ARTEMIS_AUTO_APPROVE_PROJECT_ANALYSIS=true
```

### Logging
```bash
export ARTEMIS_VERBOSE=true                 # verbose logging
export ARTEMIS_LOG_LEVEL=INFO               # DEBUG/INFO/WARNING/ERROR
```

### Security
```bash
export ARTEMIS_ENFORCE_GDPR=true            # GDPR compliance
export ARTEMIS_ENFORCE_WCAG=true            # WCAG accessibility
```

### Cost Control
```bash
export ARTEMIS_MAX_TOKENS_PER_REQUEST=8000  # max tokens per request
export ARTEMIS_COST_LIMIT_USD=100           # daily cost limit (optional)
```

## Common Patterns

### Check if API Key Exists
```python
from agents.config import get_config

config = get_config()
has_openai = bool(config.get('OPENAI_API_KEY'))
has_anthropic = bool(config.get('ANTHROPIC_API_KEY'))

if not has_openai and not has_anthropic:
    print("No API key configured")
```

### Get Masked Value for Logging
```python
from agents.config import get_config

config = get_config()
masked_key = config.get_masked('OPENAI_API_KEY')
print(f"Using API key: {masked_key}")  # sk-abc...xyz
```

### Validate Before Running Pipeline
```python
from agents.config import get_config

def run_pipeline():
    config = get_config()
    result = config.validate_configuration(require_llm_key=True)

    if not result.is_valid:
        print("Configuration errors:")
        for key in result.missing_keys:
            print(f"  - Missing: {key}")
        for key in result.invalid_keys:
            print(f"  - Invalid: {key}")
        return False

    # Configuration is valid, proceed
    provider = config.get('ARTEMIS_LLM_PROVIDER')
    model = config.get('ARTEMIS_LLM_MODEL', 'default')
    print(f"Using {provider} with model {model}")
    return True
```

### Dynamic Configuration Reload
```python
from agents.config import get_config

config = get_config()

# Initial configuration
print(config.get('ARTEMIS_LOG_LEVEL'))

# Change environment
import os
os.environ['ARTEMIS_LOG_LEVEL'] = 'DEBUG'

# Reload
config.reload_configuration()

# Updated value
print(config.get('ARTEMIS_LOG_LEVEL'))  # DEBUG
```

### Testing with Mock Configuration
```python
from agents.config import get_config, reset_config

def test_my_feature():
    # Reset singleton for clean state
    reset_config()

    # Get fresh instance
    config = get_config()

    # Set test defaults
    config.set_defaults_for_testing()

    # Now using mock provider
    assert config.get('ARTEMIS_LLM_PROVIDER') == 'mock'

    # Run tests...
```

## Migration Guide

### Step 1: Update Imports (Optional)
```python
# Old (still works)
from config_agent import ConfigurationAgent, get_config

# New (preferred)
from agents.config import ConfigurationAgent, get_config
```

### Step 2: No Code Changes Needed
All existing code continues to work unchanged!

### Step 3: Take Advantage of New Components (Optional)
```python
# Can now use components independently
from agents.config.loader import ConfigLoader
from agents.config.validator import ConfigValidator

# Build custom workflows
config = ConfigLoader.load_configuration()
result = ConfigValidator.validate_configuration(config)
```

## Troubleshooting

### Missing API Key
```python
result = config.validate_configuration()
if 'OPENAI_API_KEY' in result.missing_keys:
    print("Set OPENAI_API_KEY environment variable")
```

### Invalid Configuration Value
```python
result = config.validate_configuration()
if result.invalid_keys:
    for invalid in result.invalid_keys:
        print(f"Invalid: {invalid}")
```

### Check Available Keys
```python
from agents.config.models import ConfigSchema

schema = ConfigSchema.get_schema()
for key in schema.keys():
    print(f"{key}: {schema[key]['description']}")
```

## Best Practices

1. **Use Singleton**: Always use `get_config()` instead of creating instances
2. **Validate Early**: Validate configuration at application startup
3. **Mask Sensitive**: Use `get_masked()` when logging API keys
4. **Handle Errors**: Check `is_valid` before proceeding
5. **Test Mode**: Use `set_defaults_for_testing()` in tests
6. **Environment First**: Prefer environment variables over hardcoding

## File Locations

```
src/
├── config_agent.py                    (Backward compatibility wrapper)
└── agents/
    └── config/
        ├── __init__.py               (Package exports)
        ├── models.py                 (Data models & schema)
        ├── loader.py                 (Configuration loading)
        ├── validator.py              (Validation logic)
        ├── generator.py              (Report generation)
        └── agent_core.py             (Main agent)
```

## Support

For detailed architecture and design patterns, see:
- `CONFIG_AGENT_ARCHITECTURE.md` - Architecture documentation
- `CONFIG_AGENT_REFACTORING_REPORT.md` - Refactoring analysis
