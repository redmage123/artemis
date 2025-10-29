from artemis_logger import get_logger
logger = get_logger('ai_service_integration')
'\nAI Query Service Integration\n\nWHY: Separate KG→RAG→LLM pipeline logic from main parser\nRESPONSIBILITY: Execute centralized AI Query Service calls\nPATTERNS: Facade pattern for AIQueryService complexity\n'
from typing import Optional, Any, Dict, List
from llm_client import LLMClient
from artemis_exceptions import RequirementsParsingError
from ai_query_service import AIQueryService, create_ai_query_service, QueryType, AIQueryResult

class AIServiceIntegration:
    """
    AI Query Service integration for requirements parsing

    WHY: Centralized KG→RAG→LLM pipeline with token optimization
    RESPONSIBILITY: Route queries through AI service with proper context
    PATTERNS: Facade pattern
    """

    def __init__(self, llm: LLMClient, rag: Optional[Any]=None, ai_service: Optional[AIQueryService]=None, logger: Optional[Any]=None, verbose: bool=False):
        """
        Initialize AI Service integration

        Args:
            llm: LLM client for fallback
            rag: RAG agent for service creation
            ai_service: Pre-configured AI service (optional)
            logger: Logger instance (optional)
            verbose: Enable verbose logging
        """
        self.llm = llm
        self.verbose = verbose
        self.logger = logger
        self.ai_service = None
        self._initialize_ai_service(ai_service, rag)

    def query_with_ai_service(self, full_prompt: str, project_name: str) -> str:
        """
        Query using AI Service with KG→RAG→LLM pipeline

        WHY: Optimize token usage via KG patterns
        RESPONSIBILITY: Execute AI service query with proper error handling

        Args:
            full_prompt: Complete prompt text
            project_name: Project name for KG query

        Returns:
            LLM response content

        Raises:
            RequirementsParsingError: If query fails
        """
        if not self.ai_service:
            raise RequirementsParsingError('AI Query Service not available', context={'project_name': project_name})
        self.log('🔄 Using AI Query Service for KG→RAG→LLM pipeline')
        keywords = project_name.lower().split()[:3]
        result = self.ai_service.query(query_type=QueryType.REQUIREMENTS_PARSING, prompt=full_prompt, kg_query_params={'project_name': project_name, 'keywords': keywords}, temperature=0.3, max_tokens=4000)
        if not result.success:
            raise RequirementsParsingError(f'AI Query Service failed: {result.error}', context={'project_name': project_name})
        if result.kg_context and result.kg_context.pattern_count > 0:
            self.log(f'📊 KG found {result.kg_context.pattern_count} patterns, saved ~{result.llm_response.tokens_saved} tokens')
        return result.llm_response.content

    def is_available(self) -> bool:
        """Check if AI Service is available"""
        return self.ai_service is not None

    def _initialize_ai_service(self, ai_service: Optional[AIQueryService], rag: Optional[Any]):
        """
        Initialize AI Query Service

        WHY: Service may be provided or needs to be created
        RESPONSIBILITY: Set up AI service with proper fallback
        """
        try:
            if ai_service:
                self.ai_service = ai_service
                self.log('✅ Using provided AI Query Service')
            else:
                self.ai_service = create_ai_query_service(llm_client=self.llm, rag=rag, logger=self.logger, verbose=self.verbose)
                self.log('✅ AI Query Service initialized (KG→RAG→LLM pipeline)')
        except Exception as e:
            self.log(f'⚠️  Could not initialize AI Query Service: {e}')
            self.ai_service = None

    def log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            
            logger.log(f'[AIServiceIntegration] {message}', 'INFO')