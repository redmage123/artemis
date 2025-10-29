from artemis_logger import get_logger
logger = get_logger('code_standards_validator')
'\nBACKWARD COMPATIBILITY WRAPPER\n\nThis module maintains backward compatibility while the codebase migrates\nto the new modular structure in coding_standards/validation/.\n\nAll functionality has been refactored into:\n- coding_standards/validation/models.py - ValidationResult\n- coding_standards/validation/severity_filter.py - Severity filtering\n- coding_standards/validation/formatter.py - Violation formatting\n- coding_standards/validation/validator.py - CodeStandardsValidator\n\nTo migrate your code:\n    OLD: from code_standards_validator import CodeStandardsValidator, ValidationResult\n    NEW: from coding_standards.validation import CodeStandardsValidator, ValidationResult\n\nNo breaking changes - all imports remain identical.\n'
from coding_standards.validation import CodeStandardsValidator, ValidationResult
__all__ = ['CodeStandardsValidator', 'ValidationResult']
if __name__ == '__main__':
    validator = CodeStandardsValidator(verbose=True)
    result = validator.validate_code_standards(code_dir='src', severity_threshold='critical')
    
    logger.log(result.summary, 'INFO')
    
    logger.log(f'\nFiles scanned: {result.files_scanned}', 'INFO')
    
    logger.log(f'Violations found: {result.violation_count}', 'INFO')
    if result.is_valid:
        import sys
        sys.exit(0)
    
    logger.log('\nViolations:', 'INFO')
    for v in result.violations[:5]:
        
        logger.log(f"  {v['file']}:{v['line']} - {v['message']}", 'INFO')
    remaining = result.violation_count - 5
    if remaining > 0:
        
        logger.log(f'  ... and {remaining} more', 'INFO')