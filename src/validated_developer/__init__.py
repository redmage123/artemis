#!/usr/bin/env python3
"""
Validated Developer Package

WHY: Adds Layer 3 (Validation Pipeline), Layer 3.5 (RAG Validation),
     and Layer 5 (Self-Critique) to developer agents to catch hallucinations
     before they propagate through the codebase.

RESPONSIBILITY:
- Provides validation mixins for developer agents
- Integrates continuous validation during code generation
- Supports TDD workflow with validation

PATTERNS:
- Mixin Pattern: Add validation to existing agents without inheritance
- Observer Pattern: Notify observers of validation events
- Strategy Pattern: Different validation strategies (RAG, self-critique)
- Factory Pattern: Create validated agents with all layers enabled

USAGE:
    from validated_developer import ValidatedDeveloperMixin, create_validated_developer_agent

    # Option 1: Use mixin
    class MyAgent(BaseAgent, ValidatedDeveloperMixin):
        pass

    # Option 2: Use factory
    agent = create_validated_developer_agent(
        developer_name="agent1",
        developer_type="conservative"
    )
"""

from validated_developer.core_mixin import ValidatedDeveloperMixin
from validated_developer.tdd_mixin import ValidatedTDDMixin
from validated_developer.factory import create_validated_developer_agent
from validated_developer.validation_strategies import (
    RAGValidationStrategy,
    SelfCritiqueValidationStrategy
)
from validated_developer.event_notifier import ValidationEventNotifier
from validated_developer.code_extractor import CodeExtractor

__all__ = [
    'ValidatedDeveloperMixin',
    'ValidatedTDDMixin',
    'create_validated_developer_agent',
    'RAGValidationStrategy',
    'SelfCritiqueValidationStrategy',
    'ValidationEventNotifier',
    'CodeExtractor'
]
