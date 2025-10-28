#!/usr/bin/env python3
"""
WHY: Handle persistence and export operations for the knowledge graph
RESPONSIBILITY: Import/export graph data, clear operations, and backup
PATTERNS: Single Responsibility - only deals with storage, not queries or mutations

All functions handle serialization and file I/O.
"""

import json
from typing import Any, Dict
from pathlib import Path


class StorageOperations:
    """
    WHY: Encapsulate all storage and persistence operations
    RESPONSIBILITY: Export, import, and clear graph data
    PATTERNS: Delegation pattern - receives database connection
    """

    def __init__(self, db: Any):
        """
        Initialize with database connection

        Args:
            db: Memgraph database connection
        """
        self.db = db

    def clear_all(self) -> None:
        """
        Clear entire graph

        WHY: Reset graph for testing or fresh start
        WARNING: DANGEROUS - use only for testing

        Returns:
            None
        """
        self.db.execute("MATCH (n) DETACH DELETE n")

    def export_to_json(self, output_path: str) -> None:
        """
        Export graph to JSON

        WHY: Backup graph or share with other tools

        Args:
            output_path: Where to save JSON file

        Returns:
            None
        """
        export_query = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN collect(DISTINCT n) as nodes,
               collect(DISTINCT {type: type(r), from: id(n), to: id(m)}) as edges
        """

        result = list(self.db.execute_and_fetch(export_query))[0]

        # Ensure directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2, default=str)

    def create_indexes(self) -> None:
        """
        Create indexes for faster queries

        WHY: Improve query performance on frequently searched properties

        Returns:
            None
        """
        # Dispatch table for index creation
        index_queries = [
            "CREATE INDEX ON :File(path);",
            "CREATE INDEX ON :Class(name);",
            "CREATE INDEX ON :Function(name);",
            "CREATE INDEX ON :ADR(adr_id);",
            "CREATE INDEX ON :Requirement(req_id);",
            "CREATE INDEX ON :Task(card_id);",
        ]

        for query in index_queries:
            try:
                self.db.execute(query)
            except Exception:
                # Indexes might already exist - silently ignore
                pass


__all__ = ["StorageOperations"]
