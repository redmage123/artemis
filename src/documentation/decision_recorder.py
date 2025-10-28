#!/usr/bin/env python3
"""
WHY: Build ADR generation prompts with comprehensive context
RESPONSIBILITY: Construct prompts for LLM ADR generation with SSD and environment context
PATTERNS: Guard clauses, template method, single responsibility
"""

from datetime import datetime
from typing import Dict, Optional, Any

from documentation.models import ADRContext, SSDContext
from environment_context import get_environment_context


class DecisionRecorder:
    """
    WHY: Build comprehensive prompts for ADR generation
    RESPONSIBILITY: Construct prompts with task, SSD, and environment context
    PATTERNS: Template Method Pattern for prompt building, guard clauses
    """

    def __init__(self):
        """Initialize decision recorder"""
        self._prompt_template = self._initialize_prompt_template()

    def _initialize_prompt_template(self) -> str:
        """
        Initialize base prompt template

        Returns:
            Base prompt template string
        """
        return """Generate an Architecture Decision Record (ADR) for the following task:

**Title**: {title}
**Description**: {description}
**Priority**: {priority}
**Complexity**: {complexity}
"""

    def build_adr_prompt(
        self,
        context: ADRContext,
        adr_number: str,
        ssd_context: Optional[SSDContext] = None,
        structured_requirements: Optional[Any] = None
    ) -> str:
        """
        Build prompt for LLM ADR generation

        Args:
            context: ADR context
            adr_number: ADR number
            ssd_context: SSD context (optional)
            structured_requirements: Structured requirements (optional)

        Returns:
            Prompt string for LLM
        """
        # Guard clause: Validate context
        if not context:
            raise ValueError("ADR context is required")

        # Build base prompt
        prompt = self._build_base_prompt(context)

        # Add SSD context if available
        prompt += self._add_ssd_context_section(ssd_context)

        # Add structured requirements as fallback
        if not ssd_context and structured_requirements:
            prompt += self._add_structured_requirements_section(structured_requirements)

        # Add environment context
        prompt += get_environment_context()

        # Add ADR format template
        prompt += self._build_adr_format_section(context.title, adr_number)

        return prompt

    def _build_base_prompt(self, context: ADRContext) -> str:
        """
        Build base prompt with task context

        Args:
            context: ADR context

        Returns:
            Base prompt string
        """
        return self._prompt_template.format(
            title=context.title,
            description=context.description,
            priority=context.priority.value,
            complexity=context.complexity.value
        )

    def _add_ssd_context_section(self, ssd_context: Optional[SSDContext]) -> str:
        """
        Add SSD context section to prompt

        Args:
            ssd_context: SSD context (optional)

        Returns:
            SSD context section or empty string
        """
        # Guard clause: Check if SSD context available
        if not ssd_context:
            return ""

        section = "\n**Software Specification Document Available**: ✅\n\n"
        section += f"**Executive Summary**:\n{ssd_context.executive_summary}\n\n"
        section += f"**Business Case**:\n{ssd_context.business_case}\n\n"
        section += "**Requirements Summary**:\n"
        section += f"- Functional Requirements: {ssd_context.functional_count}\n"
        section += f"- Non-Functional Requirements: {ssd_context.non_functional_count}\n\n"
        section += f"**Key Requirements**:\n{ssd_context.key_requirements}\n\n"
        section += f"**Architectural Diagrams**:\n{ssd_context.diagram_descriptions}\n\n"

        # Add constraints if available
        section += self._format_list_section("Constraints", ssd_context.constraints)

        # Add success criteria if available
        section += self._format_list_section("Success Criteria", ssd_context.success_criteria)

        return section

    def _add_structured_requirements_section(self, structured_requirements: Any) -> str:
        """
        Add structured requirements section to prompt

        Args:
            structured_requirements: Structured requirements object

        Returns:
            Structured requirements section
        """
        section = "\n**Structured Requirements Available**:\n"
        section += f"- Project: {structured_requirements.project_name}\n"
        section += f"- Functional Requirements: {len(structured_requirements.functional_requirements)}\n"
        section += f"- Non-Functional Requirements: {len(structured_requirements.non_functional_requirements)}\n"
        section += f"- Use Cases: {len(structured_requirements.use_cases)}\n\n"
        section += "**Top Requirements**:\n"

        # Add top 3 functional requirements
        for req in structured_requirements.functional_requirements[:3]:
            section += f"- {req.id}: {req.title} [{req.priority.value}]\n"

        return section

    def _format_list_section(self, title: str, items: list) -> str:
        """
        Format list section with title

        Args:
            title: Section title
            items: List of items

        Returns:
            Formatted section or empty string
        """
        # Guard clause: Check if items exist
        if not items:
            return ""

        section = f"**{title}**:\n"
        section += '\n'.join(f'- {item}' for item in items)
        section += "\n\n"
        return section

    def _build_adr_format_section(self, title: str, adr_number: str) -> str:
        """
        Build ADR format template section

        Args:
            title: Task title
            adr_number: ADR number

        Returns:
            ADR format section
        """
        return f"""
Generate ADR-{adr_number} in this format:

# ADR-{adr_number}: {title}

**Status**: Accepted
**Date**: {datetime.utcnow().strftime('%Y-%m-%d')}
**Deciders**: Architecture Agent (Automated)

## Context
[Explain the technical context and problem being solved in a development/test environment]

## Decision
[Document the architectural decision using ONLY available standard libraries and tools]
[If requirements mention external infrastructure (Kafka/Spark/databases/message queues), provide concrete
 alternatives: mock interfaces + file storage, in-memory simulations, embedded databases (SQLite/H2), etc.]
[Specify exact libraries/frameworks to use (e.g., "use pandas for data analysis, not Spark")]

## Consequences
[List positive and negative consequences]

Focus on pragmatic, executable implementation that can run in a basic development environment
without requiring external infrastructure installation."""


class PromptBuilder:
    """
    WHY: Convenience wrapper for building ADR prompts
    RESPONSIBILITY: Simplify prompt building interface
    """

    def __init__(self):
        """Initialize prompt builder"""
        self.recorder = DecisionRecorder()

    def build(
        self,
        card: Dict[str, Any],
        adr_number: str,
        ssd_context: Optional[SSDContext] = None,
        structured_requirements: Optional[Any] = None
    ) -> str:
        """
        Build ADR prompt from card and contexts

        Args:
            card: Kanban card dictionary
            adr_number: ADR number
            ssd_context: SSD context (optional)
            structured_requirements: Structured requirements (optional)

        Returns:
            Prompt string for LLM
        """
        # Import here to avoid circular import
        from documentation.models import create_adr_context_from_card

        # Create ADR context from card
        context = create_adr_context_from_card(card)

        # Build prompt using recorder
        return self.recorder.build_adr_prompt(
            context,
            adr_number,
            ssd_context,
            structured_requirements
        )


def create_decision_recorder() -> DecisionRecorder:
    """
    Factory function to create DecisionRecorder instance

    Returns:
        DecisionRecorder instance
    """
    return DecisionRecorder()


def create_prompt_builder() -> PromptBuilder:
    """
    Factory function to create PromptBuilder instance

    Returns:
        PromptBuilder instance
    """
    return PromptBuilder()
