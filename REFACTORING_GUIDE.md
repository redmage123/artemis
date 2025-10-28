# Nested If Refactoring Guide

## Quick Reference

**Rule:** NO nested ifs. Use early returns instead.

```python
# ❌ BAD: Nested ifs
if condition1:
    if condition2:
        if condition3:
            return result

# ✅ GOOD: Early returns
if not condition1:
    return default
if not condition2:
    return default
if not condition3:
    return default
return result
```

## Pattern 1: Simple Guard Clauses

### Before
```python
def process_data(data):
    if data is not None:
        if len(data) > 0:
            if data.is_valid():
                return data.process()
    return None
```

### After
```python
def process_data(data):
    if data is None:
        return None
    if len(data) == 0:
        return None
    if not data.is_valid():
        return None

    return data.process()
```

**Transformation Steps:**
1. Invert each condition
2. Add early return with default value
3. Move final action outside all conditions

## Pattern 2: With Logging

### Before
```python
def validate(code, logger):
    if logger:
        if code:
            logger.log("Validating...")
            if is_valid(code):
                logger.log("Valid")
                return True
            else:
                logger.log("Invalid")
    return False
```

### After
```python
def validate(code, logger):
    if not logger:
        return False
    if not code:
        return False

    logger.log("Validating...")

    if not is_valid(code):
        logger.log("Invalid")
        return False

    logger.log("Valid")
    return True
```

**Key Point:** Use `logger and logger.log()` for optional logging:
```python
logger and logger.log("Message")
```

## Pattern 3: Extremely Deep Nesting (7+ levels)

### Before (from pipeline_observer.py - 11 levels!)
```python
if event_type == 'validation':
    if 'stage' in data:
        if data['stage'] == 'full_code':
            if 'passed' in data:
                if not data['passed']:
                    if 'feedback' in data:
                        if logger:
                            if self.config.get('verbose'):
                                if 'score' in data:
                                    if data['score'] < 0.5:
                                        if self.circuit_breaker:
                                            if self.circuit_breaker.should_trip():
                                                logger.log("CRITICAL")
```

### After
```python
# Early return: Not the right event type
if event_type != 'validation':
    return

# Early return: Missing required data
if 'stage' not in data:
    return
if data['stage'] != 'full_code':
    return
if 'passed' not in data:
    return

# Early return: Validation passed (no action needed)
if data['passed']:
    return

# Early return: No feedback to log
if 'feedback' not in data:
    return

# Early return: No logger available
if not logger:
    return

# Early return: Not in verbose mode
if not self.config.get('verbose'):
    return

# Early return: Score OK or missing
if 'score' not in data or data['score'] >= 0.5:
    return

# Early return: No circuit breaker
if not self.circuit_breaker:
    return

# Early return: Should not trip
if not self.circuit_breaker.should_trip():
    return

# Finally, log the critical message
logger.log("CRITICAL")
```

**Benefits:**
- Went from 11 levels → 1 level
- Each condition is crystal clear
- Easy to add/remove conditions
- Easy to understand flow

## Pattern 4: Multiple Actions in Body

### Before
```python
if has_permission:
    if has_resource:
        if is_active:
            update_database()
            send_notification()
            log_action()
            return True
return False
```

### After
```python
if not has_permission:
    return False
if not has_resource:
    return False
if not is_active:
    return False

update_database()
send_notification()
log_action()
return True
```

## Pattern 5: With Else Clauses

### Before
```python
if condition1:
    if condition2:
        return "success"
    else:
        return "failed_condition2"
else:
    return "failed_condition1"
```

### After
```python
if not condition1:
    return "failed_condition1"
if not condition2:
    return "failed_condition2"

return "success"
```

## Pattern 6: Boolean Logic Combination

### Before
```python
if user:
    if user.is_authenticated():
        if user.has_permission('admin'):
            do_admin_action()
```

### After - Option A (Early returns)
```python
if not user:
    return
if not user.is_authenticated():
    return
if not user.has_permission('admin'):
    return

do_admin_action()
```

### After - Option B (Combined condition)
```python
# Use when all conditions must be true
if user and user.is_authenticated() and user.has_permission('admin'):
    do_admin_action()
```

**When to combine:**
- All conditions are simple checks
- No actions between checks
- Related conditions (same object)

**When to use early returns:**
- Complex conditions
- Actions between checks
- Error handling needed

## Pattern 7: Try/Except with Nesting

### Before
```python
def process_file(path):
    try:
        if path:
            if os.path.exists(path):
                with open(path) as f:
                    if f.readable():
                        return f.read()
    except Exception as e:
        logger.log(str(e))
    return None
```

### After
```python
def process_file(path):
    if not path:
        return None
    if not os.path.exists(path):
        return None

    try:
        with open(path) as f:
            if not f.readable():
                return None
            return f.read()
    except Exception as e:
        logger.log(str(e))
        return None
```

## Anti-Patterns to Avoid

### ❌ Don't nest ifs inside ifs
```python
if x:
    if y:
        do_something()
```

### ❌ Don't use nested ternaries
```python
result = a if b else (c if d else e)
```

### ❌ Don't mix nested ifs with try/except
```python
try:
    if condition:
        if other_condition:
            risky_operation()
except:
    pass
```

## Checklist for Refactoring

- [ ] Read entire function to understand logic
- [ ] Identify all nested if statements (depth >= 2)
- [ ] Determine default/error return value
- [ ] Invert each condition
- [ ] Add early return for each inverted condition
- [ ] Move final action outside all conditions
- [ ] Test thoroughly
- [ ] Verify file compiles
- [ ] Run tests if available

## Tools

```bash
# Scan for violations
python3 src/code_standards_scanner.py --root src --critical-only

# Check specific file
python3 src/code_standards_scanner.py --root src | grep "your_file.py"

# Verify syntax after refactoring
python3 -m py_compile your_file.py
```

## Common Mistakes

### Mistake 1: Wrong inversion
```python
# ❌ WRONG
if condition:
    do_something()

# Becomes:
if condition:  # Forgot to invert!
    return
do_something()
```

### Mistake 2: Wrong return value
```python
# ❌ WRONG - returns True when should return False
if not has_permission:
    return True  # Should be False or None
```

### Mistake 3: Order matters
```python
# ❌ WRONG - checking details before basics
if file.is_valid():
    return None
if not file:  # This should be first!
    return None
```

**Rule:** Check in order: existence → basic properties → complex properties

## Real-World Example

From `validated_developer_mixin.py:86-99`:

### Before
```python
if self.self_critique_enabled and stage == ValidationStage.FULL_CODE:
    if logger:
        logger.log(...)

    critique_result = self.self_critique_validator.validate_code(...)

    if not critique_result.passed:
        if logger:
            logger.log(...)

        if critique_result.regeneration_needed and attempt < max_retries:
            if logger:
                logger.log(...)
            prompt += feedback
            continue
```

### After
```python
# Early return: Self-critique not applicable
should_critique = (
    self.self_critique_enabled and
    stage == ValidationStage.FULL_CODE
)
if not should_critique:
    return False, prompt

# Run critique
logger and logger.log(...)
critique_result = self.self_critique_validator.validate_code(...)

# Early return: Critique passed
if critique_result.passed:
    logger and logger.log("✅ Passed")
    return False, prompt

# Log failure
logger and logger.log("⚠️ Concerns found")

# Early return: Cannot regenerate
can_regenerate = critique_result.regeneration_needed and attempt < max_retries
if not can_regenerate:
    logger and logger.log("⚠️ Proceeding despite concerns")
    return False, prompt

# Regenerate
logger and logger.log("🔄 Regenerating...")
prompt += feedback
return True, prompt
```

## Summary

**Golden Rules:**
1. NO nested ifs (depth >= 2)
2. Use early returns
3. Invert conditions for guards
4. Check existence before properties
5. One level of indentation maximum
6. Use `logger and logger.log()` for optional logging

**Before starting:**
- Understand the full function logic
- Identify default/error values
- Plan the early return sequence

**After refactoring:**
- Verify compilation
- Run tests
- Check readability improved
