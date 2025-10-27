# Validation Stage - Notebook Task Guidance

## Overview

The ValidationStage automatically detects the type of deliverable and applies appropriate validation:

- **Notebook Tasks** (`.ipynb` files): Structural validation, not pytest
- **Code Tasks** (Python modules): pytest unit/integration tests

## Notebook Task Detection

ValidationStage detects notebook tasks by:
1. Scanning developer output directory for `**/*.ipynb` files
2. If notebooks found → use notebook validation
3. If no notebooks → use standard pytest validation

## Notebook Validation Process

### What Gets Validated

1. **File Existence**: Check that .ipynb files were created
2. **JSON Structure**: Validate notebook is valid JSON
3. **Required Fields**: Ensure 'cells' key exists in notebook
4. **Cell Count**: Report number of cells (for quality assessment)

### What Does NOT Get Validated

- ❌ **NO pytest tests** - Notebooks don't need unit tests
- ❌ **NO code execution** - Cells are not executed (can be added later)
- ❌ **NO import resolution** - src/ directory modules not required

### Exit Codes

- **0**: All notebooks valid (APPROVED)
- **1**: One or more notebooks invalid (BLOCKED)

## Developer Guidance for Notebook Tasks

### What Developers Should Create

For tasks requiring Jupyter notebooks:

```
developer-{name}/
├── notebooks/                    # ✅ Create notebooks here
│   ├── feature_demo.ipynb
│   └── analysis.ipynb
├── src/                          # ⚠️ Optional - only if needed
│   └── helper_module.py          # Support code (if any)
└── tests/                        # ❌ NOT REQUIRED for notebooks
```

### What Developers Should NOT Create

For notebook tasks:
- ❌ Don't create pytest tests expecting Python modules
- ❌ Don't create tests that import non-existent modules
- ❌ Don't worry about PYTHONPATH for notebook tasks

### Example: Valid Notebook Task Response

```json
{
  "approach": "Create slide-based Jupyter notebook demo",
  "implementation": {
    "filename": "notebooks/artemis_demo.ipynb",
    "content": "<notebook JSON>"
  },
  "tests": null,
  "explanation": "Created notebook with slide metadata for presentation"
}
```

## When Tests ARE Required

Tests are required for:
- Python modules/packages
- CLI tools
- Web services
- Libraries

Tests are NOT required for:
- Documentation notebooks
- Demo notebooks
- Analysis notebooks
- Tutorial notebooks

## Implementation Details

### ValidationStage._validate_developer()

```python
def _validate_developer(self, dev_name: str, card_id: str = None) -> Dict:
    developer_output = Path(get_developer_output_path(dev_name))

    # Auto-detect notebook task
    notebooks = list(developer_output.glob("**/*.ipynb"))

    if notebooks:
        # Notebook validation: structural checks only
        status, test_results = self._validate_notebooks(notebooks)
    else:
        # Standard validation: pytest with PYTHONPATH setup
        test_path = get_developer_tests_path(dev_name)
        test_results = self.test_runner.run_tests(test_path)
        status = "APPROVED" if test_results['exit_code'] == 0 else "BLOCKED"

    return {"developer": dev_name, "status": status, "test_results": test_results}
```

### TestRunner PYTHONPATH Setup

For code tasks with tests, TestRunner automatically:
1. Detects `src/` directory in developer output
2. Adds it to PYTHONPATH before running pytest
3. Allows tests to import modules from `src/`

```python
# TestRunner._setup_pythonpath()
# Automatically adds: developer-b/src/ to PYTHONPATH
# So tests can do: from my_module import MyClass
```

## Task Type Detection

### Indicators of Notebook Tasks

Keywords in task description:
- "Jupyter notebook"
- "notebook demo"
- "slide presentation"
- "analysis notebook"
- "tutorial notebook"

Expected deliverable:
- `.ipynb` file(s)
- Visualization-focused
- Demonstration-focused

### Indicators of Code Tasks

Keywords in task description:
- "implement class"
- "create module"
- "build API"
- "develop service"

Expected deliverable:
- `.py` file(s)
- Unit tests
- Integration tests

## Best Practices

### For Developers

1. **Read task carefully** - Identify if output is notebook or code
2. **Create appropriate structure** - notebooks/ for .ipynb, src/ for .py
3. **Don't over-engineer** - Notebooks don't need elaborate test suites
4. **Focus on deliverable** - Make notebook content excellent

### For Validation Stage

1. **Auto-detect task type** - Don't require manual configuration
2. **Fail fast** - Clear error messages for validation failures
3. **Log what's validated** - Show which notebooks/tests were checked
4. **Be lenient for notebooks** - Structure validation only, not execution

## Future Enhancements

Potential additions to notebook validation:

1. **Cell Execution** - Run `jupyter nbconvert --execute`
2. **Output Validation** - Check that cells produce expected outputs
3. **Metadata Validation** - Verify slide tags, cell types
4. **Link Checking** - Validate markdown links work
5. **Image Validation** - Check embedded images exist

## Summary

**Key Principle**: Validation matches the deliverable type.

- Notebooks → Structural validation
- Code → Test execution
- Auto-detection prevents configuration errors
- Clear logging shows what was validated
