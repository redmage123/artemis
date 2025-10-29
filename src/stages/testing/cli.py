from artemis_logger import get_logger
logger = get_logger('cli')
'\nWHY: Command-line interface helpers for test runner\nRESPONSIBILITY: Format and display test results\nPATTERNS: Strategy Pattern for output formats\n\nThis module provides functions for formatting and displaying test results\nin different formats (JSON, text) suitable for CLI usage.\n'
import json
from typing import Optional
from stages.testing.models import TestResult

def print_test_results(result: TestResult, as_json: bool=False, verbose: bool=False) -> None:
    """
    WHY: Display test results to console
    RESPONSIBILITY: Choose and apply output format

    Args:
        result: TestResult to display
        as_json: Whether to output as JSON
        verbose: Whether to include verbose output
    """
    if as_json:
        print_json_results(result)
        return
    print_text_results(result, verbose)

def print_json_results(result: TestResult) -> None:
    """
    WHY: Output results in JSON format
    RESPONSIBILITY: Serialize result to JSON

    Args:
        result: TestResult to serialize
    """
    
    logger.log(json.dumps({'framework': result.framework, 'passed': result.passed, 'failed': result.failed, 'skipped': result.skipped, 'errors': result.errors, 'total': result.total, 'pass_rate': result.pass_rate, 'success': result.success, 'exit_code': result.exit_code, 'duration': result.duration}, indent=2), 'INFO')

def print_text_results(result: TestResult, verbose: bool=False) -> None:
    """
    WHY: Output results in formatted text
    RESPONSIBILITY: Format result as human-readable table

    Args:
        result: TestResult to format
        verbose: Whether to include test output
    """
    
    logger.log(f"\n{'=' * 60}", 'INFO')
    
    logger.log(f'Test Results ({result.framework})', 'INFO')
    
    logger.log(f"{'=' * 60}", 'INFO')
    
    logger.log(f'Total:     {result.total}', 'INFO')
    
    logger.log(f'Passed:    {result.passed}', 'INFO')
    
    logger.log(f'Failed:    {result.failed}', 'INFO')
    
    logger.log(f'Skipped:   {result.skipped}', 'INFO')
    
    logger.log(f'Errors:    {result.errors}', 'INFO')
    
    logger.log(f'Pass Rate: {result.pass_rate}%', 'INFO')
    
    logger.log(f'Duration:  {result.duration:.2f}s', 'INFO')
    
    logger.log(f"Status:    {('SUCCESS' if result.success else 'FAILURE')}", 'INFO')
    
    logger.log(f"{'=' * 60}\n", 'INFO')
    if verbose:
        
        logger.log('Test Output:', 'INFO')
        
        logger.log(result.output, 'INFO')