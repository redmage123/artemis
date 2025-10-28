#!/usr/bin/env python3
"""
Stage Creation - Default pipeline stage factory

WHAT:
Factory function for creating the default Artemis pipeline stages with all
dependencies properly injected and configured.

WHY:
Separates stage creation logic from orchestrator initialization, enabling:
- Clear separation of concerns (creation vs orchestration)
- Easy customization of stage configuration
- Testable stage creation logic
- Reduced orchestrator complexity

RESPONSIBILITY:
- Create all default pipeline stages in correct order
- Inject all required dependencies (logger, rag, messenger, etc.)
- Configure stage-specific settings (AI service, supervisor, etc.)
- Handle conditional stage creation (LLM-dependent stages)

PATTERNS:
- Factory Pattern: Creates complex object graph
- Dependency Injection: Injects all stage dependencies
- Builder Pattern: Constructs stages with multiple dependencies

EXTRACTED FROM: artemis_orchestrator.py lines 405-618
"""

from typing import List, Any

from artemis_stage_interface import PipelineStage
from artemis_stages import (
    ProjectAnalysisStage,
    ArchitectureStage,
    DependencyValidationStage,
    DevelopmentStage,
    ValidationStage,
    IntegrationStage,
    TestingStage,
    ResearchStage
)
from code_review_stage import CodeReviewStage
from arbitration_stage import ArbitrationStage
from sprint_planning_stage import SprintPlanningStage
from project_review_stage import ProjectReviewStage
from uiux_stage import UIUXStage
from requirements_stage import RequirementsParsingStage
from ssd_generation_stage import SSDGenerationStage

# Import AIQueryService for centralized KG→RAG→LLM pipeline
try:
    from ai_query_service import create_ai_query_service, AIQueryService
    AI_QUERY_SERVICE_AVAILABLE = True
except ImportError:
    AI_QUERY_SERVICE_AVAILABLE = False

# Import IntelligentRouter for AI-powered stage selection
try:
    from intelligent_router import IntelligentRouter
    INTELLIGENT_ROUTER_AVAILABLE = True
except ImportError:
    INTELLIGENT_ROUTER_AVAILABLE = False


def create_default_stages(orchestrator: Any) -> List[PipelineStage]:
    """
    Create default pipeline stages with supervisor integration AND sprint workflow

    WHAT:
    Factory function that creates the complete Artemis pipeline stage sequence
    with all dependencies properly injected and configured.

    WHY:
    Centralizes stage creation logic to ensure:
    - Consistent dependency injection
    - Correct stage ordering
    - Proper supervisor integration
    - AI service configuration
    - Intelligent routing setup

    NEW Sprint-Based Workflow:
    0. RequirementsParsing - Parse free-form requirements → structured YAML/JSON
    1. SprintPlanning - Estimate features with Planning Poker, create sprints
    2. ProjectAnalysis - Analyze requirements
    3. Architecture - Design system (uses structured requirements)
    4. ProjectReview - Review & approve architecture (with feedback loop)
    5. Development - Multi-agent implementation
    6. CodeReview - Security, GDPR, accessibility
    7. UIUXStage - WCAG & GDPR compliance evaluation
    8. Validation - Test solutions
    9. Integration - Integrate winner
    10. Testing - Final tests
    11. Retrospective - Learn from sprint (handled separately)

    All stages receive supervisor for:
    - LLM cost tracking
    - Code execution sandboxing
    - Unexpected state handling and recovery
    - Dynamic heartbeat adjustment

    Args:
        orchestrator: ArtemisOrchestrator instance with all dependencies

    Returns:
        List of configured pipeline stages

    PATTERNS:
        - Factory Pattern: Creates complex object graph
        - Dependency Injection: Passes dependencies to stages
        - Guard Clause: Early returns for unavailable dependencies
    """
    stages = []

    # Initialize centralized AI Query Service (KG→RAG→LLM pipeline)
    ai_service = None
    if AI_QUERY_SERVICE_AVAILABLE and orchestrator.llm_client:
        try:
            orchestrator.logger.log("Initializing centralized AI Query Service...", "INFO")
            ai_service = create_ai_query_service(
                llm_client=orchestrator.llm_client,
                rag=orchestrator.rag,
                logger=orchestrator.logger,
                verbose=orchestrator.verbose
            )
            orchestrator.logger.log("✅ AI Query Service initialized successfully", "SUCCESS")
            orchestrator.logger.log("   All agents will use KG-First approach for token optimization", "INFO")
        except Exception as e:
            orchestrator.logger.log(f"⚠️  AI Query Service initialization failed: {e}", "WARNING")
            orchestrator.logger.log("   Agents will use direct LLM calls (no KG optimization)", "WARNING")
            ai_service = None

    # Initialize Intelligent Router for AI-powered stage selection
    orchestrator.intelligent_router = None
    if INTELLIGENT_ROUTER_AVAILABLE:
        try:
            orchestrator.logger.log("Initializing Intelligent Router for dynamic stage selection...", "INFO")
            orchestrator.intelligent_router = IntelligentRouter(
                ai_service=ai_service,
                logger=orchestrator.logger,
                config=orchestrator.config
            )
            orchestrator.logger.log("✅ Intelligent Router initialized successfully", "SUCCESS")
            orchestrator.logger.log("   Pipeline will skip unnecessary stages based on task requirements", "INFO")
        except Exception as e:
            orchestrator.logger.log(f"⚠️  Intelligent Router initialization failed: {e}", "WARNING")
            orchestrator.logger.log("   Pipeline will run all standard stages", "WARNING")
            orchestrator.intelligent_router = None

    # Requirements Parsing (new) - Parse requirements documents first
    if orchestrator.llm_client:
        stages.append(
            RequirementsParsingStage(
                logger=orchestrator.logger,
                rag=orchestrator.rag,
                messenger=orchestrator.messenger,
                supervisor=orchestrator.supervisor
                # Note: RequirementsParsingStage already integrated with AIQueryService
            )
        )

    # Sprint Planning (new) - Only if LLM client available
    if orchestrator.llm_client:
        stages.append(
            SprintPlanningStage(
                orchestrator.board,
                orchestrator.messenger,
                orchestrator.rag,
                orchestrator.logger,
                orchestrator.llm_client,
                config=orchestrator.config,
                observable=orchestrator.observable,
                supervisor=orchestrator.supervisor
            )
        )

    # Existing stages (now with AI Query Service)
    stages.extend([
        ProjectAnalysisStage(
            board=orchestrator.board,
            messenger=orchestrator.messenger,
            rag=orchestrator.rag,
            logger=orchestrator.logger,
            supervisor=orchestrator.supervisor,
            llm_client=orchestrator.llm_client,
            config=orchestrator.config
        )
    ])

    # Software Specification Document Generation (new) - After project analysis, before architecture
    # Intelligently decides if SSD is needed based on task complexity
    if orchestrator.llm_client:
        stages.append(
            SSDGenerationStage(
                llm_client=orchestrator.llm_client,
                rag=orchestrator.rag,
                logger=orchestrator.logger,
                verbose=orchestrator.verbose
            )
        )

    # Continue with remaining stages
    stages.extend([
        ArchitectureStage(
            orchestrator.board,
            orchestrator.messenger,
            orchestrator.rag,
            orchestrator.logger,
            supervisor=orchestrator.supervisor,
            llm_client=orchestrator.llm_client,
            ai_service=ai_service  # NEW: centralized KG-First service
        )
    ])

    # Project Review - Validate architecture and sprint plans
    if orchestrator.llm_client:
        stages.append(
            ProjectReviewStage(
                orchestrator.board,
                orchestrator.messenger,
                orchestrator.rag,
                orchestrator.logger,
                orchestrator.llm_client,
                config=orchestrator.config,
                observable=orchestrator.observable,
                supervisor=orchestrator.supervisor
            )
        )

    # Research Stage - Retrieve code examples before development
    # Searches GitHub, HuggingFace, and local filesystem for relevant examples
    # Stores examples in RAG for developers to query during implementation
    stages.append(
        ResearchStage(
            rag_agent=orchestrator.rag,
            sources=["local", "github", "huggingface"],
            max_examples_per_source=5,
            timeout_seconds=30
        )
    )

    # Continue with existing stages
    stages.extend([
        DependencyValidationStage(orchestrator.board, orchestrator.messenger, orchestrator.logger),
        DevelopmentStage(
            orchestrator.board,
            orchestrator.rag,
            orchestrator.logger,
            observable=orchestrator.observable,
            supervisor=orchestrator.supervisor
        ),
        # Arbitration - adjudicator selects winner when dev group (2+ developers) competes
        ArbitrationStage(
            logger=orchestrator.logger,
            messenger=None,  # Messenger doesn't support register_handler() - arbitration doesn't need it
            observable=orchestrator.observable,
            supervisor=orchestrator.supervisor,
            ai_service=ai_service
        ),
        # Validation tests ONLY the winner
        ValidationStage(
            orchestrator.board,
            orchestrator.test_runner,
            orchestrator.logger,
            messenger=orchestrator.messenger,
            observable=orchestrator.observable,
            supervisor=orchestrator.supervisor
        ),
        # UI/UX evaluates ONLY the winner (if needed)
        UIUXStage(
            orchestrator.board,
            orchestrator.messenger,
            orchestrator.rag,
            orchestrator.logger,
            observable=orchestrator.observable,
            supervisor=orchestrator.supervisor,
            config=orchestrator.config,
            ai_service=ai_service  # NEW: centralized KG-First service
        ),
        # Code Review reviews ONLY the winner
        CodeReviewStage(
            orchestrator.messenger,
            orchestrator.rag,
            orchestrator.logger,
            observable=orchestrator.observable,
            supervisor=orchestrator.supervisor,
            ai_service=ai_service  # NEW: centralized KG-First service
        ),
        # Integration and Testing proceed with winner
        IntegrationStage(
            orchestrator.board,
            orchestrator.messenger,
            orchestrator.rag,
            orchestrator.test_runner,
            orchestrator.logger,
            observable=orchestrator.observable,
            supervisor=orchestrator.supervisor
        ),
        TestingStage(orchestrator.board, orchestrator.messenger, orchestrator.rag, orchestrator.test_runner, orchestrator.logger)
    ])

    return stages
