#!/usr/bin/env python3
"""
Code Generation KG Query Strategy

WHY: Implements KG queries for code generation based on similar implementations.

RESPONSIBILITY:
- Query KG for similar implementations using keywords
- Extract file patterns (file_path, file_type, task_title)
- Estimate token savings (~3000 tokens with patterns)

PATTERNS:
- Strategy Pattern implementation
- Guard clauses for early returns
- Conditional savings estimation
"""

from typing import Dict, List, Any
import time

from artemis_exceptions import KnowledgeGraphError, wrap_exception
from ai_query.kg_query_strategy import KGQueryStrategy
from ai_query.kg_context import KGContext
from ai_query.query_type import QueryType


class CodeGenerationKGStrategy(KGQueryStrategy):
    """KG query strategy for code generation"""

    def query_kg(self, kg: Any, query_params: Dict[str, Any]) -> KGContext:
        """Query for similar implementations"""
        try:
            start = time.time()

            keywords = query_params.get('keywords', [])

            similar_files = []
            for keyword in keywords[:3]:
                files = kg.query("""
                    MATCH (task:Task)-[:MODIFIED]->(file:File)
                    WHERE toLower(task.title) CONTAINS $keyword
                    AND file.file_type = 'python'
                    RETURN DISTINCT file.path, file.file_type, task.title
                    LIMIT 3
                """, {"keyword": keyword})
                if files:
                    similar_files.extend(files)

            elapsed_ms = (time.time() - start) * 1000

            patterns = [
                {
                    'file_path': f.get('file.path'),
                    'file_type': f.get('file.file_type'),
                    'task_title': f.get('task.title')
                }
                for f in similar_files
            ]

            return KGContext(
                query_type=QueryType.CODE_GENERATION,
                patterns_found=patterns,
                pattern_count=len(patterns),
                estimated_token_savings=self.estimate_token_savings(patterns),
                kg_query_time_ms=elapsed_ms,
                kg_available=True
            )
        except Exception as e:
            raise wrap_exception(e, KnowledgeGraphError,
                               f"Failed to query KG for implementations: {str(e)}")

    def estimate_token_savings(self, patterns: List[Dict]) -> int:
        """Code generation can save ~3000 tokens with patterns"""
        return 3000 if patterns else 0
