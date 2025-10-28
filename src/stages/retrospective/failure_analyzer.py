#!/usr/bin/env python3
"""
Failure Analyzer - What Didn't Go Well Analysis

WHY: Analyze sprint failures to identify improvement opportunities
RESPONSIBILITY: Identify and categorize what didn't go well during sprint
PATTERNS: Single Responsibility, Guard Clauses, List Comprehensions
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Any

from artemis_stage_interface import LoggerInterface
from llm_client import LLMClient, LLMMessage

from .retrospective_models import RetrospectiveItem, SprintMetrics


@lru_cache(maxsize=1)
def _load_failure_analysis_prompt() -> str:
    """
    Load failure analysis prompt from dedicated file.

    WHY: Centralize prompts in files for easy maintenance
    PATTERNS: Guard clauses, early returns, fallback handling

    Returns:
        Failure analysis prompt template
    """
    prompt_file = Path(__file__).parent.parent.parent.parent / "prompts" / "retrospective_failure_analysis_prompt.md"

    # Guard: File doesn't exist
    if not prompt_file.exists():
        # Fallback to embedded prompt for backward compatibility
        return """# Retrospective: Sprint Failure Analysis

**System Role:** You are a Scrum Master conducting a sprint retrospective.

**Task:** Analyze this sprint data and identify what didn't go well:

{sprint_data}

**Focus Areas:**
- Process bottlenecks
- Communication gaps
- Technical challenges
- Estimation accuracy

**Response Format (JSON only):**
```json
{{
    "failures": [
        {{
            "description": "Clear description",
            "impact": "high | medium | low",
            "frequency": "recurring | one-time",
            "suggested_action": "Actionable improvement"
        }}
    ]
}}
```

Return ONLY valid JSON, no markdown, no explanations."""

    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


class FailureAnalyzer:
    """
    Analyze what didn't go well during sprint

    WHY: Identify improvement opportunities
    RESPONSIBILITY: Categorize failures and suggest remediation
    PATTERNS: Single Responsibility, Guard Clauses
    """

    def __init__(self, llm_client: LLMClient, logger: LoggerInterface):
        """
        Initialize Failure Analyzer

        Args:
            llm_client: LLM client for qualitative analysis
            logger: Logger interface

        WHY: Dependency injection for testability
        """
        self.llm_client = llm_client
        self.logger = logger

    def analyze_failures(
        self,
        sprint_data: Dict[str, Any],
        metrics: SprintMetrics
    ) -> List[RetrospectiveItem]:
        """
        Analyze what didn't go well using metrics and LLM

        Args:
            sprint_data: Raw sprint execution data
            metrics: Calculated sprint metrics

        Returns:
            List of failure items with suggested actions

        WHY: Combine rule-based and AI analysis
        RESPONSIBILITY: Generate comprehensive failure list
        PATTERNS: Guard clauses, List comprehensions
        """
        failures = []

        # Rule-based failures
        failures.extend(self._analyze_velocity_failure(metrics))
        failures.extend(self._analyze_bug_backlog_failure(metrics))
        failures.extend(self._analyze_code_review_failure(metrics))
        failures.extend(self._analyze_blocker_failure(metrics))

        # LLM-based qualitative analysis
        llm_failures = self._llm_analyze_failures(sprint_data)
        failures.extend(llm_failures)

        return failures

    def _analyze_velocity_failure(self, metrics: SprintMetrics) -> List[RetrospectiveItem]:
        """
        Analyze low velocity issues

        WHY: Low velocity indicates planning or execution problems
        RESPONSIBILITY: Generate velocity-related failure items
        PATTERNS: Guard clause
        """
        # Guard: Only report if velocity is low
        if metrics.velocity >= 70:
            return []

        frequency = "recurring" if metrics.velocity < 70 else "one-time"

        return [RetrospectiveItem(
            category="what_didnt_go_well",
            description=f"Low velocity: Only {metrics.velocity:.0f}% of planned work completed",
            impact="high",
            frequency=frequency,
            suggested_action="Review estimation accuracy and capacity planning"
        )]

    def _analyze_bug_backlog_failure(self, metrics: SprintMetrics) -> List[RetrospectiveItem]:
        """
        Analyze bug backlog growth

        WHY: Growing bug backlog indicates quality issues
        RESPONSIBILITY: Generate bug-related failure items
        PATTERNS: Guard clause
        """
        # Guard: Only report if bugs are accumulating
        if metrics.bugs_found <= metrics.bugs_fixed:
            return []

        return [RetrospectiveItem(
            category="what_didnt_go_well",
            description=f"Bug backlog increased: {metrics.bugs_found} found, {metrics.bugs_fixed} fixed",
            impact="medium",
            frequency="recurring",
            suggested_action="Allocate more time for bug fixes in next sprint"
        )]

    def _analyze_code_review_failure(self, metrics: SprintMetrics) -> List[RetrospectiveItem]:
        """
        Analyze excessive code review iterations

        WHY: High iterations indicate code quality or standards issues
        RESPONSIBILITY: Generate code review failure items
        PATTERNS: Guard clause
        """
        # Guard: Only report if iterations are high
        if metrics.code_review_iterations <= 3:
            return []

        return [RetrospectiveItem(
            category="what_didnt_go_well",
            description=f"High code review iterations: {metrics.code_review_iterations} average",
            impact="medium",
            frequency="recurring",
            suggested_action="Improve code quality standards and pre-review checklists"
        )]

    def _analyze_blocker_failure(self, metrics: SprintMetrics) -> List[RetrospectiveItem]:
        """
        Analyze blocker issues

        WHY: Multiple blockers indicate dependency or planning problems
        RESPONSIBILITY: Generate blocker-related failure items
        PATTERNS: Guard clause
        """
        # Guard: Only report if multiple blockers
        if metrics.blockers_encountered <= 2:
            return []

        return [RetrospectiveItem(
            category="what_didnt_go_well",
            description=f"Multiple blockers: {metrics.blockers_encountered} encountered",
            impact="high",
            frequency="recurring",
            suggested_action="Identify and address dependency issues in planning"
        )]

    def _llm_analyze_failures(self, sprint_data: Dict[str, Any]) -> List[RetrospectiveItem]:
        """
        Use LLM to identify qualitative failures

        Args:
            sprint_data: Raw sprint data

        Returns:
            List of LLM-identified failures with suggested actions

        WHY: Capture qualitative insights beyond metrics
        RESPONSIBILITY: AI-powered failure pattern detection
        PATTERNS: Guard clause, Error handling
        """
        # Load prompt template and format with sprint data
        prompt_template = _load_failure_analysis_prompt()
        prompt = prompt_template.format(
            sprint_data=json.dumps(sprint_data, indent=2)
        )

        try:
            messages = [
                LLMMessage(role="system", content="You are a Scrum Master conducting a sprint retrospective."),
                LLMMessage(role="user", content=prompt)
            ]

            llm_response = self.llm_client.complete(
                messages=messages,
                response_format={"type": "json_object"}
            )

            data = json.loads(llm_response.content)

            # List comprehension for transformation
            return [
                RetrospectiveItem(
                    category="what_didnt_go_well",
                    description=item['description'],
                    impact=item['impact'],
                    frequency=item['frequency'],
                    suggested_action=item.get('suggested_action')
                )
                for item in data.get('failures', [])
            ]

        except Exception as e:
            self.logger.log(f"Error in LLM failure analysis: {e}", "ERROR")
            return []
