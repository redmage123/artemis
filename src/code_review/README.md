# Code Review Package

Modular code review system with security, GDPR, and accessibility analysis.

## Quick Start

```python
from code_review import CodeReviewAgent

agent = CodeReviewAgent(developer_name="dev-a")

result = agent.review_implementation(
    implementation_dir="/path/to/code",
    task_title="Feature X",
    task_description="Implement feature X",
    output_dir="/path/to/output"
)

print(f"Status: {result['review_status']}")
print(f"Score: {result['overall_score']}/100")
print(f"Issues: {result['total_issues']}")
```

## Module Overview

### agent.py (557 lines)
Main orchestrator - coordinates review workflow with AI services

### strategies.py (285 lines)
Prompt building and review strategies with KG enhancement

### response_parser.py (150 lines)
Parse LLM responses from various formats (JSON, markdown, code blocks)

### report_generator.py (308 lines)
Generate JSON and Markdown reports with detailed issue tracking

### schema_normalizer.py (172 lines)
Normalize different LLM response schemas to standard format

## Design Patterns

- **Strategy Pattern**: AI service vs legacy execution
- **Template Method**: Review workflow orchestration
- **Dependency Injection**: LLM, RAG, AI service configuration
- **Chain of Responsibility**: RAG→file prompt loading
- **Facade Pattern**: Clean package-level API

## Standards

- ✅ WHY/RESPONSIBILITY/PATTERNS documentation
- ✅ Guard clauses (max 1 level nesting)
- ✅ Complete type hints
- ✅ Dispatch tables over elif chains
- ✅ Single Responsibility Principle

## Import Paths

### Recommended (New)
```python
from code_review import CodeReviewAgent
from code_review.strategies import build_base_review_prompt
from code_review.response_parser import parse_review_response
from code_review.report_generator import write_review_report
from code_review.schema_normalizer import normalize_review_schema
```

### Legacy (Still Supported)
```python
from code_review_agent import CodeReviewAgent
```

## Features

- 🔒 Security analysis (OWASP Top 10)
- 🛡️ GDPR compliance checking
- ♿ Accessibility validation (WCAG 2.1 AA)
- 📊 Code quality assessment
- 🤖 AI-enhanced with Knowledge Graph
- 📝 Dual format reports (JSON + Markdown)

## Architecture

```
CodeReviewAgent (agent.py)
├── Uses: strategies.py (prompt building)
├── Uses: response_parser.py (JSON extraction)
├── Uses: report_generator.py (output formatting)
└── Uses: schema_normalizer.py (data transformation)
```

## Performance

All modules operate in **O(n)** time complexity:
- No nested loops
- Single-pass processing
- Linear scaling with input size

## Testing

```bash
# Unit tests
pytest tests/code_review/test_schema_normalizer.py
pytest tests/code_review/test_strategies.py
pytest tests/code_review/test_response_parser.py
pytest tests/code_review/test_report_generator.py

# Integration tests
pytest tests/code_review/test_agent.py
```

## Compilation Verification

```bash
python3 -m py_compile code_review/*.py
```

## Line Counts

| Module              | Lines | Purpose                    |
|---------------------|-------|----------------------------|
| agent.py            | 557   | Main orchestrator          |
| strategies.py       | 285   | Review strategies          |
| report_generator.py | 308   | Report formatting          |
| response_parser.py  | 150   | Response parsing           |
| schema_normalizer.py| 172   | Schema transformation      |
| __init__.py         | 84    | Package interface          |
| **TOTAL**           | 1,556 | Core functionality         |

## License

Part of Artemis Autonomous Development Pipeline
