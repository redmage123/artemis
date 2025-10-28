#!/usr/bin/env python3
"""
WHY: Handle general conversation that doesn't fit specific intents
RESPONSIBILITY: Provide natural, contextual responses using LLM
PATTERNS: Facade (conversation API), Context building

General handler maintains natural conversation flow for unclassified messages.
"""

from typing import Dict, Any
from chat.models import ChatContext
from llm_client import LLMClient, LLMMessage


class GeneralHandler:
    """
    Handles general conversation.

    WHY: Not all conversation fits specific intents - need flexible fallback.
    PATTERNS: LLM-based (context-aware responses).
    """

    # Core personality for responses
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

    def __init__(self, llm_client: LLMClient):
        """
        Initialize general handler.

        Args:
            llm_client: LLM client for responses
        """
        self.llm_client = llm_client

    def handle(
        self,
        intent: Dict[str, Any],
        context: ChatContext
    ) -> str:
        """
        Handle general conversation.

        WHY: Maintains natural flow for messages that don't fit specific intents.

        Args:
            intent: Intent classification
            context: Conversation context with history

        Returns:
            Natural language response

        Example:
            >>> handler = GeneralHandler(llm_client)
            >>> response = handler.handle({}, context)
        """
        # Build conversation context from history
        recent_messages = context.conversation_history[-10:]
        history_text = self._format_history(recent_messages[:-1])  # Exclude current

        # Build system prompt with context
        system_prompt = self.CORE_PERSONALITY + f"""

Conversation context:
{history_text if history_text else "(Start of conversation)"}

Active task: {context.active_card_id or "None"}

Respond naturally to the user's message. Stay in character - you're Artemis, the autonomous dev system."""

        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=recent_messages[-1].content)
        ]

        response = self.llm_client.complete(messages, temperature=0.8, max_tokens=500)
        return response.content

    def _format_history(self, messages) -> str:
        """
        Format conversation history.

        WHY: Provides context for better responses.

        Args:
            messages: List of ChatMessage objects

        Returns:
            Formatted history string
        """
        return "\n".join([
            f"{'User' if msg.role == 'user' else 'Artemis'}: {msg.content}"
            for msg in messages
        ])
