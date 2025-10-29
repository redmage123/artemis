from artemis_logger import get_logger
logger = get_logger('__init__')
'\nWHY: Export public API for prompt_management package.\nRESPONSIBILITY: Define package interface and backward compatibility.\nPATTERNS: Facade pattern, explicit exports.\n\nPrompt Management System for Artemis\n====================================\n\nThis package provides a modular system for managing prompt templates\nwith DEPTH framework support and advanced reasoning strategies.\n\nModules:\n- models: Core data structures (PromptTemplate, PromptContext, etc.)\n- template_loader: Load templates from RAG storage\n- variable_substitutor: Template variable substitution\n- formatter: Format prompts with DEPTH framework\n- prompt_builder: Builder pattern for prompt construction\n- prompt_repository: Repository pattern for template persistence\n\nUsage:\n    from prompt_management import (\n        PromptManager,\n        PromptTemplate,\n        PromptContext,\n        ReasoningStrategyType\n    )\n\n    # Create manager\n    manager = PromptManager(rag_agent, verbose=True)\n\n    # Store template\n    manager.store_prompt(\n        name="my_prompt",\n        category="developer_agent",\n        perspectives=["Expert A", "Expert B"],\n        success_metrics=["Metric 1", "Metric 2"],\n        # ... other parameters\n    )\n\n    # Retrieve and render\n    prompt = manager.get_prompt("my_prompt")\n    rendered = manager.render_prompt(prompt, {"var": "value"})\n'
from .models import PromptTemplate, PromptContext, RenderedPrompt, ReasoningStrategyType
from .template_loader import TemplateLoader
from .variable_substitutor import VariableSubstitutor
from .formatter import PromptFormatter
from .prompt_builder import PromptBuilder, PromptBuilderFactory
from .prompt_repository import PromptRepository
from typing import Dict, List, Optional, Any

class PromptManager:
    """
    WHY: Provide unified facade for prompt management operations.
    RESPONSIBILITY: Coordinate all prompt management components.
    PATTERNS: Facade pattern, dependency injection.

    This is the main entry point for the prompt management system,
    providing a simplified API that coordinates the various modules.
    """
    PROMPT_CATEGORIES = PromptRepository.PROMPT_CATEGORIES

    def __init__(self, rag_agent, verbose: bool=True):
        """
        WHY: Initialize prompt manager with dependencies.
        RESPONSIBILITY: Set up all internal components.
        PATTERNS: Dependency injection, facade initialization.

        Args:
            rag_agent: RAG agent for storage
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self._repository = PromptRepository(rag_agent, verbose=verbose)
        self._loader = TemplateLoader(rag_agent, verbose=verbose)
        self._builder_factory = PromptBuilderFactory(verbose=verbose)
        self._substitutor = VariableSubstitutor(strict=False, verbose=verbose)
        self._formatter = PromptFormatter(verbose=verbose)
        if verbose:
            
            logger.log('[PromptManager] Initialized with modular architecture', 'INFO')

    def store_prompt(self, name: str, category: str, perspectives: List[str], success_metrics: List[str], context_layers: Dict[str, Any], task_breakdown: List[str], self_critique: str, system_message: str, user_template: str, tags: Optional[List[str]]=None, version: str='1.0', reasoning_strategy: ReasoningStrategyType=ReasoningStrategyType.NONE, reasoning_config: Optional[Dict[str, Any]]=None) -> str:
        """
        WHY: Store a prompt template.
        RESPONSIBILITY: Delegate to repository.
        PATTERNS: Facade method, delegation.

        Args:
            name: Prompt name
            category: Prompt category
            perspectives: Expert perspectives
            success_metrics: Success criteria
            context_layers: Context information
            task_breakdown: Task steps
            self_critique: Self-validation instructions
            system_message: System role message
            user_template: User prompt template
            tags: Optional tags
            version: Version string
            reasoning_strategy: Reasoning strategy
            reasoning_config: Strategy configuration

        Returns:
            Prompt ID
        """
        return self._repository.save(name=name, category=category, perspectives=perspectives, success_metrics=success_metrics, context_layers=context_layers, task_breakdown=task_breakdown, self_critique=self_critique, system_message=system_message, user_template=user_template, tags=tags, version=version, reasoning_strategy=reasoning_strategy, reasoning_config=reasoning_config)

    def get_prompt(self, name: str, version: Optional[str]=None, context: Optional[Dict[str, Any]]=None) -> Optional[PromptTemplate]:
        """
        WHY: Retrieve a prompt template.
        RESPONSIBILITY: Delegate to loader.
        PATTERNS: Facade method, delegation.

        Args:
            name: Prompt name
            version: Specific version or None for latest
            context: Optional context (for backward compatibility)

        Returns:
            PromptTemplate or None
        """
        return self._loader.load_by_name(name, version)

    def query_prompts(self, category: Optional[str]=None, tags: Optional[List[str]]=None, min_performance: float=0.0, top_k: int=5) -> List[PromptTemplate]:
        """
        WHY: Query prompts by various criteria.
        RESPONSIBILITY: Coordinate queries across criteria.
        PATTERNS: Facade method, dispatch to appropriate loader method.

        Args:
            category: Filter by category
            tags: Filter by tags
            min_performance: Minimum performance score
            top_k: Maximum results

        Returns:
            List of PromptTemplates
        """
        if category:
            templates = self._loader.load_by_category(category, top_k)
        elif tags:
            templates = self._loader.load_by_tags(tags, top_k)
        else:
            templates = self._repository.find_by_performance(min_performance, top_k)
        if min_performance > 0.0:
            templates = [t for t in templates if t.performance_score >= min_performance]
        return templates[:top_k]

    def render_prompt(self, prompt: PromptTemplate, variables: Dict[str, Any]) -> Dict[str, str]:
        """
        WHY: Render a template with variables.
        RESPONSIBILITY: Coordinate builder and return legacy format.
        PATTERNS: Facade method, adapter pattern for backward compatibility.

        Args:
            prompt: PromptTemplate to render
            variables: Variables for substitution

        Returns:
            Dict with 'system' and 'user' keys (legacy format)
        """
        builder = self._builder_factory.create_builder(prompt)
        builder.with_variables(variables)
        rendered = builder.build()
        return {'system': rendered.system, 'user': rendered.user}

    def update_performance(self, prompt_id: str, success: bool):
        """
        WHY: Update prompt performance metrics.
        RESPONSIBILITY: Delegate to repository.
        PATTERNS: Facade method, delegation.

        Args:
            prompt_id: Prompt ID
            success: Whether usage was successful
        """
        self._repository.update_performance(prompt_id, success)
__all__ = ['PromptManager', 'PromptTemplate', 'PromptContext', 'RenderedPrompt', 'ReasoningStrategyType', 'TemplateLoader', 'VariableSubstitutor', 'PromptFormatter', 'PromptBuilder', 'PromptBuilderFactory', 'PromptRepository']