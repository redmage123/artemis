# BDD Scenario Generation Package

## Overview

The `stages.bdd_scenario` package provides modular BDD scenario generation for the Artemis pipeline. It transforms structured requirements into executable Gherkin specifications using LLM-powered generation with comprehensive validation.

## Quick Start

### Using the Stage

```python
from stages.bdd_scenario import BDDScenarioStageCore

# Initialize stage
stage = BDDScenarioStageCore(
    board=kanban_board,
    rag=rag_agent,
    logger=logger,
    llm_client=llm_client,
    supervisor=supervisor,      # Optional
    ai_service=ai_query_service # Optional
)

# Execute stage
result = stage.execute(card, context)

# Access results
print(f"Generated {result['scenario_count']} scenarios")
print(f"Feature file: {result['feature_path']}")
print(f"Validation: {result['validation']}")
```

### Using Individual Components

#### Generate Scenarios
```python
from stages.bdd_scenario import ScenarioGenerator

generator = ScenarioGenerator(
    llm_client=llm_client,
    logger=logger,
    ai_service=ai_service  # Optional
)

gherkin_text = generator.generate(
    card_id="card-123",
    title="User Login",
    requirements={"description": "As a user..."}
)
```

#### Format Gherkin
```python
from stages.bdd_scenario import GherkinFormatter, Feature, Scenario, Step

formatter = GherkinFormatter(indent_spaces=2)

feature = Feature(
    name="User Login",
    description="As a user, I want to login...",
    scenarios=[
        Scenario(
            name="Successful login",
            steps=[
                Step("Given", "the user is on the login page"),
                Step("When", "the user enters valid credentials"),
                Step("Then", "the user should be logged in")
            ]
        )
    ]
)

gherkin_text = formatter.format_feature(feature)
```

#### Validate Scenarios
```python
from stages.bdd_scenario import ScenarioValidator

validator = ScenarioValidator()
result = validator.validate(gherkin_text)

if result['valid']:
    print("✅ Valid Gherkin syntax")
else:
    print(f"❌ Validation errors: {result['errors']}")
```

#### Extract Features
```python
from stages.bdd_scenario import FeatureExtractor

extractor = FeatureExtractor()
feature_data = extractor.extract(
    title="User Login",
    requirements={
        "description": "As a user...",
        "acceptance_criteria": [...]
    }
)
```

## Package Structure

```
stages/bdd_scenario/
├── __init__.py              # Package exports
├── models.py                # Data structures (Feature, Scenario, Step)
├── gherkin_formatter.py     # Gherkin formatting
├── scenario_generator.py    # LLM-based generation
├── feature_extractor.py     # Feature extraction from requirements
└── stage_core.py           # Main stage orchestrator
```

## Modules

### models.py (256 lines)
**Data structures for BDD scenarios**

Key classes:
- `Step` - Immutable Gherkin step (Given/When/Then/And/But)
- `Scenario` - Immutable scenario with validation
- `Feature` - Top-level feature container
- `ValidationResult` - Type-safe validation results
- `GenerationRequest` - Request object for scenario generation
- `GenerationResult` - Result object with success/error states

Features:
- Frozen dataclasses (immutable)
- Built-in validation
- Type safety
- Derived properties

### gherkin_formatter.py (351 lines)
**Format Feature objects as Gherkin syntax**

Key class:
- `GherkinFormatter` - Stateless formatter

Features:
- Configurable indentation
- Table alignment
- Support for all Gherkin constructs:
  - Features with tags
  - Scenarios and Scenario Outlines
  - Background steps
  - Data tables
  - Doc strings
  - Examples tables

### scenario_generator.py (422 lines)
**Generate scenarios from requirements using LLM**

Key classes:
- `ScenarioGenerator` - LLM-powered generation
- `RequirementsRetriever` - Fetch requirements from context/RAG
- `ScenarioValidator` - Validate Gherkin syntax

Features:
- Strategy Pattern (AI service with LLM fallback)
- Guard clauses for clean logic
- Dispatch table for validation
- Comprehensive prompt building
- Error handling

### feature_extractor.py (407 lines)
**Extract feature data from requirements**

Key classes:
- `FeatureExtractor` - Parse requirements
- `FeatureFileStorage` - Store feature files

Features:
- Multiple extraction strategies:
  - Structured requirements
  - User story format
  - Simple format
- Acceptance criteria parsing
- Filename sanitization

### stage_core.py (303 lines)
**Main stage orchestrator**

Key class:
- `BDDScenarioStageCore` - Stage implementation

Features:
- Implements PipelineStage interface
- Supervised execution monitoring
- Progress tracking
- Component coordination
- Artifact storage (RAG + workspace)

## Design Patterns

### Template Method Pattern
`BDDScenarioStageCore.execute()` implements consistent execution flow:
1. Retrieve requirements
2. Extract feature data
3. Generate scenarios
4. Validate syntax
5. Store artifacts

### Strategy Pattern
Multiple strategies for flexibility:
- **Generation**: AI Query Service → LLM fallback
- **Extraction**: Structured → User Story → Simple

### Value Object Pattern
Immutable data structures prevent accidental mutations:
- `Feature`, `Scenario`, `Step` are frozen dataclasses
- Once created, cannot be modified

### Facade Pattern
`BDDScenarioStageCore` provides simple interface to complex subsystem:
- Hides complexity of retrieval, generation, validation, storage
- Single execute() method for all functionality

## Backward Compatibility

Existing code continues to work via wrapper:

```python
# Old import (still works)
from bdd_scenario_generation_stage import BDDScenarioGenerationStage

# New import (recommended)
from stages.bdd_scenario import BDDScenarioStageCore

# Both work identically
# BDDScenarioGenerationStage inherits from BDDScenarioStageCore
```

## Testing

### Unit Testing Components

```python
# Test validator
from stages.bdd_scenario import ScenarioValidator

validator = ScenarioValidator()

# Valid Gherkin
result = validator.validate("""
Feature: Login
  Scenario: Success
    Given the user is on login page
    When the user enters credentials
    Then the user is logged in
""")
assert result['valid'] is True

# Invalid Gherkin (missing Then)
result = validator.validate("""
Feature: Login
  Scenario: Success
    Given the user is on login page
    When the user enters credentials
""")
assert result['valid'] is False
assert any('missing Then' in err for err in result['errors'])
```

### Mock LLM for Testing

```python
from unittest.mock import Mock
from stages.bdd_scenario import ScenarioGenerator

# Mock LLM client
mock_llm = Mock()
mock_llm.chat_completion.return_value = """
Feature: Login
  Scenario: Success
    Given the user is on login page
    When the user enters credentials
    Then the user is logged in
"""

# Test generator
generator = ScenarioGenerator(
    llm_client=mock_llm,
    logger=Mock(),
    ai_service=None
)

result = generator.generate(
    card_id="test-123",
    title="Login",
    requirements={}
)

assert "Feature: Login" in result
mock_llm.chat_completion.assert_called_once()
```

## Configuration

### LLM Parameters

```python
# Custom temperature and max tokens
gherkin_text = generator.generate(
    card_id="card-123",
    title="Feature",
    requirements={},
    temperature=0.5,    # More creative (default: 0.3)
    max_tokens=3000     # Longer response (default: 2000)
)
```

### Formatting Options

```python
# Custom indentation
formatter = GherkinFormatter(indent_spaces=4)

# Format with 4-space indent
gherkin_text = formatter.format_feature(feature)
```

### Storage Location

```python
# Custom base path
storage = FeatureFileStorage(logger=logger)
path = storage.store(
    developer="developer-a",
    title="Feature",
    content=gherkin_text,
    base_path="/custom/path"  # Default: /tmp
)
```

## Performance

### Module Loading
- First import: ~10ms (one-time cost)
- Subsequent imports: <1ms (cached)
- No runtime overhead vs monolithic implementation

### Memory Usage
- Same memory footprint as original implementation
- Modular structure enables selective imports

### Execution Performance
- No additional indirection overhead
- Dispatch tables: O(1) lookup (faster than elif chains)
- Same LLM call patterns as before

## Migration Guide

### Phase 1: No Changes (Current)
Existing code works without modifications via backward compatibility wrapper.

### Phase 2: Gradual Migration (Optional)
Update imports as you touch files:

```python
# Before
from bdd_scenario_generation_stage import BDDScenarioGenerationStage

# After
from stages.bdd_scenario import BDDScenarioStageCore as BDDScenarioGenerationStage
```

### Phase 3: Full Migration (Future)
Once all code migrated, can deprecate wrapper:

```python
# All code uses new import
from stages.bdd_scenario import BDDScenarioStageCore
```

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'stages.bdd_scenario'`

**Solution**: Ensure `stages/bdd_scenario/` directory exists with `__init__.py`

### Validation Failures

**Problem**: Generated scenarios fail validation

**Solution**:
1. Check LLM response for proper Gherkin format
2. Verify Feature: declaration present
3. Verify Scenario: declarations present
4. Verify Given/When/Then steps present

### LLM Fallback

**Problem**: AI Query Service failures

**Solution**: Generator automatically falls back to direct LLM calls. Check logs for:
```
"AI Query Service failed: {error}, falling back to direct LLM"
```

## Contributing

When modifying the package:

1. **Maintain single responsibility** - each module has one reason to change
2. **Add type hints** - all functions must have complete type hints
3. **Use guard clauses** - max 1 level of nesting
4. **Document with WHY** - explain business reasoning, not just what
5. **Add tests** - unit tests for each component
6. **Update this README** - keep documentation current

## Version History

### v1.0.0 (Current)
- Initial modular refactoring
- 6 focused modules
- Complete backward compatibility
- Full type safety
- Comprehensive documentation

## License

Part of Artemis Autonomous Development Pipeline
