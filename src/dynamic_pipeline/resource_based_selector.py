#!/usr/bin/env python3
"""
Module: resource_based_selector.py

WHY: Pipeline execution must adapt to available resources (CPU, memory, time budget).
     Resource-constrained environments prioritize critical stages, skip expensive ones.

RESPONSIBILITY: Select pipeline stages based on available computational resources.

PATTERNS:
    - Strategy: Implements resource-aware stage selection
    - Guard Clauses: Early returns for resource profile determination
    - Dispatch Table: Maps resource profiles to filtering functions
"""

from typing import Dict, Any, List, Optional

from artemis_exceptions import PipelineException, wrap_exception
from artemis_services import PipelineLogger
from dynamic_pipeline.pipeline_stage import PipelineStage
from dynamic_pipeline.stage_selection_strategy import StageSelectionStrategy


class ResourceBasedSelector(StageSelectionStrategy):
    """
    Selects stages based on available resources (time, CPU, memory).

    Why it exists: Resource-constrained environments can't run all stages.
    Prioritizes critical stages when resources limited.

    Design pattern: Strategy implementation

    Selection rules:
        HIGH resources: All stages
        MEDIUM resources: Skip performance tests, detailed security scans
        LOW resources: Only critical stages (requirements, basic tests)
    """

    def __init__(self, logger: Optional[PipelineLogger] = None):
        self.logger = logger or PipelineLogger(verbose=True)
        # Resource thresholds (arbitrary units for demo)
        self._resource_profiles = {
            "high": {"cpu": 8, "memory_gb": 16, "time_minutes": 120},
            "medium": {"cpu": 4, "memory_gb": 8, "time_minutes": 60},
            "low": {"cpu": 2, "memory_gb": 4, "time_minutes": 30}
        }

    @wrap_exception(PipelineException, "Failed to select stages based on resources")
    def select_stages(
        self,
        available_stages: List[PipelineStage],
        context: Dict[str, Any]
    ) -> List[PipelineStage]:
        """Select stages based on available resources"""

        # Extract resource constraints from context
        available_cpu = context.get("cpu_cores", 4)
        available_memory = context.get("memory_gb", 8)
        available_time = context.get("time_budget_minutes", 60)

        # Determine resource profile using helper method
        profile = self._determine_profile(available_cpu, available_memory, available_time)

        self.logger.log(
            f"Resource profile: {profile} (CPU={available_cpu}, MEM={available_memory}GB, TIME={available_time}min)",
            "INFO"
        )

        # Filter stages based on resource profile
        # Why dispatch table: Avoids elif chain, declarative
        profile_filters = {
            "high": lambda s: True,  # All stages
            "medium": lambda s: not self._is_expensive_stage(s),
            "low": lambda s: self._is_critical_stage(s)
        }

        filter_func = profile_filters.get(profile, lambda s: True)
        selected = [stage for stage in available_stages if filter_func(stage)]

        self.logger.log(
            f"Selected {len(selected)}/{len(available_stages)} stages for {profile} resources",
            "INFO"
        )

        return selected

    def _determine_profile(self, cpu: int, memory: int, time: int) -> str:
        """
        Determine resource profile based on available resources.

        Why helper method: Extracts complex nested if logic into named,
        testable method. Uses guard clauses instead of nested ifs.
        """
        # Guard clause: Low resources
        if cpu <= 2 or memory <= 4 or time <= 30:
            return "low"

        # Guard clause: High resources
        if cpu >= 8 and memory >= 16 and time >= 120:
            return "high"

        # Default: Medium resources
        return "medium"

    def _is_expensive_stage(self, stage: PipelineStage) -> bool:
        """Check if stage is resource-intensive"""
        expensive_stages = {"performance", "load_test", "security_scan", "ui_test"}
        return any(name in stage.name.lower() for name in expensive_stages)

    def _is_critical_stage(self, stage: PipelineStage) -> bool:
        """Check if stage is critical (must run even with low resources)"""
        critical_stages = {"requirements", "development", "unit_tests"}
        return any(name in stage.name.lower() for name in critical_stages)
