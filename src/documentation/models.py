#!/usr/bin/env python3
"""
WHY: Define core data models for Architecture Decision Records (ADR) generation
RESPONSIBILITY: Provide structured data types for ADR status, records, and context
PATTERNS: Enums for type safety, dataclasses for immutable records, guard clauses
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class ADRStatus(Enum):
    """ADR lifecycle status enumeration"""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


class ADRPriority(Enum):
    """ADR priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ADRComplexity(Enum):
    """ADR complexity levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


@dataclass(frozen=True)
class ADRMetadata:
    """
    WHY: Encapsulate ADR metadata for tracking and auditing
    RESPONSIBILITY: Store immutable metadata about an ADR
    """
    adr_number: str
    status: ADRStatus
    date: str
    deciders: str = "Architecture Agent (Automated)"

    def to_dict(self) -> Dict[str, str]:
        """Convert metadata to dictionary"""
        return {
            "adr_number": self.adr_number,
            "status": self.status.value,
            "date": self.date,
            "deciders": self.deciders
        }


@dataclass(frozen=True)
class ADRContext:
    """
    WHY: Encapsulate context information for ADR generation
    RESPONSIBILITY: Store immutable context about task/card requiring ADR
    """
    card_id: str
    title: str
    description: str
    priority: ADRPriority
    complexity: ADRComplexity

    def to_dict(self) -> Dict[str, str]:
        """Convert context to dictionary"""
        return {
            "card_id": self.card_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "complexity": self.complexity.value
        }


@dataclass(frozen=True)
class SSDContext:
    """
    WHY: Encapsulate Software Specification Document context
    RESPONSIBILITY: Store immutable SSD-derived context for ADR enrichment
    """
    executive_summary: str
    business_case: str
    functional_count: int
    non_functional_count: int
    key_requirements: str
    diagram_descriptions: str
    constraints: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert SSD context to dictionary"""
        return {
            "executive_summary": self.executive_summary,
            "business_case": self.business_case,
            "functional_count": self.functional_count,
            "non_functional_count": self.non_functional_count,
            "key_requirements": self.key_requirements,
            "diagram_descriptions": self.diagram_descriptions,
            "constraints": list(self.constraints),
            "success_criteria": list(self.success_criteria)
        }


@dataclass
class ADRRecord:
    """
    WHY: Represent complete ADR record with all sections
    RESPONSIBILITY: Store mutable ADR content and structure
    """
    metadata: ADRMetadata
    context: ADRContext
    decision: str
    consequences: str
    ssd_context: Optional[SSDContext] = None
    structured_requirements: Optional[Any] = None
    notes: List[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        """
        Convert ADR record to markdown format

        Returns:
            Formatted markdown string
        """
        # Guard clause: Validate required fields
        if not self.metadata or not self.context:
            raise ValueError("ADR record missing required metadata or context")

        md = f"# ADR-{self.metadata.adr_number}: {self.context.title}\n\n"
        md += f"**Status**: {self.metadata.status.value.title()}\n"
        md += f"**Date**: {self.metadata.date}\n"
        md += f"**Deciders**: {self.metadata.deciders}\n"
        md += f"**Task**: {self.context.card_id} - {self.context.title}\n\n"
        md += "---\n\n"
        md += "## Context\n\n"
        md += self._format_context_section()
        md += "\n---\n\n"
        md += "## Decision\n\n"
        md += self.decision
        md += "\n\n---\n\n"
        md += "## Consequences\n\n"
        md += self.consequences

        # Guard clause: Add notes if available
        if not self.notes:
            return md

        md += "\n\n---\n\n"
        md += "## Notes\n\n"
        md += "\n".join(f"- {note}" for note in self.notes)

        return md

    def _format_context_section(self) -> str:
        """Format context section with task details"""
        section = f"**Task Description**:\n{self.context.description}\n\n"
        section += f"**Priority**: {self.context.priority.value}\n"
        section += f"**Complexity**: {self.context.complexity.value}\n"

        # Guard clause: Add SSD context if available
        if not self.ssd_context:
            return section

        section += "\n**Software Specification Document Available**: ✅\n\n"
        section += f"**Executive Summary**:\n{self.ssd_context.executive_summary}\n\n"
        section += f"**Business Case**:\n{self.ssd_context.business_case}\n\n"

        return section

    def to_dict(self) -> Dict[str, Any]:
        """Convert ADR record to dictionary"""
        return {
            "metadata": self.metadata.to_dict(),
            "context": self.context.to_dict(),
            "decision": self.decision,
            "consequences": self.consequences,
            "ssd_context": self.ssd_context.to_dict() if self.ssd_context else None,
            "notes": list(self.notes)
        }


def create_adr_context_from_card(card: Dict[str, Any]) -> ADRContext:
    """
    WHY: Factory function to create ADRContext from Kanban card
    RESPONSIBILITY: Convert card dict to strongly-typed ADRContext
    PATTERNS: Guard clauses for validation

    Args:
        card: Kanban card dictionary

    Returns:
        ADRContext instance

    Raises:
        ValueError: If card missing required fields
    """
    # Guard clause: Validate card has required fields
    if not card:
        raise ValueError("Card cannot be None or empty")

    if "card_id" not in card:
        raise ValueError("Card missing required field: card_id")

    # Extract with defaults
    card_id = card["card_id"]
    title = card.get("title", "Untitled Task")
    description = card.get("description", "No description provided")

    # Parse priority enum
    priority_str = card.get("priority", "medium").lower()
    try:
        priority = ADRPriority(priority_str)
    except ValueError:
        priority = ADRPriority.MEDIUM

    # Parse complexity enum
    complexity_str = card.get("size", "medium").lower()
    try:
        complexity = ADRComplexity(complexity_str)
    except ValueError:
        complexity = ADRComplexity.MEDIUM

    return ADRContext(
        card_id=card_id,
        title=title,
        description=description,
        priority=priority,
        complexity=complexity
    )


def create_adr_metadata(adr_number: str, status: ADRStatus = ADRStatus.ACCEPTED) -> ADRMetadata:
    """
    WHY: Factory function to create ADRMetadata with defaults
    RESPONSIBILITY: Generate metadata with current timestamp

    Args:
        adr_number: ADR number string
        status: ADR status (default: ACCEPTED)

    Returns:
        ADRMetadata instance
    """
    return ADRMetadata(
        adr_number=adr_number,
        status=status,
        date=datetime.utcnow().strftime('%Y-%m-%d')
    )
