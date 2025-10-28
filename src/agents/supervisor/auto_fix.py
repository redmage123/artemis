"""
Module: agents/supervisor/auto_fix.py

WHY: LLM-powered automatic error fixing through source code modification.
RESPONSIBILITY: Detect, analyze, and fix errors in source code using LLM intelligence.
PATTERNS: Strategy Pattern (fix strategies), Guard Clauses (early returns).

This module handles:
- LLM client setup for auto-fixing
- Preflight validation with auto-fix
- LLM-powered error analysis and fixes
- Backup creation and safe file modifications
- Regex-based fallback fixes

EXTRACTED FROM: supervisor_agent.py (lines 406-2239)
"""

from typing import Dict, Any, Optional, Tuple
import re
import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _load_auto_fix_prompt() -> str:
    """
    Load auto-fix prompt from dedicated file.

    WHY: Centralize prompts in files for easy maintenance
    PATTERNS: Guard clauses, early returns

    Returns:
        Auto-fix prompt template
    """
    prompt_file = Path(__file__).parent.parent.parent / "prompts" / "supervisor_auto_fix_prompt.md"

    # Guard: File doesn't exist
    if not prompt_file.exists():
        # Fallback to embedded prompt for backward compatibility
        return """# Supervisor Auto-Fix: Python Code Debugging Expert

You are a Python code debugging expert. Analyze this error and provide a fix.

**Error Details:**
- Type: {error_type}
- Message: {error_message}
- File: {file_path}
- Line: {line_number}

**Problematic Line:**
```python
{problem_line}
```

**Surrounding Context:**
```python
{context_code}
```

**Task:**
Provide a fixed version of the problematic line that resolves the {error_type} error. The fix should:
1. Be defensive (use .get() for dict access, check types, handle None, etc.)
2. Maintain the same functionality
3. Include sensible defaults
4. Be a drop-in replacement (same indentation, same line)

**Response Format (JSON):**
```json
{
    "reasoning": "Brief explanation of the error and fix",
    "fixed_line": "The complete fixed line of code with proper indentation"
}
```

Respond ONLY with valid JSON, no other text."""

    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


class AutoFixEngine:
    """
    LLM-powered auto-fix engine for runtime errors

    WHY: Centralize auto-fix logic with clean interfaces
    PATTERNS: Strategy Pattern (LLM vs Regex), Guard Clauses
    """

    def __init__(self, llm_client=None, verbose: bool = False, llm_model: str = "gpt-4", llm_temperature: float = 0.2):
        """
        Initialize auto-fix engine

        Args:
            llm_client: LLM client for intelligent fixes (optional)
            verbose: Enable verbose logging
            llm_model: LLM model to use for fixes
            llm_temperature: Temperature for LLM calls
        """
        self.llm_client = llm_client
        self.verbose = verbose
        self.llm_model = llm_model
        self.llm_temperature = llm_temperature

    def setup_llm_for_autofix(self) -> Tuple[Optional[Any], bool]:
        """
        Setup LLM client for auto-fixing syntax errors

        Returns:
            Tuple of (llm_client, auto_fix_enabled)
        """
        from llm_client import LLMClientFactory

        llm_client = None
        auto_fix_enabled = False

        try:
            llm_client = LLMClientFactory.create()
            auto_fix_enabled = True
            if self.verbose:
                print(f"[AutoFix] LLM-based auto-fix enabled")
        except Exception:
            if self.verbose:
                print(f"[AutoFix] LLM not available - auto-fix disabled")

        return llm_client, auto_fix_enabled

    def handle_preflight_results(self, preflight, preflight_results: Dict, auto_fix_enabled: bool) -> None:
        """
        Handle preflight validation results with auto-fix if needed

        Args:
            preflight: Preflight validator instance
            preflight_results: Validation results
            auto_fix_enabled: Whether auto-fix is enabled

        Raises:
            RuntimeError: If validation fails and cannot be fixed
        """
        import os
        import sys

        # Guard clause: handle passed validation with warnings
        if preflight_results["passed"] and preflight_results["high_count"] > 0:
            if self.verbose:
                print(f"[AutoFix] ⚠️  Preflight warnings: {preflight_results['high_count']} high-priority issues")
            return

        # Guard clause: handle passed validation without warnings
        if preflight_results["passed"] and preflight_results["high_count"] == 0:
            if self.verbose:
                print("[AutoFix] ✅ Preflight validation passed")
            return

        # From here: preflight_results["passed"] is False

        # Failed - print critical count
        if self.verbose:
            print(f"[AutoFix] ❌ Found {preflight_results['critical_count']} critical issues")

        # Guard clause: cannot auto-fix
        if not auto_fix_enabled or preflight_results["critical_count"] == 0:
            if self.verbose:
                preflight.print_report()
            raise RuntimeError(
                f"Preflight validation failed: {preflight_results['critical_count']} "
                f"critical issues found (auto-fix disabled)"
            )

        if self.verbose:
            print(f"[AutoFix] Attempting auto-fix...")

        all_fixed = preflight.auto_fix_syntax_errors()

        # Guard clause: auto-fix failed
        if not all_fixed:
            if self.verbose:
                preflight.print_report()
            raise RuntimeError(
                f"Preflight validation failed: Could not auto-fix all {preflight_results['critical_count']} "
                f"critical issues"
            )

        if self.verbose:
            print(f"[AutoFix] ✅ All syntax errors fixed automatically!")
            print(f"[AutoFix] 🔄 Restarting Artemis to apply fixes...")

        # Re-exec the current process to restart with fixed code
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def auto_fix_error(
        self,
        error: Exception,
        traceback_info: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Use LLM to automatically analyze and fix errors by modifying source code

        Args:
            error: The exception that occurred
            traceback_info: Traceback string
            context: Execution context

        Returns:
            Fix result dict if successful, None otherwise
        """
        error_type = type(error).__name__
        error_message = str(error)

        if self.verbose:
            print(f"[AutoFix] 🧠 LLM auto-fixing {error_type}: {error_message}")

        try:
            # Extract file location from traceback
            file_info = self._extract_file_location(traceback_info)
            if not file_info:
                return self._fallback_regex_fix(error, traceback_info, context)

            file_path, line_number = file_info

            if self.verbose:
                print(f"[AutoFix] 📝 Found error in {file_path}:{line_number}")

            # Read source file with context
            file_context = self._read_file_context(file_path, line_number)
            if not file_context:
                return None

            all_lines, context_lines, problem_line = file_context

            if self.verbose:
                print(f"[AutoFix] 📄 Problem line: {problem_line.strip()}")

            # Try LLM-powered fix first
            llm_fix = self._suggest_fix_with_llm(
                error_type=error_type,
                error_message=error_message,
                file_path=file_path,
                line_number=line_number,
                problem_line=problem_line,
                context_lines=context_lines,
                context=context
            )

            # Guard: LLM fix failed
            if not llm_fix or not llm_fix.get("success"):
                if self.verbose:
                    print(f"[AutoFix] ⚠️  LLM fix failed, trying regex fallback...")
                return self._fallback_regex_fix(error, traceback_info, context)

            # Apply the LLM-suggested fix
            return self._apply_fix_to_file(
                file_path=file_path,
                line_number=line_number,
                all_lines=all_lines,
                problem_line=problem_line,
                fixed_line=llm_fix["fixed_line"],
                error_type=error_type,
                error_message=error_message,
                llm_reasoning=llm_fix.get("reasoning", "")
            )

        except Exception as e:
            if self.verbose:
                print(f"[AutoFix] ❌ LLM auto-fix failed: {e}")

            # Fallback to regex-based fix
            return self._fallback_regex_fix(error, traceback_info, context)

    def _extract_file_location(self, traceback_info: str) -> Optional[Tuple[str, int]]:
        """
        Extract file path and line number from traceback

        Args:
            traceback_info: Traceback string

        Returns:
            Tuple of (file_path, line_number) or None
        """
        file_match = re.search(r'File "([^"]+)", line (\d+)', traceback_info)
        if not file_match:
            if self.verbose:
                print(f"[AutoFix] ⚠️  Could not extract file path from traceback")
            return None

        file_path = file_match.group(1)
        line_number = int(file_match.group(2))

        return (file_path, line_number)

    def _read_file_context(
        self,
        file_path: str,
        line_number: int,
        context_size: int = 10
    ) -> Optional[Tuple[list, list, str]]:
        """
        Read source file with context around error line

        Args:
            file_path: Path to source file
            line_number: Line number with error (1-indexed)
            context_size: Number of lines before/after to include

        Returns:
            Tuple of (all_lines, context_lines, problem_line) or None
        """
        try:
            with open(file_path, 'r') as f:
                all_lines = f.readlines()

            # Guard: line number out of range
            if line_number > len(all_lines):
                if self.verbose:
                    print(f"[AutoFix] ⚠️  Line number out of range")
                return None

            # Get context lines
            context_start = max(0, line_number - context_size)
            context_end = min(len(all_lines), line_number + context_size)
            context_lines = all_lines[context_start:context_end]
            problem_line = all_lines[line_number - 1]

            return (all_lines, context_lines, problem_line)

        except Exception as e:
            if self.verbose:
                print(f"[AutoFix] ❌ Failed to read file: {e}")
            return None

    def _suggest_fix_with_llm(
        self,
        error_type: str,
        error_message: str,
        file_path: str,
        line_number: int,
        problem_line: str,
        context_lines: list,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Use LLM to suggest a fix for the error

        Args:
            error_type: Type of error (KeyError, TypeError, etc.)
            error_message: Error message
            file_path: Path to file with error
            line_number: Line number with error
            problem_line: The problematic line
            context_lines: Surrounding context lines
            context: Execution context

        Returns:
            Fix suggestion dict if successful, None otherwise
        """
        # Guard: LLM not available
        if not self.llm_client:
            if self.verbose:
                print(f"[AutoFix] ⚠️  LLM client not available")
            return None

        try:
            # Build context for LLM
            context_code = "".join(context_lines)

            # Load prompt from dedicated file and format with variables
            prompt_template = _load_auto_fix_prompt()
            prompt = prompt_template.format(
                error_type=error_type,
                error_message=error_message,
                file_path=file_path,
                line_number=line_number,
                problem_line=problem_line.strip(),
                context_code=context_code
            )

            if self.verbose:
                print(f"[AutoFix] 💬 Consulting LLM for fix suggestion...")

            # Call LLM
            response = self.llm_client.chat(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": "You are a Python debugging expert. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.llm_temperature
            )

            # Parse LLM response
            fix_data = self._parse_llm_response(response)

            # Guard: no fixed_line in response
            if not fix_data or "fixed_line" not in fix_data:
                return None

            if self.verbose:
                print(f"[AutoFix] ✅ LLM suggested fix")
                print(f"[AutoFix]    Reasoning: {fix_data.get('reasoning', 'N/A')}")
                print(f"[AutoFix]    Fixed: {fix_data['fixed_line']}")

            return {
                "success": True,
                "fixed_line": fix_data["fixed_line"],
                "reasoning": fix_data.get("reasoning", "")
            }

        except Exception as e:
            if self.verbose:
                print(f"[AutoFix] ❌ LLM suggestion failed: {e}")
            return None

    def _parse_llm_response(self, response) -> Optional[Dict[str, Any]]:
        """
        Parse LLM response and extract JSON

        Args:
            response: LLM API response

        Returns:
            Parsed JSON dict or None
        """
        try:
            response_text = response.choices[0].message.content.strip()

            # Extract JSON if wrapped in code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            return json.loads(response_text)

        except Exception as e:
            if self.verbose:
                print(f"[AutoFix] ⚠️  Failed to parse LLM response: {e}")
            return None

    def _apply_fix_to_file(
        self,
        file_path: str,
        line_number: int,
        all_lines: list,
        problem_line: str,
        fixed_line: str,
        error_type: str,
        error_message: str,
        llm_reasoning: str
    ) -> Dict[str, Any]:
        """
        Apply fix to source file with backup

        Args:
            file_path: Path to file
            line_number: Line number to fix (1-indexed)
            all_lines: All lines in file
            problem_line: Original problematic line
            fixed_line: Fixed line
            error_type: Type of error
            error_message: Error message
            llm_reasoning: LLM's reasoning for the fix

        Returns:
            Fix result dict
        """
        # Create backup
        backup_path = file_path + ".backup"
        with open(backup_path, 'w') as f:
            f.writelines(all_lines)

        if self.verbose:
            print(f"[AutoFix] 💾 Created backup: {backup_path}")

        # Write fixed version
        all_lines[line_number - 1] = fixed_line + "\n" if not fixed_line.endswith("\n") else fixed_line
        with open(file_path, 'w') as f:
            f.writelines(all_lines)

        if self.verbose:
            print(f"[AutoFix] ✅ LLM auto-fixed {file_path}")

        return {
            "success": True,
            "file_path": file_path,
            "line_number": line_number,
            "error_type": error_type,
            "error_message": error_message,
            "original_line": problem_line.strip(),
            "fixed_line": fixed_line.strip(),
            "backup_path": backup_path,
            "llm_reasoning": llm_reasoning,
            "message": f"LLM automatically fixed {error_type} in {file_path}:{line_number}"
        }

    def _fallback_regex_fix(
        self,
        error: Exception,
        traceback_info: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Fallback to regex-based fix when LLM is unavailable

        Args:
            error: Exception to fix
            traceback_info: Traceback information
            context: Execution context

        Returns:
            Fix result dict or None
        """
        error_type = type(error).__name__

        if self.verbose:
            print(f"[AutoFix] 🔧 Attempting regex-based fallback fix for {error_type}")

        # Extract file location from traceback
        file_info = self._extract_file_location(traceback_info)
        if not file_info:
            if self.verbose:
                print(f"[AutoFix] ⚠️  Could not extract file location for regex fix")
            return None

        file_path, line_number = file_info

        # Read source file with context
        file_context = self._read_file_context(file_path, line_number)
        if not file_context:
            return None

        all_lines, context_lines, problem_line = file_context

        # Apply regex-based fixes
        fixed_line = self._apply_regex_fallback_fixes(error, problem_line, error_type)

        if not fixed_line:
            if self.verbose:
                print(f"[AutoFix] ⚠️  No regex pattern matched for {error_type}")
            return None

        # Apply the fix to the file
        return self._apply_fix_to_file(
            file_path=file_path,
            line_number=line_number,
            all_lines=all_lines,
            problem_line=problem_line,
            fixed_line=fixed_line,
            error_type=error_type,
            error_message=str(error),
            llm_reasoning=f"Regex-based automatic fix for {error_type}"
        )

    def _apply_regex_fallback_fixes(
        self,
        error: Exception,
        problem_line: str,
        error_type: str
    ) -> Optional[str]:
        """
        Apply regex-based fixes for common Python error patterns

        Args:
            error: Exception that occurred
            problem_line: The problematic line of code
            error_type: Type of error (KeyError, AttributeError, TypeError)

        Returns:
            Fixed line of code or None if no pattern matches
        """
        # Dispatch table: error type → fix method
        fix_methods = {
            "KeyError": self._fix_key_error,
            "AttributeError": self._fix_attribute_error,
            "TypeError": self._fix_type_error,
        }

        # Guard: Unknown error type
        fix_method = fix_methods.get(error_type)
        if not fix_method:
            return None

        return fix_method(error, problem_line)

    def _fix_key_error(self, error: Exception, problem_line: str) -> Optional[str]:
        """
        Fix KeyError by replacing dict[key] with dict.get(key, default)

        Args:
            error: KeyError exception
            problem_line: Line with the error

        Returns:
            Fixed line or None
        """
        # Extract the missing key from error message
        error_msg = str(error).strip("'\"")

        # Try Pattern 1: Simple dict[key] access
        fixed_line = self._try_simple_dict_access_fix(error_msg, problem_line)
        if fixed_line:
            return fixed_line

        # Try Pattern 2: dict[variable] access
        return self._try_variable_dict_access_fix(problem_line)

    def _try_simple_dict_access_fix(self, error_msg: str, problem_line: str) -> Optional[str]:
        """Try to fix simple dict[key] access."""
        pattern = r'(\w+)\[(["\']?)' + re.escape(error_msg) + r'\2\]'
        match = re.search(pattern, problem_line)

        # Guard: No match
        if not match:
            return None

        dict_name = match.group(1)
        quote = match.group(2) or "'"
        replacement = f'{dict_name}.get({quote}{error_msg}{quote}, None)'
        fixed_line = re.sub(pattern, replacement, problem_line, count=1)

        if self.verbose:
            print(f"[AutoFix] 🔧 KeyError fix: {dict_name}[{quote}{error_msg}{quote}] → {replacement}")

        return fixed_line

    def _try_variable_dict_access_fix(self, problem_line: str) -> Optional[str]:
        """Try to fix dict[variable] access."""
        pattern = r'(\w+)\[([^\]]+)\](?!\s*=)'
        match = re.search(pattern, problem_line)

        # Guard: No match
        if not match:
            return None

        dict_name = match.group(1)
        key_expr = match.group(2)
        replacement = f'{dict_name}.get({key_expr}, None)'
        fixed_line = re.sub(pattern, replacement, problem_line, count=1)

        if self.verbose:
            print(f"[AutoFix] 🔧 KeyError fix: {dict_name}[{key_expr}] → {replacement}")

        return fixed_line

    def _fix_attribute_error(self, error: Exception, problem_line: str) -> Optional[str]:
        """
        Fix AttributeError by adding hasattr() checks

        Args:
            error: AttributeError exception
            problem_line: Line with the error

        Returns:
            Fixed line or None
        """
        # Guard: Extract attribute name
        attr_match = re.search(r"has no attribute '(\w+)'", str(error))
        if not attr_match:
            return None

        attr_name = attr_match.group(1)

        # Guard: Find object.attribute pattern
        pattern = r'(\w+)\.' + re.escape(attr_name) + r'\b'
        match = re.search(pattern, problem_line)
        if not match:
            return None

        obj_name = match.group(1)
        fixed_line = self._create_attribute_fix(problem_line, obj_name, attr_name)

        if self.verbose and fixed_line:
            print(f"[AutoFix] 🔧 AttributeError fix: Added safety check for {obj_name}.{attr_name}")

        return fixed_line

    @staticmethod
    def _create_attribute_fix(problem_line: str, obj_name: str, attr_name: str) -> str:
        """Create appropriate fix for attribute access."""
        indent = len(problem_line) - len(problem_line.lstrip())
        indent_str = problem_line[:indent]
        stripped_line = problem_line.strip()

        # Check for assignment or return statement
        is_assignment = '=' in stripped_line and not stripped_line.startswith('return')
        is_return = stripped_line.startswith('return')

        if is_assignment or is_return:
            # Add hasattr check
            return f"{indent_str}{stripped_line.rstrip()} if hasattr({obj_name}, '{attr_name}') else None\n"

        # Use getattr for other cases
        original_access = f'{obj_name}.{attr_name}'
        replacement = f"getattr({obj_name}, '{attr_name}', None)"
        return problem_line.replace(original_access, replacement, 1)

    def _fix_type_error(self, error: Exception, problem_line: str) -> Optional[str]:
        """
        Fix TypeError by adding type checking

        Args:
            error: TypeError exception
            problem_line: Line with the error

        Returns:
            Fixed line or None
        """
        error_msg = str(error).lower()

        # Try Pattern 1: NoneType is not iterable
        fixed_line = self._fix_nonetype_iterable(error_msg, problem_line)
        if fixed_line:
            return fixed_line

        # Try Pattern 2: unsupported operand type
        fixed_line = self._fix_unsupported_operand(error_msg, problem_line)
        if fixed_line:
            return fixed_line

        # Try Pattern 3: object is not callable
        return self._fix_not_callable(error_msg, problem_line)

    def _fix_nonetype_iterable(self, error_msg: str, problem_line: str) -> Optional[str]:
        """Fix 'NoneType' object is not iterable errors."""
        # Guard: Not a NoneType iterable error
        if "'nonetype' object is not iterable" not in error_msg and "cannot unpack non-iterable" not in error_msg:
            return None

        # Guard: No for loop pattern
        for_match = re.search(r'for\s+\w+\s+in\s+(\w+)', problem_line)
        if not for_match:
            return None

        iterable_name = for_match.group(1)
        fixed_line = problem_line.replace(
            f'in {iterable_name}',
            f'in ({iterable_name} or [])',
            1
        )

        if self.verbose:
            print(f"[AutoFix] 🔧 TypeError fix: Added None check for iteration over {iterable_name}")

        return fixed_line

    def _fix_unsupported_operand(self, error_msg: str, problem_line: str) -> Optional[str]:
        """Fix unsupported operand type errors."""
        # Guard: Not an unsupported operand error
        if "unsupported operand type" not in error_msg or "nonetype" not in error_msg:
            return None

        stripped_line = problem_line.strip()

        # Guard: No operation pattern
        op_match = re.search(r'(\w+)\s*([+\-*/])\s*(\w+)', stripped_line)
        if not op_match:
            return None

        left_operand = op_match.group(1)
        operator = op_match.group(2)
        right_operand = op_match.group(3)

        # Determine defaults based on error message
        if "str" in error_msg:
            default_left = f"({left_operand} or '')"
            default_right = f"({right_operand} or '')"
        else:
            default_left = f"({left_operand} or 0)"
            default_right = f"({right_operand} or 0)"

        original_expr = f'{left_operand} {operator} {right_operand}'
        fixed_expr = f'{default_left} {operator} {default_right}'
        fixed_line = problem_line.replace(original_expr, fixed_expr, 1)

        if self.verbose:
            print(f"[AutoFix] 🔧 TypeError fix: Added None protection for {operator} operation")

        return fixed_line

    def _fix_not_callable(self, error_msg: str, problem_line: str) -> Optional[str]:
        """Fix 'object is not callable' errors."""
        # Guard: Not a callable error
        if "object is not callable" not in error_msg:
            return None

        stripped_line = problem_line.strip()

        # Guard: No function call pattern
        call_match = re.search(r'(\w+)\(', stripped_line)
        if not call_match:
            return None

        func_name = call_match.group(1)
        indent = len(problem_line) - len(problem_line.lstrip())
        indent_str = problem_line[:indent]

        if self.verbose:
            print(f"[AutoFix] ⚠️  TypeError 'not callable': {func_name} may be shadowed or not a function")
            print(f"[AutoFix]    This requires manual inspection - attempting type check")

        # Handle return statements
        if stripped_line.startswith('return'):
            return f"{indent_str}{stripped_line.rstrip()} if callable({func_name}) else None\n"

        # Handle other cases
        original_call = re.search(r'(\w+\([^)]*\))', stripped_line)
        if not original_call:
            return None

        call_expr = original_call.group(1)
        replacement = f"({call_expr} if callable({func_name}) else None)"
        fixed_line = problem_line.replace(call_expr, replacement, 1)

        if self.verbose:
            print(f"[AutoFix] 🔧 TypeError fix: Added callable check for {func_name}")

        return fixed_line

    def print_fix_success(self, fix_result: Dict[str, Any]) -> None:
        """
        Print LLM auto-fix success details

        Args:
            fix_result: Fix result dictionary
        """
        print(f"[AutoFix] ✅ LLM AUTO-FIX SUCCESS!")
        print(f"[AutoFix]    File: {fix_result['file_path']}:{fix_result['line_number']}")
        print(f"[AutoFix]    Error: {fix_result['error_type']}")
        print(f"[AutoFix]    Before: {fix_result['original_line']}")
        print(f"[AutoFix]    After:  {fix_result['fixed_line']}")
        print(f"[AutoFix]    Backup: {fix_result['backup_path']}")
        if 'llm_reasoning' in fix_result:
            print(f"[AutoFix]    LLM Reasoning: {fix_result['llm_reasoning']}")


__all__ = [
    "AutoFixEngine"
]
