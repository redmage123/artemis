#!/usr/bin/env python3
"""
Software Specification Document (SSD) Generation Stage - Backward Compatibility Wrapper

WHY: Maintains backward compatibility while using modularized implementation.
RESPONSIBILITY: Re-export all symbols from ssd_generation package.
PATTERNS:
- Facade pattern for backward compatibility
- Clean migration path

REFACTORING NOTE:
This file is now a thin wrapper around the modularized ssd_generation package.
All implementation has been extracted into focused modules:
- Models: ssd_generation/models/
- Services: ssd_generation/services/
- Generators: ssd_generation/generators/
- Prompts: ssd_generation/prompts/

Original file: 1,380 lines
Wrapper file: ~30 lines
Reduction: 97.8%
"""

# Re-export all public symbols for backward compatibility
from ssd_generation import (
    # Main stage
    SSDGenerationStage,

    # Models
    RequirementItem,
    DiagramSpec,
    SSDDocument,

    # Services (if needed by external code)
    SSDDecisionService,
    RequirementsAnalyzer,
    DiagramGenerator,
    RAGStorageService,

    # Generators (if needed by external code)
    MarkdownGenerator,
    HTMLGenerator,
    PDFGenerator,
    OutputFileGenerator,

    # Prompts (if needed by external code)
    RequirementsPrompts,
    DiagramPrompts,
)

__all__ = [
    'SSDGenerationStage',
    'RequirementItem',
    'DiagramSpec',
    'SSDDocument',
    'SSDDecisionService',
    'RequirementsAnalyzer',
    'DiagramGenerator',
    'RAGStorageService',
    'MarkdownGenerator',
    'HTMLGenerator',
    'PDFGenerator',
    'OutputFileGenerator',
    'RequirementsPrompts',
    'DiagramPrompts',
]
