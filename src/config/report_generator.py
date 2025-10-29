from artemis_logger import get_logger
logger = get_logger('report_generator')
'\nConfiguration Validation Report Generator\n\nWHY: Handles generating and printing validation reports\n\nRESPONSIBILITY: Aggregate validation results and format reports\n\nPATTERNS: Pure functions for report generation\n'
from typing import List
from .models import ValidationResult, ValidationReport

def generate_report(results: List[ValidationResult]) -> ValidationReport:
    """
    Generate validation report from results

    WHY: Aggregates all validation results into comprehensive report
    PERFORMANCE: O(n) where n is number of results, using list comprehensions

    Args:
        results: List of validation results

    Returns:
        ValidationReport with aggregated statistics
    """
    errors = [r for r in results if not r.passed and r.severity == 'error']
    warnings = [r for r in results if not r.passed and r.severity == 'warning']
    passed = [r for r in results if r.passed]
    if errors:
        overall_status = 'fail'
    elif warnings:
        overall_status = 'warning'
    else:
        overall_status = 'pass'
    return ValidationReport(overall_status=overall_status, total_checks=len(results), passed=len(passed), warnings=len(warnings), errors=len(errors), results=results)

def print_report(report: ValidationReport) -> None:
    """
    Print validation report

    WHY: Provides human-readable summary of validation results
    PATTERNS: Strategy pattern for status messages
    PERFORMANCE: O(1) - simple string formatting

    Args:
        report: ValidationReport to print
    """
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('VALIDATION SUMMARY', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    
    logger.log(f'\nTotal checks: {report.total_checks}', 'INFO')
    
    logger.log(f'  Passed: {report.passed}', 'INFO')
    if report.warnings > 0:
        
        logger.log(f'  Warnings: {report.warnings}', 'INFO')
    if report.errors > 0:
        
        logger.log(f'  Errors: {report.errors}', 'INFO')
    status_messages = {'pass': ('\nAll validation checks passed!', 'Artemis is ready to run.'), 'warning': ('\nValidation completed with warnings', 'Artemis can run but some features may not work.'), 'fail': ('\nValidation failed!', 'Fix errors before running Artemis.')}
    messages = status_messages.get(report.overall_status, ('Unknown status', ''))
    for message in messages:
        
        logger.log(message, 'INFO')
    
    logger.log('\n' + '=' * 70 + '\n', 'INFO')

def print_result(result: ValidationResult) -> None:
    """
    Print a single validation result

    WHY: Provides formatted output for individual validation checks

    Args:
        result: ValidationResult to print
    """
    symbol = '[PASS]' if result.passed else '[WARN]' if result.severity == 'warning' else '[FAIL]'
    
    logger.log(f'{symbol} {result.check_name}: {result.message}', 'INFO')
    if not result.passed and result.fix_suggestion:
        
        logger.log(f'   Fix: {result.fix_suggestion}', 'INFO')