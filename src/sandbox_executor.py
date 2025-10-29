from artemis_logger import get_logger
logger = get_logger('sandbox_executor')
'\nSandbox Executor - Backward Compatibility Wrapper\n\nDEPRECATED: This module is deprecated. Use security.sandbox package instead.\n\nThis wrapper provides backward compatibility for existing code.\nAll functionality has been moved to the modular security.sandbox package.\n\nMigration guide:\n    Old: from sandbox_executor import SandboxExecutor, SandboxConfig\n    New: from security.sandbox import SandboxExecutor, SandboxConfig\n\nThe modular package provides:\n    - security.sandbox.models - Data models\n    - security.sandbox.validator - Security validation\n    - security.sandbox.resource_limiter - Resource limits\n    - security.sandbox.isolation_manager - Process isolation\n    - security.sandbox.executor_core - Main executor\n'
import warnings
from security.sandbox import SandboxConfig, ExecutionResult, SecurityScanResult, SecurityValidator, SecurityScanner, ResourceLimiter, DockerResourceLimiter, temporary_limits, IsolationBackend, SubprocessIsolation, DockerIsolation, IsolationManager, SubprocessSandbox, DockerSandbox, SandboxExecutor
warnings.warn('sandbox_executor module is deprecated. Use security.sandbox package instead.', DeprecationWarning, stacklevel=2)
__all__ = ['SandboxExecutor', 'SandboxConfig', 'ExecutionResult', 'SecurityScanResult', 'SecurityValidator', 'SecurityScanner', 'ResourceLimiter', 'DockerResourceLimiter', 'temporary_limits', 'IsolationBackend', 'SubprocessIsolation', 'DockerIsolation', 'IsolationManager', 'SubprocessSandbox', 'DockerSandbox']
if __name__ == '__main__':
    'Example usage and testing'
    
    logger.log('Sandbox Executor - Example Usage', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    
    logger.log('NOTE: Using backward compatibility wrapper', 'INFO')
    
    logger.log('Consider migrating to: from security.sandbox import SandboxExecutor', 'INFO')
    
    logger.log('=' * 70 + '\n', 'INFO')
    config = SandboxConfig(max_cpu_time=10, max_memory_mb=256, timeout=15)
    executor = SandboxExecutor(config)
    
    logger.log(f'Using backend: {executor.backend_name}\n', 'INFO')
    
    logger.log('1. Executing safe code...', 'INFO')
    safe_code = '\nprint("Hello from sandbox!")\nimport math\nprint(f"Pi = {math.pi}")\n'
    result = executor.execute_python_code(safe_code)
    
    logger.log(f'   Success: {result.success}', 'INFO')
    
    logger.log(f'   Output: {result.stdout.strip()}', 'INFO')
    
    logger.log(f'   Time: {result.execution_time:.2f}s', 'INFO')
    
    logger.log('\n2. Testing security scan...', 'INFO')
    unsafe_code = '\nimport os\nos.system("ls /")\n'
    result = executor.execute_python_code(unsafe_code, scan_security=True)
    
    logger.log(f'   Success: {result.success}', 'INFO')
    
    logger.log(f'   Killed: {result.killed}', 'INFO')
    
    logger.log(f'   Reason: {result.kill_reason}', 'INFO')
    
    logger.log('\n3. Testing timeout...', 'INFO')
    timeout_code = '\nimport time\ntime.sleep(20)  # Will timeout\n'
    result = executor.execute_python_code(timeout_code, scan_security=False)
    
    logger.log(f'   Success: {result.success}', 'INFO')
    
    logger.log(f'   Killed: {result.killed}', 'INFO')
    
    logger.log(f'   Reason: {result.kill_reason}', 'INFO')
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('✅ Sandbox executor working correctly!', 'INFO')