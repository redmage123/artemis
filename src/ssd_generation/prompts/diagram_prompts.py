#!/usr/bin/env python3
"""
Diagram Prompts

WHY: Centralized prompt templates for diagram generation.
RESPONSIBILITY: Build LLM prompts for diagram specifications.
PATTERNS:
- Template Method pattern
- Single Responsibility
"""

import json
from typing import Dict, List, Any

from ssd_generation.models.requirement_item import RequirementItem


class DiagramPrompts:
    """
    Prompt builders for diagram generation

    WHY: Separation of concerns - diagram prompts isolated from logic.
    WHEN: Used by DiagramGenerator to generate diagram specifications.
    """

    @staticmethod
    def build_diagram_generation_prompt(
        card: Dict[str, Any],
        requirements: Dict[str, List[RequirementItem]],
        context: Dict[str, Any]
    ) -> str:
        """Build prompt for diagram specifications"""
        # Summarize requirements for prompt
        req_summary = {
            "functional_count": len(requirements.get('functional', [])),
            "non_functional_count": len(requirements.get('non_functional', [])),
            "sample_requirements": [
                req.description for req in requirements.get('functional', [])[:3]
            ]
        }

        return f"""You are a Solutions Architect creating technical diagrams for a Software Specification Document.

**Project**: {card.get('title', 'Untitled Project')}

**Requirements Summary**:
{json.dumps(req_summary, indent=2)}

**Workflow Complexity**: {context.get('workflow_plan', {}).get('complexity', 'medium')}

Create diagram specifications for:

1. **System Architecture Diagram**:
   - High-level system components
   - Data flow between components
   - External integrations
   - Use Mermaid flowchart syntax

2. **Entity Relationship Diagram (ERD)**:
   - Database entities/tables
   - Relationships using Crow's foot notation
   - Key attributes
   - Use Mermaid ER diagram syntax

3. **Component Diagram** (if complex):
   - Major software components
   - Dependencies between components
   - Use Mermaid component diagram

For each diagram provide:
- **type**: architecture | erd | object_relational | component | sequence
- **title**: Diagram title
- **description**: What this diagram shows
- **mermaid_syntax**: Mermaid diagram code
- **chart_js_config**: {{}} (optional Chart.js configuration for visual rendering)

**Mermaid ER Diagram Crow's Foot Notation**:
```
erDiagram
    CUSTOMER ||--o{{{{ ORDER : places
    ORDER ||--||{{{{ LINE-ITEM : contains
    CUSTOMER }}|..||{{{{ DELIVERY-ADDRESS : uses
```

Notation:
- ||--o{{{{ : One-to-many
- ||--|| : One-to-one
- }}o--o{{{{ : Many-to-many
- }}|..||{{{{ : Zero or more

Provide response in JSON format:
```json
{{
  "diagrams": [
    {{
      "type": "architecture",
      "title": "System Architecture",
      "description": "High-level architecture showing...",
      "mermaid_syntax": "flowchart TD\\n    A[Client] --> B[API Gateway]\\n    B --> C[Backend Services]",
      "chart_js_config": {{}}
    }},
    {{
      "type": "erd",
      "title": "Entity Relationship Diagram",
      "description": "Database schema showing...",
      "mermaid_syntax": "erDiagram\\n    USER ||--o{{ ORDER : places\\n    ORDER ||--|{{ ITEM : contains",
      "chart_js_config": {{}}
    }}
  ]
}}
```"""
