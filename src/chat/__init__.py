#!/usr/bin/env python3
"""
WHY: Provide public API for chat package
RESPONSIBILITY: Export main classes for conversational interface
PATTERNS: Facade (simplified package interface)

Chat package provides natural language interface to Artemis pipeline.
"""

from chat.agent import ArtemisChatAgent
from chat.models import ChatMessage, ChatContext
from chat.session_manager import SessionManager

__all__ = [
    'ArtemisChatAgent',
    'ChatMessage',
    'ChatContext',
    'SessionManager',
]
