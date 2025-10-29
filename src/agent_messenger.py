from artemis_logger import get_logger
logger = get_logger('agent_messenger')
'\nAgent Messenger - File-Based Inter-Agent Communication System\n\nBACKWARD COMPATIBILITY WRAPPER\n\nThis file maintains backward compatibility with existing code that imports\nfrom agent_messenger.py. All functionality has been refactored into the\nmessaging.agent package for better modularity and maintainability.\n\nWHY: Ensure existing code continues to work without modification.\nRESPONSIBILITY: Re-export classes and functions from new package structure.\nPATTERNS: Facade Pattern, Deprecation Wrapper.\n\nNew code should import from:\n    from messaging.agent import AgentMessenger, send_update, send_notification, send_error\n\nThis wrapper will be maintained until all imports are migrated.\n'
from messaging.agent import AgentMessenger, MessageType, MessagePriority, AgentStatus, send_update, send_notification, send_error
__all__ = ['AgentMessenger', 'MessageType', 'MessagePriority', 'AgentStatus', 'send_update', 'send_notification', 'send_error']
if __name__ == '__main__':
    
    logger.log('Agent Messenger - Example Usage', 'INFO')
    
    logger.log('=' * 60, 'INFO')
    arch = AgentMessenger('architecture-agent')
    arch.register_agent(capabilities=['create_adr', 'evaluate_options', 'document_decisions'])
    msg_id = arch.send_data_update(to_agent='dependency-validation-agent', card_id='card-123', update_type='adr_created', data={'adr_file': '/tmp/adr/ADR-001.md', 'dependencies': ['chromadb>=0.4.0']})
    
    logger.log(f'✅ Sent message: {msg_id}', 'INFO')
    arch.update_shared_state(card_id='card-123', updates={'agent_status': 'COMPLETE', 'adr_file': '/tmp/adr/ADR-001.md'})
    
    logger.log('✅ Updated shared state', 'INFO')
    dep_val = AgentMessenger('dependency-validation-agent')
    messages = dep_val.read_messages()
    
    logger.log(f'✅ Read {len(messages)} messages', 'INFO')
    for msg in messages:
        
        logger.log(f'\n  From: {msg.from_agent}', 'INFO')
        
        logger.log(f'  Type: {msg.message_type}', 'INFO')
        
        logger.log(f'  Data: {msg.data}', 'INFO')
    state = dep_val.get_shared_state(card_id='card-123')
    
    logger.log(f'\n✅ Shared state:', 'INFO')
    
    logger.log(f"  ADR File: {state.get('shared_data', {}).get('adr_file')}", 'INFO')
    
    logger.log('\n' + '=' * 60, 'INFO')
    
    logger.log('Example complete!', 'INFO')