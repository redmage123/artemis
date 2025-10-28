#!/usr/bin/env python3
"""
WHY: Analyze task descriptions to extract technical requirements.

RESPONSIBILITY:
- Parse task text for technical keywords (frontend, backend, database, etc.)
- Detect task types (feature, bugfix, refactor, etc.)
- Use AI or rule-based analysis depending on configuration
- Build TaskRequirements data structure

PATTERNS:
- Strategy Pattern: AI vs rule-based analysis strategies
- Guard Clauses: Early returns for edge cases
- Dispatch Table: Keyword pattern matching
- Single Responsibility: Only analyzes task requirements
"""

from typing import Dict, Optional, Any
import re
import json

from routing.models import TaskRequirements
from routing.complexity_classifier import ComplexityClassifier
from ai_query_service import AIQueryService, QueryType


class TaskAnalyzer:
    """
    WHY: Extract structured requirements from unstructured task descriptions.

    RESPONSIBILITY:
    - Choose analysis strategy (AI vs rule-based)
    - Parse task text for technical indicators
    - Build TaskRequirements with detected needs
    - Provide confidence scores
    """

    # Pre-compiled regex patterns for keyword matching (O(n) performance)
    FRONTEND_PATTERN = re.compile(
        r'\b(html|css|javascript|react|vue|angular|frontend|ui|user\s*interface|'
        r'visualization|chart|dashboard|button|form|modal|component|page|view|template)\b',
        re.IGNORECASE
    )
    BACKEND_PATTERN = re.compile(
        r'\b(api|backend|server|endpoint|service|business\s*logic|data\s*processing|'
        r'calculation|algorithm|function|method)\b',
        re.IGNORECASE
    )
    API_PATTERN = re.compile(
        r'\b(api|endpoint|rest|graphql|request|response)\b',
        re.IGNORECASE
    )
    DATABASE_PATTERN = re.compile(
        r'\b(database|sql|nosql|mongodb|postgres|mysql|schema|table|collection|'
        r'query|data\s*model)\b',
        re.IGNORECASE
    )
    DEPENDENCY_PATTERN = re.compile(
        r'\b(library|package|dependency|npm|pip|import|external|third-party|'
        r'integration|sdk)\b',
        re.IGNORECASE
    )
    UI_COMPONENT_PATTERN = re.compile(
        r'\b(button|form|input|modal|dialog|menu|navigation|dropdown|select|'
        r'checkbox|radio|slider|tooltip)\b',
        re.IGNORECASE
    )
    A11Y_PATTERN = re.compile(
        r'\b(accessibility|wcag|screen\s*reader|aria|keyboard|a11y|alt\s*text|'
        r'focus|semantic|contrast)\b',
        re.IGNORECASE
    )
    NOTEBOOK_PATTERN = re.compile(
        r'\b(jupyter|notebook|ipynb|data\s*analysis|data\s*science|machine\s*learning|'
        r'ml|model|training|visualization|pandas|numpy|matplotlib|seaborn|'
        r'experiment|analysis)\b',
        re.IGNORECASE
    )

    # Task type detection keywords (dispatch table pattern)
    TASK_TYPE_KEYWORDS = {
        'bugfix': ['bug', 'fix', 'error', 'issue'],
        'refactor': ['refactor', 'cleanup', 'improve'],
        'test': ['test', 'testing', 'coverage'],
        'documentation': ['documentation', 'doc', 'readme']
    }

    def __init__(
        self,
        ai_service: Optional[AIQueryService] = None,
        complexity_classifier: Optional[ComplexityClassifier] = None,
        logger: Optional[Any] = None,
        config: Optional[Any] = None
    ):
        """
        WHY: Initialize analyzer with dependencies and configuration.

        Args:
            ai_service: AI service for intelligent analysis
            complexity_classifier: Classifier for complexity calculation
            logger: Logger for output
            config: Configuration for analysis rules
        """
        self.ai_service = ai_service
        self.complexity_classifier = complexity_classifier or ComplexityClassifier()
        self.logger = logger
        self.config = config

        # Load configuration
        self.enable_ai_analysis = config.get('routing.enable_ai', True) if config else True

    def analyze(self, card: Dict[str, Any]) -> TaskRequirements:
        """
        WHY: Main entry point for task requirement analysis.

        RESPONSIBILITY:
        - Extract task title and description
        - Choose analysis strategy (AI or rule-based)
        - Return structured TaskRequirements

        Args:
            card: Kanban card with task details

        Returns:
            TaskRequirements with detected needs

        PATTERNS: Strategy Pattern - delegates to AI or rule-based analyzer
        """
        task_title = card.get('title', '')
        task_description = card.get('description', '')
        full_text = f"{task_title}\n\n{task_description}".lower()

        # Strategy: AI analysis if available
        if self.ai_service and self.enable_ai_analysis:
            return self._ai_analyze(card, full_text)

        # Strategy: Rule-based fallback
        return self._rule_based_analyze(card, full_text)

    def _ai_analyze(self, card: Dict[str, Any], full_text: str) -> TaskRequirements:
        """
        WHY: Use AI to intelligently analyze task requirements.

        RESPONSIBILITY:
        - Build analysis prompt with examples
        - Query AI service
        - Parse JSON response
        - Fall back to rule-based if AI fails

        Args:
            card: Kanban card
            full_text: Combined title + description (lowercase)

        Returns:
            TaskRequirements from AI analysis

        PATTERNS: Guard Clause - fallback on exception
        """
        prompt = self._build_ai_analysis_prompt(card)

        try:
            # Query AI service
            result = self.ai_service.query(
                query_type=QueryType.PROJECT_ANALYSIS,
                prompt=prompt,
                kg_query_params={
                    'task_title': card.get('title', ''),
                    'context_type': 'requirement_analysis'
                }
            )

            # Parse AI response
            analysis = self._parse_ai_response(result.llm_response.content)

            # Build TaskRequirements from AI analysis
            return self._build_requirements_from_ai(analysis)

        except Exception as e:
            # Guard: AI failure - fallback to rule-based
            if self.logger:
                self.logger.log(
                    f"AI requirement analysis failed: {e}, using rule-based fallback",
                    "WARNING"
                )
            return self._rule_based_analyze(card, full_text)

    def _build_ai_analysis_prompt(self, card: Dict[str, Any]) -> str:
        """
        WHY: Create comprehensive analysis prompt for AI.

        RESPONSIBILITY:
        - Include task details
        - Define expected JSON schema
        - Provide classification guidelines
        - Set conservative complexity expectations

        Args:
            card: Kanban card

        Returns:
            Formatted prompt string
        """
        return f"""Analyze this software development task and extract requirements:

Task: {card.get('title', '')}
Description: {card.get('description', '')}

Provide a JSON response with the following fields:
{{
    "has_frontend": true/false,
    "has_backend": true/false,
    "has_api": true/false,
    "has_database": true/false,
    "has_external_dependencies": true/false,
    "has_ui_components": true/false,
    "has_accessibility_requirements": true/false,
    "requires_notebook": true/false,
    "complexity": "simple|medium|complex",
    "task_type": "feature|bugfix|refactor|documentation|test",
    "estimated_story_points": 1-13,
    "requires_architecture_review": true/false,
    "requires_project_review": true/false,
    "parallel_developers_recommended": 1-3,
    "confidence_score": 0.0-1.0,
    "reasoning": "Brief explanation"
}}

Consider:
- Frontend: HTML, CSS, JavaScript, React, Vue, UI, visualization, charts
- Backend: API, server, business logic, data processing
- Database: SQL, NoSQL, schema, queries, data models
- Dependencies: External libraries, packages, services, APIs
- UI/Accessibility: WCAG, screen readers, keyboard navigation, ARIA
- Notebook: Jupyter, data analysis, ML, pandas, visualization

Complexity Classification (CRITICAL - be conservative, err on the side of SIMPLE):
- SIMPLE (1-3 story points):
  * Single file or 2-3 small files (<200 lines total)
  * No database schema changes
  * No API design or new endpoints
  * No complex algorithms or business logic
  * Straightforward implementation
  * Examples: Add a button, format data, simple calculation, basic form validation

- MEDIUM (5-8 story points):
  * Multiple files (3-8 files, 200-800 lines total)
  * Simple API endpoints or database queries
  * Moderate business logic
  * Some integration with existing systems
  * Examples: New CRUD feature, dashboard page, data export functionality

- COMPLEX (13 story points):
  * Large feature (8+ files, 800+ lines)
  * Complex database schema or migrations
  * Multiple API endpoints with orchestration
  * Complex algorithms or state management
  * Multi-system integration
  * Examples: Authentication system, payment processing, real-time collaboration
"""

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """
        WHY: Extract and parse JSON from AI response.

        RESPONSIBILITY:
        - Find JSON boundaries in response text
        - Parse JSON to dictionary
        - Raise exception if invalid (triggers fallback)

        Args:
            response_text: Raw AI response content

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If no valid JSON found (triggers rule-based fallback)

        PATTERNS: Guard Clause - early exception on invalid JSON
        """
        # Find JSON boundaries
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        # Guard: No valid JSON
        if json_start < 0 or json_end <= json_start:
            raise ValueError("No valid JSON in AI response")

        # Parse and return
        return json.loads(response_text[json_start:json_end])

    def _build_requirements_from_ai(self, analysis: Dict[str, Any]) -> TaskRequirements:
        """
        WHY: Convert AI analysis dictionary to TaskRequirements dataclass.

        RESPONSIBILITY:
        - Extract fields from AI response
        - Apply defaults for missing fields
        - Build TaskRequirements instance

        Args:
            analysis: Parsed AI response dictionary

        Returns:
            TaskRequirements instance
        """
        return TaskRequirements(
            has_frontend=analysis.get('has_frontend', False),
            has_backend=analysis.get('has_backend', True),
            has_api=analysis.get('has_api', False),
            has_database=analysis.get('has_database', False),
            has_external_dependencies=analysis.get('has_external_dependencies', False),
            has_ui_components=analysis.get('has_ui_components', False),
            has_accessibility_requirements=analysis.get('has_accessibility_requirements', False),
            requires_notebook=analysis.get('requires_notebook', False),
            complexity=analysis.get('complexity', 'medium'),
            task_type=analysis.get('task_type', 'feature'),
            estimated_story_points=analysis.get('estimated_story_points', 5),
            requires_architecture_review=analysis.get('requires_architecture_review', True),
            requires_project_review=analysis.get('requires_project_review', True),
            parallel_developers_recommended=analysis.get('parallel_developers_recommended', 1),
            confidence_score=analysis.get('confidence_score', 0.7)
        )

    def _rule_based_analyze(
        self,
        card: Dict[str, Any],
        full_text: str
    ) -> TaskRequirements:
        """
        WHY: Fallback analysis using regex pattern matching.

        RESPONSIBILITY:
        - Apply regex patterns to detect technical requirements
        - Classify complexity from story points
        - Detect task type from keywords
        - Calculate review requirements
        - Build TaskRequirements with lower confidence

        Args:
            card: Kanban card
            full_text: Combined title + description (lowercase)

        Returns:
            TaskRequirements from rule-based analysis

        PATTERNS: Dispatch Table - pre-compiled regex patterns
        """
        # Pattern matching for technical requirements
        has_frontend = bool(self.FRONTEND_PATTERN.search(full_text))
        has_backend = bool(self.BACKEND_PATTERN.search(full_text))
        has_api = bool(self.API_PATTERN.search(full_text))
        has_database = bool(self.DATABASE_PATTERN.search(full_text))
        has_external_dependencies = bool(self.DEPENDENCY_PATTERN.search(full_text))
        has_ui_components = bool(self.UI_COMPONENT_PATTERN.search(full_text))
        has_accessibility_requirements = bool(self.A11Y_PATTERN.search(full_text))
        requires_notebook = bool(self.NOTEBOOK_PATTERN.search(full_text))

        # Classify complexity from story points
        story_points = card.get('story_points', 5)
        complexity = self.complexity_classifier.classify_from_story_points(story_points)

        # Detect task type
        task_type = self._detect_task_type(full_text)

        # Calculate review requirements
        review_reqs = self.complexity_classifier.calculate_review_requirements(
            complexity=complexity,
            has_database=has_database,
            has_api=has_api,
            story_points=story_points
        )

        # Build TaskRequirements
        return TaskRequirements(
            has_frontend=has_frontend,
            has_backend=has_backend,
            has_api=has_api,
            has_database=has_database,
            has_external_dependencies=has_external_dependencies,
            has_ui_components=has_ui_components,
            has_accessibility_requirements=has_accessibility_requirements,
            requires_notebook=requires_notebook,
            complexity=complexity,
            task_type=task_type,
            estimated_story_points=story_points,
            requires_architecture_review=review_reqs['architecture_review'],
            requires_project_review=review_reqs['project_review'],
            parallel_developers_recommended=2,  # Always use 2 for competitive development
            confidence_score=0.6  # Rule-based has lower confidence
        )

    def _detect_task_type(self, full_text: str) -> str:
        """
        WHY: Classify task type from text keywords.

        RESPONSIBILITY:
        - Check keywords in priority order
        - Return first matching type
        - Default to 'feature' if no match

        Args:
            full_text: Task text (lowercase)

        Returns:
            Task type: 'bugfix', 'refactor', 'test', 'documentation', or 'feature'

        PATTERNS: Dispatch Table - keyword lookup
        """
        # Check each task type in priority order
        for task_type, keywords in self.TASK_TYPE_KEYWORDS.items():
            if any(kw in full_text for kw in keywords):
                return task_type

        # Default: feature
        return 'feature'
