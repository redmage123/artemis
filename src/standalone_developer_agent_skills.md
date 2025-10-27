# Standalone Developer Agent - Skills

## Agent Overview
**File**: `standalone_developer_agent.py`
**Purpose**: Autonomous code generation using LLM APIs (OpenAI/Anthropic)
**Single Responsibility**: Execute TDD workflow with intelligent code generation

## Core Skills

### 1. Test-Driven Development (TDD) Workflow
- **RED Phase**: Generate failing tests from requirements
- **GREEN Phase**: Implement minimum code to pass tests
- **REFACTOR Phase**: Improve code quality while keeping tests green

### 2. Code Generation with Hallucination Reduction
- **Layer 3.6**: Streaming validation during generation
- **Layer 4**: Automated retry with prompt refinement
- **Circuit Breaker**: Prevents infinite retry loops (3 failure threshold)
- **Confidence Scoring**: Aggregates validation signals (acceptance threshold: 0.85)

### 3. Multi-Workflow Support
- **TDD Workflow**: For production code (tests-first approach)
- **Quality-Driven Workflow**: For notebooks/demos (comprehensive output)
- **Visual Test Workflow**: For UI components (visual regression + WCAG)
- **Content Validation**: For documentation (structure validation)

### 4. Knowledge Graph Integration
- Queries similar implementations from KG
- Applies proven code patterns
- Learns from historical solutions

### 5. RAG-Enhanced Generation
- Retrieves relevant code examples
- Uses notebook templates for consistency
- Queries best practices from RAG database

### 6. Automated Refactoring
- Integrates with CodeRefactoringAgent
- Applies anti-pattern detection
- Suggests Pythonic improvements

### 7. Jupyter Notebook Generation
- Professional structure (Executive Summary, Analysis, Visualizations)
- Plotly interactive charts
- MANDATORY styling requirements enforcement

## Key Features

- **LLM Provider Flexibility**: Supports OpenAI and Anthropic
- **Streaming Validation**: Real-time code validation during generation
- **Intelligent Retry**: Automatic prompt refinement on validation failure
- **Test Automation**: Universal test runner (pytest, unittest, gtest, junit)
- **File Management**: Handles Python, Jupyter notebooks, and multi-language projects

## Dependencies

- `llm_client`: LLM API communication
- `retry_coordinator`: Layer 4 intelligent retry
- `streaming_validator`: Real-time validation
- `ai_query_service`: Knowledge Graph queries
- `prompt_manager`: RAG-based prompts
- `code_refactoring_agent`: Automated refactoring

## Configuration

**Environment Variables**:
- `ARTEMIS_MAX_VALIDATION_RETRIES` (default: 3)
- `ARTEMIS_CONFIDENCE_THRESHOLD` (default: 0.85)
- `ARTEMIS_ENABLE_STREAMING_VALIDATION` (default: false)

## Usage Patterns

```python
developer = StandaloneDeveloperAgent(
    developer_name="developer-a",
    developer_type="conservative",  # or "aggressive"
    llm_provider="openai",
    logger=logger,
    rag_agent=rag
)

result = developer.execute(
    task_title="Build User Auth System",
    task_description="Implement JWT authentication...",
    adr_content=adr,
    output_dir=Path("./output"),
    developer_prompt_file="prompts/developer.txt"
)
```

## Design Patterns

- **Strategy Pattern**: Multiple workflow strategies (TDD, Quality-Driven, etc.)
- **Template Pattern**: Structured generation phases (RED→GREEN→REFACTOR)
- **Observer Pattern**: Progress tracking and logging
- **Dependency Injection**: Pluggable components (RAG, AI Service, etc.)

## Performance Optimizations

- Early termination on success
- Circuit breaker prevents wasteful retries
- Parallel tool calls where possible
- Compiled regex patterns for validation
