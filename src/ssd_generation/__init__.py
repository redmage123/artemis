#!/usr/bin/env python3
"""
SSD Generation Package

WHY: Modularized SSD generation pipeline.
RESPONSIBILITY: Export all public interfaces.
PATTERNS:
- Package organization by responsibility
- Clean public API
"""

# Main stage
from ssd_generation.ssd_generation_stage import SSDGenerationStage

# Models
from ssd_generation.models import (
    RequirementItem,
    DiagramSpec,
    SSDDocument,
)

# Services
from ssd_generation.services import (
    SSDDecisionService,
    RequirementsAnalyzer,
    DiagramGenerator,
    RAGStorageService,
)

# Generators
from ssd_generation.generators import (
    MarkdownGenerator,
    HTMLGenerator,
    PDFGenerator,
    OutputFileGenerator,
)

# Prompts
from ssd_generation.prompts import (
    RequirementsPrompts,
    DiagramPrompts,
)

__all__ = [
    # Main stage
    'SSDGenerationStage',

    # Models
    'RequirementItem',
    'DiagramSpec',
    'SSDDocument',

    # Services
    'SSDDecisionService',
    'RequirementsAnalyzer',
    'DiagramGenerator',
    'RAGStorageService',

    # Generators
    'MarkdownGenerator',
    'HTMLGenerator',
    'PDFGenerator',
    'OutputFileGenerator',

    # Prompts
    'RequirementsPrompts',
    'DiagramPrompts',
]
