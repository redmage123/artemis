# User Story Package Architecture

## Overview

Modular package for generating user stories from Architecture Decision Records (ADRs) using LLMs.

## Package Structure

```
user_story/
├── __init__.py              (89 lines)  - Public API exports
├── models.py               (175 lines)  - Data structures
├── validator.py            (264 lines)  - Story validation
├── prompt_builder.py       (251 lines)  - Prompt generation
├── parser.py               (330 lines)  - Response parsing
└── generator.py            (337 lines)  - Main orchestration
```

**Total:** 1,446 lines across 6 modules

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  UserStoryGenerator                          │
│                     (generator.py)                           │
│                                                              │
│  Facade Pattern: Orchestrates all components                │
└───────┬──────────────┬──────────────┬──────────────┬────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────┐
│ PromptBuilder│ │UserStoryParser│ │Validator │ │  Models  │
│ (251 lines)  │ │  (330 lines)  │ │(264 lines│ │(175 lines│
│              │ │               │ │          │ │          │
│ Builds       │ │ Parses LLM    │ │Validates │ │Data      │
│ prompts      │ │ responses     │ │stories   │ │structures│
└──────────────┘ └──────────────┘ └──────────┘ └──────────┘
```

## Data Flow

```
1. Input: ADR Content
        │
        ▼
2. PromptBuilder.build_prompts()
        │
        ├──► Try RAG prompts
        │    (from PromptManager)
        │
        └──► Fallback to default
             prompts
        │
        ▼
3. LLM Client (external)
        │
        ▼
4. UserStoryParser.parse_response()
        │
        ├──► Try code block parsing
        ├──► Try direct JSON
        └──► Try JSON search
        │
        ▼
5. UserStoryValidator.validate_stories()
        │
        ├──► Check required fields
        ├──► Validate field types
        └──► Filter invalid stories
        │
        ▼
6. Output: List[UserStory]
```

## Design Patterns

### 1. Facade Pattern
- **Where:** `UserStoryGenerator`
- **Why:** Simple interface to complex subsystem
- **Benefit:** Easy to use, hides complexity

### 2. Strategy Pattern
- **Where:** Validator field validators, Parser strategies
- **Why:** Avoid if/elif chains, enable extension
- **Benefit:** Open/Closed principle

### 3. Composition Over Inheritance
- **Where:** Generator composes validator, parser, builder
- **Why:** Flexibility, testability
- **Benefit:** Easy to replace components

### 4. Builder Pattern
- **Where:** `UserStoryGeneratorBuilder`
- **Why:** Fluent API for complex construction
- **Benefit:** Readable configuration

### 5. Immutable Data Structures
- **Where:** All dataclasses (frozen)
- **Why:** Prevent bugs from mutations
- **Benefit:** Thread-safe, predictable

### 6. Guard Clauses
- **Where:** Every module
- **Why:** Early returns, avoid nesting
- **Benefit:** Readable, maintainable

## Module Responsibilities

### models.py - Data Structures
```python
UserStory           # Immutable story representation
PromptContext       # Context for prompt generation
GenerationConfig    # LLM generation settings
Constants           # VALID_PRIORITIES, REQUIRED_FIELDS
```

**Patterns:** Immutability, factory methods, validation

### validator.py - Validation Logic
```python
UserStoryValidator  # Validates story structure
ValidationResult    # Result object with errors
Validators          # Dictionary of field validators
```

**Patterns:** Strategy (validator dict), declarative filtering

### prompt_builder.py - Prompt Generation
```python
PromptBuilder        # Builds prompts (RAG + default)
PromptBuilderFactory # Factory for builder creation
build_prompts_for_adr() # Convenience function
```

**Patterns:** Strategy (RAG vs default), template method, factory

### parser.py - Response Parsing
```python
UserStoryParser     # Parses LLM responses
ParseResult         # Result object for parsing
ParsingError        # Custom exception
```

**Patterns:** Strategy (multiple parse methods), compiled regex

### generator.py - Orchestration
```python
UserStoryGenerator        # Main facade
UserStoryGeneratorBuilder # Builder for construction
```

**Patterns:** Facade, composition, dependency injection, builder

## Usage Examples

### Basic Usage (Backward Compatible)
```python
from user_story_generator import UserStoryGenerator

generator = UserStoryGenerator(llm_client, logger, prompt_manager)
stories = generator.generate_user_stories(adr_content, "001", parent_card)
```

### Modular Usage (New)
```python
from user_story import (
    UserStoryGenerator,
    UserStoryValidator,
    UserStoryParser,
    PromptBuilder
)

# Use components independently
validator = UserStoryValidator(logger)
is_valid = validator.validate_story(story_dict)

parser = UserStoryParser(logger)
stories = parser.parse_response(llm_response)

# Or use facade
generator = UserStoryGenerator(llm_client, logger, prompt_manager)
stories = generator.generate_user_stories(adr_content, "001", parent_card)
```

### Builder Pattern (New)
```python
from user_story import UserStoryGeneratorBuilder

generator = (UserStoryGeneratorBuilder()
    .with_llm_client(llm_client)
    .with_logger(logger)
    .with_prompt_manager(prompt_manager)
    .with_temperature(0.5)
    .build())
```

## Extension Points

### Add New Validator Rules
```python
# In validator.py, add to FIELD_TYPE_VALIDATORS
FIELD_TYPE_VALIDATORS = {
    'title': lambda v: isinstance(v, str) and len(v) > 0,
    'new_field': lambda v: custom_validation(v),  # Add here
}
```

### Add New Parser Strategy
```python
# In parser.py, add to parsing_strategies
def _parse_custom_format(self, response: str) -> List[Dict]:
    # Custom parsing logic
    pass

# Add to strategy list
parsing_strategies = [
    ('code_block', self._parse_code_block),
    ('custom', self._parse_custom_format),  # Add here
]
```

### Add New Prompt Source
```python
# Subclass PromptBuilder or inject custom prompt_manager
class CustomPromptBuilder(PromptBuilder):
    def _build_custom_prompts(self, context):
        # Custom prompt logic
        pass
```

## Testing Strategy

### Unit Tests
- `test_models.py` - Test data structures
- `test_validator.py` - Test validation logic
- `test_prompt_builder.py` - Test prompt generation
- `test_parser.py` - Test response parsing
- `test_generator.py` - Test orchestration

### Integration Tests
- `test_integration.py` - Test complete workflow
- `test_rag_integration.py` - Test RAG prompts
- `test_error_handling.py` - Test error scenarios

### Mocking Strategy
- Mock `llm_client` for predictable responses
- Mock `prompt_manager` for RAG testing
- Mock `logger` to verify logging calls

## Performance Considerations

### Optimizations Applied
1. **Compiled Regex** - JSON_PATTERN, CODE_BLOCK_PATTERN compiled once
2. **List Comprehensions** - Faster than explicit loops
3. **Guard Clauses** - Early returns prevent unnecessary processing
4. **Dictionary Lookups** - O(1) strategy selection
5. **Immutable Data** - Safe for concurrent access

### Complexity Analysis
- `generate_user_stories()`: O(n) where n = response length
- `validate_stories()`: O(n*m) where n = stories, m = fields
- `parse_response()`: O(n) where n = response length
- Overall: Linear complexity with respect to input size

## Dependencies

### Internal
- `artemis_stage_interface.LoggerInterface` (optional)
- `llm_client.LLMMessage` (optional, with fallback)

### External (stdlib)
- `json` - JSON parsing
- `re` - Regex pattern matching
- `typing` - Type hints
- `dataclasses` - Data structures

## Backward Compatibility

The wrapper at `user_story_generator.py` (51 lines) maintains 100% API compatibility:

```python
# Original import (still works)
from user_story_generator import UserStoryGenerator

# New import (recommended)
from user_story import UserStoryGenerator
```

Both imports reference the same class instance.

## Future Enhancements

1. **Add caching** - Cache parsed stories for identical ADRs
2. **Add metrics** - Track parsing success rates
3. **Add validation rules** - More sophisticated story validation
4. **Add parser strategies** - Support more LLM output formats
5. **Add prompt templates** - More customizable prompt building
6. **Add async support** - Async LLM calls for performance

## Compliance

✅ **Claude.md Standards** - All patterns applied
✅ **SOLID Principles** - Each module has single responsibility
✅ **Type Safety** - Complete type hints throughout
✅ **Performance** - Optimizations applied (comprehensions, compiled regex)
✅ **Documentation** - WHY/RESPONSIBILITY/PATTERNS in every module
✅ **Testing** - Fully testable with clear interfaces

---

**Architecture Version:** 1.0.0
**Last Updated:** 2025-10-28
**Status:** ✅ Production Ready
