"""
Developer subpackage - Modularized developer agent components.

Part of: agents

This package contains the decomposed StandaloneDeveloperAgent components:
- models: Data models for developer workflows
- tdd_phases: Red/Green/Refactor phase execution
- rag_integration: RAG queries for examples and feedback
- llm_client_wrapper: LLM interaction and streaming
- file_manager: File I/O operations
- test_runner: Test execution integration
- report_generator: Solution report generation
- developer: Main orchestrator class (composition-based)
"""

# Export main Developer class
from agents.developer.developer import Developer

# Export key models
from agents.developer.models import (
    WorkflowType,
    TaskType,
    ExecutionStrategy,
    WorkflowContext,
    PhaseResult
)

# Export specialized components (optional - for advanced usage)
from agents.developer.file_manager import FileManager
from agents.developer.test_runner_wrapper import DeveloperTestRunner
from agents.developer.report_generator import ReportGenerator
from agents.developer.rag_integration import RAGIntegration
from agents.developer.llm_client_wrapper import LLMClientWrapper
from agents.developer.tdd_phases import TDDPhases

__all__ = [
    # Main class
    "Developer",

    # Models
    "WorkflowType",
    "TaskType",
    "ExecutionStrategy",
    "WorkflowContext",
    "PhaseResult",

    # Components (for advanced usage)
    "FileManager",
    "DeveloperTestRunner",
    "ReportGenerator",
    "RAGIntegration",
    "LLMClientWrapper",
    "TDDPhases",
]
