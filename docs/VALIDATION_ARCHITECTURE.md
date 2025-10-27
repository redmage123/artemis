# Artemis Validation Architecture

## Overview

Artemis uses a **4-layer validation architecture** to reduce hallucinations and ensure high-quality code generation. Each layer serves a distinct purpose and operates at different points in the development pipeline.

```
┌───────────────────────────────────────────────────────────────────────┐
│                   Artemis 4-Layer Validation                          │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Layer 1: Preflight Validation (BEFORE)                              │
│  ├─ File: preflight_validator.py                                     │
│  ├─ When: Before pipeline execution                                  │
│  ├─ What: Static checks (syntax, imports, file permissions)          │
│  └─ Purpose: Prevent execution with broken code                      │
│                                                                       │
│  Layer 2: Strategy Selection (PLANNING)                              │
│  ├─ File: requirements_driven_validator.py                           │
│  ├─ When: Before generation (planning phase)                         │
│  ├─ What: Analyze requirements → select workflow → choose validator  │
│  └─ Purpose: Determine HOW to validate based on artifact type        │
│                                                                       │
│  Layer 3: Validation Pipeline (DURING) ← ANTI-HALLUCINATION          │
│  ├─ File: validation_pipeline.py                                     │
│  ├─ When: During generation (each LLM call)                          │
│  ├─ What: Continuous validation with immediate feedback              │
│  └─ Purpose: Catch hallucinations DURING generation, not after       │
│                                                                       │
│  Layer 4: Quality Gates (AFTER)                                      │
│  ├─ File: artifact_quality_validator.py                              │
│  ├─ When: After artifact is created                                  │
│  ├─ What: Final quality checks (coverage, completeness, standards)   │
│  └─ Purpose: Ensure final artifact meets quality criteria            │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

## Layer Details

### Layer 1: Preflight Validation

**File**: `preflight_validator.py`

**When to use**: Before starting any pipeline execution

**What it checks**:
- Python syntax errors (using `py_compile`)
- Missing critical files
- File permissions
- Import-time errors

**Example**:
```python
from preflight_validator import PreflightValidator

validator = PreflightValidator(verbose=True)
results = validator.validate_all(base_path="src")

if not results['passed']:
    print(f"❌ {results['critical_count']} critical issues")
    validator.print_report()
else:
    print("✅ Preflight passed - ready to start pipeline")
```

**Key Feature**: Can auto-fix syntax errors using LLM
```python
validator = PreflightValidator(llm_client=llm, auto_fix=True)
validator.auto_fix_syntax_errors()
```

---

### Layer 2: Strategy Selection

**File**: `requirements_driven_validator.py`

**When to use**: After receiving task requirements, before generation

**What it does**:
- Analyzes task title and description
- Detects artifact type (Code, Notebook, UI, Documentation)
- Selects appropriate workflow (TDD, Quality-Driven, Visual-Test)
- Chooses matching validator
- Extracts quality criteria

**Example**:
```python
from requirements_driven_validator import RequirementsDrivenValidator

validator = RequirementsDrivenValidator(logger=logger)

strategy = validator.analyze_requirements(
    task_title="Create data analysis notebook",
    task_description="Analyze sales data with Plotly charts"
)

print(f"Artifact: {strategy.artifact_type}")  # NOTEBOOK
print(f"Workflow: {strategy.workflow}")       # QUALITY_DRIVEN
print(f"Validator: {strategy.validator_class}")  # NotebookQualityValidator
print(f"Criteria: {strategy.quality_criteria}")  # {'min_cells': 8, 'requires_visualizations': True}
```

**Why it's needed**: Eliminates the "one-size-fits-all TDD" problem. Different artifacts need different validation strategies.

---

### Layer 3: Validation Pipeline (Anti-Hallucination)

**File**: `validation_pipeline.py` ← **NEW**

**When to use**: During LLM code generation (at each stage)

**What it does**:
- Validates code **incrementally** as it's generated
- Provides **immediate feedback** to LLM
- **Regenerates with fixes** when validation fails
- Catches hallucinations **before they propagate**

**Validation Stages**:
1. `IMPORTS` - Verify imports are valid and necessary
2. `SIGNATURE` - Check function/class signatures with type hints
3. `DOCSTRING` - Validate docstring completeness
4. `BODY` - Check implementation for placeholders, wrong methods
5. `TESTS` - Verify tests have assertions and framework imports
6. `FULL_CODE` - Complete validation of entire artifact

**Example 1: Quick validation**:
```python
from validation_pipeline import validate_python_code

code = """
def process(data):
    # TODO: implement this
    pass
"""

result = validate_python_code(code, strict=True)
print(result.passed)  # False
print(result.feedback)  # ["Found placeholder: 'TODO'"]
```

**Example 2: Incremental validation**:
```python
from validation_pipeline import ValidationPipeline, ValidationStage

pipeline = ValidationPipeline(strict_mode=True)

# Stage 1: Validate imports
result = pipeline.validate_stage(
    code="import os\nfrom pathlib import Path",
    stage=ValidationStage.IMPORTS
)

# Stage 2: Validate signature
result = pipeline.validate_stage(
    code="""
import os
from pathlib import Path

def read_file(file_path: Path) -> str:
    \"\"\"Read file contents\"\"\"
    pass
""",
    stage=ValidationStage.SIGNATURE
)

# Stage 3: Validate body
result = pipeline.validate_stage(
    code="""
import os
from pathlib import Path

def read_file(file_path: Path) -> str:
    \"\"\"Read file contents\"\"\"
    with open(file_path, 'r') as f:
        return f.read()
""",
    stage=ValidationStage.BODY
)
```

**Example 3: Automatic generation with retries**:
```python
pipeline = ValidationPipeline(
    llm_client=llm,
    logger=logger,
    strict_mode=True
)

code, success = pipeline.generate_with_validation(
    task="Create a REST API endpoint for user registration",
    stages=[
        ValidationStage.IMPORTS,
        ValidationStage.SIGNATURE,
        ValidationStage.BODY,
        ValidationStage.TESTS
    ],
    max_retries=2
)

if success:
    print("✅ Generated valid code!")
    summary = pipeline.get_validation_summary()
    print(f"Pass rate: {summary['pass_rate']:.0%}")
else:
    print("❌ Failed after retries")
```

**Hallucination Detection**:

The pipeline specifically checks for:
- ✅ **Placeholders**: `TODO`, `FIXME`, `...`, `pass  # implementation`
- ✅ **Wrong methods**: `user.save()` instead of `db.session.add(user)`
- ✅ **Missing imports**: Using libraries without importing them
- ✅ **Syntax errors**: Invalid Python syntax
- ✅ **Bare excepts**: `except:` without specific exception type
- ✅ **Star imports**: `from X import *`
- ✅ **Missing type hints**: Functions without return types
- ✅ **Missing docstrings**: Undocumented functions/classes

**Example of hallucination prevention**:
```python
# LLM generates this (with hallucinations):
bad_code = """
def create_user(name, email):
    # TODO: validate email
    user = User(name=name, email=email)
    user.save()  # ← WRONG: SQLAlchemy doesn't have .save()
    return user
"""

result = validate_python_code(bad_code, strict=True)
# Feedback: [
#   "Function 'create_user' missing return type hint",
#   "Found placeholder: 'TODO' - code must be complete",
#   "SQLAlchemy uses db.session.add() and commit(), not .save()"
# ]

# Pipeline regenerates with this feedback:
feedback_prompt = pipeline.get_regeneration_prompt(result)
# LLM receives: "Fix: Missing return type, Remove TODO, Use db.session.add()"

# LLM generates corrected code:
good_code = """
from sqlalchemy.orm import Session

def create_user(name: str, email: str, db: Session) -> User:
    \"\"\"Create a new user\"\"\"
    if not is_valid_email(email):
        raise ValueError("Invalid email")
    user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()
    return user
"""
# ✅ Passes validation
```

---

### Layer 4: Quality Gates

**File**: `artifact_quality_validator.py`

**When to use**: After code generation is complete

**What it does**:
- Final quality checks on completed artifact
- Validates against requirements-driven criteria
- Checks test coverage, documentation, standards

**Validators**:
- `NotebookQualityValidator` - Jupyter notebooks
- `CodeQualityValidator` - Python code (TDD)
- `UIQualityValidator` - React/UI components

**Example**:
```python
from artifact_quality_validator import create_validator

validator = create_validator(
    validator_class='CodeQualityValidator',
    quality_criteria={
        'min_test_coverage': 0.8,
        'requires_unit_tests': True
    },
    logger=logger
)

result = validator.validate(Path("src/my_module.py"))

print(f"Score: {result.score:.2f}")
print(f"Passed: {result.passed}")
print(f"Criteria: {result.criteria_results}")
print(f"Feedback: {result.feedback}")
```

---

## Complete Integration Example

Here's how all 4 layers work together in `development_stage.py`:

```python
from preflight_validator import PreflightValidator
from requirements_driven_validator import RequirementsDrivenValidator
from validation_pipeline import ValidationPipeline, ValidationStage
from artifact_quality_validator import create_validator

class DevelopmentStage:
    def execute(self, task_title: str, task_description: str):
        # ═══════════════════════════════════════════════════
        # LAYER 1: Preflight
        # ═══════════════════════════════════════════════════
        preflight = PreflightValidator(verbose=False)
        preflight_results = preflight.validate_all()

        if not preflight_results['passed']:
            self.logger.log("❌ Preflight failed", "ERROR")
            return None

        # ═══════════════════════════════════════════════════
        # LAYER 2: Strategy Selection
        # ═══════════════════════════════════════════════════
        strategy_validator = RequirementsDrivenValidator(logger=self.logger)
        strategy = strategy_validator.analyze_requirements(
            task_title=task_title,
            task_description=task_description
        )

        # ═══════════════════════════════════════════════════
        # LAYER 3: Validation Pipeline (continuous)
        # ═══════════════════════════════════════════════════
        pipeline = ValidationPipeline(
            llm_client=self.llm_client,
            logger=self.logger,
            strict_mode=True
        )

        # Choose stages based on workflow
        if strategy.workflow.value == 'tdd':
            stages = [
                ValidationStage.IMPORTS,
                ValidationStage.TESTS,      # TDD: Tests first
                ValidationStage.SIGNATURE,
                ValidationStage.BODY,
            ]
        else:
            stages = [
                ValidationStage.IMPORTS,
                ValidationStage.SIGNATURE,
                ValidationStage.DOCSTRING,
                ValidationStage.BODY,
            ]

        code, success = pipeline.generate_with_validation(
            task=f"{task_title}\n\n{task_description}",
            stages=stages,
            max_retries=2
        )

        if not success:
            self.logger.log("❌ Validation pipeline failed", "ERROR")
            return None

        # ═══════════════════════════════════════════════════
        # LAYER 4: Quality Gates
        # ═══════════════════════════════════════════════════
        temp_file = Path(f"/tmp/code_{task_id}.py")
        temp_file.write_text(code)

        quality_validator = create_validator(
            validator_class=strategy.validator_class,
            quality_criteria=strategy.quality_criteria,
            logger=self.logger
        )

        quality_result = quality_validator.validate(temp_file)

        if not quality_result.passed:
            self.logger.log(f"❌ Quality gate failed: {quality_result.feedback}", "ERROR")
            return None

        # ✅ All layers passed
        return code
```

---

## Comparison: Before vs After

### Before (2 Layers Only)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Preflight  │ --> │   Generate   │ --> │   Quality    │
│   (before)   │     │   (no check) │     │   (after)    │
└──────────────┘     └──────────────┘     └──────────────┘
                            ❌
                     Hallucinations
                     accumulate
                     unchecked
```

**Problems**:
- Hallucinations not detected until end
- Must regenerate entire artifact
- No intermediate feedback
- Errors compound

### After (4 Layers)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Preflight  │ --> │   Strategy   │ --> │   Pipeline   │ --> │   Quality    │
│   (before)   │     │  (planning)  │     │   (during)   │     │   (after)    │
│              │     │              │     │   ✅ Check   │     │              │
│              │     │              │     │   ✅ Retry   │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

**Benefits**:
- ✅ Immediate hallucination detection
- ✅ Automatic regeneration with feedback
- ✅ Incremental validation
- ✅ Errors caught early

---

## When to Use Each Layer

| Layer | When | Required | Purpose |
|-------|------|----------|---------|
| **Preflight** | Before pipeline starts | ✅ Yes | Ensure code can run |
| **Strategy** | After requirements received | ✅ Yes | Choose validation approach |
| **Pipeline** | During generation | ⚠️ Recommended | Prevent hallucinations |
| **Quality** | After generation complete | ✅ Yes | Final quality check |

---

## Performance Impact

### Without Validation Pipeline (Layer 3)

```
Generate → Validate → ❌ Fail → Regenerate entire artifact
Time: ~30 seconds (full regeneration)
LLM calls: 2 (initial + full regen)
```

### With Validation Pipeline (Layer 3)

```
Generate imports → ✅ Pass
Generate signature → ❌ Fail → Regenerate signature only
Generate body → ✅ Pass
Time: ~15 seconds (partial regeneration)
LLM calls: 4 (incremental)
```

**Result**: 50% faster by catching errors early

---

## Configuration

### Strict Mode vs Non-Strict

```python
# Strict mode: Fail on ANY validation error
pipeline = ValidationPipeline(strict_mode=True)

# Non-strict mode: Only fail on CRITICAL errors
pipeline = ValidationPipeline(strict_mode=False)
```

**Recommendation**: Use strict mode for production, non-strict for experimentation

---

## Metrics and Monitoring

Track validation effectiveness:

```python
summary = pipeline.get_validation_summary()

print(f"Total validations: {summary['total_validations']}")
print(f"Pass rate: {summary['pass_rate']:.0%}")
print(f"By stage: {summary['by_stage']}")

# Example output:
# {
#   'total_validations': 12,
#   'passed': 10,
#   'failed': 2,
#   'pass_rate': 0.83,
#   'by_stage': {
#     'imports': {'passed': 3, 'failed': 0},
#     'signature': {'passed': 3, 'failed': 1},
#     'body': {'passed': 4, 'failed': 1}
#   }
# }
```

---

## Future Enhancements

1. **Confidence Scoring**: Add LLM confidence scores to validation results
2. **Knowledge Graph Integration**: Verify method calls against Neo4j knowledge graph
3. **Test Execution**: Run tests during validation (not just static checks)
4. **Multi-Language Support**: Extend beyond Python to JavaScript, Java, etc.
5. **Custom Validators**: Allow users to define custom validation rules

---

## References

- `src/preflight_validator.py` - Layer 1
- `src/requirements_driven_validator.py` - Layer 2
- `src/validation_pipeline.py` - Layer 3 (NEW)
- `src/artifact_quality_validator.py` - Layer 4
- `src/validation_pipeline_integration_example.py` - Examples

---

## FAQ

**Q: Do I need to use all 4 layers?**
A: Layers 1, 2, and 4 are required. Layer 3 (pipeline) is recommended for reducing hallucinations.

**Q: Can I use validation pipeline without the other layers?**
A: Yes, but you lose the benefits of preflight checks and strategy selection.

**Q: What's the performance overhead?**
A: Layer 3 adds ~0.5s per stage, but saves time by catching errors early.

**Q: How does this reduce hallucinations?**
A: By validating incrementally and providing immediate feedback, the LLM learns what's correct before generating more code.

**Q: Can I customize validation rules?**
A: Yes, modify `_validate_*` methods in `ValidationPipeline` or create custom validators.

---

**Last Updated**: 2025-10-27
**Version**: 1.0
