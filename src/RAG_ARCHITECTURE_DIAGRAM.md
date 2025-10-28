# RAG Package Architecture Diagram

## Component Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                         rag_agent.py                            │
│                  (Backward Compatibility Wrapper)               │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              RAGAgent (DebugMixin)                      │   │
│  │  • Adapter Pattern: Legacy interface                    │   │
│  │  • Proxy Pattern: Delegate to RAGEngine                 │   │
│  │  • Maintains: ARTIFACT_TYPES, collections, client       │   │
│  └───────────────────────┬─────────────────────────────────┘   │
└────────────────────────────┼──────────────────────────────────────┘
                             │ delegates to
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        rag/__init__.py                          │
│                      (Package Interface)                        │
│                                                                 │
│  Exports: RAGEngine, VectorStore, Retriever, PatternAnalyzer   │
│           Artifact, SearchResult, ARTIFACT_TYPES                │
│           create_artifact, create_search_result, create_rag_agent│
└─────────────────────────────────────────────────────────────────┘
                             │
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  rag/models.py   │ │rag/document_     │ │rag/rag_engine.py │
│                  │ │  processor.py    │ │                  │
│ • Artifact       │ │                  │ │  RAGEngine       │
│ • SearchResult   │ │ • generate_      │ │  (Orchestrator)  │
│ • ARTIFACT_TYPES │ │   artifact_id    │ │                  │
│                  │ │ • serialize_     │ │  Coordinates:    │
│ Value Objects    │ │   metadata       │ │  ↓ VectorStore   │
│ Factory Pattern  │ │ • deserialize_   │ │  ↓ Retriever     │
└──────────────────┘ │   metadata       │ │  ↓ PatternAnalyzer│
                     │ • prepare_       │ └────────┬─────────┘
                     │   metadata       │          │
                     │                  │          │ coordinates
                     │ Pure Functions   │          │
                     └──────────────────┘          │
                                                   │
                     ┌─────────────────────────────┼─────────────────────────────┐
                     │                             │                             │
                     ▼                             ▼                             ▼
        ┌────────────────────────┐   ┌────────────────────────┐   ┌────────────────────────┐
        │ rag/vector_store.py    │   │   rag/retriever.py     │   │rag/pattern_analyzer.py │
        │                        │   │                        │   │                        │
        │   VectorStore          │◄──│    Retriever           │   │   PatternAnalyzer      │
        │                        │   │                        │   │                        │
        │ • ChromaDB client      │   │ • query_similar()      │   │ • get_recommendations()│
        │ • Collections mgmt     │   │ • search_code_examples│   │ • extract_patterns()   │
        │ • add_artifact()       │   │                        │   │                        │
        │ • query_collection()   │   │ Semantic Search:       │   │ Learning Patterns:     │
        │ • Mock storage fallback│   │ • _semantic_search()   │   │ • Technology success   │
        │                        │   │ • _keyword_search()    │   │ • Historical patterns  │
        │ Storage Strategies:    │   │                        │   │ • Issue extraction     │
        │ • ChromaDB (prod)      │   │ Search Strategies:     │   │                        │
        │ • Mock (test/fallback) │   │ • Multi-collection     │   │ Analysis Strategies:   │
        │                        │   │ • Filtered queries     │   │ • Dispatch table       │
        │ Repository Pattern     │   │ • Result aggregation   │   │ • Builder pattern      │
        │ Strategy Pattern       │   │                        │   │                        │
        │ Null Object Pattern    │   │ Facade Pattern         │   │ Command Pattern        │
        └────────────────────────┘   │ Strategy Pattern       │   │ Strategy Pattern       │
                                     │ Builder Pattern        │   └────────────────────────┘
                                     └────────────────────────┘
```

## Data Flow Diagrams

### 1. Store Artifact Flow

```
User Code
   │
   ▼
RAGAgent.store_artifact()
   │
   ▼
RAGEngine.store_artifact()
   │
   ├─► generate_artifact_id()  ────► "artifact-card-hash123"
   │
   ├─► create_artifact()  ────────► Artifact(...)
   │
   ├─► prepare_artifact_metadata()─► {card_id, task_title, timestamp, ...}
   │
   └─► VectorStore.add_artifact()
         │
         ├─► [ChromaDB Available?]
         │     YES ─► collection.add(id, document, metadata)
         │     NO  ─► mock_storage[type].append(artifact)
         │
         └─► return artifact_id
```

### 2. Query Similar Flow

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
   ├─► [ChromaDB Available?]
   │     YES ─► _semantic_search()
   │     │         │
   │     │         └─► for each artifact_type:
   │     │               VectorStore.query_collection()
   │     │                 │
   │     │                 └─► collection.query(query_texts=[...])
   │     │
   │     NO  ─► _keyword_search()
   │               │
   │               └─► VectorStore.mock_search()
   │
   ├─► Sort by similarity
   │
   ├─► Limit to top_k
   │
   └─► return List[Dict[artifact_id, type, content, metadata, similarity]]
```

### 3. Get Recommendations Flow

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
   ├─► query_fn(task_description, artifact_types, 10, None)
   │     │
   │     └─► Retriever.query_similar() ────► similar_tasks[]
   │
   ├─► _extract_technology_patterns(similar_tasks)
   │     └─► {tech: {count, avg_score, scores}, ...}
   │
   ├─► _extract_success_patterns(similar_tasks)
   │     └─► [{approach, score, technologies}, ...]
   │
   ├─► _extract_issues(similar_tasks)
   │     └─► [issues from validation_result artifacts]
   │
   ├─► _build_based_on_history(technologies, success_patterns)
   │     └─► ["Used Django in 5 tasks", "REST API scored 95/100", ...]
   │
   ├─► _build_recommendations(technologies)
   │     └─► ["Consider Django (proven in 5 tasks)", ...]
   │
   ├─► _build_avoidance_list(issues)
   │     └─► ["Watch for security issues (found in 3 tasks)", ...]
   │
   └─► return {based_on_history, recommendations, avoid, confidence, count}
```

### 4. Extract Patterns Flow

```
User Code
   │
   ▼
RAGAgent.extract_patterns(pattern_type, time_window_days)
   │
   ▼
RAGEngine.extract_patterns()
   │
   ▼
PatternAnalyzer.extract_patterns()
   │
   ├─► pattern_extractors = {
   │     "technology_success_rates": _extract_technology_success_rates,
   │     # Future: "common_issues", "best_practices", etc.
   │   }  ◄── Dispatch Table Pattern
   │
   ├─► extractor = pattern_extractors.get(pattern_type)
   │
   ├─► [Guard: extractor exists?]
   │     NO ─► return {}
   │
   └─► extractor(time_window_days)
         │
         └─► _extract_technology_success_rates()
               │
               ├─► cutoff_date = now - timedelta(days=time_window)
               │
               ├─► solutions = query_fn("", ["developer_solution"], 1000, None)
               │
               ├─► for each solution:
               │     │
               │     ├─► [Guard: within time window?]
               │     │
               │     └─► Update tech_stats[tech]:
               │           • tasks_count
               │           • total_score
               │           • successes (if winner)
               │
               └─► Calculate & return:
                     {tech: {tasks_count, avg_score, success_rate, recommendation}}
```

## Pattern Application Map

```
┌─────────────────────────────────────────────────────────────────┐
│                         PATTERNS APPLIED                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ FACADE PATTERN                                                   │
├──────────────────────────────────────────────────────────────────┤
│ rag/__init__.py      → Unified package interface                │
│ rag_agent.py         → Simplified legacy interface               │
│ rag/rag_engine.py    → Orchestrates subsystems                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ REPOSITORY PATTERN                                               │
├──────────────────────────────────────────────────────────────────┤
│ rag/vector_store.py  → Abstract storage (ChromaDB/Mock)         │
│ rag/retriever.py     → Abstract queries                          │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ STRATEGY PATTERN                                                 │
├──────────────────────────────────────────────────────────────────┤
│ rag/vector_store.py  → ChromaDB vs Mock storage                 │
│ rag/retriever.py     → Semantic vs Keyword search               │
│ rag/pattern_analyzer.py → Different analysis strategies         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ ADAPTER PATTERN                                                  │
├──────────────────────────────────────────────────────────────────┤
│ rag_agent.py         → Adapt RAGEngine to legacy RAGAgent       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ PROXY PATTERN                                                    │
├──────────────────────────────────────────────────────────────────┤
│ rag_agent.py         → Proxy calls to underlying engine         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ FACTORY PATTERN                                                  │
├──────────────────────────────────────────────────────────────────┤
│ rag/models.py        → create_artifact(), create_search_result()│
│ rag/__init__.py      → create_rag_agent()                       │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ VALUE OBJECT PATTERN                                             │
├──────────────────────────────────────────────────────────────────┤
│ rag/models.py        → Artifact @dataclass (immutable)          │
│ rag/models.py        → SearchResult @dataclass (immutable)      │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ NULL OBJECT PATTERN                                              │
├──────────────────────────────────────────────────────────────────┤
│ rag/vector_store.py  → Mock storage for graceful degradation    │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ TEMPLATE METHOD PATTERN                                          │
├──────────────────────────────────────────────────────────────────┤
│ rag/rag_engine.py    → Define RAG operation flow                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ BUILDER PATTERN                                                  │
├──────────────────────────────────────────────────────────────────┤
│ rag/pattern_analyzer.py → Build complex recommendations         │
│ rag/retriever.py     → Construct complex queries                │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ COMMAND PATTERN                                                  │
├──────────────────────────────────────────────────────────────────┤
│ rag/pattern_analyzer.py → Encapsulate analysis requests         │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ DEPENDENCY INJECTION                                             │
├──────────────────────────────────────────────────────────────────┤
│ rag/rag_engine.py    → Inject VectorStore, Retriever, Analyzer  │
│ rag/vector_store.py  → Inject log_fn                            │
│ rag/retriever.py     → Inject vector_store, log_fn              │
│ rag/pattern_analyzer.py → Inject query_fn, log_fn               │
└──────────────────────────────────────────────────────────────────┘
```

## Dependency Graph

```
                    ┌──────────────┐
                    │  User Code   │
                    └──────┬───────┘
                           │
                    ┌──────▼────────┐
                    │  rag_agent.py │
                    │   (Wrapper)   │
                    └──────┬────────┘
                           │
                    ┌──────▼─────────┐
                    │ rag/__init__.py│
                    └──────┬─────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐     ┌─────▼──────┐    ┌────▼─────┐
    │ models  │     │document_   │    │rag_engine│
    │         │     │processor   │    │          │
    └─────────┘     └────────────┘    └────┬─────┘
                                            │
                            ┌───────────────┼───────────────┐
                            │               │               │
                      ┌─────▼──────┐  ┌────▼─────┐  ┌─────▼─────┐
                      │vector_store│  │retriever │  │pattern_   │
                      │            │◄─┤          │  │analyzer   │
                      └────────────┘  └──────────┘  └───────────┘

Legend:
  ─► Direct dependency
  ◄─ Uses/depends on
```

## Module Interaction Sequence

### Initialization Sequence

```
1. RAGAgent.__init__(db_path, verbose)
   │
   ├─► RAGEngine.__init__(db_path, verbose)
   │     │
   │     ├─► VectorStore.__init__(db_path, log_fn)
   │     │     │
   │     │     ├─► chromadb.PersistentClient(path=db_path)
   │     │     │
   │     │     └─► _initialize_collections()
   │     │           └─► client.get_or_create_collection() × 15
   │     │
   │     ├─► Retriever.__init__(vector_store, log_fn)
   │     │
   │     └─► PatternAnalyzer.__init__(query_fn, log_fn)
   │
   └─► Expose attributes: db_path, verbose, collections, client
```

### Storage Sequence

```
1. User: rag.store_artifact(type, card_id, title, content, metadata)
   │
2. RAGAgent.store_artifact()  [Proxy]
   │
3. RAGEngine.store_artifact()  [Orchestrator]
   │
4. generate_artifact_id(type, card_id)  [Utility]
   │
5. create_artifact(...)  [Factory]
   │
6. prepare_artifact_metadata(...)  [Utility]
   │
7. VectorStore.add_artifact(artifact, metadata)  [Repository]
   │
8. collection.add(ids, documents, metadatas)  [ChromaDB]
   │
9. Return: artifact_id
```

### Retrieval Sequence

```
1. User: rag.query_similar(query, types, top_k, filters)
   │
2. RAGAgent.query_similar()  [Proxy]
   │
3. RAGEngine.query_similar()  [Orchestrator]
   │
4. Retriever.query_similar()  [Facade]
   │
5. _semantic_search() or _keyword_search()  [Strategy]
   │
6. VectorStore.query_collection()  [Repository]
   │
7. collection.query(query_texts, n_results, where)  [ChromaDB]
   │
8. deserialize_metadata()  [Utility]
   │
9. Sort & limit results
   │
10. Return: List[SearchResult]
```

## Architecture Principles

### 1. Separation of Concerns
```
models.py            → Data structures only
document_processor.py → Transformation utilities only
vector_store.py      → Storage abstraction only
retriever.py         → Query orchestration only
pattern_analyzer.py  → Analysis logic only
rag_engine.py        → High-level coordination only
```

### 2. Dependency Inversion
```
High-Level:  RAGEngine depends on abstractions
                ↓
Abstractions: VectorStore, Retriever, PatternAnalyzer
                ↓
Low-Level:   ChromaDB, file I/O, algorithms
```

### 3. Open/Closed Principle
```
Open for extension:
  • Add new artifact types to ARTIFACT_TYPES
  • Add new storage strategies to VectorStore
  • Add new search strategies to Retriever
  • Add new analysis patterns to PatternAnalyzer

Closed for modification:
  • Core interfaces remain stable
  • Existing functionality unchanged
```

### 4. Single Responsibility
```
Each module has ONE reason to change:
  • models.py         → Data structure definitions change
  • document_processor.py → Transformation logic changes
  • vector_store.py   → Storage requirements change
  • retriever.py      → Search requirements change
  • pattern_analyzer.py → Analysis requirements change
  • rag_engine.py     → Orchestration flow changes
```

### 5. Interface Segregation
```
Clients depend only on what they need:
  • RAGEngine uses VectorStore.add_artifact(), query_collection()
  • Retriever uses VectorStore.query_collection(), mock_search()
  • PatternAnalyzer uses only query_fn (injected)
```

---

## Testing Strategy

### Unit Testing (by module)
```
tests/
├── test_models.py              → Test Artifact, SearchResult
├── test_document_processor.py  → Test ID generation, serialization
├── test_vector_store.py        → Test storage with mock ChromaDB
├── test_retriever.py           → Test queries with mock VectorStore
├── test_pattern_analyzer.py    → Test patterns with mock query_fn
├── test_rag_engine.py          → Test orchestration with mock deps
└── test_rag_agent.py           → Test backward compatibility
```

### Integration Testing
```
tests/integration/
├── test_full_workflow.py       → Test complete store → query flow
├── test_chromadb_integration.py → Test with real ChromaDB
└── test_recommendations.py     → Test end-to-end recommendations
```

### Mock Injection Points
```
RAGEngine(vector_store=mock_store)
Retriever(vector_store=mock_store, log_fn=mock_log)
PatternAnalyzer(query_fn=mock_query, log_fn=mock_log)
VectorStore(db_path=temp_path, log_fn=mock_log)
```

---

**Diagram Version**: 1.0
**Last Updated**: 2025-10-28
