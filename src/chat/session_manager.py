#!/usr/bin/env python3
"""
WHY: Manage conversation sessions and message history
RESPONSIBILITY: Create, retrieve, and update conversation sessions
PATTERNS: Repository (session storage), Factory (session creation)

Session manager maintains conversation continuity across multiple interactions.
"""

from typing import Dict, Optional
from datetime import datetime
from chat.models import ChatContext, ChatMessage


class SessionManager:
    """
    Manages conversation sessions.

    WHY: Conversations need continuity - session tracking enables context.
    PATTERNS: Repository (in-memory session storage).
    """

    def __init__(self):
        """Initialize session manager"""
        # In-memory session storage (keyed by session_id)
        self.sessions: Dict[str, ChatContext] = {}

    def get_or_create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> ChatContext:
        """
        Get existing session or create new one.

        WHY: Ensures session exists before conversation starts.

        Args:
            session_id: Unique session identifier
            user_id: Optional user identifier

        Returns:
            ChatContext for this session

        Example:
            >>> manager = SessionManager()
            >>> context = manager.get_or_create_session("abc123")
            >>> context.session_id
            'abc123'
        """
        # Guard clause - return existing session if found
        if session_id in self.sessions:
            return self.sessions[session_id]

        # Create new session
        context = ChatContext(
            session_id=session_id,
            user_id=user_id
        )

        self.sessions[session_id] = context
        return context

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Add message to session history.

        WHY: Maintains conversation context for better responses.

        Args:
            session_id: Session identifier
            role: "user" or "assistant"
            content: Message content
            metadata: Optional metadata

        Raises:
            ValueError: If session doesn't exist
        """
        # Guard clause - verify session exists
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        context = self.sessions[session_id]

        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata
        )

        context.conversation_history.append(message)

    def set_active_card(self, session_id: str, card_id: str) -> None:
        """
        Set active card for session.

        WHY: Tracks which task user is currently discussing.

        Args:
            session_id: Session identifier
            card_id: Card ID to set as active
        """
        # Guard clause - verify session exists
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        self.sessions[session_id].active_card_id = card_id

    def get_session(self, session_id: str) -> Optional[ChatContext]:
        """
        Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            ChatContext or None if not found
        """
        return self.sessions.get(session_id)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True

        return False
