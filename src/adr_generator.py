#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY WRAPPER for ADRGenerator

WHY: Maintain backward compatibility while using refactored modular package
RESPONSIBILITY: Delegate to documentation.adr_generator_core.ADRGeneratorCore
PATTERNS: Adapter Pattern, delegation

MIGRATION PATH:
    Old: from adr_generator import ADRGenerator
    New: from documentation import ADRGenerator, create_adr_generator

This module will be deprecated in a future release.
Please migrate to the documentation package.
"""

import warnings
from typing import Dict, Optional

from artemis_stage_interface import LoggerInterface
from documentation import (
    ADRGeneratorCore,
    create_adr_generator
)


# Issue deprecation warning when module is imported
warnings.warn(
    "adr_generator.py is deprecated. Please use 'from documentation import ADRGenerator' instead.",
    DeprecationWarning,
    stacklevel=2
)


class ADRGenerator:
    """
    DEPRECATED: Backward compatibility wrapper for ADRGeneratorCore

    This class delegates all calls to documentation.adr_generator_core.ADRGeneratorCore
    Please migrate to using the documentation package directly.

    Migration examples:
        # Old approach
        from adr_generator import ADRGenerator
        generator = ADRGenerator(rag, logger, ai_service=ai_service)

        # New approach (recommended)
        from documentation import create_adr_generator
        generator = create_adr_generator(rag, logger, ai_service=ai_service)
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
        Initialize ADR generator (delegates to ADRGeneratorCore)

        Args:
            rag: RAG agent for querying context
            logger: Logger interface
            llm_client: LLM client (optional, legacy)
            ai_service: AI Query Service for KG→RAG→LLM pipeline (optional)
            prompt_manager: Prompt manager for RAG-based prompts (optional, legacy)
        """
        # Delegate to refactored core implementation
        self._core = ADRGeneratorCore(
            rag,
            logger,
            llm_client,
            ai_service,
            prompt_manager
        )

        # Store attributes for backward compatibility
        self.rag = rag
        self.logger = logger
        self.llm_client = llm_client
        self.ai_service = ai_service
        self.prompt_manager = prompt_manager

    def generate_adr(
        self,
        card: Dict,
        adr_number: str,
        structured_requirements=None
    ) -> str:
        """
        Generate ADR content (delegates to ADRGeneratorCore)

        Args:
            card: Kanban card with task details
            adr_number: ADR number (e.g., "001")
            structured_requirements: Structured requirements (optional)

        Returns:
            Generated ADR content as markdown string

        Raises:
            ADRGenerationError: If ADR generation fails
        """
        return self._core.generate_adr(card, adr_number, structured_requirements)

    # Private methods delegated for backward compatibility
    def _generate_adr_with_ai_service(self, card, adr_number, structured_requirements, title):
        """Delegate to core implementation"""
        return self._core._generate_with_ai_service(card, adr_number, structured_requirements)

    def _log_token_savings_if_applicable(self, result):
        """Delegate to core implementation"""
        return self._core._log_token_savings(result)

    def _build_adr_prompt(self, card, adr_number, structured_requirements=None):
        """Delegate to prompt builder"""
        return self._core.prompt_builder.build(card, adr_number, None, structured_requirements)

    def _query_ssd_from_rag(self, card_id):
        """Delegate to context analyzer"""
        return self._core.context_analyzer.query_ssd_context(card_id)

    def _extract_list_from_ssd(self, content, section_name):
        """Delegate to context analyzer"""
        return self._core.context_analyzer._extract_list_from_content(content, section_name)

    def _generate_adr_template(self, card, adr_number, structured_requirements=None):
        """Delegate to template engine"""
        return self._core._generate_with_template(card, adr_number, structured_requirements)

    def _build_structured_requirements_section(self, structured_requirements):
        """Delegate to template engine"""
        return self._core.template_engine._build_structured_requirements_subsection(
            structured_requirements
        )

    def _build_nfr_section_if_available(self, structured_requirements):
        """Delegate to template engine"""
        return self._core.template_engine._build_key_nfr_section(structured_requirements)


# Expose factory function for convenience
def create_adr_generator_legacy(
    rag,
    logger: LoggerInterface,
    llm_client=None,
    ai_service=None,
    prompt_manager=None
) -> ADRGenerator:
    """
    DEPRECATED: Factory function for ADRGenerator

    Use documentation.create_adr_generator instead
    """
    warnings.warn(
        "create_adr_generator_legacy is deprecated. "
        "Use 'from documentation import create_adr_generator' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return ADRGenerator(rag, logger, llm_client, ai_service, prompt_manager)


# Module-level note for developers
__doc__ += """

REFACTORING NOTES:
==================

This module has been refactored into the documentation/ package with the following structure:

documentation/
├── __init__.py              # Package exports and main API
├── models.py                # ADR data models (ADRStatus, ADRRecord, ADRContext, SSDContext)
├── template_engine.py       # Template-based ADR generation
├── context_analyzer.py      # RAG/SSD context analysis
├── decision_recorder.py     # Prompt building for ADR generation
└── adr_generator_core.py    # Main orchestration logic

Benefits of refactored architecture:
- Single Responsibility: Each module has one clear purpose
- Testability: Smaller modules are easier to unit test
- Maintainability: ~150-250 lines per module vs 611 lines monolith
- Extensibility: Easy to add new template types or context sources
- Type Safety: Strong typing with dataclasses and enums

Original: 611 lines (monolithic)
Refactored: 5 focused modules + 1 wrapper (this file)
Reduction: ~70% per module
"""
