#!/usr/bin/env python3
"""
WHY: Handle all query operations on the knowledge graph
RESPONSIBILITY: Read-only queries for files, functions, dependencies, and analysis
PATTERNS: Query Object pattern - encapsulate queries as methods

No mutations - only reads. All functions return Lists or Dicts.
"""

from typing import List, Dict, Optional, Any


class QueryOperations:
    """
    WHY: Encapsulate all read-only query operations
    RESPONSIBILITY: Execute queries and return structured results
    PATTERNS: Delegation pattern - receives database connection
    """

    def __init__(self, db: Any):
        """
        Initialize with database connection

        Args:
            db: Memgraph database connection
        """
        self.db = db

    def get_file(self, path: str) -> Optional[Dict]:
        """
        Get file details

        WHY: Retrieve metadata for a specific file

        Args:
            path: File path

        Returns:
            File data or None if not found
        """
        query = """
        MATCH (f:File {path: $path})
        RETURN f.path as path,
               f.language as language,
               f.lines as lines,
               f.module as module,
               f.last_modified as last_modified
        """

        results = list(self.db.execute_and_fetch(query, {"path": path}))
        return results[0] if results else None

    def get_impact_analysis(self, file_path: str, depth: int = 3) -> List[Dict]:
        """
        Analyze what depends on this file

        WHY: Identify blast radius of changes for risk assessment

        Args:
            file_path: File to analyze
            depth: How many levels deep to traverse (guard against infinite traversal)

        Returns:
            List of dependent files with distance metric
        """
        query = f"""
        MATCH path = (f:File {{path: $file_path}})<-[:IMPORTS|CALLS|DEPENDS_ON*1..{depth}]-(dependent:File)
        RETURN DISTINCT dependent.path as dependent_path,
               dependent.language as language,
               dependent.module as module,
               length(path) as distance
        ORDER BY distance
        """

        results = list(self.db.execute_and_fetch(query, {"file_path": file_path}))
        return results

    def get_circular_dependencies(self) -> List[Dict]:
        """
        Find all circular dependencies

        WHY: Detect architectural problems and dependency cycles

        Returns:
            List of cycles with paths
        """
        query = """
        MATCH path = (f:File)-[:IMPORTS*]->(f)
        WHERE length(path) > 1
        RETURN [node in nodes(path) | node.path] as cycle,
               length(path) as cycle_length
        ORDER BY cycle_length
        """

        results = list(self.db.execute_and_fetch(query))
        return results

    def get_untested_functions(self) -> List[Dict]:
        """
        Find functions without test coverage

        WHY: Identify testing gaps for quality improvement

        Returns:
            List of untested public functions ordered by complexity
        """
        query = """
        MATCH (fn:Function)
        WHERE fn.public = true
        AND NOT EXISTS((t:Test)-[:COVERS]->(fn))
        RETURN fn.name as function_name,
               fn.file_path as file_path,
               fn.complexity as complexity
        ORDER BY fn.complexity DESC
        """

        results = list(self.db.execute_and_fetch(query))
        return results

    def get_decision_lineage(self, adr_id: str) -> List[Dict]:
        """
        Get decision chain for an ADR

        WHY: Understand how decisions influenced each other

        Args:
            adr_id: ADR identifier

        Returns:
            Chain of related decisions
        """
        query = """
        MATCH path = (adr:ADR {adr_id: $adr_id})<-[:INFLUENCED_BY*]-(related:ADR)
        RETURN [node in nodes(path) | {
            adr_id: node.adr_id,
            title: node.title,
            status: node.status
        }] as decision_chain
        """

        results = list(self.db.execute_and_fetch(query, {"adr_id": adr_id}))
        return results[0]["decision_chain"] if results else []

    def get_architectural_violations(
        self,
        forbidden_patterns: List[tuple]
    ) -> List[Dict]:
        """
        Find architectural violations

        WHY: Enforce layered architecture and prevent forbidden dependencies

        Args:
            forbidden_patterns: List of (from_module, to_module) tuples

        Returns:
            List of violations with details
        """
        if not forbidden_patterns:
            return []

        violations = []

        for from_module, to_module in forbidden_patterns:
            query = """
            MATCH (f1:File {module: $from_module})-[:IMPORTS]->(f2:File {module: $to_module})
            RETURN f1.path as violator,
                   f2.path as forbidden_import,
                   $from_module as from_module,
                   $to_module as to_module
            """

            results = list(self.db.execute_and_fetch(
                query,
                {"from_module": from_module, "to_module": to_module}
            ))
            violations.extend(results)

        return violations

    def get_file_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """
        Get all dependencies for a file

        WHY: Understand what a file depends on and what depends on it

        Args:
            file_path: File to query

        Returns:
            Dict with imports and imported_by lists
        """
        # Get imports
        imports_query = """
        MATCH (f:File {path: $file_path})-[:IMPORTS]->(imported:File)
        RETURN imported.path as path
        """

        imports = [
            r["path"]
            for r in self.db.execute_and_fetch(imports_query, {"file_path": file_path})
        ]

        # Get reverse dependencies
        imported_by_query = """
        MATCH (f:File {path: $file_path})<-[:IMPORTS]-(importer:File)
        RETURN importer.path as path
        """

        imported_by = [
            r["path"]
            for r in self.db.execute_and_fetch(imported_by_query, {"file_path": file_path})
        ]

        return {
            "imports": imports,
            "imported_by": imported_by
        }

    def get_graph_stats(self) -> Dict[str, int]:
        """
        Get graph statistics

        WHY: Monitor graph size and health

        Returns:
            Dict with node and relationship counts
        """
        stats = {}

        # Dispatch table for stat queries
        stat_queries = {
            "files": "MATCH (f:File) RETURN count(f) as count",
            "classes": "MATCH (c:Class) RETURN count(c) as count",
            "functions": "MATCH (fn:Function) RETURN count(fn) as count",
            "relationships": "MATCH ()-[r]->() RETURN count(r) as count",
        }

        for stat_name, query in stat_queries.items():
            result = list(self.db.execute_and_fetch(query))
            stats[stat_name] = result[0]["count"] if result else 0

        return stats


__all__ = ["QueryOperations"]
