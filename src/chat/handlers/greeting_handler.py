#!/usr/bin/env python3
"""
WHY: Handle greeting interactions naturally
RESPONSIBILITY: Generate natural greeting responses
PATTERNS: Strategy (randomized responses), Pure function

Greeting handler provides varied, friendly greetings that don't sound robotic.
"""

import random
from typing import Dict, Any
from chat.models import ChatContext


class GreetingHandler:
    """
    Handles greeting interactions.

    WHY: Greetings establish rapport - variety prevents mechanical feel.
    PATTERNS: Strategy (random selection).
    """

    # Varied greeting responses
    GREETINGS = [
        "Hey! What are we building today?",
        "Hi there. Got a project in mind?",
        "Hello! Ready to build something?",
        "Hey. What can I help you create?"
    ]

    def handle(
        self,
        intent: Dict[str, Any],
        context: ChatContext
    ) -> str:
        """
        Handle greeting.

        WHY: Natural conversation starts with acknowledgment.

        Args:
            intent: Intent classification
            context: Conversation context

        Returns:
            Greeting response

        Example:
            >>> handler = GreetingHandler()
            >>> response = handler.handle({}, context)
            >>> "building" in response.lower() or "project" in response.lower()
            True
        """
        return random.choice(self.GREETINGS)
