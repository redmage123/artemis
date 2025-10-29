from artemis_logger import get_logger
logger = get_logger('llm_workflow_generator')
'\nWHY: Generate recovery workflows dynamically using LLM when no predefined workflow exists\nRESPONSIBILITY: Consult LLM to create custom workflows, parse responses, build workflow objects\nPATTERNS: Builder pattern for workflow construction, strategy pattern for generation\n'
import json
import re
from typing import Dict, Any, Optional
from state_machine.issue_type import IssueType
from state_machine.pipeline_state import PipelineState
from state_machine.workflow import Workflow
from state_machine.workflow_action import WorkflowAction

class LLMWorkflowGenerator:
    """
    Generates recovery workflows using LLM when no registered workflow exists

    Features:
    - LLM-based workflow synthesis
    - JSON parsing and validation
    - Workflow object construction
    - Fallback to safe defaults
    """

    def __init__(self, llm_client: Optional[Any]=None, verbose: bool=True) -> None:
        """
        Initialize LLM workflow generator

        Args:
            llm_client: LLM client for workflow generation
            verbose: Enable verbose logging
        """
        self.llm_client = llm_client
        self.verbose = verbose

    def generate_workflow(self, issue_type: IssueType, context: Dict[str, Any]) -> Optional[Workflow]:
        """
        Generate a recovery workflow using LLM

        Args:
            issue_type: Type of issue needing a workflow
            context: Context about the issue

        Returns:
            Generated Workflow if successful, None otherwise
        """
        if not self.llm_client:
            self._log_no_llm_client()
            return None
        if self.verbose:
            
            logger.log(f'[LLMWorkflowGenerator] 🤖 Consulting LLM for {issue_type.value}...', 'INFO')
        try:
            workflow = self._generate_workflow_with_llm(issue_type, context)
            if workflow and self.verbose:
                
                logger.log(f"[LLMWorkflowGenerator] ✅ Generated '{workflow.name}' with {len(workflow.actions)} actions", 'INFO')
            return workflow
        except Exception as e:
            if self.verbose:
                
                logger.log(f'[LLMWorkflowGenerator] ❌ Failed to generate workflow: {e}', 'INFO')
            return None

    def _generate_workflow_with_llm(self, issue_type: IssueType, context: Dict[str, Any]) -> Optional[Workflow]:
        """Generate workflow using LLM"""
        llm_response = self._get_llm_workflow_response(issue_type, context)
        workflow_data = self._parse_llm_workflow_response(llm_response)
        if not workflow_data:
            return None
        return self._build_workflow_from_data(workflow_data, issue_type)

    def _get_llm_workflow_response(self, issue_type: IssueType, context: Dict[str, Any]) -> str:
        """Get LLM response for workflow generation"""
        system_message = self._build_system_message()
        user_message = self._build_user_message(issue_type, context)
        from llm_client import LLMMessage
        messages = [LLMMessage(role='system', content=system_message), LLMMessage(role='user', content=user_message)]
        llm_response = self.llm_client.complete(messages=messages, temperature=0.3, max_tokens=1500)
        return llm_response.content

    def _build_system_message(self) -> str:
        """Build system message for LLM"""
        return 'You are an expert in designing recovery workflows for software pipelines.\nWhen given an issue type and context, you generate a step-by-step recovery workflow in JSON format.'

    def _build_user_message(self, issue_type: IssueType, context: Dict[str, Any]) -> str:
        """Build user message for LLM"""
        context_str = '\n'.join((f'- {k}: {v}' for k, v in context.items() if v is not None))
        return f'Generate a recovery workflow for the following issue:\n\nIssue Type: {issue_type.value}\nContext:\n{context_str}\n\nProvide a recovery workflow in JSON format:\n{{\n  "workflow_name": "Brief descriptive name",\n  "description": "What this workflow does",\n  "actions": [\n    {{\n      "action_name": "retry_with_backoff",\n      "description": "What this action does",\n      "max_attempts": 3,\n      "parameters": {{"backoff_seconds": 60}}\n    }}\n  ],\n  "success_state": "STAGE_RUNNING",\n  "failure_state": "STAGE_FAILED",\n  "rollback_on_failure": false\n}}\n\nAvailable actions: retry_with_backoff, reset_state, skip_stage, use_cached_result, fallback_to_default\nAvailable states: IDLE, INITIALIZING, RUNNING, PAUSED, COMPLETED, FAILED, STAGE_RUNNING, STAGE_FAILED'

    def _parse_llm_workflow_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON workflow from LLM response"""
        json_match = re.search('\\{.*\\}', response, re.DOTALL)
        if not json_match:
            self._log_no_json_in_response()
            return None
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            if self.verbose:
                
                logger.log(f'[LLMWorkflowGenerator] ⚠️  Failed to parse JSON from LLM response', 'INFO')
            return None

    def _build_workflow_from_data(self, workflow_data: Dict[str, Any], issue_type: IssueType) -> Workflow:
        """Build Workflow object from parsed data"""
        actions = self._build_actions_from_data(workflow_data)
        success_state = self._parse_state(workflow_data.get('success_state', 'STAGE_RUNNING'))
        failure_state = self._parse_state(workflow_data.get('failure_state', 'STAGE_FAILED'))
        return Workflow(name=workflow_data.get('workflow_name', f'LLM-generated-{issue_type.value}'), issue_type=issue_type, actions=actions, success_state=success_state, failure_state=failure_state, rollback_on_failure=workflow_data.get('rollback_on_failure', False))

    def _build_actions_from_data(self, workflow_data: Dict[str, Any]) -> list:
        """Build list of WorkflowAction objects from data"""
        actions = []
        for action_data in workflow_data.get('actions', []):
            actions.append(WorkflowAction(action_name=action_data.get('action_name', 'retry_with_backoff'), handler=lambda ctx: True, max_retries=action_data.get('max_attempts', 1)))
        return actions

    def _parse_state(self, state_str: str) -> PipelineState:
        """Parse state string to PipelineState enum"""
        if state_str in PipelineState.__members__:
            return PipelineState[state_str]
        return PipelineState.RUNNING

    def _log_no_llm_client(self) -> None:
        """Log warning when no LLM client available"""
        if self.verbose:
            
            logger.log(f'[LLMWorkflowGenerator] ⚠️  Cannot generate workflow - no LLM client available', 'INFO')

    def _log_no_json_in_response(self) -> None:
        """Log warning when no JSON in LLM response"""
        if self.verbose:
            
            logger.log(f'[LLMWorkflowGenerator] ⚠️  LLM response did not contain valid JSON', 'INFO')