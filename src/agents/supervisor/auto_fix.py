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

            # Create prompt for LLM
            prompt = f"""You are a Python code debugging expert. Analyze this error and provide a fix.

**Error Details:**
- Type: {error_type}
- Message: {error_message}
- File: {file_path}
- Line: {line_number}

**Problematic Line:**
```python
{problem_line.strip()}
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
{{
    "reasoning": "Brief explanation of the error and fix",
    "fixed_line": "The complete fixed line of code with proper indentation"
}}

Respond ONLY with valid JSON, no other text."""

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
        # TODO: Implement regex-based fallback fixes for common patterns
        # Examples: KeyError → .get(), TypeError → type checks, etc.
        if self.verbose:
            print(f"[AutoFix] ⚠️  Regex-based fallback not yet implemented")
        return None

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
