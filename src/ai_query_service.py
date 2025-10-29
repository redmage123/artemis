from artemis_logger import get_logger
logger = get_logger('ai_query_service')
'\nAI Query Service - Backward Compatibility Wrapper\n\nWHY: Maintain backward compatibility while code is fully modularized.\n\nRESPONSIBILITY:\n- Re-export all public classes and functions from ai_query package\n- Preserve existing import paths for dependent code\n- Enable gradual migration to new package structure\n\nPATTERNS:\n- Backward compatibility wrapper\n- Minimal re-export layer\n\nMIGRATION PATH:\n  Old: from ai_query_service import AIQueryService, QueryType\n  New: from ai_query import AIQueryService, QueryType\n\nNOTE: This file should be considered deprecated. New code should import\n      directly from the ai_query package.\n'
from ai_query import QueryType, KGContext, RAGContext, LLMResponse, AIQueryResult, TokenSavingsMetrics, KGQueryStrategy, RequirementsKGStrategy, ArchitectureKGStrategy, CodeReviewKGStrategy, CodeGenerationKGStrategy, ProjectAnalysisKGStrategy, ErrorRecoveryKGStrategy, SprintPlanningKGStrategy, RetrospectiveKGStrategy, TokenSavingsTracker, AIQueryService, create_ai_query_service
__all__ = ['QueryType', 'KGContext', 'RAGContext', 'LLMResponse', 'AIQueryResult', 'TokenSavingsMetrics', 'KGQueryStrategy', 'RequirementsKGStrategy', 'ArchitectureKGStrategy', 'CodeReviewKGStrategy', 'CodeGenerationKGStrategy', 'ProjectAnalysisKGStrategy', 'ErrorRecoveryKGStrategy', 'SprintPlanningKGStrategy', 'RetrospectiveKGStrategy', 'TokenSavingsTracker', 'AIQueryService', 'create_ai_query_service']
if __name__ == '__main__':
    
    logger.log('AI Query Service - Example', 'INFO')
    
    logger.log('=' * 60, 'INFO')

    class MockLLMClient:
        model = 'gpt-4'

        def generate_text(self, system_message, user_message, temperature, max_tokens):
            return 'Mock LLM response based on enhanced prompt'
    service = create_ai_query_service(llm_client=MockLLMClient(), verbose=True)
    result = service.query(query_type=QueryType.REQUIREMENTS_PARSING, prompt='Parse these requirements: User authentication system', kg_query_params={'project_name': 'auth-system'})
    
    logger.log(f'\nQuery Type: {result.query_type.value}', 'INFO')
    
    logger.log(f'Success: {result.success}', 'INFO')
    
    logger.log(f'Tokens Saved: ~{result.llm_response.tokens_saved}', 'INFO')
    
    logger.log(f'Total Duration: {result.total_duration_ms:.2f}ms', 'INFO')