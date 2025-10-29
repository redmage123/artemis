from artemis_logger import get_logger
logger = get_logger('reporter')
'\nWHY: Format and print violation reports\nRESPONSIBILITY: Generate human-readable violation reports\nPATTERNS: Reporter (presentation logic)\n\nReporter separates presentation from scanning logic.\n'
from collections import defaultdict

def print_report(scanner):
    """
    Print comprehensive violation report.

    WHY: Separates reporting from scanning logic (SRP).

    Args:
        scanner: CodeStandardsScanner instance with violations
    """
    
    logger.log('=' * 70, 'INFO')
    
    logger.log('CODE STANDARDS VIOLATION REPORT', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    
    logger.log(f'Files scanned: {scanner.files_scanned}', 'INFO')
    
    pass
    total_violations = sum((len(v) for v in scanner.violations_by_type.values()))
    
    logger.log(f'Total violations: {total_violations}', 'INFO')
    
    pass
    if not total_violations:
        
        logger.log('✅ No violations found!', 'INFO')
        return
    
    logger.log('Violations by type:', 'INFO')
    for v_type, violations in sorted(scanner.violations_by_type.items()):
        severity_counts = defaultdict(int)
        for v in violations:
            severity_counts[v.severity] += 1
        severity_str = ', '.join((f'{count} {sev}' for sev, count in severity_counts.items()))
        
        logger.log(f'  {v_type}: {len(violations)} ({severity_str})', 'INFO')
    
    pass
    
    logger.log('=' * 70, 'INFO')
    
    logger.log('DETAILED VIOLATIONS', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    for v_type, violations in sorted(scanner.violations_by_type.items()):
        
        logger.log(f"\n{v_type.upper().replace('_', ' ')}:", 'INFO')
        
        logger.log('-' * 70, 'INFO')
        violations_by_file = defaultdict(list)
        for v in violations:
            violations_by_file[v.file_path].append(v)
        for file_path, file_violations in sorted(violations_by_file.items()):
            
            logger.log(f'\n📄 {file_path}', 'INFO')
            for v in sorted(file_violations, key=lambda x: x.line_number):
                
                logger.log(f'   Line {v.line_number} [{v.severity.upper()}]: {v.message}', 'INFO')
    
    logger.log('\n' + '=' * 70, 'INFO')