# Code Refactoring Agent - Quick Start Guide

## Overview

The Code Refactoring Agent analyzes Python source code to detect anti-patterns and suggest Pythonic improvements. It has been refactored from a monolithic 532-line file into a modular package with focused, single-responsibility components.

## Installation

No installation required - the package is part of the Artemis codebase.

## Basic Usage

### Option 1: Backward Compatible (Recommended for existing code)

```python
from code_refactoring_agent import create_refactoring_agent
from pathlib import Path

# Create agent
agent = create_refactoring_agent(verbose=True)

# Analyze a file
analysis = agent.analyze_file_for_refactoring(Path("my_module.py"))

# Generate instructions
instructions = agent.generate_refactoring_instructions(analysis)
print(instructions)
```

### Option 2: New Package Import (Recommended for new code)

```python
from agents.refactoring import create_refactoring_agent
from pathlib import Path

# Create agent
agent = create_refactoring_agent(verbose=True)

# Analyze a file
analysis = agent.analyze_file_for_refactoring(Path("my_module.py"))

# Generate instructions
instructions = agent.generate_refactoring_instructions(analysis)
print(instructions)
```

## Advanced Usage

### Using Components Independently

```python
from agents.refactoring.analyzer import CodeSmellAnalyzer
from agents.refactoring.suggestion_generator import RefactoringSuggestionGenerator
from agents.refactoring.models import PatternType
from pathlib import Path

# Create analyzer
analyzer = CodeSmellAnalyzer(verbose=False)

# Analyze file
analysis = analyzer.analyze_file(Path("my_module.py"))

# Access results
print(f"Total issues: {analysis.total_issues}")
print(f"Long methods: {len(analysis.long_methods)}")

# Filter by pattern type
for smell in analysis.all_smells:
    if smell.pattern_type == PatternType.LONG_METHOD:
        print(f"Long method at line {smell.line_number}: {smell.suggestion}")

# Generate custom instructions
generator = RefactoringSuggestionGenerator()
instructions = generator.generate_instructions(analysis)
```

### Merging Code Review Feedback

```python
from agents.refactoring import create_refactoring_agent
from pathlib import Path

agent = create_refactoring_agent()
analysis = agent.analyze_file_for_refactoring(Path("my_module.py"))

# Code review issues from another source
code_review_issues = [
    {
        'severity': 'HIGH',
        'category': 'Security',
        'description': 'SQL injection vulnerability on line 42'
    },
    {
        'severity': 'MEDIUM',
        'category': 'Performance',
        'description': 'Inefficient database query on line 67'
    }
]

# Generate combined instructions
instructions = agent.generate_refactoring_instructions(
    analysis,
    code_review_issues=code_review_issues
)
```

### Batch Analysis

```python
from agents.refactoring import create_refactoring_agent
from pathlib import Path

agent = create_refactoring_agent(verbose=False)

# Analyze multiple files
files = Path("src").glob("**/*.py")
results = []

for file_path in files:
    analysis = agent.analyze_file_for_refactoring(file_path)
    if analysis['total_issues'] > 0:
        results.append(analysis)

# Sort by issue count
results.sort(key=lambda x: x['total_issues'], reverse=True)

# Print top offenders
print("Top 10 files needing refactoring:")
for analysis in results[:10]:
    print(f"{analysis['file']}: {analysis['total_issues']} issues")
```

## What It Detects

### 1. Long Methods (>50 lines)
**Why:** Violates Single Responsibility Principle, hard to test and understand

**Example:**
```python
def process_user_data(user):  # Line 1
    # ... 60 lines of code ...
    pass  # Line 61

# Suggestion: Extract helper methods from process_user_data (61 lines)
```

### 2. Simple Loops → Comprehensions
**Why:** List comprehensions are more readable, faster, and more Pythonic

**Example:**
```python
# Before
result = []
for item in items:
    result.append(transform(item))

# Suggestion: Convert to list comprehension
# After
result = [transform(item) for item in items]
```

### 3. If/Elif Chains → Dictionary Dispatch
**Why:** Dictionary lookup is O(1) vs O(n), more maintainable

**Example:**
```python
# Before
if status == 'pending':
    return handle_pending()
elif status == 'approved':
    return handle_approved()
elif status == 'rejected':
    return handle_rejected()
elif status == 'cancelled':
    return handle_cancelled()

# Suggestion: Convert to dictionary mapping
# After
handlers = {
    'pending': handle_pending,
    'approved': handle_approved,
    'rejected': handle_rejected,
    'cancelled': handle_cancelled
}
return handlers.get(status, handle_default)()
```

## Analysis Output Format

```python
{
    'file': '/path/to/file.py',
    'long_methods': [
        {
            'name': 'process_data',
            'line': 42,
            'length': 65,
            'suggestion': 'Extract helper methods from process_data (65 lines)'
        }
    ],
    'simple_loops': [
        {
            'line': 102,
            'suggestion': 'Convert for loop to list/set/dict comprehension'
        }
    ],
    'if_elif_chains': [
        {
            'line': 156,
            'elif_count': 4,
            'suggestion': 'Convert 5-branch if/elif to dictionary mapping'
        }
    ],
    'total_issues': 3
}
```

## Customization

### Custom Logger

```python
from agents.refactoring import create_refactoring_agent

class MyLogger:
    def log(self, message, level="INFO"):
        # Custom logging logic
        print(f"[{level}] {message}")

agent = create_refactoring_agent(logger=MyLogger(), verbose=True)
```

### Silent Mode

```python
from agents.refactoring import create_refactoring_agent

# Disable verbose output
agent = create_refactoring_agent(verbose=False)
```

## Best Practices

1. **Run regularly** - Integrate into CI/CD pipeline for continuous quality monitoring
2. **Prioritize fixes** - Address CRITICAL priority issues first
3. **Review suggestions** - Not all suggestions may apply to your context
4. **Incremental refactoring** - Fix one category at a time
5. **Test after refactoring** - Ensure behavior is preserved
6. **Document exceptions** - If you intentionally ignore a suggestion, document why

## Migration from Old API

The refactored package maintains 100% backward compatibility. You can migrate gradually:

### Step 1: Keep existing imports (works immediately)
```python
from code_refactoring_agent import create_refactoring_agent
```

### Step 2: Update imports when convenient
```python
from agents.refactoring import create_refactoring_agent
```

### Step 3: Leverage new features
```python
from agents.refactoring import (
    CodeSmellAnalyzer,
    RefactoringSuggestionGenerator,
    PatternType,
    RefactoringPriority
)
```

## Troubleshooting

### Import Error
```python
ImportError: No module named 'agents.refactoring'
```
**Solution:** Ensure you're running from the correct directory with proper Python path

### No Issues Detected
If analysis finds 0 issues:
- File may already be well-refactored
- File may be very short (<50 lines)
- File may use advanced patterns the analyzer doesn't recognize

### Syntax Error During Analysis
```python
{'file': '/path/to/file.py', 'error': 'invalid syntax...', 'total_issues': 0}
```
**Solution:** Fix Python syntax errors in the analyzed file first

## Examples

See `/home/bbrelin/src/repos/artemis/src/test_refactored_agent.py` for comprehensive examples.

## Architecture

For detailed architecture documentation, see `REFACTORING_REPORT.md`

## Support

For issues or questions:
1. Check the comprehensive report: `REFACTORING_REPORT.md`
2. Review the test suite: `test_refactored_agent.py`
3. Examine module docstrings for detailed documentation
