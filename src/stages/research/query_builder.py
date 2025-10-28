#!/usr/bin/env python3
"""
WHY: Build research queries from task information
RESPONSIBILITY: Format search queries for code example research
PATTERNS: Pure function (stateless query formatting), Guard Clauses

Query builder converts task metadata into optimized search queries for
different research sources (GitHub, HuggingFace, local).
"""

from typing import List


def format_research_query(
    task_title: str,
    task_description: str,
    technologies: List[str]
) -> str:
    """
    Format research query from task information.

    WHY: Search quality depends on well-formatted queries.
         Combine task context with technology to create targeted searches.

    Args:
        task_title: Task title
        task_description: Task description
        technologies: Technologies list

    Returns:
        Formatted search query string

    Example:
        >>> format_research_query(
        ...     "User authentication",
        ...     "Implement JWT-based auth",
        ...     ["python", "flask"]
        ... )
        'python User authentication Implement JWT-based auth'
    """
    # Guard clause - early return for empty input
    if not task_title and not task_description:
        return "code example"

    # Build query parts using list comprehension
    query_parts = [
        part for part in [
            task_title,
            task_description[:100] if task_description else None
        ] if part
    ]

    query = " ".join(query_parts)

    # Add primary technology prefix if available
    return f"{technologies[0]} {query}" if technologies else query


class ResearchQueryBuilder:
    """
    Builder for research queries with advanced features.

    WHY: Enables more complex query construction with filtering and boosting.
    PATTERNS: Builder pattern (fluent interface).
    """

    def __init__(self):
        """Initialize query builder"""
        self.task_title = ""
        self.task_description = ""
        self.technologies = []
        self.project_type = None

    def with_task_title(self, title: str) -> 'ResearchQueryBuilder':
        """Set task title"""
        self.task_title = title
        return self

    def with_task_description(self, description: str) -> 'ResearchQueryBuilder':
        """Set task description"""
        self.task_description = description
        return self

    def with_technologies(self, technologies: List[str]) -> 'ResearchQueryBuilder':
        """Set technologies"""
        self.technologies = technologies
        return self

    def with_project_type(self, project_type: str) -> 'ResearchQueryBuilder':
        """Set project type"""
        self.project_type = project_type
        return self

    def build(self) -> str:
        """
        Build the query string.

        Returns:
            Formatted query string
        """
        # Use the same logic as format_research_query
        query = format_research_query(
            self.task_title,
            self.task_description,
            self.technologies
        )

        # Add project type if available
        if self.project_type:
            query = f"{self.project_type} {query}"

        return query
