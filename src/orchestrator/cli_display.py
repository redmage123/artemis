#!/usr/bin/env python3
"""
CLI Display - Workflow status display utilities

WHAT:
CLI utilities for displaying workflow status, active workflows,
and pipeline progress information.

WHY:
Separates display logic from orchestrator core and entry points, enabling:
- Focused testing of display formatting
- Reusable display utilities
- Clean separation of concerns
- Easy modification of output formats

RESPONSIBILITY:
- Display workflow status for a given card
- List all active workflows
- Format status information for human readability
- Support JSON output for programmatic access
- Handle missing/incomplete status data gracefully

PATTERNS:
- Guard Clause: Early returns for missing data
- Dispatch Table: Status icon mapping
- Template Method: Consistent display format

EXTRACTED FROM: artemis_orchestrator.py lines 1220-1382
"""

import json
from typing import Dict, Any
from pathlib import Path


def display_workflow_status(card_id: str, json_output: bool = False) -> None:
    """
    Display workflow status for a given card ID

    WHAT:
    Reads workflow status from tracking file and displays it in
    human-readable format or JSON.

    WHY:
    Provides visibility into pipeline progress without running
    the orchestrator. Useful for monitoring long-running tasks.

    OUTPUT (human-readable):
        - Card ID and current status
        - Current stage (if in progress)
        - Start and end times
        - Error messages (if failed)
        - Stage-by-stage breakdown with status icons

    OUTPUT (JSON):
        - Complete status data structure

    Args:
        card_id: Kanban card ID to query
        json_output: If True, output JSON instead of human-readable

    PATTERNS:
        - Guard Clause: Early return if status file missing
        - Dispatch Table: Status icon mapping
        - Template Method: Consistent display format
    """
    from workflow_status_tracker import WorkflowStatusTracker

    tracker = WorkflowStatusTracker(card_id=card_id)
    status_file = tracker.status_file

    # Guard: Status file doesn't exist
    if not status_file.exists():
        print(f"\n⚠️  No workflow status found for card: {card_id}")
        print(f"   Status file would be: {status_file}")
        print(f"   This workflow may not have started yet, or status tracking wasn't enabled.\n")
        return

    with open(status_file, 'r') as f:
        status_data = json.load(f)

    # JSON output mode
    if json_output:
        print(json.dumps(status_data, indent=2))
        return

    # Human-readable output
    print(f"\n{'='*70}")
    print(f"🏹 ARTEMIS WORKFLOW STATUS")
    print(f"{'='*70}")
    print(f"Card ID: {status_data['card_id']}")
    print(f"Status: {status_data['status'].upper()}")

    if status_data.get('current_stage'):
        print(f"Current Stage: {status_data['current_stage']}")

    if status_data.get('start_time'):
        print(f"Started: {status_data['start_time']}")

    if status_data.get('end_time'):
        print(f"Completed: {status_data['end_time']}")

    if status_data.get('error'):
        print(f"\n❌ ERROR: {status_data['error']}")

    # Display stages
    if status_data.get('stages'):
        print(f"\n{'-'*70}")
        print("STAGES:")
        print(f"{'-'*70}")

        for i, stage in enumerate(status_data['stages'], 1):
            status_icons = {
                'pending': '⏸️',
                'in_progress': '🔄',
                'completed': '✅',
                'failed': '❌',
                'skipped': '⏭️'
            }
            icon = status_icons.get(stage['status'], '❓')
            print(f"\n{i}. {icon} {stage['name']}")
            print(f"   Status: {stage['status']}")

            if stage.get('start_time'):
                print(f"   Started: {stage['start_time']}")
            if stage.get('end_time'):
                print(f"   Completed: {stage['end_time']}")
            if stage.get('error'):
                print(f"   ❌ Error: {stage['error']}")

    print(f"\n{'='*70}\n")


def list_active_workflows() -> None:
    """
    List all active workflows

    WHAT:
    Scans status directory for workflow status files and displays
    all currently running or failed workflows.

    WHY:
    Provides overview of all pipeline activity without querying
    individual cards. Useful for monitoring multiple concurrent
    pipelines.

    OUTPUT:
        - List of all running/failed workflows
        - Card ID, status, and current stage for each
        - Empty message if no active workflows

    PATTERNS:
        - Guard Clause: Early returns for empty/missing directory
        - Iterator Pattern: Processes all status files
    """
    status_dir = Path("/tmp/artemis_status")

    # Guard: Status directory doesn't exist
    if not status_dir.exists():
        print("\nNo active workflows found.\n")
        return

    status_files = list(status_dir.glob("*.json"))

    # Guard: No status files found
    if not status_files:
        print("\nNo active workflows found.\n")
        return

    print(f"\n{'='*70}")
    print("🏹 ACTIVE ARTEMIS WORKFLOWS")
    print(f"{'='*70}\n")

    for status_file in sorted(status_files):
        card_id = status_file.stem
        with open(status_file, 'r') as f:
            data = json.load(f)

        if data['status'] in ['running', 'failed']:
            status_str = data['status'].upper()
            print(f"📋 {card_id}")
            print(f"   Status: {status_str}")
            if data.get('current_stage'):
                print(f"   Current: {data['current_stage']}")
            print()

    print(f"{'='*70}\n")
