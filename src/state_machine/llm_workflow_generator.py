#!/usr/bin/env python3
"""
WHY: Generate recovery workflows dynamically using LLM when no predefined workflow exists
RESPONSIBILITY: Consult LLM to create custom workflows, parse responses, build workflow objects
PATTERNS: Builder pattern for workflow construction, strategy pattern for generation
"""

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

    def __init__(self, llm_client: Optional[Any] = None, verbose: bool = True) -> None:
        """
        Initialize LLM workflow generator

        Args:
            llm_client: LLM client for workflow generation
            verbose: Enable verbose logging
        """
        self.llm_client = llm_client
        self.verbose = verbose

    def generate_workflow(
        self,
        issue_type: IssueType,
        context: Dict[str, Any]
    ) -> Optional[Workflow]:
        """
        Generate a recovery workflow using LLM

        Args:
            issue_type: Type of issue needing a workflow
            context: Context about the issue

        Returns:
            Generated Workflow if successful, None otherwise
        """
        # Guard: Check LLM client available
        if not self.llm_client:
            self._log_no_llm_client()
            return None

        if self.verbose:
            print(f"[LLMWorkflowGenerator] 🤖 Consulting LLM for {issue_type.value}...")

        try:
            workflow = self._generate_workflow_with_llm(issue_type, context)
            if workflow and self.verbose:
                print(f"[LLMWorkflowGenerator] ✅ Generated '{workflow.name}' with {len(workflow.actions)} actions")
            return workflow

        except Exception as e:
            if self.verbose:
                print(f"[LLMWorkflowGenerator] ❌ Failed to generate workflow: {e}")
            return None

    def _generate_workflow_with_llm(
        self,
        issue_type: IssueType,
        context: Dict[str, Any]
    ) -> Optional[Workflow]:
        """Generate workflow using LLM"""
        llm_response = self._get_llm_workflow_response(issue_type, context)
        workflow_data = self._parse_llm_workflow_response(llm_response)

        # Guard: Check parsing succeeded
        if not workflow_data:
            return None

        return self._build_workflow_from_data(workflow_data, issue_type)

    def _get_llm_workflow_response(
        self,
        issue_type: IssueType,
        context: Dict[str, Any]
    ) -> str:
        """Get LLM response for workflow generation"""
        system_message = self._build_system_message()
        user_message = self._build_user_message(issue_type, context)

        from llm_client import LLMMessage
        messages = [
            LLMMessage(role="system", content=system_message),
            LLMMessage(role="user", content=user_message)
        ]

        llm_response = self.llm_client.complete(
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )
        return llm_response.content

    def _build_system_message(self) -> str:
        """Build system message for LLM"""
        return """You are an expert in designing recovery workflows for software pipelines.
When given an issue type and context, you generate a step-by-step recovery workflow in JSON format."""

    def _build_user_message(
        self,
        issue_type: IssueType,
        context: Dict[str, Any]
    ) -> str:
        """Build user message for LLM"""
        context_str = "\n".join(f"- {k}: {v}" for k, v in context.items() if v is not None)

        return f"""Generate a recovery workflow for the following issue:

Issue Type: {issue_type.value}
Context:
{context_str}

Provide a recovery workflow in JSON format:
{{
  "workflow_name": "Brief descriptive name",
  "description": "What this workflow does",
  "actions": [
    {{
      "action_name": "retry_with_backoff",
      "description": "What this action does",
      "max_attempts": 3,
      "parameters": {{"backoff_seconds": 60}}
    }}
  ],
  "success_state": "STAGE_RUNNING",
  "failure_state": "STAGE_FAILED",
  "rollback_on_failure": false
}}

Available actions: retry_with_backoff, reset_state, skip_stage, use_cached_result, fallback_to_default
Available states: IDLE, INITIALIZING, RUNNING, PAUSED, COMPLETED, FAILED, STAGE_RUNNING, STAGE_FAILED"""

    def _parse_llm_workflow_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON workflow from LLM response"""
        json_match = re.search(r'\{.*\}', response, re.DOTALL)

        # Guard: Check JSON found
        if not json_match:
            self._log_no_json_in_response()
            return None

        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            if self.verbose:
                print(f"[LLMWorkflowGenerator] ⚠️  Failed to parse JSON from LLM response")
            return None

    def _build_workflow_from_data(
        self,
        workflow_data: Dict[str, Any],
        issue_type: IssueType
    ) -> Workflow:
        """Build Workflow object from parsed data"""
        actions = self._build_actions_from_data(workflow_data)
        success_state = self._parse_state(workflow_data.get("success_state", "STAGE_RUNNING"))
        failure_state = self._parse_state(workflow_data.get("failure_state", "STAGE_FAILED"))

        return Workflow(
            name=workflow_data.get("workflow_name", f"LLM-generated-{issue_type.value}"),
            issue_type=issue_type,
            actions=actions,
            success_state=success_state,
            failure_state=failure_state,
            rollback_on_failure=workflow_data.get("rollback_on_failure", False)
        )

    def _build_actions_from_data(self, workflow_data: Dict[str, Any]) -> list:
        """Build list of WorkflowAction objects from data"""
        actions = []
        for action_data in workflow_data.get("actions", []):
            actions.append(WorkflowAction(
                action_name=action_data.get("action_name", "retry_with_backoff"),
                handler=lambda ctx: True,  # Placeholder handler
                max_retries=action_data.get("max_attempts", 1)
            ))
        return actions

    def _parse_state(self, state_str: str) -> PipelineState:
        """Parse state string to PipelineState enum"""
        if state_str in PipelineState.__members__:
            return PipelineState[state_str]
        return PipelineState.RUNNING  # Safe default

    def _log_no_llm_client(self) -> None:
        """Log warning when no LLM client available"""
        if self.verbose:
            print(f"[LLMWorkflowGenerator] ⚠️  Cannot generate workflow - no LLM client available")

    def _log_no_json_in_response(self) -> None:
        """Log warning when no JSON in LLM response"""
        if self.verbose:
            print(f"[LLMWorkflowGenerator] ⚠️  LLM response did not contain valid JSON")
