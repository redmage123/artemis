# RAG Module Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         rag_agent.py                             │
│                   (Backward Compatibility Wrapper)               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     RAGAgent (285 lines)                    │ │
│  │  - Adapter/Proxy wrapping RAGEngine                         │ │
│  │  - Maintains original interface                             │ │
│  │  - Integrates with DebugMixin                               │ │
│  └──────────────────────┬───────────────────────────────────────┘ │
└────────────────────────┼──────────────────────────────────────────┘
                         │
                         │ delegates to
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                          rag/ Package                            │
│                     (Modular Architecture)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  rag_engine.py (236 lines)                  │ │
│  │                    [Orchestration Layer]                     │ │
│  │                                                               │ │
│  │  RAGEngine: Main coordination class                          │ │
│  │  - store_artifact()                                          │ │
│  │  - query_similar()                                           │ │
│  │  - get_recommendations()                                     │ │
│  │  - extract_patterns()                                        │ │
│  │  - get_stats()                                               │ │
│  └───────┬──────────────────────────┬──────────────────┬────────┘ │
│          │                          │                  │          │
│          │ uses                     │ uses             │ uses     │
│          ▼                          ▼                  ▼          │
│  ┌──────────────┐         ┌──────────────┐   ┌────────────────┐ │
│  │vector_store  │         │  retriever   │   │pattern_analyzer│ │
│  │  (233 lines) │         │  (200 lines) │   │  (280 lines)   │ │
│  ├──────────────┤         ├──────────────┤   ├────────────────┤ │
│  │VectorStore   │◄────────│Retriever     │   │PatternAnalyzer │ │
│  │              │         │              │   │                │ │
│  │+ add()       │         │+ query()     │   │+ recommend()   │ │
│  │+ query_coll()│         │+ search()    │   │+ extract()     │ │
│  │+ get_counts()│         └──────────────┘   └────────────────┘ │
│  └──────┬───────┘                                                │
│         │                                                        │
│         │ uses                                                   │
│         ▼                                                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         document_processor.py (140 lines)                 │   │
│  │              [Utility Functions]                          │   │
│  │                                                            │   │
│  │  + generate_artifact_id()                                 │   │
│  │  + serialize_metadata_for_chromadb()                      │   │
│  │  + deserialize_metadata()                                 │   │
│  │  + prepare_artifact_metadata()                            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              models.py (143 lines)                        │   │
│  │              [Data Structures]                            │   │
│  │                                                            │   │
│  │  @dataclass Artifact                                      │   │
│  │  @dataclass SearchResult                                  │   │
│  │  ARTIFACT_TYPES: List[str]                                │   │
│  │  + create_artifact()                                      │   │
│  │  + create_search_result()                                 │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              __init__.py (73 lines)                       │   │
│  │              [Package API]                                │   │
│  │                                                            │   │
│  │  Exports: RAGEngine, VectorStore, Retriever,              │   │
│  │           PatternAnalyzer, Artifact, SearchResult,        │   │
│  │           create_rag_agent(), utility functions           │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Storage Operation
```
User Code
    │
    ▼
RAGAgent.store_artifact()
    │
    ▼
RAGEngine.store_artifact()
    │
    ├─► generate_artifact_id()              [document_processor]
    ├─► create_artifact()                   [models]
    ├─► prepare_artifact_metadata()         [document_processor]
    │
    ▼
VectorStore.add_artifact()
    │
    ├─► ChromaDB collection.add()
    └─► Mock storage (fallback)
```

### Query Operation
```
User Code
    │
    ▼
RAGAgent.query_similar()
    │
    ▼
RAGEngine.query_similar()
    │
    ▼
Retriever.query_similar()
    │
    ├─► VectorStore.query_collection()      [per artifact type]
    ├─► deserialize_metadata()              [document_processor]
    │
    ▼
Sort & aggregate results
    │
    ▼
Return List[SearchResult]
```

### Recommendation Operation
```
User Code
    │
    ▼
RAGAgent.get_recommendations()
    │
    ▼
RAGEngine.get_recommendations()
    │
    ▼
PatternAnalyzer.get_recommendations()
    │
    ├─► Retriever.query_similar()           [similar tasks]
    ├─► _extract_technology_patterns()
    ├─► _extract_success_patterns()
    ├─► _extract_issues()
    │
    ▼
Build recommendations dict
    │
    ▼
Return Dict[str, Any]
```

## Design Patterns Map

| Pattern | Location | Purpose |
|---------|----------|---------|
| **Adapter** | `rag_agent.py` | Adapt RAGEngine to old RAGAgent interface |
| **Proxy** | `rag_agent.py` | Delegate calls to underlying engine |
| **Facade** | `rag_engine.py`, `__init__.py` | Simplify complex subsystem access |
| **Repository** | `vector_store.py` | Abstract storage implementation |
| **Strategy** | `vector_store.py`, `retriever.py`, `pattern_analyzer.py` | Swap algorithms (storage, search, analysis) |
| **Null Object** | `vector_store.py` | Mock storage for graceful degradation |
| **Builder** | `retriever.py`, `pattern_analyzer.py` | Construct complex queries/recommendations |
| **Dependency Injection** | All classes | Constructor injection for testability |
| **Factory Method** | `models.py` | `create_artifact()`, `create_search_result()` |
| **Value Object** | `models.py` | Immutable `Artifact`, `SearchResult` dataclasses |
| **Command** | `pattern_analyzer.py` | Encapsulate analysis requests |

## Module Responsibility Matrix

| Module | Lines | Primary Responsibility | Secondary Responsibilities |
|--------|-------|------------------------|---------------------------|
| `models.py` | 143 | Define data structures | Factory functions, type definitions |
| `document_processor.py` | 140 | Transform documents | ID generation, serialization, metadata prep |
| `vector_store.py` | 233 | Abstract storage | Collection management, stats |
| `retriever.py` | 200 | Execute searches | Multi-collection queries, result aggregation |
| `pattern_analyzer.py` | 280 | Extract patterns | Generate recommendations, confidence scoring |
| `rag_engine.py` | 236 | Orchestrate operations | Coordinate components, logging |
| `__init__.py` | 73 | Export public API | Package version, convenience functions |

## Dependencies

### External Dependencies
- `chromadb`: Vector database (optional - mock fallback available)
- `sentence-transformers`: Embeddings (via ChromaDB)
- `dataclasses`: Data structures (Python stdlib)
- `pathlib`: Path handling (Python stdlib)
- `typing`: Type hints (Python stdlib)

### Internal Dependencies
```
models.py               ← (no internal deps)
    ↑
document_processor.py   ← (no internal deps)
    ↑
vector_store.py         ← models
    ↑
retriever.py            ← models, document_processor, vector_store
    ↑
pattern_analyzer.py     ← (uses retriever via injection)
    ↑
rag_engine.py           ← models, document_processor, vector_store,
    ↑                     retriever, pattern_analyzer
__init__.py             ← (imports all modules)
    ↑
rag_agent.py            ← rag/__init__ (imports from package)
```

## Extension Points

### Adding New Artifact Types
1. Add to `ARTIFACT_TYPES` in `models.py`
2. VectorStore automatically creates collection
3. No other changes needed

### Adding New Storage Backend
1. Implement interface matching `VectorStore` methods
2. Inject into `RAGEngine` constructor
3. Or add strategy to `VectorStore.__init__()`

### Adding New Search Strategy
1. Add method to `Retriever` class
2. Use strategy pattern for algorithm selection
3. Expose via `RAGEngine` if needed

### Adding New Pattern Type
1. Add extractor method to `PatternAnalyzer`
2. Add to dispatch table in `extract_patterns()`
3. Define return type structure

## Testing Strategy

### Unit Tests
- `models.py`: Test data structure creation and serialization
- `document_processor.py`: Test pure functions in isolation
- `vector_store.py`: Test with mock ChromaDB or in-memory
- `retriever.py`: Test with mock VectorStore
- `pattern_analyzer.py`: Test with mock query function
- `rag_engine.py`: Test with injected mocks

### Integration Tests
- Test full storage → retrieval flow
- Test recommendation generation pipeline
- Test backward compatibility wrapper

### Performance Tests
- Benchmark large-scale storage operations
- Measure query latency at different scales
- Profile memory usage with large datasets
