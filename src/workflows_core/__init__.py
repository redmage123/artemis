#!/usr/bin/env python3
"""
WHY: Modular workflow construction system for Artemis pipeline recovery
RESPONSIBILITY: Package initialization and public API exports
PATTERNS: Facade pattern, package organization, public API definition

workflows_core - Artemis Recovery Workflows Package
===================================================

This package provides a modular system for building and managing recovery
workflows for all types of pipeline failures in the Artemis autonomous
development system.

PACKAGE STRUCTURE:
-----------------
- models.py: Re-exports workflow models from state_machine
- workflow_builder.py: Main builder facade aggregating all specialized builders
- infrastructure_workflows.py: Timeout, memory, disk, network workflows
- code_workflows.py: Compilation, test, security, linting workflows
- dependency_workflows.py: Missing deps, version conflicts, import workflows
- llm_workflows.py: LLM API, timeout, rate limit workflows
- stage_workflows.py: Architecture, code review, integration workflows
- multiagent_workflows.py: Arbitration, developer conflict, messenger workflows
- data_workflows.py: Invalid card, corrupted state, RAG workflows
- system_workflows.py: Zombie process, file lock, permission workflows

WORKFLOW CATEGORIES:
-------------------
1. Infrastructure (5 workflows): timeout, hanging process, memory, disk, network
2. Code (4 workflows): compilation, tests, security, linting
3. Dependencies (3 workflows): missing deps, version conflicts, imports
4. LLM (4 workflows): API errors, timeouts, rate limits, invalid responses
5. Stages (4 workflows): architecture, code review, integration, validation
6. Multi-agent (3 workflows): arbitration deadlock, developer conflicts, messenger
7. Data (3 workflows): invalid card, corrupted state, RAG errors
8. System (3 workflows): zombie processes, file locks, permissions

USAGE:
------
    # Build all workflows
    from workflows_core import WorkflowBuilder
    workflows = WorkflowBuilder.build_all_workflows()

    # Build specific workflow
    timeout_workflow = WorkflowBuilder.build_timeout_workflow()

    # Use specialized builders
    from workflows_core import InfrastructureWorkflowBuilder
    infra_workflows = InfrastructureWorkflowBuilder.build_all()

    # Import models
    from workflows_core import Workflow, WorkflowAction, IssueType, PipelineState
"""

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

    # Main builder
    "WorkflowBuilder",

    # Specialized builders
    "InfrastructureWorkflowBuilder",
    "CodeWorkflowBuilder",
    "DependencyWorkflowBuilder",
    "LLMWorkflowBuilder",
    "StageWorkflowBuilder",
    "MultiAgentWorkflowBuilder",
    "DataWorkflowBuilder",
    "SystemWorkflowBuilder",
]

__version__ = "1.0.0"
__author__ = "Artemis Development Team"
