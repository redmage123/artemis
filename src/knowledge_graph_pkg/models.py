#!/usr/bin/env python3
"""
WHY: Define data models for knowledge graph entities
RESPONSIBILITY: Data classes representing graph nodes (files, classes, functions, ADRs, etc.)
PATTERNS: Dataclass pattern for immutable data transfer objects

This module contains no business logic - only data structures.
"""

from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class CodeFile:
    """Represents a code file in the graph"""
    path: str
    language: str
    lines: int = 0
    last_modified: Optional[str] = None
    module: Optional[str] = None


@dataclass
class CodeClass:
    """Represents a class in the graph"""
    name: str
    file_path: str
    public: bool = True
    abstract: bool = False
    lines: int = 0


@dataclass
class CodeFunction:
    """Represents a function in the graph"""
    name: str
    file_path: str
    class_name: Optional[str] = None
    params: Optional[List[str]] = None
    returns: Optional[str] = None
    public: bool = True
    complexity: int = 1

    def __post_init__(self):
        if self.params is None:
            self.params = []


@dataclass
class ADR:
    """Architecture Decision Record"""
    adr_id: str
    title: str
    date: str
    status: str  # proposed, accepted, rejected, deprecated, superseded
    rationale: Optional[str] = None


@dataclass
class Requirement:
    """Requirement node in knowledge graph"""
    req_id: str
    title: str
    type: str  # functional, non_functional, use_case, data, integration
    priority: str  # critical, high, medium, low
    status: str = "active"  # active, implemented, deprecated


@dataclass
class Task:
    """Task/Card node in knowledge graph"""
    card_id: str
    title: str
    priority: str
    status: str  # backlog, in_progress, review, done
    assigned_agents: Optional[List[str]] = None

    def __post_init__(self):
        if self.assigned_agents is None:
            self.assigned_agents = []


@dataclass
class CodeReview:
    """Code review result node"""
    review_id: str
    card_id: str
    status: str  # PASS, FAIL
    score: int
    critical_issues: int = 0
    high_issues: int = 0


# Export all models
__all__ = [
    "CodeFile",
    "CodeClass",
    "CodeFunction",
    "ADR",
    "Requirement",
    "Task",
    "CodeReview",
]
