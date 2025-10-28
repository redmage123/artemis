#!/usr/bin/env python3
"""
WHY: Handle task creation and modification requests
RESPONSIBILITY: Create Kanban cards and respond naturally
PATTERNS: Factory (card creation), Strategy (context-aware responses)

Task handler converts natural language requests into Kanban cards.
"""

import random
from typing import Dict, Any
from datetime import datetime
from chat.models import ChatContext
from kanban_manager import KanbanBoard


class TaskHandler:
    """
    Handles task creation and modification.

    WHY: Users describe tasks in natural language - convert to structured cards.
    PATTERNS: Factory (card creation), Strategy (response variation).
    """

    def __init__(self, kanban: KanbanBoard):
        """
        Initialize task handler.

        Args:
            kanban: Kanban board for task storage
        """
        self.kanban = kanban

    def handle_create_task(
        self,
        intent: Dict[str, Any],
        context: ChatContext
    ) -> str:
        """
        Handle task creation requests.

        WHY: Converts user request into actionable Kanban card.

        Args:
            intent: Intent classification with task description
            context: Conversation context

        Returns:
            Natural language confirmation with card ID

        Example:
            >>> handler = TaskHandler(kanban)
            >>> response = handler.handle_create_task(
            ...     {"parameters": {"task_description": "Build login page"}},
            ...     context
            ... )
            >>> "card-" in response
            True
        """
        params = intent.get("parameters", {})
        task_description = params.get("task_description", "")

        # Guard clause - request more details if description is empty
        if not task_description:
            return "What should I build? Give me some details about what you need."

        # Create Kanban card
        card_id = f"card-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.kanban.add_card({
            "card_id": card_id,
            "title": task_description[:100],  # First 100 chars
            "description": task_description,
            "status": "To Do",
            "created_at": datetime.now().isoformat(),
            "created_by": context.user_id or "chat-user"
        })

        # Set as active card for this session
        context.active_card_id = card_id

        # Generate natural response
        return self._build_create_response(card_id, task_description)

    def _build_create_response(self, card_id: str, task_description: str) -> str:
        """
        Build context-aware response for task creation.

        WHY: Acknowledgment + context shows understanding.

        Args:
            card_id: Created card ID
            task_description: Task description

        Returns:
            Natural language response
        """
        # Base responses (randomized for variety)
        base_responses = [
            f"Got it. I'll start working on that. Your task is {card_id} if you want to check on it later.",
            f"Sounds good. I'm on it - tracking this as {card_id}.",
            f"Alright, building that now. Reference: {card_id}.",
            f"Perfect. I'll get started. Track progress with {card_id}."
        ]

        base_response = random.choice(base_responses)

        # Add context-aware follow-up
        task_lower = task_description.lower()

        # Dispatch table for context-specific additions
        context_additions = {
            "frontend": " This looks like UI work - I'll make sure the design is clean.",
            "ui": " This looks like UI work - I'll make sure the design is clean.",
            "api": " API work noted - I'll focus on solid architecture.",
            "backend": " API work noted - I'll focus on solid architecture.",
            "test": " I'll make sure the tests are thorough."
        }

        # Check for context keywords (early return on first match)
        for keyword, addition in context_additions.items():
            if keyword in task_lower:
                return base_response + addition

        return base_response

    def handle_modify_task(
        self,
        intent: Dict[str, Any],
        context: ChatContext
    ) -> str:
        """
        Handle task modification requests.

        WHY: Placeholder for future functionality.

        Args:
            intent: Intent classification
            context: Conversation context

        Returns:
            Explanation that feature isn't fully implemented
        """
        return "I can update tasks, but that's not fully wired up yet. For now, create a new task with the changes you want."
