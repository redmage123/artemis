# Claude Code Generation Standards for Artemis

**MANDATORY**: All code generation MUST follow these standards. No exceptions.

## 0. Core Programming Paradigm

**ALWAYS use functional programming patterns wherever possible:**

### 0.1 Prefer Pure Functions

```python
# ❌ BAD: Impure function with side effects
results = []
def process_item(item):
    results.append(item.value)  # Mutates global state
    return item.value

# ✅ GOOD: Pure function (no side effects, same input = same output)
def process_item(item) -> int:
    """
    Pure function - no side effects.
    WHY: Easier to test, reason about, and parallelize.
    """
    return item.value

# Use map to apply pure function
results = list(map(process_item, items))
```

### 0.2 Immutability Over Mutation

```python
# ❌ BAD: Mutating data structures
def add_item(items_list, item):
    items_list.append(item)  # Mutates input
    return items_list

# ✅ GOOD: Return new data structure
def add_item(items: List, item) -> List:
    """
    Immutable operation - returns new list.
    WHY: Prevents bugs from unexpected mutations.
    """
    return [*items, item]
```

### 0.3 Declarative Over Imperative

```python
# ❌ BAD: Imperative style (HOW to do it)
def get_active_users(users):
    active = []
    for user in users:
        if user.is_active:
            active.append(user)
    return active

# ✅ GOOD: Declarative style (WHAT you want)
def get_active_users(users: List[User]) -> List[User]:
    """
    Declarative filtering.
    WHY: More readable, expresses intent clearly.
    """
    return [user for user in users if user.is_active]

# ✅ EVEN BETTER: Functional composition
from functools import partial

is_active = lambda user: user.is_active
get_active_users = partial(filter, is_active)
```

### 0.4 Function Composition

```python
# ✅ GOOD: Compose small functions
from functools import reduce

def compose(*functions):
    """
    Compose functions right-to-left.
    WHY: Build complex behavior from simple, testable parts.
    """
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)

# Example usage
normalize = str.lower
remove_spaces = lambda s: s.replace(' ', '')
validate = lambda s: len(s) > 0

process_input = compose(validate, remove_spaces, normalize)
result = process_input("  Hello World  ")
```

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

### 1.3 Observer Pattern - For event notifications (MANDATORY for Artemis Integration)

**REQUIRED** when multiple components need to react to events.
**MANDATORY** for all Artemis pipeline stages and agents.

```python
from pipeline_observer import PipelineObservable, EventBuilder

class MyComponent:
    """
    Component with Observer pattern integration.

    WHY: Observer pattern enables loose coupling - other components can
    subscribe to events without MyComponent knowing about them.

    PATTERNS: Observer pattern for event notifications
    ARTEMIS INTEGRATION: All stages MUST support PipelineObservable
    """

    def __init__(self, observable: Optional[PipelineObservable] = None):
        """
        Initialize component with optional observable.

        Args:
            observable: Optional PipelineObservable for event notifications
                       (REQUIRED for Artemis integration)
        """
        self.observable = observable

    def do_something(self):
        """
        Perform action and notify observers.

        WHY: Notify observers enables monitoring, logging, error tracking,
        and real-time updates without tight coupling.
        """
        # Perform action
        result = self._perform_action()

        # Notify observers (if available) - REQUIRED for Artemis stages
        if self.observable:
            event = EventBuilder.my_event(
                data=result,
                timestamp=datetime.now(),
                context={'component': self.__class__.__name__}
            )
            self.observable.notify(event)

        return result

# Example: Artemis Stage with Observer Pattern
class MyArtemisStage:
    """
    Artemis pipeline stage with Observer pattern.

    WHY: Enables monitoring, logging, and error tracking across pipeline.
    ARTEMIS INTEGRATION: MANDATORY for all pipeline stages.
    """

    def __init__(self, observable: Optional[PipelineObservable] = None):
        self.observable = observable

    def execute(self, context: Dict) -> StageResult:
        """Execute stage with observer notifications"""
        # Notify stage start
        if self.observable:
            self.observable.notify(
                EventBuilder.stage_started(
                    stage_name=self.__class__.__name__,
                    context=context
                )
            )

        try:
            result = self._do_work(context)

            # Notify success
            if self.observable:
                self.observable.notify(
                    EventBuilder.stage_completed(
                        stage_name=self.__class__.__name__,
                        result=result
                    )
                )

            return result

        except Exception as e:
            # Notify failure
            if self.observable:
                self.observable.notify(
                    EventBuilder.stage_failed(
                        stage_name=self.__class__.__name__,
                        error=str(e),
                        traceback=traceback.format_exc()
                    )
                )
            raise
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

### 2.2 NO Nested For Loops (MANDATORY)

**NEVER:**
```python
# ❌ FORBIDDEN: Nested loops
for item in items:
    for sub_item in item.sub_items:
        if sub_item.condition:
            process(sub_item)
```

**ALWAYS:**
```python
# ✅ REQUIRED: List comprehension (PREFERRED)
matching_items = [
    sub_item
    for item in items
    for sub_item in item.sub_items
    if sub_item.condition
]
for sub_item in matching_items:
    process(sub_item)

# ✅ ALTERNATIVE: Extract to helper method with generator
def _get_matching_sub_items(items):
    """
    Generator to flatten nested structure.
    WHY: Avoids nested loops, memory efficient.
    PERFORMANCE: Generator yields items one at a time (memory efficient).
    """
    for item in items:
        yield from (s for s in item.sub_items if s.condition)

for sub_item in _get_matching_sub_items(items):
    process(sub_item)

# ✅ ALTERNATIVE: Map/filter/reduce pattern
from itertools import chain
matching_items = filter(
    lambda s: s.condition,
    chain.from_iterable(item.sub_items for item in items)
)
for sub_item in matching_items:
    process(sub_item)
```

### 2.2b NO Nested Ifs (MANDATORY)

**NEVER:**
```python
# ❌ FORBIDDEN: Nested ifs
if condition1:
    if condition2:
        if condition3:
            do_something()
```

**ALWAYS:**
```python
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

### 5.4 List Comprehensions Over Loops (MANDATORY)

**ALWAYS prefer comprehensions, map(), filter(), reduce() over explicit loops:**

```python
# ❌ SLOWER: Loop with append
results = []
for item in items:
    if item.condition:
        results.append(item.value)

# ✅ FASTER: List comprehension
results = [item.value for item in items if item.condition]

# ✅ GOOD: Generator comprehension for large datasets (memory efficient)
results = (item.value for item in items if item.condition)

# ✅ GOOD: Dict comprehension
mapping = {item.key: item.value for item in items if item.active}

# ✅ GOOD: Set comprehension
unique_values = {item.value for item in items}

# ✅ GOOD: Map/filter pattern
from functools import reduce
values = list(map(lambda x: x.value, filter(lambda x: x.condition, items)))

# ✅ GOOD: Reduce pattern for aggregation
total = reduce(lambda acc, item: acc + item.value, items, 0)
```

### 5.5 Performance-First Mindset (MANDATORY)

**ALWAYS optimize for performance when writing code:**

```python
# ❌ BAD: Inefficient nested lookup
for item in items:
    for user in users:  # O(n*m) - quadratic time
        if item.user_id == user.id:
            process(item, user)

# ✅ GOOD: Pre-build lookup dictionary
user_lookup = {u.id: u for u in users}  # O(m) to build
for item in items:  # O(n) to iterate
    user = user_lookup.get(item.user_id)  # O(1) lookup
    if user:
        process(item, user)
# Total: O(n + m) - linear time

# ❌ BAD: Recompute in loop
for text in texts:
    if re.match(r'pattern', text):  # Recompiles regex each iteration
        process(text)

# ✅ GOOD: Compile once, reuse
pattern = re.compile(r'pattern')
for text in texts:
    if pattern.match(text):
        process(text)

# ❌ BAD: String concatenation in loop
result = ""
for item in items:
    result += str(item)  # O(n²) - creates new string each iteration

# ✅ GOOD: Use join()
result = ''.join(str(item) for item in items)  # O(n)

# ❌ BAD: Repeated database queries
for user_id in user_ids:
    user = db.get_user(user_id)  # N queries
    process(user)

# ✅ GOOD: Batch query
users = db.get_users_by_ids(user_ids)  # 1 query
for user in users:
    process(user)
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

## 13. DRY Principle - Don't Repeat Yourself (MANDATORY)

**NEVER** duplicate code logic. Extract to reusable functions/methods.

### 13.1 Extract Common Logic

**❌ BAD: Duplicated validation logic**
```python
def validate_django_code(code):
    if not code:
        return False
    if len(code) == 0:
        return False
    if 'django' not in code:
        return False
    return True

def validate_flask_code(code):
    if not code:
        return False
    if len(code) == 0:
        return False
    if 'flask' not in code:
        return False
    return True
```

**✅ GOOD: Extract common validation**
```python
def _validate_code_base(code: str) -> bool:
    """
    Base validation for all code.
    WHY: DRY - avoid duplicating basic validation across validators.
    """
    if not code:
        return False
    if len(code) == 0:
        return False
    return True

def validate_django_code(code: str) -> bool:
    """Validate Django code using DRY base validation"""
    if not _validate_code_base(code):
        return False
    return 'django' in code

def validate_flask_code(code: str) -> bool:
    """Validate Flask code using DRY base validation"""
    if not _validate_code_base(code):
        return False
    return 'flask' in code
```

### 13.2 Use Helper Functions

**❌ BAD: Repeated formatting logic**
```python
result1 = f"Validation failed: {error1}. Context: {context1}"
result2 = f"Validation failed: {error2}. Context: {context2}"
result3 = f"Validation failed: {error3}. Context: {context3}"
```

**✅ GOOD: DRY helper function**
```python
def format_validation_error(error: str, context: str) -> str:
    """
    Format validation error message.
    WHY: DRY - single source of truth for error formatting.
    """
    return f"Validation failed: {error}. Context: {context}"

result1 = format_validation_error(error1, context1)
result2 = format_validation_error(error2, context2)
result3 = format_validation_error(error3, context3)
```

### 13.3 Constants for Magic Values

**❌ BAD: Magic values repeated**
```python
if timeout > 30:
    logger.log("Timeout exceeded 30 seconds")
if duration > 30:
    raise TimeoutError("Operation exceeded 30 seconds")
```

**✅ GOOD: DRY constant**
```python
DEFAULT_TIMEOUT_SECONDS = 30  # DRY: Single source of truth

if timeout > DEFAULT_TIMEOUT_SECONDS:
    logger.log(f"Timeout exceeded {DEFAULT_TIMEOUT_SECONDS} seconds")
if duration > DEFAULT_TIMEOUT_SECONDS:
    raise TimeoutError(f"Operation exceeded {DEFAULT_TIMEOUT_SECONDS} seconds")
```

### 13.4 Template Methods

**❌ BAD: Duplicated workflow logic**
```python
def process_django_request():
    setup()
    validate_django()
    process_django()
    cleanup()

def process_flask_request():
    setup()
    validate_flask()
    process_flask()
    cleanup()
```

**✅ GOOD: DRY template method**
```python
def process_request(validator, processor):
    """
    Template method for request processing.
    WHY: DRY - extract common workflow, parameterize differences.
    """
    setup()
    validator()
    processor()
    cleanup()

process_request(validate_django, process_django)
process_request(validate_flask, process_flask)
```

---

## 14. Logging Standards

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

- [ ] **Functional programming patterns** - pure functions, immutability, declarative style
- [ ] No `elif` chains (use dictionary mapping)
- [ ] **NO nested `for` loops** (use comprehensions, map/filter/reduce, or generators)
- [ ] No nested `if` statements (use early returns with guard clauses)
- [ ] No sequential `if` statements (use Strategy pattern)
- [ ] **Prefer comprehensions** (list/dict/set/generator) over explicit loops
- [ ] **Map/filter/reduce patterns** used where appropriate
- [ ] **Declarative over imperative** - express WHAT not HOW
- [ ] **Pure functions** where possible - no side effects, same input = same output
- [ ] **Immutability** - return new data structures instead of mutating inputs
- [ ] **Performance optimized** - O(n) not O(n²), batch queries, compile regex once, use join() not +=
- [ ] **DRY principle applied** - no duplicated logic, extract to helpers
- [ ] **No magic values** - use constants for repeated values
- [ ] All exceptions are wrapped (use `artemis_exceptions`)
- [ ] Module-level docstring with WHY and PATTERNS
- [ ] Class-level docstring with RESPONSIBILITY
- [ ] Method-level docstring with WHY and PERFORMANCE
- [ ] Type hints on all functions/methods
- [ ] Design pattern used (Strategy, Factory, Observer)
- [ ] **Observer pattern used for Artemis integration** (MANDATORY for stages/agents)
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
