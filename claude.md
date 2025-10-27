# Claude Code Generation Standards for Artemis

**MANDATORY**: All code generation MUST follow these standards. No exceptions.

---

## 1. Design Patterns (REQUIRED)

### 1.1 Strategy Pattern - INSTEAD OF if/elif chains or sequential ifs

**NEVER DO THIS:**
```python
# ❌ BAD: if/elif chain
if framework == 'django':
    validator = DjangoValidator()
elif framework == 'flask':
    validator = FlaskValidator()
elif framework == 'rails':
    validator = RailsValidator()

# ❌ BAD: Sequential ifs
if 'django' in text:
    suggestions.append("Use Django ORM")
if 'flask' in text:
    suggestions.append("Use Flask patterns")
if 'rails' in text:
    suggestions.append("Use ActiveRecord")
```

**ALWAYS DO THIS:**
```python
# ✅ GOOD: Strategy pattern with dictionary mapping
VALIDATOR_STRATEGIES = {
    'django': DjangoValidator,
    'flask': FlaskValidator,
    'rails': RailsValidator
}

validator = VALIDATOR_STRATEGIES.get(framework, DefaultValidator)()

# ✅ GOOD: Dictionary mapping instead of sequential ifs
FRAMEWORK_SUGGESTIONS = {
    'django': "Use Django ORM",
    'flask': "Use Flask patterns",
    'rails': "Use ActiveRecord"
}

for framework, suggestion in FRAMEWORK_SUGGESTIONS.items():
    if framework in text:
        suggestions.append(suggestion)
```

---

### 1.2 Factory Pattern - For object creation

```python
class ValidatorFactory:
    """Factory for creating validators (avoid if/elif in client code)"""

    @staticmethod
    def create_validator(framework: str) -> Validator:
        """Create validator for framework using strategy pattern"""
        validators = {
            'django': DjangoValidator,
            'flask': FlaskValidator,
            'rails': RailsValidator
        }

        validator_class = validators.get(framework)
        if not validator_class:
            raise ValueError(f"Unknown framework: {framework}")

        return validator_class()
```

---

### 1.3 Observer Pattern - For event notifications

**REQUIRED** when multiple components need to react to events.

```python
from pipeline_observer import PipelineObservable, EventBuilder

class MyComponent:
    def __init__(self, observable: Optional[PipelineObservable] = None):
        self.observable = observable

    def do_something(self):
        # Perform action
        result = self._perform_action()

        # Notify observers (if available)
        if self.observable:
            event = EventBuilder.my_event(
                data=result,
                timestamp=datetime.now()
            )
            self.observable.notify(event)
```

---

## 2. Anti-Patterns (FORBIDDEN)

### 2.1 NO elif Chains

**NEVER:**
```python
# ❌ FORBIDDEN
if condition1:
    do_thing1()
elif condition2:
    do_thing2()
elif condition3:
    do_thing3()
elif condition4:
    do_thing4()
```

**ALWAYS:**
```python
# ✅ REQUIRED: Dictionary mapping
ACTION_MAP = {
    'condition1': do_thing1,
    'condition2': do_thing2,
    'condition3': do_thing3,
    'condition4': do_thing4
}

action = ACTION_MAP.get(condition_key)
if action:
    action()

# OR: Early returns
def handle_condition(condition):
    if condition == 'condition1':
        return do_thing1()
    if condition == 'condition2':
        return do_thing2()
    if condition == 'condition3':
        return do_thing3()
    if condition == 'condition4':
        return do_thing4()
    return default_action()
```

---

### 2.2 NO Nested For Loops or Ifs

**NEVER:**
```python
# ❌ FORBIDDEN: Nested loops
for item in items:
    for sub_item in item.sub_items:
        if sub_item.condition:
            process(sub_item)

# ❌ FORBIDDEN: Nested ifs
if condition1:
    if condition2:
        if condition3:
            do_something()
```

**ALWAYS:**
```python
# ✅ REQUIRED: Extract to helper method
def process_matching_sub_items(items):
    """
    Process sub-items that match condition.
    WHY: Avoids nested loops by extracting inner logic.
    """
    for item in items:
        matching = self._find_matching_sub_items(item)
        for sub_item in matching:
            process(sub_item)

def _find_matching_sub_items(self, item) -> List:
    """Helper method to avoid nested loop"""
    return [s for s in item.sub_items if s.condition]

# ✅ REQUIRED: Early returns instead of nested ifs
def process():
    if not condition1:
        return
    if not condition2:
        return
    if not condition3:
        return
    do_something()
```

---

### 2.3 NO Sequential Ifs - Use Strategy Pattern

**NEVER:**
```python
# ❌ FORBIDDEN: Many sequential ifs
if 'function_count' in diff:
    suggestions.append("Split into functions")
if 'class_count' in diff:
    suggestions.append("Review class structure")
if 'docstring_count' in diff:
    suggestions.append("Add docstrings")
if 'complexity' in diff:
    suggestions.append("Reduce complexity")
```

**ALWAYS:**
```python
# ✅ REQUIRED: Dictionary mapping (Strategy Pattern)
DIFF_TO_SUGGESTION = {
    'function_count': "Split into functions",
    'class_count': "Review class structure",
    'docstring_count': "Add docstrings",
    'complexity': "Reduce complexity"
}

for diff_type, suggestion in DIFF_TO_SUGGESTION.items():
    if diff_type in diff:
        suggestions.append(suggestion)
```

---

## 3. Exception Handling (MANDATORY)

### 3.1 Always Use Wrapped Exceptions

**NEVER:**
```python
# ❌ FORBIDDEN: Generic exceptions
raise Exception("Something went wrong")
raise ValueError("Invalid input")
```

**ALWAYS:**
```python
# ✅ REQUIRED: Use wrapped exceptions from artemis_exceptions.py
from artemis_exceptions import (
    ConfigurationError,
    ValidationError,
    LLMAPIError,
    wrap_exception
)

# Example 1: Direct wrapped exception
raise ConfigurationError(
    "Invalid framework configuration",
    context={'framework': framework, 'expected': ['django', 'flask']}
)

# Example 2: Wrap external exceptions
try:
    result = external_api_call()
except ExternalAPIError as e:
    raise wrap_exception(
        e,
        LLMAPIError,
        "Failed to call external API",
        context={'endpoint': endpoint, 'params': params}
    )
```

### 3.2 Exception Context

**ALWAYS** provide context with exceptions:

```python
raise ValidationError(
    "Code validation failed",
    context={
        'stage': validation_stage,
        'code_snippet': code[:100],
        'expected': expected_pattern,
        'actual': actual_pattern
    }
)
```

---

## 4. Documentation (MANDATORY)

### 4.1 Module-Level Docstrings

**REQUIRED** at the top of every file:

```python
#!/usr/bin/env python3
"""
Module Name - One-line description

WHY: Detailed explanation of why this module exists.
RESPONSIBILITY: What this module is responsible for (Single Responsibility).
PATTERNS: Which design patterns are used and why.

Example:
    validator = MyValidator()
    result = validator.validate(code)
"""
```

### 4.2 Class-Level Docstrings

**REQUIRED** for every class:

```python
class MyValidator:
    """
    One-line description of the class.

    WHY: Why this class exists (what problem it solves).
    RESPONSIBILITY: What this class is responsible for (SRP).
    PATTERNS: Design patterns used (Strategy, Factory, Observer, etc.).

    Example:
        validator = MyValidator(config)
        result = validator.validate(code)

    Attributes:
        attribute1: Description of attribute1
        attribute2: Description of attribute2
    """
```

### 4.3 Method-Level Docstrings

**REQUIRED** for every method:

```python
def validate_code(self, code: str, context: Dict) -> ValidationResult:
    """
    Validate code against patterns.

    WHY: Explains why this validation is needed (e.g., "Catches hallucinated imports").
    PERFORMANCE: Any performance considerations (e.g., "O(n) complexity, uses cache").

    Args:
        code: Source code to validate
        context: Validation context with framework, language, requirements

    Returns:
        ValidationResult with passed/failed status and recommendations

    Raises:
        ValidationError: If validation cannot be performed

    Example:
        result = validator.validate_code(
            code="import django",
            context={'framework': 'django'}
        )
    """
```

### 4.4 Inline Comments - WHY not WHAT

```python
# ✅ GOOD: Explains WHY
# Use dictionary mapping instead of if/elif chain (SOLID: Open/Closed)
validators = {
    'django': DjangoValidator,
    'flask': FlaskValidator
}

# ✅ GOOD: Explains performance consideration
# Compile regex once for performance (avoid recompiling in loop)
self.pattern = re.compile(r'pattern')

# ❌ BAD: States the obvious
# Loop through items
for item in items:
    # Process the item
    process(item)
```

---

## 5. Performance Optimization (REQUIRED)

### 5.1 Avoid Recomputation

```python
# ❌ BAD: Recomputes in loop
for item in items:
    if re.match(r'pattern', item):  # Recompiles regex every iteration
        process(item)

# ✅ GOOD: Compile once
pattern = re.compile(r'pattern')  # Compile once (performance)
for item in items:
    if pattern.match(item):
        process(item)
```

### 5.2 Use Early Returns

```python
# ❌ BAD: Nested ifs with late return
def validate(code):
    if code:
        if len(code) > 0:
            if is_valid(code):
                return True
    return False

# ✅ GOOD: Early returns (faster, cleaner)
def validate(code):
    """Validate code with early returns for performance"""
    if not code:
        return False
    if len(code) == 0:
        return False
    return is_valid(code)
```

### 5.3 Cache Expensive Operations

```python
from functools import lru_cache

class MyValidator:
    """Validator with caching for performance"""

    @lru_cache(maxsize=1000)
    def _compute_expensive_metric(self, code: str) -> float:
        """
        Compute expensive metric with caching.
        WHY: This operation is expensive (AST parsing), cache results.
        PERFORMANCE: LRU cache with 1000 entries prevents recomputation.
        """
        return expensive_computation(code)
```

### 5.4 List Comprehensions Over Loops

```python
# ❌ SLOWER: Loop with append
results = []
for item in items:
    if item.condition:
        results.append(item.value)

# ✅ FASTER: List comprehension
results = [item.value for item in items if item.condition]
```

---

## 6. SOLID Principles (MANDATORY)

### 6.1 Single Responsibility Principle (SRP)

Every class/module should have ONE responsibility:

```python
# ❌ BAD: Multiple responsibilities
class ValidatorAndLogger:
    def validate(self, code):
        # Validates code
        pass

    def log(self, message):
        # Logs messages
        pass

# ✅ GOOD: Single responsibility
class Validator:
    """ONLY validates code"""
    def validate(self, code):
        pass

class Logger:
    """ONLY logs messages"""
    def log(self, message):
        pass
```

### 6.2 Open/Closed Principle

Open for extension, closed for modification:

```python
# ✅ GOOD: Add new validators without modifying existing code
class ValidatorFactory:
    """Factory enables adding new validators without code changes"""

    _validators = {}

    @classmethod
    def register(cls, name: str, validator_class):
        """Register new validator (Open for extension)"""
        cls._validators[name] = validator_class

    @classmethod
    def create(cls, name: str):
        """Create validator (Closed for modification)"""
        return cls._validators[name]()

# Register new validators without modifying factory
ValidatorFactory.register('django', DjangoValidator)
ValidatorFactory.register('flask', FlaskValidator)
```

### 6.3 Dependency Inversion Principle

Depend on abstractions, not concretions:

```python
from abc import ABC, abstractmethod

class ValidatorInterface(ABC):
    """Abstract validator (depend on this, not concrete classes)"""

    @abstractmethod
    def validate(self, code: str) -> bool:
        pass

class DjangoValidator(ValidatorInterface):
    """Concrete implementation"""
    def validate(self, code: str) -> bool:
        return True

class MyService:
    """Depends on abstraction, not concrete validator"""
    def __init__(self, validator: ValidatorInterface):
        self.validator = validator  # Can be ANY validator
```

---

## 7. Type Hints (REQUIRED)

**ALWAYS** use type hints:

```python
from typing import Dict, List, Optional, Tuple, Callable, Any

def validate_code(
    code: str,
    context: Dict[str, Any],
    callback: Optional[Callable[[str], bool]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate code with type hints.

    Returns:
        Tuple of (is_valid, warnings)
    """
    return True, []
```

---

## 8. Code Organization

### 8.1 Constants at Module Level

```python
# Module-level constants (uppercase)
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3

VALIDATION_STRATEGIES = {
    'structural': StructuralValidator,
    'semantic': SemanticValidator,
    'ast': ASTValidator
}
```

### 8.2 Private Methods (Single Underscore)

```python
class MyClass:
    def public_method(self):
        """Public API"""
        return self._private_helper()

    def _private_helper(self):
        """
        Private helper method.
        WHY: Extracted to avoid nested logic in public method.
        """
        return "result"
```

---

## 9. Testing Requirements

### 9.1 Every Module Must Have Tests

```python
# File: my_module.py
class MyValidator:
    pass

# File: test_my_module.py (REQUIRED)
import unittest
from my_module import MyValidator

class TestMyValidator(unittest.TestCase):
    def test_validation_passes(self):
        """Test that validation passes for valid code"""
        validator = MyValidator()
        result = validator.validate("valid code")
        self.assertTrue(result)
```

### 9.2 Test Edge Cases

```python
def test_edge_cases(self):
    """Test edge cases (empty input, None, invalid types)"""
    validator = MyValidator()

    # Edge case: empty string
    result = validator.validate("")
    self.assertFalse(result)

    # Edge case: None
    with self.assertRaises(ValueError):
        validator.validate(None)
```

---

## 10. Performance Measurement

### 10.1 Profile Expensive Operations

```python
import time
from functools import wraps

def profile(func):
    """
    Profile function execution time.
    WHY: Identifies performance bottlenecks.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start

        if duration > 1.0:  # Log slow operations
            logger.warning(f"{func.__name__} took {duration:.2f}s")

        return result
    return wrapper

@profile
def expensive_operation(data):
    """This operation is profiled for performance"""
    return process(data)
```

---

## 11. Examples - Good vs Bad

### Example 1: Validation with Strategy Pattern

**❌ BAD:**
```python
def validate(code, framework):
    if framework == 'django':
        if 'from django' in code:
            return True
        else:
            return False
    elif framework == 'flask':
        if 'from flask' in code:
            return True
        else:
            return False
    elif framework == 'rails':
        if 'require' in code:
            return True
        else:
            return False
```

**✅ GOOD:**
```python
class FrameworkValidator:
    """
    Framework-specific code validation.

    WHY: Validates code matches framework patterns.
    PATTERNS: Strategy pattern for framework-specific validation.
    """

    # Strategy pattern: Dictionary mapping (avoid if/elif)
    FRAMEWORK_PATTERNS = {
        'django': r'from django',
        'flask': r'from flask',
        'rails': r'require'
    }

    def validate(self, code: str, framework: str) -> bool:
        """
        Validate code contains framework pattern.

        WHY: Ensures generated code uses correct framework imports.
        PERFORMANCE: O(n) regex search, compiled patterns cached.

        Args:
            code: Source code to validate
            framework: Framework name ('django', 'flask', 'rails')

        Returns:
            True if code matches framework pattern
        """
        pattern = self.FRAMEWORK_PATTERNS.get(framework)
        if not pattern:
            raise ValidationError(
                f"Unknown framework: {framework}",
                context={'framework': framework, 'supported': list(self.FRAMEWORK_PATTERNS.keys())}
            )

        return bool(re.search(pattern, code))
```

---

## 12. Environment Variables

**ALWAYS** support environment variable configuration:

```python
import os

# ✅ GOOD: Environment variable with default
ENABLE_VALIDATION = os.getenv("ARTEMIS_ENABLE_VALIDATION", "true").lower() == "true"
ENABLE_RAG_VALIDATION = os.getenv("ARTEMIS_ENABLE_RAG_VALIDATION", "true").lower() == "true"
VALIDATION_MODE = os.getenv("ARTEMIS_VALIDATION_MODE", "standard")
```

---

## 13. Logging Standards

```python
# ✅ GOOD: Structured logging with context
logger.log(
    f"Validation failed for {framework}",
    "WARNING",
    context={
        'framework': framework,
        'code_snippet': code[:100],
        'expected_pattern': pattern
    }
)

# ✅ GOOD: Performance logging
logger.log(f"Validation took {duration:.2f}s (threshold: 1.0s)", "DEBUG")
```

---

## Summary Checklist

Before committing code, verify:

- [ ] No `elif` chains (use dictionary mapping)
- [ ] No nested `for` loops or `if` statements (extract to helper methods)
- [ ] No sequential `if` statements (use Strategy pattern)
- [ ] All exceptions are wrapped (use `artemis_exceptions`)
- [ ] Module-level docstring with WHY and PATTERNS
- [ ] Class-level docstring with RESPONSIBILITY
- [ ] Method-level docstring with WHY and PERFORMANCE
- [ ] Type hints on all functions/methods
- [ ] Design pattern used (Strategy, Factory, Observer)
- [ ] Observer pattern used if multiple components need notifications
- [ ] Performance optimizations applied (caching, early returns, list comprehensions)
- [ ] SOLID principles followed
- [ ] Tests created for module
- [ ] Environment variables for configuration
- [ ] Logging with context

---

## Enforcement

**This is not optional.** All code MUST follow these standards. Code reviews will reject:

1. Any `elif` chains
2. Any nested loops/ifs without extraction to helper methods
3. Any sequential `if` statements (must use Strategy pattern)
4. Missing docstrings (module/class/method level)
5. Missing WHY comments
6. Unwrapped exceptions
7. Missing type hints
8. Missing performance considerations

**Good code is:**
- Readable (clear WHY comments)
- Maintainable (design patterns, SOLID)
- Performant (optimizations, caching)
- Testable (dependency injection, abstractions)
- Extensible (Open/Closed principle)
