#!/usr/bin/env python3
"""
WHY: Provide validation failure analysis to enable intelligent prompt refinement
RESPONSIBILITY: Export failure analyzer, models, and factory for external use
PATTERNS: Strategy (categorization), Factory (analyzer creation)

This package analyzes validation failures and extracts actionable constraints:
- Categorizes failures by type (missing imports, incomplete code, etc.)
- Extracts specific constraints for retry attempts
- Provides severity scoring
- Recommends retry strategies

Example:
    from validation import ValidationFailureAnalyzer, FailureCategory

    analyzer = ValidationFailureAnalyzer(logger)
    analysis = analyzer.analyze_failures(validation_results, code)

    print(f"Category: {analysis.category.value}")
    print(f"Constraints: {analysis.constraints}")
    print(f"Severity: {analysis.severity}")
    print(f"Retry recommended: {analysis.retry_recommended}")
"""

from validation.models import FailureCategory, FailureAnalysis
from validation.analyzer import ValidationFailureAnalyzer
from validation.factory import FailureAnalyzerFactory

# Anti-hallucination validation components
from validation.static_analysis_validator import (
    StaticAnalysisValidator,
    StaticAnalysisResult,
    AnalysisIssue,
)
from validation.property_based_test_generator import (
    PropertyBasedTestGenerator,
    PropertyTestSuite,
    CodeProperty,
)
from validation.symbolic_execution_validator import (
    SymbolicExecutionValidator,
    SymbolicExecutionResult,
    SymbolicPath,
    CounterExample,
    VerificationStatus,
)
from validation.formal_specification_matcher import (
    FormalSpecificationMatcher,
    FormalMatchingResult,
    FormalSpecification,
    VerificationResult,
    SpecificationType,
)
from validation.anti_hallucination_orchestrator import (
    AntiHallucinationOrchestrator,
    ValidationProfile,
    RiskLevel,
    TaskType,
    TaskContext,
    ValidationStrategy,
    ValidationTechnique,
)
# Artemis integration
from validation.artemis_integration import (
    ArtemisValidationIntegration,
    get_validation_integration,
    get_validation_strategy_for_task,
)
# Router-validation integration
from validation.router_validation_integration import (
    RouterValidationIntegration,
    StageValidationConfig,
    get_router_validation_integration,
)
# Orchestrator configuration
from validation.orchestrator_config import (
    OrchestratorConfig,
    DEFAULT_CONFIG,
    get_speed_optimized_config,
    get_quality_optimized_config,
    get_balanced_config,
    get_critical_systems_config,
)
# LLM validation prompts
from validation.llm_validation_prompts import (
    generate_validation_aware_prompt,
    generate_code_review_prompt,
    generate_refactoring_prompt,
    get_validation_summary_for_llm,
)
# Code review integration
from validation.code_review_integration import (
    CodeReviewValidationIntegration,
    get_code_review_validation_integration,
    get_code_review_validation_strategy,
    enhance_code_review_with_validation,
)

__all__ = [
    # Existing exports
    'FailureCategory',
    'FailureAnalysis',
    'ValidationFailureAnalyzer',
    'FailureAnalyzerFactory',
    # Anti-hallucination exports - Phase 1
    'StaticAnalysisValidator',
    'StaticAnalysisResult',
    'AnalysisIssue',
    'PropertyBasedTestGenerator',
    'PropertyTestSuite',
    'CodeProperty',
    # Anti-hallucination exports - Phase 3
    'SymbolicExecutionValidator',
    'SymbolicExecutionResult',
    'SymbolicPath',
    'CounterExample',
    'VerificationStatus',
    'FormalSpecificationMatcher',
    'FormalMatchingResult',
    'FormalSpecification',
    'VerificationResult',
    'SpecificationType',
    # Anti-hallucination orchestrator
    'AntiHallucinationOrchestrator',
    'ValidationProfile',
    'RiskLevel',
    'TaskType',
    'TaskContext',
    'ValidationStrategy',
    'ValidationTechnique',
    # Artemis integration
    'ArtemisValidationIntegration',
    'get_validation_integration',
    'get_validation_strategy_for_task',
    # Router-validation integration
    'RouterValidationIntegration',
    'StageValidationConfig',
    'get_router_validation_integration',
    # Orchestrator configuration
    'OrchestratorConfig',
    'DEFAULT_CONFIG',
    'get_speed_optimized_config',
    'get_quality_optimized_config',
    'get_balanced_config',
    'get_critical_systems_config',
    # LLM validation prompts
    'generate_validation_aware_prompt',
    'generate_code_review_prompt',
    'generate_refactoring_prompt',
    'get_validation_summary_for_llm',
    # Code review integration
    'CodeReviewValidationIntegration',
    'get_code_review_validation_integration',
    'get_code_review_validation_strategy',
    'enhance_code_review_with_validation',
]
