#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

Original file: 2,792 lines
Refactored to: agents/developer/ (8 modules, 2,515 lines)
This wrapper: ~100 lines (96.4% reduction!)

DEPRECATION NOTICE:
This module provides backward compatibility for existing code that imports
StandaloneDeveloperAgent. New code should use:

    from agents.developer import Developer

The StandaloneDeveloperAgent class now wraps the new modular Developer class.

WHY THIS REFACTORING:
- Original: Monolithic 2,792-line file with 73 methods (God object anti-pattern)
- Refactored: 8 specialized modules with single responsibilities
- Modules: FileManager, RAGIntegration, LLMClientWrapper, TDDPhases, ReportGenerator,
           DeveloperTestRunner, models, Developer (main orchestrator)
- Benefits: Easier testing, better separation of concerns, maintainable

ARCHITECTURE:
- agents/developer/developer.py: Main orchestrator (composition pattern)
- agents/developer/file_manager.py: File I/O operations
- agents/developer/test_runner_wrapper.py: Test execution
- agents/developer/rag_integration.py: RAG queries for examples/feedback
- agents/developer/llm_client_wrapper.py: LLM API calls with streaming validation
- agents/developer/tdd_phases.py: Red-Green-Refactor TDD workflow
- agents/developer/report_generator.py: Solution report generation
- agents/developer/models.py: Data models and enums
"""

from pathlib import Path
from typing import Dict, Optional

# Re-export the new modular Developer class
from agents.developer import Developer

# Re-export models for backward compatibility
from agents.developer.models import (
    WorkflowType,
    TaskType,
    ExecutionStrategy,
    WorkflowContext,
    PhaseResult
)


class StandaloneDeveloperAgent(Developer):
    """
    BACKWARD COMPATIBILITY WRAPPER

    Wraps the new modular Developer class to maintain existing API.

    DEPRECATED: Use agents.developer.Developer instead.

    This class simply inherits from Developer and maintains the same
    signature and behavior as the original StandaloneDeveloperAgent.

    Args:
        developer_name: "developer-a" or "developer-b"
        developer_type: "conservative" or "aggressive"
        llm_provider: "openai" or "anthropic"
        llm_model: Specific model (optional, uses default)
        logger: Logger implementation
        rag_agent: RAG agent for prompt retrieval (optional)
        ai_service: AI Query Service for KG-First queries (optional)
    """

    def __init__(
        self,
        developer_name: str,
        developer_type: str,
        llm_provider: str = "openai",
        llm_model: Optional[str] = None,
        logger = None,
        rag_agent = None,
        ai_service = None
    ):
        """
        Initialize via new Developer class

        Simply delegates to Developer.__init__() with same arguments.
        """
        # Call parent (Developer) constructor
        super().__init__(
            developer_name=developer_name,
            developer_type=developer_type,
            llm_provider=llm_provider,
            llm_model=llm_model,
            logger=logger,
            rag_agent=rag_agent,
            ai_service=ai_service
        )

        # Log deprecation warning
        if logger:
            logger.log(
                "⚠️  DEPRECATION WARNING: StandaloneDeveloperAgent is deprecated. "
                "Use agents.developer.Developer instead.",
                "WARNING"
            )


# Factory function for backward compatibility
def create_developer_agent(
    developer_name: str,
    developer_type: str,
    llm_provider: str = "openai",
    llm_model: Optional[str] = None,
    logger = None,
    rag_agent = None,
    ai_service = None
) -> Developer:
    """
    Factory function to create developer agent

    Returns:
        Developer instance (new modular implementation)
    """
    return Developer(
        developer_name=developer_name,
        developer_type=developer_type,
        llm_provider=llm_provider,
        llm_model=llm_model,
        logger=logger,
        rag_agent=rag_agent,
        ai_service=ai_service
    )


# Re-export for backward compatibility
__all__ = [
    "StandaloneDeveloperAgent",
    "create_developer_agent",
    "Developer",
    "WorkflowType",
    "TaskType",
    "ExecutionStrategy",
    "WorkflowContext",
    "PhaseResult"
]
