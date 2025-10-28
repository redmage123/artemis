#!/usr/bin/env python3
"""
Workflow Registry - Central Workflow Catalog and Lookup

WHAT:
Central registry for all recovery workflows. Provides O(1) lookup of workflows
by issue type, validation of workflow completeness, and workflow metadata.

WHY:
SupervisorAgent needs fast, reliable access to recovery workflows. Registry
pattern provides single source of truth for all workflows, enables validation
that all issue types have workflows, and supports runtime introspection.

RESPONSIBILITY:
- Maintain complete catalog of all workflows
- Provide fast workflow lookup by issue type
- Validate workflow completeness at startup
- Support workflow introspection and metadata queries

PATTERNS:
- Registry Pattern: Central catalog of workflows
- Singleton Pattern: Single global registry instance
- Lazy Initialization: Build workflows on first access
- Validation: Ensure all issue types have workflows

INTEGRATION:
- Used by: SupervisorAgent, RecoveryEngine
- Uses: WorkflowBuilder for workflow construction
- Validates: All IssueType values have corresponding workflows

EXAMPLE:
    registry = WorkflowRegistry()
    workflow = registry.get_workflow(IssueType.TIMEOUT)
    all_workflows = registry.get_all_workflows()
    registry.validate_completeness()  # Raises if workflows missing
"""

from typing import Dict, Any, Optional, List, Set
from state_machine import IssueType, Workflow
from workflows.workflow_builder import WorkflowBuilder


# ============================================================================
# WORKFLOW REGISTRY
# ============================================================================

class WorkflowRegistry:
    """
    Central registry for recovery workflows

    WHAT:
    Singleton-style registry that maintains complete catalog of all recovery
    workflows and provides fast lookup, validation, and introspection.

    WHY:
    Centralized workflow management enables:
    - Fast O(1) workflow lookup by issue type
    - Validation that all issue types have workflows
    - Runtime introspection of available workflows
    - Easy testing and debugging of workflow coverage

    RESPONSIBILITY:
    - Build and cache all workflows on initialization
    - Provide workflow lookup by issue type
    - Validate workflow completeness
    - Support workflow metadata queries

    PATTERNS:
    - Registry Pattern: Central catalog
    - Lazy Initialization: Build on first use
    - Cache: Store built workflows for reuse
    - Guard Clauses: Validate inputs (no nested ifs)

    USAGE:
        registry = WorkflowRegistry()
        workflow = registry.get_workflow(IssueType.TIMEOUT)
    """

    def __init__(self):
        """
        Initialize workflow registry

        WHAT:
        Creates registry and builds all workflows.

        WHY:
        Eager initialization ensures workflows are validated at startup
        rather than at runtime when failures occur.
        """
        self._workflows: Dict[IssueType, Workflow] = {}
        self._build_workflows()

    def _build_workflows(self) -> None:
        """
        Build all workflows and populate registry

        WHAT:
        Uses WorkflowBuilder to construct all recovery workflows
        and stores them in internal catalog.

        WHY:
        Centralizes workflow construction and enables validation
        that all issue types have workflows.
        """
        self._workflows = WorkflowBuilder.build_all_workflows()

    def get_workflow(self, issue_type: IssueType) -> Optional[Workflow]:
        """
        Get workflow for specific issue type

        WHAT:
        Returns recovery workflow for given issue type, or None if not found.

        WHY:
        Primary lookup method used by SupervisorAgent to retrieve
        recovery workflow when issue is detected.

        ARGS:
            issue_type: Type of issue requiring recovery

        RETURNS:
            Workflow if found, None otherwise

        EXAMPLE:
            workflow = registry.get_workflow(IssueType.TIMEOUT)
        """
        if not isinstance(issue_type, IssueType):
            return None

        return self._workflows.get(issue_type)

    def has_workflow(self, issue_type: IssueType) -> bool:
        """
        Check if workflow exists for issue type

        WHAT:
        Returns True if registry contains workflow for given issue type.

        WHY:
        Allows checking workflow availability before attempting retrieval.

        ARGS:
            issue_type: Type of issue to check

        RETURNS:
            True if workflow exists, False otherwise
        """
        if not isinstance(issue_type, IssueType):
            return False

        return issue_type in self._workflows

    def get_all_workflows(self) -> Dict[IssueType, Workflow]:
        """
        Get all workflows in registry

        WHAT:
        Returns complete catalog of all recovery workflows.

        WHY:
        Useful for testing, validation, and runtime introspection.

        RETURNS:
            Dict mapping issue types to workflows

        NOTE:
            Returns copy to prevent external modification
        """
        return dict(self._workflows)

    def get_workflow_count(self) -> int:
        """
        Get total number of workflows in registry

        WHAT:
        Returns count of registered workflows.

        WHY:
        Quick validation that expected number of workflows are registered.

        RETURNS:
            Number of workflows in registry
        """
        return len(self._workflows)

    def get_issue_types(self) -> Set[IssueType]:
        """
        Get all issue types with workflows

        WHAT:
        Returns set of all issue types that have registered workflows.

        WHY:
        Enables validation and introspection of workflow coverage.

        RETURNS:
            Set of issue types with workflows
        """
        return set(self._workflows.keys())

    def validate_completeness(self) -> bool:
        """
        Validate all issue types have workflows

        WHAT:
        Checks that every IssueType enum value has corresponding workflow.

        WHY:
        Ensures no issue types are missing workflows. Should be called
        at startup to catch configuration errors early.

        RETURNS:
            True if all issue types have workflows

        RAISES:
            ValueError: If any issue types lack workflows
        """
        all_issue_types = set(IssueType)
        registered_types = self.get_issue_types()

        missing_types = all_issue_types - registered_types
        if missing_types:
            missing_names = [t.name for t in missing_types]
            raise ValueError(
                f"Missing workflows for issue types: {', '.join(missing_names)}"
            )

        return True

    def get_workflow_summary(self) -> Dict[str, Any]:
        """
        Get summary of workflow registry

        WHAT:
        Returns metadata about registered workflows including counts
        by category and completeness status.

        WHY:
        Useful for monitoring, debugging, and validation.

        RETURNS:
            Dict with workflow statistics and metadata
        """
        return {
            "total_workflows": self.get_workflow_count(),
            "total_issue_types": len(IssueType),
            "coverage_complete": len(self.get_issue_types()) == len(IssueType),
            "registered_types": [t.name for t in self.get_issue_types()],
        }

    def __repr__(self) -> str:
        """String representation of registry"""
        return f"WorkflowRegistry(workflows={self.get_workflow_count()})"

    def __len__(self) -> int:
        """Support len() operation"""
        return self.get_workflow_count()


# ============================================================================
# GLOBAL REGISTRY INSTANCE (OPTIONAL)
# ============================================================================

# Global registry instance for convenience (optional usage)
# Most code should create their own registry instance for testability
_global_registry: Optional[WorkflowRegistry] = None


def get_global_registry() -> WorkflowRegistry:
    """
    Get global workflow registry instance

    WHAT:
    Returns singleton global registry, creating it if needed.

    WHY:
    Convenience function for code that doesn't need custom registry.
    Note: Creating own registry instance is preferred for testability.

    RETURNS:
        Global WorkflowRegistry instance
    """
    global _global_registry

    if _global_registry is None:
        _global_registry = WorkflowRegistry()

    return _global_registry


def reset_global_registry() -> None:
    """
    Reset global registry (for testing)

    WHAT:
    Clears global registry, forcing recreation on next access.

    WHY:
    Useful for testing to ensure clean state between tests.
    """
    global _global_registry
    _global_registry = None
