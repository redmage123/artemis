from artemis_logger import get_logger
logger = get_logger('artemis_status')
'\nArtemis Workflow Status Query Tool\nProvides real-time status information for running Artemis workflows\n'
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kanban_manager import KanbanBoard

class WorkflowStatus(Enum):
    """Workflow execution status"""
    NOT_STARTED = 'not_started'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    UNKNOWN = 'unknown'

class StageStatus(Enum):
    """Stage execution status"""
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'
    SKIPPED = 'skipped'

@dataclass
class StageInfo:
    """Information about a workflow stage"""
    name: str
    status: StageStatus
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None

@dataclass
class WorkflowInfo:
    """Complete workflow status information"""
    card_id: str
    title: str
    status: WorkflowStatus
    current_stage: Optional[str] = None
    stages: List[StageInfo] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    progress_percentage: int = 0

class ArtemisStatusQuery:
    """Query and display Artemis workflow status"""

    def __init__(self, verbose: bool=False):
        self.verbose = verbose
        self.kanban = KanbanBoard()
        status_dir = os.getenv('ARTEMIS_STATUS_DIR', '../../.artemis_data/status')
        if not os.path.isabs(status_dir):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            status_dir = os.path.join(script_dir, status_dir)
        self.status_dir = Path(status_dir)
        self.status_dir.mkdir(exist_ok=True, parents=True)

    def get_workflow_status(self, card_id: str) -> WorkflowInfo:
        """
        Get complete workflow status for a card

        Args:
            card_id: Card identifier

        Returns:
            WorkflowInfo with current status
        """
        cards = self.kanban.list_cards()
        card = next((c for c in cards if c.get('id') == card_id), None)
        if not card:
            return WorkflowInfo(card_id=card_id, title='Card not found', status=WorkflowStatus.UNKNOWN)
        status_file = self.status_dir / f'{card_id}.json'
        if status_file.exists():
            with open(status_file, 'r') as f:
                status_data = json.load(f)
            return self._parse_status_file(card_id, card['title'], status_data)
        kanban_status = card.get('status', 'To Do')
        if kanban_status == 'In Progress':
            workflow_status = WorkflowStatus.RUNNING
        elif kanban_status == 'Done':
            workflow_status = WorkflowStatus.COMPLETED
        else:
            workflow_status = WorkflowStatus.NOT_STARTED
        return WorkflowInfo(card_id=card_id, title=card['title'], status=workflow_status)

    def _parse_status_file(self, card_id: str, title: str, data: Dict) -> WorkflowInfo:
        """Parse status file data into WorkflowInfo"""
        stages = []
        for stage_data in data.get('stages', []):
            stages.append(StageInfo(name=stage_data['name'], status=StageStatus(stage_data['status']), start_time=stage_data.get('start_time'), end_time=stage_data.get('end_time'), duration_seconds=stage_data.get('duration_seconds'), error_message=stage_data.get('error')))
        total_stages = len(stages)
        completed_stages = sum((1 for s in stages if s.status == StageStatus.COMPLETED))
        progress = int(completed_stages / total_stages * 100) if total_stages > 0 else 0
        return WorkflowInfo(card_id=card_id, title=title, status=WorkflowStatus(data['status']), current_stage=data.get('current_stage'), stages=stages, start_time=data.get('start_time'), end_time=data.get('end_time'), total_duration_seconds=data.get('total_duration_seconds'), error_message=data.get('error'), progress_percentage=progress)

    def display_status(self, card_id: str, json_output: bool=False):
        """
        Display workflow status in human-readable format

        Args:
            card_id: Card identifier
            json_output: If True, output JSON instead of formatted text
        """
        workflow = self.get_workflow_status(card_id)
        if json_output:
            output = {'card_id': workflow.card_id, 'title': workflow.title, 'status': workflow.status.value, 'current_stage': workflow.current_stage, 'progress_percentage': workflow.progress_percentage, 'start_time': workflow.start_time, 'end_time': workflow.end_time, 'total_duration_seconds': workflow.total_duration_seconds, 'error_message': workflow.error_message, 'stages': [{'name': s.name, 'status': s.status.value, 'start_time': s.start_time, 'end_time': s.end_time, 'duration_seconds': s.duration_seconds, 'error_message': s.error_message} for s in workflow.stages or []]}
            
            logger.log(json.dumps(output, indent=2), 'INFO')
            return
        
        logger.log(f"\n{'=' * 70}", 'INFO')
        
        logger.log(f'🏹 ARTEMIS WORKFLOW STATUS', 'INFO')
        
        logger.log(f"{'=' * 70}", 'INFO')
        
        logger.log(f'Card ID: {workflow.card_id}', 'INFO')
        
        logger.log(f'Title: {workflow.title}', 'INFO')
        
        logger.log(f'Status: {self._format_status(workflow.status)}', 'INFO')
        if workflow.progress_percentage > 0:
            
            logger.log(f'Progress: {self._format_progress_bar(workflow.progress_percentage)}', 'INFO')
        if workflow.current_stage:
            
            logger.log(f'Current Stage: {workflow.current_stage}', 'INFO')
        if workflow.start_time:
            
            logger.log(f'Started: {workflow.start_time}', 'INFO')
        if workflow.end_time:
            
            logger.log(f'Completed: {workflow.end_time}', 'INFO')
        if workflow.total_duration_seconds:
            
            logger.log(f'Duration: {self._format_duration(workflow.total_duration_seconds)}', 'INFO')
        if workflow.error_message:
            
            logger.log(f'\n❌ ERROR: {workflow.error_message}', 'INFO')
        if workflow.stages:
            
            logger.log(f"\n{'-' * 70}", 'INFO')
            
            logger.log('STAGES:', 'INFO')
            
            logger.log(f"{'-' * 70}", 'INFO')
            for i, stage in enumerate(workflow.stages, 1):
                status_icon = self._get_stage_icon(stage.status)
                
                logger.log(f'\n{i}. {status_icon} {stage.name}', 'INFO')
                
                logger.log(f'   Status: {stage.status.value}', 'INFO')
                if stage.start_time:
                    
                    logger.log(f'   Started: {stage.start_time}', 'INFO')
                if stage.end_time:
                    
                    logger.log(f'   Completed: {stage.end_time}', 'INFO')
                if stage.duration_seconds:
                    
                    logger.log(f'   Duration: {self._format_duration(stage.duration_seconds)}', 'INFO')
                if stage.error_message:
                    
                    logger.log(f'   ❌ Error: {stage.error_message}', 'INFO')
        
        logger.log(f"\n{'=' * 70}\n", 'INFO')

    def _format_status(self, status: WorkflowStatus) -> str:
        """Format status with emoji"""
        icons = {WorkflowStatus.NOT_STARTED: '⏸️  NOT STARTED', WorkflowStatus.RUNNING: '🔄 RUNNING', WorkflowStatus.COMPLETED: '✅ COMPLETED', WorkflowStatus.FAILED: '❌ FAILED', WorkflowStatus.UNKNOWN: '❓ UNKNOWN'}
        return icons.get(status, status.value.upper())

    def _get_stage_icon(self, status: StageStatus) -> str:
        """Get emoji for stage status"""
        icons = {StageStatus.PENDING: '⏸️', StageStatus.IN_PROGRESS: '🔄', StageStatus.COMPLETED: '✅', StageStatus.FAILED: '❌', StageStatus.SKIPPED: '⏭️'}
        return icons.get(status, '❓')

    def _format_progress_bar(self, percentage: int) -> str:
        """Create a visual progress bar"""
        bar_length = 40
        filled = int(bar_length * percentage / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        return f'[{bar}] {percentage}%'

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f'{seconds:.1f}s'
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f'{minutes}m {secs}s'
        else:
            hours = int(seconds / 3600)
            minutes = int(seconds % 3600 / 60)
            return f'{hours}h {minutes}m'

    def list_active_workflows(self):
        """List all active workflows"""
        
        logger.log(f"\n{'=' * 70}", 'INFO')
        
        logger.log('🏹 ACTIVE ARTEMIS WORKFLOWS', 'INFO')
        
        logger.log(f"{'=' * 70}\n", 'INFO')
        status_files = list(self.status_dir.glob('*.json'))
        if not status_files:
            
            logger.log('No active workflows found.\n', 'INFO')
            return
        for status_file in sorted(status_files):
            card_id = status_file.stem
            workflow = self.get_workflow_status(card_id)
            if workflow.status in [WorkflowStatus.RUNNING, WorkflowStatus.FAILED]:
                status_str = self._format_status(workflow.status)
                progress = f'{workflow.progress_percentage}%' if workflow.progress_percentage > 0 else 'N/A'
                
                logger.log(f'📋 {card_id}', 'INFO')
                
                logger.log(f'   Title: {workflow.title}', 'INFO')
                
                logger.log(f'   Status: {status_str}', 'INFO')
                
                logger.log(f'   Progress: {progress}', 'INFO')
                if workflow.current_stage:
                    
                    logger.log(f'   Current: {workflow.current_stage}', 'INFO')
                
                pass
        
        logger.log(f"{'=' * 70}\n", 'INFO')

def main():
    """Main entry point for CLI"""
    import argparse
    parser = argparse.ArgumentParser(description='Query Artemis workflow status', formatter_class=argparse.RawDescriptionHelpFormatter, epilog='\nExamples:\n  # Show status for a specific card\n  python3 artemis_status.py --card-id card-20251022065323\n\n  # Show status in JSON format\n  python3 artemis_status.py --card-id card-20251022065323 --json\n\n  # List all active workflows\n  python3 artemis_status.py --list\n        ')
    parser.add_argument('--card-id', help='Card ID to query status for')
    parser.add_argument('--list', action='store_true', help='List all active workflows')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()
    query = ArtemisStatusQuery(verbose=args.verbose)
    if args.list:
        query.list_active_workflows()
    elif args.card_id:
        query.display_status(args.card_id, json_output=args.json)
    else:
        parser.print_help()
        sys.exit(1)
if __name__ == '__main__':
    main()