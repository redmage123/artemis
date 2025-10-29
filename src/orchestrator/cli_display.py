from artemis_logger import get_logger
logger = get_logger('cli_display')
'\nCLI Display - Workflow status display utilities\n\nWHAT:\nCLI utilities for displaying workflow status, active workflows,\nand pipeline progress information.\n\nWHY:\nSeparates display logic from orchestrator core and entry points, enabling:\n- Focused testing of display formatting\n- Reusable display utilities\n- Clean separation of concerns\n- Easy modification of output formats\n\nRESPONSIBILITY:\n- Display workflow status for a given card\n- List all active workflows\n- Format status information for human readability\n- Support JSON output for programmatic access\n- Handle missing/incomplete status data gracefully\n\nPATTERNS:\n- Guard Clause: Early returns for missing data\n- Dispatch Table: Status icon mapping\n- Template Method: Consistent display format\n\nEXTRACTED FROM: artemis_orchestrator.py lines 1220-1382\n'
import json
from typing import Dict, Any
from pathlib import Path

def display_workflow_status(card_id: str, json_output: bool=False) -> None:
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
    if not status_file.exists():
        
        logger.log(f'\n⚠️  No workflow status found for card: {card_id}', 'INFO')
        
        logger.log(f'   Status file would be: {status_file}', 'INFO')
        
        logger.log(f"   This workflow may not have started yet, or status tracking wasn't enabled.\n", 'INFO')
        return
    with open(status_file, 'r') as f:
        status_data = json.load(f)
    if json_output:
        
        logger.log(json.dumps(status_data, indent=2), 'INFO')
        return
    
    logger.log(f"\n{'=' * 70}", 'INFO')
    
    logger.log(f'🏹 ARTEMIS WORKFLOW STATUS', 'INFO')
    
    logger.log(f"{'=' * 70}", 'INFO')
    
    logger.log(f"Card ID: {status_data['card_id']}", 'INFO')
    
    logger.log(f"Status: {status_data['status'].upper()}", 'INFO')
    if status_data.get('current_stage'):
        
        logger.log(f"Current Stage: {status_data['current_stage']}", 'INFO')
    if status_data.get('start_time'):
        
        logger.log(f"Started: {status_data['start_time']}", 'INFO')
    if status_data.get('end_time'):
        
        logger.log(f"Completed: {status_data['end_time']}", 'INFO')
    if status_data.get('error'):
        
        logger.log(f"\n❌ ERROR: {status_data['error']}", 'INFO')
    if status_data.get('stages'):
        
        logger.log(f"\n{'-' * 70}", 'INFO')
        
        logger.log('STAGES:', 'INFO')
        
        logger.log(f"{'-' * 70}", 'INFO')
        for i, stage in enumerate(status_data['stages'], 1):
            status_icons = {'pending': '⏸️', 'in_progress': '🔄', 'completed': '✅', 'failed': '❌', 'skipped': '⏭️'}
            icon = status_icons.get(stage['status'], '❓')
            
            logger.log(f"\n{i}. {icon} {stage['name']}", 'INFO')
            
            logger.log(f"   Status: {stage['status']}", 'INFO')
            if stage.get('start_time'):
                
                logger.log(f"   Started: {stage['start_time']}", 'INFO')
            if stage.get('end_time'):
                
                logger.log(f"   Completed: {stage['end_time']}", 'INFO')
            if stage.get('error'):
                
                logger.log(f"   ❌ Error: {stage['error']}", 'INFO')
    
    logger.log(f"\n{'=' * 70}\n", 'INFO')

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
    status_dir = Path('/tmp/artemis_status')
    if not status_dir.exists():
        
        logger.log('\nNo active workflows found.\n', 'INFO')
        return
    status_files = list(status_dir.glob('*.json'))
    if not status_files:
        
        logger.log('\nNo active workflows found.\n', 'INFO')
        return
    
    logger.log(f"\n{'=' * 70}", 'INFO')
    
    logger.log('🏹 ACTIVE ARTEMIS WORKFLOWS', 'INFO')
    
    logger.log(f"{'=' * 70}\n", 'INFO')
    for status_file in sorted(status_files):
        card_id = status_file.stem
        with open(status_file, 'r') as f:
            data = json.load(f)
        if data['status'] in ['running', 'failed']:
            status_str = data['status'].upper()
            
            logger.log(f'📋 {card_id}', 'INFO')
            
            logger.log(f'   Status: {status_str}', 'INFO')
            if data.get('current_stage'):
                
                logger.log(f"   Current: {data['current_stage']}", 'INFO')
            
            pass
    
    logger.log(f"{'=' * 70}\n", 'INFO')