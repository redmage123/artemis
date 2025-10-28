#!/usr/bin/env python3
"""
AI Query Service - Backward Compatibility Wrapper

WHY: Maintain backward compatibility while code is fully modularized.

RESPONSIBILITY:
- Re-export all public classes and functions from ai_query package
- Preserve existing import paths for dependent code
- Enable gradual migration to new package structure

PATTERNS:
- Backward compatibility wrapper
- Minimal re-export layer

MIGRATION PATH:
  Old: from ai_query_service import AIQueryService, QueryType
  New: from ai_query import AIQueryService, QueryType

NOTE: This file should be considered deprecated. New code should import
      directly from the ai_query package.
"""

# Re-export everything from the modularized package
from ai_query import (
    # Enums
    QueryType,

    # Data Classes
    KGContext,
    RAGContext,
    LLMResponse,
    AIQueryResult,
    TokenSavingsMetrics,

    # Strategies
    KGQueryStrategy,
    RequirementsKGStrategy,
    ArchitectureKGStrategy,
    CodeReviewKGStrategy,
    CodeGenerationKGStrategy,
    ProjectAnalysisKGStrategy,
    ErrorRecoveryKGStrategy,
    SprintPlanningKGStrategy,
    RetrospectiveKGStrategy,

    # Service & Tracker
    TokenSavingsTracker,
    AIQueryService,

    # Factory
    create_ai_query_service,
)

__all__ = [
    # Enums
    'QueryType',

    # Data Classes
    'KGContext',
    'RAGContext',
    'LLMResponse',
    'AIQueryResult',
    'TokenSavingsMetrics',

    # Strategies
    'KGQueryStrategy',
    'RequirementsKGStrategy',
    'ArchitectureKGStrategy',
    'CodeReviewKGStrategy',
    'CodeGenerationKGStrategy',
    'ProjectAnalysisKGStrategy',
    'ErrorRecoveryKGStrategy',
    'SprintPlanningKGStrategy',
    'RetrospectiveKGStrategy',

    # Service & Tracker
    'TokenSavingsTracker',
    'AIQueryService',

    # Factory
    'create_ai_query_service',
]


# Example usage (preserved for backward compatibility)
if __name__ == "__main__":
    # Example usage
    print("AI Query Service - Example")
    print("="*60)

    # Mock LLM client
    class MockLLMClient:
        model = "gpt-4"
        def generate_text(self, system_message, user_message, temperature, max_tokens):
            return "Mock LLM response based on enhanced prompt"

    # Create service
    service = create_ai_query_service(
        llm_client=MockLLMClient(),
        verbose=True
    )

    # Example query
    result = service.query(
        query_type=QueryType.REQUIREMENTS_PARSING,
        prompt="Parse these requirements: User authentication system",
        kg_query_params={'project_name': 'auth-system'}
    )

    print(f"\nQuery Type: {result.query_type.value}")
    print(f"Success: {result.success}")
    print(f"Tokens Saved: ~{result.llm_response.tokens_saved}")
    print(f"Total Duration: {result.total_duration_ms:.2f}ms")
