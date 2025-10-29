"""
Adaptive Pipeline Integration - Smart pipeline selection based on task complexity

WHY: Automatically select optimal pipeline (FAST/MEDIUM/FULL) based on task complexity
     to avoid over-engineering simple tasks.

RESPONSIBILITY:
- Detect task complexity from parsed requirements
- Select appropriate pipeline strategy (Fast/Standard/Parallel)
- Configure skip flags and parallel settings
- Track metrics on pipeline selection

PATTERNS:
- Strategy Pattern: Select execution strategy based on complexity
- Adapter Pattern: Adapt complexity detection to strategy selection
- Metrics Pattern: Track selection accuracy and performance

INTEGRATION POINT:
Called in entry_points.py after requirements parsing, before orchestrator creation.
"""

from typing import Dict, Optional, Any
from datetime import datetime
import sys
from pathlib import Path

# Add src to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

from adaptive_pipeline_builder import detect_and_recommend_pipeline, PipelinePath
from artemis_logger import get_logger

try:
    from workflows.strategies.fast_strategy import FastPipelineStrategy
    from workflows.strategies.parallel_strategy import ParallelPipelineStrategy
except ImportError:
    # Fallback imports
    from pipeline_strategies import StandardPipelineStrategy as FastPipelineStrategy
    from pipeline_strategies import StandardPipelineStrategy as ParallelPipelineStrategy

from pipeline_strategies import StandardPipelineStrategy

logger = get_logger(__name__)


class AdaptivePipelineSelector:
    """
    Selects optimal pipeline strategy based on task complexity.

    WHY: Eliminate over-engineering by matching pipeline to task complexity.
    """

    def __init__(self, enable_metrics: bool = True):
        """
        Initialize selector.

        Args:
            enable_metrics: Enable metrics tracking (default: True)
        """
        self.enable_metrics = enable_metrics
        self.metrics = []

    def select_strategy(
        self,
        parsed_requirements: Any,
        card: Dict,
        force_path: Optional[str] = None,
        observable: Optional[Any] = None,
        verbose: bool = True
    ) -> Any:
        """
        Select appropriate pipeline strategy based on task complexity.

        Args:
            parsed_requirements: Parsed requirements from RequirementsParserAgent
            card: Task card with title, description, priority
            force_path: Optional forced path ('fast', 'medium', 'full')
            observable: Pipeline observable for event broadcasting
            verbose: Enable verbose logging

        Returns:
            Pipeline strategy instance (FastPipelineStrategy, StandardPipelineStrategy, or ParallelPipelineStrategy)
        """
        # Convert parsed requirements to dict format expected by detector
        requirements_dict = self._convert_requirements_to_dict(parsed_requirements)

        # Detect complexity and get pipeline recommendation
        logger.log("\n🔍 [AdaptivePipeline] Detecting task complexity...", "INFO")

        # Apply forced path if specified
        force_pipeline_path = None
        if force_path:
            path_map = {
                'fast': PipelinePath.FAST,
                'medium': PipelinePath.MEDIUM,
                'full': PipelinePath.FULL,
            }
            force_pipeline_path = path_map.get(force_path.lower())
            if force_pipeline_path:
                logger.log(f"⚙️  [AdaptivePipeline] Forcing pipeline path: {force_path.upper()}", "INFO")

        # Get adaptive pipeline builder recommendation
        from adaptive_pipeline_builder import AdaptivePipelineBuilder
        builder = AdaptivePipelineBuilder()

        pipeline_config = builder.build_pipeline(
            requirements_dict,
            card,
            force_path=force_pipeline_path
        )

        # Log detection results
        logger.log(f"✅ [AdaptivePipeline] Detected complexity: {pipeline_config['complexity'].upper()}", "INFO")
        logger.log(f"🎯 [AdaptivePipeline] Selected path: {pipeline_config['path'].upper()}", "INFO")
        logger.log(f"⏱️  [AdaptivePipeline] Estimated duration: {pipeline_config['estimated_duration_minutes']} minutes", "INFO")
        logger.log(f"📊 [AdaptivePipeline] Stages: {len(pipeline_config['stages'])}", "INFO")
        logger.log(f"💡 [AdaptivePipeline] Reasoning: {pipeline_config['reasoning']}", "INFO")

        # Track metrics
        if self.enable_metrics:
            self._track_selection(pipeline_config, card)

        # Map path to strategy class
        strategy = self._create_strategy(pipeline_config, observable, verbose)

        # Store pipeline config in strategy for later use
        strategy.pipeline_config = pipeline_config

        return strategy

    def _convert_requirements_to_dict(self, parsed_reqs: Any) -> Dict:
        """
        Convert StructuredRequirements to dict format.

        Args:
            parsed_reqs: StructuredRequirements object from parser

        Returns:
            Dict with 'functional' and 'non_functional' keys
        """
        # Handle StructuredRequirements object
        if hasattr(parsed_reqs, 'functional_requirements'):
            functional = [
                {
                    'id': getattr(req, 'id', f'FR-{i}'),
                    'description': getattr(req, 'description', str(req)),
                    'priority': getattr(req, 'priority', 'medium'),
                }
                for i, req in enumerate(parsed_reqs.functional_requirements, 1)
            ]

            non_functional = [
                {
                    'id': getattr(req, 'id', f'NFR-{i}'),
                    'description': getattr(req, 'description', str(req)),
                    'category': getattr(req, 'category', 'performance'),
                }
                for i, req in enumerate(parsed_reqs.non_functional_requirements, 1)
            ]

            return {
                'functional': functional,
                'non_functional': non_functional,
            }

        # Already in dict format
        if isinstance(parsed_reqs, dict):
            return parsed_reqs

        # Fallback
        return {'functional': [], 'non_functional': []}

    def _create_strategy(
        self,
        pipeline_config: Dict,
        observable: Optional[Any],
        verbose: bool
    ) -> Any:
        """
        Create appropriate strategy instance based on pipeline config.

        Args:
            pipeline_config: Pipeline configuration from adaptive builder
            observable: Pipeline observable
            verbose: Verbose logging

        Returns:
            Strategy instance
        """
        path = pipeline_config['path']

        # Determine skip stages based on config
        skip_stages = []
        for key, value in pipeline_config.items():
            if key.startswith('skip_') and value:
                # Convert skip_sprint_planning -> sprint_planning
                stage_name = key.replace('skip_', '')
                skip_stages.append(stage_name)

        if path == 'fast':
            logger.log("🚀 [AdaptivePipeline] Using FastPipelineStrategy", "INFO")
            try:
                return FastPipelineStrategy(
                    skip_stages=skip_stages,
                    verbose=verbose,
                    observable=observable
                )
            except TypeError:
                # Fallback if FastPipelineStrategy doesn't exist
                return StandardPipelineStrategy(
                    verbose=verbose,
                    observable=observable
                )

        elif path == 'medium':
            logger.log("⚡ [AdaptivePipeline] Using StandardPipelineStrategy (MEDIUM path)", "INFO")
            return StandardPipelineStrategy(
                verbose=verbose,
                observable=observable
            )

        else:  # full
            logger.log("🏗️  [AdaptivePipeline] Using ParallelPipelineStrategy (FULL path)", "INFO")
            try:
                return ParallelPipelineStrategy(
                    max_parallel_developers=pipeline_config.get('parallel_developers', 2),
                    verbose=verbose,
                    observable=observable
                )
            except TypeError:
                # Fallback if ParallelPipelineStrategy doesn't exist
                return StandardPipelineStrategy(
                    verbose=verbose,
                    observable=observable
                )

    def _track_selection(self, pipeline_config: Dict, card: Dict):
        """
        Track pipeline selection for metrics and analysis.

        Args:
            pipeline_config: Selected pipeline configuration
            card: Task card
        """
        metric = {
            'timestamp': datetime.utcnow().isoformat(),
            'card_id': card.get('id', 'unknown'),
            'title': card.get('title', 'unknown'),
            'complexity': pipeline_config['complexity'],
            'path': pipeline_config['path'],
            'estimated_duration_minutes': pipeline_config['estimated_duration_minutes'],
            'num_stages': len(pipeline_config['stages']),
            'reasoning': pipeline_config['reasoning'],
        }

        self.metrics.append(metric)

        # Log to Redis if available
        try:
            from redis_metrics import track_pipeline_selection
            track_pipeline_selection(metric)
        except ImportError:
            pass  # Redis metrics not available

    def get_metrics_summary(self) -> Dict:
        """
        Get summary of pipeline selection metrics.

        Returns:
            Dict with metrics summary
        """
        if not self.metrics:
            return {'total_selections': 0}

        total = len(self.metrics)
        by_path = {}
        by_complexity = {}

        for metric in self.metrics:
            path = metric['path']
            complexity = metric['complexity']

            by_path[path] = by_path.get(path, 0) + 1
            by_complexity[complexity] = by_complexity.get(complexity, 0) + 1

        avg_duration = sum(m['estimated_duration_minutes'] for m in self.metrics) / total

        return {
            'total_selections': total,
            'by_path': by_path,
            'by_complexity': by_complexity,
            'average_estimated_duration_minutes': avg_duration,
            'metrics': self.metrics,
        }


def select_adaptive_strategy(
    parsed_requirements: Any,
    card: Dict,
    force_path: Optional[str] = None,
    observable: Optional[Any] = None,
    verbose: bool = True
) -> Any:
    """
    Convenience function to select pipeline strategy based on complexity.

    Usage:
        strategy = select_adaptive_strategy(parsed_reqs, card)
        orchestrator = ArtemisOrchestrator(..., strategy=strategy)

    Args:
        parsed_requirements: Parsed requirements from RequirementsParserAgent
        card: Task card
        force_path: Optional forced path ('fast', 'medium', 'full')
        observable: Pipeline observable
        verbose: Verbose logging

    Returns:
        Pipeline strategy instance
    """
    selector = AdaptivePipelineSelector()
    return selector.select_strategy(
        parsed_requirements,
        card,
        force_path=force_path,
        observable=observable,
        verbose=verbose
    )