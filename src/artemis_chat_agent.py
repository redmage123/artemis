#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER

This module maintains backward compatibility while the codebase migrates
to the new modular structure in chat/.

All functionality has been refactored into:
- chat/models.py - ChatMessage, ChatContext
- chat/intent_detector.py - Intent detection
- chat/session_manager.py - Session management
- chat/handlers/greeting_handler.py - Greeting responses
- chat/handlers/task_handler.py - Task creation/modification
- chat/handlers/status_handler.py - Status checking
- chat/handlers/capability_handler.py - Feature explanations
- chat/handlers/general_handler.py - General conversation
- chat/agent.py - ArtemisChatAgent orchestrator

To migrate your code:
    OLD: from artemis_chat_agent import ArtemisChatAgent, ChatMessage, ChatContext
    NEW: from chat import ArtemisChatAgent, ChatMessage, ChatContext

No breaking changes - all imports remain identical.
"""

# Re-export all public APIs from the modular package
from chat import (
    ArtemisChatAgent,
    ChatMessage,
    ChatContext,
    SessionManager,
)

__all__ = [
    'ArtemisChatAgent',
    'ChatMessage',
    'ChatContext',
    'SessionManager',
]

# ============================================================================
# CLI INTERFACE FOR TESTING
# ============================================================================

if __name__ == "__main__":
    """Test the chat agent interactively"""
    import sys
    import uuid

    print("="*60)
    print("ARTEMIS CHAT AGENT")
    print("="*60)
    print("Talk to Artemis naturally. Type 'quit' to exit.\n")

    agent = ArtemisChatAgent(verbose=True)
    session_id = str(uuid.uuid4())

    while True:
        try:
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "bye"]:
                print("\nArtemis: See you later!")
                break

            response = agent.chat(user_input, session_id=session_id)
            print(f"\nArtemis: {response}\n")

        except KeyboardInterrupt:
            print("\n\nArtemis: Interrupted. See you!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")
