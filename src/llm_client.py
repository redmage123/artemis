from artemis_logger import get_logger
logger = get_logger('llm_client')
"\nLLM Client - Backward Compatibility Wrapper\n\nWHY: Maintain backward compatibility while using modular implementation.\nRESPONSIBILITY: Re-export all components from llm package.\nPATTERNS: Facade Pattern, Re-export Pattern.\n\nSingle Responsibility: Provide backward-compatible interface to refactored code\nOpen/Closed: Implementation changes don't affect existing imports\n"
from llm.llm_models import LLMProvider, LLMMessage, LLMResponse
from llm.llm_interface import LLMClientInterface
from llm.openai_client import OpenAIClient
from llm.anthropic_client import AnthropicClient
from llm.llm_factory import LLMClientFactory
from llm.stream_processor import StreamProcessor
from typing import Optional

def create_llm_client(provider: str='openai', api_key: Optional[str]=None) -> LLMClientInterface:
    """
    Convenience function to create LLM client

    WHY: Provides simple string-based interface for client creation.
    RESPONSIBILITY: Delegate to factory with string conversion.

    Args:
        provider: "openai" or "anthropic"
        api_key: API key (optional, will use env var if not provided)

    Returns:
        LLMClientInterface implementation

    Example:
        client = create_llm_client("openai")
        messages = [
            LLMMessage(role="system", content="You are a helpful assistant"),
            LLMMessage(role="user", content="Write a Python function to add two numbers")
        ]
        response = client.complete(messages)
        print(response.content)
    """
    return LLMClientFactory.create_from_string(provider, api_key)

class LLMClient:
    """
    Backwards compatibility wrapper

    WHY: Preserve existing code that uses LLMClient.create_from_env() or LLMClient.create().
    RESPONSIBILITY: Delegate to factory methods.
    PATTERNS: Facade Pattern.

    Provides both type compatibility (for isinstance checks) and factory methods
    """

    @staticmethod
    def create_from_env() -> LLMClientInterface:
        """
        Create LLM client from environment variables

        WHY: Backward compatibility for existing code.
        """
        return LLMClientFactory.create_from_env()

    @staticmethod
    def create(provider: LLMProvider, api_key: Optional[str]=None) -> LLMClientInterface:
        """
        Create LLM client

        WHY: Backward compatibility for existing code.
        """
        return LLMClientFactory.create(provider, api_key)
if __name__ == '__main__':
    'Test LLM client backward compatibility'
    import sys
    from artemis_exceptions import wrap_exception, LLMClientError
    
    logger.log('Testing OpenAI client...', 'INFO')
    try:
        openai_client = create_llm_client('openai')
        
        logger.log(f'✅ OpenAI client created', 'INFO')
        
        logger.log(f"Available models: {', '.join(openai_client.get_available_models()[:3])}...", 'INFO')
        messages = [LLMMessage(role='system', content='You are a helpful assistant.'), LLMMessage(role='user', content="Say 'Hello from OpenAI!' and nothing else.")]
        response = openai_client.complete(messages, max_tokens=100)
        
        logger.log(f'✅ Response: {response.content}', 'INFO')
        
        logger.log(f'   Model: {response.model}', 'INFO')
        
        logger.log(f"   Tokens: {response.usage['total_tokens']}", 'INFO')
    except Exception as e:
        error = wrap_exception(e, LLMClientError, 'OpenAI test failed', {'provider': 'openai'})
        
        logger.log(f'❌ OpenAI test failed: {error}', 'INFO')
    
    logger.log('\n' + '=' * 60 + '\n', 'INFO')
    
    logger.log('Testing Anthropic client...', 'INFO')
    try:
        anthropic_client = create_llm_client('anthropic')
        
        logger.log(f'✅ Anthropic client created', 'INFO')
        
        logger.log(f"Available models: {', '.join(anthropic_client.get_available_models()[:3])}...", 'INFO')
        messages = [LLMMessage(role='system', content='You are a helpful assistant.'), LLMMessage(role='user', content="Say 'Hello from Anthropic!' and nothing else.")]
        response = anthropic_client.complete(messages, max_tokens=100)
        
        logger.log(f'✅ Response: {response.content}', 'INFO')
        
        logger.log(f'   Model: {response.model}', 'INFO')
        
        logger.log(f"   Tokens: {response.usage['total_tokens']}", 'INFO')
    except Exception as e:
        error = wrap_exception(e, LLMClientError, 'Anthropic test failed', {'provider': 'anthropic'})
        
        logger.log(f'❌ Anthropic test failed: {error}', 'INFO')
    
    logger.log('\n' + '=' * 60 + '\n', 'INFO')
    
    logger.log('Testing backward compatibility (LLMClient.create_from_env())...', 'INFO')
    try:
        client = LLMClient.create_from_env()
        
        logger.log(f'✅ LLMClient.create_from_env() works', 'INFO')
        
        logger.log(f"Available models: {', '.join(client.get_available_models()[:3])}...", 'INFO')
    except Exception as e:
        error = wrap_exception(e, LLMClientError, 'Backward compatibility test failed', {})
        
        logger.log(f'❌ Backward compatibility test failed: {error}', 'INFO')