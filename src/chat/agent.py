#!/usr/bin/env python3
"""
WHY: Provide conversational interface to Artemis pipeline
RESPONSIBILITY: Orchestrate intent detection, routing, and response generation
PATTERNS: Facade (simplified chat API), Strategy (intent routing)

Chat agent makes technical development workflows feel like talking to a capable
colleague who happens to be very good at building software autonomously.
"""

from typing import Optional
from llm_client import create_llm_client
from kanban_manager import KanbanBoard
from chat.models import ChatMessage, ChatContext
from chat.session_manager import SessionManager
from chat.intent_detector import IntentDetector
from chat.handlers import (
    GreetingHandler,
    TaskHandler,
    StatusHandler,
    CapabilityHandler,
    GeneralHandler
)
from datetime import datetime


class ArtemisChatAgent:
    """
    Conversational interface to Artemis pipeline.

    WHY: Makes technical workflows accessible through natural conversation.
    RESPONSIBILITY: Route messages to handlers, maintain conversation flow.
    PATTERNS: Facade (simplified API), Strategy (intent routing via dispatch table).
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        kanban_board_path: str = "kanban_board.json",
        verbose: bool = False
    ):
        """
        Initialize chat agent.

        Args:
            llm_provider: LLM provider ("openai" or "anthropic")
            kanban_board_path: Path to Kanban board JSON
            verbose: Enable verbose logging
        """
        self.verbose = verbose

        # Initialize dependencies
        self.llm_client = create_llm_client(llm_provider)
        self.kanban = KanbanBoard(kanban_board_path)

        # Initialize components (Composition pattern)
        self.session_manager = SessionManager()
        self.intent_detector = IntentDetector(self.llm_client, verbose)

        # Initialize handlers
        self.greeting_handler = GreetingHandler()
        self.task_handler = TaskHandler(self.kanban)
        self.status_handler = StatusHandler(self.kanban, verbose)
        self.capability_handler = CapabilityHandler(self.llm_client)
        self.general_handler = GeneralHandler(self.llm_client)

        # Intent routing (Dispatch table - no if/elif chain)
        self.intent_handlers = {
            "greeting": self.greeting_handler.handle,
            "create_task": self.task_handler.handle_create_task,
            "check_status": self.status_handler.handle,
            "explain_feature": self.capability_handler.handle_explain_feature,
            "modify_task": self.task_handler.handle_modify_task,
            "ask_capability": self.capability_handler.handle_capability_question,
        }

    def chat(
        self,
        user_message: str,
        session_id: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Process user message and return response.

        WHY: Single entry point for all conversational interaction.

        Args:
            user_message: What the user said
            session_id: Unique session identifier
            user_id: Optional user identifier

        Returns:
            Natural language response

        Example:
            >>> agent = ArtemisChatAgent()
            >>> response = agent.chat(
            ...     "Build a login page",
            ...     session_id="abc123"
            ... )
            >>> "card-" in response
            True
        """
        # Get or create session
        context = self.session_manager.get_or_create_session(session_id, user_id)

        # Add user message to history
        self.session_manager.add_message(
            session_id,
            role="user",
            content=user_message
        )

        # Detect intent
        intent = self.intent_detector.detect_intent(user_message, context)

        # Route to appropriate handler (dispatch table lookup)
        handler = self.intent_handlers.get(
            intent["type"],
            self.general_handler.handle  # Default handler
        )

        response = handler(intent, context)

        # Add response to history
        self.session_manager.add_message(
            session_id,
            role="assistant",
            content=response
        )

        return response
