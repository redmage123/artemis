#!/usr/bin/env python3
"""
Module: dynamic_pipeline.core

WHY: Core package for dynamic pipeline execution. Provides modular components
     for pipeline orchestration, execution, lifecycle management, and AI
     optimization.

RESPONSIBILITY: Export clean public API for pipeline core functionality.

PATTERNS:
    - Facade: DynamicPipeline provides simple interface
    - Modular Design: Each component has single responsibility
    - Clean API: Only expose necessary classes
"""

from dynamic_pipeline.core.pipeline_facade import DynamicPipeline
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
