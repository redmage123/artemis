#!/usr/bin/env python3
"""
WHY: Classify user intent from natural language messages
RESPONSIBILITY: Parse messages and extract intent with parameters
PATTERNS: Strategy (LLM-based classification), Guard Clauses

Intent detector uses LLM to understand user requests and route to
appropriate handlers. Extracts parameters like task descriptions and card IDs.
"""

import json
import re
from typing import Dict, Any
from llm_client import LLMMessage, LLMClient
from chat.models import ChatContext


class IntentDetector:
    """
    Detects user intent from conversation.

    WHY: Natural language is ambiguous - need classification to route correctly.
    PATTERNS: Strategy (LLM classification), Fallback on errors.
    """

    # Intent classification prompt
    CLASSIFICATION_PROMPT = """Analyze the user's message and classify their intent.

Return a JSON object with:
{
  "type": "greeting|create_task|check_status|explain_feature|modify_task|ask_capability|general",
  "parameters": {...extracted params like task description, card_id, etc...},
  "confidence": 0.0-1.0
}

Intent types:
- greeting: Hi, hello, how are you
- create_task: Build X, implement Y, create a feature for Z
- check_status: What's the status of X, how's Y going, is Z done
- explain_feature: How does X work, what can you do, explain Y
- modify_task: Change X, update Y, cancel Z
- ask_capability: Can you do X, are you able to Y
- general: Everything else

Be direct. Extract concrete details."""

    def __init__(self, llm_client: LLMClient, verbose: bool = False):
        """
        Initialize intent detector.

        Args:
            llm_client: LLM client for classification
            verbose: Enable verbose logging
        """
        self.llm_client = llm_client
        self.verbose = verbose

    def detect_intent(
        self,
        message: str,
        context: ChatContext
    ) -> Dict[str, Any]:
        """
        Figure out what the user wants.

        WHY: Routing requires understanding user intent from natural language.

        Args:
            message: User's message
            context: Conversation context

        Returns:
            Intent classification with extracted parameters:
            {
                "type": str,
                "parameters": dict,
                "confidence": float
            }

        Example:
            >>> intent = detector.detect_intent(
            ...     "Build a login page",
            ...     context
            ... )
            >>> intent["type"]
            'create_task'
            >>> intent["parameters"]["task_description"]
            'Build a login page'
        """
        # Build context from recent history
        recent_history = context.conversation_history[-6:]  # Last 3 exchanges
        history_text = self._format_history(recent_history)

        # Build prompt
        user_prompt = f"""Recent conversation:
{history_text if history_text else "(New conversation)"}

Latest message: {message}

Classify the intent:"""

        messages = [
            LLMMessage(role="system", content=self.CLASSIFICATION_PROMPT),
            LLMMessage(role="user", content=user_prompt)
        ]

        # Get LLM classification
        response = self.llm_client.complete(messages, temperature=0.3, max_tokens=500)

        # Parse JSON response
        return self._parse_intent_response(response.content)

    def _format_history(self, messages) -> str:
        """
        Format message history for prompt.

        WHY: Provides conversation context for better classification.

        Args:
            messages: List of ChatMessage objects

        Returns:
            Formatted history string
        """
        return "\n".join([
            f"{'User' if msg.role == 'user' else 'Artemis'}: {msg.content}"
            for msg in messages
        ])

    def _parse_intent_response(self, response: str) -> Dict[str, Any]:
        """
        Parse intent from LLM response.

        WHY: LLM may return JSON in different formats - need robust parsing.

        Args:
            response: LLM response content

        Returns:
            Parsed intent dict (fallback to "general" on error)
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)

            # Guard clause - return fallback if no JSON found
            if not json_match:
                return self._fallback_intent()

            return json.loads(json_match.group(0))

        except Exception as e:
            if self.verbose:
                print(f"[IntentDetector] Parsing failed: {e}")

            return self._fallback_intent()

    def _fallback_intent(self) -> Dict[str, Any]:
        """
        Fallback intent when classification fails.

        WHY: Graceful degradation - route to general handler on errors.

        Returns:
            Generic intent dict
        """
        return {
            "type": "general",
            "parameters": {},
            "confidence": 0.5
        }
