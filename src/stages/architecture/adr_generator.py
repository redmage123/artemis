#!/usr/bin/env python3
"""
ADR Content Generator

WHY: Generate Architecture Decision Record content
RESPONSIBILITY: Create ADR content from templates or AI
PATTERNS: Strategy Pattern, Guard Clauses, Dispatch Table
"""

from datetime import datetime
from typing import Dict, Any, Optional, List, Callable

from artemis_exceptions import ADRGenerationError, wrap_exception
from ai_query_service import AIQueryService, QueryType, AIQueryResult


class ADRGenerator:
    """
    Generates ADR content using template or AI service.

    WHY: Separate ADR content generation from file management
    RESPONSIBILITY: Generate ADR markdown content only
    PATTERNS: Strategy Pattern (template vs AI), Guard Clauses
    """

    def __init__(
        self,
        ai_service: Optional[AIQueryService] = None,
        logger: Optional[Any] = None,
        debug_mixin: Optional[Any] = None
    ):
        """
        Initialize ADR generator.

        Args:
            ai_service: AI Query Service for LLM-based generation
            logger: Logger interface
            debug_mixin: Debug mixin for logging
        """
        self.ai_service = ai_service
        self.logger = logger
        self.debug_mixin = debug_mixin

    def generate_adr(
        self,
        card: Dict,
        adr_number: str,
        structured_requirements: Optional[Any] = None
    ) -> str:
        """
        Generate ADR content.

        Args:
            card: Task card with title, description, etc.
            adr_number: ADR number (e.g., "001")
            structured_requirements: Parsed requirements (optional)

        Returns:
            ADR content as markdown string

        Raises:
            ADRGenerationError: If generation fails

        WHY: Main entry point for ADR generation
        PATTERN: Guard clauses for error handling
        """
        try:
            title = card.get('title', 'Untitled Task')

            # Debug logging
            if self.debug_mixin:
                with self.debug_mixin.debug_section("ADR Generation", adr_number=adr_number):
                    return self._generate_with_strategy(card, adr_number, structured_requirements, title)
            else:
                return self._generate_with_strategy(card, adr_number, structured_requirements, title)

        except ADRGenerationError:
            raise
        except Exception as e:
            raise wrap_exception(
                e,
                ADRGenerationError,
                f"Failed to generate ADR: {str(e)}",
                context={"card_id": card.get('card_id'), "adr_number": adr_number}
            )

    def _generate_with_strategy(
        self,
        card: Dict,
        adr_number: str,
        structured_requirements: Optional[Any],
        title: str
    ) -> str:
        """
        Generate ADR using appropriate strategy.

        WHY: Choose between AI and template generation
        PATTERN: Strategy pattern with guard clause
        """
        if not self.ai_service:
            if self.logger:
                self.logger.log("⚠️  AI Query Service unavailable - using template", "WARNING")
            if self.debug_mixin:
                self.debug_mixin.debug_if_enabled('log_decisions', "Fallback to template ADR")
            return self._generate_adr_template(card, adr_number, structured_requirements)

        return self._generate_adr_with_ai(card, adr_number, structured_requirements, title)

    def _generate_adr_with_ai(
        self,
        card: Dict,
        adr_number: str,
        structured_requirements: Optional[Any],
        title: str
    ) -> str:
        """
        Generate ADR using AI Query Service.

        WHY: Use LLM for intelligent ADR generation
        PATTERN: Guard clauses for error handling
        """
        prompt = self._build_adr_prompt(card, adr_number, structured_requirements)
        keywords = title.split()[:3]

        if self.debug_mixin:
            self.debug_mixin.debug_if_enabled(
                'log_decisions',
                "Using AI Query Service for ADR generation",
                keywords=keywords,
                has_structured_reqs=structured_requirements is not None
            )

        if self.logger:
            self.logger.log("🔄 Using AI Query Service for KG→RAG→LLM pipeline", "INFO")

        result = self.ai_service.query(
            query_type=QueryType.ARCHITECTURE_DESIGN,
            prompt=prompt,
            kg_query_params={
                'keywords': keywords,
                'req_type': 'functional'
            },
            temperature=0.3,
            max_tokens=3000
        )

        if not result.success:
            raise ADRGenerationError(
                f"AI Query Service failed: {result.error}",
                context={"card_id": card.get('card_id'), "title": title}
            )

        self._log_kg_token_savings(result, adr_number, keywords)
        return result.llm_response.content

    def _build_adr_prompt(
        self,
        card: Dict,
        adr_number: str,
        structured_requirements: Optional[Any]
    ) -> str:
        """
        Build prompt for LLM ADR generation.

        WHY: Create comprehensive prompt for AI
        PATTERN: Template pattern with optional sections
        """
        title = card.get('title', 'Untitled Task')
        description = card.get('description', 'No description provided')

        prompt = f"""Generate an Architecture Decision Record (ADR) for the following task:

**Title**: {title}
**Description**: {description}
**Priority**: {card.get('priority', 'medium')}
**Complexity**: {card.get('size', 'medium')}
"""

        if structured_requirements:
            prompt += self._format_structured_requirements_for_prompt(structured_requirements)

        prompt += f"""
Generate ADR-{adr_number} in this format:

# ADR-{adr_number}: {title}

**Status**: Accepted
**Date**: {datetime.utcnow().strftime('%Y-%m-%d')}
**Deciders**: Architecture Agent (Automated)

## Context
[Explain the technical context and problem being solved]

## Decision
[Document the architectural decision and implementation approach]

## Consequences
[List positive and negative consequences]

Focus on actionable implementation guidance."""

        return prompt

    def _generate_adr_template(
        self,
        card: Dict,
        adr_number: str,
        structured_requirements: Optional[Any]
    ) -> str:
        """
        Template-based ADR generation (fallback).

        WHY: Provide fallback when AI unavailable
        PATTERN: Template pattern with sections
        """
        title = card.get('title', 'Untitled Task')
        description = card.get('description', 'No description provided')

        adr_content = f"""# ADR-{adr_number}: {title}

**Status**: Accepted
**Date**: {datetime.utcnow().strftime('%Y-%m-%d')}
**Deciders**: Architecture Agent (Automated)
**Task**: {card['card_id']} - {title}

---

## Context

**Task Description**:
{description}

**Priority**: {card.get('priority', 'medium')}
**Complexity**: {card.get('size', 'medium')}
"""

        if structured_requirements:
            adr_content += self._format_structured_requirements_section(structured_requirements)

        adr_content += """
---

## Decision

"""

        if structured_requirements:
            adr_content += self._get_structured_implementation_strategy(title, structured_requirements)
        else:
            adr_content += self._get_default_implementation_strategy(title)

        adr_content += """
---

## Consequences

### Positive
- ✅ Clear architectural direction for developers
"""

        if structured_requirements:
            adr_content += self._format_positive_consequences(structured_requirements)

        adr_content += """- ✅ Parallel development allows comparison of approaches
- ✅ TDD ensures quality and testability
"""

        if structured_requirements and structured_requirements.constraints:
            adr_content += self._format_constraints(structured_requirements)

        adr_content += """
---

**Note**: This is an automatically generated ADR. For complex tasks, manual architectural review is recommended.
"""

        if structured_requirements:
            adr_content += f"\n**Requirements Source**: Parsed from {structured_requirements.project_name} requirements document (version {structured_requirements.version})\n"

        return adr_content

    def _format_structured_requirements_for_prompt(self, structured_requirements: Any) -> str:
        """Format structured requirements for prompt"""
        content = f"""
**Structured Requirements Available**:
- Project: {structured_requirements.project_name}
- Functional Requirements: {len(structured_requirements.functional_requirements)}
- Non-Functional Requirements: {len(structured_requirements.non_functional_requirements)}
- Use Cases: {len(structured_requirements.use_cases)}

**Top Requirements**:
"""
        for req in structured_requirements.functional_requirements[:3]:
            content += f"- {req.id}: {req.title} [{req.priority.value}]\n"

        return content

    def _format_structured_requirements_section(self, structured_requirements: Any) -> str:
        """Format structured requirements section"""
        content = f"""
**Structured Requirements Available**: ✅
**Project**: {structured_requirements.project_name}
**Requirements Version**: {structured_requirements.version}

### Business Context
"""

        if structured_requirements.executive_summary:
            content += f"""
**Executive Summary**:
{structured_requirements.executive_summary}
"""

        if structured_requirements.business_goals:
            content += "\n**Business Goals**:\n"
            for goal in structured_requirements.business_goals[:5]:
                content += f"- {goal}\n"

        content += f"""
### Requirements Summary
- **Functional Requirements**: {len(structured_requirements.functional_requirements)}
- **Non-Functional Requirements**: {len(structured_requirements.non_functional_requirements)}
- **Use Cases**: {len(structured_requirements.use_cases)}
- **Data Requirements**: {len(structured_requirements.data_requirements)}
- **Integration Requirements**: {len(structured_requirements.integration_requirements)}
- **Stakeholders**: {len(structured_requirements.stakeholders)}

### Key Functional Requirements
"""

        high_priority_reqs = [
            req for req in structured_requirements.functional_requirements
            if req.priority.value in ['critical', 'high']
        ][:5]

        for req in high_priority_reqs:
            content += f"- **{req.id}**: {req.title} [{req.priority.value}]\n"

        if structured_requirements.non_functional_requirements:
            content += "\n### Key Non-Functional Requirements\n"
            nfr_high_priority = [
                req for req in structured_requirements.non_functional_requirements
                if req.priority.value in ['critical', 'high']
            ][:5]

            for req in nfr_high_priority:
                content += f"- **{req.id}**: {req.title} [{req.type.value}, {req.priority.value}]\n"
                if req.target:
                    content += f"  Target: {req.target}\n"

        return content

    def _get_structured_implementation_strategy(self, title: str, structured_requirements: Any) -> str:
        """Get implementation strategy with structured requirements"""
        return f"""**Approach**: Implement {title.lower()} following the structured requirements from {structured_requirements.project_name}.

**Implementation Strategy**:
- Use structured requirements as architectural blueprint
- Functional requirements → Feature implementations
- Non-functional requirements → Technical decisions (performance, security, scalability)
- Data requirements → Data model and database design
- Integration requirements → API and service integration design
- Developer A: Conservative, minimal-risk implementation focusing on critical requirements
- Developer B: Comprehensive implementation with enhanced features
"""

    def _get_default_implementation_strategy(self, title: str) -> str:
        """Get default implementation strategy"""
        return f"""**Approach**: Implement {title.lower()} using test-driven development with parallel developer approaches.

**Implementation Strategy**:
- Developer A: Conservative, minimal-risk implementation
- Developer B: Comprehensive implementation with enhanced features
"""

    def _format_positive_consequences(self, structured_requirements: Any) -> str:
        """Format positive consequences"""
        content = "- ✅ Structured requirements provide comprehensive implementation guidance\n"
        content += "- ✅ Non-functional requirements ensure quality attributes are met\n"
        content += f"- ✅ {len(structured_requirements.use_cases)} use cases validate implementation completeness\n\n"
        return content

    def _format_constraints(self, structured_requirements: Any) -> str:
        """Format constraints section"""
        content = "\n### Constraints\n"
        for constraint in structured_requirements.constraints[:5]:
            content += f"- **{constraint.type.upper()}**: {constraint.description} (Impact: {constraint.impact})\n"
        return content

    def _log_kg_token_savings(self, result: AIQueryResult, adr_number: str, keywords: List[str]) -> None:
        """Log token savings from KG query"""
        if not result.kg_context:
            return
        if result.kg_context.pattern_count == 0:
            return

        if self.logger:
            self.logger.log(
                f"📊 KG found {result.kg_context.pattern_count} ADR patterns, "
                f"saved ~{result.llm_response.tokens_saved} tokens",
                "INFO"
            )

        if self.debug_mixin:
            self.debug_mixin.debug_dump_if_enabled('dump_design', "ADR Generation Details", {
                "adr_number": adr_number,
                "kg_patterns_found": result.kg_context.pattern_count,
                "tokens_saved": result.llm_response.tokens_saved,
                "keywords": keywords
            })
