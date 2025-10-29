# Validation System Testing

## Overview

Comprehensive unit testing suite for the Artemis validation pipeline, ensuring reliable test execution and quality assurance for LLM-generated code.

## Test Coverage

### Components Tested

1. **TestRunner** (`services/core/test_runner.py`) - **93% coverage**
   - Pytest invocation via `python -m pytest` for proper import resolution
   - Working directory management for Python package imports
   - Exit code interpretation (0=success, 2=failures, 4=collection errors)
   - stdout/stderr separation for debugging
   - Test result parsing and metrics calculation

2. **ValidationStage** (`stages/validation_stage.py`) - **90% coverage**
   - Multi-developer validation orchestration
   - APPROVED/BLOCKED status determination
   - Observable notifications for pipeline monitoring
   - Progress tracking and reporting
   - Error handling and edge cases

3. **ValidationStrategies** (`validated_developer/validation_strategies.py`) - **61% coverage**
   - RAG-enhanced validation (pattern matching against proven code)
   - Self-critique validation (AI self-review)
   - Regeneration decision logic
   - Feedback prompt generation

### Overall Coverage: **79%**

## Running Tests

### Basic Test Run
```bash
# Run all validation tests
python -m pytest src/test_validation_system.py -v

# Run specific test class
python -m pytest src/test_validation_system.py::TestValidationStage -v

# Run specific test
python -m pytest src/test_validation_system.py::TestTestRunner::test_pytest_invocation_uses_python_module -v
```

### With Coverage
```bash
# Run with coverage report
python -m pytest src/test_validation_system.py \
  --cov=stages.validation_stage \
  --cov=services.core.test_runner \
  --cov=validated_developer.validation_strategies \
  --cov-report=term-missing

# Generate HTML coverage report
python -m pytest src/test_validation_system.py \
  --cov=stages \
  --cov=services \
  --cov=validated_developer \
  --cov-report=html:htmlcov

# Open HTML report
xdg-open htmlcov/index.html
```

### Using pytest.ini Configuration
```bash
# Run with all configured options (coverage, warnings, etc.)
python -m pytest src/test_validation_system.py
```

## Test Structure

### Unit Tests (Fast, Isolated)

**TestRunner Unit Tests** - Test pytest execution mechanics
- `test_pytest_invocation_uses_python_module` - Verify `python -m pytest` usage
- `test_working_directory_set_for_tests_folder` - Verify cwd management for imports
- `test_exit_code_zero_indicates_success` - Test success path
- `test_exit_code_nonzero_indicates_failure` - Test failure path
- `test_stdout_stderr_separation` - Test output capture

**ValidationStage Unit Tests** - Test validation orchestration
- `test_approved_when_exit_code_zero` - Single developer approval
- `test_blocked_when_exit_code_nonzero` - Single developer blocked
- `test_multiple_developers_all_approved` - Multi-developer success
- `test_multiple_developers_some_blocked` - Mixed results handling
- `test_observable_notifications` - Event broadcasting
- `test_progress_updates` - Progress tracking

**RAGValidationStrategy Unit Tests** - Test pattern-based validation
- `test_validation_passes_with_high_confidence` - High similarity to proven patterns
- `test_validation_fails_with_low_confidence` - Low similarity triggers regeneration
- `test_no_regeneration_after_max_retries` - Retry limit enforcement
- `test_feedback_prompt_generation` - Feedback from RAG recommendations

**SelfCritiqueValidationStrategy Unit Tests** - Test AI self-review
- `test_validation_passes_with_high_confidence` - AI confident in code
- `test_validation_triggers_regeneration_on_low_confidence` - Low confidence triggers retry
- `test_feedback_prompt_generation` - Feedback from critique findings

### Integration Tests (Slower, Multiple Components)

**ValidationIntegration Tests** - End-to-end validation flow
- `test_end_to_end_validation_success` - Complete flow with passing tests
- `test_end_to_end_validation_failure` - Complete flow with failing tests

## Key Bug Fixes Validated by Tests

### 1. ValidationStage BLOCKED Error (exit_code=2)

**Problem**: Tests were failing with exit_code=2 even when code was correct.

**Root Cause**:
- TestRunner used direct `pytest` executable instead of `python -m pytest`
- Python's import system couldn't resolve relative imports like `from auth.user import X`
- Missing `__init__.py` files broke package imports

**Fix**:
- Changed to `python -m pytest` for proper sys.path configuration
- Added working directory detection (run from parent of `tests/` directory)
- Auto-generate `__init__.py` files in DevelopmentStage

**Test Coverage**:
- `test_pytest_invocation_uses_python_module` - Validates correct pytest invocation
- `test_working_directory_set_for_tests_folder` - Validates cwd management
- `test_end_to_end_validation_success` - Validates complete fix

**Impact**:
- developer-a tests now pass (APPROVED with exit_code=0)
- Proper Python import resolution for all test scenarios

## Test Maintenance

### Adding New Tests

1. **Unit Tests**: Add to appropriate test class in `test_validation_system.py`
   ```python
   def test_new_feature(self):
       """
       Test that new feature works correctly.

       WHY: Explain why this test is important.
       """
       # Arrange: Set up test data
       # Act: Execute the feature
       # Assert: Verify expected behavior
   ```

2. **Integration Tests**: Add to `TestValidationIntegration` class
   ```python
   def test_feature_integration(self):
       """
       Test feature integration with other components.

       WHY: Ensures components work together correctly.
       """
       # Create real test environment
       # Execute complete workflow
       # Verify end-to-end behavior
   ```

### Maintaining Coverage

Target coverage thresholds:
- Critical components (TestRunner, ValidationStage): **90%+**
- Integration components (ValidationStrategies): **75%+**
- Overall system: **80%+**

To improve coverage:
```bash
# Identify untested lines
python -m pytest --cov=<module> --cov-report=term-missing

# Add tests for missing lines
# Re-run to verify coverage increase
```

## CI/CD Integration

### Continuous Integration

Add to GitHub Actions workflow:
```yaml
- name: Run validation tests with coverage
  run: |
    python -m pytest src/test_validation_system.py \
      --cov=stages --cov=services --cov=validated_developer \
      --cov-report=xml --cov-report=term

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
    fail_ci_if_error: true
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Run validation tests before commit
python -m pytest src/test_validation_system.py --maxfail=1 -x
if [ $? -ne 0 ]; then
    echo "Validation tests failed. Commit aborted."
    exit 1
fi
```

## Performance

Test execution times:
- Unit tests: ~2-3 seconds
- Integration tests: ~5-7 seconds
- Total suite: ~8-10 seconds

Fast enough for frequent execution during development.

## Future Enhancements

1. **Timeout Handling**: Add TestRunner timeout error handling (currently propagates to caller)
2. **Parallel Execution**: Enable pytest-xdist for faster test runs
3. **Property-Based Testing**: Add hypothesis tests for edge cases
4. **Performance Tests**: Add benchmarks for test execution speed
5. **Mutation Testing**: Use mutmut to verify test effectiveness

## References

- Validation Stage: `src/stages/validation_stage.py`
- Test Runner: `src/services/core/test_runner.py`
- Validation Strategies: `src/validated_developer/validation_strategies.py`
- Test Suite: `src/test_validation_system.py`
- Pytest Config: `pytest.ini`
