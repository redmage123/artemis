#!/usr/bin/env python3
"""
WHY: Build complex Cypher queries programmatically
RESPONSIBILITY: Construct query strings with parameters
PATTERNS: Builder pattern for query construction

All functions return query strings and parameter dictionaries.
"""

from typing import Dict, List, Optional, Any, Tuple


class QueryBuilder:
    """
    WHY: Encapsulate Cypher query construction logic
    RESPONSIBILITY: Build parameterized queries for complex operations
    PATTERNS: Builder pattern with fluent interface
    """

    def __init__(self):
        """Initialize query builder"""
        self._query_parts: List[str] = []
        self._params: Dict[str, Any] = {}

    def match_file(self, file_path: str, alias: str = "f") -> "QueryBuilder":
        """
        Add MATCH clause for a file

        Args:
            file_path: File path to match
            alias: Node alias (default: 'f')

        Returns:
            Self for chaining
        """
        self._query_parts.append(f"MATCH ({alias}:File {{path: $file_path}})")
        self._params["file_path"] = file_path
        return self

    def match_class(self, class_name: str, alias: str = "c") -> "QueryBuilder":
        """
        Add MATCH clause for a class

        Args:
            class_name: Class name to match
            alias: Node alias (default: 'c')

        Returns:
            Self for chaining
        """
        self._query_parts.append(f"MATCH ({alias}:Class {{name: $class_name}})")
        self._params["class_name"] = class_name
        return self

    def match_function(self, function_name: str, alias: str = "fn") -> "QueryBuilder":
        """
        Add MATCH clause for a function

        Args:
            function_name: Function name to match
            alias: Node alias (default: 'fn')

        Returns:
            Self for chaining
        """
        self._query_parts.append(f"MATCH ({alias}:Function {{name: $function_name}})")
        self._params["function_name"] = function_name
        return self

    def where(self, condition: str) -> "QueryBuilder":
        """
        Add WHERE clause

        Args:
            condition: WHERE condition

        Returns:
            Self for chaining
        """
        self._query_parts.append(f"WHERE {condition}")
        return self

    def return_clause(self, fields: List[str]) -> "QueryBuilder":
        """
        Add RETURN clause

        Args:
            fields: Fields to return

        Returns:
            Self for chaining
        """
        self._query_parts.append(f"RETURN {', '.join(fields)}")
        return self

    def order_by(self, field: str, descending: bool = False) -> "QueryBuilder":
        """
        Add ORDER BY clause

        Args:
            field: Field to order by
            descending: Order descending (default: False)

        Returns:
            Self for chaining
        """
        order = "DESC" if descending else "ASC"
        self._query_parts.append(f"ORDER BY {field} {order}")
        return self

    def limit(self, count: int) -> "QueryBuilder":
        """
        Add LIMIT clause

        Args:
            count: Maximum results

        Returns:
            Self for chaining
        """
        self._query_parts.append(f"LIMIT {count}")
        return self

    def build(self) -> Tuple[str, Dict[str, Any]]:
        """
        Build final query and parameters

        Returns:
            Tuple of (query_string, parameters)
        """
        query = "\n".join(self._query_parts)
        return query, self._params

    def reset(self) -> "QueryBuilder":
        """
        Reset builder for reuse

        Returns:
            Self for chaining
        """
        self._query_parts = []
        self._params = {}
        return self


class CypherQueryTemplates:
    """
    WHY: Provide pre-built query templates for common operations
    RESPONSIBILITY: Static query templates with parameter placeholders
    PATTERNS: Template Method pattern
    """

    @staticmethod
    def get_file_with_dependencies(file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Build query to get file with all its dependencies

        Args:
            file_path: File path

        Returns:
            Tuple of (query, parameters)
        """
        query = """
        MATCH (f:File {path: $file_path})
        OPTIONAL MATCH (f)-[:IMPORTS]->(imported:File)
        OPTIONAL MATCH (f)<-[:IMPORTS]-(importer:File)
        RETURN f.path as path,
               f.language as language,
               f.lines as lines,
               collect(DISTINCT imported.path) as imports,
               collect(DISTINCT importer.path) as imported_by
        """
        return query, {"file_path": file_path}

    @staticmethod
    def get_complex_functions(min_complexity: int = 10) -> Tuple[str, Dict[str, Any]]:
        """
        Build query to find complex functions

        Args:
            min_complexity: Minimum cyclomatic complexity

        Returns:
            Tuple of (query, parameters)
        """
        query = """
        MATCH (fn:Function)
        WHERE fn.complexity >= $min_complexity
        RETURN fn.name as function_name,
               fn.file_path as file_path,
               fn.complexity as complexity,
               fn.class_name as class_name
        ORDER BY fn.complexity DESC
        """
        return query, {"min_complexity": min_complexity}

    @staticmethod
    def get_files_by_module(module_name: str) -> Tuple[str, Dict[str, Any]]:
        """
        Build query to get all files in a module

        Args:
            module_name: Module name

        Returns:
            Tuple of (query, parameters)
        """
        query = """
        MATCH (f:File {module: $module_name})
        RETURN f.path as path,
               f.language as language,
               f.lines as lines,
               f.last_modified as last_modified
        ORDER BY f.path
        """
        return query, {"module_name": module_name}

    @staticmethod
    def get_adr_with_impacts(adr_id: str) -> Tuple[str, Dict[str, Any]]:
        """
        Build query to get ADR with all impacted files

        Args:
            adr_id: ADR identifier

        Returns:
            Tuple of (query, parameters)
        """
        query = """
        MATCH (adr:ADR {adr_id: $adr_id})
        OPTIONAL MATCH (adr)-[:IMPACTS|IMPLEMENTED_BY]->(f:File)
        OPTIONAL MATCH (adr)-[:ADDRESSES]->(req:Requirement)
        RETURN adr.adr_id as adr_id,
               adr.title as title,
               adr.status as status,
               adr.rationale as rationale,
               collect(DISTINCT f.path) as impacted_files,
               collect(DISTINCT req.req_id) as requirements
        """
        return query, {"adr_id": adr_id}

    @staticmethod
    def get_requirement_status(req_id: str) -> Tuple[str, Dict[str, Any]]:
        """
        Build query to get requirement implementation status

        Args:
            req_id: Requirement identifier

        Returns:
            Tuple of (query, parameters)
        """
        query = """
        MATCH (req:Requirement {req_id: $req_id})
        OPTIONAL MATCH (adr:ADR)-[:ADDRESSES]->(req)
        OPTIONAL MATCH (task:Task)-[:IMPLEMENTS]->(req)
        RETURN req.req_id as req_id,
               req.title as title,
               req.status as status,
               req.priority as priority,
               collect(DISTINCT adr.adr_id) as addressing_adrs,
               collect(DISTINCT task.card_id) as implementing_tasks
        """
        return query, {"req_id": req_id}


__all__ = ["QueryBuilder", "CypherQueryTemplates"]
