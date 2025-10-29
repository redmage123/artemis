#!/usr/bin/env python3
"""
WHY: LLM-powered comprehensive analysis using DEPTH framework
RESPONSIBILITY: Provide intelligent, context-aware analysis beyond rule-based detection
PATTERNS: DEPTH framework, KG-First approach for token savings, guard clauses

This module implements LLM-powered analysis that complements rule-based analyzers
with deeper insights, using the DEPTH framework (Define, Establish, Provide, Task, Human).
Uses AIQueryService for KG-First approach to reduce token usage (~750 tokens/task).
"""

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from artemis_logger import get_logger
from environment_context import get_environment_context_short

from project_analysis.interfaces import DimensionAnalyzer
from project_analysis.models import AnalysisResult, Issue, Severity

# Module-level logger
logger = get_logger(__name__)

# Import AIQueryService for centralized KG→RAG→LLM pipeline
try:
    from ai_query_service import AIQueryResult, QueryType
    AI_QUERY_SERVICE_AVAILABLE = True
except ImportError:
    AI_QUERY_SERVICE_AVAILABLE = False


@lru_cache(maxsize=1)
def _load_project_analysis_system_prompt() -> str:
    """
    Load project analysis system prompt from dedicated file.

    WHY: Centralize prompts in files for easy maintenance
    PATTERNS: Guard clauses, early returns, fallback handling

    Returns:
        System prompt template for project analysis
    """
    prompt_file = Path(__file__).parent.parent.parent / "prompts" / "project_analysis_system_prompt.md"

    # Guard: File doesn't exist
    if not prompt_file.exists():
        # Fallback to embedded prompt for backward compatibility
        return """You are an expert Project Analysis AI specializing in identifying issues before implementation.

**Multiple Expert Perspectives:**
Apply the viewpoints of:
- Senior Software Architect (15+ years) - focusing on architectural soundness and scalability
- Security Engineer - identifying potential vulnerabilities and compliance issues
- QA Lead - considering testability, edge cases, and quality assurance
- DevOps Engineer - evaluating deployment, monitoring, and operational concerns
- UX Designer - assessing user experience and accessibility requirements

**Success Criteria:**
Your analysis MUST:
1. Identify CRITICAL issues (security, compliance, data loss risks)
2. Highlight HIGH-priority improvements (testing, performance, scalability)
3. Suggest MEDIUM-priority enhancements (code quality, maintainability)
4. Provide specific, actionable recommendations (not generic advice)
5. Return valid JSON matching the expected schema
6. Avoid AI clichés like "robust", "delve", "leverage"

**Self-Validation:**
Before responding, ask yourself:
1. Did I identify all security vulnerabilities?
2. Are my recommendations specific and actionable?
3. Did I consider all edge cases and failure scenarios?
4. Is my JSON properly formatted?
5. Did I avoid generic advice and AI clichés?

If any answer is NO, revise your analysis."""

    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


@lru_cache(maxsize=1)
def _load_project_analysis_user_prompt() -> str:
    """
    Load project analysis user prompt from dedicated file.

    WHY: Centralize prompts in files for easy maintenance
    PATTERNS: Guard clauses, early returns, fallback handling

    Returns:
        User prompt template for project analysis
    """
    prompt_file = Path(__file__).parent.parent.parent / "prompts" / "project_analysis_user_prompt.md"

    # Guard: File doesn't exist
    if not prompt_file.exists():
        # Fallback to embedded prompt for backward compatibility
        return """Analyze the following task BEFORE implementation across these dimensions:

1. **Scope & Requirements**: Are requirements clear and complete?
2. **Security**: Any security vulnerabilities or compliance issues?
3. **Performance & Scalability**: Performance concerns or bottlenecks?
4. **Testing Strategy**: Is testing approach comprehensive?
5. **Error Handling**: Are edge cases and failures addressed?
6. **Architecture**: Architectural concerns or design issues?
7. **Dependencies**: External dependencies or integration risks?
8. **Accessibility**: WCAG compliance and UX considerations?

**Task Title:** {title}
**Description:** {description}
**Priority:** {priority}
**Story Points:** {points}
**Acceptance Criteria:**
{acceptance_criteria}

{context_summary}

{environment_context}

**Task Breakdown:**
1. Read the task requirements carefully
2. Analyze each dimension systematically
3. Identify issues categorized by severity (CRITICAL/HIGH/MEDIUM)
4. Provide specific, actionable recommendations
5. Self-validate your analysis before responding

**Response Format (JSON only):**
{{
  "issues": [
    {{
      "category": "Security|Performance|Testing|Architecture|Dependencies|Accessibility|Scope|Error Handling",
      "severity": "CRITICAL|HIGH|MEDIUM",
      "description": "Brief issue description",
      "impact": "What happens if not addressed",
      "suggestion": "Specific actionable fix",
      "reasoning": "Why this matters",
      "user_approval_needed": true|false
    }}
  ],
  "recommendations": [
    "Specific recommendation 1",
    "Specific recommendation 2"
  ],
  "overall_assessment": "Brief 1-2 sentence summary",
  "recommendation_action": "APPROVE_ALL|APPROVE_CRITICAL|REJECT"
}}

Return ONLY valid JSON, no markdown, no explanations."""

    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


class LLMPoweredAnalyzer(DimensionAnalyzer):
    """
    WHY: Provide intelligent analysis beyond deterministic rules
    RESPONSIBILITY: Use LLM to identify subtle issues and provide expert insights
    PATTERNS: DEPTH framework, KG-First approach, fallback handling

    LLM-Powered Comprehensive Analyzer using DEPTH Framework:
    - D: Define Multiple Perspectives (security, architecture, QA, DevOps, UX)
    - E: Establish Clear Success Metrics (severity levels, approval criteria)
    - P: Provide Context Layers (card details, RAG context, historical data)
    - T: Task Breakdown (dimension-by-dimension analysis)
    - H: Human Feedback Loop (self-critique and validation)

    Now uses AIQueryService for KG-First approach (token savings ~750 tokens/task).
    Complements rule-based analyzers with deeper, context-aware insights.
    """

    def __init__(
        self,
        llm_client: Optional[Any] = None,
        config: Optional[Any] = None,
        ai_service: Optional[Any] = None
    ):
        """
        Initialize with LLM client and optional AI service.

        Args:
            llm_client: LLM client instance (LLMClientInterface)
            config: Configuration agent for settings
            ai_service: AI Query Service for KG-First queries (optional)
        """
        self.llm_client = llm_client
        self.config = config
        self.ai_service = ai_service

    def analyze(self, card: Dict, context: Dict) -> AnalysisResult:
        """
        Analyze task using LLM with DEPTH framework.

        Guard clause: Return empty result if no LLM available.
        Uses AIQueryService for KG-First approach to reduce token usage.

        Args:
            card: Kanban card with task details
            context: Pipeline context (RAG recommendations, etc.)

        Returns:
            AnalysisResult with LLM-generated insights
        """
        # Guard clause: No LLM available
        if not self.ai_service and not self.llm_client:
            return AnalysisResult(
                dimension="LLM-Powered Analysis",
                issues=[],
                recommendations=["LLM client not available - using rule-based analysis only"]
            )

        # Build DEPTH-conforming prompt
        system_message = self._build_system_message()
        user_message = self._build_user_message(card, context)
        full_prompt = f"{system_message}\n\n{user_message}"

        try:
            response = self._get_llm_response(card, full_prompt, system_message, user_message)

            # Parse LLM response (expecting JSON)
            analysis_data = self._parse_llm_response(response)

            # Convert to AnalysisResult
            issues = self._extract_issues(analysis_data)
            recommendations = analysis_data.get("recommendations", [])

            return AnalysisResult(
                dimension="LLM-Powered Comprehensive Analysis",
                issues=issues,
                recommendations=recommendations
            )

        except Exception as e:
            # Fallback on error
            return AnalysisResult(
                dimension="LLM-Powered Analysis",
                issues=[],
                recommendations=[f"LLM analysis failed: {str(e)}"]
            )

    def _get_llm_response(
        self,
        card: Dict,
        full_prompt: str,
        system_message: str,
        user_message: str
    ) -> str:
        """
        Get LLM response using AIQueryService or fallback to direct LLM call.

        Guard clause: Use direct LLM call if AIQueryService unavailable.

        Args:
            card: Kanban card with task details
            full_prompt: Full prompt for AIQueryService
            system_message: System message for direct LLM call
            user_message: User message for direct LLM call

        Returns:
            LLM response text
        """
        # Guard clause: No AI service, use direct LLM
        if not self.ai_service:
            return self.llm_client.generate_text(
                system_message=system_message,
                user_message=user_message,
                temperature=0.3,
                max_tokens=2000
            )

        # Use AIQueryService (KG-First approach)
        keywords = card.get('title', '').lower().split()[:3]
        result = self.ai_service.query(
            query_type=QueryType.PROJECT_ANALYSIS,
            prompt=full_prompt,
            kg_query_params={
                'task_title': card.get('title', ''),
                'keywords': keywords
            },
            temperature=0.3,  # Lower temperature for analytical consistency
            max_tokens=2000
        )

        # Guard clause: Query failed
        if not result.success:
            raise Exception(f"AI query failed: {result.error}")

        return result.llm_response.content

    def _build_context_summary(self, context: Dict) -> str:
        """
        Build context summary from RAG recommendations.

        Guard clause: Return empty string if no context.

        Args:
            context: Pipeline context containing RAG recommendations

        Returns:
            Formatted context summary string
        """
        # Guard clause: No context
        if not context:
            return ""

        rag_recommendations = context.get('rag_recommendations', [])
        rag_list = self._normalize_rag_recommendations(rag_recommendations)

        # Guard clause: No RAG recommendations
        if not rag_list:
            return ""

        context_summary = "\n**Historical Context (RAG):**\n"
        for rec in rag_list[:3]:  # Top 3 recommendations
            context_summary += f"- {rec}\n"

        return context_summary

    def _normalize_rag_recommendations(self, rag_recommendations: Any) -> List:
        """
        Normalize RAG recommendations to list format.

        Handles both dict and list formats for flexibility.

        Args:
            rag_recommendations: RAG recommendations in dict or list format

        Returns:
            List of recommendations
        """
        if isinstance(rag_recommendations, dict):
            return list(rag_recommendations.values()) if rag_recommendations else []

        if isinstance(rag_recommendations, list):
            return rag_recommendations

        return []

    def get_dimension_name(self) -> str:
        """Get the name of this analysis dimension."""
        return "llm_powered"

    def _build_system_message(self) -> str:
        """
        Build system message with DEPTH framework.

        Defines multiple expert perspectives and success criteria.
        Now loads from dedicated prompt file for easy maintenance.

        Returns:
            System message for LLM
        """
        return _load_project_analysis_system_prompt()

    def _build_user_message(self, card: Dict, context: Dict) -> str:
        """
        Build user message with context layers.

        Provides comprehensive task context and analysis dimensions.
        Now loads from dedicated prompt file for easy maintenance.

        Args:
            card: Kanban card with task details
            context: Pipeline context

        Returns:
            User message for LLM
        """
        context_summary = self._build_context_summary(context)

        # Load prompt template and format with variables
        prompt_template = _load_project_analysis_user_prompt()
        return prompt_template.format(
            title=card.get('title', 'Unknown'),
            description=card.get('description', 'No description provided'),
            priority=card.get('priority', 'Not set'),
            points=card.get('points', 'Not estimated'),
            acceptance_criteria=card.get('acceptance_criteria', []),
            context_summary=context_summary,
            environment_context=get_environment_context_short()
        )

    def _parse_llm_response(self, response: str) -> Dict:
        """
        Parse LLM response JSON, handling markdown code blocks.

        Retries with LLM if JSON parsing fails.

        Args:
            response: LLM response text

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If JSON parsing fails after retry
        """
        # Strip markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        # Try multiple parsing strategies with increasing aggressiveness
        parsing_strategies = [
            ("direct_parse", lambda r: json.loads(r)),
            ("clean_whitespace", lambda r: json.loads(re.sub(r'^\s+', '', r, flags=re.MULTILINE))),
            ("extract_json", lambda r: self._extract_json_from_response(r)),
            ("fix_common_issues", lambda r: json.loads(self._fix_common_json_issues(r))),
        ]

        last_error = None
        for strategy_name, strategy_func in parsing_strategies:
            try:
                result = strategy_func(response)
                # Clean dictionary keys (remove leading/trailing whitespace from keys)
                result = self._clean_dict_keys(result)
                # Validate the result has expected keys
                if isinstance(result, dict) and ("issues" in result or "recommendations" in result):
                    return result
            except Exception as e:
                last_error = e
                continue

        # All strategies failed - try LLM fix as last resort
        try:
            return self._retry_with_llm_json_fix(response, str(last_error))
        except Exception as retry_error:
            # Even retry failed - return safe fallback instead of crashing
            logger.log(f"⚠️  JSON parsing failed with all strategies: {retry_error}", "WARNING")
            logger.log(f"   Returning empty analysis to allow pipeline to continue", "WARNING")
            return {
                "issues": [],
                "recommendations": ["LLM analysis unavailable - JSON parsing failed"],
                "recommendation": "APPROVE_ALL",
                "recommendation_reason": "Unable to parse LLM analysis, proceeding with caution"
            }

    def _fix_common_json_issues(self, response: str) -> str:
        """
        Fix common JSON formatting issues.

        WHY: LLMs sometimes produce almost-valid JSON with minor issues
        PATTERNS: Guard clauses, string manipulation

        Args:
            response: Response string with potential JSON issues

        Returns:
            Cleaned JSON string
        """
        # Remove leading/trailing whitespace from each line
        cleaned = re.sub(r'^\s+', '', response, flags=re.MULTILINE)

        # Fix trailing commas before closing braces/brackets
        cleaned = re.sub(r',(\s*[}\]])', r'\1', cleaned)

        # Fix missing commas between array/object elements
        cleaned = re.sub(r'"\s*\n\s*"', '",\n"', cleaned)
        cleaned = re.sub(r'}\s*\n\s*{', '},\n{', cleaned)

        # Remove any non-printable characters
        cleaned = ''.join(char for char in cleaned if char.isprintable() or char in '\n\r\t')

        return cleaned

    def _clean_dict_keys(self, data: Any) -> Any:
        """
        Recursively clean dictionary keys by removing leading/trailing whitespace.

        WHY: LLMs sometimes put whitespace inside key names, causing KeyError
        PATTERNS: Recursive traversal, type checking

        Args:
            data: Dictionary, list, or primitive value to clean

        Returns:
            Cleaned data structure with whitespace-free keys
        """
        # Guard: Not a dict or list, return as-is
        if not isinstance(data, (dict, list)):
            return data

        # Handle dictionaries: clean keys and recurse on values
        if isinstance(data, dict):
            return {
                key.strip() if isinstance(key, str) else key: self._clean_dict_keys(value)
                for key, value in data.items()
            }

        # Handle lists: recurse on each element
        return [self._clean_dict_keys(item) for item in data]

    def _extract_json_from_response(self, response: str) -> Dict:
        """
        Extract JSON from response using regex fallback.

        Args:
            response: Response string to parse

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If JSON extraction fails
            json.JSONDecodeError: If extracted JSON is malformed
        """
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        # Guard clause: No JSON found
        if not json_match:
            raise ValueError(f"No JSON object found in response: {response[:200]}...")

        return json.loads(json_match.group(0))

    def _retry_with_llm_json_fix(self, malformed_response: str, error_message: str) -> Dict:
        """
        Retry with LLM asking it to fix the malformed JSON.

        Args:
            malformed_response: The malformed JSON response from LLM
            error_message: The error message from JSON parsing

        Returns:
            Parsed JSON dict from corrected response

        Raises:
            ValueError: If retry also fails
        """
        # Guard clause: No LLM available for retry
        if not self.llm_client:
            raise ValueError(f"JSON parsing failed and no LLM available for retry: {error_message}")

        fix_prompt = f"""The previous response had a JSON formatting error:

Error: {error_message}

Malformed Response:
{malformed_response[:500]}

Please return ONLY the corrected JSON response with proper formatting.
The JSON must match this schema:
{{
  "issues": [
    {{
      "category": "string",
      "description": "string",
      "suggestion": "string",
      "severity": "CRITICAL" | "HIGH" | "MEDIUM"
    }}
  ],
  "recommendations": ["string"],
  "recommendation": "APPROVE_ALL" | "APPROVE_CRITICAL" | "REJECT",
  "recommendation_reason": "string"
}}

Return ONLY valid JSON, no markdown, no explanations."""

        try:
            # Call LLM to fix the JSON
            retry_response = self.llm_client.generate(
                prompt=fix_prompt,
                system_message="You are a JSON formatting expert. Fix the malformed JSON and return only valid JSON.",
                max_tokens=2000
            )

            # Strip and parse the fixed response
            fixed = retry_response.strip()
            if fixed.startswith("```json"):
                fixed = fixed[7:]
            if fixed.startswith("```"):
                fixed = fixed[3:]
            if fixed.endswith("```"):
                fixed = fixed[:-3]
            fixed = fixed.strip()

            return json.loads(fixed)

        except Exception as e:
            # Retry failed - raise error with full context
            raise ValueError(
                f"JSON parsing failed and retry attempt also failed.\n"
                f"Original error: {error_message}\n"
                f"Retry error: {str(e)}\n"
                f"Malformed response preview: {malformed_response[:200]}..."
            )

    def _extract_issues(self, analysis_data: Dict) -> List[Issue]:
        """
        Extract issues from LLM analysis data.

        Converts LLM response format to Issue objects.

        Args:
            analysis_data: Parsed LLM response

        Returns:
            List of Issue objects
        """
        issues = []
        for issue_data in analysis_data.get("issues", []):
            severity_str = issue_data.get("severity", "MEDIUM").upper()
            severity = Severity[severity_str] if severity_str in Severity.__members__ else Severity.MEDIUM

            issues.append(Issue(
                category=issue_data.get("category", "General"),
                severity=severity,
                description=issue_data.get("description", ""),
                impact=issue_data.get("impact", ""),
                suggestion=issue_data.get("suggestion", ""),
                reasoning=issue_data.get("reasoning", ""),
                user_approval_needed=issue_data.get("user_approval_needed", False)
            ))

        return issues
