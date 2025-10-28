#!/usr/bin/env python3
"""
Stage Filtering - Filter pipeline stages based on routing decisions

WHAT:
Stage filtering logic that determines which stages to execute based on
AI routing decisions, workflow plans, and task requirements.

WHY:
Separates stage filtering from execution logic, enabling:
- Intelligent stage skipping based on task type
- Token optimization by avoiding unnecessary stages
- Clear separation between filtering and execution
- Testable filtering logic

RESPONSIBILITY:
- Filter stages based on workflow plan
- Filter stages based on intelligent routing decisions
- Retrieve pipeline metrics from observers
- Retrieve pipeline state from observers
- Map stage names to stage objects

PATTERNS:
- Strategy Pattern: Multiple filtering strategies
- Guard Clause: Early returns for boundary conditions
- Dispatch Table: Stage name mapping

EXTRACTED FROM: artemis_orchestrator.py lines 950-1010
"""

from typing import List, Dict, Optional, Any

from artemis_stage_interface import PipelineStage


def filter_stages_by_plan(stages: List[PipelineStage], workflow_plan: Dict) -> List[PipelineStage]:
    """
    Filter stages based on workflow plan

    WHAT:
    Filters the list of pipeline stages to only include those specified
    in the workflow plan, excluding any explicitly skipped stages.

    WHY:
    The workflow plan (AI-generated or rule-based) determines which stages
    are necessary for a given task. This avoids executing unnecessary stages,
    saving time and LLM tokens.

    Args:
        stages: Complete list of pipeline stages
        workflow_plan: Workflow plan with 'stages' and 'skip_stages' keys

    Returns:
        Filtered list of stages to execute

    PATTERNS:
        - Guard Clause: Returns empty list if no stages specified
        - Dispatch Table: Maps stage names to objects
    """
    stage_names_to_run = workflow_plan.get('stages', [])
    skip_stages = set(workflow_plan.get('skip_stages', []))

    # Guard: No stages specified
    if not stage_names_to_run:
        return []

    # Map stage names to stage objects
    stage_map = {stage.get_stage_name(): stage for stage in stages}

    # Return stages in plan order, excluding skipped
    filtered = []
    for name in stage_names_to_run:
        if name not in skip_stages and name in stage_map:
            filtered.append(stage_map[name])

    return filtered


def filter_stages_by_router(
    stages: List[PipelineStage],
    routing_decision: Any,
    intelligent_router: Any,
    logger: Any
) -> List[PipelineStage]:
    """
    Filter stages using intelligent routing decision

    WHAT:
    Uses AI-powered intelligent routing to determine which stages are
    necessary for a given task, filtering out unnecessary stages.

    WHY:
    Intelligent routing uses LLM analysis to determine which stages are
    actually needed, enabling significant token savings and faster execution.

    Args:
        stages: Complete list of pipeline stages
        routing_decision: AI routing decision with stage requirements
        intelligent_router: IntelligentRouter instance
        logger: Logger for status messages

    Returns:
        Filtered list of stages to execute

    PATTERNS:
        - Strategy Pattern: Delegates filtering to intelligent router
        - Guard Clause: Validates router and decision
    """
    # Guard: Invalid router or decision
    if not intelligent_router or not routing_decision:
        return stages

    # Filter stages using intelligent router
    stages_to_run = intelligent_router.filter_stages(stages, routing_decision)

    logger.log(f"🧠 Intelligent routing selected {len(stages_to_run)}/{len(stages)} stages", "INFO")

    return stages_to_run


def get_pipeline_metrics(orchestrator: Any) -> Optional[Dict]:
    """
    Get pipeline metrics from MetricsObserver

    WHAT:
    Retrieves pipeline execution metrics (stage durations, success rates, etc.)
    from the MetricsObserver if observers are enabled.

    WHY:
    Provides visibility into pipeline performance and health without
    tightly coupling orchestrator to observer implementation.

    Returns:
        Dict with pipeline metrics, or None if observers not enabled

    PATTERNS:
        - Guard Clause: Early return if observers disabled
        - Iterator Pattern: Searches for specific observer type
    """
    # Guard: Observers not enabled
    if not orchestrator.enable_observers:
        return None

    # Find MetricsObserver in attached observers
    from pipeline_observer import MetricsObserver
    observer = next((obs for obs in orchestrator.observable._observers if isinstance(obs, MetricsObserver)), None)
    return observer.get_summary() if observer else None


def get_pipeline_state(orchestrator: Any) -> Optional[Dict]:
    """
    Get current pipeline state from StateTrackingObserver

    WHAT:
    Retrieves current pipeline state (current stage, completion status, etc.)
    from the StateTrackingObserver if observers are enabled.

    WHY:
    Provides real-time pipeline state without coupling orchestrator to
    state tracking implementation. Useful for monitoring and debugging.

    Returns:
        Dict with pipeline state, or None if observers not enabled

    PATTERNS:
        - Guard Clause: Early return if observers disabled
        - Iterator Pattern: Searches for specific observer type
    """
    # Guard: Observers not enabled
    if not orchestrator.enable_observers:
        return None

    # Find StateTrackingObserver in attached observers
    from pipeline_observer import StateTrackingObserver
    observer = next((obs for obs in orchestrator.observable._observers if isinstance(obs, StateTrackingObserver)), None)
    return observer.get_state() if observer else None
