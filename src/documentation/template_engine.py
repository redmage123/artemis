#!/usr/bin/env python3
"""
WHY: Generate ADR content using templates as fallback when AI service unavailable
RESPONSIBILITY: Template-based ADR generation with structured requirements support
PATTERNS: Template Method Pattern, guard clauses, dispatch tables
"""

from datetime import datetime
from typing import Dict, Optional, Any, Callable

from documentation.models import (
    ADRRecord,
    ADRMetadata,
    ADRContext,
    ADRStatus,
    create_adr_metadata
)


class ADRTemplateEngine:
    """
    WHY: Provide template-based ADR generation
    RESPONSIBILITY: Generate ADR content from templates with structured requirements
    PATTERNS: Template Method Pattern for ADR generation
    """

    def __init__(self):
        """Initialize template engine"""
        # Dispatch table for section builders
        self._section_builders: Dict[str, Callable] = {
            "header": self._build_header_section,
            "context": self._build_context_section,
            "decision": self._build_decision_section,
            "consequences": self._build_consequences_section,
            "notes": self._build_notes_section
        }

    def generate_adr_from_template(
        self,
        context: ADRContext,
        metadata: ADRMetadata,
        structured_requirements: Optional[Any] = None
    ) -> str:
        """
        Generate ADR using template method pattern

        Args:
            context: ADR context
            metadata: ADR metadata
            structured_requirements: Structured requirements (optional)

        Returns:
            Generated ADR content as markdown string
        """
        # Guard clause: Validate inputs
        if not context or not metadata:
            raise ValueError("Context and metadata are required")

        # Build ADR record using template sections
        record = ADRRecord(
            metadata=metadata,
            context=context,
            decision=self._build_decision_content(context, structured_requirements),
            consequences=self._build_consequences_content(context, structured_requirements),
            structured_requirements=structured_requirements
        )

        # Generate markdown
        return self._generate_complete_adr(record, structured_requirements)

    def _generate_complete_adr(
        self,
        record: ADRRecord,
        structured_requirements: Optional[Any]
    ) -> str:
        """
        Generate complete ADR markdown using sections

        Args:
            record: ADR record
            structured_requirements: Structured requirements (optional)

        Returns:
            Complete ADR markdown
        """
        sections = []

        # Header section
        sections.append(self._section_builders["header"](record))

        # Context section
        sections.append(self._section_builders["context"](record, structured_requirements))

        # Decision section
        sections.append(self._section_builders["decision"](record))

        # Consequences section
        sections.append(self._section_builders["consequences"](record, structured_requirements))

        # Notes section
        sections.append(self._section_builders["notes"](record, structured_requirements))

        return "\n".join(sections)

    def _build_header_section(self, record: ADRRecord, *args) -> str:
        """Build ADR header section"""
        header = f"# ADR-{record.metadata.adr_number}: {record.context.title}\n\n"
        header += f"**Status**: {record.metadata.status.value.title()}\n"
        header += f"**Date**: {record.metadata.date}\n"
        header += f"**Deciders**: {record.metadata.deciders}\n"
        header += f"**Task**: {record.context.card_id} - {record.context.title}\n\n"
        header += "---\n"
        return header

    def _build_context_section(
        self,
        record: ADRRecord,
        structured_requirements: Optional[Any]
    ) -> str:
        """Build ADR context section"""
        section = "\n## Context\n\n"
        section += f"**Task Description**:\n{record.context.description}\n\n"
        section += f"**Priority**: {record.context.priority.value}\n"
        section += f"**Complexity**: {record.context.complexity.value}\n"

        # Guard clause: Add structured requirements if available
        if not structured_requirements:
            return section + "\n---\n"

        section += self._build_structured_requirements_subsection(structured_requirements)
        section += "\n---\n"
        return section

    def _build_structured_requirements_subsection(self, structured_requirements: Any) -> str:
        """
        Build structured requirements subsection

        Args:
            structured_requirements: Structured requirements object

        Returns:
            Formatted subsection markdown
        """
        subsection = f"\n**Structured Requirements Available**: ✅\n"
        subsection += f"**Project**: {structured_requirements.project_name}\n"
        subsection += f"**Requirements Version**: {structured_requirements.version}\n"

        # Add business context
        subsection += self._build_business_context(structured_requirements)

        # Add requirements summary
        subsection += self._build_requirements_summary(structured_requirements)

        # Add key functional requirements
        subsection += self._build_key_functional_requirements(structured_requirements)

        # Add key non-functional requirements
        subsection += self._build_key_nfr_section(structured_requirements)

        return subsection

    def _build_business_context(self, structured_requirements: Any) -> str:
        """Build business context subsection"""
        context = "\n### Business Context\n"

        # Guard clause: Add executive summary if available
        if structured_requirements.executive_summary:
            context += f"\n**Executive Summary**:\n{structured_requirements.executive_summary}\n"

        # Guard clause: Add business goals if available
        if not structured_requirements.business_goals:
            return context

        context += "\n**Business Goals**:\n"
        for goal in structured_requirements.business_goals[:5]:
            context += f"- {goal}\n"

        return context

    def _build_requirements_summary(self, structured_requirements: Any) -> str:
        """Build requirements summary subsection"""
        summary = "\n### Requirements Summary\n"
        summary += f"- **Functional Requirements**: {len(structured_requirements.functional_requirements)}\n"
        summary += f"- **Non-Functional Requirements**: {len(structured_requirements.non_functional_requirements)}\n"
        summary += f"- **Use Cases**: {len(structured_requirements.use_cases)}\n"
        summary += f"- **Data Requirements**: {len(structured_requirements.data_requirements)}\n"
        summary += f"- **Integration Requirements**: {len(structured_requirements.integration_requirements)}\n"
        summary += f"- **Stakeholders**: {len(structured_requirements.stakeholders)}\n"
        return summary

    def _build_key_functional_requirements(self, structured_requirements: Any) -> str:
        """Build key functional requirements subsection"""
        section = "\n### Key Functional Requirements\n"

        # Guard clause: Check if functional requirements exist
        if not structured_requirements.functional_requirements:
            return section + "- No functional requirements specified\n"

        high_priority_reqs = [
            req for req in structured_requirements.functional_requirements
            if req.priority.value in ['critical', 'high']
        ][:5]

        # Guard clause: Check if high priority requirements exist
        if not high_priority_reqs:
            return section + "- No high priority requirements identified\n"

        for req in high_priority_reqs:
            section += f"- **{req.id}**: {req.title} [{req.priority.value}]\n"

        return section

    def _build_key_nfr_section(self, structured_requirements: Any) -> str:
        """Build key non-functional requirements subsection"""
        # Guard clause: Check if NFRs exist
        if not structured_requirements.non_functional_requirements:
            return ""

        section = "\n### Key Non-Functional Requirements\n"
        nfr_high_priority = [
            req for req in structured_requirements.non_functional_requirements
            if req.priority.value in ['critical', 'high']
        ][:5]

        # Guard clause: Check if high priority NFRs exist
        if not nfr_high_priority:
            return ""

        for req in nfr_high_priority:
            section += f"- **{req.id}**: {req.title} [{req.type.value}, {req.priority.value}]\n"
            # Guard clause: Add target if available
            if req.target:
                section += f"  Target: {req.target}\n"

        return section

    def _build_decision_section(self, record: ADRRecord, *args) -> str:
        """Build ADR decision section"""
        return f"\n## Decision\n\n{record.decision}\n\n---\n"

    def _build_consequences_section(
        self,
        record: ADRRecord,
        structured_requirements: Optional[Any]
    ) -> str:
        """Build ADR consequences section"""
        section = f"\n## Consequences\n\n{record.consequences}"

        # Guard clause: Add constraints if available
        if not structured_requirements or not structured_requirements.constraints:
            return section + "\n\n---\n"

        section += "\n\n### Constraints\n"
        for constraint in structured_requirements.constraints[:5]:
            section += f"- **{constraint.type.upper()}**: {constraint.description} (Impact: {constraint.impact})\n"

        section += "\n---\n"
        return section

    def _build_notes_section(
        self,
        record: ADRRecord,
        structured_requirements: Optional[Any]
    ) -> str:
        """Build ADR notes section"""
        notes = "\n**Note**: This is an automatically generated ADR. "
        notes += "For complex tasks, manual architectural review is recommended.\n"

        # Guard clause: Add requirements source if available
        if not structured_requirements:
            return notes

        notes += f"\n**Requirements Source**: Parsed from {structured_requirements.project_name} "
        notes += f"requirements document (version {structured_requirements.version})\n"

        return notes

    def _build_decision_content(
        self,
        context: ADRContext,
        structured_requirements: Optional[Any]
    ) -> str:
        """
        Build decision content based on context

        Args:
            context: ADR context
            structured_requirements: Structured requirements (optional)

        Returns:
            Decision content markdown
        """
        title_lower = context.title.lower()

        # Guard clause: Use structured requirements approach if available
        if structured_requirements:
            return self._build_structured_decision(title_lower, structured_requirements)

        # Default approach
        return self._build_default_decision(title_lower)

    def _build_structured_decision(self, title_lower: str, structured_requirements: Any) -> str:
        """Build decision content with structured requirements"""
        decision = f"**Approach**: Implement {title_lower} following the structured requirements "
        decision += f"from {structured_requirements.project_name}.\n\n"
        decision += "**Implementation Strategy**:\n"
        decision += "- Use structured requirements as architectural blueprint\n"
        decision += "- Functional requirements → Feature implementations\n"
        decision += "- Non-functional requirements → Technical decisions (performance, security, scalability)\n"
        decision += "- Data requirements → Data model and database design\n"
        decision += "- Integration requirements → API and service integration design\n"
        decision += "- Developer A: Conservative, minimal-risk implementation focusing on critical requirements\n"
        decision += "- Developer B: Comprehensive implementation with enhanced features\n"
        return decision

    def _build_default_decision(self, title_lower: str) -> str:
        """Build default decision content"""
        decision = f"**Approach**: Implement {title_lower} using test-driven development "
        decision += "with parallel developer approaches.\n\n"
        decision += "**Implementation Strategy**:\n"
        decision += "- Developer A: Conservative, minimal-risk implementation\n"
        decision += "- Developer B: Comprehensive implementation with enhanced features\n"
        return decision

    def _build_consequences_content(
        self,
        context: ADRContext,
        structured_requirements: Optional[Any]
    ) -> str:
        """
        Build consequences content

        Args:
            context: ADR context
            structured_requirements: Structured requirements (optional)

        Returns:
            Consequences content markdown
        """
        consequences = "### Positive\n"
        consequences += "- ✅ Clear architectural direction for developers\n"

        # Guard clause: Add structured requirements benefits if available
        if structured_requirements:
            consequences += "- ✅ Structured requirements provide comprehensive implementation guidance\n"
            consequences += "- ✅ Non-functional requirements ensure quality attributes are met\n"
            consequences += f"- ✅ {len(structured_requirements.use_cases)} use cases validate implementation completeness\n"

        consequences += "- ✅ Parallel development allows comparison of approaches\n"
        consequences += "- ✅ TDD ensures quality and testability\n"

        return consequences
