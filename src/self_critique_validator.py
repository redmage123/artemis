from artemis_logger import get_logger
logger = get_logger('self_critique_validator')
'\nWHY: Provide backward compatibility for existing code using self_critique_validator.\n\nRESPONSIBILITY:\n- Re-export all classes and enums from self_critique package\n- Maintain identical API to original monolithic module\n- Enable gradual migration to new package structure\n- Preserve all functionality without code changes\n\nPATTERNS:\n- Proxy Pattern: Forward all imports to new package\n- Backward Compatibility: Zero breaking changes\n- Deprecation Path: Enable future migration warnings\n\nMIGRATION NOTE:\nThis module is a compatibility wrapper. New code should import from self_critique package:\n\n    # Old (deprecated but supported):\n    from self_critique_validator import SelfCritiqueValidator\n\n    # New (recommended):\n    from self_critique import SelfCritiqueValidator\n\nREFACTORING:\nOriginal file: 653 lines\nWrapper file: ~70 lines\nReduction: ~89%\n\nModule breakdown:\n- models.py: 116 lines (data classes and enums)\n- critique_generator.py: 259 lines (LLM critique generation)\n- improvement_suggester.py: 335 lines (uncertainty analysis, citations)\n- validation_checker.py: 115 lines (pass/fail determination)\n- feedback_processor.py: 181 lines (feedback generation)\n- validator_core.py: 175 lines (orchestration)\n- __init__.py: 60 lines (package exports)\nTotal: 1,241 lines (in 7 focused modules vs 1 monolithic file)\n'
from self_critique import CritiqueLevel, CritiqueSeverity, CritiqueFinding, UncertaintyMetrics, CodeCitation, CritiqueResult, SelfCritiqueValidator, SelfCritiqueFactory, UncertaintyAnalyzer, CitationTracker
__all__ = ['CritiqueLevel', 'CritiqueSeverity', 'CritiqueFinding', 'UncertaintyMetrics', 'CodeCitation', 'CritiqueResult', 'SelfCritiqueValidator', 'SelfCritiqueFactory', 'UncertaintyAnalyzer', 'CitationTracker']
if __name__ == '__main__':
    
    logger.log('Self-Critique Validator - Layer 5 Hallucination Reduction', 'INFO')
    
    logger.log('Ready for integration with validation pipeline', 'INFO')
    
    logger.log('\nNOTE: This is a compatibility wrapper.', 'INFO')
    
    logger.log("New code should import from 'self_critique' package directly.", 'INFO')