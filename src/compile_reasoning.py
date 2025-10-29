from artemis_logger import get_logger
logger = get_logger('compile_reasoning')
'\nCompile all reasoning package modules.\n'
import py_compile
import sys
from pathlib import Path

def compile_modules():
    """Compile all reasoning package modules"""
    base_path = Path('/home/bbrelin/src/repos/artemis/src')
    modules = ['reasoning/__init__.py', 'reasoning/models.py', 'reasoning/strategy_selector.py', 'reasoning/prompt_enhancer.py', 'reasoning/executors.py', 'reasoning/llm_client_wrapper.py', 'reasoning_integration.py']
    success_count = 0
    error_count = 0
    for module in modules:
        module_path = base_path / module
        try:
            py_compile.compile(str(module_path), doraise=True)
            
            logger.log(f'✓ Compiled: {module}', 'INFO')
            success_count += 1
        except py_compile.PyCompileError as e:
            
            logger.log(f'✗ Failed: {module}', 'INFO')
            
            logger.log(f'  Error: {e}', 'INFO')
            error_count += 1
    
    logger.log(f"\n{'=' * 60}", 'INFO')
    
    logger.log(f'Compilation Results:', 'INFO')
    
    logger.log(f'  Success: {success_count}', 'INFO')
    
    logger.log(f'  Errors:  {error_count}', 'INFO')
    
    logger.log(f"{'=' * 60}", 'INFO')
    return error_count == 0
if __name__ == '__main__':
    success = compile_modules()
    sys.exit(0 if success else 1)