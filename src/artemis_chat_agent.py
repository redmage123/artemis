from artemis_logger import get_logger
logger = get_logger('artemis_chat_agent')
'\nBACKWARD COMPATIBILITY WRAPPER\n\nThis module maintains backward compatibility while the codebase migrates\nto the new modular structure in chat/.\n\nAll functionality has been refactored into:\n- chat/models.py - ChatMessage, ChatContext\n- chat/intent_detector.py - Intent detection\n- chat/session_manager.py - Session management\n- chat/handlers/greeting_handler.py - Greeting responses\n- chat/handlers/task_handler.py - Task creation/modification\n- chat/handlers/status_handler.py - Status checking\n- chat/handlers/capability_handler.py - Feature explanations\n- chat/handlers/general_handler.py - General conversation\n- chat/agent.py - ArtemisChatAgent orchestrator\n\nTo migrate your code:\n    OLD: from artemis_chat_agent import ArtemisChatAgent, ChatMessage, ChatContext\n    NEW: from chat import ArtemisChatAgent, ChatMessage, ChatContext\n\nNo breaking changes - all imports remain identical.\n'
from chat import ArtemisChatAgent, ChatMessage, ChatContext, SessionManager
__all__ = ['ArtemisChatAgent', 'ChatMessage', 'ChatContext', 'SessionManager']
if __name__ == '__main__':
    'Test the chat agent interactively'
    import sys
    import uuid
    
    logger.log('=' * 60, 'INFO')
    
    logger.log('ARTEMIS CHAT AGENT', 'INFO')
    
    logger.log('=' * 60, 'INFO')
    
    logger.log("Talk to Artemis naturally. Type 'quit' to exit.\n", 'INFO')
    agent = ArtemisChatAgent(verbose=True)
    session_id = str(uuid.uuid4())
    while True:
        try:
            user_input = input('You: ').strip()
            if not user_input:
                continue
            if user_input.lower() in ['quit', 'exit', 'bye']:
                
                logger.log('\nArtemis: See you later!', 'INFO')
                break
            response = agent.chat(user_input, session_id=session_id)
            
            logger.log(f'\nArtemis: {response}\n', 'INFO')
        except KeyboardInterrupt:
            
            logger.log('\n\nArtemis: Interrupted. See you!', 'INFO')
            break
        except Exception as e:
            
            logger.log(f'\nError: {e}\n', 'INFO')