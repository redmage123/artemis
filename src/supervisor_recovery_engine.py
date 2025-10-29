from artemis_logger import get_logger
logger = get_logger('supervisor_recovery_engine')
'\nModule: supervisor_recovery_engine.py\n\nBACKWARD COMPATIBILITY WRAPPER\n\nWHY: Maintain backward compatibility while code migrates to modular structure\nRESPONSIBILITY: Re-export all components from supervisor/recovery/ package\nMIGRATION PATH: Import from supervisor.recovery directly for new code\n\nThis file preserves the original import structure:\n    from supervisor_recovery_engine import RecoveryEngine, RecoveryStrategy\n\nNew code should import from the modular package:\n    from supervisor.recovery import RecoveryEngine, RecoveryStrategy\n    from supervisor.recovery.strategies import JSONParsingStrategy, RetryStrategy\n    from supervisor.recovery.llm_auto_fix import LLMAutoFix\n    from supervisor.recovery.failure_analysis import FailureAnalyzer\n    from supervisor.recovery.state_restoration import StateRestoration\n\nDEPRECATION TIMELINE:\n- Phase 1: This wrapper maintains compatibility (current)\n- Phase 2: Add deprecation warnings\n- Phase 3: Remove wrapper after all imports updated\n\nOriginal module location: /home/bbrelin/src/repos/artemis/src/supervisor_recovery_engine.py\nNew module location: /home/bbrelin/src/repos/artemis/src/supervisor/recovery/\nLines reduced: 941 -> ~150 (main engine) + 5 support modules\n'
from supervisor.recovery.engine import RecoveryEngine
from supervisor.recovery.strategy import RecoveryStrategy
from supervisor.recovery.strategies import JSONParsingStrategy, RetryStrategy, DefaultValueStrategy, SkipStageStrategy
from supervisor.recovery.failure_analysis import FailureAnalyzer
from supervisor.recovery.state_restoration import StateRestoration
from supervisor.recovery.llm_auto_fix import LLMAutoFix
__all__ = ['RecoveryEngine', 'RecoveryStrategy', 'JSONParsingStrategy', 'RetryStrategy', 'DefaultValueStrategy', 'SkipStageStrategy', 'FailureAnalyzer', 'StateRestoration', 'LLMAutoFix']

def _run_demo():
    """Run recovery engine demo"""
    import json
    
    logger.log('=' * 70, 'INFO')
    
    logger.log('RECOVERY ENGINE DEMO', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    engine = RecoveryEngine(verbose=True)
    
    logger.log('\n--- Simulating Crash Recovery ---', 'INFO')
    crash_info = {'agent_name': 'test-agent', 'error_type': 'KeyError', 'error': "'missing_key'", 'traceback': ''}
    context = {}
    result = engine.recover_crashed_agent(crash_info, context)
    
    logger.log(f"Result: {result.get('message')}", 'INFO')
    
    logger.log('\n--- Simulating Hung Agent Recovery ---', 'INFO')
    timeout_info = {'timeout_seconds': 300, 'elapsed_time': 350}
    result = engine.recover_hung_agent('hung-agent', timeout_info)
    
    logger.log(f"Result: {result.get('message')}", 'INFO')
    
    logger.log('\n--- Statistics ---', 'INFO')
    stats = engine.get_statistics()
    
    logger.log(json.dumps(stats, indent=2), 'INFO')

def _show_stats():
    """Show recovery engine statistics"""
    import json
    engine = RecoveryEngine(verbose=False)
    stats = engine.get_statistics()
    
    logger.log(json.dumps(stats, indent=2), 'INFO')
if __name__ == '__main__':
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='Recovery Engine Demo')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    args = parser.parse_args()
    if not args.demo and (not args.stats):
        parser.print_help()
        sys.exit(0)
    if args.demo:
        _run_demo()
    if args.stats:
        _show_stats()