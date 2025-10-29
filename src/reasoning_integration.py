"""
WHY: Backward compatibility wrapper for reasoning_integration module.

RESPONSIBILITY: Maintain existing API while delegating to modular reasoning/ package.

PATTERNS:
- Facade Pattern: Simple interface over complex subsystem
- Adapter Pattern: Bridge old and new implementations
- Deprecation Warning: Guide users to new API

MIGRATION GUIDE:
    Old:
        from reasoning_integration import ReasoningEnhancedLLMClient, ReasoningConfig
        from reasoning_strategies import ReasoningStrategy

        config = ReasoningConfig(strategy=ReasoningStrategy.CHAIN_OF_THOUGHT)
        client = ReasoningEnhancedLLMClient(base_client)

    New:
        from reasoning import ReasoningEnhancedLLMClient, ReasoningConfig, ReasoningType

        config = ReasoningConfig(strategy=ReasoningType.CHAIN_OF_THOUGHT)
        client = ReasoningEnhancedLLMClient(base_client)

REFACTORED: This module has been refactored into the reasoning/ package.
    - reasoning/models.py - Data models and configuration
    - reasoning/strategy_selector.py - Strategy selection logic
    - reasoning/prompt_enhancer.py - Prompt enhancement
    - reasoning/executors.py - Execution strategies
    - reasoning/llm_client_wrapper.py - LLM client wrapper
    - reasoning/__init__.py - Package exports

Original file: reasoning_integration_original.py (647 lines)
New structure: 6 focused modules (~150-250 lines each)
"""
import warnings
from typing import Dict, List, Optional, Any
from reasoning import ReasoningConfig, ReasoningType, ReasoningResult, ReasoningEnhancedLLMClient, PromptEnhancer as ReasoningPromptEnhancer, create_reasoning_client as create_reasoning_enhanced_client, get_default_config_for_task as get_default_reasoning_config
from reasoning_strategies import ReasoningStrategy
warnings.warn("reasoning_integration module is deprecated. Use 'from reasoning import ReasoningEnhancedLLMClient, ReasoningConfig, ReasoningType' instead. See module docstring for migration guide.", DeprecationWarning, stacklevel=2)
__all__ = ['ReasoningConfig', 'ReasoningEnhancedLLMClient', 'ReasoningPromptEnhancer', 'ReasoningType', 'ReasoningResult', 'ReasoningStrategy', 'create_reasoning_enhanced_client', 'get_default_reasoning_config']
if __name__ == '__main__':
    import argparse
    import sys
    import logging
    from llm_client import LLMMessage
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser(description='Reasoning Integration Demo')
    parser.add_argument('--provider', default='openai', choices=['openai', 'anthropic'], help='LLM provider')
    parser.add_argument('--strategy', required=True, choices=['cot', 'tot', 'lot', 'sc'], help='Reasoning strategy')
    parser.add_argument('--task', required=True, help='Task to solve')
    parser.add_argument('--context', help='Additional context')
    args = parser.parse_args()
    strategy_map = {'cot': ReasoningType.CHAIN_OF_THOUGHT, 'tot': ReasoningType.TREE_OF_THOUGHTS, 'lot': ReasoningType.LOGIC_OF_THOUGHTS, 'sc': ReasoningType.SELF_CONSISTENCY}
    try:
        client = create_reasoning_enhanced_client(args.provider)
        messages = [LLMMessage(role='system', content='You are a helpful assistant.'), LLMMessage(role='user', content=args.task)]
        if args.context:
            messages.insert(1, LLMMessage(role='system', content=args.context))
        config = ReasoningConfig(strategy=strategy_map[args.strategy], enabled=True, sc_num_samples=3 if args.strategy == 'sc' else 5)
        
        logger.log('=' * 80, 'INFO')
        
        logger.log(f'REASONING STRATEGY: {args.strategy.upper()}', 'INFO')
        
        logger.log('=' * 80, 'INFO')
        
        logger.log(f'\nTask: {args.task}', 'INFO')
        if args.context:
            
            logger.log(f'Context: {args.context}', 'INFO')
        
        logger.log('\nExecuting with reasoning enhancement...', 'INFO')
        
        logger.log('-' * 80, 'INFO')
        result = client.complete_with_reasoning(messages=messages, reasoning_config=config)
        
        logger.log('\nRESPONSE:', 'INFO')
        
        logger.log('-' * 80, 'INFO')
        
        logger.log(result['response'].content, 'INFO')
        
        logger.log('-' * 80, 'INFO')
        
        logger.log('\nREASONING METADATA:', 'INFO')
        
        logger.log(f"Strategy Applied: {result['reasoning_strategy']}", 'INFO')
        
        logger.log(f"Total Tokens: {result['response'].usage['total_tokens']}", 'INFO')
        if 'reasoning_output' in result:
            
            logger.log('\nREASONING OUTPUT:', 'INFO')
            import json
            
            logger.log(json.dumps(result['reasoning_output'], indent=2), 'INFO')
        if 'consistent_answer' in result:
            
            logger.log('\nCONSISTENT ANSWER:', 'INFO')
            import json
            
            logger.log(json.dumps(result['consistent_answer'], indent=2), 'INFO')
        
        logger.log('=' * 80, 'INFO')
    except Exception as e:
        logging.error(f'Error: {e}')
        sys.exit(1)