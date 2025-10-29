from artemis_logger import get_logger
logger = get_logger('supervisor_circuit_breaker')
'\nBACKWARD COMPATIBILITY WRAPPER\n\nThis module maintains backward compatibility while the codebase migrates\nto the new modular structure in supervisor/circuit_breaker/.\n\nAll functionality has been refactored into:\n- supervisor/circuit_breaker/models.py - StageHealth, RecoveryStrategy, CircuitState\n- supervisor/circuit_breaker/manager.py - CircuitBreakerManager\n\nTo migrate your code:\n    OLD: from supervisor_circuit_breaker import CircuitBreakerManager\n    NEW: from supervisor.circuit_breaker import CircuitBreakerManager\n\nNo breaking changes - all imports remain identical.\n'
from supervisor.circuit_breaker import StageHealth, RecoveryStrategy, CircuitState, CircuitBreakerManager
__all__ = ['StageHealth', 'RecoveryStrategy', 'CircuitState', 'CircuitBreakerManager']
if __name__ == '__main__':
    import argparse
    import json
    import sys
    parser = argparse.ArgumentParser(description='Circuit Breaker Manager Demo')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    args = parser.parse_args()
    if args.demo:
        
        logger.log('=' * 70, 'INFO')
        
        logger.log('CIRCUIT BREAKER MANAGER DEMO', 'INFO')
        
        logger.log('=' * 70, 'INFO')
        manager = CircuitBreakerManager(verbose=True)
        manager.register_stage('stage1', RecoveryStrategy(circuit_breaker_threshold=3))
        manager.register_stage('stage2')
        
        logger.log('\n--- Simulating stage1 failures ---', 'INFO')
        for i in range(5):
            manager.record_failure('stage1')
            is_open = manager.check_circuit('stage1')
            
            logger.log(f'Attempt {i + 1}: Circuit open = {is_open}', 'INFO')
        
        logger.log('\n--- Simulating stage1 success ---', 'INFO')
        manager.record_success('stage1', duration=1.5)
        is_open = manager.check_circuit('stage1')
        
        logger.log(f'After success: Circuit open = {is_open}', 'INFO')
        
        logger.log('\n--- Statistics ---', 'INFO')
        stats = manager.get_statistics()
        
        logger.log(json.dumps(stats, indent=2), 'INFO')
        sys.exit(0)
    if args.stats:
        manager = CircuitBreakerManager(verbose=False)
        stats = manager.get_statistics()
        
        logger.log(json.dumps(stats, indent=2), 'INFO')
        sys.exit(0)
    parser.print_help()