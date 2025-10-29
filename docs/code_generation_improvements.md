# Code Generation Quality Improvements

## Problem Statement

The validation system was correctly catching bugs in LLM-generated code - specifically import inconsistencies where code imported functions that weren't defined in the target module.

**Example Bug Caught:**
```python
# auth/user_auth.py
from database import get_user_by_username, validate_user_password  # ❌

# But database/__init__.py only had:
async def get_user_by_username(username):  # ✅
    ...
# Missing: validate_user_password ❌
```

## Root Cause

1. **Generic Prompts**: Quality-driven workflow prompt lacked specific consistency requirements
2. **No Pre-Validation**: Code was written to disk before checking for consistency issues
3. **Missing Guidance**: LLM wasn't explicitly told to verify import/export matching

## Solutions Implemented

### 1. Enhanced Prompt with Consistency Requirements

**File**: `src/agents/developer/developer.py:459-518`

Added explicit requirements to `_build_quality_prompt()`:

```python
CRITICAL CONSISTENCY REQUIREMENTS:
1. **Import Consistency**: Every imported function/class MUST be defined in the imported module
   - Before importing from a module, ensure that module exports those exact names
   - Example: If you write "from database import get_user, validate_password"
            then database/__init__.py MUST define both get_user() and validate_password()

2. **Complete Implementation**: NO placeholder functions or missing implementations
   - All functions must be fully implemented with working logic
   - All helper functions must be defined before use
   - All dependencies must be included in the generated files

3. **Self-Contained Code**: Generated code must work without external dependencies
   - If a function is called, it must be defined somewhere in your generated files
   - If a module is imported, it must be in your generated files or Python stdlib

4. **Test Compatibility**: Tests must import only what implementation provides
   - Review all test imports and ensure implementation files export those names
   - Ensure test function calls match implementation function signatures

VALIDATION CHECKLIST (verify before returning):
☐ All imports in implementation files have matching exports
☐ All imports in test files have matching exports in implementation
☐ No undefined functions are called
☐ No placeholder comments (TODO, FIXME, etc.)
☐ All async functions properly use await for async calls
☐ All error cases are handled
```

**Benefits:**
- ✅ LLM now has explicit guidelines for consistency
- ✅ Checklist format encourages self-validation before returning code
- ✅ Examples show correct patterns to follow
- ✅ Prevents common import/export mismatches

### 2. Import Consistency Validation

**File**: `src/agents/developer/developer.py:520-602`

Added `_validate_import_consistency()` method that:

1. **Parses all generated files** using Python AST
2. **Builds export map** tracking what each module defines
3. **Validates imports** against available exports
4. **Reports mismatches** with helpful error messages

```python
def _validate_import_consistency(self, generated_code: Dict) -> Dict:
    """
    Validate that all imports have matching exports

    WHY: Catches import inconsistencies before files are written,
         preventing ValidationStage failures due to missing functions.
    """
    # Parse all files, build export map
    module_exports = {}
    for file in all_files:
        tree = ast.parse(file['content'])
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                module_exports[module].add(node.name)

    # Check all imports against exports
    for file in all_files:
        for import_node in ast.walk(tree):
            if isinstance(import_node, ast.ImportFrom):
                # Verify imported name exists in target module
                if name not in module_exports[module]:
                    issues.append(f"❌ {path}: imports '{name}' from '{module}'
                                    but '{module}' doesn't export '{name}'")

    return {'valid': len(issues) == 0, 'issues': issues}
```

**Example Output:**
```
⚠️ Import consistency issues detected:
  ❌ auth/user_auth.py: imports 'validate_user_password' from 'database'
     but 'database' doesn't export 'validate_user_password'
   Available in 'database': get_user_by_username
```

**Benefits:**
- ✅ Catches import errors before files are written
- ✅ Provides actionable error messages
- ✅ Shows what IS available for debugging
- ✅ Runs automatically during code generation

### 3. Integration into Quality-Driven Workflow

**File**: `src/agents/developer/developer.py:287-304`

Added validation step after LLM generation, before file writing:

```python
# Generate implementation using LLM
response = self.llm_wrapper.call_llm(prompt)
implementation = self.llm_wrapper.parse_implementation(response.content)

# Validate import consistency before writing files
validation_result = self._validate_import_consistency(implementation)

if not validation_result['valid']:
    self._log_warning("⚠️ Import consistency issues detected:")
    for issue in validation_result['issues']:
        self._log_warning(f"  {issue}")

    # Log available exports for debugging
    self._log_info("📋 Module exports detected:")
    for module, exports in validation_result['module_exports'].items():
        self._log_info(f"  {module}: {', '.join(exports)}")

    # Note: Still write files but flag for ValidationStage to catch
    self._log_warning("⚠️ Files will be written but may fail validation tests")
else:
    self._log_info("✅ Import consistency validation passed")

# Write files
files_written = self.file_manager.write_implementation_files(implementation, output_dir)
```

**Workflow:**
1. LLM generates code
2. **NEW:** Validate imports/exports
3. Log any issues found
4. Write files (so ValidationStage can still test)
5. ValidationStage catches any remaining bugs

**Benefits:**
- ✅ Early warning system before validation tests run
- ✅ Detailed debugging information in logs
- ✅ Helps identify root cause of test failures
- ✅ Non-blocking - allows ValidationStage final say

## Expected Impact

### Before Improvements
```
[03:59:08] ⚠️ developer-a: BLOCKED (exit_code=2)
[03:59:09] ⚠️ developer-b: BLOCKED (exit_code=2)
❌ ValidationStage: FAILED
```

### After Improvements
```
[HH:MM:SS] ℹ️ ✅ Import consistency validation passed
[HH:MM:SS] ✅ developer-a: APPROVED (exit_code=0)
[HH:MM:SS] ✅ developer-b: APPROVED (exit_code=0)
✅ ValidationStage: PASSED
```

## Testing Strategy

### 1. Unit Test for Validation Function

```python
def test_validate_import_consistency_catches_mismatch():
    """Test that validation catches import/export mismatches"""
    code = {
        'implementation_files': [
            {'path': 'database/__init__.py', 'content': 'def get_user(): pass'},
            {'path': 'auth/user.py', 'content': 'from database import get_user, validate_password'}
        ],
        'test_files': []
    }

    validator = Developer(...)
    result = validator._validate_import_consistency(code)

    assert not result['valid']
    assert 'validate_password' in result['issues'][0]
```

### 2. Integration Test with Full Workflow

Run complete pipeline with improved prompts and validation:
```bash
python3 src/artemis_orchestrator.py --card-id card-test-ssd-simple --full
```

Verify:
- ✅ Import validation runs
- ✅ Issues are logged if found
- ✅ Code still reaches ValidationStage
- ✅ Improved prompt reduces errors

### 3. Regression Test

Re-run previous failing case to confirm improvement:
```bash
# Previous run: Both developers BLOCKED
# New run: Should show import validation warnings but potentially better code
```

## Monitoring & Metrics

Track these metrics to measure improvement:

1. **Import Validation Pass Rate**
   - % of generations passing import validation
   - Target: >80% after improvements

2. **ValidationStage Pass Rate**
   - % of developers passing ValidationStage
   - Baseline: 0% (both BLOCKED)
   - Target: >50% improvement

3. **Test Failure Root Causes**
   - Track what types of errors remain
   - ImportError should decrease significantly
   - Other errors (logic bugs, etc.) may remain

## Future Enhancements

### Short Term
1. Add retry with feedback if validation fails
2. Attempt to auto-fix simple import mismatches
3. Track validation metrics in logs

### Medium Term
1. Add type consistency validation (function signatures match calls)
2. Check for unused imports/exports
3. Validate async/await usage consistency

### Long Term
1. Use validation results to improve LLM prompts dynamically
2. Build library of correct patterns from successful generations
3. Implement semantic validation (logic correctness, not just syntax)

## Related Documentation

- Validation Testing: `docs/validation_testing.md`
- Test Runner Fix: ValidationStage BLOCKED error resolution
- Code Standards: `docs/coding_standards.md`

## Rollout Plan

1. ✅ **Phase 1**: Implement validation (DONE)
2. ✅ **Phase 2**: Run test demo to verify improvements (DONE - validation working!)
3. ✅ **Phase 3**: Fix relative import resolution and export detection (DONE)
4. ⏳ **Phase 4**: Run demo with refined validation
5. ⏳ **Phase 5**: Monitor metrics over multiple runs
6. ⏳ **Phase 6**: Iterate on prompt based on common failures
7. ⏳ **Phase 7**: Add auto-fix for simple cases

## Refinements Applied (Phase 3)

After initial testing, we discovered and fixed two critical bugs in import validation:

### Bug 1: Relative Import Resolution
**Problem**: Validation couldn't resolve relative imports like `from .database import X`

**Fix** (src/agents/developer/developer.py:647-660):
```python
# Resolve relative imports
if node.level > 0:  # Relative import (from .module or from ..module)
    if node.level == 1 and import_module:
        # from .database import X -> resolve to current package
        resolved_module = f"{current_dir}.{import_module}" if current_dir else import_module
    elif node.level == 1 and not import_module:
        # from . import X -> resolve to current package
        resolved_module = current_dir if current_dir else None
```

### Bug 2: Export Detection
**Problem**: Was detecting all variables (like `users = {}`) as exports instead of just functions/classes

**Fix** (src/agents/developer/developer.py:604-619):
```python
# Walk AST and collect only module-level definitions
for node in tree.body:  # Only top-level, not nested
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        exports.add(node.name)
    elif isinstance(node, ast.ClassDef):
        exports.add(node.name)
    elif isinstance(node, ast.ImportFrom):
        # Track re-exports in __init__.py
        if path.endswith('__init__.py'):
            for alias in node.names:
                if alias.name != '*':
                    exports.add(alias.asname if alias.asname else alias.name)
```

### Bug 3: __init__.py Re-exports
**Problem**: Didn't track what __init__.py files re-export from submodules

**Fix**: Now tracks ImportFrom statements in __init__.py files as exports

## Success Criteria

✅ Import validation runs on every code generation
⏳ ValidationStage pass rate improves by >30%
⏳ Import-related errors decrease by >50%
⏳ Developer logs show validation warnings before tests run
⏳ Zero regressions in existing functionality

## Conclusion

These improvements add two layers of quality control:

1. **Explicit Prompting**: Tell LLM exactly what consistency means
2. **Automated Validation**: Catch issues before they reach tests

The combination should significantly improve code generation quality while maintaining our robust validation safety net. The ValidationStage remains the final arbiter - these improvements help catch issues earlier and provide better debugging information.
