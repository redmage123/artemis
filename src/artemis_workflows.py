#!/usr/bin/env python3
"""
Artemis Recovery Workflows - Automated Issue Resolution

BACKWARD COMPATIBILITY WRAPPER
This module re-exports all components from the workflows_core package.
All new code should import from workflows_core package directly.

Example:
    # Old (still works):
    from artemis_workflows import WorkflowBuilder

    # New (preferred):
    from workflows_core import WorkflowBuilder

MIGRATION NOTES:
---------------
The original 718-line artemis_workflows.py has been refactored into a modular
workflows_core package with the following structure:

1. models.py (27 lines) - Re-exports workflow models from state_machine
2. infrastructure_workflows.py (190 lines) - 5 infrastructure workflows
3. code_workflows.py (149 lines) - 4 code workflows
4. dependency_workflows.py (122 lines) - 3 dependency workflows
5. llm_workflows.py (167 lines) - 4 LLM workflows
6. stage_workflows.py (137 lines) - 4 stage workflows
7. multiagent_workflows.py (117 lines) - 3 multi-agent workflows
8. data_workflows.py (120 lines) - 3 data workflows
9. system_workflows.py (117 lines) - 3 system workflows
10. workflow_builder.py (285 lines) - Main builder facade
11. __init__.py (106 lines) - Package exports

TOTAL: 1,537 lines (modular) vs 718 lines (monolithic)
The increase in line count is due to comprehensive documentation following
WHY/RESPONSIBILITY/PATTERNS standards on every module.

BENEFITS OF REFACTORING:
-----------------------
- Single Responsibility: Each builder handles one workflow category
- Guard Clauses: Max 1 level nesting throughout
- Type Hints: Full typing on all functions
- Dispatch Tables: No elif chains
- Comprehensive Documentation: WHY/RESPONSIBILITY/PATTERNS on every module
- Maintainability: Easy to find and modify specific workflow categories
- Testability: Each builder can be tested independently
- Extensibility: New workflow categories can be added without modifying existing code

Workflow Categories:
1. Infrastructure Issues (timeout, memory, disk, network)
2. Code Issues (compilation, tests, security, linting)
3. Dependency Issues (missing deps, version conflicts)
4. LLM Issues (API errors, timeouts, rate limits)
5. Stage Issues (architecture, code review, integration)
6. Multi-Agent Issues (arbitration, conflicts)
7. Data Issues (invalid card, corrupted state, RAG)
8. System Issues (zombies, file locks, permissions)
"""

# Re-export all public components from workflows_core for backward compatibility

# Models (re-exported from state_machine)
from workflows_core.models import (
    Workflow,
    WorkflowAction,
    IssueType,
    PipelineState,
)

# Main builder (facade for all specialized builders)
from workflows_core.workflow_builder import WorkflowBuilder

# Specialized builders (for advanced usage)
from workflows_core.infrastructure_workflows import InfrastructureWorkflowBuilder
from workflows_core.code_workflows import CodeWorkflowBuilder
from workflows_core.dependency_workflows import DependencyWorkflowBuilder
from workflows_core.llm_workflows import LLMWorkflowBuilder
from workflows_core.stage_workflows import StageWorkflowBuilder
from workflows_core.multiagent_workflows import MultiAgentWorkflowBuilder
from workflows_core.data_workflows import DataWorkflowBuilder
from workflows_core.system_workflows import SystemWorkflowBuilder


__all__ = [
    # Models
    "Workflow",
    "WorkflowAction",
    "IssueType",
    "PipelineState",

    # Main builder (primary interface)
    "WorkflowBuilder",

    # Specialized builders (advanced usage)
    "InfrastructureWorkflowBuilder",
    "CodeWorkflowBuilder",
    "DependencyWorkflowBuilder",
    "LLMWorkflowBuilder",
    "StageWorkflowBuilder",
    "MultiAgentWorkflowBuilder",
    "DataWorkflowBuilder",
    "SystemWorkflowBuilder",
]
