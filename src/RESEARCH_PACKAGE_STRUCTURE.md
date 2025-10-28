# Research Package Structure

## Package Organization

```
research/
├── __init__.py              (64 lines)   Public API & exports
├── models.py                (53 lines)   Data models
├── base_strategy.py         (141 lines)  Abstract base class
├── github_strategy.py       (184 lines)  GitHub implementation
├── huggingface_strategy.py  (177 lines)  HuggingFace implementation
├── local_strategy.py        (279 lines)  Local filesystem implementation
└── factory.py               (127 lines)  Strategy factory

research_strategy.py         (54 lines)   Backward compatibility wrapper
```

## Module Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                     research_strategy.py                     │
│                   (Backward Compatibility)                   │
│                  Emits deprecation warning                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓ Re-exports everything
┌─────────────────────────────────────────────────────────────┐
│                      research/__init__.py                     │
│                       (Public API)                            │
│  Exports: ResearchExample, ResearchStrategy,                 │
│           All concrete strategies, Factory                    │
└──┬────────┬────────┬────────┬────────┬────────┬─────────────┘
   │        │        │        │        │        │
   ↓        ↓        ↓        ↓        ↓        ↓
┌──────┐ ┌─────────────────────────────────┐ ┌────────┐
│models│ │      base_strategy.py           │ │factory │
│      │ │   (Abstract Base Class)         │ │        │
└──────┘ │  - search() [abstract]          │ └────┬───┘
         │  - get_source_name() [abstract] │      │
         │  - _build_queries()             │      │ Registry
         │  - _fetch_url()                 │      │
         └──────────┬──────────────────────┘      │
                    │                              │
         ┌──────────┴──────────┬──────────────────┘
         │                     │                   
         ↓                     ↓                   
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│github_strategy.py│  │huggingface_...py │  │local_strategy.py │
│                  │  │                  │  │                  │
│ Implements:      │  │ Implements:      │  │ Implements:      │
│ - search()       │  │ - search()       │  │ - search()       │
│ - get_source...()│  │ - get_source...()│  │ - get_source...()│
│                  │  │                  │  │                  │
│ GitHub API calls │  │ HuggingFace API  │  │ Filesystem ops   │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## Import Patterns

### New Style (Recommended)
```python
from research import (
    ResearchExample,
    ResearchStrategyFactory,
    GitHubResearchStrategy,
    HuggingFaceResearchStrategy,
    LocalExamplesResearchStrategy
)

# Create a strategy
strategy = ResearchStrategyFactory.create_strategy("github")

# Or create all strategies
strategies = ResearchStrategyFactory.create_all_strategies()
```

### Old Style (Deprecated)
```python
from research_strategy import (  # ⚠️ Emits DeprecationWarning
    ResearchExample,
    ResearchStrategyFactory
)
```

## Class Hierarchy

```
ABC (Abstract Base Class)
  │
  └── ResearchStrategy (research/base_strategy.py)
        │
        ├── GitHubResearchStrategy (research/github_strategy.py)
        │
        ├── HuggingFaceResearchStrategy (research/huggingface_strategy.py)
        │
        └── LocalExamplesResearchStrategy (research/local_strategy.py)

@dataclass
  │
  └── ResearchExample (research/models.py)

(No inheritance)
  │
  └── ResearchStrategyFactory (research/factory.py)
```

## Data Flow

```
User Code
    │
    ↓ create_strategy("github")
ResearchStrategyFactory
    │
    ↓ lookup in _STRATEGY_REGISTRY
GitHubResearchStrategy.__init__()
    │
    ↓ search(query, technologies)
GitHubResearchStrategy.search()
    │
    ├─→ _build_queries() [inherited from base]
    │
    ├─→ _search_github_code()
    │     │
    │     ├─→ _fetch_url() [inherited from base]
    │     │
    │     └─→ _create_example_from_item()
    │           │
    │           └─→ _fetch_file_content()
    │
    └─→ Return List[ResearchExample]
```

## Module Responsibilities

### models.py
- **Size**: 53 lines
- **Responsibility**: Data structures
- **Exports**: `ResearchExample`
- **Dependencies**: `dataclasses`, `typing`

### base_strategy.py
- **Size**: 141 lines
- **Responsibility**: Abstract interface + common utilities
- **Exports**: `ResearchStrategy`
- **Dependencies**: `abc`, `typing`, `urllib`, `json`, `research_exceptions`

### github_strategy.py
- **Size**: 184 lines
- **Responsibility**: GitHub API integration
- **Exports**: `GitHubResearchStrategy`
- **Dependencies**: `base_strategy`, `models`, `urllib`, `research_exceptions`

### huggingface_strategy.py
- **Size**: 177 lines
- **Responsibility**: HuggingFace Hub integration
- **Exports**: `HuggingFaceResearchStrategy`
- **Dependencies**: `base_strategy`, `models`, `urllib`, `research_exceptions`

### local_strategy.py
- **Size**: 279 lines
- **Responsibility**: Local filesystem search
- **Exports**: `LocalExamplesResearchStrategy`
- **Dependencies**: `base_strategy`, `models`, `pathlib`, `functools`

### factory.py
- **Size**: 127 lines
- **Responsibility**: Strategy instantiation
- **Exports**: `ResearchStrategyFactory`
- **Dependencies**: All strategy classes

### __init__.py
- **Size**: 64 lines
- **Responsibility**: Public API definition
- **Exports**: All public classes
- **Dependencies**: All modules in package

## Design Patterns Applied

1. **Strategy Pattern**: Interchangeable research algorithms
2. **Factory Pattern**: Centralized strategy creation
3. **Template Method Pattern**: Base class provides common methods
4. **Registry Pattern**: Dictionary-based strategy lookup
5. **Facade Pattern**: Simplified public API via __init__.py
6. **Guard Clause Pattern**: Early returns, flat structure
7. **Value Object Pattern**: Immutable ResearchExample dataclass

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Strategy creation | O(1) | O(1) |
| Strategy lookup | O(1) | O(1) |
| Extension lookup (cached) | O(1) | O(n) |
| Query building | O(n) | O(n) |
| File search | O(n*m) | O(n) |
| GitHub search | O(n) | O(n) |
| HuggingFace search | O(n) | O(n) |

Where:
- n = number of technologies/queries
- m = number of files in directory

## Testing Strategy

### Unit Tests
```python
# Test models
def test_research_example_validation():
    example = ResearchExample(...)
    assert example.title == "..."

# Test base strategy
def test_build_queries():
    strategy = ConcreteStrategy()
    queries = strategy._build_queries("test", ["python"])
    assert len(queries) == 1

# Test concrete strategies
def test_github_search():
    strategy = GitHubResearchStrategy()
    results = strategy.search("authentication", ["python"])
    assert len(results) <= 5

# Test factory
def test_create_strategy():
    strategy = ResearchStrategyFactory.create_strategy("github")
    assert isinstance(strategy, GitHubResearchStrategy)
```

### Integration Tests
```python
def test_end_to_end_search():
    factory = ResearchStrategyFactory()
    for source in factory.get_available_sources():
        strategy = factory.create_strategy(source)
        results = strategy.search("REST API", ["python"], max_results=3)
        assert all(isinstance(r, ResearchExample) for r in results)
```

## Migration Guide

### Step 1: Update Imports
Replace:
```python
from research_strategy import ResearchStrategyFactory
```

With:
```python
from research import ResearchStrategyFactory
```

### Step 2: Update Direct Strategy Imports
Replace:
```python
from research_strategy import GitHubResearchStrategy
```

With:
```python
from research import GitHubResearchStrategy
```

### Step 3: No Code Changes Required
All functionality remains the same. Only import paths change.

### Step 4: Run Tests
Ensure all tests pass with new imports.

### Step 5: Remove Deprecation Warnings
Once all imports are updated, remove the old wrapper (optional).

## Extension Example

Adding a new strategy:

```python
# research/stackoverflow_strategy.py
from research.base_strategy import ResearchStrategy
from research.models import ResearchExample

class StackOverflowResearchStrategy(ResearchStrategy):
    def get_source_name(self) -> str:
        return "StackOverflow"
    
    def search(self, query: str, technologies: List[str], 
               max_results: int = 5) -> List[ResearchExample]:
        # Implementation here
        pass

# Register in factory
ResearchStrategyFactory.register_strategy(
    "stackoverflow", 
    StackOverflowResearchStrategy
)
```

## Conclusion

The research package provides a clean, modular architecture for code research functionality:

- **7 focused modules** (avg 146 lines each)
- **100% backward compatible** via wrapper
- **Fully documented** with WHY/RESPONSIBILITY/PATTERNS
- **Type-safe** with comprehensive type hints
- **Extensible** via factory registration
- **Testable** with isolated, mockable components
- **Production-ready** with proper error handling

**Total: 1,079 lines** (1,025 in package + 54 in wrapper)
