#!/usr/bin/env python3
"""
LLM Validation Awareness Prompts

WHY: Inform LLMs about validation pipeline and code standards so they can generate better code
RESPONSIBILITY: Generate prompts that explain validation expectations to LLMs
PATTERNS: Template Method, Strategy

This module creates prompts that:
1. Explain the anti-hallucination validation pipeline
2. Describe code standards enforcement (no nested ifs, guard clauses)
3. Set expectations for code quality
4. Provide examples of acceptable patterns

The LLM, knowing it will be validated, can proactively generate better code.

Example:
    from validation.llm_validation_prompts import generate_validation_aware_prompt

    # Add validation awareness to any LLM prompt
    prompt = generate_validation_aware_prompt(
        base_prompt="Generate a function to process user data",
        validation_strategy=strategy,
        include_code_standards=True
    )
"""

from typing import Optional, List

from artemis_exceptions import (
    PipelineValidationError,
    wrap_exception,
)
from validation import ValidationStrategy


def generate_validation_aware_prompt(
    base_prompt: str,
    validation_strategy: Optional[ValidationStrategy] = None,
    include_code_standards: bool = True,
    include_anti_hallucination_info: bool = True,
    task_context: Optional[str] = None
) -> str:
    """
    Generate LLM prompt with validation pipeline awareness.

    WHY: LLM that knows about validation can generate better code proactively
    RESPONSIBILITY: Combine base prompt with validation expectations

    Args:
        base_prompt: The original prompt for code generation
        validation_strategy: Optional strategy from orchestrator
        include_code_standards: Include code standards expectations
        include_anti_hallucination_info: Include validation pipeline info
        task_context: Optional context about the task

    Returns:
        Enhanced prompt with validation awareness

    Raises:
        PipelineValidationError: If prompt generation fails

    Example:
        prompt = generate_validation_aware_prompt(
            base_prompt="Create an authentication function",
            validation_strategy=strategy,
            include_code_standards=True
        )
    """
    try:
        sections = [base_prompt]

        # Add validation pipeline awareness
        if include_anti_hallucination_info:
            validation_section = _generate_validation_pipeline_section(validation_strategy)
            sections.append(validation_section)

        # Add code standards awareness
        if include_code_standards:
            standards_section = _generate_code_standards_section()
            sections.append(standards_section)

        # Add task context if provided
        if task_context:
            sections.append(f"\n## Task Context\n{task_context}")

        return "\n\n".join(sections)

    except PipelineValidationError:
        raise
    except Exception as e:
        raise wrap_exception(
            e,
            PipelineValidationError,
            "Failed to generate validation-aware prompt",
            {
                "base_prompt_length": len(base_prompt),
                "has_strategy": validation_strategy is not None,
                "include_standards": include_code_standards
            }
        )


def _generate_validation_pipeline_section(strategy: Optional[ValidationStrategy]) -> str:
    """
    Generate section explaining validation pipeline to LLM.

    WHY: LLM awareness of validation improves first-attempt quality
    RESPONSIBILITY: Explain what validation checks will be performed
    """
    if strategy:
        techniques_str = ", ".join(strategy.techniques)
        profile = strategy.profile.value.upper()
        reduction = strategy.expected_reduction

        return f"""## IMPORTANT: Validation Pipeline Awareness

Your generated code will undergo {profile} validation with the following techniques:
{techniques_str}

Expected hallucination reduction: {reduction:.1%}

This means your code will be checked for:
- Logical correctness and completeness
- Type safety and null pointer safety
- Edge case handling
- Proper error handling
- Adherence to specifications
- No hallucinated functions or imports
- Correct use of APIs and libraries

To pass validation on the first attempt:
1. Only use functions and imports that actually exist
2. Handle all edge cases explicitly
3. Include proper error handling
4. Follow the exact requirements
5. Do not assume functionality that wasn't specified
6. Use guard clauses for early returns (no deeply nested ifs)

If validation fails, you will be asked to regenerate the code with specific feedback.
Maximize first-attempt quality to avoid regeneration cycles."""

    # Generic validation awareness (no strategy provided)
    return """## IMPORTANT: Validation Pipeline Awareness

Your generated code will undergo multi-layer validation including:
- Static analysis for common errors
- Property-based testing for edge cases
- Self-critique for logical correctness
- RAG-enhanced validation against known patterns

To pass validation:
1. Only use functions and imports that exist in the specified language/framework
2. Handle all edge cases and error conditions
3. Follow exact requirements - do not hallucinate features
4. Use guard clauses and early returns (avoid nested ifs)
5. Include proper type hints and documentation

Generate complete, correct code that will pass validation on first attempt."""


def _generate_code_standards_section() -> str:
    """
    Generate section explaining code standards scanner to LLM.

    WHY: LLM awareness of scanner prevents violations
    RESPONSIBILITY: Explain specific code patterns to use/avoid
    """
    return """## CRITICAL: Code Standards Scanner

Your code will be automatically scanned for these violations:

VIOLATIONS TO AVOID:
1. Nested If Statements (depth > 1)
   ❌ BAD:
   ```python
   if condition1:
       if condition2:
           if condition3:
               do_something()
   ```

   ✓ GOOD (use guard clauses):
   ```python
   if not condition1:
       return
   if not condition2:
       return
   if not condition3:
       return
   do_something()
   ```

2. Elif Chains (3+ branches)
   ❌ BAD:
   ```python
   if x == 1:
       handle_one()
   elif x == 2:
       handle_two()
   elif x == 3:
       handle_three()
   elif x == 4:
       handle_four()
   ```

   ✓ GOOD (use dispatch table or guard clauses):
   ```python
   handlers = {
       1: handle_one,
       2: handle_two,
       3: handle_three,
       4: handle_four
   }
   handler = handlers.get(x)
   if handler:
       handler()
   ```

REQUIRED PATTERNS:
- Use guard clauses for early returns
- Prefer flat code structure over nesting
- Use dispatch tables/dictionaries for multi-branch logic
- Extract complex conditions into well-named functions
- Fail fast with early validation

The scanner has ZERO tolerance for these violations. Your code will be rejected
if it contains nested ifs or long elif chains. Design your code to be flat and
readable from the start."""


def generate_code_review_prompt(
    code_to_review: str,
    review_checklist: Optional[List[str]] = None,
    validation_strategy: Optional[ValidationStrategy] = None
) -> str:
    """
    Generate prompt for LLM code review with validation awareness.

    WHY: Code review needs to check for same issues as validation
    RESPONSIBILITY: Create review prompt aligned with validation criteria

    Args:
        code_to_review: Code to be reviewed
        review_checklist: Optional specific items to check
        validation_strategy: Optional strategy for review depth

    Returns:
        Code review prompt with validation alignment
    """
    checklist_items = review_checklist or [
        "No nested if statements (use guard clauses)",
        "No elif chains with 3+ branches (use dispatch tables)",
        "No hallucinated functions or imports",
        "Proper error handling",
        "Edge case coverage",
        "Type safety",
        "Following exact requirements"
    ]

    checklist_str = "\n".join(f"- {item}" for item in checklist_items)

    if validation_strategy:
        profile = validation_strategy.profile.value.upper()
        techniques_str = ", ".join(validation_strategy.techniques)

        return f"""## Code Review Task ({profile} Level)

Review the following code with {profile} scrutiny.

Validation techniques that will be applied: {techniques_str}

### Code to Review:
```
{code_to_review}
```

### Review Checklist:
{checklist_str}

### Instructions:
1. Check each item in the checklist
2. Identify any violations of code standards (nested ifs, elif chains)
3. Look for hallucinated functionality
4. Verify edge case handling
5. Assess adherence to requirements

Provide:
- List of issues found (if any)
- Severity of each issue (critical/major/minor)
- Specific line numbers
- Suggested fixes for each issue

If no issues found, state "Code passes review."
"""

    # Generic review prompt
    return f"""## Code Review Task

Review the following code for quality and correctness.

### Code to Review:
```
{code_to_review}
```

### Review Checklist:
{checklist_str}

Provide detailed feedback on any issues found, with severity and suggested fixes.
"""


def generate_refactoring_prompt(
    code_to_refactor: str,
    violations: List[str],
    validation_strategy: Optional[ValidationStrategy] = None
) -> str:
    """
    Generate prompt for LLM to refactor code to fix violations.

    WHY: When code has violations, guide LLM to fix them correctly
    RESPONSIBILITY: Create refactoring prompt with specific violation fixes

    Args:
        code_to_refactor: Code with violations
        violations: List of violations found
        validation_strategy: Optional strategy for refactoring approach

    Returns:
        Refactoring prompt with fix instructions
    """
    violations_str = "\n".join(f"- {v}" for v in violations)

    return f"""## Code Refactoring Task

The following code has code standards violations that must be fixed:

### Violations Found:
{violations_str}

### Code to Refactor:
```
{code_to_refactor}
```

### Refactoring Requirements:
1. Fix ALL code standards violations
2. Maintain exact same functionality
3. Use guard clauses instead of nested ifs
4. Use dispatch tables instead of long elif chains
5. Preserve all edge case handling
6. Keep or improve error handling
7. Maintain type safety

### Patterns to Use:
- Guard clauses for early returns
- Dispatch dictionaries for multi-branch logic
- Well-named helper functions for complex conditions
- Flat code structure (no nesting)

Provide the refactored code that:
- Has zero code standards violations
- Maintains identical functionality
- Is more readable and maintainable

IMPORTANT: The refactored code will be re-scanned. It must pass with zero violations.
"""


def get_validation_summary_for_llm(strategy: ValidationStrategy) -> str:
    """
    Get concise validation summary to include in LLM prompts.

    WHY: Brief summary is useful for inline inclusion
    RESPONSIBILITY: Return 1-2 sentence validation description

    Args:
        strategy: Validation strategy from orchestrator

    Returns:
        Concise validation summary
    """
    profile = strategy.profile.value
    techniques_count = len(strategy.techniques)
    reduction = strategy.expected_reduction

    return (
        f"This code will undergo {profile} validation "
        f"({techniques_count} techniques, {reduction:.0%} hallucination reduction). "
        f"Ensure code is complete, correct, and follows coding standards (no nested ifs/elif chains)."
    )
