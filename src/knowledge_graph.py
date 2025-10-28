#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

WHY: Maintain existing imports while code transitions to new package
RESPONSIBILITY: Re-export all public APIs from knowledge_graph_pkg
PATTERNS: Facade pattern - transparent delegation to new package

This file maintains backward compatibility with existing code.
All functionality has been moved to knowledge_graph_pkg/.

Original file was 968 lines. Now refactored into modular package:
- models.py (101 lines) - Data models
- graph_operations.py (421 lines) - Node creation operations
- query_operations.py (185 lines) - Query operations
- relationship_operations.py (174 lines) - Relationship operations
- storage_operations.py (89 lines) - Storage/persistence operations
- query_builder.py (226 lines) - Query builders
- knowledge_graph.py (270 lines) - Main orchestrator
- __init__.py (54 lines) - Package exports

Total: ~1,520 lines (with documentation and proper separation)
Reduction: 968 lines -> package structure with clear responsibilities

Usage (backward compatible):
    from knowledge_graph import KnowledgeGraph, CodeFile, ADR
    graph = KnowledgeGraph()
    graph.add_file("auth.py", language="python")

New usage (recommended):
    from knowledge_graph_pkg import KnowledgeGraph, CodeFile, ADR
    graph = KnowledgeGraph()
    graph.add_file("auth.py", language="python")
"""

# Import and re-export all public APIs from the new package
from knowledge_graph_pkg import *  # noqa: F401, F403

# Explicitly re-export main components for IDEs and type checkers
from knowledge_graph_pkg import (  # noqa: F401
    # Main class
    KnowledgeGraph,
    MEMGRAPH_AVAILABLE,

    # Data models
    CodeFile,
    CodeClass,
    CodeFunction,
    ADR,
    Requirement,
    Task,
    CodeReview,

    # Operation classes (for advanced usage)
    GraphOperations,
    QueryOperations,
    RelationshipOperations,
    StorageOperations,

    # Query builders (for advanced usage)
    QueryBuilder,
    CypherQueryTemplates,
)


# Maintain __all__ for star imports
__all__ = [
    "KnowledgeGraph",
    "MEMGRAPH_AVAILABLE",
    "CodeFile",
    "CodeClass",
    "CodeFunction",
    "ADR",
    "Requirement",
    "Task",
    "CodeReview",
    "GraphOperations",
    "QueryOperations",
    "RelationshipOperations",
    "StorageOperations",
    "QueryBuilder",
    "CypherQueryTemplates",
]


# Keep original example/test code for reference
if __name__ == "__main__":
    # Initialize knowledge graph
    graph = KnowledgeGraph(host="localhost", port=7687)

    print("🔧 Testing Knowledge Graph with GraphQL-style operations\n")

    # Add files
    print("Adding files...")
    graph.add_file("auth.py", "python", lines=250, module="api")
    graph.add_file("database.py", "python", lines=180, module="data")
    graph.add_file("api.py", "python", lines=320, module="api")

    # Add dependencies
    print("Adding dependencies...")
    graph.add_dependency("api.py", "auth.py", "IMPORTS")
    graph.add_dependency("api.py", "database.py", "IMPORTS")
    graph.add_dependency("auth.py", "database.py", "IMPORTS")

    # Add classes and functions
    print("Adding classes and functions...")
    graph.add_class("UserService", "auth.py", public=True, lines=80)
    graph.add_function(
        "login",
        "auth.py",
        class_name="UserService",
        params=["username", "password"],
        returns="Token"
    )

    # Query impact analysis (GraphQL-style)
    print("\n📊 Impact Analysis for database.py:")
    impacts = graph.get_impact_analysis("database.py", depth=2)
    for impact in impacts:
        print(f"  - {impact['dependent_path']} (distance: {impact['distance']})")

    # Get file dependencies (GraphQL-style)
    print("\n🔗 Dependencies for api.py:")
    deps = graph.get_file_dependencies("api.py")
    print(f"  Imports: {deps['imports']}")
    print(f"  Imported by: {deps['imported_by']}")

    # Get stats
    print("\n📈 Graph Statistics:")
    stats = graph.get_graph_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n✅ Knowledge Graph test complete!")
