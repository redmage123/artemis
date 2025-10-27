# Configuration Agent - Skills

## Agent Overview
**File**: `config_agent.py`
**Purpose**: Centralized environment configuration management
**Single Responsibility**: Read, validate, and provide environment configuration

## Core Skills

### 1. Environment Variable Management
- **Reading**: Loads from system environment and .env files
- **Validation**: Checks required keys are present
- **Default Values**: Provides sensible defaults
- **Type Conversion**: Handles string→int, string→bool conversions
- **Masking**: Hides sensitive values in logs

### 2. Configuration Validation
- **Required Keys**: Enforces mandatory configuration
- **Valid Values**: Validates enum-style configurations
- **Conditional Requirements**: API keys required based on provider
- **Missing Key Detection**: Reports all missing keys at once
- **Invalid Key Detection**: Reports misconfigured values

### 3. LLM Provider Configuration
- **Provider Selection**: OpenAI or Anthropic
- **Model Selection**: Provider-specific model names
- **API Key Management**: Secure handling of sensitive keys
- **Provider Defaults**: Default models per provider

### 4. Database Configuration
- **Neo4j**: Knowledge graph connection settings
- **ChromaDB**: RAG database paths
- **SQLite**: Local database configuration
- **Path Resolution**: Absolute vs relative paths

### 5. Service Endpoints
- **API URLs**: External service endpoints
- **Timeouts**: Connection and read timeouts
- **Retry Configuration**: Retry attempts and backoff
- **Rate Limits**: API rate limit settings

### 6. Pipeline Configuration
- **Directory Paths**: Data, output, database directories
- **Logging**: Log levels and debug mode
- **Streaming Validation**: Enable/disable real-time validation
- **Retry Configuration**: Max validation retries
- **Confidence Thresholds**: Code acceptance thresholds

## Configuration Schema

### LLM Configuration
- `ARTEMIS_LLM_PROVIDER` - Primary LLM provider (openai/anthropic)
- `ARTEMIS_LLM_MODEL` - Specific model to use
- `OPENAI_API_KEY` - OpenAI API key (sensitive)
- `ANTHROPIC_API_KEY` - Anthropic API key (sensitive)

### Knowledge Graph
- `NEO4J_URI` - Neo4j connection URI
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password (sensitive)

### Artemis Paths
- `ARTEMIS_DATA_DIR` - Data storage directory
- `ARTEMIS_DB_DIR` - Database directory
- `ARTEMIS_OUTPUT_DIR` - Output directory

### Logging
- `LOG_LEVEL` - Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `DEBUG_MODE` - Enable debug mode (true/false)

### Hallucination Reduction
- `ARTEMIS_ENABLE_STREAMING_VALIDATION` - Real-time validation (true/false)
- `ARTEMIS_MAX_VALIDATION_RETRIES` - Maximum retry attempts (1-5)
- `ARTEMIS_CONFIDENCE_THRESHOLD` - Acceptance threshold (0.0-1.0)

## Usage Patterns

```python
# Initialize configuration agent
config = ConfigurationAgent(verbose=True)

# Validate all configuration
result = config.validate_configuration()

if not result.is_valid:
    print(f"Missing keys: {result.missing_keys}")
    print(f"Invalid keys: {result.invalid_keys}")
    print(f"Warnings: {result.warnings}")
    sys.exit(1)

# Get specific configuration
llm_provider = config.get("ARTEMIS_LLM_PROVIDER")
api_key = config.get("OPENAI_API_KEY", sensitive=True)

# Get configuration summary
summary = config.get_summary()
```

## Validation Results

```python
ConfigValidationResult(
    is_valid=True/False,
    missing_keys=[...],
    invalid_keys=[...],
    warnings=[...],
    config_summary={
        "llm_provider": "openai",
        "log_level": "INFO",
        "neo4j_configured": True,
        "api_keys_present": ["openai"]
    }
)
```

## SOLID Principles

- **Single Responsibility**: Only manages configuration (no business logic)
- **Open/Closed**: Easy to add new configuration keys to schema
- **Dependency Inversion**: Other components depend on ConfigurationAgent abstraction

## Design Patterns

- **Singleton Pattern**: Single source of configuration truth
- **Value Object**: ConfigValidationResult dataclass
- **Template Method**: Standard validation workflow

## Security Features

- **Sensitive Value Masking**: API keys shown as `***` in logs
- **No Logging**: Sensitive values never logged
- **Environment Isolation**: .env file not committed to Git
- **Override Protection**: dotenv overrides system environment

## Integration Points

- **All Pipeline Components**: Every component uses ConfigAgent
- **Orchestrator**: Validates config before pipeline starts
- **Logging**: Configures log levels
- **LLM Clients**: Provides API keys
- **Database Clients**: Provides connection strings

## Error Handling

- **Graceful Degradation**: Provides defaults when possible
- **Early Validation**: Fails fast on startup
- **Detailed Messages**: Clear error messages for missing config
- **Warnings**: Non-critical issues logged as warnings

## Performance Optimizations

- **Lazy Loading**: Loads .env only once
- **Caching**: Configuration cached after first load
- **O(1) Lookups**: Dictionary-based config access

## Developer Experience

- **`.env.example`**: Template for required configuration
- **Clear Documentation**: Each config key documented
- **Validation on Startup**: Catches config issues immediately
- **Helpful Messages**: Tells you exactly what's missing/wrong
