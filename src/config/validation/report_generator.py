from artemis_logger import get_logger
logger = get_logger('report_generator')
'\nReport Generator - Validation report generation and printing\n\nWHY: Generates comprehensive validation reports and provides human-readable\n     output for validation results.\n\nRESPONSIBILITY: Generate validation reports and format output.\n\nPATTERNS: Strategy pattern for status messages, pure functions for report generation.\n'
from typing import List, Tuple, Dict
from config.validation.models import ValidationResult, ValidationReport

class ReportGenerator:
    """
    Generates validation reports from results.

    WHY: Aggregates validation results into comprehensive report.
    RESPONSIBILITY: Generate ValidationReport from results only.
    PATTERNS: Pure functions for report generation, list comprehensions for filtering.
    """

    @staticmethod
    def generate(results: List[ValidationResult]) -> ValidationReport:
        """
        Generate validation report from results.

        WHY: Aggregates all validation results into comprehensive report.
        PERFORMANCE: O(n) where n is number of results, using list comprehensions.

        Args:
            results: List of ValidationResults to aggregate

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

class ReportPrinter:
    """
    Prints validation reports and individual results.

    WHY: Provides human-readable output for validation results.
    RESPONSIBILITY: Format and print validation output only.
    PATTERNS: Strategy pattern for status messages, guard clauses.
    """
    STATUS_MESSAGES: Dict[str, Tuple[str, str]] = {'pass': ('\nAll validation checks passed!', 'Artemis is ready to run.'), 'warning': ('\nValidation completed with warnings', 'Artemis can run but some features may not work.'), 'fail': ('\nValidation failed!', 'Fix errors before running Artemis.')}

    @staticmethod
    def print_result(result: ValidationResult) -> None:
        """
        Print a single validation result.

        WHY: Provides immediate feedback during validation.
        PERFORMANCE: O(1) string formatting and printing.

        Args:
            result: ValidationResult to print
        """
        symbol = '[PASS]' if result.passed else '[WARN]' if result.severity == 'warning' else '[FAIL]'
        
        logger.log(f'{symbol} {result.check_name}: {result.message}', 'INFO')
        if not result.passed and result.fix_suggestion:
            
            logger.log(f'   Fix: {result.fix_suggestion}', 'INFO')

    @staticmethod
    def print_header() -> None:
        """
        Print validation header.

        WHY: Provides clear visual separation for validation output.
        PERFORMANCE: O(1) string printing.
        """
        
        logger.log('\n' + '=' * 70, 'INFO')
        
        logger.log('ARTEMIS CONFIGURATION VALIDATION', 'INFO')
        
        logger.log('=' * 70 + '\n', 'INFO')

    @staticmethod
    def print_report(report: ValidationReport) -> None:
        """
        Print validation report summary.

        WHY: Provides human-readable summary of validation results.
        PERFORMANCE: O(1) - simple string formatting.

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
        messages = ReportPrinter.STATUS_MESSAGES.get(report.overall_status, ('Unknown status', ''))
        for message in messages:
            
            logger.log(message, 'INFO')
        
        logger.log('\n' + '=' * 70 + '\n', 'INFO')