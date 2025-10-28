#!/usr/bin/env python3
"""
User Story Generator

WHY: Convert ADRs into actionable user stories
RESPONSIBILITY: Generate user stories from architectural decisions
PATTERNS: Single Responsibility, Guard Clauses
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple

try:
    from llm_client import LLMMessage
    LLM_CLIENT_AVAILABLE = True
except ImportError:
    LLM_CLIENT_AVAILABLE = False


class UserStoryGenerator:
    """
    Generates user stories from ADR content.

    WHY: Separate user story generation from ADR creation
    RESPONSIBILITY: Convert ADRs to user stories only
    PATTERNS: Single Responsibility, Guard Clauses
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        prompt_manager: Optional[Any] = None,
        logger: Optional[Any] = None
    ):
        """
        Initialize user story generator.

        Args:
            llm_client: LLM client for generation
            prompt_manager: Prompt manager for RAG-based prompts
            logger: Logger interface
        """
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.logger = logger

    def generate_user_stories(
        self,
        adr_content: str,
        adr_number: str,
        parent_card: Dict
    ) -> List[Dict]:
        """
        Generate user stories from ADR content.

        Args:
            adr_content: Full ADR markdown content
            adr_number: ADR number (e.g., "001")
            parent_card: Parent task card

        Returns:
            List of user story dicts with title, description, acceptance_criteria, points

        WHY: Main entry point for user story generation
        PATTERN: Guard clauses for missing dependencies
        """
        if self.logger:
            self.logger.log(f"🤖 Generating user stories from ADR-{adr_number}...", "INFO")

        if not self.llm_client:
            if self.logger:
                self.logger.log("⚠️  No LLM client available - skipping user story generation", "WARNING")
            return []

        if not LLM_CLIENT_AVAILABLE:
            if self.logger:
                self.logger.log("⚠️  LLM client module unavailable", "WARNING")
            return []

        try:
            system_message, user_message = self._get_prompts(adr_content)
            response = self._call_llm(system_message, user_message)
            user_stories = self._parse_llm_response(response)

            if self.logger:
                self.logger.log(f"✅ Generated {len(user_stories)} user stories from ADR-{adr_number}", "INFO")

            return user_stories

        except Exception as e:
            if self.logger:
                self.logger.log(f"❌ Failed to generate user stories: {e}", "ERROR")
            return []

    def _get_prompts(self, adr_content: str) -> Tuple[str, str]:
        """
        Get system and user messages for user story generation.

        WHY: Support both RAG and default prompts
        PATTERN: Guard clause for prompt manager availability
        """
        if not self.prompt_manager:
            return self._get_default_prompts(adr_content)

        try:
            if self.logger:
                self.logger.log("📝 Loading architecture prompt from RAG", "INFO")

            prompt_template = self.prompt_manager.get_prompt("architecture_design_adr")

            if not prompt_template:
                raise Exception("Prompt not found in RAG")

            rendered = self.prompt_manager.render_prompt(
                prompt=prompt_template,
                variables={
                    "context": "Converting ADR to user stories",
                    "requirements": adr_content,
                    "constraints": "Focus on implementation tasks",
                    "scale_expectations": "2-5 user stories"
                }
            )

            if self.logger:
                self.logger.log(
                    f"✅ Loaded RAG prompt with {len(prompt_template.perspectives)} perspectives",
                    "INFO"
                )

            return rendered['system'], rendered['user']

        except Exception as e:
            if self.logger:
                self.logger.log(f"⚠️  Error loading RAG prompt: {e} - using default", "WARNING")
            return self._get_default_prompts(adr_content)

    def _get_default_prompts(self, adr_content: str) -> Tuple[str, str]:
        """
        Get default prompts for user story generation.

        WHY: Fallback when prompt manager unavailable
        PATTERN: Template pattern
        """
        system_message = """You are an expert at converting Architecture Decision Records (ADRs) into actionable user stories.
Generate user stories that implement the architectural decisions, following best practices:
- Use "As a [role], I want [feature], so that [benefit]" format
- Include specific acceptance criteria
- Estimate story points (1-8 scale)
- Break down complex decisions into multiple stories"""

        user_message = f"""Convert the following ADR into user stories:

{adr_content}

Generate 2-5 user stories in JSON format:
{{
  "user_stories": [
    {{
      "title": "As a developer, I want to implement X, so that Y",
      "description": "Detailed description of what needs to be built",
      "acceptance_criteria": [
        "Given X, when Y, then Z",
        "Criterion 2"
      ],
      "points": 5,
      "priority": "high"
    }}
  ]
}}

Focus on implementation tasks, not architectural discussions."""

        return system_message, user_message

    def _call_llm(self, system_message: str, user_message: str) -> str:
        """
        Call LLM with messages.

        WHY: Encapsulate LLM API call
        PATTERN: Guard clause for errors
        """
        messages = [
            LLMMessage(role="system", content=system_message),
            LLMMessage(role="user", content=user_message)
        ]

        llm_response = self.llm_client.complete(
            messages=messages,
            temperature=0.4,
            max_tokens=2000
        )

        return llm_response.content

    def _parse_llm_response(self, response: str) -> List[Dict]:
        """
        Parse JSON response from LLM.

        WHY: Extract user stories from LLM response
        PATTERN: Guard clauses for parsing errors
        """
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            if self.logger:
                self.logger.log("⚠️  LLM response did not contain valid JSON", "WARNING")
            return []

        data = json.loads(json_match.group(0))
        return data.get('user_stories', [])
