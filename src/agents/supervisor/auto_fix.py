from artemis_logger import get_logger
logger = get_logger('auto_fix')
'\nModule: agents/supervisor/auto_fix.py\n\nWHY: LLM-powered automatic error fixing through source code modification.\nRESPONSIBILITY: Detect, analyze, and fix errors in source code using LLM intelligence.\nPATTERNS: Strategy Pattern (fix strategies), Guard Clauses (early returns).\n\nThis module handles:\n- LLM client setup for auto-fixing\n- Preflight validation with auto-fix\n- LLM-powered error analysis and fixes\n- Backup creation and safe file modifications\n- Regex-based fallback fixes\n\nEXTRACTED FROM: supervisor_agent.py (lines 406-2239)\n'
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
    prompt_file = Path(__file__).parent.parent.parent / 'prompts' / 'supervisor_auto_fix_prompt.md'
    if not prompt_file.exists():
        return '# Supervisor Auto-Fix: Python Code Debugging Expert\n\nYou are a Python code debugging expert. Analyze this error and provide a fix.\n\n**Error Details:**\n- Type: {error_type}\n- Message: {error_message}\n- File: {file_path}\n- Line: {line_number}\n\n**Problematic Line:**\n```python\n{problem_line}\n```\n\n**Surrounding Context:**\n```python\n{context_code}\n```\n\n**Task:**\nProvide a fixed version of the problematic line that resolves the {error_type} error. The fix should:\n1. Be defensive (use .get() for dict access, check types, handle None, etc.)\n2. Maintain the same functionality\n3. Include sensible defaults\n4. Be a drop-in replacement (same indentation, same line)\n\n**Response Format (JSON):**\n```json\n{\n    "reasoning": "Brief explanation of the error and fix",\n    "fixed_line": "The complete fixed line of code with proper indentation"\n}\n```\n\nRespond ONLY with valid JSON, no other text.'
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()

class AutoFixEngine:
    """
    LLM-powered auto-fix engine for runtime errors

    WHY: Centralize auto-fix logic with clean interfaces
    PATTERNS: Strategy Pattern (LLM vs Regex), Guard Clauses
    """

    def __init__(self, llm_client=None, verbose: bool=False, llm_model: str='gpt-4', llm_temperature: float=0.2):
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
                
                logger.log(f'[AutoFix] LLM-based auto-fix enabled', 'INFO')
        except Exception:
            if self.verbose:
                
                logger.log(f'[AutoFix] LLM not available - auto-fix disabled', 'INFO')
        return (llm_client, auto_fix_enabled)

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
        if preflight_results['passed'] and preflight_results['high_count'] > 0:
            if self.verbose:
                
                logger.log(f"[AutoFix] ⚠️  Preflight warnings: {preflight_results['high_count']} high-priority issues", 'INFO')
            return
        if preflight_results['passed'] and preflight_results['high_count'] == 0:
            if self.verbose:
                
                logger.log('[AutoFix] ✅ Preflight validation passed', 'INFO')
            return
        if self.verbose:
            
            logger.log(f"[AutoFix] ❌ Found {preflight_results['critical_count']} critical issues", 'INFO')
        if not auto_fix_enabled or preflight_results['critical_count'] == 0:
            if self.verbose:
                preflight.print_report()
            raise RuntimeError(f"Preflight validation failed: {preflight_results['critical_count']} critical issues found (auto-fix disabled)")
        if self.verbose:
            
            logger.log(f'[AutoFix] Attempting auto-fix...', 'INFO')
        all_fixed = preflight.auto_fix_syntax_errors()
        if not all_fixed:
            if self.verbose:
                preflight.print_report()
            raise RuntimeError(f"Preflight validation failed: Could not auto-fix all {preflight_results['critical_count']} critical issues")
        if self.verbose:
            
            logger.log(f'[AutoFix] ✅ All syntax errors fixed automatically!', 'INFO')
            
            logger.log(f'[AutoFix] 🔄 Restarting Artemis to apply fixes...', 'INFO')
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def auto_fix_error(self, error: Exception, traceback_info: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
            
            logger.log(f'[AutoFix] 🧠 LLM auto-fixing {error_type}: {error_message}', 'INFO')
        try:
            file_info = self._extract_file_location(traceback_info)
            if not file_info:
                return self._fallback_regex_fix(error, traceback_info, context)
            file_path, line_number = file_info
            if self.verbose:
                
                logger.log(f'[AutoFix] 📝 Found error in {file_path}:{line_number}', 'INFO')
            file_context = self._read_file_context(file_path, line_number)
            if not file_context:
                return None
            all_lines, context_lines, problem_line = file_context
            if self.verbose:
                
                logger.log(f'[AutoFix] 📄 Problem line: {problem_line.strip()}', 'INFO')
            llm_fix = self._suggest_fix_with_llm(error_type=error_type, error_message=error_message, file_path=file_path, line_number=line_number, problem_line=problem_line, context_lines=context_lines, context=context)
            if not llm_fix or not llm_fix.get('success'):
                if self.verbose:
                    
                    logger.log(f'[AutoFix] ⚠️  LLM fix failed, trying regex fallback...', 'INFO')
                return self._fallback_regex_fix(error, traceback_info, context)
            return self._apply_fix_to_file(file_path=file_path, line_number=line_number, all_lines=all_lines, problem_line=problem_line, fixed_line=llm_fix['fixed_line'], error_type=error_type, error_message=error_message, llm_reasoning=llm_fix.get('reasoning', ''))
        except Exception as e:
            if self.verbose:
                
                logger.log(f'[AutoFix] ❌ LLM auto-fix failed: {e}', 'INFO')
            return self._fallback_regex_fix(error, traceback_info, context)

    def _extract_file_location(self, traceback_info: str) -> Optional[Tuple[str, int]]:
        """
        Extract file path and line number from traceback

        Args:
            traceback_info: Traceback string

        Returns:
            Tuple of (file_path, line_number) or None
        """
        file_match = re.search('File "([^"]+)", line (\\d+)', traceback_info)
        if not file_match:
            if self.verbose:
                
                logger.log(f'[AutoFix] ⚠️  Could not extract file path from traceback', 'INFO')
            return None
        file_path = file_match.group(1)
        line_number = int(file_match.group(2))
        return (file_path, line_number)

    def _read_file_context(self, file_path: str, line_number: int, context_size: int=10) -> Optional[Tuple[list, list, str]]:
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
            if line_number > len(all_lines):
                if self.verbose:
                    
                    logger.log(f'[AutoFix] ⚠️  Line number out of range', 'INFO')
                return None
            context_start = max(0, line_number - context_size)
            context_end = min(len(all_lines), line_number + context_size)
            context_lines = all_lines[context_start:context_end]
            problem_line = all_lines[line_number - 1]
            return (all_lines, context_lines, problem_line)
        except Exception as e:
            if self.verbose:
                
                logger.log(f'[AutoFix] ❌ Failed to read file: {e}', 'INFO')
            return None

    def _suggest_fix_with_llm(self, error_type: str, error_message: str, file_path: str, line_number: int, problem_line: str, context_lines: list, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
        if not self.llm_client:
            if self.verbose:
                
                logger.log(f'[AutoFix] ⚠️  LLM client not available', 'INFO')
            return None
        try:
            context_code = ''.join(context_lines)
            prompt_template = _load_auto_fix_prompt()
            prompt = prompt_template.format(error_type=error_type, error_message=error_message, file_path=file_path, line_number=line_number, problem_line=problem_line.strip(), context_code=context_code)
            if self.verbose:
                
                logger.log(f'[AutoFix] 💬 Consulting LLM for fix suggestion...', 'INFO')
            response = self.llm_client.chat(model=self.llm_model, messages=[{'role': 'system', 'content': 'You are a Python debugging expert. Respond only with valid JSON.'}, {'role': 'user', 'content': prompt}], temperature=self.llm_temperature)
            fix_data = self._parse_llm_response(response)
            if not fix_data or 'fixed_line' not in fix_data:
                return None
            if self.verbose:
                
                logger.log(f'[AutoFix] ✅ LLM suggested fix', 'INFO')
                
                logger.log(f"[AutoFix]    Reasoning: {fix_data.get('reasoning', 'N/A')}", 'INFO')
                
                logger.log(f"[AutoFix]    Fixed: {fix_data['fixed_line']}", 'INFO')
            return {'success': True, 'fixed_line': fix_data['fixed_line'], 'reasoning': fix_data.get('reasoning', '')}
        except Exception as e:
            if self.verbose:
                
                logger.log(f'[AutoFix] ❌ LLM suggestion failed: {e}', 'INFO')
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
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            return json.loads(response_text)
        except Exception as e:
            if self.verbose:
                
                logger.log(f'[AutoFix] ⚠️  Failed to parse LLM response: {e}', 'INFO')
            return None

    def _apply_fix_to_file(self, file_path: str, line_number: int, all_lines: list, problem_line: str, fixed_line: str, error_type: str, error_message: str, llm_reasoning: str) -> Dict[str, Any]:
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
        backup_path = file_path + '.backup'
        with open(backup_path, 'w') as f:
            f.writelines(all_lines)
        if self.verbose:
            
            logger.log(f'[AutoFix] 💾 Created backup: {backup_path}', 'INFO')
        all_lines[line_number - 1] = fixed_line + '\n' if not fixed_line.endswith('\n') else fixed_line
        with open(file_path, 'w') as f:
            f.writelines(all_lines)
        if self.verbose:
            
            logger.log(f'[AutoFix] ✅ LLM auto-fixed {file_path}', 'INFO')
        return {'success': True, 'file_path': file_path, 'line_number': line_number, 'error_type': error_type, 'error_message': error_message, 'original_line': problem_line.strip(), 'fixed_line': fixed_line.strip(), 'backup_path': backup_path, 'llm_reasoning': llm_reasoning, 'message': f'LLM automatically fixed {error_type} in {file_path}:{line_number}'}

    def _fallback_regex_fix(self, error: Exception, traceback_info: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
            
            logger.log(f'[AutoFix] 🔧 Attempting regex-based fallback fix for {error_type}', 'INFO')
        file_info = self._extract_file_location(traceback_info)
        if not file_info:
            if self.verbose:
                
                logger.log(f'[AutoFix] ⚠️  Could not extract file location for regex fix', 'INFO')
            return None
        file_path, line_number = file_info
        file_context = self._read_file_context(file_path, line_number)
        if not file_context:
            return None
        all_lines, context_lines, problem_line = file_context
        fixed_line = self._apply_regex_fallback_fixes(error, problem_line, error_type)
        if not fixed_line:
            if self.verbose:
                
                logger.log(f'[AutoFix] ⚠️  No regex pattern matched for {error_type}', 'INFO')
            return None
        return self._apply_fix_to_file(file_path=file_path, line_number=line_number, all_lines=all_lines, problem_line=problem_line, fixed_line=fixed_line, error_type=error_type, error_message=str(error), llm_reasoning=f'Regex-based automatic fix for {error_type}')

    def _apply_regex_fallback_fixes(self, error: Exception, problem_line: str, error_type: str) -> Optional[str]:
        """
        Apply regex-based fixes for common Python error patterns

        Args:
            error: Exception that occurred
            problem_line: The problematic line of code
            error_type: Type of error (KeyError, AttributeError, TypeError)

        Returns:
            Fixed line of code or None if no pattern matches
        """
        fix_methods = {'KeyError': self._fix_key_error, 'AttributeError': self._fix_attribute_error, 'TypeError': self._fix_type_error}
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
        error_msg = str(error).strip('\'"')
        fixed_line = self._try_simple_dict_access_fix(error_msg, problem_line)
        if fixed_line:
            return fixed_line
        return self._try_variable_dict_access_fix(problem_line)

    def _try_simple_dict_access_fix(self, error_msg: str, problem_line: str) -> Optional[str]:
        """Try to fix simple dict[key] access."""
        pattern = '(\\w+)\\[(["\\\']?)' + re.escape(error_msg) + '\\2\\]'
        match = re.search(pattern, problem_line)
        if not match:
            return None
        dict_name = match.group(1)
        quote = match.group(2) or "'"
        replacement = f'{dict_name}.get({quote}{error_msg}{quote}, None)'
        fixed_line = re.sub(pattern, replacement, problem_line, count=1)
        if self.verbose:
            
            logger.log(f'[AutoFix] 🔧 KeyError fix: {dict_name}[{quote}{error_msg}{quote}] → {replacement}', 'INFO')
        return fixed_line

    def _try_variable_dict_access_fix(self, problem_line: str) -> Optional[str]:
        """Try to fix dict[variable] access."""
        pattern = '(\\w+)\\[([^\\]]+)\\](?!\\s*=)'
        match = re.search(pattern, problem_line)
        if not match:
            return None
        dict_name = match.group(1)
        key_expr = match.group(2)
        replacement = f'{dict_name}.get({key_expr}, None)'
        fixed_line = re.sub(pattern, replacement, problem_line, count=1)
        if self.verbose:
            
            logger.log(f'[AutoFix] 🔧 KeyError fix: {dict_name}[{key_expr}] → {replacement}', 'INFO')
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
        attr_match = re.search("has no attribute '(\\w+)'", str(error))
        if not attr_match:
            return None
        attr_name = attr_match.group(1)
        pattern = '(\\w+)\\.' + re.escape(attr_name) + '\\b'
        match = re.search(pattern, problem_line)
        if not match:
            return None
        obj_name = match.group(1)
        fixed_line = self._create_attribute_fix(problem_line, obj_name, attr_name)
        if self.verbose and fixed_line:
            
            logger.log(f'[AutoFix] 🔧 AttributeError fix: Added safety check for {obj_name}.{attr_name}', 'INFO')
        return fixed_line

    @staticmethod
    def _create_attribute_fix(problem_line: str, obj_name: str, attr_name: str) -> str:
        """Create appropriate fix for attribute access."""
        indent = len(problem_line) - len(problem_line.lstrip())
        indent_str = problem_line[:indent]
        stripped_line = problem_line.strip()
        is_assignment = '=' in stripped_line and (not stripped_line.startswith('return'))
        is_return = stripped_line.startswith('return')
        if is_assignment or is_return:
            return f"{indent_str}{stripped_line.rstrip()} if hasattr({obj_name}, '{attr_name}') else None\n"
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
        fixed_line = self._fix_nonetype_iterable(error_msg, problem_line)
        if fixed_line:
            return fixed_line
        fixed_line = self._fix_unsupported_operand(error_msg, problem_line)
        if fixed_line:
            return fixed_line
        return self._fix_not_callable(error_msg, problem_line)

    def _fix_nonetype_iterable(self, error_msg: str, problem_line: str) -> Optional[str]:
        """Fix 'NoneType' object is not iterable errors."""
        if "'nonetype' object is not iterable" not in error_msg and 'cannot unpack non-iterable' not in error_msg:
            return None
        for_match = re.search('for\\s+\\w+\\s+in\\s+(\\w+)', problem_line)
        if not for_match:
            return None
        iterable_name = for_match.group(1)
        fixed_line = problem_line.replace(f'in {iterable_name}', f'in ({iterable_name} or [])', 1)
        if self.verbose:
            
            logger.log(f'[AutoFix] 🔧 TypeError fix: Added None check for iteration over {iterable_name}', 'INFO')
        return fixed_line

    def _fix_unsupported_operand(self, error_msg: str, problem_line: str) -> Optional[str]:
        """Fix unsupported operand type errors."""
        if 'unsupported operand type' not in error_msg or 'nonetype' not in error_msg:
            return None
        stripped_line = problem_line.strip()
        op_match = re.search('(\\w+)\\s*([+\\-*/])\\s*(\\w+)', stripped_line)
        if not op_match:
            return None
        left_operand = op_match.group(1)
        operator = op_match.group(2)
        right_operand = op_match.group(3)
        if 'str' in error_msg:
            default_left = f"({left_operand} or '')"
            default_right = f"({right_operand} or '')"
        else:
            default_left = f'({left_operand} or 0)'
            default_right = f'({right_operand} or 0)'
        original_expr = f'{left_operand} {operator} {right_operand}'
        fixed_expr = f'{default_left} {operator} {default_right}'
        fixed_line = problem_line.replace(original_expr, fixed_expr, 1)
        if self.verbose:
            
            logger.log(f'[AutoFix] 🔧 TypeError fix: Added None protection for {operator} operation', 'INFO')
        return fixed_line

    def _fix_not_callable(self, error_msg: str, problem_line: str) -> Optional[str]:
        """Fix 'object is not callable' errors."""
        if 'object is not callable' not in error_msg:
            return None
        stripped_line = problem_line.strip()
        call_match = re.search('(\\w+)\\(', stripped_line)
        if not call_match:
            return None
        func_name = call_match.group(1)
        indent = len(problem_line) - len(problem_line.lstrip())
        indent_str = problem_line[:indent]
        if self.verbose:
            
            logger.log(f"[AutoFix] ⚠️  TypeError 'not callable': {func_name} may be shadowed or not a function", 'INFO')
            
            logger.log(f'[AutoFix]    This requires manual inspection - attempting type check', 'INFO')
        if stripped_line.startswith('return'):
            return f'{indent_str}{stripped_line.rstrip()} if callable({func_name}) else None\n'
        original_call = re.search('(\\w+\\([^)]*\\))', stripped_line)
        if not original_call:
            return None
        call_expr = original_call.group(1)
        replacement = f'({call_expr} if callable({func_name}) else None)'
        fixed_line = problem_line.replace(call_expr, replacement, 1)
        if self.verbose:
            
            logger.log(f'[AutoFix] 🔧 TypeError fix: Added callable check for {func_name}', 'INFO')
        return fixed_line

    def print_fix_success(self, fix_result: Dict[str, Any]) -> None:
        """
        Print LLM auto-fix success details

        Args:
            fix_result: Fix result dictionary
        """
        
        logger.log(f'[AutoFix] ✅ LLM AUTO-FIX SUCCESS!', 'INFO')
        
        logger.log(f"[AutoFix]    File: {fix_result['file_path']}:{fix_result['line_number']}", 'INFO')
        
        logger.log(f"[AutoFix]    Error: {fix_result['error_type']}", 'INFO')
        
        logger.log(f"[AutoFix]    Before: {fix_result['original_line']}", 'INFO')
        
        logger.log(f"[AutoFix]    After:  {fix_result['fixed_line']}", 'INFO')
        
        logger.log(f"[AutoFix]    Backup: {fix_result['backup_path']}", 'INFO')
        if 'llm_reasoning' in fix_result:
            
            logger.log(f"[AutoFix]    LLM Reasoning: {fix_result['llm_reasoning']}", 'INFO')
__all__ = ['AutoFixEngine']