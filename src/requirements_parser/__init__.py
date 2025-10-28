#!/usr/bin/env python3
"""
Requirements Parser Package

WHY: Modularized requirements parsing with clean separation of concerns
RESPONSIBILITY: Export public API for requirements parsing
PATTERNS: Facade pattern - simple interface to complex subsystem

Package Structure:
- parser_agent.py - Main orchestration (RequirementsParserAgent)
- extraction_engine.py - Multi-step LLM extraction strategies
- conversion_utils.py - LLM output to StructuredRequirements conversion
- prompt_integration.py - PromptManager + RAG single-call extraction
- ai_service_integration.py - KG→RAG→LLM pipeline integration
- kg_integration.py - Knowledge Graph queries for patterns
"""

from requirements_parser.parser_agent import RequirementsParserAgent
from requirements_parser.extraction_engine import ExtractionEngine
from requirements_parser.conversion_utils import RequirementsConverter
from requirements_parser.prompt_integration import PromptManagerIntegration
from requirements_parser.ai_service_integration import AIServiceIntegration
from requirements_parser.kg_integration import KnowledgeGraphIntegration

__all__ = [
    # Main public API
    "RequirementsParserAgent",

    # Internal components (exposed for testing/customization)
    "ExtractionEngine",
    "RequirementsConverter",
    "PromptManagerIntegration",
    "AIServiceIntegration",
    "KnowledgeGraphIntegration",
]

__version__ = "2.0.0"
__author__ = "Artemis Team"
