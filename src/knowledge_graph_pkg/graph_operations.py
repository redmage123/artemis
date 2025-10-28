#!/usr/bin/env python3
"""
WHY: Handle creation of nodes in the knowledge graph
RESPONSIBILITY: Add files, classes, functions, ADRs, requirements, tasks, and code reviews
PATTERNS: Single Responsibility - only creates nodes, no queries or relationships

All functions return node IDs and follow guard clause pattern.
"""

from typing import List, Optional, Any
from datetime import datetime


class GraphOperations:
    """
    WHY: Encapsulate all node creation operations
    RESPONSIBILITY: Create and update graph nodes
    PATTERNS: Delegation pattern - receives database connection
    """

    def __init__(self, db: Any):
        """
        Initialize with database connection

        Args:
            db: Memgraph database connection
        """
        self.db = db

    def add_file(
        self,
        path: str,
        language: str,
        lines: int = 0,
        module: Optional[str] = None
    ) -> str:
        """
        Add a code file to the graph

        WHY: Track files for dependency and impact analysis

        Args:
            path: File path (serves as unique ID)
            language: Programming language
            lines: Number of lines
            module: Module/package name

        Returns:
            File path (ID)
        """
        query = """
        MERGE (f:File {path: $path})
        SET f.language = $language,
            f.lines = $lines,
            f.last_modified = $last_modified,
            f.module = $module
        RETURN f.path
        """

        self.db.execute_and_fetch(
            query,
            {
                "path": path,
                "language": language,
                "lines": lines,
                "last_modified": datetime.now().isoformat(),
                "module": module
            }
        )

        return path

    def add_class(
        self,
        name: str,
        file_path: str,
        public: bool = True,
        abstract: bool = False,
        lines: int = 0
    ) -> str:
        """
        Add a class to the graph

        WHY: Track class definitions for architectural analysis

        Args:
            name: Class name
            file_path: File containing the class
            public: Is class public?
            abstract: Is class abstract?
            lines: Number of lines

        Returns:
            Class name (ID)
        """
        query = """
        MATCH (f:File {path: $file_path})
        MERGE (c:Class {name: $name, file_path: $file_path})
        SET c.public = $public,
            c.abstract = $abstract,
            c.lines = $lines
        MERGE (f)-[:CONTAINS]->(c)
        RETURN c.name
        """

        self.db.execute_and_fetch(
            query,
            {
                "name": name,
                "file_path": file_path,
                "public": public,
                "abstract": abstract,
                "lines": lines
            }
        )

        return name

    def add_function(
        self,
        name: str,
        file_path: str,
        class_name: Optional[str] = None,
        params: Optional[List[str]] = None,
        returns: Optional[str] = None,
        public: bool = True,
        complexity: int = 1
    ) -> str:
        """
        Add a function to the graph

        WHY: Track functions for complexity and coverage analysis

        Args:
            name: Function name
            file_path: File containing function
            class_name: Class name if method
            params: Parameter names
            returns: Return type
            public: Is function public?
            complexity: Cyclomatic complexity

        Returns:
            Function name (ID)
        """
        if params is None:
            params = []

        query_func = """
        MATCH (f:File {path: $file_path})
        MERGE (fn:Function {name: $name, file_path: $file_path})
        SET fn.params = $params,
            fn.returns = $returns,
            fn.public = $public,
            fn.complexity = $complexity,
            fn.class_name = $class_name
        MERGE (f)-[:CONTAINS]->(fn)
        RETURN fn.name
        """

        self.db.execute_and_fetch(
            query_func,
            {
                "name": name,
                "file_path": file_path,
                "params": params,
                "returns": returns,
                "public": public,
                "complexity": complexity,
                "class_name": class_name
            }
        )

        # If method, link to class
        if not class_name:
            return name

        query_method = """
        MATCH (c:Class {name: $class_name, file_path: $file_path})
        MATCH (fn:Function {name: $name, file_path: $file_path})
        MERGE (c)-[:HAS_METHOD]->(fn)
        """
        self.db.execute(
            query_method,
            {
                "class_name": class_name,
                "file_path": file_path,
                "name": name
            }
        )

        return name

    def add_adr(
        self,
        adr_id: str,
        title: str,
        status: str,
        rationale: Optional[str] = None,
        impacts: Optional[List[str]] = None
    ) -> str:
        """
        Add an Architecture Decision Record

        WHY: Track architectural decisions and their impact on code

        Args:
            adr_id: ADR identifier (e.g., "ADR-001")
            title: Decision title
            status: proposed, accepted, rejected, deprecated, superseded
            rationale: Why this decision was made
            impacts: List of file paths impacted

        Returns:
            ADR ID
        """
        query = """
        MERGE (adr:ADR {adr_id: $adr_id})
        SET adr.title = $title,
            adr.date = $date,
            adr.status = $status,
            adr.rationale = $rationale
        RETURN adr.adr_id
        """

        self.db.execute_and_fetch(
            query,
            {
                "adr_id": adr_id,
                "title": title,
                "date": datetime.now().isoformat(),
                "status": status,
                "rationale": rationale
            }
        )

        # Link to impacted files
        if not impacts:
            return adr_id

        for file_path in impacts:
            impact_query = """
            MATCH (adr:ADR {adr_id: $adr_id})
            MATCH (f:File {path: $file_path})
            MERGE (adr)-[:IMPACTS]->(f)
            """
            self.db.execute(impact_query, {"adr_id": adr_id, "file_path": file_path})

        return adr_id

    def add_requirement(
        self,
        req_id: str,
        title: str,
        type: str,
        priority: str,
        status: str = "active"
    ) -> str:
        """
        Add a requirement to the graph

        WHY: Track requirements and their implementation status

        Args:
            req_id: Requirement ID (e.g., "REQ-F-001")
            title: Requirement title
            type: functional, non_functional, use_case, data, integration
            priority: critical, high, medium, low
            status: active, implemented, deprecated

        Returns:
            Requirement ID
        """
        query = """
        MERGE (req:Requirement {req_id: $req_id})
        SET req.title = $title,
            req.type = $type,
            req.priority = $priority,
            req.status = $status,
            req.created = $created
        RETURN req.req_id
        """

        self.db.execute_and_fetch(
            query,
            {
                "req_id": req_id,
                "title": title,
                "type": type,
                "priority": priority,
                "status": status,
                "created": datetime.now().isoformat()
            }
        )

        return req_id

    def add_task(
        self,
        card_id: str,
        title: str,
        priority: str,
        status: str,
        assigned_agents: Optional[List[str]] = None
    ) -> str:
        """
        Add a task/card to the graph

        WHY: Track development tasks and their relationships

        Args:
            card_id: Card identifier
            title: Task title
            priority: high, medium, low
            status: backlog, in_progress, review, done
            assigned_agents: List of agent names

        Returns:
            Card ID
        """
        if assigned_agents is None:
            assigned_agents = []

        query = """
        MERGE (task:Task {card_id: $card_id})
        SET task.title = $title,
            task.priority = $priority,
            task.status = $status,
            task.assigned_agents = $assigned_agents,
            task.created = $created
        RETURN task.card_id
        """

        self.db.execute_and_fetch(
            query,
            {
                "card_id": card_id,
                "title": title,
                "priority": priority,
                "status": status,
                "assigned_agents": assigned_agents,
                "created": datetime.now().isoformat()
            }
        )

        return card_id

    def add_code_review(
        self,
        review_id: str,
        card_id: str,
        status: str,
        score: int,
        critical_issues: int = 0,
        high_issues: int = 0
    ) -> str:
        """
        Add a code review result to the graph

        WHY: Track code quality metrics and review results

        Args:
            review_id: Review identifier
            card_id: Associated card ID
            status: PASS or FAIL
            score: Overall score (0-100)
            critical_issues: Number of critical issues
            high_issues: Number of high severity issues

        Returns:
            Review ID
        """
        query = """
        MERGE (review:CodeReview {review_id: $review_id})
        SET review.card_id = $card_id,
            review.status = $status,
            review.score = $score,
            review.critical_issues = $critical_issues,
            review.high_issues = $high_issues,
            review.created = $created
        RETURN review.review_id
        """

        self.db.execute_and_fetch(
            query,
            {
                "review_id": review_id,
                "card_id": card_id,
                "status": status,
                "score": score,
                "critical_issues": critical_issues,
                "high_issues": high_issues,
                "created": datetime.now().isoformat()
            }
        )

        # Link review to task
        link_query = """
        MATCH (review:CodeReview {review_id: $review_id})
        MATCH (task:Task {card_id: $card_id})
        MERGE (task)-[:HAS_REVIEW]->(review)
        """
        self.db.execute(link_query, {"review_id": review_id, "card_id": card_id})

        return review_id

    def update_file_metrics(
        self,
        file_path: str,
        lines: int,
        complexity: Optional[int] = None
    ) -> bool:
        """
        Update file metrics

        WHY: Keep file metrics current as code evolves

        Args:
            file_path: File to update
            lines: New line count
            complexity: Average complexity

        Returns:
            Success status
        """
        query = """
        MATCH (f:File {path: $file_path})
        SET f.lines = $lines,
            f.last_modified = $last_modified
        RETURN f.path
        """

        params = {
            "file_path": file_path,
            "lines": lines,
            "last_modified": datetime.now().isoformat()
        }

        if complexity is not None:
            query = query.replace(
                "f.last_modified = $last_modified",
                "f.last_modified = $last_modified, f.complexity = $complexity"
            )
            params["complexity"] = complexity

        results = list(self.db.execute_and_fetch(query, params))
        return len(results) > 0

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file and all its relationships

        WHY: Clean up graph when files are removed

        Args:
            file_path: File to delete

        Returns:
            Success status
        """
        query = """
        MATCH (f:File {path: $file_path})
        DETACH DELETE f
        """

        self.db.execute(query, {"file_path": file_path})
        return True


__all__ = ["GraphOperations"]
