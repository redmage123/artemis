#!/usr/bin/env python3
"""
Module: dynamic_pipeline_core.py

WHY: Backward compatibility wrapper for refactored dynamic pipeline core.
     Re-exports DynamicPipeline from modular package structure.

RESPONSIBILITY: Maintain 100% backward compatibility with existing imports.

PATTERNS:
    - Facade: Re-exports from core package
    - Backward Compatibility: Ensures existing code continues to work

MIGRATION NOTES:
    Original 664-line monolith refactored into modular package:
    - dynamic_pipeline/core/pipeline_context.py - Context management
    - dynamic_pipeline/core/execution_engine.py - Stage execution
    - dynamic_pipeline/core/lifecycle_manager.py - State transitions
    - dynamic_pipeline/core/ai_optimizer.py - AI optimization
    - dynamic_pipeline/core/pipeline_facade.py - Main orchestration

    All existing imports continue to work:
        from dynamic_pipeline.dynamic_pipeline_core import DynamicPipeline
"""

# Re-export DynamicPipeline for backward compatibility
from dynamic_pipeline.core.pipeline_facade import DynamicPipeline

# Re-export supporting classes for backward compatibility
from dynamic_pipeline.core.pipeline_context import PipelineContext
from dynamic_pipeline.core.execution_engine import ExecutionEngine
from dynamic_pipeline.core.lifecycle_manager import LifecycleManager
from dynamic_pipeline.core.ai_optimizer import AIOptimizer

__all__ = [
    'DynamicPipeline',
    'PipelineContext',
    'ExecutionEngine',
    'LifecycleManager',
    'AIOptimizer'
]
