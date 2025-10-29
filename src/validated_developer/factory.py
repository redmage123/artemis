"""
Validated Developer Agent Factory

WHY: Creating a validated developer agent requires complex initialization
     of multiple layers. Factory pattern centralizes this complexity.

RESPONSIBILITY:
- Create developer agents with all validation layers enabled
- Configure validation strategies
- Initialize event notifications
- Apply mixin functionality dynamically

PATTERNS:
- Factory Pattern: Centralize complex object creation
- Guard Clauses: Early returns for invalid configurations
- Dependency Injection: Inject dependencies from caller
"""
from typing import Optional, Any
from validated_developer.core_mixin import ValidatedDeveloperMixin


def create_validated_developer_agent(developer_name: str, developer_type:
    str, llm_provider: str='openai', llm_model: Optional[str]=None, logger:
    Optional[Any]=None, rag_agent: Optional[Any]=None, ai_service: Optional
    [Any]=None, enable_validation: bool=True, enable_rag_validation: bool=
    True, enable_self_critique: bool=True):
    """
    Factory function to create a validated developer agent.

    WHY: Creates a developer agent with all 5 validation layers enabled,
         avoiding complex initialization code in caller.

    WHAT: Creates base agent, applies validation mixin, initializes all layers.

    Args:
        developer_name: Name of developer
        developer_type: Type (conservative/aggressive)
        llm_provider: LLM provider (openai/anthropic)
        llm_model: Specific model
        logger: Logger instance
        rag_agent: RAG agent
        ai_service: AI Query Service
        enable_validation: Enable validation pipeline (Layer 3, default True)
        enable_rag_validation: Enable RAG-enhanced validation (Layer 3.5, default True)
        enable_self_critique: Enable self-critique validation (Layer 5, default True)

    Returns:
        StandaloneDeveloperAgent with validation enabled
    """
    from standalone_developer_agent import StandaloneDeveloperAgent
    agent = StandaloneDeveloperAgent(developer_name=developer_name,
        developer_type=developer_type, llm_provider=llm_provider, llm_model
        =llm_model, logger=logger, rag_agent=rag_agent, ai_service=ai_service)
    _apply_validation_mixin(agent)
    agent.__init_validation_pipeline__(strict_mode=True,
        enable_rag_validation=enable_rag_validation, enable_self_critique=
        enable_self_critique)
    agent.enable_validation(enable_validation)
    if logger:
        logger.log(f'Created validated developer: {developer_name}', 'INFO')
    return agent


def _apply_validation_mixin(agent: Any) ->None:
    """
    Apply ValidatedDeveloperMixin to agent instance dynamically.

    WHY: Allows adding validation to existing agent instances without
         modifying their class definition.

    Args:
        agent: Agent instance to add validation to
    """
    for attr_name in dir(ValidatedDeveloperMixin):
        is_magic_method = attr_name.startswith('__') and attr_name.endswith(
            '__')
        is_init_method = attr_name.startswith('__init')
        should_include = not is_magic_method or is_init_method
        if should_include:
            attr = getattr(ValidatedDeveloperMixin, attr_name)
            if callable(attr):
                if hasattr(attr, '__get__'):
                    setattr(agent, attr_name, attr.__get__(agent, type(agent)))
                else:
                    import types
                    setattr(agent, attr_name, types.MethodType(attr, agent))
