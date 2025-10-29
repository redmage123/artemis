from artemis_logger import get_logger
logger = get_logger('compile_java_ecosystem')
'\nCompile Java Ecosystem Package Modules\n\nWHY: Validates syntax of all refactored modules before deployment.\n'
import py_compile
import sys
from pathlib import Path

def compile_module(module_path: Path) -> bool:
    """
    Compile a Python module.

    Args:
        module_path: Path to module

    Returns:
        True if compilation successful
    """
    try:
        py_compile.compile(str(module_path), doraise=True)
        
        logger.log(f'✓ {module_path.name}', 'INFO')
        return True
    except py_compile.PyCompileError as e:
        
        logger.log(f'✗ {module_path.name}: {e}', 'INFO')
        return False

def main():
    """Main compilation function."""
    base_dir = Path(__file__).parent / 'java_ecosystem'
    modules = [base_dir / '__init__.py', base_dir / 'models.py', base_dir / 'maven_integration.py', base_dir / 'gradle_integration.py', base_dir / 'dependency_resolver.py', base_dir / 'build_coordinator.py', base_dir / 'ecosystem_core.py']
    modules.append(Path(__file__).parent / 'java_ecosystem_integration.py')
    
    logger.log('Compiling Java Ecosystem modules...', 'INFO')
    
    logger.log('=' * 60, 'INFO')
    all_success = True
    for module in modules:
        if not compile_module(module):
            all_success = False
    
    logger.log('=' * 60, 'INFO')
    if all_success:
        
        logger.log('All modules compiled successfully!', 'INFO')
        return 0
    else:
        
        logger.log('Some modules failed to compile!', 'INFO')
        return 1
if __name__ == '__main__':
    sys.exit(main())