# Code Standards Integration

## Overview

The code standards validator has been integrated into the Artemis Code Review Stage, providing automatic validation of generated code against `claude.md` coding standards.

## What It Validates

The code standards validator checks for:
- **Nested if statements** (maximum 1 level allowed)
- **elif chains** (should use dispatch tables instead)
- **TODO/FIXME comments** (should be resolved before production)
- Other `claude.md` code quality violations

## How It Works

### Integration Points

1. **Code Review Stage**: Automatically runs during code review for each developer's implementation
2. **Standalone Scripts**: The original standalone validation scripts remain available for manual use

### Architecture

```
CodeReviewStage
    ↓
MultiDeveloperReviewCoordinator
    ↓
    ├─→ CodeReviewAgent (security, GDPR, accessibility)
    └─→ CodeStandardsReviewer (claude.md standards) ← NEW
```

## Configuration

### Environment Variables

**Enable/Disable Code Standards Checking:**
```bash
export ARTEMIS_CODE_STANDARDS_ENABLED=true  # or false
```

**Set Severity Threshold:**
```bash
export ARTEMIS_CODE_STANDARDS_SEVERITY=warning  # or "info", "critical"
```

### Severity Levels

- **info**: Report all violations including informational ones
- **warning**: Report warnings and critical issues (default)
- **critical**: Only report critical violations

### Programmatic Configuration

When creating the Code Review Stage, you can configure code standards:

```python
from code_review_stage import CodeReviewStage

stage = CodeReviewStage(
    messenger=messenger,
    rag=rag_agent,
    logger=logger,
    # ... other parameters ...
)

# Code standards are enabled by default
# To customize, modify the MultiDeveloperReviewCoordinator initialization
```

## Review Results

Code standards results are included in the review result dictionary:

```python
review_result = {
    'developer': 'developer-a',
    'review_status': 'PASS',
    'overall_score': 85,
    # ... other review fields ...
    'code_standards': {
        'enabled': True,
        'passed': False,
        'violation_count': 3,
        'violations': [
            {
                'file': 'src/example.py',
                'line': 42,
                'severity': 'warning',
                'violation_type': 'nested_if',
                'message': 'Nested if statement detected (depth: 2)',
                'context': '    if condition1:\n        if condition2:'
            }
        ],
        'files_scanned': 5,
        'severity_threshold': 'warning',
        'summary': '❌ 3 violation(s) found'
    }
}
```

## Standalone Usage

The standalone code standards validator scripts remain available:

### Command Line

```bash
# Validate entire src directory
python3 src/code_standards_validator.py

# The pre-commit hook automatically runs validation
git commit -m "Your message"
```

### Programmatic Usage

```python
from coding_standards.validation import CodeStandardsValidator

validator = CodeStandardsValidator(verbose=True)

result = validator.validate_code_standards(
    code_dir="src",
    severity_threshold="warning"
)

if not result.is_valid:
    print(f"Found {result.violation_count} violations")
    for v in result.violations:
        print(f"  {v['file']}:{v['line']} - {v['message']}")
```

## Behavior

### Non-Blocking by Default

By default, code standards violations are **reported but do not block** code review:

- Violations are logged during code review
- They appear in the review results
- Review status is **not automatically** changed to FAIL

### Making Code Standards Blocking (Optional)

To make code standards violations block code review, uncomment this line in `review_coordinator.py`:

```python
# Adjust review status if code standards failed
if code_standards_result['enabled'] and not code_standards_result['passed']:
    self.logger.log(
        f"  ⚠️  Code standards violations detected - review may be affected",
        "WARNING"
    )
    # Optionally downgrade review status
    review_status = "FAIL"  # <--- Uncomment this line
```

## Example Output

When code standards violations are detected during code review:

```
============================================================
🔍 Reviewing developer-a implementation
============================================================
  📋 Validating code standards for developer-a...
  ❌ Code standards: 2 violation(s) found in developer-a's code
     - src/example.py:15 [warning] Nested if statement detected (depth: 2)
     - src/example.py:42 [warning] TODO comment found - resolve before production
  ⚠️  Code standards violations detected - review may be affected

Review Status: PASS
Overall Score: 85/100
Critical Issues: 0
High Issues: 1
```

## Files Modified/Created

### New Files

- `src/stages/code_review_stage/code_standards_reviewer.py` - Pipeline adapter for code standards validator

### Modified Files

- `src/stages/code_review_stage/review_coordinator.py` - Integrated code standards validation

### Unchanged (Backward Compatible)

- `src/code_standards_validator.py` - Standalone wrapper (still works)
- `src/coding_standards/validation/validator.py` - Core validator (still works)
- All existing code standards scanning components

## Disabling Code Standards Validation

If you want to disable code standards validation:

```bash
# Disable via environment variable
export ARTEMIS_CODE_STANDARDS_ENABLED=false

# Or modify the coordinator initialization
coordinator = MultiDeveloperReviewCoordinator(
    # ... other params ...
    enable_code_standards=False
)
```

## Migration Path

No migration required! The integration:
- ✅ Maintains all existing standalone scripts
- ✅ Adds pipeline integration without breaking changes
- ✅ Enabled by default but configurable
- ✅ Non-blocking by default (reports only)

## Benefits

1. **Automatic Code Quality**: Every developer implementation is automatically checked
2. **Early Detection**: Find code standards issues during code review, not after deployment
3. **Consistent Standards**: Enforce `claude.md` standards across all generated code
4. **Flexible Configuration**: Enable/disable and configure severity thresholds
5. **Non-Intrusive**: Existing workflows remain unchanged
6. **Backward Compatible**: Standalone scripts still work as before

## Next Steps

1. **Review the integration** - The code standards validator is now part of your code review workflow
2. **Configure as needed** - Set environment variables for your preferences
3. **Monitor results** - Watch for code standards violations in review output
4. **Decide on blocking** - Choose whether violations should fail code review
5. **Keep standalone scripts** - Use `code_standards_validator.py` for manual checks

## Support

For issues or questions:
- Check the code at `src/stages/code_review_stage/code_standards_reviewer.py`
- Review configuration in `src/stages/code_review_stage/review_coordinator.py`
- Run standalone validator: `python3 src/code_standards_validator.py`
