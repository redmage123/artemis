# Artemis Exception Hierarchy

## Visual Exception Tree

```
ArtemisException (base.py)
│
├── RAGException (database.py)
│   ├── RAGQueryError
│   ├── RAGStorageError
│   └── RAGConnectionError
│
├── RedisException (database.py)
│   ├── RedisConnectionError
│   └── RedisCacheError
│
├── KnowledgeGraphError (database.py)
│   ├── KGQueryError
│   └── KGConnectionError
│
├── LLMException (llm.py)
│   ├── LLMClientError
│   ├── LLMAPIError
│   ├── LLMResponseParsingError
│   ├── LLMRateLimitError [RETRYABLE]
│   └── LLMAuthenticationError [PERMANENT FAILURE]
│
├── DeveloperException (agents.py)
│   ├── DeveloperExecutionError
│   ├── DeveloperPromptError
│   └── DeveloperOutputError
│
├── CodeReviewException (agents.py)
│   ├── CodeReviewExecutionError
│   ├── CodeReviewScoringError
│   └── CodeReviewFeedbackError
│
├── RequirementsException (parsing.py)
│   ├── RequirementsFileError
│   ├── RequirementsParsingError
│   ├── RequirementsValidationError
│   ├── RequirementsExportError
│   ├── UnsupportedDocumentFormatError
│   └── DocumentReadError
│
├── PipelineException (pipeline.py)
│   ├── PipelineStageError
│   ├── PipelineValidationError
│   └── PipelineConfigurationError
│
├── ConfigurationError (pipeline.py)
│
├── KanbanException (workflow.py)
│   ├── KanbanCardNotFoundError
│   ├── KanbanBoardError
│   └── KanbanWIPLimitError
│
├── SprintException (workflow.py)
│   ├── SprintPlanningError
│   ├── FeatureExtractionError
│   ├── PlanningPokerError
│   ├── SprintAllocationError
│   ├── ProjectReviewError
│   ├── RetrospectiveError
│   └── UIUXEvaluationError
│       ├── WCAGEvaluationError
│       └── GDPREvaluationError
│
├── ArtemisFileError (filesystem.py)
│   ├── FileNotFoundError
│   ├── FileReadError
│   └── FileWriteError
│
└── ProjectAnalysisException (analysis.py)
    ├── ADRGenerationError
    └── DependencyAnalysisError
```

## Module Distribution

| Module | Exception Count | Category |
|--------|----------------|----------|
| base.py | 1 | Base class |
| database.py | 10 | RAG (4), Redis (3), Knowledge Graph (3) |
| llm.py | 6 | LLM/API operations |
| agents.py | 8 | Developer (4), Code Review (4) |
| parsing.py | 7 | Requirements and documents |
| pipeline.py | 5 | Pipeline orchestration + config |
| workflow.py | 13 | Kanban (4), Sprint (9, including UI/UX) |
| filesystem.py | 4 | File I/O operations |
| analysis.py | 3 | Project analysis |
| **Total** | **57** | **All exception types** |

## Exception Categories

### Retryable Exceptions (Transient Failures)
- `LLMRateLimitError` - Retry with exponential backoff
- `RAGConnectionError` - Retry with connection pool
- `RedisConnectionError` - Retry with fallback
- `KGConnectionError` - Retry with timeout

### Permanent Failures (Do Not Retry)
- `LLMAuthenticationError` - Invalid API key, fail fast
- `UnsupportedDocumentFormatError` - Format not supported
- `PipelineConfigurationError` - Missing configuration
- `KanbanCardNotFoundError` - Card doesn't exist

### Validation Errors (Fail Fast)
- `PipelineValidationError` - Prerequisites not met
- `RequirementsValidationError` - Invalid requirements
- `KanbanWIPLimitError` - WIP limit exceeded
- `ConfigurationError` - Configuration validation failed

### Operational Errors (May Recover)
- `RAGQueryError` - Query might succeed with different params
- `DeveloperExecutionError` - Agent might succeed on retry
- `FileReadError` - File might become readable
- `CodeReviewScoringError` - Score calculation might succeed with different metrics

## Import Reference

### Import All Exceptions (Old Style - Still Supported)
```python
from core.exceptions import (
    ArtemisException,
    RAGException, RAGQueryError, RAGStorageError, RAGConnectionError,
    RedisException, RedisConnectionError, RedisCacheError,
    LLMException, LLMAPIError, LLMRateLimitError, LLMAuthenticationError,
    DeveloperException, DeveloperExecutionError,
    CodeReviewException, CodeReviewExecutionError,
    RequirementsException, RequirementsParsingError,
    PipelineException, PipelineStageError,
    KanbanException, KanbanCardNotFoundError,
    SprintException, SprintPlanningError,
    ArtemisFileError, FileNotFoundError,
    ProjectAnalysisException, ADRGenerationError
)
```

### Import by Category (New Style - Recommended)
```python
# Database exceptions
from core.exceptions.database import RAGException, RAGQueryError

# LLM exceptions
from core.exceptions.llm import LLMException, LLMRateLimitError

# Agent exceptions
from core.exceptions.agents import DeveloperException, CodeReviewException

# Parsing exceptions
from core.exceptions.parsing import RequirementsException

# Pipeline exceptions
from core.exceptions.pipeline import PipelineException, PipelineStageError

# Workflow exceptions
from core.exceptions.workflow import KanbanException, SprintException

# Filesystem exceptions
from core.exceptions.filesystem import ArtemisFileError, FileNotFoundError

# Analysis exceptions
from core.exceptions.analysis import ProjectAnalysisException

# Utilities
from core.exceptions.utilities import wrap_exception, create_wrapped_exception
```

## Usage Patterns

### Catching by Category
```python
# Catch all database errors
try:
    rag_operation()
except RAGException as e:
    handle_database_error(e)

# Catch all LLM errors
try:
    llm_call()
except LLMException as e:
    handle_llm_error(e)

# Catch all Artemis errors
try:
    any_artemis_operation()
except ArtemisException as e:
    handle_artemis_error(e)
```

### Catching Specific Types
```python
# Handle specific LLM errors differently
try:
    llm_call()
except LLMRateLimitError as e:
    retry_with_backoff(e)  # Retryable
except LLMAuthenticationError as e:
    fail_fast(e)  # Permanent failure
except LLMException as e:
    log_and_continue(e)  # Other LLM errors
```

### Using Context
```python
# Raise with context
raise RAGQueryError(
    "Failed to query RAG database",
    context={
        "query": search_term,
        "collection": "code_examples",
        "limit": 10,
        "attempt": 3
    }
)

# Access context in handler
try:
    query_rag()
except RAGQueryError as e:
    query = e.context.get("query")
    collection = e.context.get("collection")
    log.error(f"RAG query failed: {query} in {collection}")
```

### Using Decorator
```python
from core.exceptions.utilities import wrap_exception
from core.exceptions.pipeline import PipelineStageError

# Automatically wrap all exceptions
@wrap_exception(PipelineStageError, "Stage execution failed")
def execute_stage(card, context):
    # Any exception here becomes PipelineStageError
    llm_call()
    file_operation()
    return result
```

## Exception Naming Conventions

| Pattern | Example | Usage |
|---------|---------|-------|
| `*Exception` | `RAGException` | Base category exception |
| `*Error` | `RAGQueryError` | Specific error type |
| `*ConnectionError` | `RAGConnectionError` | Connection failures |
| `*ValidationError` | `PipelineValidationError` | Validation failures |
| `*ExecutionError` | `DeveloperExecutionError` | Execution failures |

## Aliases for Compatibility

```python
RAGError = RAGException  # AIQueryService compatibility
LLMError = LLMException  # AIQueryService compatibility
```

---

**Generated:** 2025-10-28
**Total Exception Types:** 57
**Total Modules:** 10 (+ 1 facade)
**Documentation Standard:** claude.md compliant
