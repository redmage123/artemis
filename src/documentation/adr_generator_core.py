#!/usr/bin/env python3
"""
WHY: Orchestrate ADR generation using AI Query Service or template fallback
RESPONSIBILITY: Main orchestration logic for ADR content generation
PATTERNS: Template Method Pattern, Strategy Pattern, guard clauses, dispatch tables
"""

from typing import Dict, Optional, Any, Callable

from artemis_stage_interface import LoggerInterface
from artemis_exceptions import ADRGenerationError, create_wrapped_exception
from documentation.models import (
    create_adr_context_from_card,
    create_adr_metadata,
    ADRStatus
)
from documentation.template_engine import ADRTemplateEngine
from documentation.context_analyzer import ContextAnalyzer
from documentation.decision_recorder import PromptBuilder


class ADRGeneratorCore:
    """
    WHY: Core orchestration for ADR generation
    RESPONSIBILITY: Coordinate AI Query Service and template-based generation
    PATTERNS: Strategy Pattern (AI vs template), Template Method Pattern
    """

    def __init__(
        self,
        rag,
        logger: LoggerInterface,
        llm_client=None,
        ai_service=None,
        prompt_manager=None
    ):
        """
        Initialize ADR generator core

        Args:
            rag: RAG agent for querying context
            logger: Logger interface
            llm_client: LLM client (optional, legacy)
            ai_service: AI Query Service for KG→RAG→LLM pipeline (optional)
            prompt_manager: Prompt manager for RAG-based prompts (optional, legacy)
        """
        self.rag = rag
        self.logger = logger
        self.llm_client = llm_client
        self.ai_service = ai_service
        self.prompt_manager = prompt_manager

        # Initialize components
        self.template_engine = ADRTemplateEngine()
        self.context_analyzer = ContextAnalyzer(rag, logger)
        self.prompt_builder = PromptBuilder()

        # Dispatch table for generation strategies
        self._generation_strategies: Dict[str, Callable] = {
            "ai_service": self._generate_with_ai_service,
            "template": self._generate_with_template
        }

    def generate_adr(
        self,
        card: Dict,
        adr_number: str,
        structured_requirements=None
    ) -> str:
        """
        Generate ADR content using AI Query Service or template fallback

        Args:
            card: Kanban card with task details
            adr_number: ADR number (e.g., "001")
            structured_requirements: Structured requirements (optional)

        Returns:
            Generated ADR content as markdown string

        Raises:
            ADRGenerationError: If ADR generation fails
        """
        try:
            # Select generation strategy
            strategy = self._select_generation_strategy()

            # Execute strategy
            return self._generation_strategies[strategy](
                card,
                adr_number,
                structured_requirements
            )

        except ADRGenerationError:
            # Re-raise already wrapped exceptions
            raise
        except Exception as e:
            raise create_wrapped_exception(
                e,
                ADRGenerationError,
                f"Failed to generate ADR: {str(e)}",
                context={"card_id": card.get('card_id'), "adr_number": adr_number}
            )

    def _select_generation_strategy(self) -> str:
        """
        Select ADR generation strategy based on available services

        Returns:
            Strategy name: "ai_service" or "template"
        """
        # Guard clause: Check if AI service available
        if not self.ai_service:
            self.logger.log(
                "⚠️  AI Query Service unavailable - using template-based generation",
                "WARNING"
            )
            return "template"

        return "ai_service"

    def _generate_with_ai_service(
        self,
        card: Dict,
        adr_number: str,
        structured_requirements: Optional[Any]
    ) -> str:
        """
        Generate ADR using AI Query Service (KG→RAG→LLM pipeline)

        Args:
            card: Kanban card with task details
            adr_number: ADR number
            structured_requirements: Structured requirements (optional)

        Returns:
            Generated ADR content as markdown string

        Raises:
            ADRGenerationError: If AI generation fails
        """
        # Create ADR context from card
        context = create_adr_context_from_card(card)

        # Query SSD context from RAG
        ssd_context = self.context_analyzer.query_ssd_context(context.card_id)

        # Build comprehensive prompt
        prompt = self.prompt_builder.build(
            card,
            adr_number,
            ssd_context,
            structured_requirements
        )

        # Extract keywords for KG query
        keywords = context.title.split()[:3]

        # Use AI Query Service
        self.logger.log("🔄 Using AI Query Service for KG→RAG→LLM pipeline", "INFO")

        # Import QueryType here to avoid circular import
        from ai_query_service import QueryType

        result = self.ai_service.query(
            query_type=QueryType.ARCHITECTURE_DESIGN,
            prompt=prompt,
            kg_query_params={
                'keywords': keywords,
                'req_type': 'functional'
            },
            temperature=0.3,
            max_tokens=3000
        )

        # Guard clause: Check result success
        if not result.success:
            raise ADRGenerationError(
                f"AI Query Service failed: {result.error}",
                context={"card_id": context.card_id, "title": context.title}
            )

        # Log token savings if available
        self._log_token_savings(result)

        # Return LLM-generated ADR content
        return result.llm_response.content

    def _generate_with_template(
        self,
        card: Dict,
        adr_number: str,
        structured_requirements: Optional[Any]
    ) -> str:
        """
        Generate ADR using template fallback

        Args:
            card: Kanban card with task details
            adr_number: ADR number
            structured_requirements: Structured requirements (optional)

        Returns:
            Generated ADR content as markdown string
        """
        # Create ADR context and metadata
        context = create_adr_context_from_card(card)
        metadata = create_adr_metadata(adr_number, ADRStatus.ACCEPTED)

        # Generate using template engine
        return self.template_engine.generate_adr_from_template(
            context,
            metadata,
            structured_requirements
        )

    def _log_token_savings(self, result) -> None:
        """
        Log token savings if KG context available

        Args:
            result: AI Query Service result
        """
        # Guard clause: Check if KG context exists
        if not result.kg_context:
            return

        # Guard clause: Check if patterns found
        if result.kg_context.pattern_count <= 0:
            return

        self.logger.log(
            f"📊 KG found {result.kg_context.pattern_count} ADR patterns, "
            f"saved ~{result.llm_response.tokens_saved} tokens",
            "INFO"
        )


class ADRGenerationService:
    """
    WHY: High-level service interface for ADR generation
    RESPONSIBILITY: Provide simplified API for ADR generation
    """

    def __init__(
        self,
        rag,
        logger: LoggerInterface,
        llm_client=None,
        ai_service=None,
        prompt_manager=None
    ):
        """
        Initialize ADR generation service

        Args:
            rag: RAG agent for querying context
            logger: Logger interface
            llm_client: LLM client (optional, legacy)
            ai_service: AI Query Service for KG→RAG→LLM pipeline (optional)
            prompt_manager: Prompt manager for RAG-based prompts (optional, legacy)
        """
        self.core = ADRGeneratorCore(
            rag,
            logger,
            llm_client,
            ai_service,
            prompt_manager
        )

    def generate(
        self,
        card: Dict,
        adr_number: str,
        structured_requirements=None
    ) -> str:
        """
        Generate ADR content

        Args:
            card: Kanban card with task details
            adr_number: ADR number (e.g., "001")
            structured_requirements: Structured requirements (optional)

        Returns:
            Generated ADR content as markdown string

        Raises:
            ADRGenerationError: If ADR generation fails
        """
        return self.core.generate_adr(card, adr_number, structured_requirements)


def create_adr_generator(
    rag,
    logger: LoggerInterface,
    llm_client=None,
    ai_service=None,
    prompt_manager=None
) -> ADRGeneratorCore:
    """
    Factory function to create ADR generator core

    Args:
        rag: RAG agent for querying context
        logger: Logger interface
        llm_client: LLM client (optional)
        ai_service: AI Query Service (optional)
        prompt_manager: Prompt manager (optional)

    Returns:
        ADRGeneratorCore instance
    """
    return ADRGeneratorCore(
        rag,
        logger,
        llm_client,
        ai_service,
        prompt_manager
    )


def create_adr_service(
    rag,
    logger: LoggerInterface,
    llm_client=None,
    ai_service=None,
    prompt_manager=None
) -> ADRGenerationService:
    """
    Factory function to create ADR generation service

    Args:
        rag: RAG agent for querying context
        logger: Logger interface
        llm_client: LLM client (optional)
        ai_service: AI Query Service (optional)
        prompt_manager: Prompt manager (optional)

    Returns:
        ADRGenerationService instance
    """
    return ADRGenerationService(
        rag,
        logger,
        llm_client,
        ai_service,
        prompt_manager
    )
