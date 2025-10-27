# RAG Agent - Skills

## Agent Overview
**File**: `rag_agent.py`
**Purpose**: Pipeline memory and continuous learning through vector embeddings
**Single Responsibility**: Store and retrieve pipeline artifacts using semantic search

## Core Skills

### 1. Artifact Storage
- **Research Reports**: Store project analysis and findings
- **Architecture Decisions (ADRs)**: Store design decisions and rationale
- **Developer Solutions**: Store implementation code
- **Validation Results**: Store test and review outcomes
- **Arbitration Scores**: Store developer comparison metrics
- **Issue Resolutions**: Store problem-solution pairs
- **Supervisor Recovery**: Store recovery workflow outcomes
- **Sprint Plans**: Store sprint planning with story point estimates
- **Notebook Examples**: Store Jupyter notebook templates
- **Code Examples**: Store GitHub/HuggingFace/local code samples

### 2. Semantic Search
- **Vector Embeddings**: ChromaDB with sentence-transformers
- **Similarity Search**: Find related artifacts by meaning
- **Multi-Type Queries**: Search across different artifact types
- **Top-K Retrieval**: Configurable result count
- **Context-Aware**: Task-specific relevance scoring

### 3. Continuous Learning
- **Pattern Recognition**: Learns from successful implementations
- **Historical Context**: Provides "what worked before" insights
- **Best Practice Evolution**: Updates recommendations based on outcomes
- **Anti-Pattern Detection**: Identifies failed approaches to avoid

### 4. Knowledge Persistence
- **Persistent Vector Store**: ChromaDB database
- **Metadata Tracking**: Card ID, task title, timestamps
- **Deduplication**: Prevents duplicate artifact storage
- **Cleanup**: Removes outdated or irrelevant artifacts

### 5. Cross-Stage Integration
- **Research Stage**: Stores research findings
- **Planning Stage**: Stores sprint plans and story points
- **Development Stage**: Stores code examples and solutions
- **Review Stage**: Stores code review feedback
- **Supervisor**: Stores recovery patterns and issue resolutions

## Artifact Types Supported

1. `research_report` - Project analysis and research findings
2. `project_analysis` - Pre-implementation analysis
3. `project_review` - Quality gate reviews
4. `architecture_decision` - ADRs with rationale
5. `developer_solution` - Implementation code
6. `validation_result` - Test outcomes
7. `arbitration_score` - Developer comparison metrics
8. `integration_result` - Integration test results
9. `testing_result` - Test execution results
10. `issue_and_fix` - Problem-solution pairs
11. `issue_resolution` - Supervisor recovery tracking
12. `supervisor_recovery` - Recovery workflow outcomes
13. `sprint_plan` - Sprint planning with estimates
14. `notebook_example` - Jupyter notebook templates
15. `code_example` - Code snippets from various sources

## Configuration

**Database Path**:
- Default: `db/` (relative to agent location)
- Configurable via constructor parameter
- Auto-creates directory if missing

**Dependencies**:
- `chromadb`: Vector database
- `sentence-transformers`: Text embeddings
- Falls back to mock mode if ChromaDB unavailable

## Usage Patterns

```python
# Initialize RAG agent
rag = RAGAgent(db_path="db", verbose=True)

# Store artifact
rag.store_artifact(
    artifact_type="developer_solution",
    card_id="card-20251027-001",
    task_title="User Authentication System",
    content=implementation_code,
    metadata={"developer": "developer-a", "tests_passed": True}
)

# Search artifacts
results = rag.search(
    query="JWT authentication with role-based access control",
    top_k=5,
    artifact_type="developer_solution"  # Optional filter
)

# Get artifacts by card ID
artifacts = rag.get_artifacts_by_card("card-20251027-001")
```

## Design Patterns

- **Repository Pattern**: Abstracts data storage
- **Facade Pattern**: Simplifies ChromaDB complexity
- **Mock Object Pattern**: Graceful degradation without ChromaDB
- **Value Object**: Artifact dataclass

## Performance Optimizations

- **Persistent Storage**: No re-embedding on restart
- **Indexed Search**: ChromaDB's HNSW vector index
- **Batch Operations**: Stores multiple artifacts efficiently
- **Lazy Loading**: Collections created on-demand

## Integration Points

- **All Pipeline Stages**: Every stage can store/retrieve
- **Prompt Manager**: Queries RAG for dynamic prompts
- **AI Query Service**: Part of KG→RAG→LLM pipeline
- **Supervisor**: Stores and retrieves recovery patterns

## Mock Mode Features

When ChromaDB is unavailable:
- In-memory dictionary storage
- Basic search (no vector similarity)
- Same API interface (no code changes needed)
- Warnings logged for visibility

## Search Capabilities

- **Semantic Search**: Finds conceptually similar content
- **Keyword Matching**: Falls back to keyword search if needed
- **Filtered Search**: By artifact type
- **Ranked Results**: Ordered by relevance
- **Metadata Enrichment**: Returns context with results
