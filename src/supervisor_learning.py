from artemis_logger import get_logger
logger = get_logger('supervisor_learning')
'\nBACKWARD COMPATIBILITY WRAPPER\n\nWHY: Maintain API compatibility while enabling modular architecture\nRESPONSIBILITY: Re-export all components from supervisor.learning package\nPATTERNS: Facade, Adapter (for legacy code compatibility)\n\nOriginal module (776 lines) has been refactored into:\n    supervisor/learning/models.py - Data models (73 lines)\n    supervisor/learning/pattern_recognition.py - State detection (108 lines)\n    supervisor/learning/llm_strategy.py - LLM consultation (209 lines)\n    supervisor/learning/workflow_executor.py - Workflow execution (215 lines)\n    supervisor/learning/solution_storage.py - RAG integration (178 lines)\n    supervisor/learning/learning_dispatcher.py - Strategy dispatch (175 lines)\n    supervisor/learning/engine.py - Main engine (166 lines)\n    supervisor/learning/__init__.py - Package exports (72 lines)\n\nTotal modularized lines: ~1,196 lines (includes extensive documentation)\nCore logic lines: ~620 lines (excluding documentation)\nLine count reduction: 776 → 620 core lines (20% reduction in code)\nMaintainability improvement: 8 focused modules vs 1 monolithic file\n\nMigration:\n    Old: from supervisor_learning import SupervisorLearningEngine\n    New: from supervisor.learning import SupervisorLearningEngine\n    Compatibility: This wrapper supports both import styles\n\nDesign Improvements:\n    ✓ Guard clauses (max 1 level nesting)\n    ✓ Dispatch tables (no elif chains)\n    ✓ Type hints on all functions\n    ✓ Single Responsibility Principle\n    ✓ WHY/RESPONSIBILITY/PATTERNS documentation\n    ✓ Modular components for testing and reuse\n'
from supervisor.learning import SupervisorLearningEngine
from supervisor.learning import UnexpectedState, LearnedSolution, LearningStrategy
from supervisor.learning import StatePatternRecognizer, ProblemDescriptor, LLMConsultationStrategy, LLMPromptBuilder, LLMResponseParser, WorkflowExecutionEngine, WorkflowStepExecutor, SolutionRepository, SolutionAdapter, LearningStrategyDispatcher, HumanInLoopStrategy
__all__ = ['SupervisorLearningEngine', 'UnexpectedState', 'LearnedSolution', 'LearningStrategy']
if __name__ == '__main__':
    'Example usage and testing - backward compatible with original'
    
    logger.log('Supervisor Learning Engine - Example Usage', 'INFO')
    
    logger.log('=' * 70, 'INFO')
    learning = SupervisorLearningEngine(llm_client=None, rag_agent=None, verbose=True)
    
    logger.log('\n1. Detecting unexpected state...', 'INFO')
    unexpected = learning.detect_unexpected_state(card_id='card-001', current_state='STAGE_STUCK', expected_states=['STAGE_RUNNING', 'STAGE_COMPLETED'], context={'stage_name': 'development', 'error_message': 'Developer agents not responding', 'previous_state': 'STAGE_RUNNING'})
    if unexpected:
        
        logger.log(f'   Unexpected state ID: {unexpected.state_id}', 'INFO')
        
        logger.log(f'   Severity: {unexpected.severity}', 'INFO')
        
        logger.log('\n2. Would consult LLM for solution (simulated)...', 'INFO')
        
        logger.log('   (In production, this would query GPT-4o/Claude for recovery steps)', 'INFO')
    
    logger.log('\n3. Learning statistics:', 'INFO')
    stats = learning.get_statistics()
    for key, value in stats.items():
        
        logger.log(f'   {key}: {value}', 'INFO')
    
    logger.log('\n' + '=' * 70, 'INFO')
    
    logger.log('✅ Learning engine initialized and ready!', 'INFO')
    
    logger.log('\nNOTE: This is now a modular architecture!', 'INFO')
    
    logger.log('      See supervisor/learning/ for component modules', 'INFO')