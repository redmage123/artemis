# Code Refactoring Agent - Skills

## Agent Overview
**File**: `code_refactoring_agent.py`
**Purpose**: Automated code quality improvements through refactoring detection
**Single Responsibility**: Analyze code and identify refactoring opportunities

## Core Skills

### 1. Anti-Pattern Detection
- **Simple Loops**: Detect loops convertible to comprehensions
- **If/Elif Chains**: Identify chains convertible to dictionary mapping
- **Long Methods**: Find methods exceeding complexity thresholds
- **Code Duplication**: Detect repeated code blocks
- **Magic Numbers**: Find hardcoded values needing constants

### 2. AST-Based Analysis
- **Python AST Traversal**: Analyzes code structure without execution
- **Visitor Pattern**: Walks abstract syntax tree
- **Safe Analysis**: No code execution required
- **Accurate Detection**: Structural analysis vs regex

### 3. Refactoring Strategies

#### Loop to Comprehension
**Before:**
```python
result = []
for item in items:
    result.append(item * 2)
```

**After:**
```python
result = [item * 2 for item in items]
```

#### If/Elif to Mapping
**Before:**
```python
if status == 'pending':
    return process_pending()
elif status == 'approved':
    return process_approved()
elif status == 'rejected':
    return process_rejected()
```

**After:**
```python
handlers = {
    'pending': process_pending,
    'approved': process_approved,
    'rejected': process_rejected
}
return handlers[status]()
```

#### Extract Long Method
**Detects:** Methods > 20 lines or cyclomatic complexity > 10
**Suggests:** Break into smaller, focused methods

#### Remove Duplication
**Detects:** Repeated code blocks
**Suggests:** Extract to shared function

### 4. Prioritization
- **Priority 1 (Critical)**: Security issues, major bugs
- **Priority 2 (High)**: Performance, maintainability
- **Priority 3 (Medium)**: Code style, minor improvements
- **Priority 4 (Low)**: Nice-to-have refactorings

### 5. Educational Feedback
- **Why Refactor**: Explains the problem
- **How to Refactor**: Step-by-step instructions
- **Best Practices**: Pythonic alternatives
- **Trade-offs**: Pros and cons of refactoring

## Refactoring Rules

```python
RefactoringRule(
    name="loop_to_comprehension",
    pattern_type="loop",
    description="Convert simple for loops to list/dict comprehensions",
    priority=2
)

RefactoringRule(
    name="if_elif_to_mapping",
    pattern_type="if_elif",
    description="Convert long if/elif chains to dictionary mapping",
    priority=2
)

RefactoringRule(
    name="extract_long_method",
    pattern_type="long_method",
    description="Break down methods exceeding 20 lines",
    priority=2
)

RefactoringRule(
    name="remove_duplication",
    pattern_type="duplication",
    description="Extract repeated code to shared functions",
    priority=1
)
```

## Analysis Output

```python
{
    "file_path": "src/payment.py",
    "total_issues": 5,
    "issues_by_priority": {
        "1": 1,  # Critical
        "2": 2,  # High
        "3": 1,  # Medium
        "4": 1   # Low
    },
    "refactorings": [
        {
            "rule": "if_elif_to_mapping",
            "line": 42,
            "priority": 2,
            "description": "Convert if/elif chain to dictionary",
            "current_code": "...",
            "suggested_code": "...",
            "rationale": "..."
        }
    ]
}
```

## Dependencies

- Python `ast` module for code parsing
- `re` module for pattern matching
- No external dependencies required

## Usage Patterns

```python
# Create refactoring agent
refactoring_agent = create_refactoring_agent(
    logger=logger,
    verbose=False
)

# Analyze file
analysis = refactoring_agent.analyze_file(
    file_path="src/payment_processing.py"
)

# Get refactoring suggestions
for refactoring in analysis['refactorings']:
    print(f"Line {refactoring['line']}: {refactoring['description']}")
    print(f"Priority: {refactoring['priority']}")
    print(f"Suggested: {refactoring['suggested_code']}")
```

## Design Patterns

- **Visitor Pattern**: AST traversal
- **Strategy Pattern**: Different refactoring rules
- **Value Object**: RefactoringRule dataclass
- **Factory Pattern**: create_refactoring_agent()

## Integration Points

- **Code Review Agent**: Provides refactoring suggestions
- **Standalone Developer**: Applies refactorings after GREEN phase
- **REFACTOR Phase**: Core component of TDD refactor stage
- **Quality Gates**: Enforces code quality standards

## Metrics Tracked

- **Lines of Code**: Method and file length
- **Cyclomatic Complexity**: Decision point count
- **Nesting Depth**: Indentation levels
- **Duplicate Lines**: Repeated code percentage
- **Comment Ratio**: Documentation coverage

## Performance Features

- **Single-Pass Analysis**: Analyzes file once
- **Cached Patterns**: Compiled regex for performance
- **Lazy Evaluation**: Only analyzes when requested
- **No Code Execution**: Safe for untrusted code

## Educational Value

- **Teaches Best Practices**: Explains why refactorings matter
- **Shows Alternatives**: Demonstrates Pythonic approaches
- **Context-Aware**: Explains when NOT to refactor
- **Learning Tool**: Improves developer skills over time

## Limitations

- **Python-Specific**: Currently only analyzes Python
- **False Positives**: May suggest refactorings that don't apply
- **Context-Limited**: Doesn't understand business logic
- **Manual Application**: Doesn't auto-apply refactorings

## Future Enhancements

- Multi-language support (JavaScript, Java, Go)
- Auto-apply refactorings with user approval
- Machine learning for custom pattern detection
- Integration with IDE plugins
