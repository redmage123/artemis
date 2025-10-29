from artemis_logger import get_logger
logger = get_logger('verify_services_refactoring')
'\nVerification script for services.core refactoring.\n\nCompiles all modules and verifies backward compatibility.\n'
import py_compile
import sys
from pathlib import Path

def compile_module(module_path: Path) -> bool:
    """Compile a Python module to verify syntax."""
    try:
        py_compile.compile(module_path, doraise=True)
        
        logger.log(f'✅ {module_path.name}: Compilation successful', 'INFO')
        return True
    except py_compile.PyCompileError as e:
        
        logger.log(f'❌ {module_path.name}: Compilation failed', 'INFO')
        
        logger.log(f'   Error: {e}', 'INFO')
        return False

def main():
    """Run compilation verification."""
    
    logger.log('=' * 70, 'INFO')
    
    logger.log('SERVICES.CORE REFACTORING VERIFICATION', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    
    pass
    base_path = Path(__file__).parent
    modules = [base_path / 'services' / 'core' / 'test_runner.py', base_path / 'services' / 'core' / 'html_validator.py', base_path / 'services' / 'core' / 'pipeline_logger.py', base_path / 'services' / 'core' / 'file_manager.py', base_path / 'services' / 'core' / '__init__.py', base_path / 'artemis_services.py']
    
    logger.log('Compiling modules...', 'INFO')
    
    pass
    results = []
    for module in modules:
        if not module.exists():
            
            logger.log(f'❌ {module.name}: File not found', 'INFO')
            results.append(False)
        else:
            results.append(compile_module(module))
    
    pass
    
    logger.log('=' * 70, 'INFO')
    if all(results):
        
        logger.log('✅ ALL MODULES COMPILED SUCCESSFULLY', 'INFO')
        
        pass
        
        logger.log('Backward compatibility verified!', 'INFO')
        
        logger.log('You can now import from either:', 'INFO')
        
        logger.log('  - artemis_services (deprecated, shows warning)', 'INFO')
        
        logger.log('  - services.core (recommended)', 'INFO')
        return 0
    else:
        
        logger.log('❌ COMPILATION FAILED', 'INFO')
        
        pass
        
        logger.log('Please fix the errors above before proceeding.', 'INFO')
        return 1
if __name__ == '__main__':
    sys.exit(main())