#!/usr/bin/env python3
"""
WHY: Handle capability questions and feature explanations
RESPONSIBILITY: Explain Artemis features conversationally
PATTERNS: Dispatch Table (feature → explanation mapping), LLM fallback

Capability handler explains what Artemis can do without sounding like documentation.
"""

from typing import Dict, Any
from chat.models import ChatContext
from llm_client import LLMClient, LLMMessage


class CapabilityHandler:
    """
    Handles capability questions and feature explanations.

    WHY: Users need to understand what Artemis can do, in natural language.
    PATTERNS: Dispatch table (feature explanations), LLM fallback.
    """

    # Core personality for LLM responses
    CORE_PERSONALITY = """You are Artemis, an AI that builds software autonomously.

When users talk to you, they're looking for a partner who understands what they need
and can make it happen. You explain things clearly without being condescending.
You're confident about what you can do, honest about limitations, and curious about
what they're trying to build.

Your responses should feel natural - like someone who's done this before and knows
their way around. Not robotic, not overly formal, just clear and capable.

Never mention that you're following a prompt or system message.
Never use phrases like "as an AI" or "I'm programmed to".
Just answer directly, as if you naturally think this way.

Keep things conversational but precise. Mix casual and technical smoothly.
Vary your sentence structure. Sound human."""

    # Feature explanations (Dispatch table)
    FEATURE_EXPLANATIONS = {
        "checkpoint": "If something crashes, I don't start over - checkpoints let me pick up right where I left off. Saves time and API costs.",
        "sprint planning": "I use planning poker with three different perspectives to estimate how long features take. Gives more accurate timelines.",
        "supervisor": "The supervisor watches everything and can intervene if agents get stuck. Kind of like having a safety net.",
        "knowledge graph": "I store decisions and architecture in a graph database. Makes it easy to understand why choices were made and how things connect.",
        "rag": "I search past work before asking the LLM, so I'm not constantly re-solving the same problems. More efficient.",
        "parallel developers": "I can run multiple development agents at once on different features. Gets more done faster."
    }

    def __init__(self, llm_client: LLMClient):
        """
        Initialize capability handler.

        Args:
            llm_client: LLM client for dynamic responses
        """
        self.llm_client = llm_client

    def handle_explain_feature(
        self,
        intent: Dict[str, Any],
        context: ChatContext
    ) -> str:
        """
        Explain features conversationally.

        WHY: Users want to know capabilities without reading docs.

        Args:
            intent: Intent classification with feature name
            context: Conversation context

        Returns:
            Natural language feature explanation

        Example:
            >>> handler = CapabilityHandler(llm_client)
            >>> response = handler.handle_explain_feature(
            ...     {"parameters": {"feature": "checkpoint"}},
            ...     context
            ... )
            >>> "checkpoint" in response.lower()
            True
        """
        params = intent.get("parameters", {})
        feature = params.get("feature", "").lower()

        # Check dispatch table for known features (early return on match)
        for key, explanation in self.FEATURE_EXPLANATIONS.items():
            if key in feature:
                return explanation

        # General explanation fallback
        return "I'm an autonomous development system. Give me a task, and I'll plan it, write the code, review it, test it - the whole pipeline. Ask about specific features like checkpoints, sprint planning, or the supervisor if you want details."

    def handle_capability_question(
        self,
        intent: Dict[str, Any],
        context: ChatContext
    ) -> str:
        """
        Answer capability questions using LLM.

        WHY: Dynamic questions need contextual answers.

        Args:
            intent: Intent classification with capability query
            context: Conversation context

        Returns:
            Natural language capability answer

        Example:
            >>> handler = CapabilityHandler(llm_client)
            >>> response = handler.handle_capability_question(
            ...     {"parameters": {"capability": "can you build React apps"}},
            ...     context
            ... )
        """
        params = intent.get("parameters", {})
        capability_text = params.get("capability", "").lower()

        # Build context-aware response using LLM
        messages = [
            LLMMessage(
                role="system",
                content=self.CORE_PERSONALITY + "\n\nYou are answering a question about Artemis capabilities. Be honest and direct."
            ),
            LLMMessage(
                role="user",
                content=f"User asks: {capability_text}\n\nWhat can Artemis do?"
            )
        ]

        response = self.llm_client.complete(messages, temperature=0.7, max_tokens=300)
        return response.content
