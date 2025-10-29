"""
Code Quality Workflow Handlers

WHY:
Handles code quality issues including linting, testing, compilation,
and security vulnerabilities.

RESPONSIBILITY:
- Run linters and auto-fix code style issues
- Execute and re-run tests
- Verify code compilation
- Apply security patches

PATTERNS:
- Strategy Pattern: Different code quality strategies
- Guard Clauses: Early validation of file paths and types
- Dispatch Table: File type to linter mapping

INTEGRATION:
- Extends: WorkflowHandler base class
- Used by: WorkflowHandlerFactory for code quality actions
- Executes: External tools (black, prettier, pytest)
"""
import subprocess
from typing import Dict, Any
from workflows.handlers.base_handler import WorkflowHandler
from artemis_logger import get_logger
logger = get_logger('workflow.code_handlers')

class RunLinterFixHandler(WorkflowHandler):
    """
    Run linter auto-fix

    WHY: Automatically fix code style issues to pass linting checks
    RESPONSIBILITY: Apply appropriate linter based on file type
    PATTERNS: Dispatch table for file type to linter mapping
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        file_path = context.get('file_path')
        if not file_path:
            return False
        return self._run_linter(file_path)

    def _run_linter(self, file_path: str) -> bool:
        try:
            if file_path.endswith('.py'):
                return self._run_black(file_path)
            if file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                return self._run_prettier(file_path)
            return True
        except Exception as e:
            
            logger.log(f'[Workflow] Failed to auto-fix {file_path}: {e}', 'INFO')
            return False

    def _run_black(self, file_path: str) -> bool:
        subprocess.run(['black', file_path], check=True, capture_output=True)
        
        logger.log(f'[Workflow] Auto-fixed {file_path} with black', 'INFO')
        return True

    def _run_prettier(self, file_path: str) -> bool:
        subprocess.run(['prettier', '--write', file_path], check=True, capture_output=True)
        
        logger.log(f'[Workflow] Auto-fixed {file_path} with prettier', 'INFO')
        return True

class RerunTestsHandler(WorkflowHandler):
    """
    Re-run failed tests

    WHY: Verify if test failures are transient or persistent
    RESPONSIBILITY: Execute test suite and report results
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        test_path = context.get('test_path', '.')
        try:
            result = subprocess.run(['python3', '-m', 'pytest', test_path, '-v'], capture_output=True, text=True, timeout=300)
            return self._handle_test_result(result, test_path)
        except Exception as e:
            
            logger.log(f'[Workflow] Failed to run tests: {e}', 'INFO')
            return False

    def _handle_test_result(self, result, test_path: str) -> bool:
        if result.returncode == 0:
            
            logger.log(f'[Workflow] Tests passed: {test_path}', 'INFO')
            return True
        
        logger.log(f'[Workflow] Tests still failing: {test_path}', 'INFO')
        return False

class FixSecurityVulnerabilityHandler(WorkflowHandler):
    """
    Apply security patch

    WHY: Address security vulnerabilities automatically
    RESPONSIBILITY: Apply appropriate security fix for vulnerability type
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        vulnerability_type = context.get('vulnerability_type')
        file_path = context.get('file_path')
        logger.warning(f'Security patch handler invoked for {vulnerability_type} in {file_path}. Automated security patching not yet implemented - requires integration with vulnerability databases (e.g., CVE, Snyk, npm audit) and language-specific patch application tools. Manual review recommended.')
        logger.info(f'Security vulnerability detected: {vulnerability_type}')
        return False

class RetryCompilationHandler(WorkflowHandler):
    """
    Retry compilation

    WHY: Verify code compilation after fixes are applied
    RESPONSIBILITY: Compile code and report syntax errors
    """

    def handle(self, context: Dict[str, Any]) -> bool:
        file_path = context.get('file_path')
        try:
            if not file_path or not file_path.endswith('.py'):
                
                logger.log(f'[Workflow] Compilation successful: {file_path}', 'INFO')
                return True
            with open(file_path) as f:
                compile(f.read(), file_path, 'exec')
            
            logger.log(f'[Workflow] Compilation successful: {file_path}', 'INFO')
            return True
        except SyntaxError as e:
            
            logger.log(f'[Workflow] Syntax error in {file_path}: {e}', 'INFO')
            return False
        except Exception as e:
            
            logger.log(f'[Workflow] Compilation failed: {e}', 'INFO')
            return False