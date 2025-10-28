#!/usr/bin/env python3
"""
WHY: Define data structures for chat conversations
RESPONSIBILITY: Immutable data models for messages and context
PATTERNS: Value Object (immutable dataclasses), Default Factory

Chat models represent conversation state without containing business logic.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ChatMessage:
    """
    A message in the conversation.

    WHY: Messages need timestamp and metadata for conversation tracking.
    PATTERNS: Value Object (immutable data structure).
    """
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatContext:
    """
    Conversation context and state.

    WHY: Maintains conversation continuity and personalization.
    PATTERNS: Value Object, Default Factory (for mutable defaults).

    Tracks:
    - session_id: Unique conversation identifier
    - user_id: Optional user identifier
    - active_card_id: Currently referenced task
    - conversation_history: Message history
    - personality_state: Tone, formality, verbosity settings
    """
    session_id: str
    user_id: Optional[str] = None
    active_card_id: Optional[str] = None
    conversation_history: List[ChatMessage] = field(default_factory=list)
    personality_state: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        Initialize default personality if not provided.

        WHY: Provides sensible defaults for conversational tone.
        """
        if not self.personality_state:
            self.personality_state = {
                "formality": "casual",  # casual, professional, technical
                "verbosity": "balanced",  # concise, balanced, detailed
                "empathy_level": "medium"  # low, medium, high
            }
