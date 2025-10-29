"""
Reasoning Strategy Integration for Artemis

Integrates Chain of Thought (CoT), Tree of Thoughts (ToT), and Logic of Thoughts (LoT)
into the Artemis prompt system and LLM client.

Design Patterns:
- Strategy Pattern: Different reasoning strategies
- Decorator Pattern: Enhance LLM calls with reasoning
- Factory Pattern: Strategy selection
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import json
import logging
from artemis_exceptions import wrap_exception, LLMClientError
from reasoning_strategies import ReasoningStrategy, ReasoningStrategyBase, ReasoningStrategyFactory, ChainOfThoughtStrategy, TreeOfThoughtsStrategy, LogicOfThoughtsStrategy, SelfConsistencyStrategy
from llm_client import LLMClientInterface, LLMMessage, LLMResponse

@dataclass
class ReasoningConfig:
    """Configuration for reasoning strategy"""
    strategy: ReasoningStrategy
    enabled: bool = True
    cot_examples: Optional[List[Dict[str, str]]] = None
    tot_branching_factor: int = 3
    tot_max_depth: int = 4
    lot_axioms: Optional[List[str]] = None
    sc_num_samples: int = 5
    temperature: float = 0.7
    max_tokens: int = 4000

class ReasoningEnhancedLLMClient:
    """
    Wrapper around LLMClientInterface that adds reasoning capabilities.

    Uses Decorator pattern to enhance any LLM client with reasoning strategies.

    Example:
        base_client = create_llm_client("openai")
        reasoning_client = ReasoningEnhancedLLMClient(base_client)

        response = reasoning_client.complete_with_reasoning(
            messages=[...],
            reasoning_config=ReasoningConfig(strategy=ReasoningStrategy.CHAIN_OF_THOUGHT)
        )
    """

    def __init__(self, base_client: LLMClientInterface, logger: Optional[logging.Logger]=None):
        """
        Initialize reasoning-enhanced LLM client.

        Args:
            base_client: Base LLM client to enhance
            logger: Logger instance
        """
        self.base_client = base_client
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    @wrap_exception(LLMClientError, 'Failed to complete with reasoning')
    def complete_with_reasoning(self, messages: List[LLMMessage], reasoning_config: ReasoningConfig, model: Optional[str]=None, temperature: Optional[float]=None, max_tokens: Optional[int]=None) -> Dict[str, Any]:
        """
        Complete LLM request with reasoning strategy applied.

        Args:
            messages: Conversation messages
            reasoning_config: Reasoning configuration
            model: Model to use
            temperature: Temperature override
            max_tokens: Max tokens override

        Returns:
            Dict with response and reasoning metadata

        Raises:
            LLMClientError: If completion fails
        """
        if not reasoning_config.enabled:
            response = self.base_client.complete(messages=messages, model=model, temperature=temperature or 0.7, max_tokens=max_tokens or 4000)
            return {'response': response, 'reasoning_applied': False, 'reasoning_strategy': None}
        strategy = self._create_strategy(reasoning_config)
        task = self._extract_task_from_messages(messages)
        context = self._extract_context_from_messages(messages)
        reasoning_prompt = self._generate_reasoning_prompt(strategy, task, context, reasoning_config)
        enhanced_messages = self._build_enhanced_messages(messages, reasoning_prompt)
        if reasoning_config.strategy == ReasoningStrategy.SELF_CONSISTENCY:
            return self._execute_self_consistency(enhanced_messages, strategy, reasoning_config, model, temperature, max_tokens)
        elif reasoning_config.strategy == ReasoningStrategy.TREE_OF_THOUGHTS:
            return self._execute_tree_of_thoughts(enhanced_messages, strategy, reasoning_config, model, temperature, max_tokens)
        else:
            return self._execute_single_reasoning(enhanced_messages, strategy, reasoning_config, model, temperature, max_tokens)

    def _create_strategy(self, config: ReasoningConfig) -> ReasoningStrategyBase:
        """Create reasoning strategy from config"""
        kwargs = {'logger': self.logger}
        if config.strategy == ReasoningStrategy.TREE_OF_THOUGHTS:
            kwargs['branching_factor'] = config.tot_branching_factor
            kwargs['max_depth'] = config.tot_max_depth
        elif config.strategy == ReasoningStrategy.SELF_CONSISTENCY:
            kwargs['num_samples'] = config.sc_num_samples
        return ReasoningStrategyFactory.create(config.strategy, **kwargs)

    def _extract_task_from_messages(self, messages: List[LLMMessage]) -> str:
        """Extract main task from messages"""
        for msg in reversed(messages):
            if msg.role == 'user':
                return msg.content
        return ''

    def _extract_context_from_messages(self, messages: List[LLMMessage]) -> Optional[str]:
        """Extract context from system messages"""
        for msg in messages:
            if msg.role == 'system':
                return msg.content
        return None

    def _generate_reasoning_prompt(self, strategy: ReasoningStrategyBase, task: str, context: Optional[str], config: ReasoningConfig) -> str:
        """Generate reasoning-enhanced prompt"""
        if config.strategy == ReasoningStrategy.CHAIN_OF_THOUGHT:
            return strategy.generate_prompt(task=task, context=context, examples=config.cot_examples)
        if config.strategy == ReasoningStrategy.TREE_OF_THOUGHTS:
            return strategy.generate_prompt(task=task, context=context, depth=0)
        if config.strategy == ReasoningStrategy.LOGIC_OF_THOUGHTS:
            return strategy.generate_prompt(task=task, context=context, axioms=config.lot_axioms)
        return strategy.generate_prompt(task=task, context=context)

    def _build_enhanced_messages(self, original_messages: List[LLMMessage], reasoning_prompt: str) -> List[LLMMessage]:
        """Build enhanced messages with reasoning prompt"""
        enhanced = []
        for msg in original_messages:
            if msg.role == 'system':
                enhanced.append(msg)
        enhanced.append(LLMMessage(role='user', content=reasoning_prompt))
        return enhanced

    def _execute_single_reasoning(self, messages: List[LLMMessage], strategy: ReasoningStrategyBase, config: ReasoningConfig, model: Optional[str], temperature: Optional[float], max_tokens: Optional[int]) -> Dict[str, Any]:
        """Execute single-shot reasoning (CoT, LoT)"""
        response = self.base_client.complete(messages=messages, model=model, temperature=temperature or config.temperature, max_tokens=max_tokens or config.max_tokens)
        reasoning_output = strategy.parse_response(response.content)
        self.logger.info(f"Applied {config.strategy.value} reasoning (tokens: {response.usage['total_tokens']})")
        return {'response': response, 'reasoning_applied': True, 'reasoning_strategy': config.strategy.value, 'reasoning_output': reasoning_output}

    def _execute_tree_of_thoughts(self, messages: List[LLMMessage], strategy: TreeOfThoughtsStrategy, config: ReasoningConfig, model: Optional[str], temperature: Optional[float], max_tokens: Optional[int]) -> Dict[str, Any]:
        """Execute Tree of Thoughts exploration"""
        response = self.base_client.complete(messages=messages, model=model, temperature=temperature or config.temperature, max_tokens=max_tokens or config.max_tokens)
        reasoning_output = strategy.parse_response(response.content)
        best_path = strategy.select_best_path() if strategy.root else []
        self.logger.info(f"Applied Tree of Thoughts reasoning with {reasoning_output.get('branches', 0)} branches explored")
        return {'response': response, 'reasoning_applied': True, 'reasoning_strategy': 'tree_of_thoughts', 'reasoning_output': reasoning_output, 'best_path': [node.thought for node in best_path]}

    def _execute_self_consistency(self, messages: List[LLMMessage], strategy: SelfConsistencyStrategy, config: ReasoningConfig, model: Optional[str], temperature: Optional[float], max_tokens: Optional[int]) -> Dict[str, Any]:
        """Execute Self-Consistency with multiple samples"""
        samples = []
        total_tokens = 0
        for i in range(config.sc_num_samples):
            response = self.base_client.complete(messages=messages, model=model, temperature=temperature or config.temperature, max_tokens=max_tokens or config.max_tokens)
            samples.append(response.content)
            total_tokens += response.usage['total_tokens']
            strategy.parse_response(response.content)
        consistent_answer = strategy.get_consistent_answer()
        self.logger.info(f'Applied Self-Consistency reasoning with {config.sc_num_samples} samples (total tokens: {total_tokens})')
        return {'response': response, 'reasoning_applied': True, 'reasoning_strategy': 'self_consistency', 'samples': samples, 'consistent_answer': consistent_answer, 'total_tokens': total_tokens}

class ReasoningPromptEnhancer:
    """
    Enhances PromptManager prompts with reasoning strategies.

    Integrates with PromptManager to add reasoning instructions to prompts.
    """

    def __init__(self, logger: Optional[logging.Logger]=None):
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    @wrap_exception(LLMClientError, 'Failed to enhance prompt with reasoning')
    def enhance_prompt_with_reasoning(self, base_prompt: Dict[str, str], reasoning_config: ReasoningConfig) -> Dict[str, str]:
        """
        Enhance a prompt with reasoning strategy instructions.

        Args:
            base_prompt: Dict with 'system' and 'user' messages
            reasoning_config: Reasoning configuration

        Returns:
            Enhanced prompt dict

        Example:
            enhancer = ReasoningPromptEnhancer()
            enhanced = enhancer.enhance_prompt_with_reasoning(
                base_prompt={"system": "...", "user": "..."},
                reasoning_config=ReasoningConfig(strategy=ReasoningStrategy.CHAIN_OF_THOUGHT)
            )
        """
        if not reasoning_config.enabled:
            return base_prompt
        enhanced = base_prompt.copy()
        reasoning_instructions = self._get_reasoning_instructions(reasoning_config)
        enhanced['system'] = f"{base_prompt['system']}\n\n{reasoning_instructions}"
        enhanced = self._add_reasoning_template_to_user_message(enhanced, base_prompt, reasoning_config)
        self.logger.info(f'Enhanced prompt with {reasoning_config.strategy.value} reasoning')
        return enhanced

    def _add_reasoning_template_to_user_message(self, enhanced: Dict[str, str], base_prompt: Dict[str, str], reasoning_config: ReasoningConfig) -> Dict[str, str]:
        """Add reasoning template to user message based on strategy"""
        if reasoning_config.strategy == ReasoningStrategy.CHAIN_OF_THOUGHT:
            cot_template = self._get_cot_template()
            enhanced['user'] = f"{base_prompt['user']}\n\n{cot_template}"
            return enhanced
        if reasoning_config.strategy == ReasoningStrategy.LOGIC_OF_THOUGHTS:
            lot_template = self._get_lot_template(reasoning_config.lot_axioms)
            enhanced['user'] = f"{base_prompt['user']}\n\n{lot_template}"
            return enhanced
        return enhanced

    def _get_reasoning_instructions(self, config: ReasoningConfig) -> str:
        """Get reasoning strategy instructions for system message"""
        instructions = {ReasoningStrategy.CHAIN_OF_THOUGHT: '\n**Reasoning Strategy: Chain of Thought**\n\nYou must think through this problem step-by-step, showing all intermediate reasoning.\nBreak down complex problems into logical steps and explain each step clearly.\n', ReasoningStrategy.TREE_OF_THOUGHTS: '\n**Reasoning Strategy: Tree of Thoughts**\n\nExplore multiple approaches in parallel. For each approach:\n1. Describe the core idea\n2. List advantages and challenges\n3. Score from 0-10\n\nPresent alternatives as JSON array with thought, advantages, challenges, and score.\n', ReasoningStrategy.LOGIC_OF_THOUGHTS: '\n**Reasoning Strategy: Logic of Thoughts**\n\nUse formal logical reasoning and deductions. Apply logical rules:\n- Modus Ponens: If P then Q, P is true, therefore Q\n- Modus Tollens: If P then Q, Q is false, therefore P is false\n- Syllogism: If P then Q, Q then R, therefore P then R\n\nShow each deduction explicitly and verify conclusions logically.\n', ReasoningStrategy.SELF_CONSISTENCY: '\n**Reasoning Strategy: Self-Consistency**\n\nSolve this problem and show your complete reasoning.\nYour answer will be compared with multiple samples to ensure consistency.\n'}
        return instructions.get(config.strategy, '')

    def _get_cot_template(self) -> str:
        """Get Chain of Thought template"""
        return '\nPlease think through this step by step:\n1. First, identify what information we have\n2. Then, determine what we need to find\n3. Next, break down the solution into logical steps\n4. Work through each step carefully\n5. Finally, verify the answer makes sense\n'

    def _get_lot_template(self, axioms: Optional[List[str]]) -> str:
        """Get Logic of Thoughts template"""
        template = '\n**Apply Formal Logic:**\n'
        template += '1. Identify all given premises\n'
        template += '2. State any assumptions clearly\n'
        template += '3. Apply logical rules step by step\n'
        template += '4. Show each deduction explicitly\n'
        template += '5. Verify conclusion follows logically\n'
        if not axioms:
            return template
        template += '\n**Known Facts (Axioms):**\n'
        for i, axiom in enumerate(axioms, 1):
            template += f'{i}. {axiom}\n'
        return template

def create_reasoning_enhanced_client(provider: str='openai', api_key: Optional[str]=None) -> ReasoningEnhancedLLMClient:
    """
    Create reasoning-enhanced LLM client.

    Args:
        provider: "openai" or "anthropic"
        api_key: API key (optional)

    Returns:
        ReasoningEnhancedLLMClient

    Example:
        client = create_reasoning_enhanced_client("openai")
        response = client.complete_with_reasoning(
            messages=[...],
            reasoning_config=ReasoningConfig(strategy=ReasoningStrategy.CHAIN_OF_THOUGHT)
        )
    """
    from llm_client import create_llm_client
    base_client = create_llm_client(provider, api_key)
    return ReasoningEnhancedLLMClient(base_client)

def get_default_reasoning_config(task_type: str) -> ReasoningConfig:
    """
    Get default reasoning configuration for task type.

    Args:
        task_type: Type of task (e.g., "coding", "analysis", "planning")

    Returns:
        ReasoningConfig

    Example:
        config = get_default_reasoning_config("coding")
    """
    configs = {'coding': ReasoningConfig(strategy=ReasoningStrategy.CHAIN_OF_THOUGHT, enabled=True), 'architecture': ReasoningConfig(strategy=ReasoningStrategy.TREE_OF_THOUGHTS, enabled=True, tot_branching_factor=3, tot_max_depth=4), 'analysis': ReasoningConfig(strategy=ReasoningStrategy.LOGIC_OF_THOUGHTS, enabled=True), 'testing': ReasoningConfig(strategy=ReasoningStrategy.SELF_CONSISTENCY, enabled=True, sc_num_samples=3)}
    return configs.get(task_type, ReasoningConfig(strategy=ReasoningStrategy.CHAIN_OF_THOUGHT, enabled=True))
if __name__ == '__main__':
    import argparse
    import sys
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    parser = argparse.ArgumentParser(description='Reasoning Integration Demo')
    parser.add_argument('--provider', default='openai', choices=['openai', 'anthropic'], help='LLM provider')
    parser.add_argument('--strategy', required=True, choices=['cot', 'tot', 'lot', 'sc'], help='Reasoning strategy')
    parser.add_argument('--task', required=True, help='Task to solve')
    parser.add_argument('--context', help='Additional context')
    args = parser.parse_args()
    strategy_map = {'cot': ReasoningStrategy.CHAIN_OF_THOUGHT, 'tot': ReasoningStrategy.TREE_OF_THOUGHTS, 'lot': ReasoningStrategy.LOGIC_OF_THOUGHTS, 'sc': ReasoningStrategy.SELF_CONSISTENCY}
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
            
            logger.log(json.dumps(result['reasoning_output'], indent=2), 'INFO')
        if 'consistent_answer' in result:
            
            logger.log('\nCONSISTENT ANSWER:', 'INFO')
            
            logger.log(json.dumps(result['consistent_answer'], indent=2), 'INFO')
        
        logger.log('=' * 80, 'INFO')
    except Exception as e:
        logging.error(f'Error: {e}')
        sys.exit(1)