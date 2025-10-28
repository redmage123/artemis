#!/usr/bin/env python3
"""
Success Analyzer - What Went Well Analysis

WHY: Analyze sprint successes to identify patterns
RESPONSIBILITY: Identify and categorize what went well during sprint
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
def _load_success_analysis_prompt() -> str:
    """
    Load success analysis prompt from dedicated file.

    WHY: Centralize prompts in files for easy maintenance
    PATTERNS: Guard clauses, early returns, fallback handling

    Returns:
        Success analysis prompt template
    """
    prompt_file = Path(__file__).parent.parent.parent.parent / "prompts" / "retrospective_success_analysis_prompt.md"

    # Guard: File doesn't exist
    if not prompt_file.exists():
        # Fallback to embedded prompt for backward compatibility
        return """# Retrospective: Sprint Success Analysis

**System Role:** You are a Scrum Master conducting a sprint retrospective.

**Task:** Analyze this sprint data and identify what went well:

{sprint_data}

**Focus Areas:**
- Team collaboration
- Process improvements
- Technical achievements
- Communication effectiveness

**Response Format (JSON only):**
```json
{{
    "successes": [
        {{
            "description": "Clear description",
            "impact": "high | medium | low",
            "frequency": "recurring | one-time"
        }}
    ]
}}
```

Return ONLY valid JSON, no markdown, no explanations."""

    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


class SuccessAnalyzer:
    """
    Analyze what went well during sprint

    WHY: Separate success analysis from failure analysis
    RESPONSIBILITY: Identify positive patterns and achievements
    PATTERNS: Single Responsibility, Guard Clauses
    """

    def __init__(self, llm_client: LLMClient, logger: LoggerInterface):
        """
        Initialize Success Analyzer

        Args:
            llm_client: LLM client for qualitative analysis
            logger: Logger interface

        WHY: Dependency injection for testability
        """
        self.llm_client = llm_client
        self.logger = logger

    def analyze_successes(
        self,
        sprint_data: Dict[str, Any],
        metrics: SprintMetrics
    ) -> List[RetrospectiveItem]:
        """
        Analyze what went well using metrics and LLM

        Args:
            sprint_data: Raw sprint execution data
            metrics: Calculated sprint metrics

        Returns:
            List of success items

        WHY: Combine rule-based and AI analysis
        RESPONSIBILITY: Generate comprehensive success list
        PATTERNS: Guard clauses, List comprehensions
        """
        successes = []

        # Rule-based successes
        successes.extend(self._analyze_velocity_success(metrics))
        successes.extend(self._analyze_test_quality_success(metrics))
        successes.extend(self._analyze_blocker_success(metrics))

        # LLM-based qualitative analysis
        llm_successes = self._llm_analyze_successes(sprint_data)
        successes.extend(llm_successes)

        return successes

    def _analyze_velocity_success(self, metrics: SprintMetrics) -> List[RetrospectiveItem]:
        """
        Analyze velocity achievements

        WHY: Velocity is key sprint success indicator
        RESPONSIBILITY: Generate velocity-related success items
        PATTERNS: Guard clause (early return)
        """
        # Guard: Only report if velocity is high
        if metrics.velocity < 90:
            return []

        frequency = "recurring" if metrics.velocity >= 90 else "one-time"

        return [RetrospectiveItem(
            category="what_went_well",
            description=f"Excellent velocity: {metrics.velocity:.0f}% of planned work completed",
            impact="high",
            frequency=frequency,
            suggested_action="Maintain current sprint planning accuracy"
        )]

    def _analyze_test_quality_success(self, metrics: SprintMetrics) -> List[RetrospectiveItem]:
        """
        Analyze test quality achievements

        WHY: Test quality indicates code health
        RESPONSIBILITY: Generate test-quality success items
        PATTERNS: Guard clause
        """
        # Guard: Only report if test quality is high
        if metrics.tests_passing < 95:
            return []

        return [RetrospectiveItem(
            category="what_went_well",
            description=f"High test quality: {metrics.tests_passing:.0f}% tests passing",
            impact="high",
            frequency="recurring",
            suggested_action="Continue strong testing practices"
        )]

    def _analyze_blocker_success(self, metrics: SprintMetrics) -> List[RetrospectiveItem]:
        """
        Analyze blocker avoidance

        WHY: Absence of blockers indicates smooth execution
        RESPONSIBILITY: Generate blocker-avoidance success items
        PATTERNS: Guard clause
        """
        # Guard: Only report if no blockers
        if metrics.blockers_encountered != 0:
            return []

        return [RetrospectiveItem(
            category="what_went_well",
            description="No blockers encountered during sprint",
            impact="medium",
            frequency="one-time",
            suggested_action="Document factors that prevented blockers"
        )]

    def _llm_analyze_successes(self, sprint_data: Dict[str, Any]) -> List[RetrospectiveItem]:
        """
        Use LLM to identify qualitative successes

        Args:
            sprint_data: Raw sprint data

        Returns:
            List of LLM-identified successes

        WHY: Capture qualitative insights beyond metrics
        RESPONSIBILITY: AI-powered success pattern detection
        PATTERNS: Guard clause, Error handling
        """
        # Load prompt template and format with sprint data
        prompt_template = _load_success_analysis_prompt()
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
                    category="what_went_well",
                    description=item['description'],
                    impact=item['impact'],
                    frequency=item['frequency']
                )
                for item in data.get('successes', [])
            ]

        except Exception as e:
            self.logger.log(f"Error in LLM success analysis: {e}", "ERROR")
            return []
