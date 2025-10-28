#!/usr/bin/env python3
"""
SSDDocument Data Model

WHY: Represents the complete Software Specification Document structure.
RESPONSIBILITY: Aggregate all SSD components into a single document model.
PATTERNS:
- Dataclass pattern for structured data
- to_dict() method for JSON serialization
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

from ssd_generation.models.requirement_item import RequirementItem
from ssd_generation.models.diagram_spec import DiagramSpec


@dataclass
class SSDDocument:
    """
    Complete Software Specification Document

    WHY: Central data structure containing all SSD sections.
    Used for output generation (JSON, Markdown, HTML, PDF).
    """
    project_name: str
    card_id: str
    generated_at: str

    # Executive Summary
    executive_summary: str
    business_case: str

    # Requirements
    functional_requirements: List[RequirementItem]
    non_functional_requirements: List[RequirementItem]
    business_requirements: List[RequirementItem]

    # Diagrams
    diagrams: List[DiagramSpec]

    # Additional sections
    constraints: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization

        WHY: Enables easy serialization to JSON format.
        """
        return asdict(self)
