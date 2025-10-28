#!/usr/bin/env python3
"""
Batch Processing - Process multiple tasks from Kanban board

WHAT:
Batch processing logic for iterating through all pending tasks on
the Kanban board and executing the pipeline for each one.

WHY:
Separates batch processing from single-task execution, enabling:
- Focused testing of batch logic
- Clear separation of concerns
- Easy modification of batch behavior
- Independent evolution of batch vs single-task modes

RESPONSIBILITY:
- Iterate through pending tasks on Kanban board
- Execute pipeline for each task
- Handle task failures gracefully
- Generate consolidated batch report
- Track batch progress and statistics

PATTERNS:
- Iterator Pattern: Processes tasks sequentially
- Template Method: Uses run_full_pipeline for each task
- Guard Clause: Early returns for boundary conditions
- Facade Pattern: Simplifies batch execution

EXTRACTED FROM: artemis_orchestrator.py lines 841-948
"""

import json
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime


def run_all_pending_tasks(orchestrator: Any, max_tasks: int = None) -> List[Dict]:
    """
    Process all pending tasks on the kanban board until complete

    WHAT:
    Iterates through all pending tasks on the Kanban board, executes the
    pipeline for each one, and generates a consolidated report of results.

    WHY:
    Enables autonomous batch processing of multiple tasks without manual
    intervention. This is the "batch mode" equivalent of run_full_pipeline.

    FLOW:
    1. Loop while board has incomplete cards
    2. Get next pending card (backlog or in-progress)
    3. Switch to that card's context
    4. Execute full pipeline
    5. Capture results and update statistics
    6. Repeat until all cards complete or max_tasks reached
    7. Generate consolidated batch report

    This method implements the intelligent orchestrator pattern where
    the pipeline iterates over ALL tasks on the board, processes each one,
    and updates the board status accordingly.

    Args:
        orchestrator: ArtemisOrchestrator instance
        max_tasks: Maximum number of tasks to process (None = all)

    Returns:
        List of pipeline reports for each processed task

    PATTERNS:
        - Iterator Pattern: Processes tasks one at a time
        - Guard Clause: Early returns for boundary conditions
        - Template Method: Reuses run_full_pipeline for each task
    """
    orchestrator.logger.log("=" * 60, "INFO")
    orchestrator.logger.log("🔄 PROCESSING ALL PENDING TASKS ON KANBAN BOARD", "STAGE")
    orchestrator.logger.log("=" * 60, "INFO")

    all_reports = []
    task_count = 0

    # Loop until all tasks are complete or max reached
    while orchestrator.board.has_incomplete_cards():
        # Get pending cards (backlog + in-progress)
        pending_cards = orchestrator.board.get_pending_cards()

        # Guard: No more pending tasks
        if not pending_cards:
            orchestrator.logger.log("✅ No more pending tasks - board complete!", "SUCCESS")
            break

        # Guard: Reached maximum task limit
        if max_tasks and task_count >= max_tasks:
            orchestrator.logger.log(f"⚠️  Reached maximum task limit ({max_tasks})", "WARNING")
            break

        # Process next card
        card = pending_cards[0]  # Process in order
        card_id = card.get('card_id')
        card_title = card.get('title', 'Unknown')

        orchestrator.logger.log("", "INFO")
        orchestrator.logger.log("=" * 60, "INFO")
        orchestrator.logger.log(f"📋 PROCESSING TASK {task_count + 1}: {card_title}", "STAGE")
        orchestrator.logger.log(f"   Card ID: {card_id}", "INFO")
        orchestrator.logger.log("=" * 60, "INFO")

        # Temporarily switch card_id for this task
        original_card_id = orchestrator.card_id
        orchestrator.card_id = card_id

        try:
            # Run full pipeline for this card
            from orchestrator.pipeline_execution import run_full_pipeline
            report = run_full_pipeline(orchestrator)
            all_reports.append(report)

            task_count += 1

            # Check if task completed successfully
            if report.get('status') == 'COMPLETED_SUCCESSFULLY':
                orchestrator.logger.log(f"✅ Task {task_count} completed successfully", "SUCCESS")
            else:
                orchestrator.logger.log(f"❌ Task {task_count} failed: {report.get('status')}", "ERROR")

        except Exception as e:
            orchestrator.logger.log(f"❌ Task {task_count + 1} failed with exception: {e}", "ERROR")
            all_reports.append({
                "card_id": card_id,
                "status": "FAILED_WITH_EXCEPTION",
                "error": str(e)
            })
            task_count += 1

        finally:
            # Restore original card_id
            orchestrator.card_id = original_card_id

        # Brief pause between tasks
        orchestrator.logger.log("", "INFO")

    # Final summary
    orchestrator.logger.log("=" * 60, "INFO")
    orchestrator.logger.log("📊 BOARD PROCESSING COMPLETE", "STAGE")
    orchestrator.logger.log("=" * 60, "INFO")
    orchestrator.logger.log(f"Total tasks processed: {task_count}", "INFO")

    successful = sum(1 for r in all_reports if r.get('status') == 'COMPLETED_SUCCESSFULLY')
    failed = task_count - successful

    orchestrator.logger.log(f"✅ Successful: {successful}", "SUCCESS")
    if failed > 0:
        orchestrator.logger.log(f"❌ Failed: {failed}", "ERROR")

    # Save consolidated report
    consolidated_report = {
        "total_tasks_processed": task_count,
        "successful_tasks": successful,
        "failed_tasks": failed,
        "task_reports": all_reports,
        "completion_timestamp": datetime.utcnow().isoformat() + 'Z'
    }

    report_path = Path("/tmp") / "pipeline_board_processing_report.json"
    with open(report_path, 'w') as f:
        json.dump(consolidated_report, f, indent=2)

    orchestrator.logger.log(f"📄 Consolidated report saved: {report_path}", "INFO")
    orchestrator.logger.log("=" * 60, "INFO")

    return all_reports
