#!/usr/bin/env python3
"""
WHY: Use LLM to generate solutions for novel failure modes
RESPONSIBILITY: LLM consultation, prompt building, response parsing
PATTERNS: Strategy (learning strategy), Template Method (prompt building)
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import UnexpectedState, LearnedSolution, LearningStrategy


class LLMPromptBuilder:
    """
    WHY: Generate effective prompts for LLM problem-solving
    RESPONSIBILITY: Build structured prompts with context and constraints
    PATTERNS: Builder pattern (prompt construction)
    """

    @staticmethod
    def build_recovery_prompt(unexpected_state: UnexpectedState) -> str:
        """
        WHY: Create detailed, structured prompts for LLM consultation
        RESPONSIBILITY: Format unexpected state into actionable LLM query
        PATTERNS: Template Method
        """
        prompt = f"""You are an expert DevOps/SRE engineer helping debug an autonomous AI development pipeline called Artemis.

UNEXPECTED STATE DETECTED:

Current State: {unexpected_state.current_state}
Expected States: {', '.join(unexpected_state.expected_states)}
Severity: {unexpected_state.severity}

CONTEXT:
Card ID: {unexpected_state.card_id}
Stage: {unexpected_state.stage_name or 'Unknown'}
Previous State: {unexpected_state.previous_state or 'Unknown'}

ERROR INFORMATION:
{unexpected_state.error_message or 'No error message'}

ADDITIONAL CONTEXT:
{json.dumps(unexpected_state.context, indent=2)}

TASK:
Analyze this unexpected state and provide a step-by-step recovery workflow to fix the problem.

Your response MUST be in the following JSON format:

{{
  "problem_analysis": "Brief analysis of what went wrong",
  "root_cause": "Most likely root cause",
  "solution_description": "High-level description of the fix",
  "workflow_steps": [
    {{
      "step": 1,
      "action": "action_type",
      "description": "What this step does",
      "parameters": {{"key": "value"}}
    }},
    ...
  ],
  "confidence": "high|medium|low",
  "risks": ["potential risk 1", "potential risk 2"],
  "alternative_approaches": ["alternative 1", "alternative 2"]
}}

AVAILABLE ACTIONS:
- "retry_stage": Retry the failed stage
- "rollback_to_state": Rollback to a previous state
- "skip_stage": Skip the current stage
- "reset_state": Reset to a clean state
- "cleanup_resources": Clean up stuck resources
- "restart_process": Restart a stuck process
- "manual_intervention": Request human intervention

Provide a practical, actionable recovery workflow.
"""
        return prompt


class LLMResponseParser:
    """
    WHY: Extract structured workflow from LLM responses
    RESPONSIBILITY: Parse JSON/text responses into workflow steps
    PATTERNS: Strategy (parsing strategies), Guard Clause
    """

    @staticmethod
    def parse_llm_response(llm_response: str) -> List[Dict[str, Any]]:
        """
        WHY: Convert LLM text into executable workflow steps
        RESPONSIBILITY: Parse JSON or extract steps from text
        PATTERNS: Guard Clause (JSON parsing), fallback strategy
        """
        try:
            # Try to parse as JSON
            response_data = json.loads(llm_response)

            # Guard: Has workflow_steps field
            if "workflow_steps" in response_data:
                return response_data["workflow_steps"]

            # Fallback to text extraction
            return LLMResponseParser._extract_workflow_from_text(llm_response)

        except json.JSONDecodeError:
            # Not JSON, extract from text
            return LLMResponseParser._extract_workflow_from_text(llm_response)

    @staticmethod
    def _extract_workflow_from_text(text: str) -> List[Dict[str, Any]]:
        """
        WHY: Handle unstructured LLM responses
        RESPONSIBILITY: Extract numbered steps from text
        PATTERNS: Pattern matching (numbered steps)
        """
        steps = []
        lines = text.split('\n')

        for line in lines:
            # Look for patterns like "1. ", "2. ", "Step 1:", etc.
            if any(pattern in line.lower() for pattern in ["1.", "2.", "3.", "step 1", "step 2"]):
                steps.append({
                    "step": len(steps) + 1,
                    "action": "manual_intervention",  # Default to manual
                    "description": line.strip(),
                    "parameters": {}
                })

        # Guard: No steps found, create default manual intervention
        if not steps:
            return [
                {
                    "step": 1,
                    "action": "manual_intervention",
                    "description": "Consult LLM response for guidance",
                    "parameters": {"llm_response": text[:500]}
                }
            ]

        return steps

    @staticmethod
    def extract_solution_description(llm_response: str) -> str:
        """
        WHY: Get concise solution summary from LLM response
        RESPONSIBILITY: Extract solution_description field or first sentence
        """
        try:
            data = json.loads(llm_response)
            return data.get("solution_description", "LLM-generated solution")
        except json.JSONDecodeError:
            # Extract first sentence or first 100 chars
            return llm_response.split('.')[0][:100]


class LLMConsultationStrategy:
    """
    WHY: Implement LLM-based learning strategy
    RESPONSIBILITY: Consult LLM and create learned solutions
    PATTERNS: Strategy (learning approach), Template Method (consultation flow)
    """

    def __init__(self, llm_client: Optional[Any], verbose: bool = True):
        self.llm_client = llm_client
        self.verbose = verbose
        self.consultation_count = 0

    def consult_llm_for_solution(
        self,
        unexpected_state: UnexpectedState
    ) -> Optional[LearnedSolution]:
        """
        WHY: Generate novel solutions using LLM reasoning
        RESPONSIBILITY: Query LLM, parse response, create LearnedSolution
        PATTERNS: Guard Clause (client availability), Template Method

        Args:
            unexpected_state: The unexpected state

        Returns:
            LearnedSolution from LLM or None if failed
        """
        # Guard: No LLM client available
        if not self.llm_client:
            if self.verbose:
                print(f"[Learning] ⚠️  No LLM client available for consultation")
            return None

        self.consultation_count += 1

        # Build prompt
        prompt = LLMPromptBuilder.build_recovery_prompt(unexpected_state)

        if self.verbose:
            print(f"[Learning] 💬 Consulting LLM for solution...")

        try:
            # Query LLM
            from llm_client import LLMMessage
            messages = [LLMMessage(role="user", content=prompt)]
            response = self.llm_client.complete(messages, max_tokens=2000, temperature=0.7)

            # Parse response
            workflow_steps = LLMResponseParser.parse_llm_response(response.content)
            solution_description = LLMResponseParser.extract_solution_description(response.content)

            # Create learned solution
            solution = LearnedSolution(
                solution_id=f"learned-{unexpected_state.state_id}",
                timestamp=datetime.utcnow().isoformat() + 'Z',
                unexpected_state_id=unexpected_state.state_id,
                problem_description=self._describe_problem(unexpected_state),
                solution_description=solution_description,
                workflow_steps=workflow_steps,
                success_rate=0.0,  # Unknown yet
                times_applied=0,
                times_successful=0,
                learning_strategy=LearningStrategy.LLM_CONSULTATION.value,
                llm_model_used=getattr(response, 'model', 'unknown'),
                human_validated=False,
                metadata={
                    "llm_tokens_input": getattr(response.usage, 'prompt_tokens', 0),
                    "llm_tokens_output": getattr(response.usage, 'completion_tokens', 0),
                    "llm_response_raw": response.content
                }
            )

            if self.verbose:
                print(f"[Learning] ✅ Solution learned from LLM!")
                print(f"[Learning]    Solution ID: {solution.solution_id}")
                print(f"[Learning]    Workflow steps: {len(solution.workflow_steps)}")

            return solution

        except Exception as e:
            if self.verbose:
                print(f"[Learning] ❌ LLM consultation failed: {e}")
            return None

    def _describe_problem(self, unexpected_state: UnexpectedState) -> str:
        """Generate problem description"""
        from .pattern_recognition import ProblemDescriptor
        return ProblemDescriptor.describe_problem(unexpected_state)
