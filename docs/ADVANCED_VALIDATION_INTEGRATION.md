# Advanced Validation Integration

## Overview

Artemis now includes **advanced validation** features as part of Phase 1 anti-hallucination strategy:
- **Static Analysis**: Type checking (mypy), linting (ruff), complexity analysis (radon)
- **Property-Based Testing**: Auto-generate hypothesis tests from code invariants

These features are integrated into the code review pipeline and help catch:
- Type errors before execution
- Code style issues and anti-patterns
- Overly complex code (hallucination indicator)
- Missing test coverage for code properties

## What's Included

### 1. Static Analysis Validator

**Location:** `src/validation/static_analysis_validator.py`

Runs multiple static analysis tools on generated code:

- **mypy** - Strict type checking with error codes
- **ruff** - Fast Python linter (replaces pylint/flake8)
- **radon** - Cyclomatic complexity analyzer

**Key Features:**
- ✅ Guard clauses throughout (no nested ifs)
- ✅ Configurable tool selection
- ✅ Configurable complexity threshold
- ✅ Aggregated results with severity levels
- ✅ Graceful handling of missing tools

**Usage:**
```python
from validation import StaticAnalysisValidator

validator = StaticAnalysisValidator(
    enable_type_checking=True,
    enable_linting=True,
    enable_complexity_check=True,
    max_complexity=10,
    logger=logger
)

result = validator.validate_code(
    code=python_code,
    language="python",
    file_name="module.py"
)

# Check results
print(f"Passed: {result.passed}")
print(f"Errors: {result.error_count}")
print(f"Warnings: {result.warning_count}")
print(f"Summary: {result.summary}")

for issue in result.issues:
    print(f"  {issue.file}:{issue.line} - {issue.message}")
```

### 2. Property-Based Test Generator

**Location:** `src/validation/property_based_test_generator.py`

Automatically generates property-based tests using hypothesis patterns:

**Extracts properties from:**
1. **Type hints**: `def add(x: int, y: int) -> int` → generates int type checks
2. **Docstrings**: "Returns non-negative" → generates `assert result >= 0`
3. **Return patterns**: `return max(values)` → generates bounded checks

**Supported Patterns:**
- Non-negative returns
- Positive returns
- Sorted returns
- Size-preserving operations
- Idempotent operations
- Min/max bounds

**Usage:**
```python
from validation import PropertyBasedTestGenerator

generator = PropertyBasedTestGenerator(logger=logger)

code = """
def calculate_square(n: int) -> int:
    '''Returns the square of a number. Returns non-negative integer.'''
    return n * n
"""

test_suites = generator.generate_tests(code)

for suite in test_suites:
    print(f"Function: {suite.function_name}")
    print(f"Properties: {len(suite.properties)}")
    print(f"Test code:\n{suite.test_code}")
```

### 3. Advanced Validation Reviewer

**Location:** `src/stages/code_review_stage/advanced_validation_reviewer.py`

Facade that orchestrates both static analysis and property-based testing:

**Features:**
- ✅ Runs both validation techniques
- ✅ Aggregates results
- ✅ Formats markdown reports
- ✅ Configurable enable/disable

**Usage:**
```python
from advanced_validation_reviewer import AdvancedValidationReviewer

reviewer = AdvancedValidationReviewer(
    logger=logger,
    enable_static_analysis=True,
    enable_property_tests=True,
    static_analysis_config={
        'max_complexity': 10
    }
)

result = reviewer.review_code(
    code=code,
    developer_name="developer-a",
    language="python"
)

# Format report
report = reviewer.format_report(result)
print(report)
```

## Code Review Pipeline Integration

### Location

**File:** `src/stages/code_review_stage/review_coordinator.py`

**Integration Point:** `_review_single_developer()` method

### What Happens

When a code review runs, the coordinator now:

1. **Reviews code** (existing behavior)
2. **Validates code standards** (nested ifs, elif chains, TODOs)
3. **✨ NEW: Advanced validation**
   - Finds all Python files in implementation directory
   - Runs static analysis on each file
   - Generates property-based tests
   - Aggregates results
4. **Reports findings**

### Review Result Structure

```python
{
    "developer": "developer-a",
    "review_status": "PASS",
    "overall_score": 85,

    # Existing
    "code_standards": {...},

    # NEW: Advanced validation
    "advanced_validation": {
        "enabled": True,
        "files_validated": 5,
        "files_passed": 4,
        "overall_passed": False,
        "static_analysis_errors": 2,
        "static_analysis_warnings": 3,
        "total_issues": 5,
        "summary": "❌ Advanced validation: 2 error(s), 3 warning(s) across 5 file(s)",
        "results": [
            {
                "file_name": "module.py",
                "file_path": "src/module.py",
                "developer": "developer-a",
                "overall_passed": False,
                "static_analysis": {
                    "enabled": True,
                    "passed": False,
                    "error_count": 2,
                    "warning_count": 1,
                    "issues": [...]
                },
                "property_tests": {
                    "enabled": True,
                    "test_suites": [...],
                    "summary": "Generated 3 property tests"
                },
                "issues_found": [...],
                "suggestions": [...]
            }
        ]
    }
}
```

## Configuration

### Environment Variables

Control advanced validation behavior via environment variables:

```bash
# Enable/disable advanced validation entirely
export ARTEMIS_ADVANCED_VALIDATION_ENABLED=true

# Enable/disable specific components
export ARTEMIS_STATIC_ANALYSIS_ENABLED=true
export ARTEMIS_PROPERTY_TESTS_ENABLED=true

# Configure complexity threshold
export ARTEMIS_MAX_COMPLEXITY=15
```

### Code Configuration

When creating `MultiDeveloperReviewCoordinator`:

```python
coordinator = MultiDeveloperReviewCoordinator(
    logger=logger,
    llm_provider="anthropic",
    llm_model="claude-sonnet-4",
    rag_agent=rag_agent,
    code_review_dir="/path/to/reviews",

    # Advanced validation configuration
    enable_advanced_validation=True,  # Master switch
    enable_static_analysis=True,      # Run mypy/ruff/radon
    enable_property_tests=True,       # Generate hypothesis tests
    max_complexity=10                 # Complexity threshold
)
```

## Coding Standards Compliance

All new code follows claude.md standards:

✅ **No nested if statements** - All code uses guard clauses
✅ **No elif chains** - Uses dispatch tables instead
✅ **Guard clause pattern** - Early returns for edge cases
✅ **Single responsibility** - Each function has one job
✅ **Helper method extraction** - Complex logic broken down

**Verification:**
```bash
python3 -c "
from coding_standards.validation import CodeStandardsValidator

validator = CodeStandardsValidator()
result = validator.validate_code_standards(
    code_dir='src/validation',
    severity_threshold='warning'
)

print(f'Files scanned: {result.files_scanned}')
print(f'Valid: {result.is_valid}')
print(f'Violations: {result.violation_count}')
"
```

**Result:** ✅ 0 violations - All code meets standards!

## Testing

### Test Suite

**Location:** `src/test_anti_hallucination_integration.py`

**Tests:**
1. Static analysis validator functionality
2. Property-based test generator functionality
3. Advanced validation reviewer facade
4. Code review integration structure
5. Environment variable configuration
6. Guard clause compliance

**Run Tests:**
```bash
python3 test_anti_hallucination_integration.py
```

**Expected Output:**
```
======================================================================
✅ ALL TESTS PASSED
======================================================================

Anti-hallucination features are ready:
  ✓ Static analysis validator works
  ✓ Property-based test generator works
  ✓ Advanced validation reviewer works
  ✓ Code review integration works
  ✓ Environment variables work
  ✓ Code follows guard clause pattern
```

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  MultiDeveloperReviewCoordinator            │
│                                                               │
│  _review_single_developer()                                 │
│    │                                                          │
│    ├─> CodeReviewAgent (existing)                           │
│    ├─> CodeStandardsReviewer (existing)                     │
│    └─> AdvancedValidationReviewer (NEW)                     │
│           │                                                   │
│           ├─> StaticAnalysisValidator                       │
│           │      ├─> mypy (type checking)                    │
│           │      ├─> ruff (linting)                          │
│           │      └─> radon (complexity)                      │
│           │                                                   │
│           └─> PropertyBasedTestGenerator                    │
│                  ├─> Type hint analysis                      │
│                  ├─> Docstring pattern extraction            │
│                  └─> Return statement analysis               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Developer Implementation
         │
         ▼
Find Python Files
         │
         ▼
For Each File:
         │
         ├─> Read Code
         │       │
         │       ▼
         │   Advanced Validation Reviewer
         │       │
         │       ├─> Static Analysis
         │       │      ├─> mypy
         │       │      ├─> ruff
         │       │      └─> radon
         │       │           │
         │       │           ▼
         │       │   StaticAnalysisResult
         │       │
         │       └─> Property Test Generation
         │              ├─> Parse AST
         │              ├─> Extract properties
         │              └─> Generate tests
         │                      │
         │                      ▼
         │              PropertyTestSuites
         │
         ▼
Aggregate Results
         │
         ▼
Review Result with
Advanced Validation
```

## Anti-Hallucination Impact

### How It Reduces Hallucinations

1. **Type Checking (mypy)**
   - Catches type inconsistencies
   - Prevents type-based bugs
   - Validates function signatures

2. **Linting (ruff)**
   - Detects common anti-patterns
   - Enforces code style
   - Finds potential bugs

3. **Complexity Analysis (radon)**
   - Flags overly complex code
   - High complexity often indicates hallucination
   - Encourages simpler, clearer code

4. **Property-Based Testing**
   - Tests invariants that ALWAYS hold
   - Finds edge cases regular tests miss
   - Validates mathematical properties

### Integration with Existing Anti-Hallucination

This is **Phase 1** of the anti-hallucination strategy. It complements:

- ✅ Thermodynamic Computing (Bayesian/Monte Carlo confidence)
- ✅ Two-Pass Pipeline (independent attempts + comparison)
- ✅ RAG Validation (grounding in proven code)
- ✅ Self-Consistency (multiple sampling + voting)
- ✅ Chain-of-Thought (step-by-step reasoning)
- ✅ Self-Critique (LLM critiques itself)
- ✅ Dynamic Pipeline (adaptive validation)
- ✅ Code Standards (nested ifs, elif chains, TODOs)

## File Structure

```
src/
├── validation/
│   ├── __init__.py                         # Exports all validation components
│   ├── static_analysis_validator.py        # Static analysis orchestrator
│   ├── property_based_test_generator.py    # Property test generator
│   └── ... (other validation components)
│
├── stages/code_review_stage/
│   ├── review_coordinator.py               # Code review orchestration (MODIFIED)
│   ├── advanced_validation_reviewer.py     # Advanced validation facade (NEW)
│   ├── code_standards_reviewer.py          # Code standards adapter
│   └── ... (other code review components)
│
└── test_anti_hallucination_integration.py  # Integration tests
```

## Next Steps

### Phase 2 (Planned)

- Contract-Based Programming (pre/post conditions)
- Adversarial Testing (edge case generation)
- Cross-Model Validation (multiple LLMs agree)

### Phase 3 (Planned)

- Symbolic Execution (prove correctness mathematically)
- Formal Specification Matching (verify against specs)
- Differential Testing (compare to reference implementation)

## Troubleshooting

### Tools Not Installed

If mypy, ruff, or radon are not installed:

```bash
pip install mypy ruff radon
```

**Graceful Degradation:** If tools are missing, validation continues but logs warnings.

### High Number of Warnings

Adjust the complexity threshold:

```bash
export ARTEMIS_MAX_COMPLEXITY=15
```

Or configure in code:
```python
max_complexity=15
```

### Disable Advanced Validation

To disable entirely:

```bash
export ARTEMIS_ADVANCED_VALIDATION_ENABLED=false
```

To disable specific components:

```bash
export ARTEMIS_STATIC_ANALYSIS_ENABLED=false
export ARTEMIS_PROPERTY_TESTS_ENABLED=false
```

## Performance Considerations

- **File Size Limit**: Files > 50KB are skipped (configurable in code)
- **Tool Timeouts**: Each tool has 10-second timeout
- **Parallel Execution**: Files validated sequentially (could be parallelized)

## References

- **Anti-Hallucination Strategy**: `ANTI_HALLUCINATION_STRATEGY.md`
- **Code Standards**: `claude.md` (coding standards)
- **Static Analysis**: mypy, ruff, radon documentation
- **Property-Based Testing**: hypothesis documentation

## Support

For issues or questions:
- Check test suite: `python3 test_anti_hallucination_integration.py`
- Verify code standards: Run code standards validator
- Review logs: Advanced validation logs to console

## Summary

✅ **Static Analysis Validator** - Catches type errors, style issues, complexity
✅ **Property-Based Test Generator** - Auto-generates hypothesis tests
✅ **Advanced Validation Reviewer** - Orchestrates both techniques
✅ **Code Review Integration** - Integrated into pipeline
✅ **Coding Standards Compliant** - All code follows claude.md
✅ **Fully Tested** - 6/6 integration tests pass
✅ **Configurable** - Environment variables and code configuration
✅ **Documented** - Comprehensive documentation

**The anti-hallucination Phase 1 features are ready for production use!**
