#!/usr/bin/env python3
"""
WHY: Provide unified package interface for knowledge_graph
RESPONSIBILITY: Export all public classes and functions for backward compatibility
PATTERNS: Facade pattern for package exports

This package provides graph-based code analysis including:
- Dependency tracking
- Impact analysis
- Architectural validation
- Decision lineage
- Multi-hop queries
"""

# Main orchestrator
from .knowledge_graph import KnowledgeGraph, MEMGRAPH_AVAILABLE

# Data models
from .models import (
    CodeFile,
    CodeClass,
    CodeFunction,
    ADR,
    Requirement,
    Task,
    CodeReview,
)

# Operation classes (for advanced usage)
from .graph_operations import GraphOperations
from .query_operations import QueryOperations
from .relationship_operations import RelationshipOperations
from .storage_operations import StorageOperations

# Query builders (for advanced usage)
from .query_builder import QueryBuilder, CypherQueryTemplates


__all__ = [
    # Main class
    "KnowledgeGraph",
    "MEMGRAPH_AVAILABLE",

    # Data models
    "CodeFile",
    "CodeClass",
    "CodeFunction",
    "ADR",
    "Requirement",
    "Task",
    "CodeReview",

    # Operation classes
    "GraphOperations",
    "QueryOperations",
    "RelationshipOperations",
    "StorageOperations",

    # Query builders
    "QueryBuilder",
    "CypherQueryTemplates",
]
