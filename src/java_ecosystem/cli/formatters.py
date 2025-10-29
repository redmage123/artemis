from artemis_logger import get_logger
logger = get_logger('formatters')
'\nWHY: Format CLI output for analysis, build, and test results\nRESPONSIBILITY: Convert data structures to human-readable or JSON output\nPATTERNS: Visitor (data formatting), Template Method (output templates)\n\nFormatters provide clean separation between data and presentation.\n'
import json
from typing import Any

def print_analysis(analysis: Any, as_json: bool=False) -> None:
    """
    Print formatted analysis results.

    WHY: Single place for analysis output formatting (DRY).

    Args:
        analysis: JavaEcosystemAnalysis object
        as_json: Whether to output as JSON
    """
    if as_json:
        
        logger.log(json.dumps(analysis.summary, indent=2), 'INFO')
        return
    _print_table('Java Ecosystem Analysis', analysis.summary)

def print_build_result(result: Any, skip_tests: bool) -> None:
    """
    Print formatted build results.

    WHY: Single place for build output formatting (DRY).

    Args:
        result: Build result object
        skip_tests: Whether tests were skipped
    """
    status = 'SUCCESS' if result.success else 'FAILURE'
    data = {'Build Result': status, 'Duration': f'{result.duration:.2f}s', 'Exit Code': result.exit_code}
    if not skip_tests and hasattr(result, 'tests_run'):
        data['Tests'] = f'{result.tests_passed}/{result.tests_run} passed'
    _print_table(f'Build Result: {status}', data)

def print_test_result(result: Any) -> None:
    """
    Print formatted test results.

    WHY: Single place for test output formatting (DRY).

    Args:
        result: Test result object
    """
    status = 'SUCCESS' if result.success else 'FAILURE'
    data = {'Tests Run': result.tests_run, 'Passed': result.tests_passed, 'Failed': result.tests_failed, 'Duration': f'{result.duration:.2f}s'}
    _print_table(f'Test Result: {status}', data)

def _print_table(title: str, data: dict) -> None:
    """
    Print a formatted table with title and data.

    WHY: DRY - single table formatting template.

    Args:
        title: Table title
        data: Dictionary of key-value pairs to display
    """
    separator = '=' * 60
    
    logger.log(f'\n{separator}', 'INFO')
    
    logger.log(title, 'INFO')
    
    logger.log(separator, 'INFO')
    for key, value in data.items():
        if isinstance(key, str) and isinstance(value, (str, int, float)):
            
            logger.log(f'{key:25} {value}', 'INFO')
        else:
            
            logger.log(f'{key} {value}', 'INFO')
    
    logger.log(f'{separator}\n', 'INFO')