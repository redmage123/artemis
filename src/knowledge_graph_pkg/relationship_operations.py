#!/usr/bin/env python3
"""
WHY: Handle relationship creation between nodes in the knowledge graph
RESPONSIBILITY: Create edges/relationships between existing nodes
PATTERNS: Single Responsibility - only creates relationships, no node creation

All functions return None and use guard clauses to fail fast.
"""

from typing import Any
from datetime import datetime


class RelationshipOperations:
    """
    WHY: Encapsulate all relationship/edge creation operations
    RESPONSIBILITY: Link existing nodes with typed relationships
    PATTERNS: Delegation pattern - receives database connection
    """

    def __init__(self, db: Any):
        """
        Initialize with database connection

        Args:
            db: Memgraph database connection
        """
        self.db = db

    def add_dependency(
        self,
        from_file: str,
        to_file: str,
        relationship: str = "IMPORTS"
    ) -> None:
        """
        Add a file dependency

        WHY: Track how files depend on each other for impact analysis

        Args:
            from_file: Source file
            to_file: Target file
            relationship: Type (IMPORTS, CALLS, DEPENDS_ON)
        """
        query = f"""
        MATCH (f1:File {{path: $from_file}})
        MATCH (f2:File {{path: $to_file}})
        MERGE (f1)-[r:{relationship}]->(f2)
        SET r.created = $created
        """

        self.db.execute(
            query,
            {
                "from_file": from_file,
                "to_file": to_file,
                "created": datetime.now().isoformat()
            }
        )

    def add_function_call(
        self,
        caller: str,
        callee: str,
        caller_file: str,
        callee_file: str
    ) -> None:
        """
        Add a function call relationship

        WHY: Track function call graphs for complexity analysis

        Args:
            caller: Calling function name
            callee: Called function name
            caller_file: File containing caller
            callee_file: File containing callee
        """
        query = """
        MATCH (fn1:Function {name: $caller, file_path: $caller_file})
        MATCH (fn2:Function {name: $callee, file_path: $callee_file})
        MERGE (fn1)-[r:CALLS]->(fn2)
        SET r.created = $created
        """

        self.db.execute(
            query,
            {
                "caller": caller,
                "callee": callee,
                "caller_file": caller_file,
                "callee_file": callee_file,
                "created": datetime.now().isoformat()
            }
        )

    def link_requirement_to_adr(self, req_id: str, adr_id: str) -> None:
        """
        Link a requirement to an ADR that addresses it

        WHY: Track which decisions implement which requirements

        Args:
            req_id: Requirement ID
            adr_id: ADR ID
        """
        query = """
        MATCH (req:Requirement {req_id: $req_id})
        MATCH (adr:ADR {adr_id: $adr_id})
        MERGE (adr)-[:ADDRESSES]->(req)
        SET adr.last_updated = $updated
        """

        self.db.execute(
            query,
            {
                "req_id": req_id,
                "adr_id": adr_id,
                "updated": datetime.now().isoformat()
            }
        )

    def link_requirement_to_task(self, req_id: str, card_id: str) -> None:
        """
        Link a requirement to a task

        WHY: Track which tasks implement which requirements

        Args:
            req_id: Requirement ID
            card_id: Card ID
        """
        query = """
        MATCH (req:Requirement {req_id: $req_id})
        MATCH (task:Task {card_id: $card_id})
        MERGE (task)-[:IMPLEMENTS]->(req)
        """

        self.db.execute(query, {"req_id": req_id, "card_id": card_id})

    def link_adr_to_file(
        self,
        adr_id: str,
        file_path: str,
        relationship: str = "IMPLEMENTED_BY"
    ) -> None:
        """
        Link an ADR to files that implement it

        WHY: Track where decisions are implemented in code

        Args:
            adr_id: ADR ID
            file_path: File path
            relationship: IMPLEMENTED_BY, IMPACTS, DEPENDS_ON
        """
        query = f"""
        MATCH (adr:ADR {{adr_id: $adr_id}})
        MATCH (f:File {{path: $file_path}})
        MERGE (adr)-[r:{relationship}]->(f)
        SET r.created = $created
        """

        self.db.execute(
            query,
            {
                "adr_id": adr_id,
                "file_path": file_path,
                "created": datetime.now().isoformat()
            }
        )

    def link_task_to_file(self, card_id: str, file_path: str) -> None:
        """
        Link a task to files it modified

        WHY: Track which files were changed for which tasks

        Args:
            card_id: Card ID
            file_path: File path
        """
        query = """
        MATCH (task:Task {card_id: $card_id})
        MATCH (f:File {path: $file_path})
        MERGE (task)-[:MODIFIED]->(f)
        """

        self.db.execute(query, {"card_id": card_id, "file_path": file_path})


__all__ = ["RelationshipOperations"]
