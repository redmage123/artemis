#!/usr/bin/env python3
"""
Pipeline Execution - Core pipeline execution logic

WHAT:
Main pipeline execution flow including planning, stage filtering,
execution via strategy, and result reporting.

WHY:
Separates execution logic from orchestrator initialization and configuration,
enabling:
- Focused testing of execution flow
- Clear separation between setup and execution
- Easy modification of execution strategy
- Isolated checkpoint/resume logic

RESPONSIBILITY:
- Execute full pipeline from planning to retrospective
- Generate AI-powered orchestration plans
- Filter stages using intelligent routing
- Coordinate strategy execution
- Handle checkpoints and resume
- Generate execution reports
- Broadcast pipeline events

PATTERNS:
- Template Method: Defines execution algorithm
- Strategy Pattern: Delegates to pluggable execution strategy
- Observer Pattern: Broadcasts lifecycle events
- Memento Pattern: Checkpoint/resume capability

EXTRACTED FROM: artemis_orchestrator.py lines 620-839
"""

import json
from typing import Dict, Any, List
from pathlib import Path

from artemis_stage_interface import PipelineStage
from artemis_constants import MAX_RETRY_ATTEMPTS
from orchestrator.helpers import notify_pipeline_start, notify_pipeline_completion, notify_pipeline_failure, run_retrospective


def run_full_pipeline(orchestrator: Any, max_retries: int = None) -> Dict:
    """
    Run complete Artemis pipeline using configured strategy

    WHAT:
    Executes end-to-end autonomous development pipeline: planning → development →
    review → testing → retrospective. Coordinates all stages, handles failures,
    broadcasts events, and produces comprehensive execution report.

    WHY:
    This is the main entry point for autonomous task execution. It orchestrates
    the entire workflow while maintaining separation of concerns:
    - Orchestrator handles planning, coordination, reporting
    - Strategy handles execution details (sequential vs parallel)
    - Stages handle specific functionality (development, testing, etc.)
    - Supervisor handles failure recovery
    - Observers handle monitoring

    EXECUTION FLOW:
    1. Validate card exists and retrieve details
    2. Generate AI-powered orchestration plan (or rule-based fallback)
    3. Query RAG for historical context and recommendations
    4. Broadcast pipeline_started event to observers
    5. Use intelligent routing to filter unnecessary stages (if available)
    6. Resume from checkpoint if requested (skip completed stages)
    7. Delegate execution to strategy (StandardPipelineStrategy by default)
    8. Broadcast pipeline_completed/pipeline_failed event
    9. Print supervisor health report (if supervision enabled)
    10. Run sprint retrospective (if LLM available and pipeline succeeded)
    11. Generate and save comprehensive execution report

    PATTERNS:
    - Template Method: Defines algorithm structure, strategy fills in execution
    - Strategy Pattern: Delegates execution to pluggable strategy
    - Observer Pattern: Broadcasts events at key points
    - Memento Pattern: Checkpoint resume capability

    INTEGRATION:
    - Calls: OrchestrationPlanner.create_plan() for AI planning
    - Calls: IntelligentRouter.make_routing_decision() for stage filtering
    - Calls: PipelineStrategy.execute() for stage execution
    - Calls: RetrospectiveAgent.conduct_retrospective() for learning
    - Calls: SupervisorAgent.print_health_report() for monitoring

    Args:
        orchestrator: ArtemisOrchestrator instance
        max_retries: Maximum number of retries for failed code reviews (default: MAX_RETRY_ATTEMPTS - 1)

    RETURNS:
        Dict with execution results:
            - card_id: str
            - workflow_plan: Dict (AI-generated plan)
            - stages: Dict (results from each stage)
            - status: str (COMPLETED_SUCCESSFULLY or FAILED)
            - execution_result: Dict (detailed execution info)
            - supervisor_statistics: Dict (health metrics)
            - retrospective: Dict (sprint learnings)

    RAISES:
        Exception: Re-raised from strategy.execute() if pipeline fails catastrophically
    """
    if max_retries is None:
        max_retries = MAX_RETRY_ATTEMPTS - 1  # Default: 2 retries

    # Start pipeline
    orchestrator.logger.log("=" * 60, "INFO")
    orchestrator.logger.log("🏹 ARTEMIS - STARTING AUTONOMOUS HUNT FOR OPTIMAL SOLUTION", "STAGE")
    orchestrator.logger.log(f"   Execution Strategy: {orchestrator.strategy.__class__.__name__}", "INFO")
    orchestrator.logger.log("=" * 60, "INFO")

    # Get card
    card, _ = orchestrator.board._find_card(orchestrator.card_id)
    if not card:
        orchestrator.logger.log(f"Card {orchestrator.card_id} not found", "ERROR")
        return {"status": "ERROR", "reason": "Card not found"}

    # Create AI-powered orchestration plan
    orchestration_plan = orchestrator.orchestration_planner.create_plan(
        card=card,
        platform_info=orchestrator.platform_info,
        resource_allocation=orchestrator.resource_allocation
    )

    # Convert OrchestrationPlan to dict for backward compatibility
    workflow_plan = orchestration_plan.to_dict()

    orchestrator.logger.log("📋 AI-GENERATED ORCHESTRATION PLAN", "INFO")
    orchestrator.logger.log(f"Complexity: {workflow_plan['complexity']}", "INFO")
    orchestrator.logger.log(f"Task Type: {workflow_plan['task_type']}", "INFO")
    orchestrator.logger.log(f"Parallel Developers: {workflow_plan['parallel_developers']}", "INFO")
    orchestrator.logger.log(f"Estimated Duration: {workflow_plan['estimated_duration_minutes']} minutes", "INFO")

    # Log AI reasoning
    if workflow_plan.get('reasoning'):
        orchestrator.logger.log("AI Reasoning:", "INFO")
        for reason in workflow_plan['reasoning']:
            orchestrator.logger.log(f"  • {reason}", "INFO")

    # Query RAG for historical context
    rag_recommendations = orchestrator.rag.get_recommendations(
        task_description=card.get('description', card.get('title', '')),
        context={'priority': card.get('priority'), 'complexity': workflow_plan['complexity']}
    )

    # Notify pipeline start
    notify_pipeline_start(
        orchestrator.card_id,
        card,
        workflow_plan,
        orchestrator.observable,
        orchestrator.messenger,
        orchestrator.enable_observers
    )

    # Build execution context
    context = {
        'card_id': orchestrator.card_id,
        'card': card,
        'workflow_plan': workflow_plan,
        'rag_recommendations': rag_recommendations,
        'parallel_developers': workflow_plan['parallel_developers']
    }

    # Use intelligent routing if available
    if orchestrator.intelligent_router:
        routing_decision = orchestrator.intelligent_router.make_routing_decision(card)
        orchestrator.intelligent_router.log_routing_decision(routing_decision)

        # Update workflow plan with intelligent router's recommendations
        workflow_plan['parallel_developers'] = routing_decision.requirements.parallel_developers_recommended
        context['parallel_developers'] = routing_decision.requirements.parallel_developers_recommended

        # Filter stages using intelligent router
        from orchestrator.stage_filtering import filter_stages_by_router
        stages_to_run = filter_stages_by_router(
            orchestrator.stages,
            routing_decision,
            orchestrator.intelligent_router,
            orchestrator.logger
        )
    else:
        # Fallback: Filter stages based on workflow plan
        from orchestrator.stage_filtering import filter_stages_by_plan
        stages_to_run = filter_stages_by_plan(orchestrator.stages, workflow_plan)

    # Checkpoint resume logic
    if orchestrator.resume and hasattr(orchestrator, 'checkpoint_manager') and orchestrator.checkpoint_manager.can_resume():
        checkpoint = orchestrator.checkpoint_manager.resume()
        orchestrator.logger.log(f"📥 Resuming from checkpoint: {len(checkpoint.stage_checkpoints)} stages completed", "INFO")

        # Get completed stages
        completed_stages = set(checkpoint.stage_checkpoints.keys())

        # Filter out completed stages
        original_count = len(stages_to_run)
        stages_to_run = [
            s for s in stages_to_run
            if s.__class__.__name__.replace('Stage', '').lower() not in completed_stages
        ]

        orchestrator.logger.log(f"⏭️  Skipping {len(completed_stages)} completed stages", "INFO")
        orchestrator.logger.log(f"▶️  Running {len(stages_to_run)} remaining stages", "INFO")
    else:
        # Execute pipeline using strategy (Strategy Pattern - delegates complexity)
        orchestrator.logger.log(f"▶️  Executing {len(stages_to_run)} stages...", "INFO")

    # Add orchestrator to context so strategy can access checkpoint_manager
    context['orchestrator'] = orchestrator

    execution_result = orchestrator.strategy.execute(stages_to_run, context)

    # Extract results
    stage_results = execution_result.get("results", {})
    final_status = execution_result.get("status")

    # Notify pipeline completion
    notify_pipeline_completion(
        orchestrator.card_id,
        card,
        stage_results,
        orchestrator.observable,
        orchestrator.messenger,
        orchestrator.enable_observers
    )

    # Determine completion status
    if final_status == "success":
        orchestrator.logger.log("=" * 60, "INFO")
        orchestrator.logger.log("🎉 ARTEMIS HUNT SUCCESSFUL - OPTIMAL SOLUTION DELIVERED!", "SUCCESS")
        orchestrator.logger.log("=" * 60, "INFO")
        pipeline_status = "COMPLETED_SUCCESSFULLY"
    else:
        orchestrator.logger.log("=" * 60, "ERROR")
        orchestrator.logger.log(f"❌ ARTEMIS PIPELINE FAILED - {execution_result.get('error', 'Unknown error')}", "ERROR")
        orchestrator.logger.log("=" * 60, "ERROR")
        pipeline_status = "FAILED"
        # Notify pipeline failure
        error = Exception(execution_result.get('error', 'Unknown error'))
        notify_pipeline_failure(
            orchestrator.card_id,
            card,
            error,
            stage_results,
            orchestrator.observable,
            orchestrator.messenger,
            orchestrator.enable_observers
        )

    # Print supervisor health report if supervision enabled
    if orchestrator.enable_supervision and orchestrator.supervisor:
        orchestrator.supervisor.print_health_report()

        # Cleanup any zombie processes
        cleaned = orchestrator.supervisor.cleanup_zombie_processes()
        if cleaned > 0:
            orchestrator.logger.log(f"🧹 Cleaned up {cleaned} zombie processes", "INFO")

    # Build final report
    supervisor_stats = orchestrator.supervisor.get_statistics() if orchestrator.enable_supervision and orchestrator.supervisor else None

    # Run Sprint Retrospective if LLM client available
    retrospective_report = None
    if orchestrator.llm_client and final_status == "success":
        try:
            orchestrator.logger.log("🔄 Conducting Sprint Retrospective...", "INFO")
            retrospective_report = run_retrospective(
                card,
                stage_results,
                context,
                orchestrator.llm_client,
                orchestrator.rag,
                orchestrator.logger,
                orchestrator.messenger,
                orchestrator.card_id
            )
            orchestrator.logger.log("✅ Retrospective complete", "SUCCESS")
        except Exception as e:
            orchestrator.logger.log(f"⚠️  Retrospective failed: {e}", "WARNING")

    report = {
        "card_id": orchestrator.card_id,
        "workflow_plan": workflow_plan,
        "stages": stage_results,
        "status": pipeline_status,
        "execution_result": execution_result,
        "supervisor_statistics": supervisor_stats,
        "retrospective": retrospective_report
    }

    # Save report
    report_path = Path("/tmp") / f"pipeline_full_report_{orchestrator.card_id}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    orchestrator.logger.log(f"📄 Full report saved: {report_path}", "INFO")

    return report
