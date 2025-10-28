#!/usr/bin/env python3
"""
PromptManager Integration for Requirements Parser

WHY: Separate PromptManager logic from main parser
RESPONSIBILITY: Single-call structured extraction via PromptManager + RAG
PATTERNS: Facade pattern - simplifies PromptManager interaction
"""

import json
import re
from typing import Dict, Any, Optional

from llm_client import LLMClient, LLMMessage
from artemis_exceptions import RequirementsParsingError

# Import PromptManager and RAG
try:
    from prompt_manager import PromptManager
    from rag_agent import RAGAgent
    PROMPT_MANAGER_AVAILABLE = True
except ImportError:
    PROMPT_MANAGER_AVAILABLE = False


class PromptManagerIntegration:
    """
    PromptManager-based requirements extraction

    WHY: Production-grade single-call extraction vs multi-step fallback
    RESPONSIBILITY: Use RAG-enhanced prompts for structured extraction
    PATTERNS: Facade pattern for PromptManager complexity
    """

    def __init__(
        self,
        llm: LLMClient,
        rag: Optional[Any] = None,
        verbose: bool = False
    ):
        """
        Initialize PromptManager integration

        Args:
            llm: LLM client for making calls
            rag: RAG agent (optional, will create if needed)
            verbose: Enable verbose logging
        """
        self.llm = llm
        self.verbose = verbose
        self.prompt_manager = None

        if not PROMPT_MANAGER_AVAILABLE:
            self.log("⚠️  PromptManager not available - using hardcoded prompts")
            return

        self._initialize_prompt_manager(rag)

    def parse_with_prompt_manager(
        self,
        raw_text: str,
        project_name: str
    ) -> Dict[str, Any]:
        """
        Parse requirements using PromptManager

        WHY: Single high-quality LLM call vs multiple fallback calls
        RESPONSIBILITY: Execute PromptManager-based extraction

        Args:
            raw_text: Raw requirements text
            project_name: Project name

        Returns:
            Dict with parsed requirements data

        Raises:
            RequirementsParsingError: If extraction fails
        """
        if not self.prompt_manager:
            raise RequirementsParsingError(
                "PromptManager not available",
                context={"prompt_manager_available": PROMPT_MANAGER_AVAILABLE}
            )

        try:
            import uuid

            # Generate IDs for this extraction run
            run_id = f"r-{uuid.uuid4().hex[:8]}"
            correlation_id = f"c-req-{uuid.uuid4().hex[:8]}"

            # Get prompt from PromptManager
            prompt_template = self.prompt_manager.get_prompt("requirements_structured_extraction")

            if not prompt_template:
                raise RequirementsParsingError(
                    "requirements_structured_extraction prompt not found in RAG",
                    context={"prompt_name": "requirements_structured_extraction"}
                )

            # Render prompt with variables
            rendered = self.prompt_manager.render_prompt(
                prompt=prompt_template,
                variables={
                    "run_id": run_id,
                    "correlation_id": correlation_id,
                    "output_format": "json",
                    "user_requirements": raw_text[:10000]  # Limit to 10k chars
                }
            )

            # Call LLM with rendered prompt
            response = self.llm.generate_text(messages=[
                LLMMessage(role="system", content=rendered['system']),
                LLMMessage(role="user", content=rendered['user'])
            ], temperature=0.3)

            # Parse JSON response
            return self._parse_json_response(response.content)

        except RequirementsParsingError:
            # Re-raise already wrapped exceptions
            raise
        except Exception as e:
            raise RequirementsParsingError(
                f"Failed to parse requirements with PromptManager: {str(e)}",
                context={"project_name": project_name},
                original_exception=e
            )

    def is_available(self) -> bool:
        """Check if PromptManager is available and initialized"""
        return self.prompt_manager is not None

    def _initialize_prompt_manager(self, rag: Optional[Any]):
        """Initialize PromptManager with RAG"""
        try:
            # Use provided RAG or create new one
            if rag is None:
                rag = RAGAgent(db_path="db", verbose=False)
            self.prompt_manager = PromptManager(rag, verbose=self.verbose)
            self.log("✅ Prompt manager initialized (using RAG-based prompts)")
        except Exception as e:
            self.log(f"⚠️  Could not initialize PromptManager: {e}")
            self.log("   Falling back to hardcoded prompts")

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response

        WHY: LLM may wrap JSON in markdown blocks
        RESPONSIBILITY: Extract JSON regardless of wrapping
        """
        try:
            # Try direct JSON parse
            return json.loads(response)
        except json.JSONDecodeError as e:
            return self._extract_json_from_markdown(response, e)

    def _extract_json_from_markdown(
        self,
        response: str,
        original_error: Exception
    ) -> Dict[str, Any]:
        """Extract JSON from markdown code blocks"""
        json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if not json_match:
            raise RequirementsParsingError(
                f"LLM returned invalid JSON: {original_error}",
                context={"response_preview": response[:200]},
                original_exception=original_error
            )
        return json.loads(json_match.group(1))

    def log(self, message: str):
        """Log message if verbose"""
        if self.verbose:
            print(f"[PromptManagerIntegration] {message}")
