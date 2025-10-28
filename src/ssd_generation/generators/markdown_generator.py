#!/usr/bin/env python3
"""
Markdown Generator

WHY: Generates Markdown representation of SSD documents.
RESPONSIBILITY: Convert SSDDocument to Markdown format.
PATTERNS:
- Generator pattern (Pattern #11) for large content processing
- Single Responsibility
"""

from typing import Generator

from ssd_generation.models.ssd_document import SSDDocument


class MarkdownGenerator:
    """
    Generates Markdown representation of SSD

    WHY: Produces human-readable Markdown documentation.
    WHEN: Called during output generation to create .md files.
    """

    @staticmethod
    def generate_markdown(ssd_document: SSDDocument) -> str:
        """Generate Markdown representation of SSD"""
        md_lines = [
            f"# Software Specification Document: {ssd_document.project_name}",
            "",
            f"**Generated**: {ssd_document.generated_at}",
            f"**Card ID**: {ssd_document.card_id}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            ssd_document.executive_summary,
            "",
            "## Business Case",
            "",
            ssd_document.business_case,
            "",
            "---",
            "",
            "## Functional Requirements",
            ""
        ]

        # Pattern #11: Use generator to build functional requirements markdown
        def _format_functional_requirements() -> Generator[str, None, None]:
            """Generator yielding markdown lines for functional requirements"""
            for req in ssd_document.functional_requirements:
                yield from [
                    f"### {req.id}: {req.description}",
                    "",
                    f"**Priority**: {req.priority}",
                    "",
                    "**Acceptance Criteria**:",
                    *[f"- {criterion}" for criterion in req.acceptance_criteria],
                    "",
                    f"**Dependencies**: {', '.join(req.dependencies) if req.dependencies else 'None'}",
                    ""
                ]

        md_lines.extend(_format_functional_requirements())

        md_lines.extend([
            "---",
            "",
            "## Non-Functional Requirements",
            ""
        ])

        # Pattern #11: Generator for non-functional requirements
        def _format_non_functional_requirements() -> Generator[str, None, None]:
            """Generator yielding markdown lines for non-functional requirements"""
            for req in ssd_document.non_functional_requirements:
                yield from [
                    f"### {req.id}: {req.description}",
                    "",
                    f"**Priority**: {req.priority}",
                    "",
                    "**Acceptance Criteria**:",
                    *[f"- {criterion}" for criterion in req.acceptance_criteria],
                    ""
                ]

        md_lines.extend(_format_non_functional_requirements())

        md_lines.extend([
            "---",
            "",
            "## Business Requirements",
            ""
        ])

        # Pattern #11: Generator for business requirements
        def _format_business_requirements() -> Generator[str, None, None]:
            """Generator yielding markdown lines for business requirements"""
            for req in ssd_document.business_requirements:
                yield from [
                    f"### {req.id}: {req.description}",
                    "",
                    f"**Priority**: {req.priority}",
                    ""
                ]

        md_lines.extend(_format_business_requirements())

        md_lines.extend([
            "---",
            "",
            "## Diagrams",
            ""
        ])

        # Pattern #11: Generator for diagrams
        def _format_diagrams() -> Generator[str, None, None]:
            """Generator yielding markdown lines for diagrams"""
            for diagram in ssd_document.diagrams:
                yield f"### {diagram.title}"
                yield ""
                yield diagram.description
                yield ""
                yield f"**Type**: {diagram.diagram_type}"
                yield ""

                if diagram.mermaid_syntax:
                    yield "```mermaid"
                    yield diagram.mermaid_syntax
                    yield "```"
                    yield ""

        md_lines.extend(_format_diagrams())

        md_lines.extend([
            "---",
            "",
            "## Constraints",
            "",
            *[f"- {constraint}" for constraint in ssd_document.constraints],
            "",
            "## Assumptions",
            "",
            *[f"- {assumption}" for assumption in ssd_document.assumptions],
            "",
            "## Risks",
            "",
            *[f"- {risk}" for risk in ssd_document.risks],
            "",
            "## Success Criteria",
            "",
            *[f"- {criterion}" for criterion in ssd_document.success_criteria],
            ""
        ])

        return "\n".join(md_lines)
