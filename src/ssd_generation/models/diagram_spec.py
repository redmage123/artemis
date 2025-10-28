#!/usr/bin/env python3
"""
DiagramSpec Data Model

WHY: Represents diagram specifications for Chart.js and Mermaid rendering.
RESPONSIBILITY: Store diagram metadata and configuration.
PATTERNS:
- Dataclass pattern for structured data
- Optional fields with defaults
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class DiagramSpec:
    """
    Specification for a diagram to be generated

    WHY: Supports multiple diagram types (architecture, ERD, etc.)
    with flexible rendering options (Chart.js or Mermaid).
    """
    diagram_type: str  # architecture, erd, object_relational, sequence, component
    title: str
    description: str
    chart_js_config: Dict[str, Any]  # Chart.js configuration
    mermaid_syntax: Optional[str] = None  # Alternative: Mermaid diagram syntax
