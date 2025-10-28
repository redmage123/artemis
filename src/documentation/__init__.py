#!/usr/bin/env python3
"""
WHY: Architecture Decision Record (ADR) generation package
RESPONSIBILITY: Provide modular ADR generation with AI and template strategies
PATTERNS: Package initialization with controlled exports

This package provides comprehensive ADR generation capabilities:
- Data models for ADR records and context
- Template-based ADR generation
- Context analysis from RAG and SSD
- Decision recording with prompt building
- Core orchestration with AI Query Service integration

Usage:
    from documentation import ADRGenerator, create_adr_generator

    generator = create_adr_generator(rag, logger, ai_service=ai_service)
    adr_content = generator.generate_adr(card, "001", structured_requirements)
"""

from documentation.models import (
    ADRStatus,
    ADRPriority,
    ADRComplexity,
    ADRMetadata,
    ADRContext,
    SSDContext,
    ADRRecord,
    create_adr_context_from_card,
    create_adr_metadata
)

from documentation.template_engine import ADRTemplateEngine

from documentation.context_analyzer import (
    ContextAnalyzer,
    create_context_analyzer
)

from documentation.decision_recorder import (
    DecisionRecorder,
    PromptBuilder,
    create_decision_recorder,
    create_prompt_builder
)

from documentation.adr_generator_core import (
    ADRGeneratorCore,
    ADRGenerationService,
    create_adr_generator,
    create_adr_service
)


# Backward compatibility: Main class alias
ADRGenerator = ADRGeneratorCore


# Public API exports
__all__ = [
    # Main classes
    "ADRGenerator",
    "ADRGeneratorCore",
    "ADRGenerationService",
    "ADRTemplateEngine",
    "ContextAnalyzer",
    "DecisionRecorder",
    "PromptBuilder",

    # Data models
    "ADRStatus",
    "ADRPriority",
    "ADRComplexity",
    "ADRMetadata",
    "ADRContext",
    "SSDContext",
    "ADRRecord",

    # Factory functions
    "create_adr_generator",
    "create_adr_service",
    "create_context_analyzer",
    "create_decision_recorder",
    "create_prompt_builder",
    "create_adr_context_from_card",
    "create_adr_metadata",
]


# Package metadata
__version__ = "2.0.0"
__author__ = "Artemis Development Team"
__description__ = "Modular ADR generation with AI and template strategies"
