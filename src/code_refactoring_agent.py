from artemis_logger import get_logger
logger = get_logger('code_refactoring_agent')
'\nModule: Code Refactoring Agent - Backward Compatibility Wrapper\n\nWHY: Maintains backward compatibility with existing code that imports\n     from code_refactoring_agent module. Delegates to refactored package.\n\nRESPONSIBILITY:\n    - Re-export public API from agents.refactoring package\n    - Preserve original module interface\n    - Support existing import statements\n    - Provide migration path to new package\n\nPATTERNS:\n    - Facade Pattern: Wraps new implementation with old interface\n    - Adapter Pattern: Adapts new API to old expectations\n\nMIGRATION:\n    Old: from code_refactoring_agent import CodeRefactoringAgent\n    New: from agents.refactoring import CodeRefactoringAgent\n\n    This wrapper allows both styles to work during transition period.\n\nARCHITECTURE:\n    - Refactored implementation lives in agents/refactoring/\n    - This file is a thin wrapper for backward compatibility\n    - Will be deprecated in future version\n\nDEPRECATION NOTICE:\n    This module is maintained for backward compatibility only.\n    New code should import from agents.refactoring package directly.\n    See agents/refactoring/__init__.py for public API.\n'
from agents.refactoring import CodeRefactoringAgent, create_refactoring_agent, RefactoringRule, RefactoringAnalysis, CodeSmell, LongMethodSmell, SimpleLoopSmell, IfElifChainSmell, PatternType, RefactoringPriority
__all__ = ['CodeRefactoringAgent', 'create_refactoring_agent', 'RefactoringRule', 'RefactoringAnalysis', 'CodeSmell', 'LongMethodSmell', 'SimpleLoopSmell', 'IfElifChainSmell', 'PatternType', 'RefactoringPriority']
if __name__ == '__main__':
    '\n    Example usage demonstrating backward compatibility.\n\n    WHY: Maintains original test behavior for regression testing.\n    '
    import sys
    from pathlib import Path
    agent = create_refactoring_agent()
    file_path = Path(__file__)
    analysis = agent.analyze_file_for_refactoring(file_path)
    
    logger.log('\nRefactoring Analysis:', 'INFO')
    
    logger.log(f"File: {analysis['file']}", 'INFO')
    
    logger.log(f"Total Issues: {analysis['total_issues']}", 'INFO')
    if analysis.get('long_methods'):
        
        logger.log(f"\nLong Methods: {len(analysis['long_methods'])}", 'INFO')
        for method in analysis['long_methods']:
            
            logger.log(f"  - {method['name']} ({method['length']} lines)", 'INFO')
    instructions = agent.generate_refactoring_instructions(analysis)
    
    logger.log('\n' + instructions, 'INFO')
    
    logger.log('\n' + '=' * 60, 'INFO')
    
    logger.log('BACKWARD COMPATIBILITY WRAPPER ACTIVE', 'INFO')
    
    logger.log('=' * 60, 'INFO')
    
    logger.log('This module delegates to agents.refactoring package.', 'INFO')
    
    logger.log('Consider migrating to: from agents.refactoring import ...', 'INFO')
    
    logger.log('=' * 60, 'INFO')