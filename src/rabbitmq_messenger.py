from artemis_logger import get_logger
logger = get_logger('rabbitmq_messenger')
'\nRabbitMQ Messenger - Distributed Inter-Agent Communication (Backward Compatibility Wrapper)\n\nWHY: Maintain backward compatibility while delegating to modular implementation\nRESPONSIBILITY: Provide legacy API that forwards to messaging.rabbitmq package\nPATTERNS: Adapter, Facade, Proxy\n\nThis module serves as a backward compatibility wrapper around the new modular\nmessaging.rabbitmq package. It preserves the original API while delegating all\nfunctionality to the refactored components.\n\nREFACTORED: This file has been refactored into messaging/rabbitmq/ package:\n    - messaging/rabbitmq/models.py - RabbitMQ models and configurations\n    - messaging/rabbitmq/connection_manager.py - Connection lifecycle management\n    - messaging/rabbitmq/publisher.py - Message publishing operations\n    - messaging/rabbitmq/consumer.py - Message consumption operations\n    - messaging/rabbitmq/messenger_core.py - Main messenger implementation\n\nBenefits over file-based:\n- Distributed: Agents can run on different machines\n- Guaranteed delivery: Messages persist until acknowledged\n- Real-time: Push-based, no polling required\n- Scalable: Multiple agent instances can share work\n- Load balancing: Round-robin across worker pools\n\nRequirements:\n    pip install pika\n    docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management\n'
from typing import Dict, List, Optional, Callable
from messenger_interface import MessengerInterface, Message
from messaging.rabbitmq import RabbitMQMessengerCore, RABBITMQ_AVAILABLE

class RabbitMQMessenger(MessengerInterface):
    """
    RabbitMQ-based messenger for distributed agent communication (Backward Compatibility Wrapper)

    This class wraps the new RabbitMQMessengerCore implementation to maintain
    backward compatibility with existing code.

    Usage:
        messenger = RabbitMQMessenger(
            agent_name="architecture-agent",
            rabbitmq_url="amqp://localhost"
        )

        # Send message
        messenger.send_message(
            to_agent="dependency-validation-agent",
            message_type="data_update",
            card_id="card-123",
            data={"adr_file": "/tmp/adr/ADR-001.md"}
        )

        # Read messages (blocking, waits for messages)
        def handle_message(message):
            print(f"Received: {message.data}")

        messenger.start_consuming(callback=handle_message)
    """

    def __init__(self, agent_name: str, rabbitmq_url: str='amqp://localhost', durable: bool=True, prefetch_count: int=1):
        """
        Initialize RabbitMQ messenger

        Args:
            agent_name: Name of this agent
            rabbitmq_url: RabbitMQ connection URL
            durable: Whether queues/messages persist across restarts
            prefetch_count: How many unacknowledged messages to buffer
        """
        if not RABBITMQ_AVAILABLE:
            raise ImportError("RabbitMQ messenger requires 'pika' package. Install with: pip install pika")
        self._core = RabbitMQMessengerCore(agent_name=agent_name, rabbitmq_url=rabbitmq_url, durable=durable, prefetch_count=prefetch_count)
        self.agent_name = agent_name

    def send_message(self, to_agent: str, message_type: str, data: Dict, card_id: str, priority: str='medium', metadata: Optional[Dict]=None) -> str:
        """Send message to another agent via RabbitMQ"""
        return self._core.send_message(to_agent=to_agent, message_type=message_type, data=data, card_id=card_id, priority=priority, metadata=metadata)

    def read_messages(self, message_type: Optional[str]=None, from_agent: Optional[str]=None, priority: Optional[str]=None, unread_only: bool=True, mark_as_read: bool=True) -> List[Message]:
        """Read messages from queue (non-blocking)"""
        return self._core.read_messages(message_type=message_type, from_agent=from_agent, priority=priority, unread_only=unread_only, mark_as_read=mark_as_read)

    def start_consuming(self, callback: Callable[[Message], None]) -> None:
        """Start consuming messages (blocking)"""
        self._core.start_consuming(callback)

    def send_data_update(self, to_agent: str, card_id: str, update_type: str, data: Dict, priority: str='medium') -> str:
        """Send data update"""
        return self._core.send_data_update(to_agent=to_agent, card_id=card_id, update_type=update_type, data=data, priority=priority)

    def send_notification(self, to_agent: str, card_id: str, notification_type: str, data: Dict, priority: str='low') -> str:
        """Send notification"""
        return self._core.send_notification(to_agent=to_agent, card_id=card_id, notification_type=notification_type, data=data, priority=priority)

    def send_error(self, to_agent: str, card_id: str, error_type: str, message: str, severity: str='high', blocks_pipeline: bool=True, resolution_suggestions: Optional[List[str]]=None) -> str:
        """Send error"""
        return self._core.send_error(to_agent=to_agent, card_id=card_id, error_type=error_type, message=message, severity=severity, blocks_pipeline=blocks_pipeline, resolution_suggestions=resolution_suggestions)

    def update_shared_state(self, card_id: str, updates: Dict) -> None:
        """Update shared pipeline state"""
        self._core.update_shared_state(card_id, updates)

    def get_shared_state(self, card_id: Optional[str]=None) -> Dict:
        """Get current shared pipeline state"""
        return self._core.get_shared_state(card_id)

    def register_agent(self, capabilities: List[str], status: str='active') -> None:
        """Register agent in agent registry"""
        self._core.register_agent(capabilities, status)

    def cleanup(self) -> None:
        """Cleanup resources"""
        self._core.cleanup()

    def get_messenger_type(self) -> str:
        """Get messenger implementation type"""
        return self._core.get_messenger_type()
if __name__ == '__main__':
    '\n    Example usage of RabbitMQ messenger\n\n    Prerequisites:\n        docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:3-management\n        pip install pika\n    '
    if not RABBITMQ_AVAILABLE:
        
        logger.log("❌ RabbitMQ messenger requires 'pika' package", 'INFO')
        
        logger.log('Install with: pip install pika', 'INFO')
        exit(1)
    
    logger.log('RabbitMQ Messenger - Example Usage', 'INFO')
    
    logger.log('=' * 60, 'INFO')
    messenger = RabbitMQMessenger(agent_name='example-agent', rabbitmq_url='amqp://localhost')
    msg_id = messenger.send_data_update(to_agent='test-agent', card_id='card-123', update_type='test', data={'hello': 'world'})
    
    logger.log(f'✅ Sent message: {msg_id}', 'INFO')
    messenger.cleanup()
    
    logger.log('✅ Cleaned up', 'INFO')