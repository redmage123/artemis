#!/usr/bin/env python3
"""
RequirementItem Data Model

WHY: Represents a single requirement item with all necessary attributes.
RESPONSIBILITY: Store requirement data (functional, non-functional, or business).
PATTERNS:
- Dataclass pattern for immutable data structure
- Type hints for clarity and validation
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class RequirementItem:
    """
    Single requirement item

    WHY: Encapsulates all requirement metadata in a single structure.
    Used across functional, non-functional, and business requirements.
    """
    id: str
    category: str  # functional, non_functional, business
    priority: str  # must_have, should_have, nice_to_have
    description: str
    acceptance_criteria: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
