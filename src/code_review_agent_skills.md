# Code Review Agent - Skills

## Agent Overview
**File**: `code_review_agent.py`
**Purpose**: Automated code review for quality, security, compliance, and accessibility
**Single Responsibility**: Comprehensive code analysis using LLM intelligence

## Core Skills

### 1. Security Analysis (OWASP Top 10)
- **Injection Vulnerabilities**: SQL, NoSQL, Command injection
- **Broken Authentication**: Weak password policies, session management
- **Sensitive Data Exposure**: Hardcoded secrets, unencrypted data
- **XML External Entities (XXE)**: XML parsing vulnerabilities
- **Broken Access Control**: Authorization flaws
- **Security Misconfiguration**: Default credentials, verbose errors
- **Cross-Site Scripting (XSS)**: Reflected, stored, DOM-based
- **Insecure Deserialization**: Pickle, YAML deserialization
- **Using Components with Known Vulnerabilities**: Outdated dependencies
- **Insufficient Logging & Monitoring**: Audit trail gaps

### 2. Code Quality Analysis
- **Anti-Patterns**: Detection and suggested fixes
- **Code Smells**: Long methods, duplicate code, complex conditionals
- **Best Practices**: PEP 8, Pythonic idioms
- **Maintainability**: Cyclomatic complexity, coupling metrics
- **Performance**: Inefficient algorithms, unnecessary loops
- **Error Handling**: Try/except best practices, exception types

### 3. GDPR Compliance Checking
- **Personal Data Handling**: PII identification and protection
- **Data Minimization**: Excessive data collection detection
- **Purpose Limitation**: Data used only for stated purpose
- **Consent Management**: Explicit consent mechanisms
- **Data Retention**: Automatic deletion policies
- **Right to Access**: Data export capabilities
- **Right to Erasure**: Data deletion mechanisms
- **Data Portability**: Standard format exports
- **Privacy by Design**: Default privacy settings

### 4. Accessibility Analysis (WCAG 2.1 AA)
- **Perceivable**: Alt text, captions, color contrast
- **Operable**: Keyboard navigation, focus management
- **Understandable**: Clear labels, error messages, instructions
- **Robust**: Semantic HTML, ARIA attributes, screen reader compatibility
- **Focus Indicators**: Visible focus states
- **Skip Links**: Navigation shortcuts
- **Heading Hierarchy**: Proper semantic structure
- **Form Validation**: Accessible error messages

### 5. RAG-Enhanced Review
- **Historical Pattern Analysis**: Learns from past reviews
- **Best Practice Retrieval**: Queries coding standards from RAG
- **Similar Code Comparison**: Finds related implementations
- **Automated Fix Suggestions**: Based on proven solutions

### 6. AI Query Service Integration
- **Knowledge Graph Queries**: Architectural patterns
- **Semantic Search**: Related security issues
- **Context-Aware Analysis**: Project-specific standards
- **Multi-Layer Analysis**: KG → RAG → LLM pipeline

## Review Output Structure

```json
{
  "overall_quality": "PASS|FAIL|NEEDS_IMPROVEMENT",
  "security_issues": [...],
  "quality_issues": [...],
  "gdpr_issues": [...],
  "accessibility_issues": [...],
  "recommendations": [...],
  "severity_summary": {
    "critical": 0,
    "high": 2,
    "medium": 5,
    "low": 3
  }
}
```

## Configuration

**Environment Variables**:
- `ARTEMIS_LLM_PROVIDER`: LLM provider (openai/anthropic)
- `ARTEMIS_LLM_MODEL`: Specific model to use

## Dependencies

- `llm_client`: LLM API communication
- `review_request_builder`: Structures review requests
- `prompt_manager`: RAG-based review prompts
- `ai_query_service`: KG→RAG→LLM pipeline

## Usage Patterns

```python
reviewer = CodeReviewAgent(
    developer_name="developer-a",
    llm_provider="openai",
    logger=logger,
    rag_agent=rag,
    ai_service=ai_service
)

review_result = reviewer.review_implementation(
    implementation_dir=Path("./output/task-123"),
    task_title="User Authentication System",
    task_description="JWT-based auth with role-based access"
)
```

## Design Patterns

- **Builder Pattern**: ReviewRequestBuilder for complex requests
- **Strategy Pattern**: Different analysis strategies per dimension
- **Template Method**: Standard review workflow
- **Facade Pattern**: Unified review interface

## Performance Optimizations

- Parallel file analysis where possible
- Cached security patterns (compiled regex)
- Batched LLM requests
- Early termination on critical issues

## Integration Points

- **Development Stage**: Pre-commit review feedback
- **Refactor Stage**: Quality improvement suggestions
- **Validation Stage**: Final approval gate
- **RAG Agent**: Historical pattern storage

## Review Dimensions

1. **Security**: OWASP compliance
2. **Quality**: Code smells, anti-patterns
3. **GDPR**: Privacy and data protection
4. **Accessibility**: WCAG 2.1 AA compliance
5. **Performance**: Algorithm efficiency
6. **Maintainability**: Long-term code health
7. **Testing**: Test coverage and quality
8. **Documentation**: Code and API documentation
