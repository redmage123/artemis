from artemis_logger import get_logger
logger = get_logger('preflight_validator')
'\nPreflight Validator - Static code validation before pipeline execution\n\nThis module validates Python files for syntax errors, import issues, and other\nstatic problems BEFORE the pipeline starts. This allows the supervisor to detect\nand potentially fix issues that would otherwise cause import-time failures.\n'
import sys
import os
import py_compile
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class ValidationIssue:
    """Represents a validation issue found during preflight checks"""
    file_path: str
    issue_type: str
    severity: str
    message: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None

class PreflightValidator:
    """
    Validates Python files before pipeline execution.

    Checks:
    - Syntax errors (py_compile)
    - Import errors
    - Missing required files
    - File permissions

    Can auto-fix syntax errors using LLM.
    """

    def __init__(self, verbose: bool=True, llm_client=None, auto_fix: bool=False):
        self.verbose = verbose
        self.issues: List[ValidationIssue] = []
        self.llm_client = llm_client
        self.auto_fix = auto_fix
        self.fixes_applied: List[Dict] = []

    def validate_all(self, base_path: str='.') -> Dict:
        """
        Run all preflight validation checks.

        Returns:
            dict: {
                "passed": bool,
                "critical_count": int,
                "high_count": int,
                "issues": List[ValidationIssue]
            }
        """
        self.issues = []
        agile_dir = Path(base_path)
        python_files = list(agile_dir.glob('*.py'))
        if self.verbose:
            
            logger.log(f'\n🔍 Preflight Validation - Checking {len(python_files)} Python files...', 'INFO')
        for py_file in python_files:
            self._check_syntax(str(py_file))
        self._check_critical_files(base_path)
        self._test_imports(base_path)
        self._validate_signatures(base_path)
        critical_count = sum((1 for issue in self.issues if issue.severity == 'critical'))
        high_count = sum((1 for issue in self.issues if issue.severity == 'high'))
        passed = critical_count == 0
        if self.verbose:
            if passed:
                
                logger.log(f'✅ Preflight validation PASSED - {len(self.issues)} non-critical issues found', 'INFO')
            else:
                
                logger.log(f'❌ Preflight validation FAILED - {critical_count} critical issues found', 'INFO')
        return {'passed': passed, 'critical_count': critical_count, 'high_count': high_count, 'medium_count': sum((1 for issue in self.issues if issue.severity == 'medium')), 'low_count': sum((1 for issue in self.issues if issue.severity == 'low')), 'total_issues': len(self.issues), 'issues': self.issues}

    def _check_syntax(self, file_path: str) -> bool:
        """Check if a Python file has valid syntax"""
        try:
            py_compile.compile(file_path, doraise=True)
            if self.verbose:
                
                logger.log(f'  ✅ {Path(file_path).name}', 'INFO')
            return True
        except SyntaxError as e:
            self.issues.append(ValidationIssue(file_path=file_path, issue_type='syntax_error', severity='critical', message=f'Syntax error: {e.msg}', line_number=e.lineno, suggestion=f'Fix syntax error at line {e.lineno}: {e.text}'))
            if self.verbose:
                
                logger.log(f'  ❌ {Path(file_path).name} - Syntax error at line {e.lineno}', 'INFO')
            return False
        except Exception as e:
            self.issues.append(ValidationIssue(file_path=file_path, issue_type='syntax_error', severity='critical', message=f'Compilation error: {str(e)}', suggestion='Review the file for syntax issues'))
            if self.verbose:
                
                logger.log(f'  ❌ {Path(file_path).name} - Compilation error: {e}', 'INFO')
            return False

    def _check_critical_files(self, base_path: str):
        """Check that critical files exist and are readable"""
        critical_files = ['artemis_orchestrator.py', 'artemis_stages.py', 'pipeline_strategies.py', 'kanban_manager.py', 'rag_agent.py']
        for filename in critical_files:
            self._validate_critical_file(base_path, filename)

    def _validate_critical_file(self, base_path: str, filename: str):
        """Validate a single critical file exists and is readable"""
        file_path = Path(base_path) / filename
        if not file_path.exists():
            self.issues.append(ValidationIssue(file_path=str(file_path), issue_type='missing_file', severity='critical', message=f'Critical file not found: {filename}', suggestion=f'Ensure {filename} exists in the agile directory'))
            return
        if not os.access(file_path, os.R_OK):
            self.issues.append(ValidationIssue(file_path=str(file_path), issue_type='permission_error', severity='high', message=f'Critical file not readable: {filename}', suggestion=f'Check file permissions for {filename}'))

    def _test_imports(self, base_path: str):
        """
        Test that main entry point can be imported (catches circular imports early)

        WHY: Import errors and circular dependencies only manifest at runtime.
        Testing the import chain early catches these before they cause failures.
        """
        if self.verbose:
            
            logger.log('  🔍 Testing imports...', 'INFO')
        import subprocess
        entry_points = ['artemis_orchestrator', 'artemis_stages', 'pipeline_strategies']
        for module_name in entry_points:
            self._test_single_import(module_name, base_path, subprocess)

    def _test_single_import(self, module_name: str, base_path: str, subprocess):
        """Test import for a single module (extracted to avoid nesting)"""
        module_file = Path(base_path) / f'{module_name}.py'
        if not module_file.exists():
            return
        try:
            result = subprocess.run([sys.executable, '-c', f"import sys; sys.path.insert(0, '{base_path}'); import {module_name}"], cwd=base_path, capture_output=True, timeout=10, text=True)
            if result.returncode == 0:
                self._log_import_success(module_name)
                return
            self._handle_import_failure(module_name, result.stderr.strip(), str(module_file))
        except subprocess.TimeoutExpired:
            self._handle_import_timeout(module_name, str(module_file))
        except Exception as e:
            self._log_import_exception(module_name, e)

    def _handle_import_failure(self, module_name: str, error_msg: str, module_file: str):
        """Handle import failure by creating appropriate issue"""
        is_circular = 'circular import' in error_msg.lower() or 'partially initialized module' in error_msg.lower()
        if is_circular:
            self.issues.append(ValidationIssue(file_path=module_file, issue_type='circular_import', severity='critical', message=f'Circular import detected in {module_name}', suggestion=f'Review import statements in {module_name} and related modules'))
        else:
            self.issues.append(ValidationIssue(file_path=module_file, issue_type='import_error', severity='critical', message=f'Failed to import {module_name}: {error_msg[:200]}', suggestion=f'Fix import errors in {module_name}'))
        self._log_import_failure(module_name)

    def _handle_import_timeout(self, module_name: str, module_file: str):
        """Handle import timeout"""
        self.issues.append(ValidationIssue(file_path=module_file, issue_type='import_timeout', severity='high', message=f'Import timeout for {module_name} (possible infinite loop)', suggestion=f'Check for initialization loops in {module_name}'))
        if self.verbose:
            
            logger.log(f'    ⏱️  Import timeout: {module_name}', 'INFO')

    def _log_import_success(self, module_name: str):
        """Log successful import"""
        if self.verbose:
            
            logger.log(f'    ✅ Import OK: {module_name}', 'INFO')

    def _log_import_failure(self, module_name: str):
        """Log import failure"""
        if self.verbose:
            
            logger.log(f'    ❌ Import failed: {module_name}', 'INFO')

    def _log_import_exception(self, module_name: str, exception: Exception):
        """Log import test exception"""
        if self.verbose:
            
            logger.log(f'    ⚠️  Could not test import for {module_name}: {exception}', 'INFO')

    def _validate_signatures(self, base_path: str):
        """
        Validate function call signatures to catch parameter mismatches

        WHY: Parameter mismatches (wrong args, unknown kwargs) cause TypeErrors at runtime.
        Static analysis can catch many of these errors before execution.
        """
        if self.verbose:
            
            logger.log('  🔍 Validating function signatures...', 'INFO')
        try:
            from signature_validator import SignatureValidator
            sig_validator = SignatureValidator(verbose=False)
            python_files = list(Path(base_path).glob('*.py'))
            self._validate_all_signatures(sig_validator, python_files)
            self._log_signature_results()
        except ImportError:
            self._log_signature_import_error()
        except Exception as e:
            self._log_signature_validation_error(e)

    def _validate_all_signatures(self, sig_validator, python_files):
        """Validate signatures for all Python files (extracted to avoid nesting)"""
        for py_file in python_files:
            sig_issues = sig_validator.validate_file(str(py_file))
            self._convert_signature_issues(sig_issues)

    def _convert_signature_issues(self, sig_issues):
        """Convert SignatureIssue objects to ValidationIssue objects"""
        for sig_issue in sig_issues:
            validation_severity = 'critical' if sig_issue.severity == 'critical' else 'medium'
            self.issues.append(ValidationIssue(file_path=sig_issue.file_path, issue_type='signature_mismatch', severity=validation_severity, message=sig_issue.message, line_number=sig_issue.line_number, suggestion=f'Check function call to {sig_issue.function_name}() at line {sig_issue.line_number}'))

    def _log_signature_results(self):
        """Log signature validation results (avoids nested if)"""
        if not self.verbose:
            return
        sig_count = sum((1 for issue in self.issues if issue.issue_type == 'signature_mismatch'))
        if sig_count == 0:
            
            logger.log(f'    ✅ No signature issues found', 'INFO')
            return
        
        logger.log(f'    ⚠️  Found {sig_count} signature issues', 'INFO')

    def _log_signature_import_error(self):
        """Log SignatureValidator import error"""
        if self.verbose:
            
            logger.log(f'    ⚠️  SignatureValidator not available - skipping signature checks', 'INFO')

    def _log_signature_validation_error(self, exception: Exception):
        """Log signature validation exception"""
        if self.verbose:
            
            logger.log(f'    ⚠️  Error during signature validation: {exception}', 'INFO')

    def auto_fix_syntax_errors(self) -> bool:
        """
        Automatically fix syntax errors using LLM.

        Returns:
            bool: True if all critical syntax errors were fixed
        """
        if not self.llm_client or not self.auto_fix:
            return False
        critical_syntax_errors = [issue for issue in self.issues if issue.severity == 'critical' and issue.issue_type == 'syntax_error']
        if not critical_syntax_errors:
            return True
        if self.verbose:
            
            logger.log(f'\n🔧 Auto-fixing {len(critical_syntax_errors)} syntax errors...', 'INFO')
        all_fixed = True
        for issue in critical_syntax_errors:
            fixed = self._attempt_fix_with_error_handling(issue)
            if not fixed:
                all_fixed = False
        return all_fixed

    def _attempt_fix_with_error_handling(self, issue: ValidationIssue) -> bool:
        """Attempt to fix an issue and handle errors"""
        try:
            fixed = self._fix_syntax_error_with_llm(issue)
            self._record_fix_result(issue, fixed)
            return fixed
        except Exception as e:
            self._handle_fix_error(issue, e)
            return False

    def _record_fix_result(self, issue: ValidationIssue, fixed: bool):
        """Record the result of a fix attempt"""
        if fixed:
            self.fixes_applied.append({'file': issue.file_path, 'issue': issue.message, 'fixed': True})
            if self.verbose:
                
                logger.log(f'  ✅ Fixed: {Path(issue.file_path).name}', 'INFO')
            return
        if self.verbose:
            
            logger.log(f'  ❌ Could not fix: {Path(issue.file_path).name}', 'INFO')

    def _handle_fix_error(self, issue: ValidationIssue, error: Exception):
        """Handle errors during fix attempts"""
        if self.verbose:
            
            logger.log(f'  ❌ Error fixing {Path(issue.file_path).name}: {error}', 'INFO')

    def _fix_syntax_error_with_llm(self, issue: ValidationIssue) -> bool:
        """Use LLM to fix a specific syntax error"""
        with open(issue.file_path, 'r') as f:
            broken_code = f.read()
        prompt = f'Fix this Python syntax error:\n\nFile: {issue.file_path}\nError: {issue.message}\nLine: {issue.line_number}\n\nBROKEN CODE:\n```python\n{broken_code}\n```\n\nReturn ONLY the corrected Python code, nothing else. No explanations, no markdown formatting.\nThe code must be syntactically valid Python that fixes the error while preserving all functionality.'
        try:
            response = self.llm_client.generate(prompt=prompt, max_tokens=4000, temperature=0.1)
            fixed_code = response.strip()
            fixed_code = self._strip_markdown_formatting(fixed_code)
            if not self._validate_fixed_code(fixed_code, issue.file_path):
                return False
            with open(issue.file_path, 'w') as f:
                f.write(fixed_code)
            return True
        except Exception as e:
            if self.verbose:
                
                logger.log(f'    LLM fix failed: {e}', 'INFO')
            return False

    def _strip_markdown_formatting(self, code: str) -> str:
        """Remove markdown code block formatting from code"""
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]
        return code.strip()

    def _validate_fixed_code(self, fixed_code: str, file_path: str) -> bool:
        """Validate that fixed code compiles without syntax errors"""
        try:
            compile(fixed_code, file_path, 'exec')
            return True
        except SyntaxError:
            if self.verbose:
                
                logger.log(f'    LLM fix still has syntax errors, skipping', 'INFO')
            return False

    def print_report(self):
        """Print a detailed validation report"""
        
        logger.log('\n' + '=' * 70, 'INFO')
        
        logger.log('🔍 PREFLIGHT VALIDATION REPORT', 'INFO')
        
        logger.log('=' * 70, 'INFO')
        if len(self.issues) == 0:
            
            logger.log('\n✅ All checks passed - No issues found!', 'INFO')
            
            logger.log('\n' + '=' * 70, 'INFO')
            return
        from collections import defaultdict
        issues_by_severity = defaultdict(list)
        for issue in self.issues:
            issues_by_severity[issue.severity].append(issue)
        critical = issues_by_severity['critical']
        high = issues_by_severity['high']
        medium = issues_by_severity['medium']
        low = issues_by_severity['low']
        
        logger.log(f'\n📊 Summary:', 'INFO')
        
        logger.log(f'  🔴 Critical: {len(critical)}', 'INFO')
        
        logger.log(f'  🟠 High: {len(high)}', 'INFO')
        
        logger.log(f'  🟡 Medium: {len(medium)}', 'INFO')
        
        logger.log(f'  🟢 Low: {len(low)}', 'INFO')
        if critical:
            
            logger.log(f'\n🔴 CRITICAL ISSUES (must fix before running):', 'INFO')
            for i, issue in enumerate(critical, 1):
                self._print_issue_details(i, issue, include_line_number=True)
        if high:
            
            logger.log(f'\n🟠 HIGH PRIORITY ISSUES:', 'INFO')
            for i, issue in enumerate(high, 1):
                self._print_issue_details(i, issue, include_line_number=False)
        self._print_fixes_applied()
        
        logger.log('\n' + '=' * 70, 'INFO')

    def _print_issue_details(self, index: int, issue: ValidationIssue, include_line_number: bool=True):
        """Print details for a single issue"""
        
        logger.log(f'\n{index}. [{issue.issue_type}] {Path(issue.file_path).name}', 'INFO')
        
        logger.log(f'   {issue.message}', 'INFO')
        if include_line_number and issue.line_number:
            
            logger.log(f'   Line: {issue.line_number}', 'INFO')
        if issue.suggestion:
            
            logger.log(f'   💡 {issue.suggestion}', 'INFO')

    def _print_fixes_applied(self):
        """Print details of automatic fixes that were applied"""
        if not self.fixes_applied:
            return
        
        logger.log(f'\n🔧 AUTOMATIC FIXES APPLIED:', 'INFO')
        for i, fix in enumerate(self.fixes_applied, 1):
            
            logger.log(f"\n{i}. {Path(fix['file']).name}", 'INFO')
            
            logger.log(f"   Issue: {fix['issue']}", 'INFO')
            
            logger.log(f"   Status: {('✅ Fixed' if fix['fixed'] else '❌ Failed')}", 'INFO')

def run_preflight_validation(base_path: str='.agents/agile', verbose: bool=True) -> Dict:
    """
    Convenience function to run preflight validation.

    Args:
        base_path: Directory containing Python files to validate
        verbose: Print progress messages

    Returns:
        Validation results dictionary
    """
    validator = PreflightValidator(verbose=verbose)
    results = validator.validate_all(base_path)
    if verbose:
        validator.print_report()
    return results
if __name__ == '__main__':
    import sys
    base_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    results = run_preflight_validation(base_path, verbose=True)
    sys.exit(0 if results['passed'] else 1)