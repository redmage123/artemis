"""
Module: orchestrator/helpers.py

WHY: Helper functions for platform, notifications, retrospective, code review.
RESPONSIBILITY: Standalone utility functions used by orchestrator.
PATTERNS: Guard Clauses, Early Returns.

EXTRACTED FROM: artemis_orchestrator.py (platform, notification, retrospective, code review helpers)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from platform_detector import PlatformDetector, PlatformInfo, ResourceAllocation
from rag_agent import RAGAgent
from artemis_stage_interface import LoggerInterface
from pipeline_observer import PipelineObservable, EventBuilder
from messenger_interface import MessengerInterface
from retrospective_agent import RetrospectiveAgent
from llm_client import LLMClient
from artemis_exceptions import RAGStorageError, FileReadError, create_wrapped_exception


def store_and_validate_platform_info(
    platform_info: PlatformInfo,
    resource_allocation: ResourceAllocation,
    rag: RAGAgent,
    logger: LoggerInterface,
    verbose: bool = True
) -> None:
    """Store platform information in RAG and validate against stored data"""
    try:
        # Query RAG for previously stored platform info
        stored_platform_data = rag.query(
            query="platform_info",
            collection_name="platform_metadata",
            n_results=1
        )

        # Validate platform hash if we have stored data
        if stored_platform_data and len(stored_platform_data.get('metadatas', [[]])[0]) > 0:
            stored_metadata = stored_platform_data['metadatas'][0][0]
            stored_platform_hash = stored_metadata.get('platform_hash')

            if stored_platform_hash and stored_platform_hash != platform_info.platform_hash:
                logger.log("⚠️  Platform configuration has changed since last run!", "WARNING")
                logger.log(f"   Previous platform hash: {stored_platform_hash}", "WARNING")
                logger.log(f"   Current platform hash: {platform_info.platform_hash}", "WARNING")
                logger.log("   Updating platform information in RAG...", "INFO")
            elif stored_platform_hash:
                logger.log("✅ Platform validation: Current platform matches stored configuration", "INFO")

        # Store/update platform information
        platform_data = platform_info.to_dict()
        allocation_data = resource_allocation.to_dict()

        combined_data = {
            "platform": platform_data,
            "resource_allocation": allocation_data,
            "timestamp": datetime.now().isoformat(),
            "platform_hash": platform_info.platform_hash
        }

        rag.store_artifact(
            artifact_type="platform_metadata",
            content=json.dumps(combined_data, indent=2),
            metadata={
                "platform_hash": platform_info.platform_hash,
                "os_type": platform_info.os_type,
                "cpu_cores": platform_info.cpu_count_logical,
                "total_memory_gb": platform_info.total_memory_gb,
                "max_parallel_developers": resource_allocation.max_parallel_developers,
                "max_parallel_tests": resource_allocation.max_parallel_tests,
                "timestamp": datetime.now().isoformat()
            },
            collection_name="platform_metadata"
        )

        if verbose:
            logger.log("✅ Platform information stored in RAG successfully", "INFO")

    except Exception as e:
        logger.log(f"⚠️  Failed to store/validate platform info in RAG: {e}", "WARNING")
        logger.log("   Continuing without platform validation...", "INFO")


def notify_pipeline_start(
    card_id: str,
    card: Dict,
    workflow_plan: Dict,
    observable: Optional[PipelineObservable],
    messenger: MessengerInterface,
    enable_observers: bool = True
) -> None:
    """Notify agents and observers that pipeline has started"""
    if enable_observers and observable:
        event = EventBuilder.pipeline_started(
            card_id,
            card_title=card.get('title'),
            workflow_plan=workflow_plan,
            complexity=workflow_plan.get('complexity'),
            parallel_developers=workflow_plan.get('parallel_developers')
        )
        observable.notify(event)

    messenger.send_notification(
        to_agent="all",
        card_id=card_id,
        notification_type="pipeline_started",
        data={
            "card_title": card.get('title'),
            "workflow_plan": workflow_plan
        },
        priority="medium"
    )

    messenger.update_shared_state(
        card_id=card_id,
        updates={
            "pipeline_status": "running",
            "current_stage": "planning"
        }
    )


def notify_pipeline_completion(
    card_id: str,
    card: Dict,
    stage_results: Dict,
    observable: Optional[PipelineObservable],
    messenger: MessengerInterface,
    enable_observers: bool = True
) -> None:
    """Notify agents and observers that pipeline completed"""
    if enable_observers and observable:
        event = EventBuilder.pipeline_completed(
            card_id,
            card_title=card.get('title'),
            stages_executed=len(stage_results),
            stage_results=stage_results
        )
        observable.notify(event)

    messenger.send_notification(
        to_agent="all",
        card_id=card_id,
        notification_type="pipeline_completed",
        data={
            "status": "COMPLETED_SUCCESSFULLY",
            "stages_executed": len(stage_results)
        },
        priority="medium"
    )

    messenger.update_shared_state(
        card_id=card_id,
        updates={
            "pipeline_status": "complete",
            "current_stage": "done"
        }
    )


def notify_pipeline_failure(
    card_id: str,
    card: Dict,
    error: Exception,
    stage_results: Dict,
    observable: Optional[PipelineObservable],
    messenger: MessengerInterface,
    enable_observers: bool = True
) -> None:
    """Notify agents and observers that pipeline failed"""
    if enable_observers and observable:
        event = EventBuilder.pipeline_failed(
            card_id,
            error=error,
            card_title=card.get('title'),
            stages_executed=len(stage_results) if stage_results else 0
        )
        observable.notify(event)

    messenger.send_notification(
        to_agent="all",
        card_id=card_id,
        notification_type="pipeline_failed",
        data={
            "error": str(error),
            "stages_executed": len(stage_results) if stage_results else 0
        },
        priority="high"
    )

    messenger.update_shared_state(
        card_id=card_id,
        updates={
            "pipeline_status": "failed",
            "current_stage": "failed",
            "error": str(error)
        }
    )


def collect_sprint_metrics(card: Dict, stage_results: Dict, context: Dict) -> Dict:
    """Collect sprint metrics from pipeline execution"""
    planned_story_points = context.get('sprints', [{}])[0].get('total_story_points',
                                                                 card.get('story_points', 5))

    total_stages = len(stage_results)
    completed_stages = sum(1 for result in stage_results.values()
                         if result.get('status') in ['PASS', 'success', 'completed'])

    completion_rate = (completed_stages / max(total_stages, 1)) * 100
    completed_story_points = int(planned_story_points * (completion_rate / 100))

    testing_result = stage_results.get('testing', {})
    tests_passing = testing_result.get('test_pass_rate', 100.0)

    validation_result = stage_results.get('validation', {})
    bugs_found = validation_result.get('issues_found', 0) if validation_result else 0
    bugs_fixed = validation_result.get('issues_fixed', 0) if validation_result else 0

    blockers_encountered = total_stages - completed_stages

    return {
        "sprint_number": 1,
        "start_date": card.get('created_at', datetime.now().isoformat())[:10],
        "end_date": datetime.now().isoformat()[:10],
        "total_story_points": planned_story_points,
        "completed_story_points": completed_story_points,
        "bugs_found": bugs_found,
        "bugs_fixed": bugs_fixed,
        "test_pass_rate": tests_passing,
        "code_review_iterations": 1,
        "average_task_duration_hours": 0,
        "blockers_encountered": blockers_encountered
    }


def run_retrospective(
    card: Dict,
    stage_results: Dict,
    context: Dict,
    llm_client: LLMClient,
    rag: RAGAgent,
    logger: LoggerInterface,
    messenger: MessengerInterface,
    card_id: str
) -> Dict:
    """Run sprint retrospective to learn from pipeline execution"""
    sprint_data = collect_sprint_metrics(card, stage_results, context)

    retrospective = RetrospectiveAgent(
        llm_client=llm_client,
        rag=rag,
        logger=logger,
        messenger=messenger,
        historical_sprints_to_analyze=3
    )

    report = retrospective.conduct_retrospective(
        sprint_number=1,
        sprint_data=sprint_data,
        card_id=card_id
    )

    return {
        "sprint_number": report.sprint_number,
        "overall_health": report.overall_health,
        "velocity": report.metrics.velocity,
        "velocity_trend": report.velocity_trend,
        "what_went_well_count": len(report.what_went_well),
        "what_didnt_go_well_count": len(report.what_didnt_go_well),
        "action_items_count": len(report.action_items),
        "key_learnings": report.key_learnings,
        "recommendations": report.recommendations
    }


def load_review_report(report_file: str, developer_name: str) -> List[Dict]:
    """Load detailed issues from a review report file"""
    if not report_file or not Path(report_file).exists():
        return []

    try:
        with open(report_file, 'r') as f:
            full_review = json.load(f)
            return full_review.get('issues', [])
    except Exception as e:
        raise create_wrapped_exception(
            e,
            FileReadError,
            "Could not load detailed code review report",
            {
                "report_file": report_file,
                "developer": developer_name
            }
        )


def extract_code_review_feedback(code_review_result: Dict) -> Dict:
    """Extract detailed code review feedback for developers"""
    feedback = {
        'status': code_review_result.get('status', 'UNKNOWN'),
        'total_critical_issues': code_review_result.get('total_critical_issues', 0),
        'total_high_issues': code_review_result.get('total_high_issues', 0),
        'developer_reviews': []
    }

    reviews = code_review_result.get('reviews', [])
    for review in reviews:
        developer_name = review.get('developer', 'unknown')
        report_file = review.get('report_file', '')

        detailed_issues = load_review_report(report_file, developer_name)

        feedback['developer_reviews'].append({
            'developer': developer_name,
            'review_status': review.get('review_status', 'UNKNOWN'),
            'overall_score': review.get('overall_score', 0),
            'critical_issues': review.get('critical_issues', 0),
            'high_issues': review.get('high_issues', 0),
            'detailed_issues': detailed_issues,
            'report_file': report_file
        })

    return feedback


__all__ = [
    "store_and_validate_platform_info",
    "notify_pipeline_start",
    "notify_pipeline_completion",
    "notify_pipeline_failure",
    "collect_sprint_metrics",
    "run_retrospective",
    "load_review_report",
    "extract_code_review_feedback"
]
